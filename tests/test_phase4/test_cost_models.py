"""Tests for Phase 4 CapEx and OpEx cost models."""

import pytest

from src.phase4.cost_models import annual_opex, capex_per_kw, total_capex

TURBINE_TYPES = ("Kaplan", "Francis", "Pelton", "in_conduit_micro")


class TestCapexPerKw:
    def test_returns_positive_for_each_type(self):
        for t in TURBINE_TYPES:
            assert capex_per_kw(t, 100.0) > 0, f"Non-positive capex for {t}"

    def test_clamped_to_min_at_large_power(self):
        # At very large power, power-law pushes below min; clamp kicks in
        for t in TURBINE_TYPES:
            c = capex_per_kw(t, 100_000.0)
            assert c > 0  # must still be positive (clamped to min)

    def test_per_type_max_at_zero_power(self):
        # Zero rated power → returns per-type max (D3 fix: no longer global 10,000)
        expected_max = {
            "Kaplan":           10_000,
            "Francis":           9_000,
            "Pelton":            8_000,
            "in_conduit_micro": 15_000,
        }
        for t in TURBINE_TYPES:
            assert capex_per_kw(t, 0.0) == pytest.approx(expected_max[t]), \
                f"{t}: expected per-type max {expected_max[t]}, got {capex_per_kw(t, 0.0)}"

    def test_economies_of_scale(self):
        # Larger plant → lower $/kW (before clamping)
        for t in TURBINE_TYPES:
            c1 = capex_per_kw(t, 10.0)
            c2 = capex_per_kw(t, 1_000.0)
            assert c1 >= c2, f"{t}: no economies of scale detected"

    def test_unknown_type_falls_back_to_kaplan(self):
        known  = capex_per_kw("Kaplan", 100.0)
        unk    = capex_per_kw("UnknownTurbine", 100.0)
        assert known == unk

    def test_capex_per_kw_range_physically_plausible(self):
        # ORNL/DOE range for conduit hydro: ~$1,000–$15,000/kW
        for t in TURBINE_TYPES:
            c = capex_per_kw(t, 100.0)
            assert 500 <= c <= 20_000, f"{t}: capex/kW={c} out of plausible range"


class TestTotalCapex:
    def test_total_equals_per_kw_times_power(self):
        for t in TURBINE_TYPES:
            kw = 250.0
            assert abs(total_capex(t, kw) - capex_per_kw(t, kw) * kw) < 1e-6

    def test_zero_power_still_computes(self):
        c = total_capex("Kaplan", 0.0)
        assert c >= 0


class TestAnnualOpex:
    def test_returns_positive_fraction_of_capex(self):
        for t in TURBINE_TYPES:
            capex = 500_000.0
            opex  = annual_opex(t, capex)
            assert 0 < opex < capex, f"{t}: opex={opex} outside (0, capex)"

    def test_opex_fraction_between_1_and_5_pct(self):
        for t in TURBINE_TYPES:
            capex = 1_000_000.0
            frac  = annual_opex(t, capex) / capex
            assert 0.01 <= frac <= 0.05, f"{t}: opex fraction={frac:.3f} unusual"

    def test_unknown_type_gets_default_fraction(self):
        capex = 1_000_000.0
        opex  = annual_opex("UnknownType", capex)
        assert 0 < opex < capex
