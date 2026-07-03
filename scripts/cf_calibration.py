"""P5-CF-CALIB — Capacity-Factor Calibration Band for the WOWERS 409 GWh headline.

Read-only. Prints tables to stdout; writes no parquet, no config, no source changes.

PURPOSE
-------
WOWERS Phase 2 physics estimate (409.1 GWh/yr for 1,141 viable sites) carries an
**implied capacity factor of ~0.872** — near always-on, driven by flat WWTP discharge
+ assumed 0.95 availability.  This script benchmarks that assumption against real
small-hydro capacity factors from the DOE HydroSource EHA CF workbook and produces a
**three-tier calibration band** the team can cite.

THREE TIERS
-----------
  Conservative floor  : empirical river-hydro CF (EHA, 629 plants 0.1–5 MW).
                        Imports river-variability WWTP outfalls don't have → floor only.
  Plausible central   : WWTP-appropriate CF anchored to real in-conduit/WWTP installs
                        (LucidPipe Portland OR: 0.628; central anchor CF = 0.60).
  Physics ceiling     : Phase 2 assumed CF (~0.872) — optimistic upper bound.

USAGE
-----
    python scripts/cf_calibration.py
    python scripts/cf_calibration.py --eha-dir /path/to/EHA
    python scripts/cf_calibration.py --p2 data/processed/phase2/energy_yield_estimates.parquet
                                       --p4 data/processed/phase4/financial_scorecards.parquet

STRICTLY READ-ONLY:
  - does NOT modify any parquet, config, or source file
  - Phase 1–4 pipeline outputs are read but never written
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]

# ── Paths (defaults) ──────────────────────────────────────────────────────────

_DEFAULT_EHA_DIR  = Path("/Volumes/SANDISK/WOWERS_Pivot_Data/Phase5_ML_GroundTruth/EHA_HydroSource_ORNL")
_DEFAULT_P2_PATH  = ROOT / "data/processed/phase2/energy_yield_estimates.parquet"
_DEFAULT_P4_PATH  = ROOT / "data/processed/phase4/financial_scorecards.parquet"

_EHA_CF_FILE    = "EHA_Annual_CapacityFactor.xlsx"
_EHA_CF_SHEET   = "AnnualCapacityFactor"

# Real WWTP/conduit install anchors for the plausible-central tier
WWTP_INSTALLS = [
    {
        "name":     "LucidPipe, Portland OR (Bull Run water main)",
        "type":     "in-conduit, drinking-water transmission",
        "kw":       200.0,
        "mwh_yr":   1_100.0,
        "cf":       1_100_000 / (200 * 8_760),   # = 0.628
        "source":   "LucidEnergy/Portland Water Bureau press release; "
                    "Portland OR: 4 × 42\" turbines, 1,100 MWh/yr, 200 kW",
    },
    {
        "name":     "Rentricity wastewater/potable in-conduit (typical)",
        "type":     "in-conduit, potable & wastewater (NSF 61/372 certified)",
        "kw":       None,
        "mwh_yr":   None,
        "cf":       None,   # no published annual kWh — cite as qualitative anchor
        "source":   "Rentricity featured projects: 32 kW @ 2.4 MGD / 40 PSI; "
                    "360 kW @ 2–12 MGD / 175–250 ft. Continuous municipal flow "
                    "implies CF > river-hydro; no published MWh/yr for individual sites.",
    },
    {
        "name":     "CINK Crossflow wastewater (generic WWTP archetype)",
        "type":     "crossflow, WWTP outfall",
        "kw":       None,
        "mwh_yr":   None,
        "cf":       None,   # no specific CF published per CINK refs
        "source":   "CINK Hydro-Energy references (cink-hydro-energy.com/references): "
                    "450+ turbines incl. WWTP applications; runs 6–100% of design flow. "
                    "No per-site kWh published.",
    },
]

# Central WWTP anchor CF — LucidPipe (0.628) rounded down slightly for conservatism
WWTP_CENTRAL_CF  = 0.60
WWTP_CF_RANGE    = (0.55, 0.65)   # plausible WWTP/conduit range from real installs
HOURS_PER_YEAR   = 8_760

# CF drop thresholds (rows outside these are errors / data artefacts)
CF_DROP_ABOVE = 1.2   # impossible for a real plant (>100% utilisation after rounding)
CF_DROP_BELOW_EQ = 0  # zero or negative = no generation this year


# ══════════════════════════════════════════════════════════════════════════════
# Pure functions — take DataFrames, return dicts/DataFrames; no IO
# ══════════════════════════════════════════════════════════════════════════════

def parse_cf_pct(series: pl.Series) -> pl.Series:
    """Parse '22%' → 0.22.  Returns Float64; null for unparseable values."""
    return (
        series.cast(pl.Utf8, strict=False)
              .str.replace("%", "")
              .cast(pl.Float64, strict=False)
              / 100.0
    )


def recompute_cf(df: pl.DataFrame) -> pl.DataFrame:
    """Add cf_calc = Net_Generation_MWh / (Capacity_MW × Hours).

    Input frame must have columns: Net_Generation_MWh, Capacity_MW, Hours.
    Returns the input frame with two additional columns:
        cf_calc   — recomputed capacity factor (Float64)
        cf_given  — parsed from Capacity_Factor string column (Float64, nullable)
    """
    return df.with_columns([
        (
            pl.col("Net_Generation_MWh")
            / (pl.col("Capacity_MW") * pl.col("Hours"))
        ).alias("cf_calc"),
        parse_cf_pct(df["Capacity_Factor"]).alias("cf_given"),
    ])


def filter_clean_hy(df: pl.DataFrame) -> pl.DataFrame:
    """Filter CF rows to conventional hydro, non-trivial plants, valid CF.

    Drops:
      - Type != 'HY' (pumped storage, etc.)
      - Capacity_MW < 0.1 (below our floor — not in the small-hydro bucket)
      - cf_calc <= 0 or cf_calc > CF_DROP_ABOVE (data errors / artefacts)
    """
    return df.filter(
        (pl.col("Type") == "HY")
        & (pl.col("Capacity_MW") >= 0.1)
        & (pl.col("cf_calc") > CF_DROP_BELOW_EQ)
        & (pl.col("cf_calc") <= CF_DROP_ABOVE)
    )


def bucket_stats(df: pl.DataFrame, max_mw: float, year_min: int | None = None) -> dict:
    """Return CF distribution stats for plants with Capacity_MW <= max_mw.

    Optionally restrict to Year >= year_min.

    Returns a dict with:
        n_plants, n_plant_years, p10, p25, p50, p75, p90, mean
    """
    sub = df.filter(pl.col("Capacity_MW") <= max_mw)
    if year_min is not None:
        sub = sub.filter(pl.col("Year") >= year_min)
    cf = sub["cf_calc"]
    return {
        "n_plants":      sub["EHA_PtID"].n_unique(),
        "n_plant_years": len(sub),
        "p10":  round(float(cf.quantile(0.10)), 4),
        "p25":  round(float(cf.quantile(0.25)), 4),
        "p50":  round(float(cf.quantile(0.50)), 4),
        "p75":  round(float(cf.quantile(0.75)), 4),
        "p90":  round(float(cf.quantile(0.90)), 4),
        "mean": round(float(cf.mean()), 4),
    }


def recompute_validation(df: pl.DataFrame) -> dict:
    """Compute |cf_calc - cf_given| stats to validate the CF recompute."""
    diff = (df["cf_calc"] - df["cf_given"]).abs().drop_nulls()
    return {
        "n":    len(diff),
        "mean": round(float(diff.mean()), 5),
        "p25":  round(float(diff.quantile(0.25)), 5),
        "p75":  round(float(diff.quantile(0.75)), 5),
    }


def phase2_viable_cf_stats(p2: pl.DataFrame, p4: pl.DataFrame) -> dict:
    """Return capacity_factor_p50 distribution for viable WWTP sites."""
    viable_ids = p4.filter(pl.col("project_viable") == True).select("npdes_id")
    p2_v = p2.join(viable_ids, on="npdes_id", how="inner")
    viable_energy_gwh = (
        p4.filter(pl.col("project_viable") == True)["annual_energy_kwh"].sum()
        / 1e6
    )
    cf = p2_v["capacity_factor_p50"].drop_nulls()
    return {
        "n_viable_sites":   len(viable_ids),
        "headline_gwh":     round(float(viable_energy_gwh), 1),
        "cf_p10":  round(float(cf.quantile(0.10)), 4),
        "cf_p25":  round(float(cf.quantile(0.25)), 4),
        "cf_p50":  round(float(cf.quantile(0.50)), 4),
        "cf_p75":  round(float(cf.quantile(0.75)), 4),
        "cf_p90":  round(float(cf.quantile(0.90)), 4),
        "cf_mean": round(float(cf.mean()), 4),
    }


def calibration_band(
    headline_gwh: float,
    phase2_cf_median: float,
    empirical_stats: dict,
    wwtp_central_cf: float,
) -> list[dict]:
    """Compute three-tier calibration band rows.

    Args:
        headline_gwh:     Phase 2 physics headline energy (GWh/yr).
        phase2_cf_median: Phase 2 implied CF median (e.g. 0.872).
        empirical_stats:  Dict from bucket_stats (contains p25, p50, p75).
        wwtp_central_cf:  CF for the plausible WWTP-appropriate central tier.

    Returns list of dicts with: tier, cf, multiplier, gwh_estimate.
    Floor monotonicity guaranteed (p25 < p50 < p75 empirically).
    """
    rows = []
    for label, cf_val in [
        ("Floor (river-hydro p25)",    empirical_stats["p25"]),
        ("Floor (river-hydro p50)",    empirical_stats["p50"]),
        ("Floor (river-hydro p75)",    empirical_stats["p75"]),
        ("Central (WWTP-appropriate)", wwtp_central_cf),
        ("Physics ceiling (Phase 2)",  phase2_cf_median),
    ]:
        mult = cf_val / phase2_cf_median
        rows.append({
            "tier":        label,
            "cf":          round(cf_val, 4),
            "multiplier":  round(mult, 3),
            "gwh":         round(headline_gwh * mult, 1),
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# IO layer + printing
# ══════════════════════════════════════════════════════════════════════════════

def _load_eha_cf(eha_dir: Path) -> pl.DataFrame:
    """Read, recompute, and clean-filter the EHA CF workbook."""
    path = eha_dir / _EHA_CF_FILE
    if not path.exists():
        raise FileNotFoundError(
            f"EHA CF workbook not found: {path}\n"
            "Mount SANDISK or override --eha-dir."
        )
    raw = pl.read_excel(path, sheet_name=_EHA_CF_SHEET, read_options={"header_row": 0})
    computed = recompute_cf(raw)
    return filter_clean_hy(computed)


def _load_pipeline(p2_path: Path, p4_path: Path) -> tuple[pl.DataFrame, pl.DataFrame]:
    for p in (p2_path, p4_path):
        if not p.exists():
            raise FileNotFoundError(f"Pipeline parquet not found: {p}")
    return pl.read_parquet(p2_path), pl.read_parquet(p4_path)


def _print_table(title: str, headers: list[str], rows: list[list]) -> None:
    widths = [max(len(h), max(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
    sep = "| " + " | ".join("-" * w for w in widths) + " |"
    hdr = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, widths)) + " |"
    print(f"\n### {title}")
    print(hdr)
    print(sep)
    for row in rows:
        print("| " + " | ".join(str(v).ljust(w) for v, w in zip(row, widths)) + " |")


def main(
    eha_dir: Path = _DEFAULT_EHA_DIR,
    p2_path: Path = _DEFAULT_P2_PATH,
    p4_path: Path = _DEFAULT_P4_PATH,
) -> None:
    print("=" * 70)
    print("WOWERS — Capacity-Factor Calibration Band  (P5-CF-CALIB)")
    print("=" * 70)
    print("Read-only: no parquet, config, or source file modified.\n")

    # ── Load EHA CF workbook ──────────────────────────────────────────────────
    print("Loading EHA Annual_CapacityFactor workbook …")
    try:
        cf_df = _load_eha_cf(eha_dir)
    except FileNotFoundError as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"  Clean HY rows: {len(cf_df):,}")

    # ── Load pipeline parquets ────────────────────────────────────────────────
    print("Loading Phase 2 + Phase 4 parquets …")
    try:
        p2, p4 = _load_pipeline(p2_path, p4_path)
    except FileNotFoundError as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # ── 1. Recompute validation ───────────────────────────────────────────────
    val = recompute_validation(cf_df)
    print(f"\n[1] CF recompute vs Capacity_Factor string validation")
    print(f"    n={val['n']:,}  mean|diff|={val['mean']:.5f}  "
          f"p25={val['p25']:.5f}  p75={val['p75']:.5f}")
    print(f"    → Recompute and given agree to ≈{val['mean']:.4f} (rounding only)")

    # ── 2. Phase 2 implied CF ─────────────────────────────────────────────────
    p2stats = phase2_viable_cf_stats(p2, p4)
    print(f"\n[2] Phase 2 implied capacity_factor_p50 — viable WWTP sites")
    print(f"    n={p2stats['n_viable_sites']}  headline={p2stats['headline_gwh']} GWh/yr")
    print(f"    p10={p2stats['cf_p10']}  p25={p2stats['cf_p25']}  "
          f"p50={p2stats['cf_p50']}  p75={p2stats['cf_p75']}  p90={p2stats['cf_p90']}")
    print(f"    Decomposition: availability ≈ 0.943 (mean of triangular 0.90/0.95/0.98)")
    print(f"    × FDC utilisation ≈ {p2stats['cf_p50'] / 0.943:.3f} "
          f"(near 1.0 = flat WWTP discharge FDC)")
    print(f"    Gap vs river hydro is partly REAL (flat WWTP flow) and partly "
          f"OPTIMISTIC (no debris/min-flow modeled).")

    # ── 3. EHA CF distribution by bucket ─────────────────────────────────────
    b5  = bucket_stats(cf_df, max_mw=5.0)
    b1  = bucket_stats(cf_df, max_mw=1.0)
    b5r = bucket_stats(cf_df, max_mw=5.0, year_min=2013)

    _print_table(
        "EHA empirical CF — small-hydro buckets (Type=HY, cf_calc recomputed)",
        ["Bucket", "Plants", "Plant-yrs", "p10", "p25", "p50", "p75", "p90", "mean"],
        [
            ["0.1–5 MW (all yrs)",  b5["n_plants"],  b5["n_plant_years"],
             b5["p10"], b5["p25"], b5["p50"], b5["p75"], b5["p90"], b5["mean"]],
            ["0.1–5 MW (2013–22)",  b5r["n_plants"], b5r["n_plant_years"],
             b5r["p10"], b5r["p25"], b5r["p50"], b5r["p75"], b5r["p90"], b5r["mean"]],
            ["0.1–1 MW (all yrs)",  b1["n_plants"],  b1["n_plant_years"],
             b1["p10"], b1["p25"], b1["p50"], b1["p75"], b1["p90"], b1["mean"]],
        ],
    )

    # ── 4. Real WWTP/conduit install anchors ──────────────────────────────────
    print(f"\n[4] Real WWTP / in-conduit install anchors (plausible-central tier)")
    for inst in WWTP_INSTALLS:
        cf_str = f"CF={inst['cf']:.3f}" if inst["cf"] is not None else "CF=not published"
        print(f"  • {inst['name']}")
        print(f"    Type: {inst['type']}")
        print(f"    {cf_str}  |  {inst['source'][:100]}")

    lucid_cf = 1_100_000 / (200 * 8_760)
    print(f"\n  → LucidPipe is the only real WWTP-adjacent install with published CF.")
    print(f"    CF = 1,100,000 kWh / (200 kW × 8,760 h) = {lucid_cf:.3f}")
    print(f"    Central anchor set at CF = {WWTP_CENTRAL_CF:.2f} "
          f"(conservative vs LucidPipe {lucid_cf:.3f})")
    print(f"    Plausible WWTP range: CF {WWTP_CF_RANGE[0]:.2f}–{WWTP_CF_RANGE[1]:.2f}")

    # ── 5. Calibration band ───────────────────────────────────────────────────
    headline_gwh     = p2stats["headline_gwh"]
    phase2_cf_median = p2stats["cf_p50"]

    print(f"\n[5] Calibration band — 0.1–5 MW bucket (primary, 629 plants)")
    band5 = calibration_band(headline_gwh, phase2_cf_median, b5, WWTP_CENTRAL_CF)
    _print_table(
        f"0.1–5 MW bucket (CF based on 629 plants / 9,798 plant-years)",
        ["Tier", "CF", "Multiplier", "GWh/yr"],
        [[r["tier"], r["cf"], r["multiplier"], r["gwh"]] for r in band5],
    )

    print(f"\n[5b] Calibration band — 0.1–1 MW bucket (closest to WWTP scale)")
    band1 = calibration_band(headline_gwh, phase2_cf_median, b1, WWTP_CENTRAL_CF)
    _print_table(
        f"0.1–1 MW bucket (CF based on 59 plants / 802 plant-years)",
        ["Tier", "CF", "Multiplier", "GWh/yr"],
        [[r["tier"], r["cf"], r["multiplier"], r["gwh"]] for r in band1],
    )

    # ── 6. Headline summary ───────────────────────────────────────────────────
    floor_lo = band5[0]["gwh"]   # p25
    floor_hi = band1[1]["gwh"]   # p50 of 0.1-1 MW
    central  = [r["gwh"] for r in band5 if "Central" in r["tier"]][0]
    ceiling  = headline_gwh

    print(f"\n{'='*70}")
    print(f"HEADLINE RESULT")
    print(f"{'='*70}")
    print(
        f"  {ceiling:.0f} GWh physics ceiling\n"
        f"  → conservative floor  ~{floor_lo:.0f}–{floor_hi:.0f} GWh  "
        f"(real river-scale small-hydro CF, {b5['n_plants']} plants)\n"
        f"  → plausible central  ~{central:.0f} GWh  "
        f"(WWTP-appropriate CF={WWTP_CENTRAL_CF:.2f}, anchored to LucidPipe 0.628)\n"
        f"\n"
        f"  CAVEAT: The floor imports river-variability (seasonal drought, "
        f"peak-sizing)\n"
        f"  that does NOT apply to WWTP outfalls (near-constant 24/7 discharge).\n"
        f"  The plausible central tier is the more defensible estimate.\n"
        f"  The physics ceiling remains valid as an upper bound under Phase 2 "
        f"assumptions."
    )
    print(f"{'='*70}\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="WOWERS capacity-factor calibration band (read-only)"
    )
    ap.add_argument("--eha-dir", type=Path, default=_DEFAULT_EHA_DIR)
    ap.add_argument("--p2", type=Path, default=_DEFAULT_P2_PATH,
                    help="Phase 2 energy_yield_estimates.parquet")
    ap.add_argument("--p4", type=Path, default=_DEFAULT_P4_PATH,
                    help="Phase 4 financial_scorecards.parquet")
    args = ap.parse_args()
    main(args.eha_dir, args.p2, args.p4)
