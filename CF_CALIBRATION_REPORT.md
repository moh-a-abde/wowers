# WOWERS Capacity-Factor Calibration Report

**Status:** Validation band — not a replacement for the physics estimate  
**Date:** 2026-07-03  
**Script:** `scripts/cf_calibration.py` (read-only; run to reproduce all numbers)

---

## One-Sentence Deliverable

> "409 GWh physics ceiling → conservative floor ~119–194 GWh (real river-scale small-hydro CF, 629 plants, 9,798 plant-years) → plausible central ~281 GWh (WWTP-appropriate CF = 0.60, anchored to LucidPipe Portland OR measured CF = 0.628)."

---

## 1. What This Report Is — and Is Not

The Phase 2 physics estimate (**408.8 GWh/yr, 1,140 viable sites**) is computed from the standard hydropower equation `P = η·ρ·g·Q·H`, integrated over each WWTP site's measured flow-duration curve, with efficiency and availability sampled via Monte Carlo. It has not been validated against a single real operating plant.

This report is the cheapest available credibility check: benchmark the **implied capacity factor** embedded in the physics estimate against real small-hydro plants from the DOE HydroSource EHA dataset, and express the 409 GWh headline as a three-tier band.

**This is a validation band, not a better model.** The physics estimate is not "wrong" — the band tells you what happens when you substitute the empirically observed CF from real plants for the model's implicit assumption.

---

## 2. Phase 2 Implied Capacity Factor

### Why it is ~0.87

Each viable site's `capacity_factor_p50` column is:
```
CF = energy_p50_kwh / (power_p50_kw × 8,760 hours)
```
For the 1,140 viable sites (post P1-COORD-GUARD; 408.8 GWh vs 409.1 pre-guard — original Monte-Carlo draws retained):

| Metric | Value |
|---|---|
| Viable sites | 1,140 |
| Headline energy | 408.8 GWh/yr |
| CF p10 | 0.856 |
| CF p25 | 0.865 |
| **CF p50 (median)** | **0.872** |
| CF p75 | 0.881 |
| CF p90 | 0.883 |

### Decomposition

```
CF ≈ availability × FDC_utilisation
   ≈ 0.943         × 0.925
   ≈ 0.872
```

- **Availability** is sampled from a triangular distribution (min=0.90, mode=0.95, max=0.98); mean ≈ 0.943.
- **FDC utilisation** ≈ 0.925: WWTP outfalls discharge nearly constant 24/7 municipal wastewater, so the flow-duration curve is nearly flat and the turbine operates close to rated conditions almost continuously.

### What is realistic vs. optimistic

| Component | Status | Explanation |
|---|---|---|
| Flat FDC (high utilisation) | **Realistic** | WWTP discharge is driven by municipal demand, not rainfall; seasonal variation is small |
| 0.95 availability | **Mildly optimistic** | Real micro-hydro installations experience debris fouling, seasonal maintenance, minimum-flow cutoff; 0.90 is more conservative |
| No minimum-flow cutoff | **Optimistic** | In-conduit turbines shut down below ~6–20% of rated flow; Phase 2 does not model this |

**Net: part of the 0.87 vs. river-hydro ~0.39 gap is legitimate (flatter WWTP flow); part is optimistic (no debris/minimum-flow losses modeled).**

---

## 3. Empirical Capacity Factors from Real Small-Hydro Plants

**Source:** DOE HydroSource EHA `EHA_Annual_CapacityFactor.xlsx`, sheet `AnnualCapacityFactor`  
**Filter:** `Type == "HY"` (conventional hydro only; pumped storage excluded)  
**CF recomputed** from `Net_Generation_MWh / (Capacity_MW × Hours)` rather than the provided string column  
**Drop rules:** CF ≤ 0 or CF > 1.2 removed (data errors / artefacts)

### Recompute validation

|  | Value |
|---|---|
| n rows validated | 23,483 |
| Mean \|cf_calc − cf_given\| | 0.00250 |
| p25 \|diff\| | 0.00125 |
| p75 \|diff\| | 0.00375 |

The recomputed CF agrees with the provided percentage string to within rounding error (≈ 0.0025 mean absolute difference). This confirms the CF arithmetic is correct.

### CF distribution by size bucket

