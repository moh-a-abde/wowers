# WOWERS Phase 2 Report — Estimate Annual Energy Yield

**Project:** WOWERS (Wastewater Outfall Water Energy Recovery System)
**Phase:** 2 of 5 — Head Assumption, Monte Carlo Energy Estimation, Output Validation
**Date completed:** 2026-04-11
**Final run timestamp:** 2026-04-11 01:22:30 – 01:23:18 (0.8 minutes)
**Output:** `energy_yield_estimates.parquet` — 15,691 facilities

---

## 1. Executive Summary

Phase 2 successfully estimated annual micro-hydropower energy yield for **15,691 US POTWs** using a Monte Carlo model over literature-backed head distributions. The pipeline ran in under one minute on a laptop, producing P10/P50/P90 energy confidence intervals for each facility.

Key validated outputs:
- **National energy_p50: 697 GWh/yr** — within the DOE conduit hydro expected range of 500–5,000 GWh/yr
- **Stickney WRP (IL0028053) ranks #1** at 29.25 GWh/yr — correct, as the largest US POTW by actual flow (1,200 MGD)
- **Top 10 all well-known large POTWs** across IL, WA, MA, DC, CA, NJ — no artifacts
- **1,472 facilities excluded** by the pre-Phase-2 filter (8.6% of the 17,163 Phase 1 candidates)
- One bug fixed post-run: duplicate log lines caused by Python logging propagation; resolved in `src/common/logging_setup.py`

Phase 2 head values remain **literature-assumed ranges**, not measured. Phase 3 replaces them with USGS 3DEP elevation data, which will narrow the P10–P90 spread substantially.

---

## 2. Methodology

### 2.1 Pre-Phase-2 Exclusion Filter

Before any energy calculation, facilities are dropped if they cannot produce a meaningful Monte Carlo estimate:

| Exclusion condition | Count dropped |
|--------------------|--------------|
| `mean_flow_mgd` is null or ≤ 0 | 1,445 |
| `data_quality == "dmr_limited"` AND `n_months_data < 3` | 92 |
| **Total excluded** | **1,472** |
| **Remaining for estimation** | **15,691** |

The 1,445 zero/null-flow facilities are primarily design_only or actual_avg_only fallbacks whose permit had no design flow and no actual average on file. The 92 sparse-DMR facilities have CV = 0 on n=1–2 records, which produces spuriously narrow confidence intervals.

### 2.2 Head Archetype Classification

Each facility is classified into one of three archetypes based on `design_flow_mgd` (falling back to `mean_flow_mgd` if design is absent):

| Archetype | Threshold | Head Distribution | Source |
|-----------|-----------|-------------------|--------|
| `large_potw_gravity` | design_flow > 10 MGD | Triangular(3, 8, 15) m | EPA conduit hydro reports |
| `medium_potw_gravity` | 1 ≤ design_flow ≤ 10 MGD | Triangular(2, 5, 10) m | EPA conduit hydro reports |
| `small_potw_gravity` | design_flow < 1 MGD | Triangular(1, 3, 6) m | EPA conduit hydro reports |

All POTWs are assigned gravity outfall archetypes. PRV (pressure reducing valve) and pump-bypass archetypes — which have significantly higher head potential (10–70 m) — cannot be distinguished from ICIS permit data alone. Phase 3 site elevation analysis may identify some of these.

### 2.3 Monte Carlo Model

For each facility, **10,000 iterations** sample three independent triangular distributions:

| Parameter | Distribution | Rationale |
|-----------|-------------|-----------|
| Head H (m) | Triangular(low, mode, high) per archetype | Site-to-site elevation variability |
| Turbine efficiency η | Triangular(0.70, 0.82, 0.90) | Range across micro-hydro turbine types |
| Availability A | Triangular(0.90, 0.95, 0.98) | Downtime for maintenance and inspection |

Per iteration, power is computed at each of 20 flow-duration-curve points:

```
P_kw = η × 998.2 × 9.81 × (Q_mgd × 0.043813) × H / 1000
```

Annual energy integrates the power-duration curve:

```
E_kwh_yr = ∫₀¹ P(Q(p)) dp × 8,766 h/yr × A
```

implemented via `numpy.trapezoid` with rectangular end-caps for the 0→0.01 and 0.95→1.0 FDC tails.

**FDC fallback:** For facilities without a monthly DMR time series (`design_only`, `actual_avg_only`), a flat FDC at `mean_flow_mgd` is used. This is conservative — it assumes constant flow with no seasonal variation.

**Vectorisation:** All 10,000 iterations per facility run as a single `(10000, 20)` numpy matrix operation. No Python loop over iterations. Wall time: ~4 ms/facility.

### 2.4 Hand-Calculation Validation

From ARCHITECTURE.md §2.5: for a constant 10 MGD flow, 10 m head, η = 0.85, availability = 0.95:

| Quantity | Expected | Observed |
|---------|---------|---------|
| Power | ~36.5 kW | **36.5 kW** ✓ |
| Annual energy | ~303,862 kWh/yr | **303,692 kWh/yr** ✓ |

The 170 kWh/yr gap (0.06%) is the trapezoidal approximation error from discretising the FDC at 20 points vs. the exact rectangular formula in the architecture doc.

---

## 3. Results

### 3.1 Run Statistics

| Metric | Value |
|--------|-------|
| Phase 1 input facilities | 17,163 |
| Excluded by pre-Phase-2 filter | 1,472 (8.6%) |
| Facilities with energy estimates | 15,691 |
| MC iterations per facility | 10,000 |
| Wall time | 0.8 minutes |
| Random seed | 0 |

### 3.2 National Energy Summary

| Metric | Value |
|--------|-------|
| National energy_p50 | **697 GWh/yr** |
| DOE expected range | 500–5,000 GWh/yr |
| In range? | **Yes** ✓ |

The 697 GWh/yr figure is on the lower end of the DOE range, which is expected: POTWs are only a subset of all conduit hydropower opportunities (the DOE estimate includes irrigation canals, water supply conduits, and other pressure-reducing systems), and the Phase 2 head assumptions are conservative gravity-outfall values.

### 3.3 Top 10 Facilities by Energy P50

| Rank | NPDES ID | Facility | State | Mean Flow (MGD) | Energy P50 (GWh/yr) | Archetype |
|------|----------|----------|-------|----------------|---------------------|-----------|
| 1 | IL0028053 | MWRDGC Stickney WRP | IL | 1,200.0 | 29.25 | large_potw_gravity |
| 2 | WA0029181 | King County West Point WWTP | WA | 483.8 | 11.84 | large_potw_gravity |
| 3 | IL0028061 | MWRDGC Calumet WRP | IL | 354.0 | 8.64 | large_potw_gravity |
| 4 | IL0028088 | MWRDGC Terrence J O'Brien WRP | IL | 333.0 | 8.17 | large_potw_gravity |
| 5 | MA0103284 | MWRA Deer Island Treatment Plant | MA | 327.5 | 8.02 | large_potw_gravity |
| 6 | WA0029581 | King County South WWTP | WA | 324.0 | 7.88 | large_potw_gravity |
| 7 | DC0021199 | D.C. WASA (Blue Plains) | DC | 303.0 | 7.47 | large_potw_gravity |
| 8 | CA0053813 | AK Warren Water Resource Facility | CA | 259.6 | 6.33 | large_potw_gravity |
| 9 | NJ0021016 | Passaic Valley Sewerage Comm | NJ | 248.0 | 6.02 | large_potw_gravity |
| 10 | CA0109991 | Hyperion Water Reclamation Plant | CA | 239.6 | 5.89 | large_potw_gravity |

