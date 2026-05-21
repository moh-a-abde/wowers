"""Tests for phase1/flow_features.py — architecture verification plan §1.5 items 3–5."""

from __future__ import annotations

import polars as pl
import pytest

from src.phase1.flow_features import compute_flow_features, _compute_fdc, FDC_PROBS


class TestFlowFeatures:

    def test_output_has_one_row_per_facility(
        self, sample_timeseries, sample_potw_facilities
    ):
        result = compute_flow_features(sample_timeseries, sample_potw_facilities)
        assert result["npdes_id"].n_unique() == len(result)
        assert len(result) == len(sample_potw_facilities)

    def test_mean_flow_is_correct(self, sample_timeseries, sample_potw_facilities):
        """MN0000000 has flows ~10–11.5 MGD, mean should be ~10.75."""
        result = compute_flow_features(sample_timeseries, sample_potw_facilities)
        mn0 = result.filter(pl.col("npdes_id") == "MN0000000")
        assert len(mn0) == 1
        mean_flow = mn0["mean_flow_mgd"][0]
        assert 10.0 <= mean_flow <= 12.0, f"Unexpected mean flow: {mean_flow}"

    def test_no_negative_flow_values(self, sample_timeseries, sample_potw_facilities):
        result = compute_flow_features(sample_timeseries, sample_potw_facilities)
        for col in ["mean_flow_mgd", "p10_flow_mgd", "min_flow_mgd"]:
            vals = result[col].drop_nulls()
            assert (vals >= 0).all(), f"Negative values found in {col}"

    def test_utilization_ratio_bounds(self, sample_timeseries, sample_potw_facilities):
        """utilization_ratio should be in [0, ~2.0] — no extreme values."""
        result = compute_flow_features(sample_timeseries, sample_potw_facilities)
        ratios = result["utilization_ratio"].drop_nulls()
        assert (ratios >= 0).all()
        assert (ratios <= 3.0).all(), f"Extreme utilization ratios: {ratios.max()}"

    def test_facilities_without_dmr_get_fallback(
        self, sample_timeseries, sample_potw_facilities
    ):
        """MN0000003 has no DMR records — should fall back to design/actual flow."""
        result = compute_flow_features(sample_timeseries, sample_potw_facilities)
        mn3 = result.filter(pl.col("npdes_id") == "MN0000003")
        assert len(mn3) == 1
        # Should have non-null mean_flow from actual_avg or design_flow
        assert mn3["mean_flow_mgd"][0] is not None
        assert mn3["data_quality"][0] in ("actual_avg_only", "design_only")

    def test_n_months_matches_input_records(
        self, sample_timeseries, sample_potw_facilities
    ):
        """MN0000000 has 36 months of data."""
        result = compute_flow_features(sample_timeseries, sample_potw_facilities)
        mn0 = result.filter(pl.col("npdes_id") == "MN0000000")
        assert mn0["n_months_data"][0] == 36

    def test_pct_missing_is_zero_for_complete_records(
        self, sample_timeseries, sample_potw_facilities
    ):
        """MN0000000 has consecutive monthly records — pct_missing should be ~0."""
        result = compute_flow_features(sample_timeseries, sample_potw_facilities)
        mn0 = result.filter(pl.col("npdes_id") == "MN0000000")
        assert mn0["pct_missing"][0] < 0.05

    def test_fdc_has_correct_length(self, sample_timeseries, sample_potw_facilities):
        """Flow duration curve should have exactly len(FDC_PROBS) values."""
        result = compute_flow_features(sample_timeseries, sample_potw_facilities)
        mn0 = result.filter(
            pl.col("npdes_id") == "MN0000000"
        ).filter(pl.col("flow_duration_curve").is_not_null())
        if len(mn0) > 0:
            fdc = mn0["flow_duration_curve"][0]
            assert len(fdc) == len(FDC_PROBS)

    def test_fdc_is_non_increasing(self):
        """FDC values must be monotonically non-increasing (higher exceedance = lower flow)."""
        import numpy as np
        flows = np.array([5.0, 10.0, 8.0, 12.0, 6.0, 9.0, 11.0, 7.0, 4.0, 3.0])
        fdc = _compute_fdc(flows)
        for i in range(len(fdc) - 1):
            assert fdc[i] >= fdc[i + 1] - 1e-9, (
                f"FDC not non-increasing at index {i}: {fdc[i]} < {fdc[i+1]}"
            )

    def test_cv_flow_is_lower_for_steady_plant(
        self, sample_timeseries, sample_potw_facilities
    ):
        """MN0000000 (steady) should have lower CV than MN0000001 (variable)."""
        result = compute_flow_features(sample_timeseries, sample_potw_facilities)
        cv_steady = result.filter(pl.col("npdes_id") == "MN0000000")["cv_flow"][0]
        cv_variable = result.filter(pl.col("npdes_id") == "MN0000001")["cv_flow"][0]
        assert cv_steady is not None and cv_variable is not None
        assert cv_steady < cv_variable, (
            f"Expected steady CV ({cv_steady:.3f}) < variable CV ({cv_variable:.3f})"
        )


