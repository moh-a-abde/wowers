"""F4-OFFSET — read-only MINREV what-if analysis.

Reads data/processed/phase4/financial_scorecards.parquet (must be a
post-F4-OFFSET re-run so the energy_offset_pct columns are present) and
prints a markdown table comparing viability under four gate scenarios.

This script is STRICTLY read-only:
  - does NOT write any parquet file
  - does NOT modify settings.yaml or financials.py
  - does NOT change any column or viability flag

Usage:
    python scripts/minrev_whatif.py
    python scripts/minrev_whatif.py --parquet path/to/financial_scorecards.parquet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import polars as pl

# ── Locate default parquet ────────────────────────────────────────────────────

_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_PARQUET = _ROOT / "data" / "processed" / "phase4" / "financial_scorecards.parquet"


def _gwh(df: pl.DataFrame) -> float:
    """Sum annual_energy_kwh → GWh/yr."""
    return float(df["annual_energy_kwh"].sum()) / 1e6


def main(parquet_path: Path) -> None:  # noqa: C901
    if not parquet_path.exists():
        print(f"ERROR: parquet not found at {parquet_path}", file=sys.stderr)
        print("  Run Phase 4 first: python -m src.phase4.run", file=sys.stderr)
        sys.exit(1)

    df = pl.read_parquet(parquet_path)

    # Verify required columns exist (post-F4-OFFSET re-run)
    required = {"project_viable", "site_tier", "annual_energy_kwh",
                "npv_usd", "payback_years", "irr", "energy_offset_pct"}
    missing = required - set(df.columns)
    if missing:
        print(
            f"ERROR: missing columns {sorted(missing)}.\n"
            "  Re-run Phase 4 after the F4-OFFSET changes:\n"
            "  python -m src.phase4.run",
            file=sys.stderr,
        )
        sys.exit(1)

    # ── Tier cohorts (using existing scored columns; no recomputation) ─────────
    tier_a  = df.filter(pl.col("site_tier") == "A")
    tier_b  = df.filter(pl.col("site_tier") == "B")
    tier_ab = df.filter(pl.col("site_tier").is_in(["A", "B"]))

    # ── Scenario table ─────────────────────────────────────────────────────────
    rows: list[dict] = []

    # Scenario 0 — current: project_viable == True (Tier A only)
    rows.append({
        "Scenario":     "0 — Current (project_viable)",
        "Gate":         "Tier A only",
        "Sites":        len(tier_a),
        "GWh/yr":       round(_gwh(tier_a), 1),
    })

    # Scenario 1 — MINREV floor removed: Tier A + Tier B
    # (Tier B = NPV>0, payback≤20yr, real IRR, fails only MINREV)
    rows.append({
        "Scenario":     "1 — Floor removed (Tier A + B)",
        "Gate":         "NPV+payback+IRR, no revenue floor",
        "Sites":        len(tier_ab),
        "GWh/yr":       round(_gwh(tier_ab), 1),
    })

    # Scenario 2 — offset-based gate: Tier A + Tier B with offset ≥ threshold
    for thr in (1.0, 2.0, 5.0):
        tier_b_pass = tier_b.filter(pl.col("energy_offset_pct") >= thr)
        combined = pl.concat([tier_a, tier_b_pass])
        rows.append({
            "Scenario":     f"2 — Offset ≥ {thr:.0f}% gate (Tier A + filtered B)",
            "Gate":         f"Tier A + Tier B with offset_pct ≥ {thr:.0f}%",
            "Sites":        len(combined),
            "GWh/yr":       round(_gwh(combined), 1),
        })

    # ── Print markdown table ──────────────────────────────────────────────────
    print()
    print("## MINREV What-If Analysis")
    print()
    print(f"Parquet: `{parquet_path}`")
    print(f"Total scored sites: {len(df):,}")
    print()

    hdr = ("Scenario", "Gate", "Sites", "GWh/yr")
    widths = [max(len(h), max(len(str(r[h])) for r in rows)) for h in hdr]

    def _row(vals: tuple) -> str:
        return "| " + " | ".join(
            str(v).ljust(w) for v, w in zip(vals, widths)
        ) + " |"

    print(_row(hdr))
    print("| " + " | ".join("-" * w for w in widths) + " |")
    for r in rows:
        print(_row((r["Scenario"], r["Gate"], r["Sites"], r["GWh/yr"])))

    # ── Tier B offset % distribution ─────────────────────────────────────────
    print()
    print("## Tier B — energy_offset_pct distribution")
    print()
    b_off = tier_b["energy_offset_pct"].drop_nulls().sort()
    if len(b_off) == 0:
        print("No Tier B sites with energy_offset_pct data.")
    else:
        n = len(b_off)
        med  = float(b_off[n // 2])
        p90  = float(b_off[int(n * 0.90)])
        p99  = float(b_off[int(n * 0.99)])
        pmax = float(b_off[-1])
        print(f"Tier B sites:   {n:,}")
        print(f"  median:   {med:.2f}%")
        print(f"  p90:      {p90:.2f}%")
        print(f"  p99:      {p99:.2f}%")
        print(f"  max:      {pmax:.2f}%")
        print()
        # Show how many Tier B pass each threshold
        for thr in (1.0, 2.0, 5.0, 10.0):
            n_pass = int((b_off >= thr).sum())
            print(f"  Tier B with offset ≥ {thr:.0f}%: {n_pass:,} ({n_pass/n*100:.1f}%)")

    # ── National sanity ───────────────────────────────────────────────────────
    if "est_plant_consumption_kwh_yr" in df.columns:
        print()
        print("## National consumption sanity (F4-OFFSET columns)")
        print()
        has_cons = df.filter(pl.col("est_plant_consumption_kwh_yr").is_not_null())
        nat_twh = float(has_cons["est_plant_consumption_kwh_yr"].sum()) / 1e9
        print(f"Scored sites with consumption estimate: {len(has_cons):,}")
        print(f"Sum est_plant_consumption_kwh_yr:       {nat_twh:.1f} TWh/yr")
        print(f"  (Reference: scored-site subset of EPRI/EPA ~30.2 TWh/yr national)")
        print()
        med_off = float(
            df.filter(pl.col("energy_offset_pct").is_not_null())
            ["energy_offset_pct"].median()
        )
        print(f"Median energy_offset_pct (all scored): {med_off:.2f}%")
        print(f"  (Expected: low single-digit, ~0.8%)")

    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Read-only MINREV what-if analysis (F4-OFFSET)"
    )
    parser.add_argument(
        "--parquet",
        type=Path,
        default=_DEFAULT_PARQUET,
        help="Path to financial_scorecards.parquet (default: data/processed/phase4/)",
    )
    args = parser.parse_args()
    main(args.parquet)
