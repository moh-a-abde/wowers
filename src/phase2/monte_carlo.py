"""Phase 2 — Per-facility Monte Carlo runner.

Processes all facilities from Phase 1 ``ranked_candidates.parquet``, applies
the pre-Phase-2 exclusion filter (zero/null mean flow, sparse DMR data), and
runs the Monte Carlo energy estimation for each.

Performance
-----------
With vectorised NumPy, 10,000 iterations per facility completes in ~10 ms per
facility.  For 15,000 facilities, the total wall-clock time is roughly 2–3
minutes single-threaded, or under 30 seconds with parallelisation.

Parallelisation uses ``concurrent.futures.ProcessPoolExecutor`` (process-based
to bypass the GIL for NumPy workloads).  Each worker receives a batch of
facilities and processes them sequentially, returning a list of result dicts.
"""

from __future__ import annotations

import logging
import math
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any

import numpy as np
import polars as pl

from src.phase2.energy_physics import run_monte_carlo
from src.phase2.head_assumptions import classify_archetype, get_head_distribution

log = logging.getLogger("wowers.phase2.monte_carlo")

# ── Exclusion filter (pre-Phase-2) ────────────────────────────────────────────

def _exclude(row: dict) -> str | None:
    """Return an exclusion reason string, or None if the row is usable."""
    mean_flow = row.get("mean_flow_mgd")
    if mean_flow is None or mean_flow <= 0:
        return "no_usable_flow"
    dq = row.get("data_quality", "dmr")
    n_months = row.get("n_months_data", 99)
    if dq == "dmr_limited" and (n_months is None or n_months < 3):
        return "sparse_dmr_artifact"
    return None


# ── Single-facility processing (called in worker processes) ───────────────────

def _process_one(row: dict, n_iterations: int, seed: int | None) -> dict:
    """Run Monte Carlo for one facility row.  Returns output dict."""
    exclusion = _exclude(row)
    npdes_id = row["npdes_id"]

    if exclusion is not None:
        return {
            "npdes_id":             npdes_id,
            "archetype":            None,
            "head_assumed_low_m":   None,
            "head_assumed_mode_m":  None,
            "head_assumed_high_m":  None,
            "energy_p10_kwh_yr":    None,
            "energy_p50_kwh_yr":    None,
            "energy_p90_kwh_yr":    None,
            "energy_mean_kwh_yr":   None,
            "energy_std_kwh_yr":    None,
            "power_p50_kw":         None,
            "capacity_factor_p50":  None,
            "head_m_p10":           None,
            "head_m_p50":           None,
            "head_m_p90":           None,
            "equivalent_homes_p50": None,
            "excluded":             True,
            "exclusion_reason":     exclusion,
        }

    design_flow = row.get("design_flow_mgd")
    archetype = classify_archetype(design_flow)
    head_dist = get_head_distribution(archetype)

    # Build FDC array (20-point, MGD)
    raw_fdc = row.get("flow_duration_curve")
    if raw_fdc is not None and len(raw_fdc) >= 2:
        fdc_flows = np.asarray(raw_fdc, dtype=np.float64)
    else:
        # Fall back to mean flow as a flat FDC
        mean_flow = float(row["mean_flow_mgd"])
        fdc_flows = np.full(20, mean_flow, dtype=np.float64)

    rng = np.random.default_rng(seed)
    mc = run_monte_carlo(
        fdc_flows_mgd=fdc_flows,
        head_low_m=head_dist.low_m,
        head_mode_m=head_dist.mode_m,
        head_high_m=head_dist.high_m,
        n_iterations=n_iterations,
        rng=rng,
    )

    energy_p50_kwh = mc["energy_p50_kwh_yr"]
    avg_us_household_kwh = 10_500  # EIA 2023 average
    equiv_homes = int(round(energy_p50_kwh / avg_us_household_kwh)) if energy_p50_kwh > 0 else 0

    return {
        "npdes_id":             npdes_id,
        "archetype":            archetype,
        "head_assumed_low_m":   head_dist.low_m,
        "head_assumed_mode_m":  head_dist.mode_m,
        "head_assumed_high_m":  head_dist.high_m,
        **mc,
        "equivalent_homes_p50": equiv_homes,
        "excluded":             False,
        "exclusion_reason":     None,
    }


def _process_batch(rows: list[dict], n_iterations: int, base_seed: int) -> list[dict]:
    """Process a batch of facility rows.  Used in worker processes."""
    results = []
    for i, row in enumerate(rows):
        results.append(_process_one(row, n_iterations, base_seed + i))
    return results


# ── Public batch runner ───────────────────────────────────────────────────────

def estimate_all_facilities(
    candidates: pl.DataFrame,
    n_iterations: int = 10_000,
    n_workers: int = 1,
    seed: int = 42,
    log_interval: int = 1_000,
) -> pl.DataFrame:
    """Run Monte Carlo for all facilities.

    Args:
        candidates:   Phase 1 ``ranked_candidates.parquet`` loaded as a Polars
                      DataFrame.  Must contain columns: ``npdes_id``,
                      ``mean_flow_mgd``, ``design_flow_mgd``,
                      ``flow_duration_curve``, optionally ``data_quality`` and
                      ``n_months_data``.
        n_iterations: MC samples per facility (default 10,000).
        n_workers:    Parallel worker processes.  1 = single-threaded.
        seed:         Base random seed (each facility gets seed + row_index).
        log_interval: Log a progress message every N facilities.

    Returns:
        Polars DataFrame with one row per facility (all 15,000+, including
        excluded ones flagged with ``excluded=True``).
    """
    rows: list[dict[str, Any]] = candidates.to_dicts()
    n_total = len(rows)
    log.info(f"Phase 2 Monte Carlo: {n_total:,} facilities × {n_iterations:,} iterations")

    if n_workers <= 1:
        results: list[dict] = []
        for i, row in enumerate(rows):
            results.append(_process_one(row, n_iterations, seed + i))
            if (i + 1) % log_interval == 0 or (i + 1) == n_total:
                n_exc = sum(1 for r in results if r["excluded"])
                log.info(f"  Processed {i + 1:,}/{n_total:,} | excluded: {n_exc:,}")
    else:
        # Split into batches, one per worker
        batch_size = math.ceil(n_total / n_workers)
        batches = [
            (rows[i: i + batch_size], n_iterations, seed + i)
            for i in range(0, n_total, batch_size)
        ]
        results = []
        with ProcessPoolExecutor(max_workers=n_workers) as exe:
            futures = {
                exe.submit(_process_batch, *b): idx
                for idx, b in enumerate(batches)
            }
            for fut in as_completed(futures):
                batch_results = fut.result()
                results.extend(batch_results)
                log.info(f"  Batch complete: {len(results):,}/{n_total:,} processed")

    log.info(f"  Done. {sum(1 for r in results if not r['excluded']):,} facilities estimated.")

    return pl.DataFrame(results)
