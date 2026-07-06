"""GeoJSON export for the WOWERS frontend map demo.

Reads the Phase 4 financial scorecard + Phase 1 facility coordinates and
exports the 1,138 project-viable sites (post P2-SEED re-baseline) as a GeoJSON FeatureCollection.

The output file (exports/viable_sites.geojson) is git-tracked and intended
as the static data source for the vite+react+maplibre frontend map.

COORDINATE ORDER: [longitude, latitude] per GeoJSON spec (RFC 7946 §3.1.1).
``geometry.coordinates = [longitude, latitude]`` — NOT [lat, lon].

ROUNDING:
  USD and kWh columns  → rounded to integer
  Ratio columns (irr, lcoe_per_kwh, capacity_factor, energy_offset_pct)
                       → rounded to 4 decimal places
  Coordinates          → rounded to 5 decimal places (≈ 1 m precision)
  Null / inf / NaN     → JSON null (frontend handles gracefully)

USAGE:
    python scripts/export_geojson.py                   # viable only (default)
    python scripts/export_geojson.py --all             # all 3,778 scored sites (post P2-SEED)
    python scripts/export_geojson.py --out path.geojson
    python scripts/export_geojson.py --scorecard path --p1 path
"""

from __future__ import annotations

import argparse
import json
import logging
import math
from pathlib import Path
from typing import Any

import polars as pl

ROOT = Path(__file__).resolve().parents[1]

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("wowers.export_geojson")

# ── Default paths ─────────────────────────────────────────────────────────────

_DEFAULT_SCORECARD = ROOT / "data/processed/phase4/financial_scorecards.parquet"
_DEFAULT_P1        = ROOT / "data/processed/phase1/ranked_candidates.parquet"
_DEFAULT_OUT       = ROOT / "exports/viable_sites.geojson"

# ── Property list (exact order as specified) ──────────────────────────────────

PROPERTIES: list[str] = [
    "npdes_id",
    "facility_name",
    "city",
    "state_code",
    "turbine_type",
    "rated_power_kw",
    "annual_energy_kwh",
    "energy_kwh_calib_floor_p25",
    "energy_kwh_calib_floor_p50",
    "energy_kwh_calib_central",
    "capacity_factor",
    "total_capex_usd",
    "npv_usd",
    "irr",
    "payback_years",
    "lcoe_per_kwh",
    "annual_revenue_usd",
    "energy_offset_pct",
    "site_tier",
    "econ_cat_payback",
    "econ_cat_npv",
    "econ_cat_irr",
    "data_quality_tier",
    "project_viable",
]

# Columns whose values are rounded to integer (USD magnitudes + kWh magnitudes)
_INT_COLS: frozenset[str] = frozenset({
    "rated_power_kw",
    "annual_energy_kwh",
    "energy_kwh_calib_floor_p25",
    "energy_kwh_calib_floor_p50",
    "energy_kwh_calib_central",
    "total_capex_usd",
    "npv_usd",
    "annual_revenue_usd",
})

# Columns whose values are rounded to 4 decimal places (ratios / rates)
_RATIO_COLS: frozenset[str] = frozenset({
    "irr",
    "lcoe_per_kwh",
    "capacity_factor",
    "energy_offset_pct",
})

_COORD_PRECISION: int = 5


# ── Pure functions (unit-testable) ────────────────────────────────────────────

def _to_python(val: Any) -> Any:
    """Convert polars/numpy scalar to a Python primitive."""
    if hasattr(val, "item"):
        return val.item()
    return val


def round_property(col: str, val: Any) -> Any:
    """Apply per-column rounding rules; return JSON-safe Python value.

    - _INT_COLS  → int (or null if not finite)
    - _RATIO_COLS→ float rounded to 4 d.p. (or null if not finite)
    - bool       → bool (preserved before int check; bool is subclass of int)
    - int        → int as-is
    - float      → pass-through (None if NaN/inf)
    - other      → pass-through unchanged
    """
    val = _to_python(val)
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if col in _INT_COLS:
        try:
            f = float(val)
            return None if (math.isnan(f) or math.isinf(f)) else int(round(f))
        except (TypeError, ValueError):
            return val
    if col in _RATIO_COLS:
        try:
            f = float(val)
            return None if (math.isnan(f) or math.isinf(f)) else round(f, 4)
        except (TypeError, ValueError):
            return val
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return None if (math.isnan(val) or math.isinf(val)) else val
    return val


def build_feature(row: dict) -> dict | None:
    """Build one GeoJSON Feature dict from a joined row.

    Returns None if latitude or longitude is missing/invalid.
    Coordinates: [longitude, latitude] per GeoJSON spec.
    """
    lat = _to_python(row.get("latitude"))
    lon = _to_python(row.get("longitude"))
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError):
        return None
    if math.isnan(lat_f) or math.isnan(lon_f):
        return None

    props: dict[str, Any] = {
        col: round_property(col, row.get(col))
        for col in PROPERTIES
    }

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [
                round(lon_f, _COORD_PRECISION),
                round(lat_f, _COORD_PRECISION),
            ],
        },
        "properties": props,
    }


