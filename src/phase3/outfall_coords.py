"""Phase 3 — NPDES Outfall Coordinate Loader.

Loads outfall discharge-point coordinates from NPDES_PERM_FEATURE_COORDS.csv
(part of the EPA NPDES downloads) and returns one representative outfall per
NPDES permit.  Selection priority:

  1. PERM_FEATURE_NMBR == '001'   (primary discharge outfall)
  2. Lowest numeric PERM_FEATURE_NMBR  (e.g. '002', '003')
  3. First row available

Coordinates sourced from LATITUDE_MEASURE / LONGITUDE_MEASURE columns.
Rows with null or geo-implausible coordinates are dropped.

The default file path is resolved from ``phase3.outfall_coords_path`` in
settings.yaml (falls back to ``data/raw/npdes_downloads/NPDES_PERM_FEATURE_COORDS.csv``).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

import polars as pl

from src.common import config, logging_setup

log = logging_setup.get("wowers.phase3.outfall_coords")

# ── Config ────────────────────────────────────────────────────────────────────

def _cfg(key: str, default=None):
    return config.get(f"phase3.{key}", default)


OUTFALL_COORDS_PATH: Path = (
    config.project_root()
    / _cfg(
        "outfall_coords_path",
        "data/raw/npdes_downloads/NPDES_PERM_FEATURE_COORDS.csv",
    )
)

# Loose bounding box: continental US + AK + HI + territories
_LAT_MIN, _LAT_MAX = 10.0, 72.0
_LON_MIN, _LON_MAX = -180.0, -60.0


# ── Helpers ────────────────────────────────────────────────────────────────────

def _is_valid_coord(lat: float, lon: float) -> bool:
    return _LAT_MIN <= lat <= _LAT_MAX and _LON_MIN <= lon <= _LON_MAX


def _feature_priority(feat: str) -> int:
    """Lower = more preferred.  '001' → 0, numeric → int value, text → 9999."""
    stripped = feat.strip()
    if stripped == "001":
        return 0
    try:
        return int(stripped)
    except ValueError:
        return 9_999


# ── Public API ─────────────────────────────────────────────────────────────────

def load_primary_outfall_coords(
    npdes_ids: Optional[list[str]] = None,
    path: Optional[Path] = None,
) -> pl.DataFrame:
    """Load one representative outfall coordinate per NPDES permit.

    Args:
        npdes_ids: Optional allowlist of NPDES permit numbers to load.
                   Pass ``None`` to load all (slower; returns full dataset).
        path:      Override for the CSV path (defaults to ``OUTFALL_COORDS_PATH``).

    Returns:
        DataFrame with columns:
            npdes_id    (str)    NPDES permit number (upper-cased)
            lat_outfall (float)  outfall latitude  (NAD83)
            lon_outfall (float)  outfall longitude (NAD83)

        Empty DataFrame with the same schema if the file is missing or no
        valid rows are found.
    """
    csv_path = path or OUTFALL_COORDS_PATH
    empty = pl.DataFrame(
        {"npdes_id": pl.Series([], dtype=pl.Utf8),
         "lat_outfall": pl.Series([], dtype=pl.Float64),
         "lon_outfall": pl.Series([], dtype=pl.Float64)}
    )

    if not csv_path.exists():
        log.warning(
            f"NPDES_PERM_FEATURE_COORDS.csv not found at {csv_path}. "
            "Phase 3 will use literature-based head for all sites. "
            "Place the file (or a symlink) at the path above to enable "
            "USGS 3DEP real-elevation head calculation."
        )
        return empty

    log.info(f"Loading outfall coordinates from {csv_path.name} …")

    id_set: Optional[set[str]] = set(npdes_ids) if npdes_ids is not None else None

    records: list[dict] = []
    with open(csv_path, "r", encoding="utf-8", errors="replace") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            npdes_id = (row.get("EXTERNAL_PERMIT_NMBR") or "").strip().upper()
            if not npdes_id:
                continue
            if id_set is not None and npdes_id not in id_set:
                continue

            feat    = (row.get("PERM_FEATURE_NMBR") or "").strip()
            lat_raw = (row.get("LATITUDE_MEASURE")  or "").strip()
            lon_raw = (row.get("LONGITUDE_MEASURE") or "").strip()

            try:
                lat = float(lat_raw)
                lon = float(lon_raw)
            except ValueError:
                continue

            if not _is_valid_coord(lat, lon):
                continue

            records.append({
                "npdes_id":    npdes_id,
                "perm_feature": feat,
                "lat_outfall": lat,
                "lon_outfall": lon,
                "_prio":       _feature_priority(feat),
            })

    if not records:
        log.warning(
            "No valid outfall coordinates found in NPDES_PERM_FEATURE_COORDS.csv "
            f"for the {len(npdes_ids) if npdes_ids else 'N/A'} requested permits."
        )
        return empty

    df = pl.DataFrame(records)
    n_raw     = len(df)
    n_permits = df["npdes_id"].n_unique()
    log.info(f"  Read {n_raw:,} valid outfall rows covering {n_permits:,} permits")

    # Pick one outfall per facility: lowest _prio wins (001 → 0)
    df = (
        df.sort(["npdes_id", "_prio"])
          .unique(subset=["npdes_id"], keep="first")
          .drop(["_prio", "perm_feature"])
    )

    n_selected = len(df)
    log.info(f"  Selected {n_selected:,} primary outfall coordinates (one per permit)")
    return df
