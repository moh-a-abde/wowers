"""Phase 4 — Sensitivity (tornado) analysis.

Runs the NPV model at low/high values of three key uncertain inputs:

    head_factor        ×0.50 and ×1.50  (proxy for measurement error)
    flow_factor        ×0.80 and ×1.20  (seasonal/year-to-year variability)
    rate_factor        ×0.70 and ×1.30  (electricity price range)

Head and flow adjustments are applied to ``annual_energy_kwh`` because
P ∝ Q × H → energy scales linearly with either factor.  This avoids
re-running the full FDC integration and is accurate for small perturbations.

Returns six NPV values per facility (low/high for each dimension) and a
``dominant_sensitivity`` string indicating which variable swings NPV most.
"""

from __future__ import annotations

from src.phase4.financials import compute_npv, DISCOUNT_RATE, PROJECT_YEARS, DEGRADATION_RATE

# Sensitivity sweep factors (hold two at 1.0, vary the third)
_HEAD_FACTORS:  tuple[float, float] = (0.50, 1.50)  # ±50%
_FLOW_FACTORS:  tuple[float, float] = (0.80, 1.20)  # ±20%
_RATE_FACTORS:  tuple[float, float] = (0.70, 1.30)  # ±30%

# Range widths used to normalise swings so dominant_sensitivity reflects
# NPV elasticity per unit of input change, not the width of the assumed range.
_HEAD_RANGE: float = _HEAD_FACTORS[1] - _HEAD_FACTORS[0]  # 1.00
_FLOW_RANGE: float = _FLOW_FACTORS[1] - _FLOW_FACTORS[0]  # 0.40
_RATE_RANGE: float = _RATE_FACTORS[1] - _RATE_FACTORS[0]  # 0.60


def run_tornado(
    annual_energy_kwh:  float,
    elec_rate_per_kwh:  float,
    annual_opex_usd:    float,
    total_capex_usd:    float,
    discount_rate:      float = DISCOUNT_RATE,
    project_years:      int   = PROJECT_YEARS,
    degradation_rate:   float = DEGRADATION_RATE,
) -> dict[str, float | str]:
    """Compute tornado sensitivity for one facility.

    Args:
        annual_energy_kwh:  Base case annual generation (kWh/yr).
        elec_rate_per_kwh:  Base case electricity rate ($/kWh).
        annual_opex_usd:    Annual O&M cost (USD/yr).
        total_capex_usd:    Total installed CapEx (USD).
        discount_rate:      Real discount rate.
        project_years:      Asset lifetime (years).
        degradation_rate:   Annual output decline.

    Returns:
        Dict with 6 NPV columns + ``dominant_sensitivity`` string.
    """
    def _npv(energy_factor: float = 1.0, rate_factor: float = 1.0) -> float:
        return compute_npv(
            annual_energy_kwh * energy_factor,
            elec_rate_per_kwh * rate_factor,
            annual_opex_usd,
            total_capex_usd,
            discount_rate,
            project_years,
            degradation_rate,
        )

    npv_head_low  = _npv(energy_factor=_HEAD_FACTORS[0])
    npv_head_high = _npv(energy_factor=_HEAD_FACTORS[1])
    npv_flow_low  = _npv(energy_factor=_FLOW_FACTORS[0])
    npv_flow_high = _npv(energy_factor=_FLOW_FACTORS[1])
    npv_rate_low  = _npv(rate_factor=_RATE_FACTORS[0])
    npv_rate_high = _npv(rate_factor=_RATE_FACTORS[1])

    # Normalise raw NPV swing by the range width so dominant_sensitivity
    # reflects NPV elasticity per unit of input change, not range-width bias.
    swings = {
        "head": abs(npv_head_high - npv_head_low) / _HEAD_RANGE,
        "flow": abs(npv_flow_high - npv_flow_low) / _FLOW_RANGE,
        "rate": abs(npv_rate_high - npv_rate_low) / _RATE_RANGE,
    }
    dominant = max(swings, key=swings.__getitem__)

    return {
        "sensitivity_head_npv_low":  npv_head_low,
        "sensitivity_head_npv_high": npv_head_high,
        "sensitivity_flow_npv_low":  npv_flow_low,
        "sensitivity_flow_npv_high": npv_flow_high,
        "sensitivity_rate_npv_low":  npv_rate_low,
        "sensitivity_rate_npv_high": npv_rate_high,
        "dominant_sensitivity":      dominant,
    }
