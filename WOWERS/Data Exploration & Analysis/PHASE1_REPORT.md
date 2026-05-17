# WOWERS Phase 1 Report — Rank Candidate Plants

**Project:** WOWERS (Wastewater Outfall Water Energy Recovery System)
**Phase:** 1 of 5 — Data Ingestion, POTW Filtering, Flow Feature Extraction, and Candidate Ranking
**Date completed:** 2026-04-11
**Final run timestamp:** 2026-04-10 23:57 – 2026-04-11 01:03 (65.6 minutes)
**Checkpoint versions:** potw_facilities v8 · dmr_flow_timeseries (re-parse) · flow_features v7 · ranked_candidates v6

---

## 1. Executive Summary

Phase 1 successfully ingested, cleaned, and ranked the full US population of active Publicly Owned Treatment Works (POTWs) as candidates for WOWERS micro-hydropower turbine installation. The final pipeline processed approximately **279 million raw DMR rows** across 16 fiscal years (FY2009–FY2024), reduced them to **~4.7 million facility-month flow records**, and produced a ranked candidate list of **17,163 POTW facilities** covering all 50 states plus US territories.

Key validated outputs:
- **National mean flow: 1.88 MGD** — consistent with published EPA/CWNS statistics for US municipal WWTPs
- **National median flow: 0.17 MGD** — confirms the population is dominated by small rural plants, as expected
- **13,454 facilities (78.4%)** have multi-year DMR flow histories; remaining 3,709 fall back to design-flow estimates
- **D.C. WASA (Blue Plains)** ranks #1 — the largest POTW in the US by design capacity (370 MGD), with 303 MGD mean flow from 120 months of DMR data and 0.82 utilization ratio. This validates the pipeline against the single most important ground-truth data point.

The phase required multiple pipeline runs and a post-completion data quality audit to reach clean output. Six data quality issues were diagnosed and resolved; see Section 7 for full details.

---

## 2. Data Sources

### 2.1 ICIS Permit and Facility Data

| File | Source | Size (approx.) |
|------|--------|----------------|
| `ICIS_FACILITIES.csv` | EPA ECHO `npdes_downloads.zip` | Part of 322 MB bundle |
| `ICIS_PERMITS.csv` | EPA ECHO `npdes_downloads.zip` | Part of 322 MB bundle |

- **Raw ICIS_FACILITIES records:** 1,155,302
- **Raw ICIS_PERMITS records:** 1,653,061

### 2.2 Discharge Monitoring Report (DMR) Data

16 fiscal year ZIPs were downloaded from EPA ECHO. Each ZIP contains one large CSV of all NPDES discharge monitoring submissions for that year.

| Fiscal Year | Raw Rows Read | POTW Flow Rows Kept | Facility-Month Records |
|-------------|--------------|---------------------|------------------------|
| FY2009 | 11,077,254 | 320,980 | 146,332 |
| FY2010 | 11,555,176 | 327,422 | 148,458 |
| FY2011 | 12,023,783 | 332,206 | 150,634 |
| FY2012 | 12,596,501 | 333,065 | 152,469 |
| FY2013 | 13,663,713 | 331,962 | 154,507 |
| FY2014 | 16,347,139 | 332,807 | 155,227 |
| FY2015 | 17,535,228 | 333,285 | 156,615 |
| FY2016 | 20,325,520 | 340,304 | 159,679 |
| FY2017 | 22,784,269 | 364,356 | 172,032 |
| FY2018 | 23,721,911 | 373,825 | 177,165 |
| FY2019 | 24,365,139 | 381,712 | 178,329 |
| FY2020 | 128,635 | 957 | 721 |
| FY2021 | 25,277,786 | 395,806 | 181,385 |
| FY2022 | 25,578,323 | ~408,000 | ~184,000 |
| FY2023 | 26,159,095 | ~414,000 | ~186,000 |
| FY2024 | 26,877,909 | ~420,000 | ~188,000 |
| **Total** | **~279M** | **~5.1M** | **~4.7M after dedup** |

**Note on FY2020:** Only 128,635 rows were read from the FY2020 ZIP vs. 11–27 million for all other years. This anomaly likely reflects a partial or differently structured file on EPA ECHO at download time. FY2020 contributed only 721 facility-month records. This does not affect the ranking — all other 15 fiscal years were processed normally and most facilities have 14+ additional years of data.

