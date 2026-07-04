# FERC Conduit Label Hunt — Review Prompt (corrected after round-1 review)

**To: Reviewing agent (fresh session, repo + SANDISK access)**
**Re: FERC Conduit-Scale Label Hunt + Phase 5 Go/No-Go Gate**
**Branch:** `tom`
**Note: WOWERS_PROJECT_JOURNAL.md must NOT be written until this review passes.**

---

## 1. What Was Built

| Artifact | Location | Purpose |
|---|---|---|
| `FERC_CONDUIT_LABEL_REPORT.md` | repo root | Findings report — sources searched, corrected usable-site count, gate outcome, FERC verdict |
| `FERC_REVIEW_PROMPT.md` | repo root | This file |
| `ferc_conduit_candidates_2026-07-04.csv` | `/Volumes/SANDISK/WOWERS_Pivot_Data/Phase5_ML_GroundTruth/FERC_Conduit/` | 115-row candidate table |
| `ferc_active_conduit_exemptions_2025-04-08.xlsx` | same SANDISK dir | FERC conduit exemptions source (222 active) |
| `ferc_active_licenses_2025-04-08.xlsx` | same SANDISK dir | FERC active licenses source (1,016) |
| `ferc_conduit_candidates.parquet` | `data/raw/ground_truth/` | Same in polars parquet (gitignored path) |

No Phase 1–4 source code or parquets modified. `.gitignore` has one additive change (`.gstack/` added by browse skill preamble). Journal not written.

---

## 2. Gate Arithmetic — Corrected

| Metric | Value |
|---|---|
| Gate threshold | ≥ 50 genuinely new usable sites |
| Conduit sites with capacity + measured generation (any scale) | 115 |
| Already in Jun-30 combined_ground_truth (by EIA_PtID) | 103 |
| **Genuinely new sites** | **11** |
| Gate result | **FAILS (11 < 50)** |
| Phase 5 recommendation | **Decision unchanged** — full Phase 5 ML not worth training as product |

---

## 3. Verification Commands

