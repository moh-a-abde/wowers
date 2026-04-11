"""Filter ICIS facilities and permits to active POTWs only."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from src.common import config, logging_setup

log = logging_setup.get("wowers.phase1.filter_potw")

# Output schema — enforced after join
POTW_SCHEMA = {
    "npdes_id": pl.Utf8,
    "facility_name": pl.Utf8,
    "city": pl.Utf8,
    "state_code": pl.Utf8,
    "zip": pl.Utf8,
    "latitude": pl.Float64,
    "longitude": pl.Float64,
    "facility_type_indicator": pl.Utf8,
    "facility_type_code": pl.Utf8,
    "major_minor": pl.Utf8,
    "design_flow_mgd": pl.Float64,
    "actual_avg_flow_mgd": pl.Float64,
    "permit_status_code": pl.Utf8,
}


def load_potw_facilities(
    facilities_csv: Path,
    permits_csv: Path,
) -> pl.DataFrame:
    """Read, filter, and join ICIS CSVs to produce the POTW facility table.

    Returns a DataFrame conforming to POTW_SCHEMA (~16,000 rows expected).
    """
    log.info("Loading ICIS_FACILITIES.CSV …")
    facilities = _load_facilities(facilities_csv)

    log.info("Loading ICIS_PERMITS.CSV …")
    permits = _load_permits(permits_csv)

    log.info(f"Raw facilities: {len(facilities):,} | Raw permits: {len(permits):,}")

    potw_permits = _filter_potw_permits(permits)
    log.info(f"POTW permits after filter: {len(potw_permits):,}")

    joined = _join(facilities, potw_permits)
    log.info(f"POTW facilities after join: {len(joined):,}")

    result = _cast_schema(joined)
    _log_summary(result)
    return result


# ── Loading ───────────────────────────────────────────────────────────────────

def _load_facilities(path: Path) -> pl.DataFrame:
    df = pl.read_csv(
        path,
        infer_schema_length=10000,
        null_values=["", "NULL", "null", "N/A"],
        ignore_errors=True,
        encoding="utf8-lossy",
    )
    # Normalise column names to uppercase
    df = df.rename({c: c.upper().strip() for c in df.columns})

    keep = {
        "NPDES_ID": "npdes_id",
        "FACILITY_TYPE_CODE": "facility_type_code",
        "FACILITY_NAME": "facility_name",
        "LOCATION_ADDRESS": "location_address",
        "CITY": "city",
        "STATE_CODE": "state_code",
        "ZIP": "zip",
        "GEOCODE_LATITUDE": "latitude",
        "GEOCODE_LONGITUDE": "longitude",
    }
    # Only keep columns that exist in the actual file
    rename_map = {k: v for k, v in keep.items() if k in df.columns}
    df = df.select(list(rename_map.keys())).rename(rename_map)

    return df.with_columns([
        pl.col("npdes_id").cast(pl.Utf8).str.strip_chars(),
        pl.col("latitude").cast(pl.Float64, strict=False),
        pl.col("longitude").cast(pl.Float64, strict=False),
    ])


def _load_permits(path: Path) -> pl.DataFrame:
    df = pl.read_csv(
        path,
        infer_schema_length=10000,
        null_values=["", "NULL", "null", "N/A"],
        ignore_errors=True,
        encoding="utf8-lossy",
    )
    df = df.rename({c: c.upper().strip() for c in df.columns})

    keep = {
        "EXTERNAL_PERMIT_NMBR": "npdes_id",
        "FACILITY_TYPE_INDICATOR": "facility_type_indicator",
        "TOTAL_DESIGN_FLOW_NMBR": "design_flow_mgd",
        "ACTUAL_AVERAGE_FLOW_NMBR": "actual_avg_flow_mgd",
        "MAJOR_MINOR_STATUS_FLAG": "major_minor",
        "PERMIT_STATUS_CODE": "permit_status_code",
    }
    rename_map = {k: v for k, v in keep.items() if k in df.columns}
    df = df.select(list(rename_map.keys())).rename(rename_map)

    return df.with_columns([
        pl.col("npdes_id").cast(pl.Utf8).str.strip_chars(),
        pl.col("design_flow_mgd").cast(pl.Float64, strict=False),
        pl.col("actual_avg_flow_mgd").cast(pl.Float64, strict=False),
    ])


# ── Filtering ─────────────────────────────────────────────────────────────────

def _filter_potw_permits(permits: pl.DataFrame) -> pl.DataFrame:
    cfg_types = config.get("potw_filter.facility_type_indicators", ["POTW"])
    cfg_statuses = config.get("potw_filter.active_permit_status_codes", ["EFF", "NON"])
    cfg_exclude_codes = config.get("potw_filter.exclude_facility_type_codes", ["FDF"])

    # Normalise to uppercase
    permits = permits.with_columns(
        pl.col("facility_type_indicator").str.strip_chars().str.to_uppercase(),
        pl.col("permit_status_code").str.strip_chars().str.to_uppercase()
        if "permit_status_code" in permits.columns else pl.lit(None).alias("permit_status_code"),
    )

    # Filter: type must be in allowed list
    type_filter = pl.col("facility_type_indicator").is_in(
        [t.upper() for t in cfg_types]
    )

    # Filter: permit must be active (if column exists and is non-null)
    if "permit_status_code" in permits.columns:
        status_filter = (
            pl.col("permit_status_code").is_null()
            | pl.col("permit_status_code").is_in([s.upper() for s in cfg_statuses])
        )
        permits = permits.filter(type_filter & status_filter)
    else:
        permits = permits.filter(type_filter)

    # Deduplicate: keep one row per NPDES ID (largest design flow wins)
    if "design_flow_mgd" in permits.columns:
        permits = (
            permits.sort("design_flow_mgd", descending=True, nulls_last=True)
            .unique(subset=["npdes_id"], keep="first")
        )
    else:
        permits = permits.unique(subset=["npdes_id"], keep="first")

    return permits


# ── Join ──────────────────────────────────────────────────────────────────────

def _join(facilities: pl.DataFrame, permits: pl.DataFrame) -> pl.DataFrame:
    # Left join: facilities is the left table so we keep all POTW permits
    # even if facility record is missing (will have null location fields)
    joined = permits.join(facilities, on="npdes_id", how="left")

    # Drop rows with no location at all (can't be used for mapping or elevation)
    before = len(joined)
    joined = joined.filter(
        pl.col("latitude").is_not_null() & pl.col("longitude").is_not_null()
    )
    dropped = before - len(joined)
    if dropped > 0:
        log.warning(f"Dropped {dropped:,} facilities with no coordinates")

    return joined


# ── Schema cast ───────────────────────────────────────────────────────────────

def _cast_schema(df: pl.DataFrame) -> pl.DataFrame:
    casts = []
    for col, dtype in POTW_SCHEMA.items():
        if col in df.columns:
            casts.append(pl.col(col).cast(dtype, strict=False))
        else:
            casts.append(pl.lit(None).cast(dtype).alias(col))
    return df.with_columns(casts).select(list(POTW_SCHEMA.keys()))


# ── Summary ───────────────────────────────────────────────────────────────────

def _log_summary(df: pl.DataFrame) -> None:
    total = len(df)
    with_design_flow = df.filter(pl.col("design_flow_mgd").is_not_null()).shape[0]
    major = df.filter(pl.col("major_minor") == "M").shape[0]
    by_state = df.group_by("state_code").len().sort("len", descending=True)

    log.info(f"POTW facilities: {total:,} total")
    log.info(f"  With design flow: {with_design_flow:,} ({with_design_flow/total*100:.1f}%)")
    log.info(f"  Major facilities: {major:,}")
    log.info(f"  States covered:   {df['state_code'].n_unique()}")
    top5 = by_state.head(5)
    for row in top5.iter_rows(named=True):
        log.info(f"  {row['state_code']}: {row['len']:,} plants")
