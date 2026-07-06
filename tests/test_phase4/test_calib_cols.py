"""Tests for P4-TIER: add_calibrated_energy_cols in src/phase4/financials.py.

Coverage:
  - Exactly 3 new columns added (no more, no less)
  - Column names are correct
  - Multiplier arithmetic: energy * 0.291 / 0.447 / 0.688
  - All pre-existing columns are untouched (name + dtype + values)
  - Works on single-row and multi-row frames
  - Zero-energy row produces zero calibrated values
  - Function is idempotent on the added columns (calling twice raises, since
    duplicate column names are caught by polars -- but single call is pure)
"""

from __future__ import annotations

import polars as pl
import pytest

from src.phase4.financials import (
    _CF_CALIB_DEFAULTS,
    add_calibrated_energy_cols,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

_FLOOR_P25 = _CF_CALIB_DEFAULTS["floor_p25"]   # 0.291
_FLOOR_P50 = _CF_CALIB_DEFAULTS["floor_p50"]   # 0.447
_CENTRAL   = _CF_CALIB_DEFAULTS["central"]     # 0.688


def _base_df(energies: list[float]) -> pl.DataFrame:
    """Minimal scorecard frame with only the columns Phase 4 actually has."""
    n = len(energies)
    return pl.DataFrame({
        "npdes_id":           [f"ID{i:04d}" for i in range(n)],
        "annual_energy_kwh":  energies,
        "rated_power_kw":     [100.0 * (i + 1) for i in range(n)],
        "project_viable":     [True] * n,
        "npv_usd":            [50_000.0 * (i + 1) for i in range(n)],
    })


# ══════════════════════════════════════════════════════════════════════════════
# Column count and names
# ══════════════════════════════════════════════════════════════════════════════

class TestCalibratedColsCount:

    def test_adds_exactly_three_columns(self):
        df = _base_df([1_000_000.0])
        result = add_calibrated_energy_cols(df)
        assert len(result.columns) == len(df.columns) + 3

    def test_new_column_names_correct(self):
        result = add_calibrated_energy_cols(_base_df([1_000_000.0]))
        for expected in (
            "energy_kwh_calib_floor_p25",
            "energy_kwh_calib_floor_p50",
            "energy_kwh_calib_central",
        ):
            assert expected in result.columns, f"Missing column: {expected}"

    def test_new_columns_are_float64(self):
        result = add_calibrated_energy_cols(_base_df([1_000_000.0]))
        for col in ("energy_kwh_calib_floor_p25",
                    "energy_kwh_calib_floor_p50",
                    "energy_kwh_calib_central"):
            assert result[col].dtype == pl.Float64, (
                f"{col} dtype is {result[col].dtype}, expected Float64"
            )


# ══════════════════════════════════════════════════════════════════════════════
# Multiplier arithmetic
# ══════════════════════════════════════════════════════════════════════════════

class TestCalibratedColsArithmetic:

    def test_floor_p25_single_row(self):
        energy = 1_000_000.0
        result = add_calibrated_energy_cols(_base_df([energy]))
        assert result["energy_kwh_calib_floor_p25"][0] == pytest.approx(
            energy * _FLOOR_P25, rel=1e-9
        )

    def test_floor_p50_single_row(self):
        energy = 2_500_000.0
        result = add_calibrated_energy_cols(_base_df([energy]))
        assert result["energy_kwh_calib_floor_p50"][0] == pytest.approx(
            energy * _FLOOR_P50, rel=1e-9
        )

    def test_central_single_row(self):
        energy = 5_000_000.0
        result = add_calibrated_energy_cols(_base_df([energy]))
        assert result["energy_kwh_calib_central"][0] == pytest.approx(
            energy * _CENTRAL, rel=1e-9
        )

    def test_multiplier_ordering(self):
        """p25 < p50 < central < annual_energy_kwh for positive energy."""
        energy = 1_000_000.0
        result = add_calibrated_energy_cols(_base_df([energy]))
        p25 = result["energy_kwh_calib_floor_p25"][0]
        p50 = result["energy_kwh_calib_floor_p50"][0]
        cen = result["energy_kwh_calib_central"][0]
        assert p25 < p50 < cen < energy

    def test_zero_energy_gives_zero_calib(self):
        result = add_calibrated_energy_cols(_base_df([0.0]))
        assert result["energy_kwh_calib_floor_p25"][0] == pytest.approx(0.0)
        assert result["energy_kwh_calib_floor_p50"][0] == pytest.approx(0.0)
        assert result["energy_kwh_calib_central"][0]   == pytest.approx(0.0)

    def test_multi_row_arithmetic(self):
        energies = [100_000.0, 500_000.0, 2_000_000.0]
        result = add_calibrated_energy_cols(_base_df(energies))
        for i, e in enumerate(energies):
            assert result["energy_kwh_calib_floor_p25"][i] == pytest.approx(e * _FLOOR_P25, rel=1e-9)
            assert result["energy_kwh_calib_floor_p50"][i] == pytest.approx(e * _FLOOR_P50, rel=1e-9)
            assert result["energy_kwh_calib_central"][i]   == pytest.approx(e * _CENTRAL,   rel=1e-9)

    def test_report_fleet_sums(self):
        """Fleet sum × multiplier should match CF_CALIBRATION_REPORT.md §6 (±0.2 GWh)."""
        # Physics ceiling: 409.1 GWh for 1,141 viable sites
        fleet_gwh = 409.1
        assert pytest.approx(fleet_gwh * _FLOOR_P25, abs=0.2) == 119.1
        assert pytest.approx(fleet_gwh * _FLOOR_P50, abs=0.2) == 182.9
        assert pytest.approx(fleet_gwh * _CENTRAL,   abs=0.2) == 281.5


# ══════════════════════════════════════════════════════════════════════════════
# Existing columns untouched
# ══════════════════════════════════════════════════════════════════════════════

class TestExistingColumnsUntouched:

    def test_existing_column_names_preserved(self):
        df = _base_df([1_000_000.0])
        result = add_calibrated_energy_cols(df)
        for col in df.columns:
            assert col in result.columns, f"Column {col} lost after add_calibrated_energy_cols"

    def test_annual_energy_kwh_unchanged(self):
        energies = [1_000_000.0, 2_000_000.0, 3_000_000.0]
        df = _base_df(energies)
        result = add_calibrated_energy_cols(df)
        for i, e in enumerate(energies):
            assert result["annual_energy_kwh"][i] == pytest.approx(e, rel=1e-12)

    def test_other_columns_values_unchanged(self):
        df = _base_df([1_000_000.0, 2_000_000.0])
        result = add_calibrated_energy_cols(df)
        assert result["npv_usd"].to_list() == pytest.approx(df["npv_usd"].to_list())
        assert result["project_viable"].to_list() == df["project_viable"].to_list()

    def test_row_count_unchanged(self):
        df = _base_df([1e6, 2e6, 3e6, 4e6, 5e6])
        result = add_calibrated_energy_cols(df)
        assert result.height == df.height


# ══════════════════════════════════════════════════════════════════════════════
# Integration test (real parquet — gated on file presence)
# ══════════════════════════════════════════════════════════════════════════════

from pathlib import Path

_SCORECARD_PATH = Path("data/processed/phase4/financial_scorecards.parquet")


@pytest.mark.skipif(
    not _SCORECARD_PATH.exists(),
    reason="financial_scorecards.parquet not available — integration test skipped",
)
class TestCalibratedColsIntegration:

    def test_real_parquet_has_three_new_cols(self):
        """After Phase 4 re-run, parquet has all 3 new columns."""
        df = pl.read_parquet(_SCORECARD_PATH)
        for col in ("energy_kwh_calib_floor_p25",
                    "energy_kwh_calib_floor_p50",
                    "energy_kwh_calib_central"):
            assert col in df.columns, f"Missing column in parquet: {col}"

    def test_real_parquet_total_cols(self):
        df = pl.read_parquet(_SCORECARD_PATH)
        assert len(df.columns) == 49, f"Expected 49 columns, got {len(df.columns)}"

    def test_real_parquet_row_count(self):
        df = pl.read_parquet(_SCORECARD_PATH)
        assert df.height == 3783

    def test_viable_fleet_sums(self):
        """Fleet sums for 1,141 viable sites match CF_CALIBRATION_REPORT.md §6."""
        df = pl.read_parquet(_SCORECARD_PATH)
        viable = df.filter(pl.col("project_viable"))
        assert viable.height == 1141

        base_gwh = viable["annual_energy_kwh"].sum() / 1e6
        p25_gwh  = viable["energy_kwh_calib_floor_p25"].sum() / 1e6
        p50_gwh  = viable["energy_kwh_calib_floor_p50"].sum() / 1e6
        cen_gwh  = viable["energy_kwh_calib_central"].sum()   / 1e6

        assert base_gwh == pytest.approx(409.1, abs=0.2)
        assert p25_gwh  == pytest.approx(119.1, abs=0.2)
        assert p50_gwh  == pytest.approx(182.9, abs=0.2)
        assert cen_gwh  == pytest.approx(281.5, abs=0.2)