```bash
cd "/Users/tomsmacbookpro/Desktop/Temp/WOWERS /wowers"

# === A. Core numbers ===
/opt/miniconda3/bin/python -c "
import polars as pl
plant = pl.read_excel(
    '/Volumes/SANDISK/WOWERS_Pivot_Data/Phase5_ML_GroundTruth/EHA_HydroSource_ORNL/ORNL_EHAHydroPlant_PublicFY2024.xlsx',
    sheet_name='Operational', read_options={'header_row': 0})
cf = pl.read_excel(
    '/Volumes/SANDISK/WOWERS_Pivot_Data/Phase5_ML_GroundTruth/EHA_HydroSource_ORNL/EHA_Annual_CapacityFactor.xlsx',
    sheet_name='AnnualCapacityFactor', read_options={'header_row': 0})
conduit = plant.filter(pl.col('Mode') == 'Canal/Conduit')
cf_latest = (cf.filter((pl.col('Type')=='HY') & (pl.col('Net_Generation_MWh')>0))
               .sort('Year', descending=True)
               .unique(subset=['EHA_PtID'], keep='first'))
result = (conduit
    .join(cf_latest.select(['EHA_PtID','Net_Generation_MWh','Capacity_MW','Year']),
          on='EHA_PtID', how='inner')
    .filter(pl.col('Net_Generation_MWh') > 0))
combined = pl.read_parquet('data/raw/ground_truth/combined_ground_truth.parquet')
conduit_eia = plant.filter(pl.col('Mode')=='Canal/Conduit').select(['EHA_PtID','EIA_PtID'])
result_eia = result.join(conduit_eia, on='EHA_PtID', how='left')
new_codes = set(result_eia.filter(pl.col('EIA_PtID').is_not_null())['EIA_PtID'].cast(pl.Int64).to_list())
old_codes = set(combined['source_plant_code'].drop_nulls().to_list())
print(f'Any-scale: {result.height}')
print(f'<=5 MW (Capacity_MW): {result.filter(pl.col(\"Capacity_MW\")<=5).height}')
print(f'Already in combined: {len(new_codes & old_codes)}')
print(f'Genuinely new: {len(new_codes - old_codes)}')
"
# Expected: Any-scale: 115; <=5 MW: 80; Already in combined: 103; Genuinely new: 11

# === B. Point Loma offline check ===
/opt/miniconda3/bin/python -c "
import polars as pl
cf = pl.read_excel(
    '/Volumes/SANDISK/WOWERS_Pivot_Data/Phase5_ML_GroundTruth/EHA_HydroSource_ORNL/EHA_Annual_CapacityFactor.xlsx',
    sheet_name='AnnualCapacityFactor', read_options={'header_row': 0})
pl_gen = cf.filter((pl.col('EHA_PtID')=='hc2003_p01') & (pl.col('Type')=='HY')).sort('Year')
print('Point Loma (hc2003_p01) generation by year:')
print(pl_gen.select(['Year','Net_Generation_MWh']))
print('2022 value:', cf.filter((pl.col('EHA_PtID')=='hc2003_p01') & (pl.col('Year')==2022))['Net_Generation_MWh'].to_list())
print('Latest nonzero year:', cf.filter((pl.col('EHA_PtID')=='hc2003_p01') & (pl.col('Net_Generation_MWh')>0)).sort('Year', descending=True)['Year'][0])
"
# Expected: 2022 value: [0.0]; latest nonzero year: 2017; plant offline 2018-2022

# === C. WWTP type breakdown ===
/opt/miniconda3/bin/python -c "
import polars as pl
plant = pl.read_excel(
    '/Volumes/SANDISK/WOWERS_Pivot_Data/Phase5_ML_GroundTruth/EHA_HydroSource_ORNL/ORNL_EHAHydroPlant_PublicFY2024.xlsx',
    sheet_name='Operational', read_options={'header_row': 0})
cf = pl.read_excel(
    '/Volumes/SANDISK/WOWERS_Pivot_Data/Phase5_ML_GroundTruth/EHA_HydroSource_ORNL/EHA_Annual_CapacityFactor.xlsx',
    sheet_name='AnnualCapacityFactor', read_options={'header_row': 0})
conduit = plant.filter(pl.col('Mode') == 'Canal/Conduit')
cf_latest = (cf.filter((pl.col('Type')=='HY') & (pl.col('Net_Generation_MWh')>0))
               .sort('Year', descending=True).unique(subset=['EHA_PtID'], keep='first'))
result = conduit.join(cf_latest.select(['EHA_PtID','Net_Generation_MWh','Capacity_MW','Year']),
                       on='EHA_PtID', how='inner').filter(pl.col('Net_Generation_MWh')>0)
ww = result.filter(pl.col('Water').str.contains('(?i)waste water|wastewater|treated waste', literal=False))
mu = result.filter(pl.col('Water').str.contains('(?i)municipality|municipal', literal=False))
print(f'True wastewater: {ww.height} (should be 1 — Point Loma, offline)')
print(f'Municipal drinking water: {mu.height} (should be 3)')
print(f'Neither (irrigation canal): {result.height - ww.height - mu.height}')
"
# Expected: wastewater: 1; municipal: 3; irrigation canal: 111

# === D. FERC has no generation data ===
/opt/miniconda3/bin/python -c "
import polars as pl
ex = pl.read_excel(
    '/Volumes/SANDISK/WOWERS_Pivot_Data/Phase5_ML_GroundTruth/FERC_Conduit/ferc_active_conduit_exemptions_2025-04-08.xlsx',
    sheet_name='ActiveExemption_4.8.2025', read_options={'header_row': 2})
conduit_ex = ex.filter(pl.col('Description') == 'Conduit Exemption')
print(f'FERC conduit exemptions: {conduit_ex.height}')
print(f'Columns: {conduit_ex.columns}')
has_gen = any(k in c.lower() for c in conduit_ex.columns for k in ('generation','energy','kwh','mwh'))
print(f'Any generation/energy column: {has_gen}')
"
# Expected: 222 conduit exemptions; no generation column

# === E. Scope integrity ===
git diff HEAD -- src/phase1 src/phase2 src/phase3 src/phase4 config/settings.yaml src/phase5/ground_truth.py
# Expected: empty output (no Phase 1-4 changes)

git diff HEAD -- WOWERS_PROJECT_JOURNAL.md
# Expected: empty output (journal untouched)

git status --short | grep -v "WOWERS_Director_Deepdive\|frontend\|\.gstack"
# Expected: M .gitignore (additive only — adds .gstack/)
#           ?? FERC_CONDUIT_LABEL_REPORT.md
#           ?? FERC_REVIEW_PROMPT.md
#           (ferc_conduit_candidates.parquet is in gitignored data/ dir)

# === F. Test suite ===
/opt/miniconda3/bin/python -m pytest -q --tb=no
# Expected: 532 passed, 1 skipped
```