def build_feature_collection(
    df: pl.DataFrame,
    *,
    viable_only: bool = True,
) -> tuple[dict, list[str]]:
    """Build a GeoJSON FeatureCollection from the joined scorecard+coords frame.

    Args:
        df:          Joined DataFrame containing all PROPERTIES columns plus
                     ``latitude``, ``longitude``, ``project_viable``.
        viable_only: Include only project_viable == True rows when True.

    Returns:
        (feature_collection_dict, dropped_npdes_ids)
        where dropped_npdes_ids lists sites excluded for null/invalid coords.
    """
    if viable_only:
        df = df.filter(pl.col("project_viable"))

    features: list[dict] = []
    dropped: list[str] = []

    for row in df.to_dicts():
        feat = build_feature(row)
        if feat is None:
            dropped.append(str(row.get("npdes_id", "?")))
        else:
            features.append(feat)

    if dropped:
        log.warning(
            "Excluded %d site(s) with null/invalid lat-lon: %s",
            len(dropped), dropped[:20],
        )

    return {"type": "FeatureCollection", "features": features}, dropped


def load_and_join(
    scorecard_path: Path,
    p1_path: Path,
) -> pl.DataFrame:
    """Load Phase 4 scorecard + Phase 1 facility metadata; left-join on npdes_id.

    Phase 1 supplies: facility_name, city, latitude, longitude.
    These are NOT in the scorecard parquet.
    """
    scorecard = pl.read_parquet(scorecard_path)
    p1 = pl.read_parquet(p1_path).select(
        ["npdes_id", "facility_name", "city", "latitude", "longitude"]
    )
    return scorecard.join(p1, on="npdes_id", how="left")


def validate_geojson(fc: dict, expected_features: int) -> None:
    """Assert basic GeoJSON structure, feature count, and coordinate order.

    Raises AssertionError on any mismatch — used in export() and tests.
    """
    assert fc.get("type") == "FeatureCollection", "type must be FeatureCollection"
    feats = fc.get("features", [])
    assert len(feats) == expected_features, (
        f"Expected {expected_features} features, got {len(feats)}"
    )
    for feat in feats[:5]:
        assert feat["type"] == "Feature"
        coords = feat["geometry"]["coordinates"]
        assert len(coords) == 2, "coordinates must be [lon, lat]"
        lon, lat = coords
        assert -180.0 <= lon <= 180.0, f"longitude {lon} out of range"
        assert  -90.0 <= lat <=  90.0, f"latitude {lat} out of range"


# ── IO orchestrator ───────────────────────────────────────────────────────────

def export(
    scorecard_path: Path = _DEFAULT_SCORECARD,
    p1_path: Path = _DEFAULT_P1,
    out_path: Path = _DEFAULT_OUT,
    *,
    viable_only: bool = True,
) -> tuple[Path, int, int]:
    """End-to-end export: load → join → build → validate → write.

    Returns:
        (out_path, n_features_written, n_dropped_for_null_coords)
    """
    df = load_and_join(scorecard_path, p1_path)
    fc, dropped = build_feature_collection(df, viable_only=viable_only)
    n_features = len(fc["features"])
    validate_geojson(fc, n_features)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(fc, fh, separators=(",", ":"))

    log.info(
        "Wrote %d features → %s  (%d dropped for null coords)",
        n_features, out_path, len(dropped),
    )
    return out_path, n_features, len(dropped)


# ── CLI entry ─────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Export WOWERS viable sites as GeoJSON for the frontend map."
    )
    ap.add_argument(
        "--scorecard", type=Path, default=_DEFAULT_SCORECARD,
        help="Path to financial_scorecards.parquet (default: Part A output)",
    )
    ap.add_argument(
        "--p1", type=Path, default=_DEFAULT_P1,
        help="Path to Phase 1 ranked_candidates.parquet",
    )
    ap.add_argument(
        "--out", type=Path, default=_DEFAULT_OUT,
        help=f"Output GeoJSON path (default: {_DEFAULT_OUT})",
    )
    ap.add_argument(
        "--all", dest="all_sites", action="store_true",
        help="Export all scored sites, not just project_viable==True",
    )
    args = ap.parse_args()

    out_path, n_features, n_dropped = export(
        scorecard_path=args.scorecard,
        p1_path=args.p1,
        out_path=args.out,
        viable_only=not args.all_sites,
    )
    print(f"Features written  : {n_features:,}")
    print(f"Dropped (no coord): {n_dropped}")
    print(f"Output            : {out_path}")


if __name__ == "__main__":
    main()
