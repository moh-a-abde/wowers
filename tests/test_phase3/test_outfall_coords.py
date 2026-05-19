"""Tests for src.phase3.outfall_coords."""

from __future__ import annotations

import csv
import io
import tempfile
from pathlib import Path

import polars as pl
import pytest

from src.phase3.outfall_coords import (
    _feature_priority,
    _is_valid_coord,
    load_primary_outfall_coords,
)


# ── Unit: helpers ──────────────────────────────────────────────────────────────

def test_feature_priority_001():
    assert _feature_priority("001") == 0


def test_feature_priority_numeric():
    assert _feature_priority("002") == 2
    assert _feature_priority("010") == 10


def test_feature_priority_text():
    assert _feature_priority("SW1") == 9_999


def test_is_valid_coord_us():
    assert _is_valid_coord(39.0, -77.0)   # DC


def test_is_valid_coord_alaska():
    assert _is_valid_coord(61.0, -150.0)


def test_is_valid_coord_out_of_range():
    assert not _is_valid_coord(0.0, 0.0)   # middle of Atlantic
    assert not _is_valid_coord(90.0, -90.0)  # Arctic, outside bounds


# ── Integration: load_primary_outfall_coords ──────────────────────────────────

def _make_csv(rows: list[dict], path: Path) -> None:
    """Write a minimal NPDES_PERM_FEATURE_COORDS.csv fixture."""
    fieldnames = [
        "EXTERNAL_PERMIT_NMBR", "PERM_FEATURE_NMBR", "PERM_FEATURE_ID",
        "LATITUDE_MEASURE", "LONGITUDE_MEASURE",
    ]
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_missing_file_returns_empty():
    result = load_primary_outfall_coords(path=Path("/nonexistent/file.csv"))
    assert isinstance(result, pl.DataFrame)
    assert len(result) == 0
    assert set(result.columns) == {"npdes_id", "lat_outfall", "lon_outfall"}


def test_single_permit_primary_outfall():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as tf:
        tmp = Path(tf.name)

    _make_csv([
        {"EXTERNAL_PERMIT_NMBR": "OH0012345", "PERM_FEATURE_NMBR": "001",
         "PERM_FEATURE_ID": "1", "LATITUDE_MEASURE": "39.5", "LONGITUDE_MEASURE": "-82.0"},
        {"EXTERNAL_PERMIT_NMBR": "OH0012345", "PERM_FEATURE_NMBR": "002",
         "PERM_FEATURE_ID": "2", "LATITUDE_MEASURE": "39.6", "LONGITUDE_MEASURE": "-82.1"},
    ], tmp)

    result = load_primary_outfall_coords(path=tmp)
    assert len(result) == 1
    row = result.row(0, named=True)
    assert row["npdes_id"] == "OH0012345"
    assert row["lat_outfall"] == pytest.approx(39.5)   # '001' selected
    assert row["lon_outfall"] == pytest.approx(-82.0)

    tmp.unlink()


def test_multiple_permits_one_each():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tf:
        tmp = Path(tf.name)

    _make_csv([
        {"EXTERNAL_PERMIT_NMBR": "IN0001111", "PERM_FEATURE_NMBR": "001",
         "PERM_FEATURE_ID": "1", "LATITUDE_MEASURE": "40.0", "LONGITUDE_MEASURE": "-86.0"},
        {"EXTERNAL_PERMIT_NMBR": "IN0002222", "PERM_FEATURE_NMBR": "001",
         "PERM_FEATURE_ID": "2", "LATITUDE_MEASURE": "41.0", "LONGITUDE_MEASURE": "-87.0"},
    ], tmp)

    result = load_primary_outfall_coords(path=tmp)
    assert len(result) == 2
    assert set(result["npdes_id"].to_list()) == {"IN0001111", "IN0002222"}

    tmp.unlink()


def test_npdes_id_filter():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tf:
        tmp = Path(tf.name)

    _make_csv([
        {"EXTERNAL_PERMIT_NMBR": "TX0001111", "PERM_FEATURE_NMBR": "001",
         "PERM_FEATURE_ID": "1", "LATITUDE_MEASURE": "30.0", "LONGITUDE_MEASURE": "-97.0"},
        {"EXTERNAL_PERMIT_NMBR": "TX0002222", "PERM_FEATURE_NMBR": "001",
         "PERM_FEATURE_ID": "2", "LATITUDE_MEASURE": "29.0", "LONGITUDE_MEASURE": "-98.0"},
    ], tmp)

    result = load_primary_outfall_coords(npdes_ids=["TX0001111"], path=tmp)
    assert len(result) == 1
    assert result["npdes_id"][0] == "TX0001111"

    tmp.unlink()


def test_bad_coords_dropped():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tf:
        tmp = Path(tf.name)

    _make_csv([
        # valid
        {"EXTERNAL_PERMIT_NMBR": "CA0001111", "PERM_FEATURE_NMBR": "001",
         "PERM_FEATURE_ID": "1", "LATITUDE_MEASURE": "34.0", "LONGITUDE_MEASURE": "-118.0"},
        # ocean coord (0, 0) — should be dropped
        {"EXTERNAL_PERMIT_NMBR": "CA0002222", "PERM_FEATURE_NMBR": "001",
         "PERM_FEATURE_ID": "2", "LATITUDE_MEASURE": "0.0", "LONGITUDE_MEASURE": "0.0"},
        # non-numeric — dropped
        {"EXTERNAL_PERMIT_NMBR": "CA0003333", "PERM_FEATURE_NMBR": "001",
         "PERM_FEATURE_ID": "3", "LATITUDE_MEASURE": "N/A", "LONGITUDE_MEASURE": ""},
    ], tmp)

    result = load_primary_outfall_coords(path=tmp)
    assert len(result) == 1
    assert result["npdes_id"][0] == "CA0001111"

    tmp.unlink()


def test_fallback_to_lowest_numeric_when_no_001():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tf:
        tmp = Path(tf.name)

    _make_csv([
        {"EXTERNAL_PERMIT_NMBR": "WA0009999", "PERM_FEATURE_NMBR": "003",
         "PERM_FEATURE_ID": "1", "LATITUDE_MEASURE": "47.5", "LONGITUDE_MEASURE": "-122.5"},
        {"EXTERNAL_PERMIT_NMBR": "WA0009999", "PERM_FEATURE_NMBR": "002",
         "PERM_FEATURE_ID": "2", "LATITUDE_MEASURE": "47.6", "LONGITUDE_MEASURE": "-122.6"},
    ], tmp)

    result = load_primary_outfall_coords(path=tmp)
    assert len(result) == 1
    row = result.row(0, named=True)
    # '002' (priority 2) beats '003' (priority 3)
    assert row["lat_outfall"] == pytest.approx(47.6)

    tmp.unlink()
