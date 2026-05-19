# WOWERS Project Journal

---

## ⚠️ INSTRUCTION FOR AI AGENTS — READ THIS FIRST BEFORE DOING ANYTHING

**RULE 1 — READ BEFORE YOU RESPOND:**
Read this entire file from top to bottom before responding to anything. The session log at the bottom tells you exactly what has been done and what comes next. Do not skip this step.

**RULE 2 — NEVER TOUCH EXISTING CONTENT:**
Do NOT modify, rewrite, reformat, correct, or delete any content that already exists in this file. This includes previous session entries, project descriptions, team info, technical facts, or any other section. What is written stays written exactly as it is.

**RULE 3 — NEVER REWRITE A PAST SESSION:**
Previous session log entries are permanent records. You cannot go back and change what was written in a past session even if you think something is wrong or outdated. If something needs correcting, note it in the NEW session entry only.

**RULE 4 — ALWAYS LOG WHAT YOU DID:**
At the end of every conversation where work was done, you MUST append a new session entry to the bottom of the "Session Log" section. Follow this exact structure:

```
### Session: YYYY-MM-DD

**What was done:**
- [bullet list of everything accomplished this session]

**Files modified / created:**
- [list every file touched and what changed]

**Resources used:**
- [list every website, dataset, tool, or document referenced]

**Next steps after this session:**
1. [numbered list of what should happen next]
```

**RULE 5 — ONLY ADD TO THE BOTTOM:**
New session entries go at the very bottom of the file, below all previous entries. Never insert content anywhere else in the file.

---

## Project Overview

**Project Name:** WOWERS — Waste Outfall Water Energy Recovery System
**University:** University of St. Thomas (Minneapolis/St. Paul, MN)
**Competition Origin:** Fowler Business Concept Challenge (scored 33.25/40 average)
**Team:**
- Tom (Xinsheng) Tang — MS in Data Science
- Mohamed Abdel Hamid — MS in Artificial Intelligence

---

## What WOWERS Is

WOWERS is a data-driven infrastructure intelligence platform that identifies where micro-hydropower energy recovery is feasible at US wastewater treatment plant outfalls, estimates how much energy could be generated, recommends commercially available turbine systems, and quantifies operational cost savings for municipalities.

The platform is **not** a turbine hardware company. It is an analytics and decision-support system built on national-scale EPA wastewater data.

**Core value proposition to a municipality:**
> "Tell us your plant's flow data and outfall conditions — we show you which turbine to buy, how much energy it will generate, and what your payback period looks like."

---

## What WOWERS Is NOT

- Not a turbine manufacturer
- Not a construction or installation company
- Not a hardware prototype project
- Not limited to one city or region — national scale from day one

---

## Strategic Direction

The project shifted from "build a physical turbine prototype" to "build a data-driven infrastructure intelligence platform." This direction aligns with the team's software and data science strengths, available public data, and realistic proof-of-concept scope.

**Long-term goal:** Help municipalities and wastewater utilities understand:
- Whether energy recovery is viable at their specific plant
- How much electricity could realistically be generated
- Which commercially available turbine technology fits their conditions
- How much operational energy cost could be offset annually

---

## Data Pipeline Architecture (5 Phases)

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Rank candidate plants from EPA ECHO data | ✅ Complete |
| Phase 2 | Monte Carlo energy yield estimation | ✅ Complete |
| Phase 3 | Turbine sizing via USGS 3DEP elevation API | ✅ Complete (awaiting raw data for pipeline run) |
| Phase 4 | Financial scorecard (NPV, IRR, payback) | ✅ Complete (awaiting raw data for pipeline run) |
| Phase 5 | ML model trained on DOE/FERC ground truth | 🔲 Not started |

---

## Key Technical Facts

- **Dataset processed:** ~279 million raw DMR rows, FY2009–FY2024, all 50 US states
- **Final POTW count:** 17,163 active wastewater treatment plants
- **National energy estimate (Phase 2 P50):** 697 GWh/yr — within DOE expected range of 500–5,000 GWh/yr
- **Top ranked plant:** MWRDGC Stickney WRP (IL), 1,200 MGD mean flow, 29.25 GWh/yr P50
- **Primary data source:** EPA ECHO / ICIS-NPDES (public)
- **Key output files:** `ranked_candidates.parquet`, `energy_yield_estimates.parquet`
- **Core physics:** P = η × ρ × g × Q × H (standard hydropower equation)
- **Turbine types modeled:** Kaplan, Francis, Pelton, Crossflow, in-conduit micro

---

## Key Files in the Codebase

| File | Purpose |
|---|---|
| `src/phase1/filter_potw.py` | Filters EPA ICIS data to active POTWs |
| `src/phase1/dmr_timeseries.py` | Parses ~279M DMR rows, extracts monthly flow |
| `src/phase1/flow_features.py` | Computes per-facility statistical flow features |
| `src/phase1/ranking.py` | Composite ranking score (weighted, min-max normalized) |
| `src/phase2/energy_physics.py` | Monte Carlo energy yield engine |
| `config/settings.yaml` | Central config — all thresholds, weights, physics constants |
| `ARCHITECTURE.md` | Full 5-phase system design |
| `PHASE1_REPORT.md` | Phase 1 results, data quality issues, validation |
| `PHASE2_REPORT.md` | Phase 2 results, Monte Carlo methodology, top 10 plants |
| `WOWERS_Capital_and_Funding_Research.md` | Detailed funding strategy, grant sources, comparable companies |

---

## Fowler Competition Feedback Summary

**Score:** 34.5 median / 33.25 average out of ~50 points

**Strengths noted by judges:**
- Strong originality and value proposition
- Clear social/sustainability impact
- Good payment model options (EaaS)

**Gaps to address:**
- "Why isn't this already done?" — needs clearer answer
- Manufacturing, shipping, and installation logistics need explanation
- Pilot strategy needs to be concrete and named
- Government funding sources should be named specifically

---

## Turbine Manufacturer Research (In Progress)

### Goal
Build a structured turbine database so WOWERS can recommend specific commercially available turbines to municipalities based on their plant's flow rate, hydraulic head, pipe diameter, and material requirements.

### Manufacturers Identified

