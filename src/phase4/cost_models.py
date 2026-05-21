"""Phase 4 — CapEx and OpEx cost models for small/micro hydropower.

Equipment CapEx model: power-law scaling from DOE Hydropower Vision & ORNL
conduit hydropower studies.

    CapEx_per_kW = max(min_per_kw, min(max_per_kw, A × rated_kW ^ B))
    Equipment_CapEx = CapEx_per_kW × rated_kW

Balance-of-system adders (F4-INTERCON, F4-PERMIT — added 2026-05):
    Interconnection_CapEx  = tier lookup by rated_kw   ($50k–$200k)
    Permitting_CapEx       = fixed adder if rated_kw < small_site_threshold

Project (all-in) CapEx for NPV/IRR:
    Project_CapEx = Equipment_CapEx + Interconnection_CapEx + Permitting_CapEx

OpEx: annual O&M as a fixed percentage of *equipment* CapEx (per turbine type).
Interconnection and permitting are one-time costs, not O&M-bearing.

All parameters are read from ``config/settings.yaml`` under ``cost_model`` so
they can be updated without touching source code.

References
----------
DOE Water Power Technologies Office, "Hydropower Vision" (2016), Chapter 3;
ORNL TM-2014/525, "New Stream-reach Development" appendix cost tables;
FERC small-hydro interconnection cost surveys (industry-typical $50k–$200k
range for sites ≤ 1 MW);
DOE/EERE permitting / environmental review cost benchmarks for small hydro
(fixed ~$150k overhead is non-trivial relative to micro-hydro CapEx).
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


# ── F4-INTERCON: grid interconnection cost tiers ──────────────────────────────
# Tier lookup by rated_power_kw upper bound (inclusive).  Tier costs cover the
# utility-side study fee, transformer / protection equipment, switchgear, and
# metering for a typical < 1 MW behind-the-meter or distribution-tie project.
# Industry-typical range: $50k–$200k for small / micro hydro (FERC small-hydro
# interconnection cost surveys; NREL distributed generation cost handbook).
_INTERCON_DEFAULT_TIERS: list[dict] = [
    {"max_kw":       10.0, "cost_usd":  50_000.0},
    {"max_kw":       50.0, "cost_usd": 100_000.0},
    {"max_kw":      250.0, "cost_usd": 150_000.0},
    {"max_kw": 1_000_000.0, "cost_usd": 200_000.0},  # catch-all
]

_INTERCON_TIERS_RAW = config.get("cost_model.interconnection.tiers")
if _INTERCON_TIERS_RAW:
    _INTERCON_TIERS = [
        {"max_kw": float(t["max_kw"]), "cost_usd": float(t["cost_usd"])}
        for t in _INTERCON_TIERS_RAW
    ]
else:
    _INTERCON_TIERS = _INTERCON_DEFAULT_TIERS

# Sort ascending by max_kw so lookup is deterministic.
_INTERCON_TIERS.sort(key=lambda t: t["max_kw"])


# ── F4-PERMIT (tiered, F4-PERMIT-TIER 2026-05-20) ─────────────────────────────
# Permitting / environmental review cost as a 3-tier step function of rated
# power.  Replaces the original single-step $150k-or-$0 model, which created
# an unrealistic cliff at 50 kW and made 92 % of POTW sites economically
# unviable in the first Phase 4 calibration run.
#
# Tier semantics (matches FERC small-hydro practice):
#   - qualified_facility (≤ 25 kW): conduit-exemption / qualifying-facility
#     filing, minimal NEPA review.  Typical industry cost $10k–$30k.
#   - small_ferc (25 < kW ≤ 250):  abbreviated FERC review, state water-quality
#     cert, light environmental survey.  Typical $50k–$100k.
#   - full_nepa  (kW > 250):       full FERC licensing or major exemption with
#     formal NEPA EA/EIS.  Typical $100k–$200k.
_PERMIT_DEFAULT_TIERS: list[dict] = [
    {"max_kw":        25.0, "cost_usd":  25_000.0, "label": "qualified_facility"},
    {"max_kw":       250.0, "cost_usd":  75_000.0, "label": "small_ferc"},
    {"max_kw": 1_000_000.0, "cost_usd": 150_000.0, "label": "full_nepa"},  # catch-all
]

_PERMIT_TIERS_RAW = config.get("cost_model.permitting.tiers")
if _PERMIT_TIERS_RAW:
    _PERMIT_TIERS = [
        {
            "max_kw":   float(t["max_kw"]),
            "cost_usd": float(t["cost_usd"]),
            "label":    str(t.get("label", f"tier_{i}")),
        }
        for i, t in enumerate(_PERMIT_TIERS_RAW)
    ]
else:
    _PERMIT_TIERS = _PERMIT_DEFAULT_TIERS

# Sort ascending by max_kw so lookup is deterministic.
_PERMIT_TIERS.sort(key=lambda t: t["max_kw"])


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
        capex_usd:    Equipment CapEx (USD).  Do NOT pass project CapEx —
                      interconnection and permitting are one-time costs.

    Returns:
        Annual O&M cost (USD/yr).
    """
    pct = _OPEX_PCT.get(turbine_type, 0.025)
    return capex_usd * pct


