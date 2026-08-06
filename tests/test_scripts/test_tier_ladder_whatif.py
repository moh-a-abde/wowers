"""Tests for scripts/tier_ladder_whatif.py (P4-TIER-LADDER).

Covers the pure functions only — no parquet I/O, no report rendering against
real data.  The harness's correctness against real data is asserted by the
report's own baseline-reproduction check (ceiling / 6 % / no grant must
reproduce the P2-SEED headline).
"""

from __future__ import annotations

import math

import pytest

from scripts.tier_ladder_whatif import (
    _MEASURED_CFS,
    _PHASE2_IMPLIED_CF,
    rescore_row,
    summarize,
    tier_ladder,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def row() -> dict:
    """A synthetic scorecard row with round numbers.

    100 kW site, 500,000 kWh/yr, $0.09/kWh state rate, $5k/yr O&M, $500k CapEx.
    """
    return {
        "npdes_id":           "TEST0000001",
        "annual_energy_kwh":  500_000.0,
        "elec_rate_per_kwh":  0.09,
        "annual_opex_usd":    5_000.0,
        "total_capex_usd":    500_000.0,
        "rated_power_kw":     100.0,
    }


# ── Tier ladder ───────────────────────────────────────────────────────────────

def test_ladder_is_monotonically_harsher():
    """Tiers must be ordered ceiling -> harshest, with no ties."""
    mults = [t["multiplier"] for t in tier_ladder()]
    assert mults == sorted(mults, reverse=True)
    assert len(set(mults)) == len(mults)


def test_ceiling_multiplier_is_unity():
    """The ceiling is the pre-existing annual_energy_kwh column, untouched."""
    ceiling = tier_ladder()[0]
    assert ceiling["key"] == "ceiling"
    assert ceiling["multiplier"] == 1.0
    assert ceiling["cf"] == pytest.approx(_PHASE2_IMPLIED_CF)


def test_cf_and_multiplier_are_not_the_same_number():
    """Guard against the labelling error this script exists to catch.

    Every non-ceiling tier has multiplier = CF / 0.872, so the two values must
    differ.  Reporting 0.447 as a capacity factor (it is a multiplier; the CF
    is 0.390) is the specific mistake being prevented.
    """
    for tier in tier_ladder()[1:]:
        assert tier["multiplier"] != pytest.approx(tier["cf"])
        assert tier["cf"] == pytest.approx(tier["multiplier"] * _PHASE2_IMPLIED_CF)


def test_measured_tiers_derive_from_metered_cfs():
    ladder = {t["key"]: t for t in tier_ladder()}
    for key, cf in _MEASURED_CFS.items():
        assert ladder[key]["cf"] == pytest.approx(cf)
        assert ladder[key]["multiplier"] == pytest.approx(cf / _PHASE2_IMPLIED_CF)


# ── Re-scoring ────────────────────────────────────────────────────────────────

def test_energy_scales_by_multiplier(row):
    out = rescore_row(row, 0.5, 0.06, 0.0)
    assert out["annual_energy_kwh"] == pytest.approx(250_000.0)


def test_grant_halves_the_financed_capex(row):
    full = rescore_row(row, 1.0, 0.06, 0.0)
    half = rescore_row(row, 1.0, 0.06, 0.5)
    assert full["net_capex_usd"] == pytest.approx(500_000.0)
    assert half["net_capex_usd"] == pytest.approx(250_000.0)
    # Halving the owner's capital outlay must raise NPV and shorten payback.
    assert half["npv_usd"] > full["npv_usd"]
    assert half["payback_years"] < full["payback_years"]


def test_lower_discount_rate_raises_npv(row):
    npvs = [rescore_row(row, 1.0, r, 0.0)["npv_usd"] for r in (0.06, 0.035, 0.0)]
    assert npvs == sorted(npvs)


def test_harsher_tier_lowers_npv(row):
    ceiling = rescore_row(row, 1.0, 0.06, 0.0)["npv_usd"]
    measured = rescore_row(row, 0.2195, 0.06, 0.0)["npv_usd"]
    assert measured < ceiling


def test_opex_does_not_scale_with_energy(row):
    """O&M is a fraction of equipment CapEx, so it is tier-invariant.

    Verified indirectly: at zero discount and zero degradation-free framing the
    NPV gap between two tiers is driven purely by the revenue delta, so halving
    energy must cut *less* than half the net cash flow (the constant OpEx eats
    a larger share of the smaller revenue).
    """
    full = rescore_row(row, 1.0, 0.0, 0.0)
    half = rescore_row(row, 0.5, 0.0, 0.0)
    full_cf = full["annual_net_cf_usd"]
    half_cf = half["annual_net_cf_usd"]
    assert half_cf < full_cf / 2.0


# ── Summaries ─────────────────────────────────────────────────────────────────

def test_summarize_counts_only_viable_rows():
    scored = [
        {"project_viable": True,  "npv_usd": 100.0, "payback_years": 5.0,
         "annual_energy_kwh": 1e6, "net_capex_usd": 50.0, "rated_power_kw": 150.0},
        {"project_viable": False, "npv_usd": -10.0, "payback_years": 1e6,
         "annual_energy_kwh": 9e9, "net_capex_usd": 99.0, "rated_power_kw": 900.0},
    ]
    s = summarize(scored)
    assert s["viable"] == 1
    assert s["gwh"] == pytest.approx(1.0)
    assert s["npv_musd"] == pytest.approx(100.0 / 1e6)
    assert s["capex_musd"] == pytest.approx(50.0 / 1e6)
    assert s["ge_100kw"] == 1          # the 900 kW row is non-viable, excluded
    assert s["median_payback"] == pytest.approx(5.0)


def test_summarize_empty_portfolio_gives_nan_payback():
    s = summarize([{"project_viable": False, "npv_usd": -1.0, "payback_years": 1e6,
                    "annual_energy_kwh": 0.0, "net_capex_usd": 0.0,
                    "rated_power_kw": 1.0}])
    assert s["viable"] == 0
    assert math.isnan(s["median_payback"])


def test_summarize_excludes_payback_sentinel_from_median():
    """1e6 is the _INF_SENTINEL for 'never pays back' and must not skew the median."""
    scored = [
        {"project_viable": True, "npv_usd": 1.0, "payback_years": 4.0,
         "annual_energy_kwh": 0.0, "net_capex_usd": 0.0, "rated_power_kw": 1.0},
        {"project_viable": True, "npv_usd": 1.0, "payback_years": 1e6,
         "annual_energy_kwh": 0.0, "net_capex_usd": 0.0, "rated_power_kw": 1.0},
    ]
    assert summarize(scored)["median_payback"] == pytest.approx(4.0)