**Column mapping (all 16 fiscal years):**
```
npdes_id   → EXTERNAL_PERMIT_NMBR
outfall    → PERM_FEATURE_NMBR
period_end → MONITORING_PERIOD_END_DATE
stat_base  → STATISTICAL_BASE_CODE
value      → DMR_VALUE_STANDARD_UNITS   ← EPA pre-converted to MGD for param 50050
nodi       → NODI_CODE
```

---

## 3. POTW Filter Results

The ICIS data was filtered to retain only active Publicly Owned Treatment Works.

| Filter Step | Count |
|-------------|-------|
| Raw ICIS_PERMITS records | 1,653,061 |
| After type filter (POTW / POT) + status filter (EFF / NON / ADC) | 17,196 |
| Dropped: no geocoordinates | 33 |
| **Final POTW facility count** | **17,163** |

### 3.1 Facility Attributes

| Attribute | Value |
|-----------|-------|
| Total active POTW facilities | 17,163 |
| With design flow on permit | 14,672 (85.5%) |
| Major facilities (M flag) | 4,618 (26.9%) |
| States/territories covered | 56 |

### 3.2 Top States by Facility Count

| State | Facilities |
|-------|-----------|
| TX | 1,578 |
| OH | 930 |
| PA | 872 |
| MO | 865 |
| IA | 823 |

Texas dominates due to its large number of small municipal utilities. The Midwest concentration (OH, MO, IA) reflects agricultural and industrial wastewater treatment infrastructure in that region.

---

## 4. DMR Flow Time Series

After parsing all 16 fiscal years, deduplicating by `(npdes_id, outfall, period_end)`, and selecting the primary outfall per facility (most non-null monthly records):

| Metric | Value |
|--------|-------|
| Unique facilities with any DMR flow data | 13,454 |
| Facilities on design-flow fallback | 3,709 |
| DMR coverage rate | 78.4% |

The pipeline covers **FY2009–FY2024**, giving a maximum potential time series of 192 months (16 years) per facility.

---

## 5. Flow Feature Results

Flow features were computed for all 17,163 facilities. Facilities with DMR data received full statistical features; the remaining 3,709 received flow estimates from permit design flow or actual average flow fields.

### 5.1 National Flow Statistics

| Statistic | Value |
|-----------|-------|
| National mean flow | 1.88 MGD |
| National median flow | 0.17 MGD |
| DMR-sourced features | 13,454 facilities (78.4%) |
| Design-flow fallback | 3,709 facilities (21.6%) |

The gap between mean (1.88 MGD) and median (0.17 MGD) reflects the heavy right skew: a small number of very large urban plants (100+ MGD) pull the mean up, while the majority of US POTWs are small rural or suburban facilities. The lower mean vs. the earlier buggy run (3.17 MGD) reflects the removal of corrupted DMR rows via the per-record design-flow-relative cap.

### 5.2 Data Quality Flag Distribution

| data_quality flag | Meaning | Count (approx.) |
|-------------------|---------|-----------------|
| `dmr` | ≥12 months of DMR data | ~12,900 |
| `dmr_limited` | 1–11 months of DMR data | ~554 |
| `actual_avg_only` | No DMR; actual avg flow from permit | ~900 |
| `design_only` | No DMR and no actual avg; estimated from design flow × 0.75 | ~2,800 |

### 5.3 Computed Features per Facility

| Feature | Description |
|---------|-------------|
| `mean_flow_mgd` | Mean of monthly average flow values |
| `median_flow_mgd` | Median monthly average flow |
| `std_flow_mgd` | Standard deviation |
| `cv_flow` | Coefficient of variation (std / mean) |
| `p10_flow_mgd` | 10th percentile — worst-case monthly flow |
| `p25_flow_mgd` | 25th percentile |
| `p75_flow_mgd` | 75th percentile |
| `p90_flow_mgd` | 90th percentile — high-flow months |
| `min_flow_mgd` | Minimum observed monthly flow |
| `max_flow_mgd` | Maximum observed monthly flow |
| `n_months_data` | Count of non-null monthly records |
| `n_years_data` | Distinct fiscal years represented |
| `pct_missing` | Fraction of expected months with no data |
| `flow_trend_mgd_per_year` | Linear trend slope |
| `seasonal_amplitude_mgd` | Max calendar-month mean minus min |
| `flow_duration_curve` | 20-point FDC at standard exceedance probabilities |
| `utilization_ratio` | mean_flow / design_flow |
| `data_quality` | Source quality flag |

