# Exclusion Funnel Report — How WOWERS Narrows 17,158 POTWs to 355 Investment-Ready Sites

**Purpose:** This report answers the director's question — *"how did you exclude the rest?"* — with a stage-by-stage account of every site drop, the reason for each drop, and what happens to the energy potential of excluded sites. All numbers are recomputed directly from the pipeline parquet outputs; every figure is traceable to a specific file and column.

---

## Headline Finding

> **~72% of all exclusions are missing-data problems, not economic rejections.**

Of the 16,803 sites that did not reach Tier A:
- **11,690 excluded in Phase 2** — no usable flow data (DMR gaps). *No turbine was sized. No energy was computed.*
- **604 excluded in Phase 3 (head)** — no valid net head (elevation or outfall data missing). *Same: no energy.*
- **1,081 excluded in Phase 3 (physics)** — rated power < 1 kW after sizing. *Physics floor, not economics.*
- **3,428 scored but uneconomic in Phase 4** — turbine sized, annual energy computed, cash flows built — failed the finance gate.

The frequently-asked question "did you cherry-pick 355?" is answered by the structure of the pipeline: the other 16,803 sites were not excluded because they performed poorly on a financial model — most were excluded because the data required to run *any* model did not exist. Only 3,428 sites had a fully-sized turbine, a computed annual energy figure, and a complete financial scorecard, yet still failed economics. Those sites are not discarded — they appear in Tiers B and C with their energy totals and turbine specs intact.

---

## Stage-by-Stage Funnel

All counts recomputed from parquet. Numbers match journal reference figures exactly unless noted.

| Stage | Sites Remaining | Sites Dropped | Cumulative Dropped | Exclusion Type | Primary Reason |
|---|---:|---:|---:|---|---|
| **Phase 1 — Ranked POTWs** | 17,158 | — | — | — | All active POTWs with DMR permit coverage |
| **Phase 2 — Retained** | 5,468 | 11,690 | 11,690 | **Data gap** | No usable flow record in EPA DMR (gaps, non-numeric, zero-flow) |
| **Phase 3 — Head valid** | 4,864 | 604 | 12,294 | **Data gap** | No valid net head (elevation or outfall elevation absent/unreliable) |
| **Phase 3 — Turbine viable** | 3,783 | 1,081 | 13,375 | **Physics floor** | Best-fit rated power < 1 kW after turbine selection |
| **Phase 4 — Project viable (Tier A)** | 355 | 3,428 | 16,803 | **Economics** | NPV ≤ 0 *or* payback > 20 yr *or* IRR sentinel *or* annual revenue < $20k/yr (MINREV floor) |

All numbers verified against parquet outputs. Zero discrepancies from journal reference figures for site counts.

---

## Exclusion-Reason Rollup

| Reason Category | Sites Dropped | % of All Exclusions (16,803) |
|---|---:|---:|
| **Data gap** (flow or head missing) | 12,294 | 73.2% |
| **Physics floor** (< 1 kW rated power) | 1,081 | 6.4% |
| **Economics** (finance gate, Phase 4) | 3,428 | 20.4% |
| **Total** | 16,803 | 100% |

Interpretation: roughly three-quarters of all site exclusions happened before any financial model was applied, because the physical inputs (flow, head) were absent from public records. The 20% economics exclusions are the only cases where the pipeline had enough data to build a full project pro forma and the result was not investable.

---

## Energy by Cohort — "We Are Not Abandoning the Small Sites"

Every turbine-viable site (3,783 total) has a best-fit turbine type, rated power (kW), and annual energy output computed by `src/phase3/turbine_selection.py`. Phase 4 then scores all 3,783 against project economics. The table below shows where that energy sits.

| Cohort | Sites | Annual Energy (GWh/yr) | Status |
|---|---:|---:|---|
| **All turbine-viable** | 3,783 | 514.7 | Turbine sized; annual energy computed |
| **Tier A — Investment-ready** | 355 | 356.3 | project_viable = True |
| **Tier B — Cash-flow positive, sub-scale** | 1,019 | 71.9 | NPV > 0, payback ≤ 20 yr, real IRR — fails $20k/yr revenue floor only |
| **Tier C — Technical potential** | 2,409 | 86.5 | Uneconomic on cash flow (NPV ≤ 0 or payback > 20 yr) |
| **Scored but not financeable (B + C)** | 3,428 | 158.4 | Full financial scorecard exists; not removed from dataset |