| Bucket | Plants | Plant-years | p10 | p25 | p50 | p75 | p90 | Mean |
|---|---|---|---|---|---|---|---|---|
| 0.1–5 MW (all years) | 629 | 9,798 | 0.138 | 0.254 | **0.390** | 0.541 | 0.693 | 0.404 |
| 0.1–5 MW (2013–2022) | 611 | 5,530 | 0.123 | 0.242 | **0.382** | 0.529 | 0.684 | 0.393 |
| 0.1–1 MW (all years) | 59 | 802 | 0.127 | 0.268 | **0.415** | 0.546 | 0.684 | 0.410 |

**Stability check:** The 2013–2022 decade shows similar CF distribution to the full 2005–2022 sample (p50: 0.382 vs. 0.390), confirming the empirical band is not driven by a particular period. The 0.1–1 MW bucket (closest to WWTP turbine scale) has a slightly higher median (0.415) than the 0.1–5 MW bucket (0.390), consistent with smaller plants being sited on more reliable low-head flows.

---

## 4. The WWTP/River-Hydro Distinction — Why the Floor Is Conservative

**The most important caveat in this report.**

River hydro CF (~0.39 median) is low for three reasons that do NOT apply to WWTP outfalls:

1. **Seasonal rainfall variability.** Rivers flood in spring and dry up in late summer; turbines are sized for peak flow and idle during droughts. WWTP discharge tracks municipal population, not weather — it varies ±15–25% seasonally, not 10×.
2. **Peak-sizing.** River turbines are sized to capture high-flow events; most of the year the turbine operates below rated flow. WWTP turbines are sized to the plant's *design flow*, so the rated point is closer to the actual operating point.
3. **Licensing / environmental flow requirements.** Many river plants must release minimum ecological flows that bypass the turbine entirely. WWTP outfalls have no minimum-flow reservation — all discharge is available.

**Consequence:** using the river-hydro CF floor haircuts the ~409 GWh by a factor (~2.2×) that overstates the loss for WWTP applications. The floor is genuinely a floor — a scenario where WWTP turbines perform no better than river run-of-river plants, which is implausible but serves as the most pessimistic defensible bound.

---

## 5. Real WWTP / In-Conduit Install Anchors

The plausible-central tier requires at least one real conduit/WWTP installation with a published capacity factor. Only one qualified:

### LucidPipe, Portland OR (primary anchor)

- **Project:** 4 × 42" LucidPipe spherical turbines in a 42" Bull Run drinking-water transmission main  
- **Installed capacity:** 200 kW  
- **Annual generation:** 1,100 MWh/yr (reported)  
- **Measured CF:** 1,100,000 kWh ÷ (200 kW × 8,760 h) = **0.628**  
- **Source:** LucidEnergy / Portland Water Bureau press release; reported in thecivilengineer.org and project documentation  
- **Note:** This is drinking-water, not wastewater — but the hydraulic conditions are nearly identical (continuous pressurized conduit flow, no seasonal drought, no minimum-flow reservation). It is the most directly applicable real-world reference available.

### Rentricity (qualitative only)

- **Projects:** 32 kW @ 2.4 MGD / 40 PSI; 360 kW @ 2–12 MGD / 175–250 ft  
- **CF:** not published (no annual kWh for individual sites)  
- **Relevance:** NSF 61/372-certified for potable and wastewater; continuous in-conduit flow → CF expected > river hydro. Confirms the plausible WWTP CF range but cannot anchor a specific number.

### CINK Hydro-Energy (qualitative only)

- **Projects:** 450+ turbines in 50+ countries, including explicitly WWTP applications  
- **CF:** not published per site  
- **Relevance:** Crossflow turbines at 6–100% of design flow → high part-load availability confirms flat WWTP FDC reasoning.

**Central anchor:** CF = **0.60** — deliberately set 5% below LucidPipe (0.628) to acknowledge that:
- LucidPipe is drinking water, not wastewater (slightly more controlled)  
- No second real WWTP install can independently confirm the 0.628 figure  
- Some of Phase 2's optimism (no debris/min-flow modeling) will reduce real-world CF below the physics ceiling

**Plausible WWTP range:** CF 0.55–0.65. The lower end (0.55) accounts for small systems with more maintenance downtime; the upper end (0.65) is consistent with LucidPipe's measured performance.

---

## 6. Calibration Band

**Phase 2 implied CF median = 0.872.** Multiplier = empirical_CF / 0.872.

### Primary bucket: 0.1–5 MW (629 plants, 9,798 plant-years)

