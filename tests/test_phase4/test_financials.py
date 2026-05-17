"""Tests for Phase 4 financial calculations: NPV, IRR, payback, LCOE."""

import math

import pytest

from src.phase4.financials import (
    compute_irr,
    compute_lcoe,
    compute_npv,
    compute_payback,
    compute_scorecard,
)

# Shared fixture values — clearly viable small hydro project
# Revenue = 1M kWh × $0.085 = $85,000/yr, net = $72,500/yr, payback ≈ 7 yrs
_ENERGY   = 1_000_000.0  # kWh/yr
_RATE     = 0.085         # $/kWh (e.g. Wisconsin industrial)
_CAPEX    = 500_000.0     # USD
_OPEX     = 12_500.0      # USD/yr  (2.5% of CapEx)
_REVENUE  = _ENERGY * _RATE  # $85,000/yr


# ── compute_npv ───────────────────────────────────────────────────────────────

class TestComputeNpv:
    def test_positive_npv_for_viable_project(self):
        npv = compute_npv(_ENERGY, _RATE, _OPEX, _CAPEX)
        assert npv > 0, "Expected positive NPV for viable project"

    def test_negative_npv_for_tiny_generation(self):
        npv = compute_npv(1_000.0, 0.05, 50_000.0, 2_000_000.0)
        assert npv < 0

    def test_zero_capex_npv_equals_sum_of_pvs(self):
        # With zero CapEx, NPV = PV of all net cash flows
        npv = compute_npv(_ENERGY, _RATE, _OPEX, 0.0)
        assert npv > 0

    def test_50pct_grant_increases_npv(self):
        npv_base  = compute_npv(_ENERGY, _RATE, _OPEX, _CAPEX)
        npv_grant = compute_npv(_ENERGY, _RATE, _OPEX, _CAPEX, capex_subsidy_pct=0.5)
        assert npv_grant > npv_base

    def test_higher_discount_rate_lowers_npv(self):
        npv_low  = compute_npv(_ENERGY, _RATE, _OPEX, _CAPEX, discount_rate=0.04)
        npv_high = compute_npv(_ENERGY, _RATE, _OPEX, _CAPEX, discount_rate=0.12)
        assert npv_low > npv_high

    def test_longer_lifetime_increases_npv(self):
        npv_20 = compute_npv(_ENERGY, _RATE, _OPEX, _CAPEX, project_years=20)
        npv_40 = compute_npv(_ENERGY, _RATE, _OPEX, _CAPEX, project_years=40)
        assert npv_40 > npv_20

    def test_returns_float(self):
        assert isinstance(compute_npv(_ENERGY, _RATE, _OPEX, _CAPEX), float)


# ── compute_irr ───────────────────────────────────────────────────────────────

class TestComputeIrr:
    def test_irr_between_0_and_1_for_viable(self):
        irr = compute_irr(_ENERGY, _RATE, _OPEX, _CAPEX)
        assert 0 < irr < 1.0

    def test_higher_energy_gives_higher_irr(self):
        irr_low  = compute_irr(100_000.0, _RATE, _OPEX, _CAPEX)
        irr_high = compute_irr(900_000.0, _RATE, _OPEX, _CAPEX)
        assert irr_high > irr_low

    def test_zero_capex_returns_nan_or_high(self):
        irr = compute_irr(_ENERGY, _RATE, _OPEX, 0.0)
        # Zero capex → no valid IRR; must return nan
        assert math.isnan(irr)

    def test_never_pays_back_returns_boundary(self):
        # Tiny revenue, huge capex → IRR negative boundary
        irr = compute_irr(100.0, 0.001, 100_000.0, 50_000_000.0)
        assert irr < 0 or math.isnan(irr)

    def test_consistency_with_npv(self):
        # At IRR, NPV ≈ 0 (tolerance proportional to CapEx, not flat $1k)
        irr = compute_irr(_ENERGY, _RATE, _OPEX, _CAPEX)
        if not math.isnan(irr) and -0.98 < irr < 2.99:
            npv_at_irr = compute_npv(_ENERGY, _RATE, _OPEX, _CAPEX, discount_rate=irr)
            tol = _CAPEX * 1e-3  # 0.1% of CapEx
            assert abs(npv_at_irr) < tol, f"NPV at IRR should be near 0: {npv_at_irr}"

    def test_trivially_profitable_returns_sentinel(self):
        # Tiny CapEx + huge revenue → NPV always positive → returns +3.0 sentinel
        irr = compute_irr(10_000_000.0, 0.20, 1_000.0, 10_000.0)
        assert irr == pytest.approx(3.0)


# ── compute_payback ───────────────────────────────────────────────────────────

