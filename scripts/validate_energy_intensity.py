"""Step 6 validation for the energy-intensity method.

Implements the log-linear interpolation rule from config/energy_intensity.yaml,
applies it to all ranked candidates, and runs the three Step-6 sanity checks:
  6.1  spot-check vs. published large-utility consumption
  6.2  national total (target ~30.2 TWh/yr)
  6.3  offset sanity (turbine output / consumption should be low single-digit %)
"""
import math
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config" / "energy_intensity.yaml").read_text())


def observed_intensity(flow_mgd: float) -> float:
    """kWh/MG point estimate from EPRI Table 5-1 observed flow bands (band lookup)."""
    for b in CFG["observed_flow_band_intensity"]["bands"]:
        if b["max_mgd"] is None or flow_mgd < b["max_mgd"]:
            return float(b["kwh_per_mg"])
    return float(CFG["observed_flow_band_intensity"]["bands"][-1]["kwh_per_mg"])


def intensity(treatment_type: str, flow_mgd: float) -> float:
    """kWh/MG for a treatment type at a given flow, log-linear interpolated,
    clamped at the table edges."""
    t = CFG["treatment_types"][treatment_type]
    sizes = t["size_points_mgd"]
    vals = t["kwh_per_mg"]
    if flow_mgd <= sizes[0]:
        return float(vals[0])
    if flow_mgd >= sizes[-1]:
        return float(vals[-1])
    for i in range(len(sizes) - 1):
        lo, hi = sizes[i], sizes[i + 1]
        if lo <= flow_mgd <= hi:
            vlo, vhi = vals[i], vals[i + 1]
            # log-linear: straight line in log-flow / log-intensity space
            frac = math.log(flow_mgd / lo) / math.log(hi / lo)
            return float(vlo * (vhi / vlo) ** frac)
    return float(vals[-1])


def consumption_kwh_yr(flow_mgd: float, treatment_type: str) -> float:
    return flow_mgd * 365.0 * intensity(treatment_type, flow_mgd)


def main() -> None:
    df = pd.read_parquet(ROOT / "data/processed/phase1/ranked_candidates.parquet")
    df = df[df["mean_flow_mgd"] > 0].copy()

    low = CFG["treatment_assignment"]["sensitivity_low"]
    high = CFG["treatment_assignment"]["sensitivity_high"]

    # Point estimate: observed flow-band averages (Table 5-1)
    df["cons_point_kwh_yr"] = [
        f * 365.0 * observed_intensity(f) for f in df["mean_flow_mgd"]
    ]
    # Sensitivity band: treatment-type curves (Table 5-4)
    for label, ttype in [("low", low), ("high", high)]:
        df[f"cons_{label}_kwh_yr"] = [
            consumption_kwh_yr(f, ttype) for f in df["mean_flow_mgd"]
        ]

    # ---- 6.2 National sanity check ----
    total_flow_mgd = df["mean_flow_mgd"].sum()
    twh = {k: df[f"cons_{k}_kwh_yr"].sum() / 1e9 for k in ("point", "low", "high")}

    print("=" * 64)
    print("STEP 6.2  NATIONAL SANITY CHECK")
    print("=" * 64)
    print(f"Plants with positive flow:        {len(df):,}")
    print(f"Total mean flow:                  {total_flow_mgd:,.0f} MGD")
    print(f"  (EPRI national POTW flow ref:   ~32,000-32,845 MGD)")
    print(f"National consumption  POINT (observed): {twh['point']:.1f} TWh/yr")
    print(f"National consumption  LOW  (TF):        {twh['low']:.1f} TWh/yr")
    print(f"National consumption  HIGH (BNR+N):     {twh['high']:.1f} TWh/yr")
    print(f"  EPRI/EPA reference total:             30.2 TWh/yr")
    print(f"  Point estimate is within "
          f"{abs(twh['point']-30.2)/30.2*100:.0f}% of reference.")
    print()

    # ---- 6.1 Spot-checks vs. published actuals ----
    print("=" * 64)
    print("STEP 6.1  SPOT-CHECKS vs PUBLISHED ACTUALS")
    print("=" * 64)
    # (flow_mgd, published_actual_gwh_yr, source note)
    spot = {
        "MWRA Deer Island": (250.0, 155.0, "~18 MW demand / $16M bill"),
        "DC Water Blue Plains": (290.0, 240.0, "~30 MW total (10 MW=1/3)"),
        "King County West Point": (90.0, None, "no published figure found"),
    }
    print(f"{'Plant':22s} {'MGD':>5s} {'Est':>7s} {'Actual':>8s} {'Err':>6s}  Note")
    for name, (flow, actual, note) in spot.items():
        est = flow * 365.0 * observed_intensity(flow) / 1e6
        if actual:
            err = f"{(est-actual)/actual*100:+.0f}%"
            act = f"{actual:.0f}"
        else:
            err, act = "--", "--"
        print(f"{name:22s} {flow:5.0f} {est:6.0f}G {act:>7s}G {err:>6s}  {note}")
    print()

    print("Point-estimate (observed) intensity at sample flows (kWh/MG):")
    for q in (0.5, 1, 3, 7, 15, 35, 75, 150):
        print(f"  {q:6.1f} MGD -> {observed_intensity(q):6.0f}")

    # ---- 6.3 Offset sanity (illustrative turbine output) ----
    print()
    print("=" * 64)
    print("STEP 6.3  OFFSET SANITY CHECK")
    print("=" * 64)
    p2 = ROOT / "data/processed/phase2/energy_yield_estimates.parquet"
    if p2.exists():
        ey = pd.read_parquet(p2)
        yield_col = "energy_p50_kwh_yr"
        m = df.merge(ey[["npdes_id", yield_col]], on="npdes_id", how="inner")
        m = m[m["cons_point_kwh_yr"] > 0]
        m["offset_pct"] = m[yield_col] / m["cons_point_kwh_yr"] * 100
        print(f"Merged {len(m):,} plants with turbine yield (p50).")
        print(f"  Turbine offset as %% of plant consumption:")
        print(f"    median {m['offset_pct'].median():.2f}%   "
              f"p90 {m['offset_pct'].quantile(0.9):.2f}%   "
              f"p99 {m['offset_pct'].quantile(0.99):.2f}%   "
              f"max {m['offset_pct'].max():.2f}%")
        print("  (Expect low single-digit %% for most plants.)")
    else:
        print("phase2 energy_yield_estimates.parquet not found — skipping 6.3.")


if __name__ == "__main__":
    main()
