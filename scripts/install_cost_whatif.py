"""F4-INSTALL — read-only installation-cost what-if analysis.

Reads data/processed/phase4/financial_scorecards.parquet (must be a
post-F4-INSTALL re-run so the installation_capex_usd column is present) and
prints a decision table comparing project_viable count and viable GWh/yr
across four installation fractions: 0.00, 0.15, 0.175, 0.20.

How it works
------------
For each installation fraction ``f``, total project CapEx is recomputed as:

    new_total_capex = equipment_capex_usd × (1 + f)
                    + interconnection_capex_usd
                    + permitting_capex_usd

OpEx stays on equipment CapEx only (installation is a one-time cost, not
O&M-bearing).  ``compute_scorecard`` is called per row to derive fresh
NPV / IRR / payback under the new CapEx, and ``project_viable`` is re-derived
using the same gate (NPV>0 AND payback≤20yr AND real IRR).

This script is STRICTLY read-only:
  - does NOT write any parquet file
  - does NOT modify settings.yaml or any source file
  - does NOT change any column or viability flag in the parquet

Usage:
    python scripts/install_cost_whatif.py
    python scripts/install_cost_whatif.py --parquet path/to/financial_scorecards.parquet
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import polars as pl

# ── Locate root and import financial helpers ──────────────────────────────────

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from src.phase4.financials import (   # noqa: E402
    DEGRADATION_RATE,
    DISCOUNT_RATE,
    PROJECT_YEARS,
    compute_npv,
    compute_irr,
    compute_payback,
)

_DEFAULT_PARQUET = _ROOT / "data" / "processed" / "phase4" / "financial_scorecards.parquet"

# Installation fractions to compare (0.00 = prior behavior baseline)
_FRACTIONS: list[float] = [0.00, 0.15, 0.175, 0.20]

_REQUIRED_COLS = {
    "equipment_capex_usd",
    "installation_capex_usd",
    "interconnection_capex_usd",
    "permitting_capex_usd",
    "annual_energy_kwh",
    "elec_rate_per_kwh",
    "annual_opex_usd",
    "annual_revenue_usd",
}


def _is_real_irr(irr: float) -> bool:
    """Return True iff IRR is a real solver result (not NaN or ±sentinel)."""
    return not math.isnan(irr) and irr > -0.99 and irr < 3.0


def _viable_under_fraction(rows: list[dict], frac: float) -> tuple[int, float]:
    """Re-derive project_viable count and viable GWh/yr for ``frac``.

    Args:
        rows:  list of row dicts from the parquet (all scored sites).
        frac:  installation cost as fraction of equipment CapEx.

    Returns:
        (n_viable, viable_gwh_yr)
    """
    n_viable = 0
    viable_kwh = 0.0

    for row in rows:
        eq   = float(row.get("equipment_capex_usd") or 0.0)
        intc = float(row.get("interconnection_capex_usd") or 0.0)
        perm = float(row.get("permitting_capex_usd") or 0.0)

        new_total = eq * (1.0 + frac) + intc + perm

        energy  = float(row.get("annual_energy_kwh") or 0.0)
        rate    = float(row.get("elec_rate_per_kwh") or 0.0)
        opex    = float(row.get("annual_opex_usd") or 0.0)

        if energy <= 0 or new_total <= 0:
            continue

        npv     = compute_npv(energy, rate, opex, new_total,
                              DISCOUNT_RATE, PROJECT_YEARS, DEGRADATION_RATE)
        payback = compute_payback(energy, rate, opex, new_total,
                                  PROJECT_YEARS, DEGRADATION_RATE)
        irr     = compute_irr(energy, rate, opex, new_total,
                              PROJECT_YEARS, DEGRADATION_RATE)

        if npv > 0 and payback <= 20.0 and _is_real_irr(irr):
            n_viable += 1
            viable_kwh += energy

    viable_gwh = viable_kwh / 1e6
    return n_viable, viable_gwh


def main(parquet_path: Path) -> None:
    if not parquet_path.exists():
        print(f"ERROR: parquet not found at {parquet_path}", file=sys.stderr)
        print("  Run Phase 4 first: python -m src.phase4.run", file=sys.stderr)
        sys.exit(1)

    df = pl.read_parquet(parquet_path)

    missing = _REQUIRED_COLS - set(df.columns)
    if missing:
        print(
            f"ERROR: missing columns {sorted(missing)}.\n"
            "  Re-run Phase 4 after F4-INSTALL changes:\n"
            "  python -m src.phase4.run",
            file=sys.stderr,
        )
        sys.exit(1)

    rows = df.to_dicts()
    total = len(rows)

    # Derive baseline (frac=0.00) and current (frac=0.175) for Δ column
    results: list[dict] = []
    baseline_viable: int | None = None

    for frac in _FRACTIONS:
        n_viable, viable_gwh = _viable_under_fraction(rows, frac)
        results.append({
            "install_pct":   frac,
            "viable_sites":  n_viable,
            "viable_GWh_yr": round(viable_gwh, 1),
        })
        if frac == 0.00:
            baseline_viable = n_viable

    # ── Print header ──────────────────────────────────────────────────────────
    print()
    print("## F4-INSTALL What-If Analysis")
    print()
    print(f"Parquet:            `{parquet_path}`")
    print(f"Total scored sites: {total:,}")
    print(f"Financial model:    NPV>0 AND payback≤20yr AND real IRR")
    print(f"OpEx basis:         equipment CapEx only (installation is one-time, not O&M)")
    print()

    # ── Decision table ────────────────────────────────────────────────────────
    hdr = ("install_pct", "viable_sites", "viable_GWh_yr", "Δ vs 0%")
    col_data = [
        (
            f"{r['install_pct']:.3f}",
            str(r["viable_sites"]),
            str(r["viable_GWh_yr"]),
            (
                f"{r['viable_sites'] - baseline_viable:+d}"
                if baseline_viable is not None else "—"
            ),
        )
        for r in results
    ]
    widths = [
        max(len(h), max(len(d[i]) for d in col_data))
        for i, h in enumerate(hdr)
    ]

    def _row(vals: tuple) -> str:
        return "| " + " | ".join(
            str(v).ljust(w) for v, w in zip(vals, widths)
        ) + " |"

    print(_row(hdr))
    print("| " + " | ".join("-" * w for w in widths) + " |")
    for d in col_data:
        print(_row(d))

    print()
    print(f"Committed production default: 0.175 (midpoint of director 15–20% range)")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Read-only F4-INSTALL what-if analysis"
    )
    parser.add_argument(
        "--parquet",
        type=Path,
        default=_DEFAULT_PARQUET,
        help="Path to financial_scorecards.parquet (default: data/processed/phase4/)",
    )
    args = parser.parse_args()
    main(args.parquet)