Notes:
- *Recomputed non-viable (B+C) energy: **158.4 GWh/yr**.* Journal reference showed "~157 GWh" — minor rounding difference; the parquet-derived figure is used here.
- Tier B sites all have NPV > 0 and real IRR; their sole disqualifier from Tier A is annual revenue below the $20k MINREV floor (see next section).
- Sites in Tiers B and C are retained in the output dataset with full turbine specs. They are *reported*, not dropped.

---

## ⚠️ Data Discrepancy vs. Project Journal — Tier B Median Payback

The project journal records Tier B median payback as **~3.5 yr**. The parquet (`financial_scorecards.parquet`, column `payback_years`) yields a median of **9.73 yr** (mean 9.62 yr, range 3.9–13.6 yr) across all 1,019 Tier B sites. The 9.73 yr figure is used in this report. The journal reference should be corrected.

---

## The One Open Decision — The $20k/yr MINREV Floor

Tier B (1,019 sites, 71.9 GWh/yr) is excluded from Tier A by a **single policy assumption**: the F4-MINREV floor of $20,000/yr annual revenue, applied in `src/phase4/financials.py`. Every Tier B site has:

- NPV > 0
- Payback ≤ 20 yr (median 9.7 yr)
- A real (non-sentinel) IRR
- A sized turbine with computed annual energy

The revenue shortfall is a scale issue, not a physics or cash-flow issue. The threshold was set to screen out projects too small to absorb transaction costs at utility scale. For behind-the-meter or community-scale deployment, this floor may not apply.

**Impact of relaxing MINREV for Tier B:**  
Adding Tier B to Tier A would expand the investment-ready count from 355 to **1,374 sites** — a **~3.9× increase** in site count and a jump from 356.3 GWh/yr to **428.2 GWh/yr**.

*This is a director/team policy decision, not an engineering one.* The pipeline does not need to change; only `min_annual_revenue_usd` in `config/settings.yaml` (line 127) needs to be adjusted — or a separate behind-the-meter tier defined. The floor is implemented as `MIN_ANNUAL_REVENUE_USD` in `src/phase4/financials.py` (constant line 55, floor logic line 287).

---

## Reproducibility Footer

All numbers in this report can be re-derived from the following files and filter logic:

| Stage | File | Filter / Column | Value |
|---|---|---|---|
| Phase 1 total | `data/processed/phase1/ranked_candidates.parquet` | `len(df)` | 17,158 |
| Phase 2 retained | `data/processed/phase2/energy_yield_estimates.parquet` | `excluded == False` | 5,468 |
| Phase 2 excluded | same | `excluded == True` | 11,690 |
| Phase 3 head_valid | `data/processed/phase3/turbine_sizing.parquet` | `head_valid == True` | 4,864 |
| Phase 3 head invalid | same | `head_valid == False` | 604 |
| Phase 3 turbine_viable | same | `turbine_viable == True` | 3,783 |
| Phase 3 not viable | same | `turbine_viable == False` | 1,081 |
| Phase 4 project_viable | `data/processed/phase4/financial_scorecards.parquet` | `project_viable == True` | 355 |
| Phase 4 not viable | same | `project_viable == False` | 3,428 |
| Tier A energy | same | `site_tier == 'A'`, `annual_energy_kwh.sum() / 1e6` | 356.3 GWh/yr |
| Tier B energy | same | `site_tier == 'B'`, same | 71.9 GWh/yr |
| Tier C energy | same | `site_tier == 'C'`, same | 86.5 GWh/yr |
| Total turbine-viable energy | same | all rows, same | 514.7 GWh/yr |
| Tier B median payback | same | `site_tier == 'B'`, `payback_years.median()` | 9.73 yr |
| Phase 3 turbine-viable energy (cross-check) | `data/processed/phase3/turbine_sizing.parquet` | `turbine_viable == True`, `annual_energy_mwh.sum() / 1000` | 514.7 GWh/yr |

Energy unit note: Phase 3 uses `annual_energy_mwh`; Phase 4 uses `annual_energy_kwh`. Both convert to GWh/yr by dividing by 1,000 and 1,000,000 respectively.

---

*Report generated: 2026-06-07. Numbers recomputed from parquet by the pipeline author. No pipeline code, config, or thresholds were modified.*