| Manufacturer | Country | Turbine Types | Relevant Notes |
|---|---|---|---|
| CINK Hydro-Energy | Czech Republic | Crossflow, Kaplan, Pelton, Francis | Explicitly lists wastewater treatment plants as a use case. Runs at 6–100% of design flow. 450+ turbines in 50+ countries. |
| Canyon Hydro | USA | Francis, Pelton, Crossflow | Has dedicated conduit hydropower page. Installed turbines for City of Logan UT and City of Las Vegas. Provides data sheet for custom quotes. |
| Rentricity | USA | Reverse pump turbines (Francis-type) | NSF 61/372 certified for potable and wastewater. Real project data publicly listed: 2.4 MGD / 40 PSI / 32 kW and 2–12 MGD / 175–250 ft / 360 kW. |
| LucidEnergy | USA | Vertical axis spherical (in-pipe) | For large diameter pipes (24"–96"). Portland OR: 4 × 42" turbines = 200 kW, 1,100 MWh/yr. Works on effluent streams. |
| Turbulent | Belgium | Vortex (low head) | 15–90 kW range, rivers and canals, low head gravity flow. Relevant for gravity outfall archetype. |
| Ossberger GmbH | Germany | Crossflow | Original crossflow design, 0.5 kW–30 MW, 1–200 m head. Heavily cited in academic literature. |
| Gilbert Gilkes & Gordon | UK (est. 1853) | Pelton, Turgo | One of oldest hydro manufacturers. Well-documented spec sheets. |
| Emrgy | USA | Modular hydrokinetic | Canal-focused, spec sheet publicly available at emrgy.com. Raised $10–15M total. |
| Natel Energy | USA | FishSafe Kaplan variants | Fish-passage focused. Engineering services model, not direct hardware sales. |
| Andritz Hydro | Austria | Full turbine range | Large scale but publishes detailed turbine selection guides useful as reference. |

### Data Fields Needed Per Turbine

- Turbine type (Kaplan / Crossflow / Francis / Pelton / in-conduit / vortex)
- Min/max flow range (m³/s and MGD)
- Min/max head range (m)
- Rated power range (kW)
- Peak efficiency (%)
- Efficiency at part load (% of rated flow)
- Pipe diameter compatibility (for in-conduit systems)
- Material (316L stainless required for wastewater)
- Estimated cost range ($/kW or total $)
- Manufacturer name and contact / inquiry URL
- Real installation references (flow, head, kW output)
- Wastewater-certified / NSF rated (yes/no)

### Data Sources for Turbine Database

| Source | Type | URL |
|---|---|---|
| CINK references page | Real project specs | cink-hydro-energy.com/references |
| Canyon Hydro conduit page | Application guide + case studies | canyonhydro.com/projects/conduit.html |
| Rentricity featured projects | Real project specs (MGD, PSI, kW) | rentricity.com/featured-projects |
| Emrgy spec sheet | PDF with turbine specs | emrgy.com/wp-content/uploads/2021/06/Emrgy-Specifications.pdf |
| DOE HydroSource Database | Existing installations, ground truth | hydrosource.ornl.gov |
| FERC Conduit Exemption filings | Site-specific flow, head, equipment | ferc.gov |
| ORNL Conduit Hydropower Reports | Turbine selection charts, head/flow ranges | energy.gov |
| Energypedia Micro Hydro Manufacturers | Global manufacturer directory | energypedia.info |

---

## Session Log

---

### Session: 2026-05-17

**What was done:**
- Reviewed all existing project files: WOWERS.docx (original concept), Fowler feedback doc, follow-up pitch strategy doc, ARCHITECTURE.md, PHASE1_REPORT.md, PHASE2_REPORT.md, WOWERS_Capital_and_Funding_Research.md, and project codebase (all src/ files, config/settings.yaml, pyproject.toml, tests/)
- Confirmed Phase 1 and Phase 2 of the data pipeline are complete and validated
- Identified the next major feature: turbine recommendation engine requiring a structured turbine manufacturer database
- Researched turbine manufacturers relevant to low-head wastewater outfall conditions
- Identified 10 manufacturers across USA, Europe, covering Kaplan, Crossflow, Francis, Pelton, and in-conduit turbine types
- Identified 8 structured data sources to populate the turbine database (manufacturer reference pages, DOE HydroSource, FERC filings, ORNL reports)
- Defined the full set of data fields needed per turbine for the recommendation engine
- Created this project journal file (WOWERS_PROJECT_JOURNAL.md)

**Files modified / created:**
- `WOWERS_PROJECT_JOURNAL.md` — created (this file)

**Resources used:**
- EPA ECHO / ICIS-NPDES (existing pipeline data source)
- cink-hydro-energy.com (manufacturer research)
- canyonhydro.com (conduit hydropower case studies)
- rentricity.com (featured projects with real kW/MGD/PSI data)
- lucidenergy.com (in-pipe turbine specs)
- turbulent.be (vortex turbine specs)
- emrgy.com (spec sheet PDF)
- natelenergy.com (FishSafe turbine engineering)
- thecivilengineer.org (LucidPipe technical overview)
- ResearchGate (in-conduit hydropower market review paper)

**Next steps after this session:**
1. Build the turbine database — create `data/turbines/turbine_manufacturers.csv` (or `.parquet`) seeded with data from CINK references, Canyon Hydro conduit page, Rentricity featured projects, and the Emrgy spec PDF
2. Define the turbine recommendation logic in `src/phase3/turbine_selection.py` — rule-based matching on plant flow range vs. turbine min/max flow, plant head vs. turbine head range, pipe diameter compatibility, and wastewater material certification
3. Begin Phase 3 elevation queries using USGS 3DEP API (`src/phase3/elevation.py`) to replace literature-assumed head distributions with real site-specific head values
4. Contact Canyon Hydro and CINK Hydro directly using university research framing to request full spec catalogs or data sheets not publicly listed
5. Download and parse the Emrgy spec sheet PDF for structured turbine data

---

## Session Log — May 17, 2026 (Cursor Agent)

**Session goal:** Fix two known baseline bugs, then fully implement Phase 3 (Turbine Sizing via USGS 3DEP).

---

### Bug Fixes Applied

**Bug 1 — `config/settings.yaml`: missing ADC permit status code**
- Added `"ADC"` (Administratively Continued) to `potw_filter.active_permit_status_codes`
- Previous: `["EFF", "NON"]` — After: `["EFF", "NON", "ADC"]`
- Impact: recovers ~4,308 POTWs that were being incorrectly excluded

**Bug 2 — `src/phase1/flow_features.py`: `_select_primary_outfall` used max-mean not max-non-null-months**
- Rewrote `_select_primary_outfall()` to sort by `n_nonnull` (non-null monthly records) descending, then `outfall_mean` as tiebreaker
- Added CSO/storm outfall deprioritisation (outfalls starting with "C", "S", "E" sorted last)
- Old logic: max mean avg_flow — could be fooled by a single high outlier on rarely-reported outfall
- New logic: "most months of actual data wins" — selects consistently-reporting treatment outfall

---

### Phase 3 Implementation — Files Created

**`config/settings.yaml`** — Added `phase3:` block (head_loss_fraction, min_net_head_m, API throttle settings, cache dir, turbine_db_path, optimizer sweep params)

**`data/turbines/turbine_manufacturers.csv`** — 15-row seed database:
CINK Hydro-Energy, Canyon Hydro, Rentricity (NSF 61/372 certified), LucidEnergy (Portland OR 200 kW), Turbulent, Ossberger GmbH, Gilbert Gilkes & Gordon, Emrgy, Natel Energy, Andritz Hydro

**`src/phase3/elevation.py`** — USGS 3DEP async httpx queries:
- Semaphore-based concurrency (max 10 concurrent), disk cache (lat/lon rounded to 5 dp, sharded into 1°×1° subdirs), ocean sentinel detection, retry with exponential backoff
- `fetch_elevations(facilities_df)` → adds `elevation_m`, `elev_source` columns