# ── F4-INTERCON ───────────────────────────────────────────────────────────────

def interconnection_cost(rated_power_kw: float) -> float:
    """Grid interconnection cost (USD) — F4-INTERCON.

    Tier lookup by rated power.  Covers utility study fee, step-up transformer,
    protection relays, switchgear, and revenue-grade metering for a typical
    distribution-tie small / micro hydro project.

    Args:
        rated_power_kw: Nameplate power (kW).  Must be > 0; non-positive
            inputs return the lowest tier cost as a safety floor.

    Returns:
        One-time interconnection CapEx (USD).
    """
    if rated_power_kw <= 0:
        return float(_INTERCON_TIERS[0]["cost_usd"])
    for tier in _INTERCON_TIERS:
        if rated_power_kw <= tier["max_kw"]:
            return float(tier["cost_usd"])
    # Above every tier (shouldn't happen with catch-all) — return the top.
    return float(_INTERCON_TIERS[-1]["cost_usd"])


# ── F4-PERMIT (tiered) ────────────────────────────────────────────────────────

def _lookup_permit_tier(rated_power_kw: float) -> dict:
    """Return the matching permitting tier dict (or the lowest tier if input ≤ 0)."""
    if rated_power_kw <= 0:
        return _PERMIT_TIERS[0]
    for tier in _PERMIT_TIERS:
        if rated_power_kw <= tier["max_kw"]:
            return tier
    # Above every tier (shouldn't happen with catch-all) — return the top.
    return _PERMIT_TIERS[-1]


def permitting_cost(rated_power_kw: float) -> float:
    """Permitting / environmental review cost (USD) — F4-PERMIT (tiered).

    Tier lookup by rated power.  Replaces the original single-step model.
    Default tiers:
        ≤  25 kW  →  $25,000  (qualified_facility / conduit exemption)
        ≤ 250 kW  →  $75,000  (abbreviated FERC review)
        >  250 kW → $150,000  (full FERC licensing + NEPA review)

    Args:
        rated_power_kw: Nameplate power (kW).  Non-positive inputs return
            the lowest tier cost as a safety floor.

    Returns:
        One-time permitting CapEx (USD).
    """
    return float(_lookup_permit_tier(rated_power_kw)["cost_usd"])


def permitting_tier_label(rated_power_kw: float) -> str:
    """Return the permitting tier label string for ``rated_power_kw``.

    Used as a categorical column in the Phase 4 output parquet for cohort
    segmentation downstream.
    """
    return str(_lookup_permit_tier(rated_power_kw)["label"])


# ── Project CapEx aggregation ─────────────────────────────────────────────────

def project_capex(turbine_type: str, rated_power_kw: float) -> dict[str, float | str]:
    """Full project CapEx breakdown including all balance-of-system adders.

    Returns:
        Dict with keys:
            ``equipment_capex_usd``       — power-law turbine + BOP cost
            ``interconnection_capex_usd`` — F4-INTERCON tier lookup
            ``permitting_capex_usd``      — F4-PERMIT-TIER tier lookup
            ``permitting_tier``           — F4-PERMIT-TIER label (categorical)
            ``total_project_capex_usd``   — sum of the three USD components
    """
    eq    = total_capex(turbine_type, rated_power_kw)
    intc  = interconnection_cost(rated_power_kw)
    perm  = permitting_cost(rated_power_kw)
    label = permitting_tier_label(rated_power_kw)
    return {
        "equipment_capex_usd":       eq,
        "interconnection_capex_usd": intc,
        "permitting_capex_usd":      perm,
        "permitting_tier":           label,
        "total_project_capex_usd":   eq + intc + perm,
    }
