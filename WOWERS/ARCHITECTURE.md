# WOWERS Data Pipeline & Modeling System -- Complete Architecture

## Project Context

This system supports the WOWERS (Waste Outfall Water Energy Recovery System) business concept from the University of St. Thomas Fowler Business Concept Challenge. It predicts energy recovery potential from installing hydroelectric micro-turbines at US wastewater treatment plant outfalls.

---

## Implementation Status

| Phase | Status | Key Output | Notes |
|-------|--------|-----------|-------|
| Phase 1: Rank Candidates | **Complete** | `ranked_candidates.parquet` | 17,163 POTWs with flow features (post-cleanup). Four data-quality bugs diagnosed and fixed during Phase 2 spot-checks: (1) unit conversion — use `DMR_VALUE_STANDARD_UNITS`, not `DMR_VALUE_NMBR`; (2) ADC (Administratively Continued) permit status added to active whitelist — recovered 4,308 POTWs including real DC0021199 Blue Plains; (3) design-flow sanity bounds (null values > 2,000 MGD wet-weather peaks, < 0.005 MGD entry errors, and the 999.0 sentinel); (4) per-record flow cap at `max(2 MGD, 10 × design_flow)` nulls DMR unit errors before stats; (5) primary-outfall selection changed from max-mean to max-non-null-months to avoid single-row corruption winning. Validated: national mean ~2.0 MGD, median ~0.17 MGD, top 16 all well-known large POTWs (Warren CA, Hyperion, Passaic Valley, Wards Island, Stickney, Newtown Creek, Metro WWTP, Sacramento, Dallas Central, Hunt's Point, Nashville, North River, NEORSD Southerly, Bowery Bay, Owls Head, Akron). See `PHASE1_REPORT.md` §7 Issues 6–7 for full diagnoses. Pre-Phase-2 filter in `src/phase2/run.py` now excludes by `mean_flow_mgd ≤ 0` OR `(dmr_limited AND n_months_data < 3)`. |
| Phase 2: Energy Yield | **Complete** | `energy_yield_estimates.parquet` | 15,691 facilities estimated. National energy_p50 = 697 GWh/yr (within DOE 500–5,000 range). Head values are literature-assumed triangular distributions (large: Tri(3,8,15) m, medium: Tri(2,5,10) m, small: Tri(1,3,6) m) — Phase 3 replaces these with USGS 3DEP measurements. Two bugs fixed: `np.trapz` → `np.trapezoid` (NumPy 2.x), duplicate log lines from logging propagation. See `PHASE2_REPORT.md`. |
| Phase 3: Turbine Sizing | Not started | `turbine_sizing.parquet` | Requires USGS 3DEP elevation API |
| Phase 4: Financial Scorecard | Not started | `financial_scorecards.parquet` | Requires Phase 3 |
| Phase 5: ML Model | Not started | `model_predictions.parquet` | Requires labeled ground truth from DOE/FERC |

---

## Project Directory Structure

```
wowers/
|-- README.md
|-- pyproject.toml                    # Project metadata, dependencies
|-- config/
|   |-- settings.yaml                 # URLs, thresholds, constants
|   |-- logging.yaml                  # Logging configuration
|
|-- data/
|   |-- raw/                          # Untouched downloads (gitignored)
|   |   |-- npdes_downloads/          # Extracted from npdes_downloads.zip
|   |   |-- npdes_outfalls_layer/     # Extracted from npdes_outfalls_layer.zip
|   |   |-- dmr/                      # DMR files by fiscal year
|   |   |   |-- npdes_dmrs_fy2009/
|   |   |   |-- ...
|   |   |   |-- npdes_dmrs_fy2025/
|   |   |-- elevation_cache/          # Cached USGS 3DEP responses
|   |   |-- ground_truth/             # DOE HydroSource, FERC, case studies
|   |
|   |-- processed/                    # Phase outputs (parquet files)
|   |   |-- phase1/
|   |   |   |-- potw_facilities.parquet
|   |   |   |-- dmr_flow_timeseries.parquet
|   |   |   |-- flow_features.parquet
|   |   |   |-- ranked_candidates.parquet
|   |   |-- phase2/
|   |   |   |-- energy_yield_estimates.parquet
|   |   |-- phase3/
|   |   |   |-- elevation_data.parquet
|   |   |   |-- turbine_sizing.parquet
|   |   |-- phase4/
|   |   |   |-- financial_scorecards.parquet
|   |   |-- phase5/
|   |       |-- training_data.parquet
|   |       |-- model_predictions.parquet
|   |
|   |-- checkpoints/                  # DVC-tracked or manual versioning
|       |-- phase1_v001.parquet
|       |-- ...
|
|-- src/
|   |-- __init__.py
|   |-- common/
|   |   |-- __init__.py
|   |   |-- config.py                 # Load settings.yaml
|   |   |-- download.py               # Robust file downloader with retries
|   |   |-- io.py                     # Read/write parquet, checkpointing
|   |   |-- validation.py             # Schema validation with pandera
|   |   |-- logging_setup.py
|   |
|   |-- phase1/
|   |   |-- __init__.py
|   |   |-- ingest.py                 # Download + extract ECHO bulk files
|   |   |-- filter_potw.py            # Filter to POTWs only
|   |   |-- dmr_timeseries.py         # Parse DMR files, extract flow param 50050
|   |   |-- flow_features.py          # Compute statistical flow features
|   |   |-- ranking.py                # Composite ranking score
|   |   |-- run.py                    # Phase 1 orchestrator
|   |
|   |-- phase2/
|   |   |-- __init__.py
|   |   |-- head_assumptions.py       # Head ranges by facility type
|   |   |-- energy_physics.py         # P = eta * rho * g * Q * H
|   |   |-- monte_carlo.py            # Range-based energy estimation
|   |   |-- run.py
|   |
|   |-- phase3/
|   |   |-- __init__.py
|   |   |-- elevation.py              # USGS 3DEP point queries
|   |   |-- head_estimation.py        # Compute net head from elevation + plant data
|   |   |-- turbine_selection.py      # Match turbine type to flow/head regime
|   |   |-- sizing_optimizer.py       # Optimize rated capacity vs capacity factor
|   |   |-- run.py
|   |
|   |-- phase4/
|   |   |-- __init__.py
|   |   |-- cost_models.py            # CapEx/OpEx by turbine type and size
|   |   |-- revenue.py                # Electricity rate lookup, REC values
|   |   |-- financials.py             # NPV, IRR, payback
|   |   |-- sensitivity.py            # Tornado/spider sensitivity analysis
|   |   |-- run.py
|   |
|   |-- phase5/
|       |-- __init__.py
|       |-- ground_truth.py           # Ingest labeled data from DOE, FERC, etc.
|       |-- feature_engineering.py    # Combine features from phases 1-4
|       |-- train.py                  # Model training
|       |-- evaluate.py              # Cross-val, comparison to physics model
|       |-- run.py
|
|-- notebooks/
|   |-- 01_eda_echo_data.ipynb
|   |-- 02_flow_feature_exploration.ipynb
|   |-- 03_energy_yield_validation.ipynb
|   |-- 04_turbine_sizing_analysis.ipynb
|   |-- 05_financial_dashboard.ipynb
|   |-- 06_ml_model_analysis.ipynb
|
|-- tests/
|   |-- test_phase1/
|   |-- test_phase2/
|   |-- test_phase3/
|   |-- test_phase4/
|   |-- test_phase5/
|   |-- conftest.py                   # Shared fixtures, sample data
|
|-- scripts/
|   |-- run_pipeline.py               # End-to-end pipeline runner
|   |-- download_all_data.py          # Standalone data downloader
```

## Inter-Phase Storage Format Decision

**Parquet** is the correct choice for all inter-phase storage. Rationale:
- Columnar format, excellent for analytical queries on wide tables
- Native support for typed columns (float64, string, datetime, etc.)
- Compression (snappy by default) reduces the multi-GB DMR data to manageable sizes
- Direct read into pandas/polars DataFrames with zero schema ambiguity
- Supports partitioning (e.g., DMR data partitioned by fiscal year)

SQLite is unnecessary overhead for this batch pipeline. CSV is rejected because it loses type information and is slow for large files. Parquet files act as the "contract" between phases.

## Versioning/Checkpointing Strategy

Each phase's `run.py` writes output to `data/processed/phaseN/` and simultaneously copies to `data/checkpoints/phaseN_vXXX.parquet` with an auto-incrementing version number. A `manifest.json` in `data/checkpoints/` tracks which version of each phase was used to produce downstream results, creating a full lineage chain.

---

## PHASE 1: Rank Candidate Plants

### 1.1 Architecture

```
[EPA ECHO Bulk Downloads]
        |
        v
+-------------------+     +------------------------+
| npdes_downloads   | --> | ICIS_PERMITS.csv       |  (design flow, facility type)
| .zip (322 MB)     |     | ICIS_FACILITIES.csv    |  (name, location, coords)
+-------------------+     +------------------------+
                                    |
                          filter: FACILITY_TYPE_INDICATOR = 'POTW'
                                    |
                                    v
                          +-------------------+
                          | potw_facilities   |  (~16,000 rows)
                          | .parquet          |
                          +-------------------+
                                    |
+-------------------+               |
| npdes_dmrs_fy     |               |
| 2009..2025.zip    | ----+         |
| (~600MB x 16yr)  |     |         |
+-------------------+     v         |
                    filter: PARAMETER_CODE = '50050'
                    join on: EXTERNAL_PERMIT_NMBR
                          |         |
                          v         v
                  +---------------------------+
                  | dmr_flow_timeseries       |
                  | .parquet (partitioned     |
                  |  by fiscal_year)          |
                  +---------------------------+
                              |
                    compute flow features
                              |
                              v
                  +---------------------------+
                  | flow_features.parquet     |
                  +---------------------------+
                              |
                    composite ranking score
                              |
                              v
                  +---------------------------+
                  | ranked_candidates.parquet |
                  +---------------------------+
```

### 1.2 Data Requirements

**Source file 1: `npdes_downloads.zip`** (322 MB)
- URL: `https://echo.epa.gov/files/echodownloads/npdes_downloads.zip`
- Extract to get 11 CSV files. Needed files:
  - `ICIS_FACILITIES.csv` -- Fields: `NPDES_ID`, `FACILITY_UIN`, `FACILITY_TYPE_CODE`, `FACILITY_NAME`, `LOCATION_ADDRESS`, `CITY`, `STATE_CODE`, `ZIP`, `GEOCODE_LATITUDE`, `GEOCODE_LONGITUDE`
  - `ICIS_PERMITS.csv` -- Fields: `EXTERNAL_PERMIT_NMBR`, `FACILITY_TYPE_INDICATOR`, `TOTAL_DESIGN_FLOW_NMBR`, `ACTUAL_AVERAGE_FLOW_NMBR`, `MAJOR_MINOR_STATUS_FLAG`, `PERMIT_STATUS_CODE`, `EFFECTIVE_DATE`, `EXPIRATION_DATE`
- Join key: `NPDES_ID` = `EXTERNAL_PERMIT_NMBR`

**Source file 2: DMR files** (~9.6 GB total for FY2009-FY2025)
- URLs: `https://echo.epa.gov/files/echodownloads/npdes_dmrs_fy20XX.zip` for XX in 09..25
- Each ZIP contains a large CSV. Key fields (based on NPDES_EFF_VIOLATIONS schema which mirrors DMR structure):
  - `EXTERNAL_PERMIT_NMBR` -- join key to facilities
  - `PERM_FEATURE_NMBR` -- outfall identifier
  - `MONITORING_PERIOD_END_DATE` -- the reporting month
  - `PARAMETER_CODE` -- filter to `50050` (Flow, in MGD)
  - `PARAMETER_DESC` -- "Flow, in conduit or thru treatment plant"
  - `STATISTICAL_BASE_CODE` -- distinguishes average vs maximum vs minimum
  - `STATISTICAL_BASE_SHORT_DESC` -- human-readable (e.g., "MO AVG", "MO MAX")
  - `DMR_VALUE_STANDARD_UNITS` -- **preferred value field**: EPA pre-converts to standard units (always MGD for parameter 50050). Use this, not `DMR_VALUE_NMBR`.
  - `DMR_VALUE_NMBR` -- raw reported value in **whatever unit the facility chose** (gal/d, gal/min, Mgal/mo, etc.). Do NOT use this as a flow value in MGD without unit conversion -- doing so inflates values by 100,000x for gal/d facilities. Only fall back to this if `DMR_VALUE_STANDARD_UNITS` is absent.
  - `NODI_CODE` -- No Data Indicator (explains why value might be missing)
  - `LIMIT_VALUE_STANDARD_UNITS` -- permitted limit for comparison

### 1.3 Processing Logic

**Step 1: Download and extract**
```
download(url) -> save to data/raw/ -> extract ZIP -> validate expected CSVs exist
```
Use `requests` with streaming + retry (exponential backoff, 3 retries). Verify file integrity with size checks (npdes_downloads.zip should be ~322 MB). Do NOT re-download if file already exists and size matches.

**Step 2: Filter to POTWs**
```python
# Load ICIS_PERMITS.csv
# Filter: FACILITY_TYPE_INDICATOR contains 'POTW'
# Also keep: PERMIT_STATUS_CODE in ('EFF', 'NON') -- effective or non-major
# Drop: retired/terminated permits (RETIREMENT_DATE or TERMINATION_DATE is not null)
# Join with ICIS_FACILITIES.csv on NPDES_ID = EXTERNAL_PERMIT_NMBR
# Result: ~16,000 active POTW facilities
```

Important filtering details:
- `FACILITY_TYPE_INDICATOR` values to include: `'POTW'` (may also appear as `'POT'` in some records)
- Exclude `FACILITY_TYPE_CODE` = `'FDF'` (federal facilities -- these are not treatment plants)
- Keep both major (`MAJOR_MINOR_STATUS_FLAG = 'M'`) and minor facilities; minor plants may still have viable turbine potential

**Step 3: Parse DMR flow time series**

Process one fiscal year at a time to manage memory (each DMR file is ~600 MB uncompressed). Column names vary across fiscal years — use alias resolution to handle variants:

```
# Column aliases (first match wins):
npdes_id  : EXTERNAL_PERMIT_NMBR | NPDES_ID | PERMIT_ID
outfall   : PERM_FEATURE_NMBR | OUTFALL_CODE | FEATURE_NMBR
period_end: MONITORING_PERIOD_END_DATE | MONITORING_END_DATE | PERIOD_END_DATE
stat_base : STATISTICAL_BASE_SHORT_DESC | STAT_BASE_SHORT_DESC | STATISTICAL_BASE_CODE
value     : DMR_VALUE_STANDARD_UNITS | DMR_VALUE_NMBR | DMR_VALUE | REPORTED_VALUE
              ↑ CRITICAL: standard units MUST come first (already MGD for param 50050)
nodi      : NODI_CODE | NO_DATA_INDICATOR_CODE
```

```
For each fiscal year FY2009..FY2025:
  1. Read DMR CSV with chunked reader (chunksize=500_000)
  2. Filter rows: PARAMETER_CODE == '50050'
  3. Filter rows: EXTERNAL_PERMIT_NMBR is in potw_facilities.NPDES_ID
  4. Keep: EXTERNAL_PERMIT_NMBR, PERM_FEATURE_NMBR, MONITORING_PERIOD_END_DATE,
           STATISTICAL_BASE_SHORT_DESC, DMR_VALUE_STANDARD_UNITS (preferred) or
           DMR_VALUE_NMBR (fallback only), NODI_CODE
  5. Resolve value column — **prefer DMR_VALUE_STANDARD_UNITS** (already in MGD); only
     fall back to DMR_VALUE_NMBR if standard-units column is absent in a given file.
     After casting to float, null out any value > 2,000 MGD (physically impossible —
     the largest POTW in the US, Stickney/Chicago, peaks at ~1,440 MGD). Values above
     2,000 are data entry errors where a facility reported in gal/d but the wrong field
     was read.
  6. Pivot: separate columns for avg_flow, max_flow, min_flow based on STATISTICAL_BASE_SHORT_DESC
  7. **Primary outfall selection**: for facilities with multiple outfall codes, keep
     the outfall with (a) the most non-null monthly avg_flow records (non-storm/CSO
     outfalls preferred first), falling back to (b) highest mean as tiebreaker. This
     prevents double-counting across outfalls AND avoids the earlier "max-mean" bug
     where a single corrupted DMR row on a rarely-reported outfall (e.g., an STR/CSO
     storm outfall) beat dozens of clean rows on the real treatment outfall. See
     `src/phase1/flow_features.py::_select_primary_outfall`.
  8. Append to dmr_flow_timeseries.parquet (partitioned by fiscal_year)
  9. Final deduplication across all years: for the same (npdes_id, outfall, period_end),
     keep the row with a non-null avg_flow. This handles re-submissions and overlap
     between fiscal years.
```

NODI code handling: When `DMR_VALUE_NMBR` is null and `NODI_CODE` is present, interpret as:
- `C` = "Conditionally exempt" -- treat as 0 flow
- `B` = "Below detection" -- treat as 0 flow
- `Q` = "Quantity not sufficient" -- treat as missing
- `E` = "Estimated" -- keep value but flag as estimated
- All others -- treat as missing

**Step 4: Compute flow features per facility**

For each `EXTERNAL_PERMIT_NMBR`:
```
mean_flow         = mean(monthly_avg_flow)          # MGD
median_flow       = median(monthly_avg_flow)
std_flow          = std(monthly_avg_flow)
cv_flow           = std_flow / mean_flow             # coefficient of variation
p10_flow          = percentile(monthly_avg_flow, 10)
p25_flow          = percentile(monthly_avg_flow, 25)
p50_flow          = percentile(monthly_avg_flow, 50)
p75_flow          = percentile(monthly_avg_flow, 75)
p90_flow          = percentile(monthly_avg_flow, 90)
min_flow          = min(monthly_avg_flow)
max_flow          = max(monthly_avg_flow)
n_months          = count(non-null monthly records)
n_years           = count(distinct fiscal years with data)
pct_missing       = (expected_months - n_months) / expected_months
design_flow       = TOTAL_DESIGN_FLOW_NMBR           # from facility data
utilization_ratio = mean_flow / design_flow           # how fully loaded
flow_trend        = slope of linear regression on monthly_avg_flow vs time
seasonal_amplitude = (max of monthly means) - (min of monthly means) across calendar months
flow_duration_curve = array of [0.01, 0.05, 0.10, 0.20, ..., 0.95, 0.99] exceedance probabilities
```

Flow duration curve construction:
```
Sort all monthly_avg_flow values descending
For each value at rank i out of N total:
  exceedance_probability = i / (N + 1)
Store as 20-point interpolated curve at standard exceedance probabilities
```

**Step 5: Composite ranking score**

The ranking score identifies plants most suitable for turbine installation. It combines flow magnitude (bigger = more energy), flow consistency (steadier = better capacity factor), and data quality (more data = more confidence):

```
score = w1 * normalize(mean_flow)
      + w2 * normalize(1 - cv_flow)       # lower CV = steadier flow = better
      + w3 * normalize(utilization_ratio)  # higher utilization = consistent operation
      + w4 * normalize(n_years)            # data quality proxy
      + w5 * normalize(p10_flow)           # even the low-flow months matter

Default weights: w1=0.35, w2=0.20, w3=0.15, w4=0.10, w5=0.20
Normalization: min-max scaling to [0, 1] within the POTW population
```

Rationale for weights: Mean flow dominates because energy output scales linearly with flow. The 10th-percentile flow gets significant weight because a turbine's value proposition depends on reliable minimum flow (a plant with high mean but near-zero P10 has long idle periods). CV captures flow variability. The weights are configurable in `settings.yaml`.

### 1.4 Technology Choices

| Component | Library | Rationale |
|-----------|---------|-----------|
| Data download | `requests` + `tqdm` | Streaming download with progress bar |
| ZIP extraction | `zipfile` (stdlib) | Standard library, handles large files |
| CSV parsing | `polars` (preferred) or `pandas` | Polars is 5-10x faster for large CSVs and uses lazy evaluation; falls back to pandas chunked reader if needed |
| Statistical features | `numpy`, `scipy.stats` | Linear regression for trend, percentile calculations |
| Storage | `pyarrow.parquet` | Write partitioned parquet |
| Schema validation | `pandera` | Define expected schemas, catch data drift |
| Configuration | `pyyaml` | Simple YAML config |

### 1.5 Verification / Testing Plan

1. **Unit tests for POTW filter**: Create a 50-row synthetic ICIS_PERMITS.csv with known POTW/non-POTW mix. Assert filter returns exact expected count.
2. **Unit tests for DMR parsing**: Create a synthetic DMR CSV with known flow values for parameter code 50050 and other parameter codes. Assert only 50050 rows are retained, NODI codes handled correctly.
3. **Integration test -- known facility**: Pick 3 real NPDES permit numbers (e.g., a large POTW like `IL0028053` for Chicago MWRD). After full Phase 1 run, verify:
   - The facility appears in the ranked list
   - Its mean_flow is within 10% of publicly reported values
   - It has DMR records spanning multiple years
4. **Aggregate sanity checks** (validated against actual pipeline runs):
   - Total POTW count should be between 14,000 and 18,000 (CWNS reports 17,544 POTWs; not all have NPDES permits). **Observed: 12,855 facilities with DMR flow data.**
   - National mean flow across all POTWs: **~3.17 MGD**. National median: **~0.21 MGD** (reflects that the majority of the ~12,855 facilities are small/rural plants — expected and correct).
   - No negative flow values.
   - `utilization_ratio` should be between 0 and ~1.5 (some plants exceed design capacity temporarily).
   - Top-ranked facilities should correspond to well-known large POTWs. **Observed top plants:** Blue Plains AWTP (DC, ~3,339 MGD peak — largest WWTP in the world by design capacity), Hyperion WRP (LA, ~301 MGD), Stickney/Chicago MWRD (~1,440 MGD). If these facilities do not appear near the top of ranked_candidates, the unit conversion is wrong.
   - If mean flow is in the billions of MGD or thousands of MGD, `DMR_VALUE_NMBR` (raw units, often gal/d) was used instead of `DMR_VALUE_STANDARD_UNITS`. Fix by ensuring the column alias resolution picks up `DMR_VALUE_STANDARD_UNITS` first.
5. **Data completeness report**: Log how many POTWs have 0, 1-5, 5-10, 10+ years of DMR data. Expect >80% to have at least 5 years.

### 1.6 Output Schema

**`ranked_candidates.parquet`** -- one row per facility:

| Column | Type | Description |
|--------|------|-------------|
| npdes_id | string | NPDES permit number (primary key) |
| facility_name | string | Plant name |
| city | string | City |
| state_code | string | 2-letter state |
| zip | string | ZIP code |
| latitude | float64 | Facility latitude |
| longitude | float64 | Facility longitude |
| facility_type_indicator | string | POTW subtype |
| major_minor | string | Major (M) or minor facility |
| design_flow_mgd | float64 | Total design flow (MGD) |
| actual_avg_flow_mgd | float64 | Actual average flow from permit app |
| mean_flow_mgd | float64 | Mean of DMR monthly averages |
| median_flow_mgd | float64 | Median of DMR monthly averages |
| std_flow_mgd | float64 | Std dev of DMR monthly averages |
| cv_flow | float64 | Coefficient of variation |
| p10_flow_mgd | float64 | 10th percentile flow |
| p25_flow_mgd | float64 | 25th percentile flow |
| p75_flow_mgd | float64 | 75th percentile flow |
| p90_flow_mgd | float64 | 90th percentile flow |
| min_flow_mgd | float64 | Minimum observed monthly flow |
| max_flow_mgd | float64 | Maximum observed monthly flow |
| n_months_data | int32 | Number of months with flow data |
| n_years_data | int32 | Number of distinct fiscal years |
| pct_missing | float64 | Fraction of expected months missing |
| utilization_ratio | float64 | mean_flow / design_flow |
| flow_trend_mgd_per_year | float64 | Linear trend slope |
| seasonal_amplitude_mgd | float64 | Max monthly mean minus min monthly mean |
| flow_duration_curve | list[float64] | 20-point FDC at standard exceedance probabilities |
| ranking_score | float64 | Composite score [0, 1] |
| rank | int32 | Ordinal rank (1 = best candidate) |

### 1.7 Dependencies

None -- this is the entry point of the pipeline.

### 1.8 Known Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| DMR download takes 10+ hours on slow connection | Medium | Blocks entire pipeline | Download in parallel (4 concurrent); cache downloads; provide resume capability |
| DMR CSV schema changes between fiscal years | Medium | Parsing failures | Detect columns dynamically; log schema per file; map known column name variants |
| Some POTWs have no DMR flow records | High | Missing flow features for ~10-20% of plants | Assign flow features from design_flow when DMR is absent; flag `data_quality = 'design_only'` |
| Duplicate DMR records for same month | Medium | Inflated statistics | Deduplicate by (permit, outfall, month, stat_base); keep most recent submission |
| Memory issues with large DMR files | Medium | OOM crash | Use chunked reading (500K rows); process one fiscal year at a time; use polars lazy frames |
| DMR values reported in non-standard units (gal/d, gal/min, Mgal/mo instead of MGD) | **High** | 100,000x flow overestimation — national mean blows up to 4,000+ MGD | **Always prefer `DMR_VALUE_STANDARD_UNITS`** (EPA already converts to MGD); never use `DMR_VALUE_NMBR` as a direct MGD value. Apply hard cap at 2,000 MGD as a backstop for data entry errors. **This bug was discovered and fixed during Phase 1 runs.** |
| Double-counting flow from multiple outfalls per facility | Medium | Overestimated mean flow, distorted rankings | Select primary outfall by **max-non-null-months** (non-storm/CSO preferred first, mean as tiebreaker) per facility before computing flow features; do not sum across outfalls. **The earlier "max-mean" rule had a latent bug** where a single 208 MGD corrupted row on a rarely-used outfall beat 68 clean records on the real outfall — fixed April 2026. |
| Per-record DMR unit errors inflate facility-level flow features | **High** | Single DMR row at 7,000 MGD on a 0.02 MGD plant destroys the mean | Apply per-record cap at `max(2 MGD, 10 × design_flow_mgd)` in `flow_features._apply_design_flow_cap` BEFORE any statistics are computed. Rows above the cap are nulled (not dropped — they remain in the parquet for auditing but do not contribute to mean/std/FDC). When design_flow is null, a 50 MGD sentinel cap is used. **This bug was discovered during Phase 2 spot-checks and fixed April 2026.** |
| ADC (Administratively Continued) permit status omitted from active-POTW whitelist | **High** | Real large POTWs whose most-recent permit versions are ADC (not EFF) are silently dropped — cost 4,308 POTWs including real DC0021199 D.C. WASA (Blue Plains) | `potw_filter.active_permit_status_codes` now whitelists `EFF`, `NON`, and `ADC`. An ADC permit means the facility is still operating legally under its prior permit while EPA processes a timely renewal. **Discovered and fixed April 2026.** |
| ICIS design_flow field contains sentinel / wet-weather-peak / entry-error values | **High** | 999.0 sentinel treated as a real 999 MGD plant; 4,453 MGD DC CSO peak treated as a POTW design; 0.001 MGD entry error produces utilization_ratio = 1,500 | `filter_potw._filter_potw_permits` nulls design_flow when (a) value > 2,000 MGD, (b) value equals the 999.0 sentinel, or (c) value > 0 and < 0.005 MGD. Nulled rows fall to the bottom of the largest-design-flow-wins dedup and the facility falls through to the actual-avg / design-only fallback path. **Discovered and fixed April 2026.** |

---

## PHASE 2: Estimate Annual Energy Yield

### 2.1 Architecture

```
+---------------------------+     +---------------------------+
| ranked_candidates.parquet | --> | head_assumptions table    |
| (from Phase 1)            |     | (facility_type -> head    |
+---------------------------+     |  range in meters)         |
              |                   +---------------------------+
              |                               |
              v                               v
      +---------------------------------------+
      | Energy Physics Engine                 |
      | P = eta * rho * g * Q * H             |
      | Monte Carlo over head distribution    |
      +---------------------------------------+
                      |
                      v
      +---------------------------+
      | energy_yield_estimates    |
      | .parquet                  |
      +---------------------------+
```

### 2.2 Data Requirements

**From Phase 1**: `ranked_candidates.parquet` -- specifically: `npdes_id`, `mean_flow_mgd`, `p10_flow_mgd`, `p90_flow_mgd`, `flow_duration_curve`, `facility_type_indicator`, `design_flow_mgd`

**Head assumption table** (hardcoded in `head_assumptions.py`, sourced from literature):

| Facility Archetype | Typical Head Range (m) | Distribution | Source Rationale |
|---------------------|----------------------|--------------|------------------|
| Large POTW (>10 MGD), gravity outfall | 3 - 15 | Triangular(3, 8, 15) | Typical elevation difference between treatment tanks and receiving water body |
| Medium POTW (1-10 MGD), gravity outfall | 2 - 10 | Triangular(2, 5, 10) | Smaller plants, less elevation differential |
| Small POTW (<1 MGD), gravity outfall | 1 - 6 | Triangular(1, 3, 6) | Compact sites, limited head |
| PRV (Pressure Reducing Valve) location | 10 - 70 | Triangular(10, 30, 70) | Pressure drop in water distribution; highest energy potential |
| Pump station bypass | 5 - 30 | Triangular(5, 15, 30) | Head that would otherwise be dissipated by the pump |

Size classification uses `design_flow_mgd` from Phase 1.

### 2.3 Processing Logic

**Step 0: Pre-Phase-2 exclusion filter** (implemented in `src/phase2/run.py:load_candidates`)

Before any energy calculation, drop facilities that cannot produce a meaningful energy estimate:

```python
# Exclude if ANY condition holds:
mean_flow_mgd is null or <= 0                               # no usable flow signal
(data_quality == "dmr_limited") AND (n_months_data < 3)     # single-point artifact risk
```

Rationale:

1. **No usable flow** — facilities on the `design_only` or `actual_avg_only` fallback path can still end up with zero or null `mean_flow_mgd` when the permit has no `TOTAL_DESIGN_FLOW_NMBR` and no `ACTUAL_AVERAGE_FLOW_NMBR` on file (e.g., some KYP-prefix and decommissioned permits). Those cannot be sampled by Monte Carlo.
2. **Sparse DMR artifacts** — a facility with `data_quality = "dmr_limited"` and fewer than 3 surviving monthly records has CV collapsing to 0.0, a flat FDC, and a spuriously narrow Monte Carlo CI.

**Historical note:** The filter originally used `n_months_data < 3 AND design_flow_mgd == 999.0` to catch KYP000044 (Boyd County SD 4) and KYP000040 (Boyd & Greenup SD 1), which the old ranking placed at #4 and #5 with single-point DMR values of 243 and 273.6 MGD. After the April 2026 Phase 1 cleanup (see PHASE1_REPORT.md §7 Issues 6–7), those facilities are no longer a concern: (a) the 999.0 sentinel is nulled upstream in `filter_potw`, (b) their corrupt DMR rows are nulled by the per-record design-flow-relative cap in `flow_features`, and (c) they now fall onto the `actual_avg_only` fallback with rank > 14,000. The filter was rewritten to the current condition-form so it remains defensive against future single-point artifacts while not depending on the now-nulled 999.0 sentinel.

**Step 1: Classify each facility into an archetype**
```
if design_flow_mgd > 10:       archetype = 'large_potw_gravity'
elif design_flow_mgd > 1:      archetype = 'medium_potw_gravity'
else:                           archetype = 'small_potw_gravity'
```
Note: In Phase 2 we cannot distinguish PRV or pump-bypass sites without more data, so all POTWs are assigned gravity outfall archetypes. Phase 3 will refine this.

**Step 2: Monte Carlo energy estimation (N=10,000 iterations per plant)**

For each facility, for each Monte Carlo iteration:
```
1. Sample H from the archetype's triangular distribution
2. Sample eta (turbine efficiency) from Triangular(0.70, 0.82, 0.90)
3. For each of 20 flow duration curve points:
     Q_m3s = flow_mgd * 0.043813     # Convert MGD to m^3/s  (1 MGD = 0.043813 m^3/s)
     P_watts = eta * rho * g * Q_m3s * H
     where rho = 998.2 kg/m^3, g = 9.81 m/s^2
4. Integrate power over the flow duration curve to get annual energy:
     E_kwh_year = sum over FDC bins of (P_kw * hours_in_bin)
     where hours_in_bin = 8766 * (exceedance_width)
     # 8766 = average hours/year accounting for leap years
5. Apply availability factor: E_net = E_kwh_year * availability
     availability sampled from Triangular(0.90, 0.95, 0.98)
```

**Step 3: Aggregate Monte Carlo results**
```
energy_p10  = percentile(all_iterations, 10)   # conservative estimate
energy_p50  = percentile(all_iterations, 50)   # central estimate
energy_p90  = percentile(all_iterations, 90)   # optimistic estimate
energy_mean = mean(all_iterations)
energy_std  = std(all_iterations)
```

**Unit conversion constants** (store in `config/settings.yaml`):
```yaml
conversions:
  mgd_to_m3s: 0.043813          # 1 MGD = 0.043813 m^3/s
  m3s_to_mgd: 22.8245           # inverse
physics:
  rho_water: 998.2              # kg/m^3 at ~20C
  g: 9.81                       # m/s^2
  hours_per_year: 8766          # average including leap years
```

### 2.4 Technology Choices

| Component | Library | Rationale |
|-----------|---------|-----------|
| Monte Carlo sampling | `numpy.random` | Fast vectorized sampling; use `Generator` (not legacy `RandomState`) for reproducibility with seed |
| FDC integration | `numpy.trapz` | Trapezoidal integration over flow duration curve |
| Parallelization | `joblib` or `concurrent.futures` | Parallelize across facilities (not iterations); each facility's 10K iterations run as vectorized numpy |
| Storage | `pyarrow.parquet` | Consistent with Phase 1 |

Performance note: With vectorized numpy, 10,000 iterations per plant for 16,000 plants requires ~160M power calculations. At ~1 billion FLOPS on a laptop, this completes in under 60 seconds.

### 2.5 Verification / Testing Plan

1. **Hand-calculation test**: For a plant with constant flow of 10 MGD and head of exactly 10 m, eta=0.85:
   ```
   Q = 10 * 0.043813 = 0.43813 m^3/s
   P = 0.85 * 998.2 * 9.81 * 0.43813 * 10 = 36,492 W = 36.5 kW
   E = 36.5 * 8766 * 0.95 = 303,862 kWh/year
   ```
   Assert the model produces this exact value when distributions are replaced with point values.
2. **Dimensional analysis test**: Assert all energy outputs are in kWh/year, all power in kW. Assert no negative values.
3. **Monotonicity test**: Plants with higher mean flow should generally have higher energy_p50 (within same archetype). Test rank correlation > 0.95.
4. **Literature cross-check**: The DOE estimates ~4,000 MW potential from conduit hydropower in the US. Summing energy_p50 across all 16,000 POTWs should yield a number in the range of 500-5,000 GWh/year (since not all plants are candidates and POTWs are a subset of all conduit opportunities).
5. **Confidence interval width test**: For plants with low CV (steady flow), the P10-P90 range should be driven primarily by head uncertainty. For plants with high CV, flow variability should also contribute.

### 2.6 Output Schema

**`energy_yield_estimates.parquet`**:

| Column | Type | Description |
|--------|------|-------------|
| npdes_id | string | Primary key (from Phase 1) |
| archetype | string | Facility size/type classification |
| head_assumed_low_m | float64 | Low end of head range used |
| head_assumed_mode_m | float64 | Mode of head range used |
| head_assumed_high_m | float64 | High end of head range used |
| power_p50_kw | float64 | Median estimated power output (kW) |
| energy_p10_kwh_yr | float64 | 10th percentile annual energy (conservative) |
| energy_p50_kwh_yr | float64 | 50th percentile annual energy (central) |
| energy_p90_kwh_yr | float64 | 90th percentile annual energy (optimistic) |
| energy_mean_kwh_yr | float64 | Mean annual energy |
| energy_std_kwh_yr | float64 | Std dev of annual energy |
| capacity_factor_p50 | float64 | Median capacity factor (0-1) |
| equivalent_homes_p50 | int32 | energy_p50 / 10,500 (avg US household consumption) |

### 2.7 Dependencies

- **Phase 1 output**: `ranked_candidates.parquet` (for `npdes_id`, `mean_flow_mgd`, `flow_duration_curve`, `design_flow_mgd`, `facility_type_indicator`)

### 2.8 Known Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Head assumptions too wide, yielding unhelpful confidence intervals | High | Reduces decision value | Use literature-backed triangular distributions; clearly label as "screening estimate"; Phase 3 narrows this |
| Not distinguishing gravity outfall vs PRV sites | High | Underestimate for PRV, overestimate for gravity-only | Accept this limitation in Phase 2; flag it in output metadata; Phase 3 resolves |
| Flow duration curve has too few points (some plants have <24 months data) | Medium | Noisy FDC integration | For plants with <24 months, use mean_flow * 8766 * eta * rho * g * H_mode as a simpler estimate; flag as `fdc_quality = 'limited'` |
| Single-point DMR records with degenerate CV=0 inflate ranking and corrupt Monte Carlo | **Resolved** (Phase 1 cleanup, April 2026) | Previously: Monte Carlo CI spuriously narrow; facility ranked as perfectly consistent | The root cause is now handled upstream: (1) the per-record design-flow-relative cap in `flow_features._apply_design_flow_cap` nulls the corrupt multi-thousand-MGD DMR rows before aggregation, pushing former artifacts (KYP000044, KYP000040) onto the `actual_avg_only` fallback; (2) `filter_potw` nulls the 999.0 design-flow sentinel and values < 0.005 MGD. The Phase 2 filter remains as defensive insurance — it now excludes by `mean_flow_mgd ≤ 0` OR `(dmr_limited AND n_months_data < 3)` rather than depending on the (now always-null) 999.0 sentinel. See PHASE1_REPORT.md §7 Issues 6–7 and Phase 2 §2.3 Step 0. |

---

## PHASE 3: Optimize Turbine Sizing

### 3.1 Architecture

```
+---------------------------+     +---------------------------+
| ranked_candidates.parquet | --> |                           |
| (Phase 1)                 |     |  USGS 3DEP Elevation     |
+---------------------------+     |  Point Query Service      |
              |                   |  (per outfall lat/lon)    |
              |                   +---------------------------+
              |                               |
+---------------------------+                 |
| npdes_outfalls_layer.zip  | ---> outfall lat/lon ---> elevation query
| (50 MB)                   |                 |
+---------------------------+                 v
              |               +-------------------------------+
              |               | elevation_data.parquet        |
              |               | (facility_elev, outfall_elev, |
              |               |  net_head_m)                  |
              |               +-------------------------------+
              v                               |
+---------------------------+                 |
| energy_yield_estimates    |                 |
| .parquet (Phase 2)        | ----+          |
+---------------------------+     |          |
                                  v          v
                    +-------------------------------+
                    | Turbine Selection & Sizing    |
                    | - Type: Kaplan/Francis/Pelton/ |
                    |   in-conduit by flow/head      |
                    | - Rated kW from FDC optimization|
                    +-------------------------------+
                                  |
                                  v
                    +-------------------------------+
                    | turbine_sizing.parquet         |
                    +-------------------------------+
```

### 3.2 Data Requirements

**From Phase 1**: `ranked_candidates.parquet` -- `npdes_id`, `latitude`, `longitude`, `flow_duration_curve`, `mean_flow_mgd`, `design_flow_mgd`

**From Phase 2**: `energy_yield_estimates.parquet` -- `npdes_id`, `archetype`

**New source: Outfall locations**
- URL: `https://echo.epa.gov/files/echodownloads/npdes_outfalls_layer.zip` (46 MB)
- Contains: `NPDES_PERM_FEATURE_COORDS.csv`
- Fields needed: `EXTERNAL_PERMIT_NMBR`, `PERM_FEATURE_NMBR`, `LATITUDE_MEASURE`, `LONGITUDE_MEASURE`
- Join key: `EXTERNAL_PERMIT_NMBR` = `npdes_id`

**New source: USGS 3DEP Elevation Point Query Service**
- Endpoint: `https://epqs.nationalmap.gov/v1/json`
- Parameters: `x` (longitude), `y` (latitude), `wkid=4326`, `units=Meters`
- Response: JSON with `value` field containing elevation in meters
- Rate limit: No published limit, but be respectful -- use 2-second delay between requests or batch via concurrent requests with max 10 parallel
- Need TWO elevation queries per facility: (1) facility location, (2) outfall discharge point

### 3.3 Processing Logic

**Step 1: Load outfall coordinates**
```
Read NPDES_PERM_FEATURE_COORDS.csv
Filter to EXTERNAL_PERMIT_NMBR in Phase 1 POTW list
For facilities with multiple outfalls: keep the outfall with the largest
  flow (if DMR data distinguishes by PERM_FEATURE_NMBR) or keep the first outfall
```

**Step 2: Query elevations**
```
For each facility:
  facility_elev = query_3dep(facility_latitude, facility_longitude)
  outfall_elev  = query_3dep(outfall_latitude, outfall_longitude)
  gross_head_m  = facility_elev - outfall_elev  # positive if facility is uphill

If outfall coords = facility coords (same point):
  Use facility_elev only; estimate head from archetype assumptions (Phase 2)
  Flag: head_source = 'archetype_assumption'

If gross_head < 0:
  # Outfall is uphill from facility -- possible data error or pumped discharge
  Flag: head_source = 'negative_check_data'
  Use abs(gross_head) but flag for manual review

net_head_m = gross_head_m * head_loss_factor
  where head_loss_factor = 0.85  # 15% friction/minor losses in penstock
```

Cache all elevation queries to `data/raw/elevation_cache/` as a JSON keyed by `(lat, lon)` rounded to 5 decimal places. This avoids re-querying on reruns and reduces API calls from ~32,000 to whatever is needed on first run.

**Step 3: Turbine type selection**

Use the classic turbine selection chart logic based on net head and design flow:

```
Q_m3s = mean_flow_mgd * 0.043813
H = net_head_m

if H > 50 and Q_m3s < 2:
    turbine_type = 'Pelton'
elif H > 10 and H <= 50 and Q_m3s < 10:
    turbine_type = 'Francis'
elif H <= 10 and Q_m3s > 0.5:
    turbine_type = 'Kaplan'  # or propeller
elif H <= 10 and Q_m3s <= 0.5:
    turbine_type = 'in_conduit_micro'  # inline turbine, e.g., Lucid, Natel
else:
    turbine_type = 'Francis'  # default for medium conditions
```

Efficiency curves by type (as a function of fraction of rated flow):
```
Kaplan:    eta(q) = -0.3*q^2 + 0.6*q + 0.6   # peaks ~0.90 at q=1.0, stays >0.80 at q=0.4
Francis:   eta(q) = -0.5*q^2 + 0.9*q + 0.45   # peaks ~0.86 at q=0.9, drops below 0.70 at q=0.3
Pelton:    eta(q) = 0.88 for q > 0.2, else 0   # relatively flat efficiency
In-conduit: eta(q) = 0.75 * q for q < 0.5, else 0.75  # simpler curve
```

**Step 4: Optimize turbine rated capacity**

The goal is to find the rated flow `Q_rated` that maximizes annual energy output (or alternatively, maximizes capacity factor above a threshold like 0.40). This is NOT about maximizing peak power -- it is about maximizing total energy across the full flow duration curve.

```
For Q_rated in linspace(p90_flow, p10_flow, 50):  # search space
    annual_energy = 0
    For each FDC bin (Q_actual, hours_in_bin):
        if Q_actual >= Q_rated:
            Q_turbine = Q_rated           # spill excess
            q_fraction = 1.0
        else:
            Q_turbine = Q_actual
            q_fraction = Q_actual / Q_rated
        
        if q_fraction < 0.15:             # below minimum operating point
            Q_turbine = 0
            eta = 0
        else:
            eta = efficiency_curve(turbine_type, q_fraction)
        
        P = eta * rho * g * Q_turbine_m3s * net_head_m
        annual_energy += P * hours_in_bin / 1000  # kWh
    
    capacity_factor = annual_energy / (Q_rated_power * 8766)
    
    # Objective: maximize annual_energy subject to capacity_factor >= 0.40
    Store (Q_rated, annual_energy, capacity_factor, rated_power_kw)

Select the Q_rated that maximizes annual_energy while maintaining capacity_factor >= 0.40
If no solution meets CF >= 0.40, select Q_rated that maximizes CF
```

### 3.4 Technology Choices

| Component | Library | Rationale |
|-----------|---------|-----------|
| Elevation queries | `httpx` (async) | Async HTTP for parallel elevation queries; max 10 concurrent |
| Caching | `diskcache` or simple JSON files | Persist elevation lookups across runs |
| Optimization | `scipy.optimize.minimize_scalar` or grid search | The objective function is smooth enough for grid search over 50 points |
| Spatial data | `geopandas` (if outfall layer is shapefile) or `pandas` (if CSV) | Read outfall coordinates |

### 3.5 Verification / Testing Plan

1. **Elevation API smoke test**: Query 5 known locations (e.g., Denver CO = ~1609m, New Orleans LA = ~1m, NYC = ~10m). Assert values within 10m of known elevations.
2. **Head reasonableness check**: For all facilities, assert `net_head_m` is between -5 and 200 m. Flag any outliers for manual review. Expect 95% of POTWs to have net head between 1 and 30 m.
3. **Turbine type distribution check**: Expect the vast majority (>80%) of POTWs to be assigned Kaplan or in-conduit (low-head, moderate-to-high flow). Only a few percent should be Pelton (very rare for wastewater).
4. **Capacity factor validation**: For the optimized turbine, capacity factor should be between 0.30 and 0.85 for most plants. Mean across all plants should be approximately 0.45-0.65.
5. **Energy consistency check**: Phase 3 energy output (using real elevation-derived head) should correlate strongly with Phase 2 energy output (r > 0.70). Systematic differences indicate the Phase 2 head assumptions were biased in a specific direction.
6. **Known installation comparison**: If any existing turbine installations at POTWs can be identified (e.g., Deer Island WWTP in Boston, or the City of Boulder WWTP), compare modeled turbine type and size to the actual installation.

### 3.6 Output Schema

**`elevation_data.parquet`**:

| Column | Type | Description |
|--------|------|-------------|
| npdes_id | string | Primary key |
| facility_lat | float64 | Facility latitude |
| facility_lon | float64 | Facility longitude |
| facility_elev_m | float64 | Facility elevation (m) |
| outfall_lat | float64 | Outfall latitude |
| outfall_lon | float64 | Outfall longitude |
| outfall_elev_m | float64 | Outfall elevation (m) |
| gross_head_m | float64 | facility_elev - outfall_elev |
| net_head_m | float64 | gross_head * 0.85 |
| head_source | string | 'elevation_derived', 'archetype_assumption', 'negative_check_data' |

**`turbine_sizing.parquet`**:

| Column | Type | Description |
|--------|------|-------------|
| npdes_id | string | Primary key |
| net_head_m | float64 | Net head used for sizing |
| turbine_type | string | Kaplan, Francis, Pelton, in_conduit_micro |
| rated_flow_mgd | float64 | Optimal turbine rated flow |
| rated_flow_m3s | float64 | Same in m^3/s |
| rated_power_kw | float64 | Rated power at design point |
| annual_energy_kwh | float64 | Expected annual energy output |
| capacity_factor | float64 | Annual energy / (rated_power * 8766h) |
| min_operating_flow_mgd | float64 | Below this, turbine shuts off |
| spill_fraction | float64 | Fraction of time flow exceeds rated |
| efficiency_at_rated | float64 | Turbine efficiency at rated conditions |
| energy_vs_phase2_ratio | float64 | Phase 3 energy / Phase 2 energy_p50 |

### 3.7 Dependencies

- **Phase 1**: `ranked_candidates.parquet` (coordinates, flow data, FDC)
- **Phase 2**: `energy_yield_estimates.parquet` (archetype, for comparison)
- **External**: USGS 3DEP API availability, outfall coordinates file

### 3.8 Known Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| USGS 3DEP API downtime or rate limiting | Medium | Blocks elevation queries | Cache aggressively; implement exponential backoff; have fallback to SRTM 30m data via `elevation` PyPI package |
| Outfall coordinates missing for many POTWs | Medium | Cannot compute head from elevation | Fall back to facility coordinates only; if facility and outfall are the same point, use Phase 2 archetype head |
| 3DEP resolution insufficient in flat areas (1m DEM may show 0 head difference) | Medium | Underestimates or misses head potential | Apply a minimum head floor of 1m for any gravity-fed outfall; note that DEM captures terrain, not pipe invert elevations |
| Turbine selection oversimplified | Low | Sub-optimal type recommendation | This is a screening tool; note that final turbine selection requires site-specific engineering study |

---

## PHASE 4: Financial Scorecard / ROI

### 4.1 Architecture

```
+---------------------------+     +---------------------------+
| turbine_sizing.parquet    | --> |                           |
| (Phase 3)                 |     |  Cost Model Lookup        |
+---------------------------+     |  (CapEx, OpEx by type     |
              |                   |   and rated kW)           |
              |                   +---------------------------+
              |                               |
+---------------------------+                 |
| ranked_candidates.parquet |                 |
| (Phase 1 -- state_code   |                 |
|  for electricity rates)   |                 |
+---------------------------+                 |
              |                               |
              v                               v
      +---------------------------------------+
      | Financial Model Engine                |
      | - CapEx = f(turbine_type, rated_kW)   |
      | - OpEx = f(turbine_type, rated_kW)    |
      | - Revenue = energy * elec_rate        |
      | - NPV, IRR, payback                   |
      | - Sensitivity analysis                |
      +---------------------------------------+
                      |
                      v
      +---------------------------+
      | financial_scorecards      |
      | .parquet                  |
      +---------------------------+
```

### 4.2 Data Requirements

**From Phase 1**: `ranked_candidates.parquet` -- `npdes_id`, `state_code`

**From Phase 3**: `turbine_sizing.parquet` -- `npdes_id`, `turbine_type`, `rated_power_kw`, `annual_energy_kwh`, `net_head_m`, `capacity_factor`

**New data: Electricity rate by state**
- Source: EIA (US Energy Information Administration) average commercial/industrial electricity rates
- URL: `https://api.eia.gov/v2/electricity/retail-sales/data/` (requires free API key)
- Alternatively, hardcode a state lookup table from EIA published data (updated annually). For 2024, national average industrial rate is approximately $0.08/kWh; rates range from $0.04/kWh (Idaho) to $0.20/kWh (Hawaii).
- Store as a YAML or CSV lookup: `state_code -> industrial_rate_per_kwh`

**Cost model parameters** (from DOE and published literature on small/micro hydro):

CapEx (installed cost per kW, including civil works, equipment, grid connection):
```yaml
capex_per_kw:
  Kaplan:
    # Follows power law: CapEx/kW = A * (rated_kW)^B
    # Source: DOE Hydropower Vision, ORNL conduit hydropower studies
    A: 9500    # $/kW at 1 kW
    B: -0.35   # economies of scale exponent
    # Example: 100 kW -> 9500 * 100^(-0.35) = $2,126/kW
    # Example: 1000 kW -> 9500 * 1000^(-0.35) = $949/kW
    min_per_kw: 800
    max_per_kw: 10000
  Francis:
    A: 8500
    B: -0.32
    min_per_kw: 700
    max_per_kw: 9000
  Pelton:
    A: 7000
    B: -0.30
    min_per_kw: 600
    max_per_kw: 8000
  in_conduit_micro:
    A: 12000
    B: -0.25   # Less economies of scale for small units
    min_per_kw: 2000
    max_per_kw: 15000
```

OpEx (annual O&M as percentage of CapEx):
```yaml
opex_pct_of_capex:
  Kaplan: 0.025          # 2.5% of CapEx per year
  Francis: 0.020         # 2.0%
  Pelton: 0.015          # 1.5% (simpler, fewer moving parts)
  in_conduit_micro: 0.030  # 3.0% (more frequent maintenance)
```

Other financial parameters:
```yaml
financial:
  discount_rate: 0.06        # 6% real discount rate for municipal projects
  project_lifetime_years: 30  # typical hydro asset life
  inflation_rate: 0.02       # for nominal calculations
  degradation_rate: 0.002    # 0.2% annual output degradation
  rec_value_per_kwh: 0.01    # Renewable Energy Certificate value (conservative)
  federal_tax_credit: 0.30   # ITC for small hydro (if applicable -- POTWs are tax-exempt, so this may not apply; set to 0 for municipal)
  municipal_bond_rate: 0.04  # Alternative financing cost
```

### 4.3 Processing Logic

**Step 1: Compute CapEx**
```
capex_per_kw = max(min_per_kw, min(max_per_kw, A * rated_power_kw^B))
total_capex = capex_per_kw * rated_power_kw
```

**Step 2: Compute annual revenue and costs**
```
elec_rate = state_electricity_rates[state_code]
annual_revenue = annual_energy_kwh * (elec_rate + rec_value_per_kwh)
annual_opex = total_capex * opex_pct_of_capex[turbine_type]
annual_net_cash_flow_year1 = annual_revenue - annual_opex
```

**Step 3: NPV calculation (30-year DCF)**
```
For year t = 1 to 30:
    energy_t = annual_energy_kwh * (1 - degradation_rate)^(t-1)
    revenue_t = energy_t * (elec_rate + rec_value_per_kwh)  # assume real rates constant
    opex_t = annual_opex  # constant in real terms
    net_cf_t = revenue_t - opex_t
    pv_t = net_cf_t / (1 + discount_rate)^t

NPV = -total_capex + sum(pv_t for t=1..30)
```

**Step 4: IRR calculation**
```
Find rate r such that:
    -total_capex + sum(net_cf_t / (1+r)^t for t=1..30) = 0
Use scipy.optimize.brentq on the NPV function
```

**Step 5: Simple payback period**
```
cumulative = 0
For year t = 1 to 30:
    cumulative += net_cf_t
    if cumulative >= total_capex:
        payback = t + (total_capex - cumulative + net_cf_t) / net_cf_t  # interpolate
        break
If cumulative < total_capex after 30 years: payback = inf
```

**Step 6: Sensitivity analysis (per plant)**

Run the NPV calculation across a grid:
```
For head_factor in [0.5, 0.75, 1.0, 1.25, 1.5]:       # head uncertainty
  For flow_factor in [0.8, 0.9, 1.0, 1.1, 1.2]:         # flow uncertainty
    For rate_factor in [0.7, 0.85, 1.0, 1.15, 1.3]:      # electricity price uncertainty
      Compute NPV with adjusted inputs
      Store (head_factor, flow_factor, rate_factor, NPV)

# Identify: which variable has the largest impact on NPV?
# Compute tornado diagram values (hold all but one at base, vary one)
```

Store the tornado sensitivity as three pairs: `(npv_at_low_head, npv_at_high_head)`, `(npv_at_low_flow, npv_at_high_flow)`, `(npv_at_low_rate, npv_at_high_rate)`.

### 4.4 Technology Choices

| Component | Library | Rationale |
|-----------|---------|-----------|
| DCF / NPV | `numpy-financial` (`npf.npv`, `npf.irr`) | Purpose-built financial functions |
| IRR solver | `scipy.optimize.brentq` | More robust than `npf.irr` for edge cases |
| Sensitivity grid | `itertools.product` + vectorized numpy | Fast grid evaluation |
| Electricity rates | Static YAML lookup | Avoids EIA API dependency; update annually |

### 4.5 Verification / Testing Plan

1. **Hand-calculation test**: For a 100 kW Kaplan turbine in Minnesota (rate ~$0.09/kWh), CF=0.50:
   ```
   CapEx/kW = 9500 * 100^(-0.35) = $2,126/kW
   Total CapEx = $212,600
   Annual energy = 100 * 8766 * 0.50 = 438,300 kWh
   Annual revenue = 438,300 * ($0.09 + $0.01) = $43,830
   Annual OpEx = $212,600 * 0.025 = $5,315
   Net CF = $38,515/year
   Simple payback = $212,600 / $38,515 = 5.5 years
   ```
   Assert model produces values within 1% of hand calculation.
2. **NPV sign test**: Plants with payback < 15 years should have positive NPV at 6% discount rate. Assert this holds for 100% of such plants.
3. **IRR bounds test**: No plant should have IRR > 50% (unrealistic). If any do, the cost model or energy estimate is likely wrong.
4. **Sensitivity monotonicity**: NPV should increase monotonically with head, flow, and electricity rate. Assert this holds for all tornado values.
5. **Distribution check**: Across all 16,000 plants, expect:
   - ~20-30% to have positive NPV (these are the actionable candidates)
   - Median payback period of 8-15 years for positive-NPV plants
   - IRR distribution peaked around 5-15% for viable plants

### 4.6 Output Schema

**`financial_scorecards.parquet`**:

| Column | Type | Description |
|--------|------|-------------|
| npdes_id | string | Primary key |
| state_code | string | For rate lookup reference |
| turbine_type | string | From Phase 3 |
| rated_power_kw | float64 | From Phase 3 |
| annual_energy_kwh | float64 | From Phase 3 |
| capacity_factor | float64 | From Phase 3 |
| capex_per_kw | float64 | Installed cost per kW |
| total_capex_usd | float64 | Total capital cost |
| annual_opex_usd | float64 | Annual O&M cost |
| elec_rate_per_kwh | float64 | State electricity rate |
| annual_revenue_usd | float64 | Year-1 gross revenue |
| annual_net_cf_usd | float64 | Year-1 net cash flow |
| npv_usd | float64 | 30-year NPV at 6% discount rate |
| irr | float64 | Internal rate of return (decimal) |
| payback_years | float64 | Simple payback period |
| lcoe_per_kwh | float64 | Levelized cost of energy |
| sensitivity_head_npv_low | float64 | NPV at 50% head |
| sensitivity_head_npv_high | float64 | NPV at 150% head |
| sensitivity_flow_npv_low | float64 | NPV at 80% flow |
| sensitivity_flow_npv_high | float64 | NPV at 120% flow |
| sensitivity_rate_npv_low | float64 | NPV at 70% rate |
| sensitivity_rate_npv_high | float64 | NPV at 130% rate |
| dominant_sensitivity | string | Which variable most affects NPV |
| project_viable | bool | NPV > 0 and payback < 20 years |

### 4.7 Dependencies

- **Phase 1**: `ranked_candidates.parquet` (state_code)
- **Phase 3**: `turbine_sizing.parquet` (turbine specs, energy output)
- **External**: EIA electricity rate data (can be static lookup)

### 4.8 Known Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Cost model parameters outdated | Medium | CapEx estimates off by 20-40% | Source from DOE 2023/2024 reports; add update date to config; allow easy override |
| Municipal POTWs are tax-exempt, so ITC/PTC may not apply | High | Overestimate returns if tax credits included | Default `federal_tax_credit = 0` for municipal facilities; note this in output |
| Electricity rates vary within states (utility territory) | Medium | 10-20% rate error for some plants | State average is sufficient for screening; note in output metadata |
| Negative NPV plants may still be viable with grants/subsidies | Medium | Undercounts viable projects | Add a `npv_with_50pct_grant` column showing NPV if 50% of CapEx is covered |

---

## PHASE 5: Train ML Model

### 5.1 Architecture

```
+---------------------------+     +---------------------------+
| All Phase 1-4 outputs     | --> | Feature Engineering       |
| (16,000 plants x ~50      |     | (combine, normalize,      |
|  features each)            |     |  create interaction terms) |
+---------------------------+     +---------------------------+
              |                               |
+---------------------------+                 |
| Ground Truth Data         |                 |
| - DOE HydroSource DB      |                 |
| - FERC license filings    |                 |
| - State energy databases  |                 |
| - Published case studies  |                 |
+---------------------------+                 |
              |                               |
              v                               v
      +---------------------------------------+
      | Training Pipeline                     |
      | 1. Match ground truth to ECHO plants  |
      | 2. Create labeled dataset             |
      | 3. Train gradient boosted model       |
      | 4. Compare to physics-based estimate  |
      +---------------------------------------+
                      |
                      v
      +---------------------------+     +---------------------------+
      | trained model (joblib)    |     | model_predictions.parquet |
      +---------------------------+     +---------------------------+
```

### 5.2 Data Requirements

**From Phases 1-4**: All output parquet files, joined on `npdes_id`

**Ground truth sources** (new data to collect):

1. **DOE HydroSource Database**
   - URL: `https://hydrosource.ornl.gov/`
   - Contains: Existing and potential hydropower facilities, including conduit projects
   - Key fields: facility name, location, installed capacity (kW), annual generation (MWh), head (m), flow (cfs)
   - Matching strategy: Spatial join (lat/lon within 500m) AND fuzzy name matching

2. **FERC License/Exemption Database**
   - URL: `https://www.ferc.gov/industries-data/hydropower` (eLibrary search)
   - Contains: Licensed and exempted small hydro projects, including conduit exemptions
   - Key fields: project name, capacity, annual generation, location
   - Note: FERC conduit exemptions (18 CFR 4.30) are particularly relevant -- these are exactly the type of project WOWERS would install

3. **State energy databases**
   - Various state energy offices publish small hydro installation data
   - Example: California SGIP (Self-Generation Incentive Program), Colorado small hydro database
   - Manual collection required; likely 50-200 labeled examples

4. **Published case studies**
   - DOE Water Power Technologies Office reports
   - NREL technical reports on conduit hydropower
   - Academic papers on WWTP energy recovery
   - Expected yield: 20-50 additional labeled examples

**Estimated total labeled dataset size: 100-500 plants with known energy output**

### 5.3 Processing Logic

**Step 1: Assemble ground truth**
```
For each ground truth source:
    Load records
    Geocode if needed (most have lat/lon)
    Attempt match to ECHO plants:
        1. Exact match on NPDES permit number (if available)
        2. Spatial match: find nearest ECHO plant within 500m
        3. Fuzzy name match: Levenshtein distance on facility name
    
    For matched records, extract:
        actual_annual_energy_kwh (the label/target)
        actual_installed_kw (secondary label)
        actual_head_m (if reported)
        actual_flow_m3s (if reported)
    
    Store in ground_truth.parquet
```

**Step 2: Feature engineering**

Combine all features from phases 1-4 into a single feature matrix. Add derived features:

```
Features (approximately 60 total):
FROM PHASE 1 (flow features):
  mean_flow_mgd, median_flow_mgd, std_flow_mgd, cv_flow,
  p10_flow_mgd, p25_flow_mgd, p75_flow_mgd, p90_flow_mgd,
  min_flow_mgd, max_flow_mgd, design_flow_mgd, utilization_ratio,
  flow_trend_mgd_per_year, seasonal_amplitude_mgd, n_years_data,
  pct_missing, ranking_score

FROM PHASE 2 (energy physics):
  energy_p50_kwh_yr, energy_p10_kwh_yr, energy_p90_kwh_yr,
  power_p50_kw, capacity_factor_p50

FROM PHASE 3 (turbine sizing):
  net_head_m, turbine_type (one-hot encoded), rated_power_kw,
  annual_energy_kwh, capacity_factor, spill_fraction,
  facility_elev_m, outfall_elev_m, gross_head_m

FROM PHASE 4 (financials):
  total_capex_usd, annual_revenue_usd, npv_usd, irr,
  payback_years, elec_rate_per_kwh, lcoe_per_kwh

DERIVED INTERACTION FEATURES:
  flow_x_head = mean_flow_mgd * net_head_m
  power_density = rated_power_kw / design_flow_mgd  # kW per MGD
  revenue_per_kw = annual_revenue_usd / rated_power_kw
  
GEOGRAPHIC FEATURES:
  state_code (one-hot or target encoded)
  latitude, longitude (raw -- captures climate/geography)
  climate_zone (derived from lat/lon -- affects seasonal flow patterns)
```

**Step 3: Model training**

```
Algorithm: LightGBM (gradient boosted trees)
Rationale:
  - Handles mixed feature types (numeric + categorical)
  - Robust to missing values
  - Provides feature importance
  - Small dataset friendly (works with 100-500 examples)
  - Fast training

Target variable: log(actual_annual_energy_kwh)
  (log-transform because energy output spans several orders of magnitude)

Validation strategy:
  - Given small labeled dataset (100-500), use nested cross-validation:
    - Outer loop: 5-fold stratified by state_code (geographic diversity in each fold)
    - Inner loop: 3-fold for hyperparameter tuning
  
  - Stratification ensures no single state dominates any fold
  - NEVER put two plants from the same utility in different folds (group-aware splitting)

Hyperparameter search space:
  n_estimators: [50, 100, 200, 500]
  max_depth: [3, 5, 7]
  learning_rate: [0.01, 0.05, 0.1]
  min_child_samples: [5, 10, 20]  # important for small datasets
  reg_alpha: [0, 0.1, 1.0]
  reg_lambda: [0, 0.1, 1.0]
  subsample: [0.7, 0.8, 1.0]
  colsample_bytree: [0.6, 0.8, 1.0]
```

**Step 4: Model evaluation**

```
Metrics:
  - RMSE on log(energy) -- primary metric
  - MAPE (Mean Absolute Percentage Error) on raw energy -- interpretable metric
  - R^2 -- variance explained
  - Spearman rank correlation -- does the model rank plants correctly?

Comparison to physics-based estimate:
  For each ground truth plant:
    physics_error = |phase3_annual_energy - actual_annual_energy| / actual_annual_energy
    ml_error = |ml_predicted_energy - actual_annual_energy| / actual_annual_energy
  
  Paired t-test: is ml_error significantly lower than physics_error?
  
  If ML does NOT beat physics:
    The physics model is sufficient -- ML adds complexity without value
    This is a valid and informative outcome
```

**Step 5: Score all 16,000 plants**
```
Load trained model
Apply to full feature matrix (all plants, not just labeled ones)
Output: ml_predicted_energy_kwh for each plant
Compare to Phase 3 physics estimate -- identify plants where ML disagrees strongly
  (these may be cases where the physics model assumptions are wrong)
```

### 5.4 Technology Choices

| Component | Library | Rationale |
|-----------|---------|-----------|
| Model training | `lightgbm` | Best for small tabular datasets with mixed types |
| Hyperparameter tuning | `optuna` | Bayesian optimization, more efficient than grid search for small data |
| Cross-validation | `sklearn.model_selection.GroupKFold` | Group-aware splitting by utility |
| Feature importance | `shap` | SHAP values for interpretability -- critical for business case |
| Fuzzy matching | `rapidfuzz` | Fast Levenshtein/token-set-ratio matching for ground truth assembly |
| Geocoding/spatial match | `scipy.spatial.cKDTree` | Fast nearest-neighbor for lat/lon matching |
| Model serialization | `joblib` | Standard sklearn/lightgbm model persistence |

### 5.5 Verification / Testing Plan

1. **Ground truth assembly QA**: For each matched record, manually verify 10% (random sample). Matching accuracy should be >90%.
2. **Feature completeness**: Assert no feature has >50% missing values in the training set. Plants with >30% missing features should be excluded from training (but can still receive predictions via the model's native missing-value handling).
3. **Overfitting check**: Training RMSE and validation RMSE should be within 20% of each other. If training RMSE is much lower, the model is overfitting -- reduce complexity.
4. **Learning curve**: Plot validation error vs. training set size (by subsampling). Determine if more labeled data would substantially improve the model.
5. **SHAP value sanity check**: The top 5 most important features should include at least 2 of: `mean_flow_mgd`, `net_head_m`, `rated_power_kw`, `capacity_factor`. If unexpected features dominate, investigate for data leakage.
6. **Physics vs. ML comparison**: Report median and mean absolute percentage error for both approaches. If ML MAPE < 30% and Physics MAPE > 40%, the ML model provides genuine value.
7. **Residual analysis**: Plot ML residuals vs. key features. No systematic pattern should be visible. If residuals correlate with a feature, the model is underfit on that dimension.

### 5.6 Output Schema

**`training_data.parquet`**:

| Column | Type | Description |
|--------|------|-------------|
| npdes_id | string | Primary key |
| ground_truth_source | string | DOE, FERC, state, case_study |
| match_method | string | exact, spatial, fuzzy_name |
| match_confidence | float64 | 0-1 confidence in the match |
| actual_annual_energy_kwh | float64 | Ground truth energy output |
| actual_installed_kw | float64 | Ground truth capacity (if known) |
| actual_head_m | float64 | Ground truth head (if known) |
| [all ~60 features] | various | Full feature vector |

**`model_predictions.parquet`**:

| Column | Type | Description |
|--------|------|-------------|
| npdes_id | string | Primary key |
| ml_predicted_energy_kwh | float64 | ML model prediction |
| ml_prediction_lower_kwh | float64 | Prediction interval lower bound |
| ml_prediction_upper_kwh | float64 | Prediction interval upper bound |
| physics_energy_kwh | float64 | Phase 3 physics estimate |
| ml_vs_physics_ratio | float64 | ML / physics (1.0 = agreement) |
| ml_vs_physics_flag | string | 'agree', 'ml_higher', 'ml_lower' |
| shap_top1_feature | string | Most important feature for this prediction |
| shap_top1_value | float64 | SHAP contribution of top feature |
| shap_top2_feature | string | Second most important |
| shap_top2_value | float64 | Second SHAP contribution |

### 5.7 Dependencies

- **Phases 1-4**: All output files (complete feature set)
- **External**: Ground truth from DOE HydroSource, FERC, state databases, published literature
- **Human effort**: Ground truth assembly requires manual curation and verification; this is the bottleneck

### 5.8 Known Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Too few labeled examples (<100) | High | Model underfits, poor generalization | Use simpler model (Ridge/Lasso instead of LightGBM); lean on physics model; augment with synthetic data from physics model with added noise |
| Ground truth biased toward large/successful projects | High | Model biased toward optimistic predictions for small plants | Track and report the size distribution of labeled vs. unlabeled plants; re-weight training examples if needed |
| Feature leakage from Phase 3/4 outputs | Medium | Overly optimistic cross-validation results | Ensure no target-derived features (e.g., Phase 2 energy estimate is physics-based, not ground-truth-derived, so it is NOT leakage) |
| HydroSource/FERC data not readily matchable to ECHO permits | High | Small training set | Invest in manual matching for the largest/most impactful cases; accept that spatial matching will have noise |
| Model cannot learn head implicitly from labeled data | Medium | Poor accuracy | Head correlates with geography (elevation, terrain) and facility characteristics; if model struggles, add more geographic features (slope, watershed area, etc.) |

---

## Cross-Phase Concerns

### Missing Data Strategy (Applied Across All Phases)

| Data Gap | Frequency | Handling |
|----------|-----------|---------|
| No DMR flow records at all | ~10-15% of POTWs | Use `design_flow_mgd * 0.75` (assumed 75% utilization) as flow estimate; if `actual_avg_flow_mgd` is present, prefer that; set `data_quality = 'design_only'` or `'actual_avg_only'`; n_years_data = 0 reduces ranking score |
| DMR records but < 12 months | ~5% of POTWs | Compute features from available data; flag `data_quality = 'dmr_limited'`; FDC computed from available months |
| ≥ 12 months of DMR data | majority | Full feature set computed; `data_quality = 'dmr'` |
| No design_flow on permit | ~5-10% | Fallback order: actual_avg_flow → design_flow * 0.75 → null; utilization_ratio set to null when design_flow missing |
| No outfall coordinates | ~15-20% | Use facility coordinates for elevation query; assume net_head from archetype |
| No lat/lon at all | <2% | Geocode from address using Census geocoder; if address is also missing, drop plant |

### Error Handling Strategy

All phases implement a common error handling pattern:
```
try:
    process_plant(npdes_id)
except DataQualityError as e:
    log.warning(f"Plant {npdes_id}: {e}")
    plant_record['error_flag'] = str(e)
    plant_record['data_quality'] = 'degraded'
    # Continue to next plant -- never crash the full pipeline for one bad record
except ExternalAPIError as e:
    log.error(f"API failure for {npdes_id}: {e}")
    # Retry 3 times with exponential backoff
    # If still failing, use cached/fallback value
    # If no fallback available, mark plant as 'api_failure' and continue
```

### Python Dependencies (pyproject.toml)

```
Core: polars >= 0.20, pandas >= 2.0, pyarrow >= 14.0, numpy >= 1.26
Statistics: scipy >= 1.12
HTTP: httpx >= 0.27, requests >= 2.31, tqdm >= 4.66
Geospatial: geopandas >= 0.14 (optional, for outfall shapefile)
Financial: numpy-financial >= 1.0
ML: lightgbm >= 4.0, scikit-learn >= 1.4, optuna >= 3.5, shap >= 0.44
Matching: rapidfuzz >= 3.6
Validation: pandera >= 0.18
Config: pyyaml >= 6.0
Visualization (notebooks): matplotlib >= 3.8, seaborn >= 0.13, plotly >= 5.18
```

### Pipeline Execution Order

```
python scripts/run_pipeline.py --phases 1,2,3,4,5
  OR
python scripts/run_pipeline.py --phases 1    # Run one phase at a time

Each phase:
  1. Checks for required input files (from previous phases)
  2. Validates input schemas with pandera
  3. Runs processing
  4. Validates output schema
  5. Writes to data/processed/phaseN/
  6. Writes checkpoint to data/checkpoints/
  7. Logs summary statistics
```

---

### Critical Files for Implementation

- `/Users/mohamedayman/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/Fowler/Fowler/.claude/settings.local.json` -- already configured with EPA ECHO domain permissions for WebFetch
- `src/phase1/dmr_timeseries.py` (**implemented**) -- parses ~9.6 GB of DMR data across 16 fiscal years, filters to parameter code 50050, resolves column aliases across schema changes per fiscal year, applies NODI codes, caps at 2,000 MGD, deduplicates, and pivots statistical bases into avg/max/min columns. Key design decision: prefers `DMR_VALUE_STANDARD_UNITS` (EPA pre-converted to MGD) over `DMR_VALUE_NMBR` (raw reported units). **Note:** this module filters rows by the `potw_ids` set passed in from `filter_potw`, so any change to the POTW whitelist (e.g., the April 2026 ADC recovery) requires re-parsing the DMR ZIPs to pick up the newly-included facilities.
- `src/phase1/filter_potw.py` (**implemented**) -- loads ICIS_FACILITIES.csv and ICIS_PERMITS.csv, filters to active POTWs (status whitelist: `EFF`, `NON`, `ADC`), nulls design-flow values outside the plausibility band (`> 2000 MGD`, `== 999.0` sentinel, `> 0 AND < 0.005 MGD`) before deduplication so the largest-design-flow-wins dedup cannot pick a corrupted permit version, then deduplicates by keeping the highest-design-flow permit per NPDES ID, and drops facilities with no coordinates.
- `src/phase1/flow_features.py` (**implemented**) -- computes all statistical flow features per facility. Two critical pre-processing steps run BEFORE any aggregation: (1) `_apply_design_flow_cap` joins design_flow_mgd onto the timeseries and nulls any row where `avg_flow_mgd > max(2 MGD, 10 × design_flow_mgd)` — catches per-record DMR unit errors like small plants reporting 7,000 MGD; (2) `_select_primary_outfall` picks the outfall with the most non-null monthly records (non-storm/CSO preferred, mean as tiebreaker) — replaces the earlier max-mean rule which was vulnerable to a single corrupted row winning. After cleanup, per-facility features are computed (mean, std, CV, percentiles, FDC, seasonal amplitude, linear trend); facilities with no surviving DMR data fall back to `actual_avg_only` or `design_only` using permit-level fields.
- `src/phase1/ranking.py` (**implemented**) -- composite ranking score with configurable weights; min-max normalises each component, caps CV at 2.0 and utilization at 2.0 to prevent outliers from dominating.
- `src/phase2/energy_physics.py` (to be created) -- implements the core physics equation P = eta * rho * g * Q * H with Monte Carlo sampling and flow duration curve integration; this is the heart of the energy estimation
- `src/phase3/elevation.py` (to be created) -- manages the USGS 3DEP elevation API calls for ~32,000 lat/lon points with caching, rate limiting, and error handling; the quality of head estimation depends entirely on this component
- `config/settings.yaml` (to be created) -- central configuration file controlling all thresholds, weights, cost model parameters, physical constants, and API endpoints; every phase reads from this file, making it the single source of truth for all tunable parameters