---

## 4. Expected Numbers

| Check | Expected |
|---|---|
| Canal/Conduit plants in EHA | 338 |
| With measured generation (any scale) | 115 |
| ≤ 5 MW | **80** |
| ≤ 1 MW | 6 |
| Already in Jun-30 combined (by EIA_PtID) | 103 |
| **Genuinely new** | **11** |
| Point Loma 2022 MWh | **0** (offline) |
| Point Loma latest nonzero year | 2017 |
| True wastewater plants (not drinking water) | 1 (offline) |
| FERC conduit exemptions | 222 |
| FERC measured generation columns | 0 |
| Gate result (≥50 new) | **FAILS** |
| Phase 5 recommendation | Decision unchanged |
| Test suite | 532 passed / 1 skipped |

---

## 5. Scope-Integrity Checklist

- [ ] `git diff HEAD -- src/phase1 src/phase2 src/phase3 src/phase4` is empty
- [ ] `git diff HEAD -- WOWERS_PROJECT_JOURNAL.md` is empty
- [ ] `.gitignore` change is additive-only (adds `.gstack/`; no other modifications)
- [ ] `ferc_conduit_candidates.parquet` is in `data/raw/ground_truth/` (gitignored, not tracked)
- [ ] FERC source files are on SANDISK, not in repo
- [ ] Point Loma 2022 generation = 0 MWh confirmed
- [ ] Genuinely new count = 11 (not 115)
- [ ] Gate fails (11 < 50)
- [ ] Test suite: 532 passed / 1 skipped

---

## 6. Key Judgment Calls

1. **"New" defined as not in Jun-30 combined_ground_truth by EIA_PtID.** The combined parquet has 1,360 plants from EIA + EHA (all HY type). 103 of 115 conduit plants match by EIA_PtID. The 11 genuinely new are smaller canal-drop sites not previously in the EIA-923 sample that feeds EHA.

2. **Point Loma is not removed from the candidate CSV** (it stays in the 115-row file for completeness with Year=2017 as its last-nonzero label). But it is flagged offline in the report and must not be used as a live anchor. Any downstream use should filter to Year ≥ 2018 → it drops out.

3. **"WWTP" vs "municipal drinking water" distinction matters for WOWERS.** WOWERS targets wastewater OUTFALLS. Municipal drinking water transmission mains are hydraulically similar (continuous pressurized flow) but carry treated potable water, not effluent. The distinction is maintained in the corrected report.

4. **Gate framing.** The literal gate (≥50 sites with capacity + energy) passes at 115. The practical gate (≥50 new sites that change the Jul-2 kill decision) fails at 11. The report uses the practical framing — reviewers should verify they agree with this interpretation.

---

**If all checks pass: reviewer approves, and only then is `WOWERS_PROJECT_JOURNAL.md` written (by the coding agent per Tom's instruction). Journal must not be written before approval.**
