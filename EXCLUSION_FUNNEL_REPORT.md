# Exclusion Funnel Report — How WOWERS Narrows 17,158 POTWs to 1,141 Investment-Ready Sites

**Purpose:** This report answers the director's question — *"how did you exclude the rest?"* — with a stage-by-stage account of every site drop, the reason for each drop, and what happens to the energy potential of excluded sites. All numbers are recomputed directly from the pipeline parquet outputs; every figure is traceable to a specific file and column.

**Framing update (Jun 2026):** Two pipeline changes since the first version of this report supersede its old "355 viable / Tier A-B-C" framing:
1. **F4-MINREV-REMOVE (Jun 12):** the $20k/yr revenue floor was removed per director decision. Viability is now pure economics — `NPV>0 AND payback≤20yr AND real IRR`. Tier B (the old "MINREV-only kills" cohort) no longer exists — those sites are now investment-ready.
2. **F4-INSTALL (Jun 20):** an installation/labor cost line was added to CapEx (default **17.5%** of equipment cost, director's 15–20% midpoint), where previously installation was implicitly $0.

Current production headline at install = 17.5%: **1,141 investment-ready sites · 409.1 GWh/yr.**

---

## Headline Finding

> **~80% of all exclusions are missing-data problems, not economic rejections.**

Of the 16,017 sites that are not investment-ready:
- **11,690 excluded in Phase 2** — no usable flow data (DMR gaps). *No turbine was sized. No energy was computed.*
- **604 excluded in Phase 3 (head)** — no valid net head (elevation or outfall data missing). *Same: no energy.*
- **1,081 excluded in Phase 3 (physics)** — rated power < 1 kW after sizing. *Physics floor, not economics.*
- **2,642 scored but uneconomic in Phase 4** — turbine sized, annual energy computed, cash flows built — failed the finance gate.

The question "did you cherry-pick the viable sites?" is answered by the structure of the pipeline: most non-viable sites were not excluded because they performed poorly on a financial model — they were excluded because the data required to run *any* model did not exist. Only 2,642 sites had a fully-sized turbine, a computed annual energy figure, and a complete financial scorecard, yet still failed economics. Those sites are not discarded — they remain in the output with their energy totals and turbine specs intact, and are categorized by profitability (see the econ_cat gradient below).

---

## Stage-by-Stage Funnel

All counts recomputed from parquet.

| Stage | Sites Remaining | Sites Dropped | Cumulative Dropped | Exclusion Type | Primary Reason |
|---|---:|---:|---:|---|---|
| **Phase 1 — Ranked POTWs** | 17,158 | — | — | — | All active POTWs with DMR permit coverage |
| **Phase 2 — Retained** | 5,468 | 11,690 | 11,690 | **Data gap** | No usable flow record in EPA DMR (gaps, non-numeric, zero-flow) |
| **Phase 3 — Head valid** | 4,864 | 604 | 12,294 | **Data gap** | No valid net head (elevation or outfall elevation absent/unreliable) |
| **Phase 3 — Turbine viable** | 3,783 | 1,081 | 13,375 | **Physics floor** | Best-fit rated power < 1 kW after turbine selection |
| **Phase 4 — Project viable** | 1,141 | 2,642 | 16,017 | **Economics** | NPV ≤ 0 *or* payback > 20 yr *or* IRR not real (no revenue floor — removed Jun 12) |

The viability gate at install = 17.5%. The `min_annual_revenue_usd` floor is set to 0 (no-op, reversible lever retained in config).

---

## Exclusion-Reason Rollup

| Reason Category | Sites Dropped | % of All Exclusions (16,017) |
|---|---:|---:|
| **Data gap** (flow or head missing) | 12,294 | 76.8% |
| **Physics floor** (< 1 kW rated power) | 1,081 | 6.7% |
| **Economics** (finance gate, Phase 4) | 2,642 | 16.5% |
| **Total** | 16,017 | 100% |

Interpretation: more than three-quarters of all site exclusions happened before any financial model was applied, because the physical inputs (flow, head) were absent from public records. The 16.5% economics exclusions are the only cases where the pipeline had enough data to build a full project pro forma and the result was not investable.

---

## Energy by Cohort — "We Are Not Abandoning the Small Sites"

Every turbine-viable site (3,783 total) has a best-fit turbine type, rated power (kW), and annual energy output computed by `src/phase3/turbine_selection.py`. Phase 4 then scores all 3,783 against project economics. The table below shows where that energy sits.

| Cohort | Sites | Annual Energy (GWh/yr) | Status |
|---|---:|---:|---|
| **All turbine-viable** | 3,783 | 514.7 | Turbine sized; annual energy computed |
| **Investment-ready** (`project_viable`) | 1,141 | 409.1 | NPV>0, payback≤20yr, real IRR, at install 17.5% |
| **Scored but not financeable** | 2,642 | 105.6 | Full financial scorecard exists; not removed from dataset |

Sites that fail economics are retained in the output dataset with full turbine specs. They are *reported and categorized*, not dropped.

---

## Profit Gradient — econ_cat Categories (F4-ECON-CAT)

Rather than a single binary viable/not-viable cut, all 3,783 scored sites are independently categorized on three economic dimensions. Each is computed from the post-install (17.5%) scorecard. (Columns: `econ_cat_payback`, `econ_cat_npv`, `econ_cat_irr` in `financial_scorecards.parquet`.)

**Payback period** (`econ_cat_payback`)

| Band | Criteria | Sites | Energy (GWh/yr) |
|---|---|---:|---:|
| Excellent | ≤ 5 yr | 94 | 181.7 |
| Good | 5–10 yr | 507 | 153.3 |
| Marginal | 10–20 yr | 540 | 74.1 |
| Uneconomic | > 20 yr or not viable | 2,642 | 105.6 |

**Net present value** (`econ_cat_npv`)

| Band | Criteria | Sites | Energy (GWh/yr) |
|---|---|---:|---:|
| High | ≥ $500k | 103 | 241.1 |
| Medium | $100k–500k | 155 | 71.9 |
| Low | $0–100k | 883 | 96.2 |
| Negative | ≤ $0 | 2,642 | 105.6 |

**Internal rate of return** (`econ_cat_irr`, stored as fraction)

| Band | Criteria | Sites | Energy (GWh/yr) |
|---|---|---:|---:|
| Strong | ≥ 15% | 196 | 242.1 |
| Moderate | 8–15% | 578 | 120.3 |
| Weak | 0–8% | 2,181 | 139.1 |
| None | < 0 or non-real | 828 | 13.3 |

The three dimensions are intentionally independent and do not sum to the viable count the same way (e.g. IRR "weak" includes positive-IRR-but-negative-NPV sites). NPV-positive (1,141) equals `project_viable` in this run — every positive-NPV site also clears payback and real IRR.

---

## Portfolio Cost Structure (at install = 17.5%)

| CapEx component | $M | Notes |
|---|---:|---|
| Equipment | 181.6 | Power-law, vendor-band clamped (equipment-only) |
| Installation | 31.8 | = equipment × 0.175 (F4-INSTALL, mechanical labor only) |
| Interconnection | 82.8 | Tiered by rated power |
| Permitting | 57.3 | FERC conduit-NOI / abbreviated / full-NEPA tiers |
| **Total** | **353.5** | 4-component sum |

Vendor-band check (`capex_outside_vendor_band`) is on equipment $/kW only and remains **0 of 3,783** sites.

---

## The Open Lever — Installation %

Viability count is sensitive to the installation cost fraction. The director's committed value is pending (default **0.175**, midpoint of his stated 15–20%). The pipeline does not need to change to test other values — only `cost_model.installation_pct_of_equipment` in `config/settings.yaml` (line 76); set to 0.0 to recover the prior no-installation behavior.

**What-if band** (`scripts/install_cost_whatif.py`, read-only):

| install_pct | Viable sites | Viable GWh/yr |
|---:|---:|---:|
| 0% | 1,374 | 428.2 |
| 15% | 1,172 | 411.7 |
| **17.5%** (production) | **1,141** | **409.1** |
| 20% | 1,120 | 407.5 |

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
| Phase 3 not viable | same | `turbine_viable == False` | 1,685 |
| Phase 4 project_viable | `data/processed/phase4/financial_scorecards.parquet` | `project_viable == True` | 1,141 |
| Phase 4 not viable | same | `project_viable == False` | 2,642 |
| Viable energy | same | `project_viable == True`, `annual_energy_kwh.sum() / 1e6` | 409.1 GWh/yr |
| Total turbine-viable energy | same | all rows, same | 514.7 GWh/yr |
| Median payback (viable) | same | `project_viable == True`, `payback_years.median()` | 9.84 yr |
| Equipment CapEx | same | `equipment_capex_usd.sum() / 1e6` | $181.6M |
| Installation CapEx | same | `installation_capex_usd.sum() / 1e6` | $31.8M |
| What-if band | `scripts/install_cost_whatif.py` | read-only re-score at 0/15/17.5/20% | see table |

Energy unit note: Phase 3 uses `annual_energy_mwh`; Phase 4 uses `annual_energy_kwh`. Both convert to GWh/yr by dividing by 1,000 and 1,000,000 respectively.

---

*Report regenerated: 2026-06-21. Numbers recomputed from post-F4-INSTALL parquet. No pipeline code, config, or thresholds were modified by this report.*