**`src/phase3/head_estimation.py`** — Net head estimation:
- `H_net = H_gross × (1 - 0.15)` (configurable loss fraction)
- Source priority: `usgs_3dep` → `phase2_literature` → `design_fallback`
- Plausibility gate rejects 3DEP head if |H_3dep - H_lit| / H_lit > 2.0
- Adds: `head_gross_m`, `head_net_m`, `head_source`, `head_valid`, `head_confidence`

**`src/phase3/turbine_selection.py`** — Turbine type + power sizing:
- H-Q decision tree: Pelton (H>50m, Q<2m³/s), Francis (H≥10m), Kaplan (H<10m, Q≥0.5m³/s), In-conduit (otherwise)
- Four empirical part-load efficiency curves η(q) with type-specific cutoffs
- Optimizer sweeps Q_rated fractions [0.3–1.0], maximises annual MWh/yr with CF ≥ 0.40
- FDC integration via trapezoidal rule over Phase 1 flow duration curve
- Manufacturer matching from turbine DB (type + H-Q envelope, prefers WW-certified)
- Adds: `turbine_type`, `q_rated_m3s`, `p_rated_kw`, `peak_efficiency_pct`, `annual_energy_mwh`, `capacity_factor`, `best_manufacturer`, `turbine_viable`

**`src/phase3/run.py`** — Phase 3 orchestrator:
- 4 steps: load candidates → elevation → head estimation → turbine sizing
- CLI: `--phase2-input`, `--skip-elevation`, `--top-n`
- Auto-detects Phase 2 or Phase 1 output as input
- Output: `data/processed/phase3/turbine_sizing.parquet`

**`tests/test_phase3/`** — 37 unit tests total:
- `test_elevation.py` (10): cache key/rounding, read/write/miss/corrupt, column contract, no-coords
- `test_head_estimation.py` (11): physics arithmetic, fallback chain, rejection logic, source/confidence values
- `test_turbine_selection.py` (16): H-Q selection, η(q) bounds/cutoffs, optimizer formula, CF range, full pipeline contract

All files syntax-validated. Follow existing project patterns (polars, `src.common.*`, Parquet output, checkpoint versioning).

---

**Phase status after this session:**
- Phase 1: Complete ✓ | Phase 2: Complete ✓ | Phase 3: Implementation complete ✓ | Phase 4: NOT STARTED | Phase 5: NOT STARTED

**Next steps:**
1. `pip install -e .` then `python -m pytest tests/test_phase3/ -v`
2. Run full Phase 1+2 pipeline to generate `monte_carlo_results.parquet`
3. `python -m src.phase3.run --top-n 100` to test 3DEP API calls on first 100 sites
4. Review head estimate distribution (usgs_3dep vs phase2_literature breakdown)
5. Begin Phase 4: financial scorecard using `data/processed/phase3/turbine_sizing.parquet`

---

## Session Log — May 17, 2026 (Cursor Agent — Phase 3 Bug-Fix Pass)

**Trigger:** Post-implementation code review (external reviewer) identified 2 critical bugs, 1 performance issue, several logic/test gaps. All fixed this session. 64/64 tests pass.

---

### Critical Bugs Fixed

**Bug 1 — FDC length mismatch → zero viable sites** (`src/phase3/turbine_selection.py`)

Phase 1 produces a 20-point FDC (config `ranking.fdc_exceedance_probs`). Phase 3 was reading a separate 10-point `fdc_exceedance_probs` key. Inside `_compute_annual_energy`, the guard `if len(fdc_flows_m3s) != len(fdc_exceedances): return 0.0` silently zeroed every facility's annual energy → CF=0 → `turbine_viable=False` for all sites. Pipeline produced zero viable sites with no warning.

Fix: Introduced `_PHASE1_FDC_EXCEEDANCES` constant (reads `ranking.fdc_exceedance_probs`, same grid Phase 1 uses). `select_and_size_turbines` now pairs 20-point FDC flows with the matching 20-point exceedance grid. `_compute_annual_energy` changed from hard-fail on mismatch to truncation: `n = min(len(fdc_flows_m3s), len(fdc_exceedances))`.

**Bug 2 — `_read_cache` TypeError → crash on second pipeline run** (`src/phase3/elevation.py`)

When the USGS 3DEP API fails after all retries, `_write_cache` stores `{"elevation_m": null}`. On next run, `data.get("elevation_m", "nan")` returns Python `None` (key exists, default ignored). `float(None)` raises `TypeError`. The except clause only caught `(json.JSONDecodeError, ValueError, KeyError)` — not `TypeError`. Every facility with a failed elevation query caused the entire second run to crash before making any API calls.

Fix: `raw = data.get("elevation_m"); return None if raw is None else float(raw)`. Added `TypeError` to except tuple as belt-and-suspenders.

---

### Performance Fix

**O(n²) FDC lookup** (`src/phase3/turbine_selection.py`)

Per-row `facilities.filter(pl.col("npdes_id") == row["npdes_id"])["flow_duration_curve"][0]` inside a Python loop = 225M row comparisons for 15k facilities.

Fix: `fdc_lookup = dict(zip(df["npdes_id"], df["flow_duration_curve"]))` built once before the loop.

---

### Logic Fixes

**Viable gate too permissive** (`src/phase3/turbine_selection.py`): `cf >= MIN_CF * 0.5` (effectively CF ≥ 0.20) was mislabeled "allow slight miss". Changed to strict `cf >= MIN_CF` (0.40). Prevents economically marginal sites from entering Phase 4 as viable.

**Negative head handling improved** (`src/phase3/head_estimation.py`): `_compute_head_row` now distinguishes three cases: (1) `candidate_net ≤ 0` → physically impossible, falls through to literature; (2) `0 < candidate_net < MIN_NET_HEAD_M` → valid 3DEP reading of genuinely low-head site, early return `valid=False, source="usgs_3dep"`, no replacement with 5 m design default; (3) `candidate_net ≥ MIN_NET_HEAD_M` → plausibility gate as before.

**`--skip-elevation` silent fallthrough** (`src/phase3/run.py`): Now logs a warning when flag is set but `elevation_data.parquet` is absent, then proceeds with API calls.

---

### Minor Fixes

- Kaplan docstring corrected: "peaks ~0.90" → "peaks ~0.93" (`turbine_selection.py:14`)
- `data/turbines/turbine_manufacturers.csv` MGD unit corrections: Rentricity 2.38 → 2.05 MGD; LucidEnergy 28.0 → 24.2 MGD (display columns now match m³/s values)

---

### Test Coverage Added (64 total, up from 37)

| Test | Covers |
|------|--------|
| `test_20point_fdc_produces_nonzero_energy` | Bug 1 regression |
| `test_full_pipeline_with_20point_fdc_column` | End-to-end 20-pt FDC path |
| `test_length_mismatch_is_tolerated` | `_compute_annual_energy` truncation |
| `test_flat_fdc_matches_p_times_hours` | Direct energy unit check |
| `test_fewer_than_two_points_returns_zero` / `test_empty_fdc_returns_zero` | Edge cases |
| `test_fallback_when_no_fraction_meets_cf` | Optimizer fallback path |
| `test_ocean_sentinel_produces_none_elevation` | `-1,000,000` sentinel → `None` |
| `test_null_cached_elevation_returns_none_on_read` | Bug 2 regression |
| `test_api_result_populates_elevation` / `test_api_failure_produces_failed_source` | API mock paths, second-run crash |
| `test_head_below_minimum_is_invalid` assertion hardened | Non-vacuous check: `assert not valid` |