| Tier | CF | Multiplier | GWh/yr | Interpretation |
|---|---|---|---|---|
| Conservative floor (p25) | 0.254 | 0.291 | **119** | River-hydro 25th percentile — pessimistic floor |
| Conservative floor (p50) | 0.390 | 0.447 | **183** | River-hydro median — central floor |
| Conservative floor (p75) | 0.541 | 0.620 | **254** | River-hydro 75th percentile |
| **Plausible central** | **0.600** | **0.688** | **281** | WWTP-appropriate; anchored to LucidPipe 0.628 |
| Physics ceiling | 0.872 | 1.000 | **409** | Phase 2 assumed; optimistic upper bound (408.8 GWh post-guard) |

### Sub-bucket: 0.1–1 MW (59 plants, 802 plant-years — closest to WWTP turbine scale)

| Tier | CF | Multiplier | GWh/yr |
|---|---|---|---|
| Floor (p25) | 0.268 | 0.307 | 125 |
| Floor (p50) | 0.415 | 0.475 | 194 |
| Floor (p75) | 0.546 | 0.626 | 256 |
| **Plausible central** | **0.600** | **0.688** | **281** |
| Physics ceiling | 0.872 | 1.000 | 409 |

The 0.1–1 MW sub-bucket (most comparable to WWTP micro-scale) shows a slightly higher CF than the full 0.1–5 MW bucket (p50: 0.415 vs. 0.390), which slightly narrows the floor.

---

## 7. How to Cite This in a Pitch or Report

**Conservative framing (to a skeptical audience):**
> "Benchmarked against 629 real small-hydro plants (9,798 plant-years, DOE HydroSource EHA), the conservative floor for the WOWERS portfolio is 119–194 GWh/yr. These plants are river-based with seasonal variability that WWTP outfalls do not experience, so this is a worst-case floor."

**Central framing (the defensible number):**
> "Anchored to the LucidPipe Portland OR project (measured CF = 0.628 on a continuous-flow drinking-water transmission main), a WWTP-appropriate capacity factor of 0.60 implies ~281 GWh/yr — roughly 69% of the physics ceiling, representing realistic continuous-flow conduit operations."

**Full honest statement:**
> "The ~409 GWh physics estimate is a ceiling under Phase 2 assumptions (CF ≈ 0.87). Benchmarked against 629 real small-hydro plants, the conservative floor is ~119–194 GWh. For the more relevant WWTP/conduit case — continuous municipal discharge, no seasonal drought — the plausible central estimate is ~281 GWh (CF = 0.60), anchored to LucidPipe Portland OR (measured CF = 0.628, 1,100 MWh/yr on a 200 kW system). Real performance will depend on site-specific factors not yet modeled: debris fouling, minimum-flow cutoffs, and maintenance downtime."

---

## 8. Limitations and Next Steps

| Limitation | Impact | Next step |
|---|---|---|
| Only one real WWTP/conduit install with published CF (LucidPipe) | Central anchor is from a single project | Collect FERC conduit-exemption NOI data; some may report annual generation |
| EHA CF workbook covers plants ≥ 1 MW (fleet median ~7.7 MW); the 0.1–5 MW bucket deliberately restricts to smaller sites | CF distribution may not fully represent micro-scale | The 0.1–1 MW sub-bucket (59 plants) partially addresses this |
| Phase 2 does not model debris fouling, minimum-flow cutoffs, or ice | Physics ceiling is optimistic | Phase 5 ML model (when trained) should correct for these implicitly |
| Multiplier assumes linear scaling (CF × energy) | Valid if the energy ratio matches the CF ratio — true for the physics model | No correction needed |
| Band applies to viable-energy (408.8 GWh from 1,140 sites) only | The 3,780 turbine-viable sites represent 514.4 GWh physics ceiling; band not computed for that set | Can be rerun with different energy totals via the script |

---

## 9. Reproduction

```bash
# Requires SANDISK mounted + Phase 2/4 parquets present
python scripts/cf_calibration.py

# Override paths
python scripts/cf_calibration.py \
  --eha-dir /Volumes/SANDISK/WOWERS_Pivot_Data/Phase5_ML_GroundTruth/EHA_HydroSource_ORNL \
  --p2 data/processed/phase2/energy_yield_estimates.parquet \
  --p4 data/processed/phase4/financial_scorecards.parquet
```

All pure computation functions in `scripts/cf_calibration.py` are tested in `tests/test_phase5/test_cf_calibration.py` on synthetic frames (no drive required).