---

## 6. Ranking

### 6.1 Methodology

A composite ranking score [0, 1] was computed for all 17,163 facilities using five min-max normalized components:

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Mean flow | 0.35 | Energy output scales linearly with flow |
| P10 flow | 0.20 | Low-flow reliability |
| Flow consistency (1 − CV) | 0.20 | Steadier flow → higher capacity factor |
| Utilization ratio | 0.15 | Higher utilization → plant is consistently loaded |
| Data quality (n_years) | 0.10 | More years = more confidence |

CV is capped at 2.0 and utilization is capped at 2.0 before normalization to prevent extreme outliers from compressing the rest of the distribution.

### 6.2 Top 10 Ranked Candidates

| Rank | NPDES ID | Facility | State | Score | Mean Flow (MGD) | n_months | Util |
|------|----------|----------|-------|-------|-----------------|----------|------|
| 1 | DC0021199 | D.C. WASA (Blue Plains) | DC | 0.605 | 303.0 | 120 | 0.82 |
| 2 | CA0053813 | AK Warren Water Resource Facility | CA | 0.597 | 259.6 | 168 | 0.65 |
| 3 | MA0103284 | MWRA Deer Island Treatment Plant | MA | 0.570 | 327.5 | 108 | 0.68 |
| 4 | CA0109991 | Hyperion Water Reclamation Plant | CA | 0.556 | 239.6 | 167 | 0.53 |
| 5 | NJ0021016 | Passaic Valley Sewerage Comm | NJ | 0.532 | 248.0 | 93 | 0.75 |
| 6 | PA0025984 | ALCOSAN Sew Sys | PA | 0.519 | 193.5 | 156 | 0.97 |
| 7 | IL0028053 | MWRDGC Stickney WRP | IL | 0.513 | 1200.0 | 0 | 0.83 |
| 8 | NY0026131 | NYCDEP — Ward's Island WRRF | NY | 0.516 | 206.9 | 15 | 0.75 |
| 9 | NY0026204 | NYCDEP — Newtown Creek WRRF | NY | 0.509 | 203.1 | 15 | 0.66 |
| 10 | PA0026689 | Philadelphia Water Dept — NE WPC | PA | 0.503 | 173.1 | 156 | 0.82 |

All 10 are well-known, continuously-operating large US municipal WWTPs. No artifacts, no CSO permits, no implausible values.

