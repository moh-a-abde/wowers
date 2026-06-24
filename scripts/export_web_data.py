"""Export pipeline outputs (phases 1-4) to static web artifacts for the dashboard.

Produces, under ``frontend/public/data/``:
  - plants.geojson            one point per scored site, slim props for the map + filters
  - national.json             national KPIs, viable-by-state histogram, top opportunities
  - portfolio/<STATE>.json     per-state ranked table rows + aggregates
  - plants/<npdes_id>.json     full per-plant detail record

The frontend fetches these directly; there is no backend.

Run:  .venv/bin/python -m scripts.export_web_data      (or python scripts/export_web_data.py)
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P1 = ROOT / "data/processed/phase1/ranked_candidates.parquet"
P2 = ROOT / "data/processed/phase2/energy_yield_estimates.parquet"
P3 = ROOT / "data/processed/phase3/turbine_sizing.parquet"
P4 = ROOT / "data/processed/phase4/financial_scorecards.parquet"
OUT = ROOT / "frontend/public/data"

PAYBACK_SENTINEL = 1e5  # values >= this are "never pays back" (pipeline uses 1e6)


# ── JSON-safe helpers ──────────────────────────────────────────────────────────
def num(v, ndigits: int | None = None):
    """Return a JSON-safe number, or None for NaN/inf/sentinel/missing."""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return round(f, ndigits) if ndigits is not None else f


def payback(v):
    f = num(v, 2)
    if f is None or f >= PAYBACK_SENTINEL:
        return None
    return f


def text(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    return str(v)


# ── Derived classifications ────────────────────────────────────────────────────
def viability_band(pb) -> str:
    """Map payback (years) to the mockup's legend bands."""
    if pb is None:
        return "nonviable"
    if pb < 5:
        return "high"
    if pb <= 15:
        return "moderate"
    if pb <= 20:
        return "marginal"
    return "nonviable"


def confidence(data_quality: str | None, high_conf: bool) -> str:
    """High / Medium / Lower from flow-data quality + viability confidence."""
    if high_conf:
        return "High"
    if data_quality == "dmr":
        return "High"
    if data_quality == "dmr_limited":
        return "Medium"
    return "Lower"


def dmr_backed(data_quality: str | None) -> bool:
    return data_quality in ("dmr", "dmr_limited")


# ── Load + join ────────────────────────────────────────────────────────────────
def load_master() -> tuple[pd.DataFrame, int]:
    p1 = pd.read_parquet(P1)
    p2 = pd.read_parquet(P2)
    p3 = pd.read_parquet(P3)
    p4 = pd.read_parquet(P4)
    total_analyzed = len(p1)

    p1_cols = ["npdes_id", "facility_name", "city", "state_code", "zip",
               "latitude", "longitude", "mean_flow_mgd", "p10_flow_mgd",
               "p90_flow_mgd", "n_months_data", "utilization_ratio", "rank"]
    p2_cols = ["npdes_id", "energy_p10_kwh_yr", "energy_p50_kwh_yr",
               "energy_p90_kwh_yr", "equivalent_homes_p50"]
    p3_cols = ["npdes_id", "head_net_m", "head_gross_m", "elevation_m",
               "elev_outfall_m", "head_source", "head_confidence",
               "q_rated_m3s", "peak_efficiency_pct"]

    df = p4.merge(p1[[c for c in p1_cols if c in p1.columns]], on="npdes_id",
                  how="left", suffixes=("", "_p1"))
    df = df.merge(p2[[c for c in p2_cols if c in p2.columns]], on="npdes_id", how="left")
    df = df.merge(p3[[c for c in p3_cols if c in p3.columns]], on="npdes_id", how="left")
    return df, total_analyzed


# ── Record builders ─────────────────────────────────────────────────────────────
def map_props(r) -> dict:
    pb = payback(r.payback_years)
    return {
        "id": r.npdes_id,
        "name": text(r.facility_name),
        "city": text(r.city),
        "state": text(r.state_code),
        "turbine": text(r.turbine_type),
        "rated_kw": num(r.rated_power_kw, 0),
        "energy_mwh": num((r.annual_energy_kwh or 0) / 1e3, 0),
        "payback": pb,
        "npv": num(r.npv_usd, 0),
        "tier": text(r.site_tier),
        "viable": bool(r.project_viable),
        "band": viability_band(pb),
        "confidence": confidence(text(r.data_quality),
                                 bool(r.project_viable_high_confidence)),
    }