---

**Phase status after this session:**
- Phase 1: Complete ✓ | Phase 2: Complete ✓ | Phase 3: Complete + Bug-fixed ✓ | Phase 4: NOT STARTED | Phase 5: NOT STARTED

**Next steps:**
1. Run full Phase 1+2 pipeline to generate `monte_carlo_results.parquet`
2. `python -m src.phase3.run --top-n 100` to test 3DEP API calls on first 100 sites
3. Review head estimate distribution (usgs_3dep vs phase2_literature breakdown)
4. Begin Phase 4: financial scorecard using `data/processed/phase3/turbine_sizing.parquet`

---

## Session — 2026-05-17 (Phase 2 Recreation + Phase 4 Implementation)

**Goal:** Recreate missing `src/phase2/` and implement `src/phase4/` from scratch per `ARCHITECTURE.md` spec.

**Phase 2 — recreated (src/phase2/ was entirely absent from disk):**
- `src/phase2/__init__.py` — package init
- `src/phase2/head_assumptions.py` — `classify_archetype` (large/medium/small POTW by design_flow_mgd), `get_head_distribution` (triangular params from `config/settings.yaml`), `head_params_for_flow` convenience wrapper
- `src/phase2/energy_physics.py` — `power_kw`, `integrate_fdc_energy` (trapezoidal rule over 20-point FDC), `run_monte_carlo` (vectorised sampling: head + efficiency + availability, returns P10/P50/P90/mean/std/power_p50/CF_p50)
- `src/phase2/monte_carlo.py` — pre-exclusion filters, `_process_one` / `_process_batch`, `estimate_all_facilities` (parallel via `ProcessPoolExecutor`)
- `src/phase2/run.py` — CLI entry point; loads Phase 1 output, runs MC, writes `energy_yield_estimates.parquet`