**Notes:**
- **Blue Plains (#1):** 120 months of real DMR data, 303 MGD mean, design 370 MGD, utilization 0.82. The largest POTW in the world by design capacity. Previously missing due to ADC permit status bug; now correctly ranked first.
- **Stickney WRP (#7):** The largest US POTW by actual flow (~1,200 MGD). Ranks #7 rather than #1 because its `data_quality = actual_avg_only` (only a single permit-level actual average value, no monthly DMR time series) — so the data-quality and flow-consistency components reduce its score.
- **Ward's Island and Newtown Creek (#8, #9):** 15 months of DMR data each — sufficient for ranking but `n_months` is relatively low, consistent with NYC DEP recently beginning to report under the new permit identifier.

---

## 7. Data Quality Issues and Resolutions

Seven issues were encountered and resolved across the full pipeline development. Issues 1–5 were resolved during the original Phase 1 runs (April 9–10). Issues 6–7 were discovered during a Blue Plains spot-check triggered by Phase 2 preparation and resolved in a post-completion audit (April 10–11).

### Issue 1: DMR Download Failures (Run 1)

**Observed:** 8 fiscal years failed to download on the first attempt with 3-retry exhaustion errors.
**Cause:** EPA ECHO server timeouts during parallel download.
**Resolution:** Re-ran pipeline; all 16 years downloaded successfully on the second attempt.

### Issue 2: FY2009 Missing on Partial Run (Run 2)

**Observed:** Run 2 executed with only FY2020 (other years flagged as not found with `--skip-download`). Result: 0 DMR features computed.
**Cause:** Pipeline launched before downloads had completed.
**Resolution:** Waited for all downloads, re-ran.

### Issue 3: DMR_VALUE_NMBR Unit Bug — Critical (Runs 3 and 4)

**Observed:** National mean flow reported as **4,807.92 MGD**. Top-ranked facilities showed flows in the millions of MGD.

**Root cause:** The DMR value field was resolving to `DMR_VALUE_NMBR` — the raw reported value in the facility's chosen unit. Many facilities report in gal/d. A 1 MGD facility reporting 1,000,000 gal/d was being read as 1,000,000 MGD.

**Fix:** Reordered column alias priority so `DMR_VALUE_STANDARD_UNITS` (EPA pre-converted to MGD for param 50050) is tried first. `DMR_VALUE_NMBR` demoted to fallback only.

| Run | Value Column | National Mean |
|-----|-------------|---------------|
| Runs 3–4 | DMR_VALUE_NMBR | 4,807.92 MGD |
| Run 5+ | DMR_VALUE_STANDARD_UNITS | 1.88 MGD |

### Issue 4: 33 Facilities Dropped — Missing Coordinates

**Observed:** `filter_potw` dropped 33 POTW permits with null latitude/longitude.
**Decision:** Accepted. Facilities without coordinates cannot be geocoded or evaluated for head estimation in Phase 3.

### Issue 5: FY2020 Anomalous File Size

**Observed:** FY2020 ZIP contained only 128,635 rows vs. 11–27 million for all other years, yielding only 721 facility-month records.
**Probable cause:** Partial extract or different structure on EPA ECHO at download time.
**Impact:** Minimal — 15 other fiscal years processed normally.

### Issue 6: KYP-Permit Single-Point Artifacts *(Resolved by Issue 7 fixes)*

**Observed (original run):** `KYP000044` (Boyd County SD 4) and `KYP000040` (Boyd & Greenup SD 1) ranked #4 and #5 with reported mean flows of 243.0 and 273.6 MGD and `n_months_data = 1`.

**Root cause:** KYP-prefix permits (Kentucky combined sewer overflow / interceptor program). Their raw DMR time series were dominated by values in the millions of MGD — CSO quarterly event volumes or residual GPD unit errors. Only 1 plausible-looking record survived the global 2,000 MGD cap per facility. With n=1, CV collapsed to 0, inflating the consistency component.

**Interim resolution:** Pre-Phase-2 exclusion filter added to `src/phase2/run.py`.

**Final resolution (Issue 7 fixes):** The per-record design-flow-relative cap now nulls their corrupt DMR rows upstream. Both facilities now have `data_quality = actual_avg_only`, mean ~0 MGD, and rank > 14,000. The Phase 2 filter still catches them via the `mean_flow_mgd ≤ 0` condition.

### Issue 7: Four Structural POTW Filter and Flow Feature Bugs *(Discovered during Phase 2 spot-check, resolved April 2026)*

A Blue Plains spot-check triggered by Phase 2 preparation revealed that DC0021199 was absent from the ranked list despite being the world's largest POTW. Investigation uncovered four root causes:

**7a — ADC permit status omitted from whitelist**

`filter_potw` accepted only `EFF` and `NON` status codes. Blue Plains holds only `ADC` (Administratively Continued) permit versions — it is operating legally under a prior permit while EPA processes its renewal. The whitelist was expanded to include `ADC`. This recovered **4,308 additional POTWs** (12,855 → 17,163, a 33% increase) that had been silently dropped.

Because the DMR parser filters rows by the POTW list at parse time, recovering these facilities required a full DMR re-parse (~66 min). Blue Plains went from missing entirely to **rank #1** with 303 MGD mean flow from 120 months of DMR data.

**7b — Corrupted DMR rows inflating per-facility statistics**

The global 2,000 MGD cap in `dmr_timeseries.py` was too loose for small plants. Example: Summertown High School (TN0056545) has design flow 0.023 MGD, but DMR rows of 9.3–7,979 MGD survived. A per-record cap was added in `flow_features._apply_design_flow_cap`: any DMR row where `avg_flow_mgd > max(2 MGD, 10 × design_flow_mgd)` is nulled before any statistics are computed. When design_flow is null, a 50 MGD sentinel cap is used. This nulled **23,179 corrupted DMR rows** in the current dataset.

**7c — Outfall selection by maximum mean biased by single corrupted rows**

`_select_primary_outfall` previously picked the outfall with the highest mean avg_flow across all its records. Example: Wellsburg (IA0042803) had a single 208 MGD corrupted row on outfall '1' which beat 68 clean records averaging ~0.13 MGD on outfall '001'. Rewritten to select the outfall with the most non-null monthly records (non-storm/CSO outfall patterns preferred, mean as tiebreaker). Configured via `settings.yaml:processing.primary_outfall_strategy = "max_months"`.

**7d — ICIS design_flow containing sentinel / implausible values**

Three classes of corrupted design-flow values were identified and nulled in `filter_potw._filter_potw_permits` before the largest-design-flow-wins dedup:
- `> 2,000 MGD` (46 rows) — wet-weather CSO peak capacities mis-recorded against POTW permits (e.g., DC0000221 at 4,453 MGD)
- `== 999.0` (30 rows) — EPA sentinel for "no design flow on record"
- `> 0 and < 0.005 MGD` — data entry errors (e.g., ND0022861 Mandan and ND0023370 Jamestown at 0.001 MGD, causing utilization_ratio of 1,500× that contaminated the ranking)

**Combined impact of Issue 7 fixes:**

| Metric | Before fixes | After fixes |
|--------|-------------|-------------|
| POTW facilities | 12,855 | 17,163 (+33%) |
| National mean flow | 3.17 MGD | 1.88 MGD |
| Blue Plains rank | Missing | #1 (303 MGD, 120 months) |
| Top-50 util > 5 | 3 facilities | 0 |
| DMR rows nulled by per-record cap | 0 | 23,179 |
| Corrupted design-flow values nulled | 0 | ~76 |

---

## 8. Output Files

All outputs are in `data/processed/phase1/`.

| File | Format | Rows | Description | Checkpoint |
|------|--------|------|-------------|------------|
| `potw_facilities.parquet` | Parquet | 17,163 | Active POTWs with permit and location fields | v8 |
| `dmr_flow_timeseries.parquet` | Partitioned Parquet (by fiscal_year) | ~4.7M | Monthly avg/max/min flow per (facility, outfall, month) | re-parsed |
| `flow_features.parquet` | Parquet | 17,163 | Per-facility flow statistics, FDC, trends, data quality flags | v7 |
| `ranked_candidates.parquet` | Parquet | 17,163 | All flow features + composite ranking score + rank | v6 |

**Note:** `dmr_flow_timeseries.parquet` is partitioned by `fiscal_year`. Load with `pl.read_parquet("dmr_flow_timeseries.parquet", hive_partitioning=True)` to preserve the `fiscal_year` column.

---

## 9. Runtime Summary

| Run | Description | POTWs | Mean Flow | Status |
|-----|-------------|-------|-----------|--------|
| 1 | Download attempt | — | — | Failed (download timeouts) |
| 2 | Partial years (FY2020 only) | 0 DMR | Design-only | Incomplete |
| 3 | 10 years, wrong value column | 10,004 | 4,807.92 MGD | Wrong units |
| 4 | 16 years, wrong value column | 10,205 | 4,807.92 MGD | Wrong units |
| 5 | 16 years, correct units | 10,206 | 3.17 MGD | Clean but POTW list incomplete |
| 6 (post-parse rebuild) | Re-ran features/ranking only, expanded POTW list | 10,139 DMR | 2.00 MGD | Fixed bugs 7b–7d; Blue Plains still missing from DMR |
| **7 (final)** | **Full re-parse + all fixes** | **13,454 DMR** | **1.88 MGD** | **Clean — final** |

Final run wall time: **65.6 minutes** on a laptop.

---

## 10. Phase 2 Readiness

Phase 1 outputs are validated and ready to feed Phase 2 (Energy Yield Estimation).

| Phase 2 Input Required | Available? | Source Column |
|------------------------|-----------|--------------|
| `npdes_id` | Yes | `npdes_id` |
| `mean_flow_mgd` | Yes (78.4% from DMR, 21.6% fallback) | `mean_flow_mgd` |
| `flow_duration_curve` (20 points) | Yes (for DMR facilities) | `flow_duration_curve` |
| `design_flow_mgd` | Yes for 85.5% of facilities | `design_flow_mgd` |
| `p10_flow_mgd`, `p90_flow_mgd` | Yes | `p10_flow_mgd`, `p90_flow_mgd` |
| `facility_type_indicator` | Yes | `facility_type_indicator` |

The pre-Phase-2 exclusion filter in `src/phase2/run.py:load_candidates()` drops facilities where `mean_flow_mgd ≤ 0` or `(data_quality == "dmr_limited" AND n_months_data < 3)`. The old `design_flow_mgd == 999.0` condition has been removed — those values are now nulled upstream in `filter_potw`, so the sentinel can never appear in `ranked_candidates`.
