"""Tests for Phase 2 Monte Carlo exclusion filter — W13 small-POTW gate."""

from __future__ import annotations

import polars as pl

from src.phase2.monte_carlo import _exclude, _MIN_VIABLE_FLOW_MGD, _OUTPUT_KEYS


# ── _exclude: zero / null flow ─────────────────────────────────────────────────

class TestExcludeNoUsableFlow:
    def test_none_flow_excluded(self):
        assert _exclude({"mean_flow_mgd": None}) == "no_usable_flow"

    def test_zero_flow_excluded(self):
        assert _exclude({"mean_flow_mgd": 0.0}) == "no_usable_flow"

    def test_negative_flow_excluded(self):
        assert _exclude({"mean_flow_mgd": -1.0}) == "no_usable_flow"

    def test_nan_flow_excluded(self):
        """NaN slips past None check and <= 0 check — must be caught explicitly."""
        assert _exclude({"mean_flow_mgd": float("nan")}) == "no_usable_flow"

    def test_missing_key_excluded(self):
        """Row dict with no mean_flow_mgd key → .get() returns None → excluded."""
        assert _exclude({}) == "no_usable_flow"

    def test_string_flow_excluded(self):
        """Non-numeric value in mean_flow_mgd field → excluded (isinstance guard)."""
        assert _exclude({"mean_flow_mgd": "1.5"}) == "no_usable_flow"


# ── _exclude: W13 small-POTW gate ─────────────────────────────────────────────

class TestExcludeSmallPotw:
    def test_below_threshold_excluded(self):
        row = {"mean_flow_mgd": _MIN_VIABLE_FLOW_MGD - 0.01}
        assert _exclude(row) == "small_potw"

    def test_well_below_threshold_excluded(self):
        row = {"mean_flow_mgd": 0.1}
        assert _exclude(row) == "small_potw"

    def test_at_threshold_not_excluded(self):
        """Boundary: mean_flow == threshold passes (filter is strictly < threshold)."""
        row = {"mean_flow_mgd": _MIN_VIABLE_FLOW_MGD}
        assert _exclude(row) is None

    def test_above_threshold_not_excluded(self):
        row = {"mean_flow_mgd": 1.0}
        assert _exclude(row) is None

    def test_large_flow_not_excluded(self):
        row = {"mean_flow_mgd": 500.0}
        assert _exclude(row) is None

    def test_threshold_value_matches_config(self):
        """_MIN_VIABLE_FLOW_MGD should match settings.yaml phase2.min_viable_mean_flow_mgd."""
        from src.common import config
        expected = float(config.get("phase2.min_viable_mean_flow_mgd", 0.5))
        assert _MIN_VIABLE_FLOW_MGD == expected


# ── _exclude: sparse DMR gate (regression — W13 must not break existing gate) ──

class TestExcludeSparseDmr:
    def test_dmr_limited_sparse_excluded(self):
        row = {"mean_flow_mgd": 2.0, "data_quality": "dmr_limited", "n_months_data": 2}
        assert _exclude(row) == "sparse_dmr_artifact"

    def test_dmr_limited_sufficient_not_excluded(self):
        row = {"mean_flow_mgd": 2.0, "data_quality": "dmr_limited", "n_months_data": 12}
        assert _exclude(row) is None

    def test_normal_dmr_not_excluded(self):
        row = {"mean_flow_mgd": 2.0, "data_quality": "dmr", "n_months_data": 120}
        assert _exclude(row) is None

    def test_dmr_limited_none_months_excluded(self):
        """n_months_data == None with dmr_limited → sparse_dmr_artifact."""
        row = {"mean_flow_mgd": 2.0, "data_quality": "dmr_limited", "n_months_data": None}
        assert _exclude(row) == "sparse_dmr_artifact"

    def test_missing_data_quality_key_not_excluded(self):
        """data_quality key absent → defaults to 'design_only' → not dmr_limited → passes."""
        row = {"mean_flow_mgd": 2.0}
        assert _exclude(row) is None


# ── Priority order: no_usable_flow before small_potw ──────────────────────────