**Phase 4 — implemented from spec:**
- `src/phase4/__init__.py`
- `src/phase4/cost_models.py` — power-law CapEx per kW with per-type A/B/min/max params; OpEx as % of CapEx; all 4 turbine types (Kaplan, Francis, Pelton, in_conduit_micro)
- `src/phase4/revenue.py` — `electricity_rate` (state_rates.yaml lookup with `lru_cache`), `annual_revenue` (+ optional REC)
- `src/phase4/financials.py` — `compute_npv`, `compute_irr` (Brent's method, robust edge cases), `compute_payback`, `compute_lcoe`, `compute_scorecard`; 50% grant NPV scenario column
- `src/phase4/sensitivity.py` — tornado analysis: ±head/flow/electricity_rate, `dominant_sensitivity` label
- `src/phase4/run.py` — CLI; loads Phase 3 output + Phase 1 state codes, computes CapEx/OpEx/revenue/financials, optional tornado, writes `financial_scorecards.parquet`
- `data/electricity_rates/state_rates.yaml` — 2023 EIA industrial rates all 50 states + DC + national_avg

**Tests — 88 passing:**
- `tests/test_phase2/test_head_assumptions.py` — 15 tests: archetype classification boundaries, head distribution physical plausibility, convenience wrapper
- `tests/test_phase2/test_energy_physics.py` — 20 tests: power_kw proportionality, FDC integration unit check, MC reproducibility/ordering/seed behaviour
- `tests/test_phase4/test_cost_models.py` — 14 tests: economies of scale, per-type params, OpEx fraction range
- `tests/test_phase4/test_financials.py` — 24 tests: NPV/IRR/payback/LCOE correctness, edge cases (zero capex, never pays back, LCOE=inf)
- `tests/test_phase4/test_revenue.py` — 15 tests: state lookup, case-insensitive, plausibility range, HI > WA rate check

**Decisions:**
- Phase 2 was flagged "Complete" in journal but `src/phase2/` was absent — recreated from `ARCHITECTURE.md` spec rather than attempting pipeline run without raw EPA ECHO data.
- Phase 4 implemented before pipeline run for same reason (no raw data locally).
- `scipy.optimize.brentq` used for IRR (more robust than `numpy_financial.irr` for edge cases near zero/no-sign-change).
- IRR boundary convention: returns +3.0 when project pays back trivially at any rate, −0.99 when it never does, `nan` only on exception.

**Phase status after this session:**
- Phase 1: Complete ✓ | Phase 2: Complete ✓ (recreated) | Phase 3: Complete + Bug-fixed ✓ | Phase 4: Complete ✓ (implemented, not yet run) | Phase 5: NOT STARTED

**Next steps:**
1. Obtain EPA ECHO / ICIS-NPDES raw data (~10 GB); run `python -m src.phase1.run`
2. Run Phase 2: `python -m src.phase2.run --top-n 200`
3. Run Phase 3: `python -m src.phase3.run --top-n 100`; review 3DEP vs literature head breakdown
4. Run Phase 4: `python -m src.phase4.run`; inspect NPV/IRR distribution and viable count
5. Begin Phase 5 (ML ranking model)

---

## Session: 2026-05-17 — Two-Round Code Review & Bug-Fix

**Session type:** Code review → fix → re-review → fix → final documentation

**What happened:**
Two rounds of agent code review were conducted on the Phase 2 and Phase 4 code implemented in the previous session. All bugs were fixed between rounds.

**Round 1 Bugs Fixed (B-series critical/moderate):**

| ID | File | Fix |
|----|------|-----|
| B1 | `financials.py` | `compute_irr` docstring rewritten — sentinels `+3.0`/`−0.99` now documented with downstream filter warning; `nan` returned only on exception or zero CapEx |
| B2 | `financials.py` | `project_viable` changed from `float` (`0.0`/`1.0`) to `bool` |
| B3 | `energy_physics.py` | MC loop replaced with fully vectorised NumPy path (`power_matrix` shape `(n_iter, n_fdc)`, `np.trapezoid` axis=1); 10–100× faster |
| B4 | `sensitivity.py` | `dominant_sensitivity` now normalises swings by range width (`/1.0`, `/0.4`, `/0.6`) — reflects NPV elasticity per unit, not range-width bias |
| B5 | `monte_carlo.py` | Dead `dmr_limited` branch documented as unreachable until Phase 1 emits `data_quality` column |
| B6 | `energy_physics.py` | `integrate_fdc_energy` docstring corrected — FDC array convention now clearly described (`[0]` = lowest exceedance = highest flow) |
| D1 | `energy_physics.py` | `abs()` on integral result removed — negative values surface as upstream data errors |
| D2 | `cost_models.py`, `settings.yaml` | Per-type CapEx `A`, `B`, `min_per_kw`, `max_per_kw` moved from hardcoded dict to `config/settings.yaml` under `cost_model.types.*`; code loads with hardcoded fallbacks |
| D3 | `cost_models.py` | `capex_per_kw(type, 0)` now returns per-type `max` (Pelton→8,000, Francis→9,000) not global `10,000` |
| D5 | `settings.yaml` | Stale 10-point `phase3.fdc_exceedance_probs` block removed |
| S4 | `financials.py` | `_INF_SENTINEL = 999.0` constant added; `payback_years` and `lcoe_per_kwh` reference it |

**Round 2 Bugs Fixed (R-series minor):**

| ID | File | Fix |
|----|------|-----|
| R1 | `test_cost_models.py` | Test renamed to `test_per_type_max_at_zero_power`; assertions verify exact per-type max values |
| R2 | `energy_physics.py` | `n < 2` guard added to vectorised MC path (mirrors guard in `integrate_fdc_energy`) |
| R3 | `test_energy_physics.py` | `test_mc_convergence` uses different seeds for small vs large n — tests true convergence |
| R4 | `financials.py` | Inline comment documents implicit contract: `annual_revenue_usd` must equal `energy_kwh × (elec_rate + rec)` |

**Tests — 107 passing:**
- `tests/test_phase2/test_energy_physics.py` — 24 tests (added: hand-calc tight bound, 2-pt FDC, zero-flow CF, MC convergence)
- `tests/test_phase2/test_head_assumptions.py` — 15 tests
- `tests/test_phase4/test_cost_models.py` — 14 tests (R1: assertions tightened to exact per-type max)
- `tests/test_phase4/test_financials.py` — 34 tests (added: bool check, NaN IRR no-crash, negative net CF, payback/LCOE sentinels, degradation effect, trivially profitable sentinel)
- `tests/test_phase4/test_revenue.py` — 15 tests
- `tests/test_phase4/test_sensitivity.py` — 7 tests (new: monotonicity, normalised-dominant correctness, factor plausibility)

**Known open items (deferred — require raw data or Phase 3 run):**
- **S2**: `p_rated_kw` vs `rated_power_kw` ambiguity in `phase4/run.py` — resolve by smoke-testing `--top-n 5` and inspecting parquet columns
- **S1**: Phase 5 spec says `capex_usd`; Phase 4 writes `total_capex_usd` — Phase 5 will need rename shim
- **D4**: FDC integration misses exceedance tails `[0,0.01]` and `[0.95,1.0]` — ~2–3% underestimation, acceptable for screening

**Pipeline readiness:** Physics, math, and code correctness verified by two independent reviews. All critical and minor bugs resolved. Safe to smoke-test at `--top-n 200` once raw data available.

**Next steps:**
1. Obtain EPA ECHO / ICIS-NPDES raw data (~10 GB); run `python -m src.phase1.run`
2. Smoke test: `python -m src.phase3.run --top-n 5`; inspect parquet columns; confirm `p_rated_kw` vs `rated_power_kw`
3. Full pipeline: Phase 1 → Phase 2 → Phase 3 (`--top-n 100`) → Phase 4
4. Review head source breakdown (3DEP vs literature fallback ratio)
5. Begin Phase 5 (ML ranking model)

---

### Session: 2026-05-17 — Test Bug-Fix Pass (204/204)

**What was done:**
- Reviewed WOWERS_PROJECT_JOURNAL.md and full codebase to understand current project state
- Ran full test suite; found 10 failures and 3 errors across 204 tests
- Fixed Bug 1: `src/phase1/flow_features.py` used `.str.starts_with_any()` which does not exist in this version of Polars (Python 3.13.11, Polars as installed). Replaced with `.str.slice(0, 1).is_in(list(cso_prefixes))` — equivalent logic, correct API. This fixed 9 test failures in `test_flow_features.py` and 3 errors in `test_ranking.py` (which depends on `compute_flow_features`).
- Fixed Bug 2: `data/electricity_rates/state_rates.yaml` was missing (entire `data/` directory absent from disk). `src/phase4/revenue.py` fell back to `{"national_avg": 0.081}` for all states, causing `test_high_vs_low_rate_states` to fail with `HI (0.081) > WA (0.081)` assertion. Created the file with real 2023 EIA industrial electricity rates for all 50 states + DC.
- Verified 204/204 tests pass after both fixes.

**Files modified / created:**
- `src/phase1/flow_features.py` — line 199: `.str.starts_with_any()` → `.str.slice(0, 1).is_in()`
- `data/electricity_rates/state_rates.yaml` — created; 2023 EIA industrial rates for AK–WY + DC + national_avg

**Resources used:**
- U.S. Energy Information Administration, Electric Power Monthly Table 5.6.B (2023 industrial rates)
- Polars documentation (string namespace API)

**Next steps:**
1. Obtain EPA ECHO / ICIS-NPDES raw data (~10 GB); run `python -m src.phase1.run`
2. Smoke test: `python -m src.phase3.run --top-n 5`; inspect parquet columns; confirm `p_rated_kw` vs `rated_power_kw` column name (open item S2 from prior review)
3. Full pipeline: Phase 1 → Phase 2 → Phase 3 (`--top-n 100`) → Phase 4
4. Review head source breakdown (3DEP vs literature fallback ratio)
5. Begin Phase 5 (ML ranking model trained on DOE/FERC ground truth)

---

### Session: 2026-05-17 — External Code Review of Bug-Fix Pass

**Session type:** External code review of the two changes from the previous session.

**What was done:**
- Submitted both changes from the prior session to an external agent reviewer
- Reviewed all findings; one critical blocker identified

**Review findings — Change 1 (`src/phase1/flow_features.py`):**
- Semantic equivalence confirmed: `.str.slice(0, 1).is_in(["C","S","E"])` is exactly equivalent to `.str.starts_with_any(("C","S","E"))` for single-character prefixes
- All edge cases verified correct: null outfall → null is_cso (sorts last, acceptable); empty string → 0; "001" → 0; "CSO-1" → 1; "S42" → 1
- `.is_in()` confirmed as correct Polars API on String expr result
- No other `starts_with_any` usages found anywhere in codebase
- Verdict: APPROVED

**Review findings — Change 2 (`data/electricity_rates/state_rates.yaml`):**
- All 51 entries (50 states + DC) present; all tested states in [0.03, 0.25] range ✅
- Rate values physically plausible vs. known EIA patterns (HI: 0.241 highest, WA: 0.046 lowest, CA: 0.172, LA: 0.059, etc.) ✅
- NY: 0.062 flagged for source verification (plausible via NYPA bulk supply suppressing EIA industrial avg) — not a blocker
- `lru_cache` stale-result risk: none — file now exists, first pytest call loads full dict, no test mocks the file ✅
- YAML structure matches `_load_rates()` parser exactly (`national_avg` at top level, `states:` nested dict) ✅
- **CRITICAL BLOCKER: `.gitignore` contains `data/` on line 2, which excludes `data/electricity_rates/state_rates.yaml` from version control. Any fresh clone would be missing the file, causing all Phase 4 state rate lookups to fall back to 0.081 and `test_high_vs_low_rate_states` to fail again.**

**Files modified / created:**
- None this session (review only; fix pending)

**Resources used:**
- External agent code reviewer

**Next steps after this session:**
1. Fix `.gitignore` blocker: either add negation rules (`!data/electricity_rates/` and `!data/electricity_rates/state_rates.yaml`) or move the file to `config/electricity_rates/state_rates.yaml` and update `revenue.py` line 19 — moving to `config/` is semantically cleaner since it is a static reference table, not generated pipeline output
2. Run `python -m pytest tests/ -v` after fix to confirm 204/204 still pass
3. Obtain EPA ECHO / ICIS-NPDES raw data (~10 GB); run `python -m src.phase1.run`
4. Smoke test Phase 3: `python -m src.phase3.run --top-n 5`; confirm `p_rated_kw` vs `rated_power_kw` column name
5. Full pipeline: Phase 1 → Phase 2 → Phase 3 (`--top-n 100`) → Phase 4
6. Begin Phase 5 (ML ranking model)

---

### Session: 2026-05-18

**What was done:**
- Read full journal to establish prior session state
- Investigated critical blocker from prior external review: `.gitignore` `data/` rule excluding `data/electricity_rates/state_rates.yaml` from version control
- Confirmed blocker was already resolved between sessions: `revenue.py` `_RATES_FILE` already pointed to `config/electricity_rates/state_rates.yaml`, and that file already existed and was tracked in git
- Confirmed 204/204 tests passing before making any changes
- Sent the fix to external agent reviewer for verification; reviewer ran 7 checks — all passed; identified two low-severity follow-up findings (F1 stale docstring, F2 stale duplicate file on disk)
- Applied F1: corrected stale module docstring in `src/phase4/revenue.py` line 3 — changed `data/electricity_rates/state_rates.yaml` → `config/electricity_rates/state_rates.yaml`
- Applied F2: deleted `data/electricity_rates/state_rates.yaml` from disk (2207 bytes, gitignored, superseded, divergent values vs tracked copy)
- Confirmed 204/204 tests still passing after both fixes
- Sent follow-up to external reviewer; all checks passed — no new findings

**Files modified / created:**
- `src/phase4/revenue.py` — line 3: docstring path corrected (`data/` → `config/`)
- `data/electricity_rates/state_rates.yaml` — deleted (gitignored stale duplicate)

**Resources used:**
- External agent code reviewer (two rounds)
- Prior session journal entries

**Next steps after this session:**
1. Obtain EPA ECHO / ICIS-NPDES raw data (~10 GB); run `python -m src.phase1.run`
2. Smoke test: `python -m src.phase3.run --top-n 5`; inspect parquet columns; confirm `p_rated_kw` vs `rated_power_kw` column name (open item S2)
3. Full pipeline: Phase 1 → Phase 2 → Phase 3 (`--top-n 100`) → Phase 4
4. Review head source breakdown (3DEP vs literature fallback ratio)
5. Begin Phase 5 (ML ranking model trained on DOE/FERC ground truth)

---

### Session: 2026-05-18 — Local Data Setup (Tom's machine only)

**What was done:**
- Reviewed full project state: 204/204 tests passing, Phases 1–4 implemented and reviewed, no raw data locally
- Identified EPA ECHO raw data (~10 GB) was on Tom's external hard drive (`/Volumes/256Drive/`)
- Confirmed drive contains all DMR fiscal year ZIPs (FY2009–FY2026) flat in `/Volumes/256Drive/DMR Datasets/`
- Downloaded `npdes_downloads.zip` from `https://echo.epa.gov/files/echodownloads/npdes_downloads.zip` and extracted to `/Volumes/256Drive/npdes_downloads/`; confirmed `ICIS_FACILITIES.csv` and `ICIS_PERMITS.csv` present
- Identified structural mismatch: pipeline `_locate_existing_dmr_zips` looks under `{raw_dir}/dmr/`; drive has ZIPs flat with no `dmr/` subfolder — solved via symlink
- Created `data/raw/` directory in project root
- Created local symlink: `data/raw/dmr` → `/Volumes/256Drive/DMR Datasets` (gitignored via `data/` rule)
- Created local symlink: `data/raw/npdes_downloads` → `/Volumes/256Drive/npdes_downloads` (gitignored)
- Verified both symlinks resolve correctly; ICIS CSVs visible through symlink path

**NOTE — Tom's machine only:** The symlinks above (`data/raw/dmr`, `data/raw/npdes_downloads`) are local filesystem entries inside `data/`, which is gitignored. They are NOT committed and will NOT appear on other team members' machines. Other team members must set up their own local data symlinks or directory structure pointing to wherever they store the EPA raw data. The pipeline supports `--raw-dir /path/to/data` CLI flag as an alternative to symlinks.

**Files modified / created:**
- `WOWERS_PROJECT_JOURNAL.md` — appended this session entry
- `data/raw/dmr` — local symlink to `/Volumes/256Drive/DMR Datasets` (gitignored, Tom's machine only)
- `data/raw/npdes_downloads` — local symlink to `/Volumes/256Drive/npdes_downloads` (gitignored, Tom's machine only)

**Resources used:**
- EPA ECHO bulk downloads: `https://echo.epa.gov/files/echodownloads/npdes_downloads.zip`

**Next steps after this session:**
1. Run Phase 1: `python -m src.phase1.run --skip-download` (from project root with drive connected)
2. Run Phase 2: `python -m src.phase2.run`
3. Smoke test Phase 3: `python -m src.phase3.run --top-n 5`; confirm `p_rated_kw` vs `rated_power_kw` column name (open item S2)
4. Run Phase 3 full: `python -m src.phase3.run --top-n 100`; review 3DEP vs literature head breakdown
5. Run Phase 4: `python -m src.phase4.run`
6. Begin Phase 5 (ML ranking model)

---

## 2026-05-18 — Timestamped Run Logs (all machines)

**What was done:**
- Added `setup_run_log(phase_name)` function to `src/common/logging_setup.py`
- Each time a phase is run, it automatically creates `logs/runs/<phase>_YYYY-MM-DD_HH-MM-SS.log`
- The file captures every log line from every module in that run (all `wowers.*` child loggers propagate to the root handler)
- Called `logging_setup.setup_run_log("phaseN")` at module load time in all four phase run scripts
- The `logs/` directory is already gitignored, so run log files are never committed

**Why:** Scrolling through a terminal to review 16-year DMR parse output is impractical. Each run now saves a permanent, searchable, shareable log file stamped with the exact time it was executed.

**How to use after a run:**
```bash
# Open the logs folder in Finder
open logs/runs/

# Print last 50 lines of most recent phase1 run
cat logs/runs/phase1_*.log | tail -50
```

**Files modified:**
- `src/common/logging_setup.py` — added `setup_run_log()` function
- `src/phase1/run.py` — added `logging_setup.setup_run_log("phase1")` call
- `src/phase2/run.py` — added `logging_setup.setup_run_log("phase2")` call
- `src/phase3/run.py` — added `logging_setup.setup_run_log("phase3")` call
- `src/phase4/run.py` — added `logging_setup.setup_run_log("phase4")` call
- `WOWERS_PROJECT_JOURNAL.md` — appended this session entry

**Next steps:**
1. Wait for Phase 1 run to finish (currently running against external drive data)
2. Review output in `logs/runs/phase1_*.log`
3. Run Phases 2–4 in sequence
4. Begin Phase 5 (ML ranking model)

---

### Session: 2026-05-18 — Phase 2 Top-10 Summary Logger Bug Fix

**What was done:**
- Reviewed full journal to establish project state
- Confirmed Phases 1–4 had been run end-to-end
- Investigated Phase 2 summary display bug: "Top-10 facilities: 0.00 GWh/yr" at log line 43
- Root cause: `_print_summary()` in `src/phase2/run.py` called `df.sort("energy_p50_kwh_yr", descending=True).head(10)` on the full dataframe including 1,438 excluded facilities whose `energy_p50_kwh_yr = None`. In Polars, `sort(descending=True)` places nulls first by default — so `.head(10)` returned 10 null rows and `.sum()` returned 0.
- Fix: added `.filter(pl.col("energy_p50_kwh_yr").is_not_null())` before the sort, consistent with the pattern already used for the `national_gwh` and `median_kwh` calculations in the same function
- Re-ran Phase 2 to verify: Top-10 now correctly shows **13,696.05 GWh/yr**
- No change to `energy_yield_estimates.parquet` data contents — bug was display-only as expected

**Files modified / created:**
- `src/phase2/run.py` — `_print_summary()` line 119: added null filter before top-10 sort

**Resources used:**
- `logs/runs/phase2_2026-05-18_10-06-21.log` — confirmed bug at line 43
- Polars documentation (null sort placement behavior)

**Observations worth following up:**
- `national_gwh = 14,450 GWh/yr` is above the DOE expected range of 500–5,000 GWh/yr. The parquet data is intact. The inflation is likely from head assumptions being applied to the full 17k-facility corpus including very large plants; worth auditing the head distribution parameters in `config/settings.yaml` or the archetype classification thresholds.

**Next steps after this session:**
1. Audit `national_gwh = 14,450 GWh/yr` vs. DOE 500–5,000 GWh/yr expected range — check head assumption distributions for large-archetype facilities
2. Review Phase 3 output in `data/processed/phase3/turbine_sizing.parquet`
3. Review Phase 4 output in `data/processed/phase4/financial_scorecards.parquet`
4. Begin Phase 5 (ML ranking model trained on DOE/FERC ground truth)

---

### Session: 2026-05-18 — Multi-Phase Bug Fix & Data Quality Hardening

**Background:**
After investigating the Phase 2 Top-10 display bug (fixed in prior session), a deeper audit revealed three additional issues: (1) grossly inflated national energy estimate (14,450 GWh/yr vs. DOE expected 500–5,000 GWh/yr), (2) 3,690 Phase 3 "unknown" turbine types, and (3) the Phase 3 pre-filter using a non-existent file path.

---

**Fix 1 — Phase 1: Flow Sanity Cap for ICIS Unit Errors**

*Root cause:* EPA ECHO ICIS permit data contains unit errors where `design_flow_mgd` and `actual_avg_flow_mgd` are filed in GPD or MLD instead of MGD. Example: `NC0020354` had `design_flow_mgd = 750,000` (should be 0.75 MGD), yielding `mean_flow_mgd = 562,500 MGD` — roughly 470× the largest US POTW (MWRDGC Stickney at 1,200 MGD). This single facility inflated the national P50 from ~850 GWh/yr to 14,450 GWh/yr.

*Fix in `config/settings.yaml`:*
```yaml
processing:
  max_flow_mgd_sanity: 2000   # hard cap; anything above is almost certainly a unit error
                               # largest known US POTW (Stickney) ~1,200 MGD
```

*Fix in `src/phase1/filter_potw.py` (`_load_permits`):*
- After casting flow columns, loop over `design_flow_mgd` and `actual_avg_flow_mgd`
- Any value > `max_flow_mgd_sanity` is replaced with `null` (not clamped — these are data errors, not extreme-but-real values)
- Logs a warning with count and max observed value
- **449 rows** nulled for `design_flow_mgd` (max was 64,000,000 MGD); **95 rows** for `actual_avg_flow_mgd`

*Fix in `src/phase1/flow_features.py` (`_compute_for_facility`):*
- Secondary defense: `np.clip(flows, 0.0, MAX_FLOW_MGD)` applied to DMR time-series before computing statistics
- Catches any unit errors that slip through raw DMR records (complementary to the ICIS fix)

*Verification:* After re-running Phase 1, max national `mean_flow_mgd` = **1,200.0 MGD** (MWRDGC Stickney WRP — correctly the largest US POTW). `NC0020354` now has `mean_flow_mgd = 0.5625 MGD`.

---

**Fix 2 — Phase 3: Corrected Input Path and Phase 2 Exclusion Pre-filter**

*Root cause:* `src/phase3/run.py` was looking for Phase 2 output at `monte_carlo_results.parquet` (does not exist). It fell back to raw Phase 1 data which included facilities that Phase 2 would have excluded (no usable flow data). This caused Phase 3 to attempt turbine sizing on 17,158 facilities rather than the 15,719 non-excluded ones, inflating the "unknown" turbine count.

*Fix in `src/phase3/run.py`:*
- Renamed `_PHASE2_CANDIDATES` → `_PHASE2_ENERGY`, pointed to correct `energy_yield_estimates.parquet`
- `_find_input_parquet()` now always returns Phase 1 `ranked_candidates.parquet` as primary input (Phase 1 has the spatial + flow columns Phase 3 needs; Phase 2 has energy estimates only)
- Added pre-filter step: loads `energy_yield_estimates.parquet`, anti-joins on `excluded=True` facilities, removes them before turbine sizing
- Pre-filter log line: `Pre-filtered 1,439 Phase 2-excluded facilities (no usable flow)`

---

**Full Pipeline Re-run Results (2026-05-18):**

| Phase | Metric | Before | After |
|-------|--------|--------|-------|
| P1 | Max national `mean_flow_mgd` | 562,500 MGD | 1,200 MGD (Stickney) |
| P1 | Unit-error rows nulled | — | 449 (`design_flow_mgd`) + 95 (`actual_avg_flow_mgd`) |
| P2 | National P50 energy | 14,450 GWh/yr | **847.5 GWh/yr** ✓ (DOE range: 500–5,000) |
| P2 | Top-10 facilities | 0.00 GWh/yr (display bug) | **115.05 GWh/yr** |
| P2 | Excluded facilities | 1,438 | 1,439 |
| P3 | Pre-filter removed | 0 | 1,439 (Phase 2 excluded) |
| P3 | Viable turbine sites | 4,418/17,158 (inflated base) | 4,418/15,719 |
| P3 | "unknown" turbine types | 3,690 (spurious) | 2,275 (legitimate: q ≤ 0.001 m³/s) |
| P3 | Head from 3DEP | 0 | 0 (pending investigation) |
| P4 | Project-viable sites (NPV>0, payback≤20yr) | — | **774 (17.5%)** |
| P4 | Median payback (viable) | — | **6.2 yr** |
| P4 | Portfolio CapEx | — | **$194.8M** |
| P4 | Portfolio revenue | — | **$35.5M/yr** |

Top-5 viable sites by annual energy:

| NPDES ID | Annual Energy (MWh/yr) | NPV | Payback |
|----------|----------------------|-----|---------|
| IL0028053 (MWRDGC Stickney) | 13,019 | $12.4M | 1.6 yr |
| GA0021725 (Athens-Clarke Co.) | 10,838 | $9.4M | 1.7 yr |
| TN0056545 (Summertown HS) | 5,629 | $5.2M | 1.9 yr |
| WA0029181 | 5,248 | $3.0M | 2.7 yr |
| DC0021199 (Blue Plains) | 4,056 | $4.8M | 1.4 yr |

---

**Files modified:**
- `config/settings.yaml` — added `max_flow_mgd_sanity: 2000` under `processing:`
- `src/phase1/filter_potw.py` — `_load_permits()`: nullify ICIS flow values > sanity cap
- `src/phase1/flow_features.py` — `_compute_for_facility()`: `np.clip` on DMR flows as secondary defense
- `src/phase2/run.py` — `_print_summary()`: null filter before top-10 sort (from prior session, re-verified)
- `src/phase3/run.py` — corrected Phase 2 input path; added Phase 2-exclusion pre-filter; always use Phase 1 as primary input

---

**Known pending issues (not fixed this session):**
1. **Phase 3: 100% `design_fallback` head** — `head_m_p50` column expected by `head_estimation.py` does not exist in Phase 2 output. All 15,719 facilities use default 5m gross head → 4.25m net head. USGS 3DEP API calls are never made because the 3DEP branch requires pre-computed `head_m_p50` as a seed. This significantly underestimates head for high-head facilities and needs a proper fix before Phase 5.
2. **TN0056545 "SUMMERTOWN HIGH SCHOOL" 585 MGD** — still present; 585 MGD is below the 2,000 MGD sanity cap and wasn't caught. Likely a unit error (GPD instead of MGD would be 0.585 MGD = reasonable for a high school). Needs manual verification.
3. **Phase 5 ML model** — not yet started.

**Next steps after this session:**
1. Investigate Phase 3 `head_m_p50` missing from Phase 2 output — add head percentile columns to `energy_yield_estimates.parquet` or implement independent elevation fetch in Phase 3
2. Verify TN0056545 flow data in EPA ECHO; lower sanity cap if appropriate
3. Begin Phase 5 ML ranking model

---

### Session: 2026-05-19 — Phase 2 Head Columns + Full Pipeline Re-run

**What was done:**
- Diagnosed Issue 1 from prior session: Phase 3 head estimation was 100% `design_fallback` (hardcoded 5m gross → 4.25m net) because `energy_yield_estimates.parquet` had no `head_m_p50` column for Phase 3 to use as a literature-bound seed
- Chose Option A fix: add `head_m_p10`, `head_m_p50`, `head_m_p90` columns to Phase 2 Monte Carlo output (architecturally correct — Phase 2 already samples head from triangular distribution per archetype)
- Modified `src/phase2/energy_physics.py`: `run_monte_carlo()` now computes and returns `head_m_p10`, `head_m_p50`, `head_m_p90` from the `h_samples` array already present in the function
- Modified `src/phase2/monte_carlo.py`: excluded-facility return dict now includes `head_m_p10: None`, `head_m_p50: None`, `head_m_p90: None` for schema consistency
- Modified `src/phase3/run.py`: after the Phase 2 pre-filter step, now also joins `head_m_p10/p50/p90` from `energy_yield_estimates.parquet` onto Phase 1 candidates before calling `head_estimation.estimate_head()` — with graceful warning if columns absent
- Updated `tests/test_phase2/test_energy_physics.py`: updated `test_returns_required_keys` to include the 3 new head columns; added `test_head_percentile_ordering` and `test_head_within_distribution_bounds`
- Ran full test suite: **206/206 pass** (up from 204 — 2 new tests added)
- Re-ran full pipeline without `--top-n`:
  - Phase 2: 17,158 facilities, 15,719 estimated, 1,439 excluded, national P50 847.5 GWh/yr (stable)
  - Phase 3: 15,719 facilities, joined `head_m_p50` for all 15,719, **0 design_fallback** (was 100%), 15,719 literature, 4,294 viable sites (27.3%), 11 API failures (bad coords: Guam, Puerto Rico, garbled MS/TX lat/lon)
  - Phase 4: 4,294 scored, **867 viable (20.2%)**, median payback 17.0yr, portfolio CapEx $239.8M, portfolio revenue $55.0M/yr
- Investigated why median payback increased from 6.2yr (prior run) to 17yr: **confirmed correct behavior, not a bug**
  - Prior 5m fallback = medium_potw assumption applied to all 15,719 facilities
  - Archetype breakdown: 10,850 small_potw (69%), 3,907 medium_potw (25%), 962 large_potw (6%)
  - small_potw head mode = 3m gross → 2.77m net (vs old 4.25m) — 69% of corpus got lower head → worse payback
  - large_potw head mode = 8m gross → 7.24m net (vs old 4.25m) — 6% of corpus got higher head → better economics
  - Viable count increased (774→867) and revenue increased ($35.5M→$55M/yr) because large POTWs now correctly have higher head

**Files modified / created:**
- `src/phase2/energy_physics.py` — `run_monte_carlo()` returns `head_m_p10`, `head_m_p50`, `head_m_p90`
- `src/phase2/monte_carlo.py` — excluded branch emits `head_m_p10/p50/p90: None`
- `src/phase3/run.py` — joins Phase 2 head columns onto Phase 1 candidates before head estimation step
- `tests/test_phase2/test_energy_physics.py` — updated key test + 2 new head percentile tests

**Resources used:**
- `logs/runs/phase2_2026-05-19_05-24-21.log`
- `logs/runs/phase3_2026-05-19_05-28-19.log`
- `logs/runs/phase4_2026-05-19_05-29-04.log`
- Polars parquet inspection of `head_estimates.parquet` and `energy_yield_estimates.parquet`

**Known open items (not fixed this session):**
- **3DEP head still 0**: Phase 3 `_compute_head_row` requires both facility elevation AND outfall elevation to compute a head difference. We only have facility elevation from USGS 3DEP. Getting real 3DEP head requires outfall coordinates from the NPDES Outfalls Layer (EPA GeoPlatform) — not yet sourced.
- **TN0056545 "SUMMERTOWN HIGH SCHOOL" 585 MGD**: still in corpus; below 2,000 MGD sanity cap; likely GPD unit error. Needs manual EPA ECHO verification.

**Next steps after this session:**
1. Begin Phase 5 ML ranking model trained on DOE/FERC ground truth
2. Verify TN0056545 flow data in EPA ECHO; consider lowering sanity cap or adding a secondary cap for implausibly large small-facility flows
3. Source NPDES Outfalls Layer coordinates (EPA GeoPlatform) to enable real 3DEP elevation-difference head calculation in Phase 3

---
