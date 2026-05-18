"""Phase 4 orchestrator — Financial Scorecard.

Usage:
    python -m src.phase4.run                          # full run
    python -m src.phase4.run --top-n 500              # limit to top-N by rank
    python -m src.phase4.run --no-sensitivity         # skip tornado analysis

Pipeline steps
--------------
[1/4]  Load Phase 3 turbine_sizing.parquet + Phase 1 state codes.
[2/4]  Look up electricity rates and compute CapEx / OpEx / revenue.
[3/4]  Compute NPV, IRR, payback, LCOE.
[4/4]  Run sensitivity analysis and save financial_scorecards.parquet.

Output: data/processed/phase4/financial_scorecards.parquet
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import polars as pl

from src.common import config, io, logging_setup
from src.phase4.cost_models import annual_opex, capex_per_kw, total_capex
from src.phase4.financials import (
    DEGRADATION_RATE, DISCOUNT_RATE, PROJECT_YEARS, compute_scorecard,
)
from src.phase4.revenue import annual_revenue, electricity_rate
from src.phase4.sensitivity import run_tornado

logging_setup.setup_run_log("phase4")
log = logging_setup.get("wowers.phase4")

OUTPUT_DIR: Path = config.processed_dir() / "phase4"
_PHASE1_OUTPUT: Path = config.processed_dir() / "phase1" / "ranked_candidates.parquet"
_PHASE3_OUTPUT: Path = config.processed_dir() / "phase3" / "turbine_sizing.parquet"


def run(
    phase3_input: Path | None = None,
    phase1_input: Path | None = None,
    top_n:        int | None = None,
    run_sensitivity: bool = True,
) -> Path:
    """Run the full Phase 4 pipeline.

    Args:
        phase3_input:    Path to turbine_sizing.parquet.  Auto-detects if None.
        phase1_input:    Path to ranked_candidates.parquet.  Auto-detects if None.
        top_n:           Limit to top-N viable turbine sites (by rated_power_kw).
        run_sensitivity: Whether to compute tornado sensitivity columns.

    Returns:
        Path to financial_scorecards.parquet.
    """
    t0 = time.time()
    p3_path = phase3_input or _PHASE3_OUTPUT
    p1_path = phase1_input or _PHASE1_OUTPUT

    log.info("=" * 60)
    log.info("WOWERS Phase 4 — Financial Scorecard")
    log.info(f"  Phase 3 input: {p3_path}")
    log.info(f"  Phase 1 input: {p1_path}")
    log.info(f"  Output dir:    {OUTPUT_DIR}")
    log.info("=" * 60)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Load inputs ───────────────────────────────────────────────────
    log.info("[1/4] Loading Phase 3 turbine sizing …")
    if not p3_path.exists():
        raise FileNotFoundError(
            f"Phase 3 output not found: {p3_path}\n"
            "Run Phase 3 first: python -m src.phase3.run"
        )
    turbines = io.read_parquet(p3_path)
    log.info(f"  Loaded {len(turbines):,} facilities from Phase 3")

    # Join state_code from Phase 1 (Phase 3 may not carry it through)
    if "state_code" not in turbines.columns and p1_path.exists():
        log.info("  Joining state_code from Phase 1 …")
        p1 = io.read_parquet(p1_path).select(["npdes_id", "state_code"])
        turbines = turbines.join(p1, on="npdes_id", how="left")

    # Restrict to viable sites
    if "turbine_viable" in turbines.columns:
        viable = turbines.filter(pl.col("turbine_viable") == True)  # noqa: E712
        log.info(f"  Viable sites: {len(viable):,}/{len(turbines):,}")
    else:
        viable = turbines

    if top_n is not None:
        sort_col = "p_rated_kw" if "p_rated_kw" in viable.columns else viable.columns[0]
        viable = viable.sort(sort_col, descending=True).head(top_n)
        log.info(f"  Limited to top {top_n} by rated power (--top-n)")

    if len(viable) == 0:
        raise RuntimeError("No viable turbine sites found. Check Phase 3 output.")

    # ── Step 2: CapEx / OpEx / Revenue ────────────────────────────────────────
    log.info("[2/4] Computing CapEx, OpEx, and revenue …")
    rows = viable.to_dicts()
    financial_rows: list[dict] = []

    for row in rows:
        npdes_id    = row["npdes_id"]
        t_type      = row.get("turbine_type", "Kaplan")
        rated_kw    = float(row.get("p_rated_kw") or 0.0)
        energy_kwh  = float(row.get("annual_energy_mwh") or 0.0) * 1_000  # MWh → kWh
        state_code  = row.get("state_code")

        if rated_kw <= 0 or energy_kwh <= 0:
            continue  # skip non-viable rows that slipped through

        cap_usd      = total_capex(t_type, rated_kw)
        cap_per_kw   = capex_per_kw(t_type, rated_kw)
        opex_usd     = annual_opex(t_type, cap_usd)
        elec_rate    = electricity_rate(state_code)
        rev_usd      = annual_revenue(energy_kwh, state_code)

        scorecard = compute_scorecard(
            annual_energy_kwh=energy_kwh,
            elec_rate_per_kwh=elec_rate,
            annual_opex_usd=opex_usd,
            total_capex_usd=cap_usd,
            annual_revenue_usd=rev_usd,
        )

        financial_rows.append({
            "npdes_id":            npdes_id,
            "state_code":          state_code,
            "turbine_type":        t_type,
            "rated_power_kw":      rated_kw,
            "annual_energy_kwh":   energy_kwh,
            "capacity_factor":     row.get("capacity_factor"),
            "capex_per_kw":        cap_per_kw,
            "total_capex_usd":     cap_usd,
            "annual_opex_usd":     opex_usd,
            "elec_rate_per_kwh":   elec_rate,
            "annual_revenue_usd":  rev_usd,
            **scorecard,
        })

    log.info(f"  Scored {len(financial_rows):,} facilities")

    # ── Step 3: Sensitivity analysis ──────────────────────────────────────────
    if run_sensitivity:
        log.info("[3/4] Running tornado sensitivity analysis …")
        for fr in financial_rows:
            tornado = run_tornado(
                annual_energy_kwh=fr["annual_energy_kwh"],
                elec_rate_per_kwh=fr["elec_rate_per_kwh"],
                annual_opex_usd=fr["annual_opex_usd"],
                total_capex_usd=fr["total_capex_usd"],
            )
            fr.update(tornado)
    else:
        log.info("[3/4] Skipping sensitivity (--no-sensitivity)")
        for fr in financial_rows:
            fr.update({
                "sensitivity_head_npv_low":  None,
                "sensitivity_head_npv_high": None,
                "sensitivity_flow_npv_low":  None,
                "sensitivity_flow_npv_high": None,
                "sensitivity_rate_npv_low":  None,
                "sensitivity_rate_npv_high": None,
                "dominant_sensitivity":      None,
            })

    # ── Step 4: Save ──────────────────────────────────────────────────────────
    log.info("[4/4] Saving financial_scorecards.parquet …")
    out_df = pl.DataFrame(financial_rows)
    out_path = OUTPUT_DIR / "financial_scorecards.parquet"
    io.write_parquet(out_df, out_path)
    io.checkpoint(out_df, "phase4", "financial_scorecards")

    elapsed = time.time() - t0
    _print_summary(out_df, elapsed)
    return out_path


# ── Summary ───────────────────────────────────────────────────────────────────

def _print_summary(df: pl.DataFrame, elapsed: float) -> None:
    total = len(df)

    viable_mask = (pl.col("npv_usd") > 0) & (pl.col("payback_years") <= 20)
    n_viable = df.filter(viable_mask).shape[0] if "npv_usd" in df.columns else 0

    log.info("")
    log.info("=" * 60)
    log.info("Phase 4 Complete")
    log.info(f"  Total scored:            {total:,}")
    log.info(f"  Project viable (NPV>0 & payback≤20yr): {n_viable:,} ({n_viable/max(total,1)*100:.1f}%)")

    if "payback_years" in df.columns:
        valid_payback = df.filter(pl.col("payback_years") < 999)["payback_years"]
        if len(valid_payback) > 0:
            log.info(f"  Median payback (viable): {valid_payback.median():.1f} yr")

    if "total_capex_usd" in df.columns:
        total_inv = df["total_capex_usd"].sum() / 1e6
        log.info(f"  Total portfolio CapEx:   ${total_inv:,.1f}M")

    if "annual_revenue_usd" in df.columns:
        total_rev = df["annual_revenue_usd"].sum() / 1e6
        log.info(f"  Total portfolio revenue: ${total_rev:,.1f}M/yr")

    log.info(f"  Runtime:                 {elapsed:.1f}s")
    log.info(f"  Output: {OUTPUT_DIR / 'financial_scorecards.parquet'}")
    log.info("=" * 60)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WOWERS Phase 4: Financial Scorecard")
    parser.add_argument("--phase3-input", type=Path, default=None,
                        help="Path to Phase 3 turbine_sizing.parquet")
    parser.add_argument("--phase1-input", type=Path, default=None,
                        help="Path to Phase 1 ranked_candidates.parquet (for state codes)")
    parser.add_argument("--top-n", type=int, default=None,
                        help="Limit to top-N sites by rated power")
    parser.add_argument("--no-sensitivity", action="store_true",
                        help="Skip tornado sensitivity analysis")
    args = parser.parse_args()

    run(
        phase3_input=args.phase3_input,
        phase1_input=args.phase1_input,
        top_n=args.top_n,
        run_sensitivity=not args.no_sensitivity,
    )