class TestFDCComputation:

    def test_fdc_all_same_flow(self):
        import numpy as np
        flows = np.ones(20) * 5.0
        fdc = _compute_fdc(flows)
        assert all(abs(v - 5.0) < 0.01 for v in fdc)

    def test_fdc_empty_returns_zeros(self):
        import numpy as np
        fdc = _compute_fdc(np.array([]))
        assert fdc == [0.0] * len(FDC_PROBS)

    def test_fdc_single_value(self):
        import numpy as np
        fdc = _compute_fdc(np.array([7.5]))
        assert all(abs(v - 7.5) < 0.01 for v in fdc)


class TestSingleOutlierFix:
    """Regression tests for the per-reading outlier filter (Phase 1 bug fix).

    Root cause: a single bogus DMR month (e.g. 300 MGD on a 0.19 MGD plant)
    inflated mean_flow_mgd above the 5x design ratio cap, causing the safety-net
    guard to null ALL stats — including the FDC built from 70 legitimate months.
    Fix: filter individual readings > cap × design_flow BEFORE computing stats.
    """

    def _make_ts(self, npdes_id: str, good_flows: list[float], bad_flow: float) -> pl.DataFrame:
        import datetime
        rows = []
        for i, f in enumerate(good_flows):
            rows.append({
                "npdes_id": npdes_id,
                "outfall": "001",
                "period_end": datetime.date(2015 + i // 12, 1 + i % 12, 28),
                "avg_flow_mgd": f,
                "max_flow_mgd": f,
                "min_flow_mgd": f,
                "is_estimated": False,
                "fiscal_year": 2015 + i // 12,
            })
        rows.append({
            "npdes_id": npdes_id,
            "outfall": "001",
            "period_end": datetime.date(2020, 6, 30),
            "avg_flow_mgd": bad_flow,
            "max_flow_mgd": bad_flow,
            "min_flow_mgd": bad_flow,
            "is_estimated": False,
            "fiscal_year": 2020,
        })
        return pl.DataFrame(rows)

    def _make_facility(self, npdes_id: str, design: float) -> pl.DataFrame:
        return pl.DataFrame({
            "npdes_id": [npdes_id],
            "facility_name": ["Test WWTP"],
            "state_code": ["TX"],
            "city": ["Test City"],
            "county": ["Test County"],
            "latitude": [30.0],
            "longitude": [-90.0],
            "design_flow_mgd": [design],
            "actual_avg_flow_mgd": [None],
        })

    def test_single_outlier_does_not_null_fdc(self):
        """70 good months (0.2 MGD) + 1 bad month (300 MGD) → FDC and mean_flow survive."""
        ts = self._make_ts("TST_OUTLIER", [0.2] * 70, bad_flow=300.0)
        facilities = self._make_facility("TST_OUTLIER", design=0.5)
        result = compute_flow_features(ts, facilities)
        row = result.filter(pl.col("npdes_id") == "TST_OUTLIER")
        assert row.height == 1
        assert row["mean_flow_mgd"][0] is not None, "mean_flow_mgd should not be nulled"
        assert row["flow_duration_curve"][0] is not None, "FDC should not be nulled"
        assert abs(row["mean_flow_mgd"][0] - 0.2) < 0.01, (
            f"mean_flow should be ~0.2 MGD, got {row['mean_flow_mgd'][0]}"
        )
        assert row["data_quality"][0] == "dmr"

    def test_true_unit_error_still_nulled(self):
        """All months at 300 MGD on a 0.5 MGD design plant → stats correctly nulled."""
        ts = self._make_ts("TST_UNIT_ERR", [300.0] * 36, bad_flow=350.0)
        facilities = self._make_facility("TST_UNIT_ERR", design=0.5)
        result = compute_flow_features(ts, facilities)
        row = result.filter(pl.col("npdes_id") == "TST_UNIT_ERR")
        assert row.height == 1
        assert row["mean_flow_mgd"][0] is None or row["flow_duration_curve"][0] is None, (
            "Unit-error site should have null flow stats"
        )