class TestComputePayback:
    def test_payback_within_lifetime(self):
        pb = compute_payback(_ENERGY, _RATE, _OPEX, _CAPEX)
        assert 0 < pb < 30, f"Payback={pb:.1f} outside expected range"

    def test_never_pays_back_returns_inf_or_999(self):
        pb = compute_payback(10.0, 0.001, 100_000.0, 10_000_000.0)
        assert math.isinf(pb) or pb > 30

    def test_higher_energy_shorter_payback(self):
        pb_small = compute_payback(50_000.0,  _RATE, _OPEX, _CAPEX)
        pb_large = compute_payback(900_000.0, _RATE, _OPEX, _CAPEX)
        assert pb_large < pb_small

    def test_zero_capex_immediate_payback(self):
        pb = compute_payback(_ENERGY, _RATE, _OPEX, 0.0)
        assert pb == 0.0 or pb < 1.0


# ── compute_lcoe ─────────────────────────────────────────────────────────────

class TestComputeLcoe:
    def test_lcoe_positive_for_normal_inputs(self):
        lcoe = compute_lcoe(_ENERGY, _OPEX, _CAPEX)
        assert 0 < lcoe < 1.0, f"LCOE={lcoe:.4f} not in $/kWh range"

    def test_lcoe_is_inf_for_zero_energy(self):
        lcoe = compute_lcoe(0.0, _OPEX, _CAPEX)
        assert math.isinf(lcoe)

    def test_lcoe_decreases_with_higher_energy(self):
        lcoe_low  = compute_lcoe(100_000.0, _OPEX, _CAPEX)
        lcoe_high = compute_lcoe(900_000.0, _OPEX, _CAPEX)
        assert lcoe_high < lcoe_low

    def test_lcoe_in_realistic_range(self):
        # Conduit hydro literature: $0.05–$0.25/kWh
        lcoe = compute_lcoe(_ENERGY, _OPEX, _CAPEX)
        assert 0.02 <= lcoe <= 0.50, f"LCOE={lcoe:.4f} out of plausible range"


# ── compute_scorecard ─────────────────────────────────────────────────────────

class TestComputeScorecard:
    def _scorecard(self, **kw):
        defaults = dict(
            annual_energy_kwh=_ENERGY,
            elec_rate_per_kwh=_RATE,
            annual_opex_usd=_OPEX,
            total_capex_usd=_CAPEX,
            annual_revenue_usd=_REVENUE,
        )
        defaults.update(kw)
        return compute_scorecard(**defaults)

    def test_returns_required_keys(self):
        sc = self._scorecard()
        required = {
            "annual_net_cf_usd", "npv_usd", "npv_with_50pct_grant_usd",
            "irr", "payback_years", "lcoe_per_kwh", "project_viable",
        }
        assert required == set(sc.keys())

    def test_grant_npv_exceeds_base_npv(self):
        sc = self._scorecard()
        assert sc["npv_with_50pct_grant_usd"] > sc["npv_usd"]

    def test_project_viable_flag_consistent(self):
        sc = self._scorecard()
        if sc["npv_usd"] > 0 and sc["payback_years"] <= 20:
            assert sc["project_viable"] is True
        else:
            assert sc["project_viable"] is False

    def test_annual_net_cf_correct(self):
        sc = self._scorecard()
        expected = _REVENUE - _OPEX
        assert abs(sc["annual_net_cf_usd"] - expected) < 1e-3

    def test_project_viable_is_bool(self):
        sc = self._scorecard()
        assert isinstance(sc["project_viable"], bool)

    def test_nan_irr_in_scorecard_no_crash(self):
        # zero CapEx → compute_irr returns nan; scorecard must not raise
        sc = self._scorecard(total_capex_usd=0.0)
        assert math.isnan(sc["irr"])
        assert isinstance(sc["npv_usd"], float)

    def test_negative_annual_net_cf(self):
        # opex > revenue → net CF negative, project not viable
        sc = self._scorecard(annual_opex_usd=200_000.0, annual_revenue_usd=50_000.0)
        assert sc["annual_net_cf_usd"] < 0
        assert sc["project_viable"] is False

    def test_payback_sentinel_in_scorecard(self):
        # Project that can never pay back → payback_years == 999.0
        sc = self._scorecard(
            annual_energy_kwh=100.0,
            annual_revenue_usd=8.5,
            total_capex_usd=5_000_000.0,
            annual_opex_usd=100_000.0,
        )
        assert sc["payback_years"] == 999.0

    def test_lcoe_sentinel_in_scorecard(self):
        # Zero energy → LCOE = inf → sentinel 999.0
        sc = self._scorecard(annual_energy_kwh=0.0, annual_revenue_usd=0.0)
        assert sc["lcoe_per_kwh"] == 999.0

    def test_degradation_effect(self):
        # Higher degradation → lower NPV
        npv_low_deg  = compute_npv(_ENERGY, _RATE, _OPEX, _CAPEX, degradation_rate=0.001)
        npv_high_deg = compute_npv(_ENERGY, _RATE, _OPEX, _CAPEX, degradation_rate=0.010)
        assert npv_low_deg > npv_high_deg

    def test_unprofitable_project_not_viable(self):
        sc = self._scorecard(
            annual_energy_kwh=1_000.0,
            annual_revenue_usd=80.0,
            total_capex_usd=5_000_000.0,
        )
        assert sc["project_viable"] is False