def detail_record(r) -> dict:
    pb = payback(r.payback_years)
    dq = text(r.data_quality)
    return {
        "id": r.npdes_id,
        "name": text(r.facility_name),
        "city": text(r.city),
        "state": text(r.state_code),
        "lat": num(r.latitude, 6),
        "lon": num(r.longitude, 6),
        "confidence": confidence(dq, bool(r.project_viable_high_confidence)),
        "dmr_backed": dmr_backed(dq),
        "viable": bool(r.project_viable),
        "tier": text(r.site_tier),
        "flow": {
            "mean_mgd": num(r.mean_flow_mgd, 1),
            "p10_mgd": num(r.p10_flow_mgd, 1),
            "p90_mgd": num(r.p90_flow_mgd, 1),
            "n_months_dmr": num(r.n_months_data, 0),
            "utilization": num(r.utilization_ratio, 2),
            "data_quality": dq,
        },
        "energy": {
            "p10_mwh": num((r.energy_p10_kwh_yr or 0) / 1e3, 0),
            "p50_mwh": num((r.energy_p50_kwh_yr or 0) / 1e3, 0),
            "p90_mwh": num((r.energy_p90_kwh_yr or 0) / 1e3, 0),
            "equivalent_homes": num(r.equivalent_homes_p50, 0),
            "annual_kwh": num(r.annual_energy_kwh, 0),
            "offset_pct": num(r.energy_offset_pct, 2),
        },
        "elevation": {
            "head_source": text(r.head_source),
            "head_net_m": num(r.head_net_m, 1),
            "head_gross_m": num(r.head_gross_m, 1),
            "facility_elev_m": num(r.elevation_m, 0),
            "outfall_elev_m": num(r.elev_outfall_m, 0),
            "head_confidence": text(r.head_confidence),
        },
        "turbine": {
            "type": text(r.turbine_type),
            "rated_power_kw": num(r.rated_power_kw, 0),
            "rated_flow_m3s": num(r.q_rated_m3s, 1),
            "peak_efficiency_pct": num(r.peak_efficiency_pct, 0),
            "capacity_factor": num(r.capacity_factor, 2),
        },
        "financial": {
            "npv_usd": num(r.npv_usd, 0),
            "npv_with_grant_usd": num(r.npv_with_50pct_grant_usd, 0),
            "irr": num(r.irr, 4),
            "payback_years": pb,
            "lcoe_per_kwh": num(r.lcoe_per_kwh, 4),
            "annual_revenue_usd": num(r.annual_revenue_usd, 0),
            "annual_opex_usd": num(r.annual_opex_usd, 0),
            "elec_rate_per_kwh": num(r.elec_rate_per_kwh, 4),
            "capex": {
                "total_usd": num(r.total_capex_usd, 0),
                "equipment_usd": num(r.equipment_capex_usd, 0),
                "installation_usd": num(r.installation_capex_usd, 0),
                "interconnection_usd": num(r.interconnection_capex_usd, 0),
                "permitting_usd": num(r.permitting_capex_usd, 0),
                "permitting_tier": text(r.permitting_tier),
            },
        },
        "sensitivity": {
            "head": [num(r.sensitivity_head_npv_low, 0), num(r.sensitivity_head_npv_high, 0)],
            "flow": [num(r.sensitivity_flow_npv_low, 0), num(r.sensitivity_flow_npv_high, 0)],
            "rate": [num(r.sensitivity_rate_npv_low, 0), num(r.sensitivity_rate_npv_high, 0)],
            "dominant": text(r.dominant_sensitivity),
        },
    }