**Notes:**
- **Stickney #1:** In Phase 1 it ranked #7 because its `data_quality = actual_avg_only` penalised the data-quality and flow-consistency components. Phase 2 energy is driven primarily by flow magnitude, so the largest plant by actual flow correctly tops the list.
- **Blue Plains drops to #7:** 303 MGD vs. Stickney's 1,200 MGD. Blue Plains ranked #1 in Phase 1 due to 120 months of high-quality DMR data and strong utilisation — factors not in the Phase 2 model.
- **King County plants (#2, #6):** West Point (484 MGD) and South (324 MGD) are large Pacific Northwest plants that were outside the Phase 1 top 10 but rank high here on flow alone.
- **All 10 are well-known continuously-operating large municipal WWTPs.** No artifacts, no CSO permits, no implausible values.

---

## 4. Issues and Resolutions

### Issue 1: `numpy.trapz` removed in NumPy 2.x

**Observed:** `AttributeError: module 'numpy' has no attribute 'trapz'` on first import test.
**Cause:** `np.trapz` was deprecated and removed in NumPy 2.0. Project venv runs NumPy 2.4.4.
**Fix:** Replaced all calls with `np.trapezoid` in `src/phase2/energy_physics.py`.

### Issue 2: Duplicate log lines from all Monte Carlo progress messages

**Observed:** Every `wowers.phase2.monte_carlo` log line printed twice in the console output.
**Cause:** `logging_setup.get()` called `setup(name)` for each child logger name, attaching a handler directly to `wowers.phase2` and to `wowers.phase2.monte_carlo`. Python logging propagates child records up to parent loggers by default, so each record fired both the child's own handler and the parent's handler.
**Fix:** `logging_setup.get()` now always calls `setup("wowers")` (the root pipeline logger, idempotent) and returns `logging.getLogger(name)` without attaching any handler to the child. Child loggers propagate naturally to the single root handler. One line per record.

---

## 5. Output File

| File | Format | Rows | Description |
|------|--------|------|-------------|
| `data/processed/phase2/energy_yield_estimates.parquet` | Parquet | 15,691 | Per-facility energy yield P10/P50/P90, power, capacity factor, equivalent homes |

### Schema

| Column | Type | Description |
|--------|------|-------------|
| `npdes_id` | string | Primary key (from Phase 1) |
| `archetype` | string | `large_potw_gravity` / `medium_potw_gravity` / `small_potw_gravity` |
| `head_assumed_low_m` | float64 | Triangular distribution lower bound (m) |
| `head_assumed_mode_m` | float64 | Triangular distribution mode (m) |
| `head_assumed_high_m` | float64 | Triangular distribution upper bound (m) |
| `power_p50_kw` | float64 | Rated power at median η and H, mean flow (kW) |
| `energy_p10_kwh_yr` | float64 | 10th percentile annual energy — conservative estimate |
| `energy_p50_kwh_yr` | float64 | 50th percentile annual energy — central estimate |
| `energy_p90_kwh_yr` | float64 | 90th percentile annual energy — optimistic estimate |
| `energy_mean_kwh_yr` | float64 | Mean annual energy across 10,000 iterations |
| `energy_std_kwh_yr` | float64 | Std dev of annual energy |
| `capacity_factor_p50` | float64 | Median energy / (rated power × 8,766 h) |
| `equivalent_homes_p50` | int32 | `energy_p50_kwh_yr` / 10,500 (US avg household kWh/yr) |

---

## 6. Phase 3 Readiness

Phase 2 outputs are complete and ready to inform Phase 3 (Turbine Sizing and Head Estimation).

| Phase 3 Input Required | Available? | Notes |
|------------------------|-----------|-------|
| `npdes_id` | Yes | From Phase 1 `ranked_candidates.parquet` |
| `latitude`, `longitude` | Yes | From Phase 1 `ranked_candidates.parquet` |
| `energy_yield_estimates.parquet` | Yes | Phase 2 output — used to prioritise which facilities to query USGS for |
| `archetype` | Yes | Informs expected head range before elevation data arrives |
| USGS 3DEP API | External | Live HTTP queries to `epqs.nationalmap.gov/v1/json` — needs internet |

**Key limitation Phase 3 resolves:** Every large plant in Phase 2 received the same `Triangular(3, 8, 15)` m head distribution regardless of actual site topography. A plant discharging at sea level from a 2 m outfall and one discharging down a 12 m bluff both got the same estimate. Phase 3 queries upstream and downstream elevation at each facility's coordinates and computes site-specific net head, collapsing the wide triangular uncertainty into a measured point value (± survey error).
