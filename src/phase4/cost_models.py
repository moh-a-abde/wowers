"""Phase 4 — CapEx and OpEx cost models for small/micro hydropower.

CapEx model: power-law scaling from DOE Hydropower Vision & ORNL conduit
hydropower studies.

    CapEx_per_kW = max(min_per_kw, min(max_per_kw, A × rated_kW ^ B))
    Total_CapEx  = CapEx_per_kW × rated_kW

OpEx: annual O&M as a fixed percentage of installed CapEx (per turbine type).

All parameters are read from ``config/settings.yaml`` under ``cost_model`` so
they can be updated without touching source code.

Reference
---------
DOE Water Power Technologies Office, "Hydropower Vision" (2016), Chapter 3;
ORNL TM-2014/525, "New Stream-reach Development" appendix cost tables.
"""

from __future__ import annotations

from src.common import config

# ── Load cost model config ────────────────────────────────────────────────────

_CM = config.get("cost_model", {})

# Global fallback (unknown turbine types)
_CAPEX_A:    float = float(_CM.get("capex_A",          9_500))
_CAPEX_B:    float = float(_CM.get("capex_B",         -0.35))
_MIN_PER_KW: float = float(_CM.get("capex_min_per_kw",   800))
_MAX_PER_KW: float = float(_CM.get("capex_max_per_kw", 10_000))

# Per-type A/B/min/max — loaded from settings.yaml; hard-coded fallbacks
# match ARCHITECTURE.md §4.2 and are used only if YAML keys are absent.
_YAML_TYPES: dict = config.get("cost_model.types", {}) or {}

def _load_type(name: str, default_A: float, default_B: float,
               default_min: float, default_max: float) -> dict:
    y = _YAML_TYPES.get(name, {})
    return {
        "A":   float(y.get("A",          default_A)),
        "B":   float(y.get("B",          default_B)),
        "min": float(y.get("min_per_kw", default_min)),
        "max": float(y.get("max_per_kw", default_max)),
    }

_TYPE_PARAMS: dict[str, dict] = {
    "Kaplan":           _load_type("Kaplan",           9_500,  -0.35,   800, 10_000),
    "Francis":          _load_type("Francis",           8_500,  -0.32,   700,  9_000),
    "Pelton":           _load_type("Pelton",            7_000,  -0.30,   600,  8_000),
    "in_conduit_micro": _load_type("in_conduit_micro", 12_000,  -0.25, 2_000, 15_000),
    # Crossflow (Ossberger/CINK): simpler runner → lower cost than Kaplan
    "Crossflow":        _load_type("Crossflow",         7_500,  -0.28,   500,  7_500),
}

# OpEx fraction of CapEx per type
_OPEX_PCT: dict[str, float] = {}
for t in ("Kaplan", "Francis", "Pelton", "in_conduit_micro", "Crossflow"):
    pct = config.get(f"cost_model.opex_pct_of_capex.{t}")
    if pct is None:
        pct = {"Kaplan": 0.025, "Francis": 0.020, "Pelton": 0.015,
               "in_conduit_micro": 0.030, "Crossflow": 0.020}[t]
    _OPEX_PCT[t] = float(pct)


# ── Public API ────────────────────────────────────────────────────────────────

def capex_per_kw(turbine_type: str, rated_power_kw: float) -> float:
    """Installed cost per kW using the power-law model.

    Args:
        turbine_type:   One of Kaplan, Francis, Pelton, in_conduit_micro, Crossflow.
        rated_power_kw: Nameplate power (kW).  Must be > 0.

    Returns:
        Installed cost per kW (USD/kW), clamped to [min_per_kw, max_per_kw].
    """
    p = _TYPE_PARAMS.get(turbine_type, _TYPE_PARAMS["Kaplan"])
    if rated_power_kw <= 0:
        return float(p["max"])  # per-type max, not global fallback
    raw = p["A"] * (rated_power_kw ** p["B"])
    return max(p["min"], min(p["max"], raw))


def total_capex(turbine_type: str, rated_power_kw: float) -> float:
    """Total installed CapEx (USD).

    Args:
        turbine_type:   Turbine type string.
        rated_power_kw: Nameplate power (kW).

    Returns:
        Total capital expenditure in USD.
    """
    return capex_per_kw(turbine_type, rated_power_kw) * rated_power_kw


def annual_opex(turbine_type: str, capex_usd: float) -> float:
    """Annual O&M cost (USD/yr) as a percentage of installed CapEx.

    Args:
        turbine_type: Turbine type string.
        capex_usd:    Total installed CapEx (USD).

    Returns:
        Annual O&M cost (USD/yr).
    """
    pct = _OPEX_PCT.get(turbine_type, 0.025)
    return capex_usd * pct