class TestExcludePriority:
    def test_zero_flow_takes_priority_over_small_potw(self):
        """Flow == 0 → no_usable_flow, not small_potw (zero check runs first)."""
        row = {"mean_flow_mgd": 0.0}
        assert _exclude(row) == "no_usable_flow"

    def test_small_potw_takes_priority_over_sparse_dmr(self):
        """Flow < threshold with sparse DMR → small_potw reported first."""
        row = {"mean_flow_mgd": 0.3, "data_quality": "dmr_limited", "n_months_data": 1}
        assert _exclude(row) == "small_potw"


# ── estimate_all_facilities: integration smoke test ───────────────────────────

class TestEstimateAllFacilities:
    # Minimal schema — real Phase 1 parquet has more columns (facility_name, state, etc.)
    # _process_one only reads npdes_id, mean_flow_mgd, design_flow_mgd,
    # flow_duration_curve, data_quality, n_months_data — so minimal schema is intentional.

    def test_small_potw_excluded_in_batch(self):
        """estimate_all_facilities marks small sites excluded=True, exclusion_reason=small_potw."""
        from src.phase2.monte_carlo import estimate_all_facilities

        # A002 uses flat FDC fallback (None); A003 uses realistic 20-point FDC
        fdc_20pt = [5.0 - i * 0.2 for i in range(20)]  # 5.0 → 1.2 MGD descending

        candidates = pl.DataFrame({
            "npdes_id":          ["A001", "A002", "A003"],
            "mean_flow_mgd":     [0.2,    1.0,    5.0],
            "design_flow_mgd":   [0.3,    1.5,    6.0],
            "flow_duration_curve": [None,  None,  fdc_20pt],
            "data_quality":      ["dmr",  "dmr",  "dmr"],
            "n_months_data":     [60,     60,     60],
        })

        results = estimate_all_facilities(candidates, n_iterations=100, seed=0)

        a001 = results.filter(pl.col("npdes_id") == "A001").to_dicts()[0]
        a002 = results.filter(pl.col("npdes_id") == "A002").to_dicts()[0]
        a003 = results.filter(pl.col("npdes_id") == "A003").to_dicts()[0]

        # Excluded site: correct flags, all energy fields None
        assert a001["excluded"] is True
        assert a001["exclusion_reason"] == "small_potw"
        assert a001["energy_p50_kwh_yr"] is None

        # Success path: not excluded, energy and archetype populated
        assert a002["excluded"] is False
        assert a002["energy_p50_kwh_yr"] is not None
        assert a002["archetype"] is not None

        # Success path with real 20-pt FDC: same contracts hold
        assert a003["excluded"] is False
        assert a003["energy_p50_kwh_yr"] is not None

    def test_exclusion_count_reflects_small_potw_filter(self):
        """All facilities below threshold → all excluded."""
        from src.phase2.monte_carlo import estimate_all_facilities

        candidates = pl.DataFrame({
            "npdes_id":          ["X001", "X002"],
            "mean_flow_mgd":     [0.1,    0.4],
            "design_flow_mgd":   [0.2,    0.5],
            "flow_duration_curve": [None, None],
            "data_quality":      ["dmr",  "dmr"],
            "n_months_data":     [24,     24],
        })

        results = estimate_all_facilities(candidates, n_iterations=100, seed=0)
        excluded = results.filter(pl.col("excluded") == True)
        assert len(excluded) == 2
        reasons = set(excluded["exclusion_reason"].to_list())
        assert reasons == {"small_potw"}

    def test_excluded_row_schema_matches_success_row(self):
        """Excluded and non-excluded rows must have identical column sets (no drift)."""
        from src.phase2.monte_carlo import estimate_all_facilities

        candidates = pl.DataFrame({
            "npdes_id":          ["S001", "S002"],
            "mean_flow_mgd":     [0.2,    2.0],
            "design_flow_mgd":   [0.3,    3.0],
            "flow_duration_curve": [None, None],
            "data_quality":      ["dmr",  "dmr"],
            "n_months_data":     [60,     60],
        })

        results = estimate_all_facilities(candidates, n_iterations=50, seed=0)
        assert len(results) == 2
        # Column set must exactly match _OUTPUT_KEYS — catches silent drift if
        # success-path dict gains a new key that exclusion rows don't emit.
        assert set(results.columns) == set(_OUTPUT_KEYS)
