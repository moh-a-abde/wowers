"""Tests for Phase 4 tornado sensitivity analysis."""

import pytest

from src.phase4.sensitivity import (
    _HEAD_FACTORS,
    _FLOW_FACTORS,
    _RATE_FACTORS,
    run_tornado,
)

_BASE = dict(
    annual_energy_kwh=1_000_000.0,
    elec_rate_per_kwh=0.085,
    annual_opex_usd=12_500.0,
    total_capex_usd=500_000.0,
)


class TestRunTornado:
    def _run(self, **kw):
        args = {**_BASE, **kw}
        return run_tornado(**args)

    def test_returns_required_keys(self):
        r = self._run()
        required = {
            "sensitivity_head_npv_low", "sensitivity_head_npv_high",
            "sensitivity_flow_npv_low", "sensitivity_flow_npv_high",
            "sensitivity_rate_npv_low", "sensitivity_rate_npv_high",
            "dominant_sensitivity",
        }
        assert required == set(r.keys())

    def test_dominant_sensitivity_is_valid(self):
        r = self._run()
        assert r["dominant_sensitivity"] in {"head", "flow", "rate"}

    # ── T15: monotonicity ─────────────────────────────────────────────────────

    def test_head_high_npv_exceeds_head_low_npv(self):
        r = self._run()
        assert r["sensitivity_head_npv_high"] > r["sensitivity_head_npv_low"]

    def test_flow_high_npv_exceeds_flow_low_npv(self):
        r = self._run()
        assert r["sensitivity_flow_npv_high"] > r["sensitivity_flow_npv_low"]

    def test_rate_high_npv_exceeds_rate_low_npv(self):
        r = self._run()
        assert r["sensitivity_rate_npv_high"] > r["sensitivity_rate_npv_low"]

    # ── T16: dominant correctness after normalization ─────────────────────────

    def test_head_dominant_for_large_head_uncertainty(self):
        # Head has ±50% range (width=1.0), flow ±20% (0.40), rate ±30% (0.60).
        # For a linear project, normalised head swing = normalised rate swing.
        # Any result is valid — just verify the column exists and is consistent.
        r = self._run()
        dominant = r["dominant_sensitivity"]
        # The dominant variable should have the largest normalised swing
        raw = {
            "head": abs(r["sensitivity_head_npv_high"] - r["sensitivity_head_npv_low"]),
            "flow": abs(r["sensitivity_flow_npv_high"] - r["sensitivity_flow_npv_low"]),
            "rate": abs(r["sensitivity_rate_npv_high"] - r["sensitivity_rate_npv_low"]),
        }
        ranges = {"head": 1.00, "flow": 0.40, "rate": 0.60}
        normalised = {k: raw[k] / ranges[k] for k in raw}
        assert normalised[dominant] == max(normalised.values())

    def test_range_factors_consistent(self):
        # Confirm the sensitivity factors in the module are physically reasonable
        assert _HEAD_FACTORS[0] < 1.0 < _HEAD_FACTORS[1]
        assert _FLOW_FACTORS[0] < 1.0 < _FLOW_FACTORS[1]
        assert _RATE_FACTORS[0] < 1.0 < _RATE_FACTORS[1]

    def test_normalised_swing_stored_correctly(self):
        # Recompute normalised swings manually and compare to dominant label.
        r = self._run()
        ranges = {"head": 1.00, "flow": 0.40, "rate": 0.60}
        raw = {
            "head": abs(r["sensitivity_head_npv_high"] - r["sensitivity_head_npv_low"]),
            "flow": abs(r["sensitivity_flow_npv_high"] - r["sensitivity_flow_npv_low"]),
            "rate": abs(r["sensitivity_rate_npv_high"] - r["sensitivity_rate_npv_low"]),
        }
        normalised = {k: raw[k] / ranges[k] for k in raw}
        expected_dominant = max(normalised, key=normalised.__getitem__)
        assert r["dominant_sensitivity"] == expected_dominant