def table_row(r) -> dict:
    pb = payback(r.payback_years)
    return {
        "id": r.npdes_id,
        "name": text(r.facility_name),
        "city": text(r.city),
        "flow_mgd": num(r.mean_flow_mgd, 0),
        "turbine": text(r.turbine_type),
        "capex_usd": num(r.total_capex_usd, 0),
        "annual_savings_usd": num(r.annual_revenue_usd, 0),
        "payback": pb,
        "npv_usd": num(r.npv_usd, 0),
        "energy_mwh": num((r.annual_energy_kwh or 0) / 1e3, 0),
        "confidence": confidence(text(r.data_quality),
                                 bool(r.project_viable_high_confidence)),
        "band": viability_band(pb),
        "viable": bool(r.project_viable),
    }


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, separators=(",", ":")))


# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    df, total_analyzed = load_master()
    df = df.sort_values("npv_usd", ascending=False).reset_index(drop=True)
    viable = df[df.project_viable].copy()

    # 1) plants.geojson
    features = [{
        "type": "Feature",
        "geometry": {"type": "Point",
                     "coordinates": [num(r.longitude, 6), num(r.latitude, 6)]},
        "properties": map_props(r),
    } for r in df.itertuples() if pd.notna(r.latitude) and pd.notna(r.longitude)]
    write_json(OUT / "plants.geojson",
               {"type": "FeatureCollection", "features": features})

    # 2) national.json
    by_state = (viable.groupby("state_code").size()
                .sort_values(ascending=False))
    top = [{
        "id": r.npdes_id, "name": text(r.facility_name), "city": text(r.city),
        "state": text(r.state_code), "energy_mwh": num((r.annual_energy_kwh or 0) / 1e3, 0),
        "payback": payback(r.payback_years), "npv_usd": num(r.npv_usd, 0),
    } for r in viable.head(5).itertuples()]
    national = {
        "plants_analyzed": total_analyzed,
        "scored_sites": int(len(df)),
        "viable_projects": int(len(viable)),
        "tier_a_sites": int((df.site_tier == "A").sum()),
        "high_confidence_sites": int(viable.project_viable_high_confidence.sum()),
        "portfolio_npv_usd": num(viable.npv_usd.sum(), 0),
        "portfolio_capex_usd": num(viable.total_capex_usd.sum(), 0),
        "annual_savings_usd": num(viable.annual_revenue_usd.sum(), 0),
        "viable_energy_mwh": num(viable.annual_energy_kwh.sum() / 1e3, 0),
        "median_payback": num(viable.payback_years[viable.payback_years < PAYBACK_SENTINEL].median(), 1),
        "by_state": [{"state": s, "viable": int(n)} for s, n in by_state.items()],
        "top_opportunities": top,
    }
    write_json(OUT / "national.json", national)

    # 3) portfolio/<STATE>.json
    for state, g in df.groupby("state_code"):
        if not isinstance(state, str) or not state:
            continue
        g = g.sort_values("npv_usd", ascending=False).reset_index(drop=True)
        gv = g[g.project_viable]
        rows = []
        for i, r in enumerate(g.itertuples(), start=1):
            row = table_row(r)
            row["rank"] = i
            rows.append(row)
        pv = gv.payback_years[gv.payback_years < PAYBACK_SENTINEL]
        write_json(OUT / "portfolio" / f"{state}.json", {
            "state": state,
            "n_scored": int(len(g)),
            "n_viable": int(len(gv)),
            "combined_npv_usd": num(gv.npv_usd.sum(), 0),
            "annual_savings_usd": num(gv.annual_revenue_usd.sum(), 0),
            "total_capex_usd": num(gv.total_capex_usd.sum(), 0),
            "avg_payback": num(pv.mean(), 1),
            "high_confidence_sites": int(gv.project_viable_high_confidence.sum()),
            "rows": rows,
        })

    # 4) plants/<npdes_id>.json
    pdir = OUT / "plants"
    for r in df.itertuples():
        write_json(pdir / f"{r.npdes_id}.json", detail_record(r))

    print(f"Exported {len(features):,} map features, "
          f"{df.state_code.nunique()} states, {len(df):,} plant detail files.")
    print(f"National: {national['viable_projects']:,} viable / "
          f"{national['viable_energy_mwh']:,.0f} MWh/yr / "
          f"${(national['portfolio_capex_usd'] or 0)/1e6:,.1f}M CapEx / "
          f"median payback {national['median_payback']} yr")
    print(f"Output → {OUT}")


if __name__ == "__main__":
    main()
