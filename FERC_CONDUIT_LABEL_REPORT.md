# FERC Conduit-Scale Label Hunt — Phase 5 Go/No-Go Gate Report

**Date:** 2026-07-04 (corrected after review)
**Branch:** `tom`
**Gate threshold:** ≥ 50 *new* usable sites with both installed capacity and measured annual energy → Phase 5 ML lives; < 50 → Jul-2 kill decision stands.
**Script to reproduce all numbers:** see §7.

---

## ONE-SENTENCE VERDICT

> **GATE FAILS: only 11 conduit sites with measured generation are genuinely new (not already in the Jun-30 combined ground truth). 103 of 115 were already owned. All 115 are ≥ 1 MW irrigation canal drops; no head/flow; the one wastewater site (Point Loma CA) has been offline since 2018. The Jul-2 "full Phase 5 ML not worth training as product" decision stands unchanged.**

---

## 1. Executive Summary

The hunt found that **FERC licensing databases carry no measured operating generation** (confirmed dead end, matching the RISE trap). The EHA FcDocket cross-link — data already on SANDISK — surfaces 115 Canal/Conduit plants with measured generation. But 103 of those 114 EIA-coded plants are already present in the Jun-30 combined ground truth. Only **11 are genuinely new**. 11 < 50 → gate fails on the real question (does new evidence flip the kill decision?).

Post-review corrections to the draft report:

| Claim (draft) | Corrected value | Error |
|---|---|---|
| ≤5 MW usable sites | **80** (not 81) | Off by one; verified against both CH_MW and Capacity_MW columns |
| Point Loma 2022 generation | **0 MWh** (not 5,422 MWh) | 5,422 MWh was 2005 value; plant offline 2018–2022 |
| "4 WWTP/municipal sites" | **1 wastewater + 3 drinking water** | Point Loma = treated wastewater; R E Badger / Manitou Springs / Ruxton Park = municipal drinking water |

---

## 2. Sources Searched

| Source | URL | What It Yields | Generation Data? |
|---|---|---|---|
| EHA Plant Inventory (already on SANDISK) | hydrosource.ornl.gov/data/datasets/eha2024/ | Plant name, lat/lon, capacity, FERC docket, mode | No (inventory only) |
| EHA Annual Capacity Factor workbook (already on SANDISK) | hydrosource.ornl.gov/data/datasets/existing-hydropower-assets-eha-capacity-factor-plant-database-2005-2022/ | Measured annual Net_Generation_MWh per plant, 2005–2022 (from EIA-923) | **YES — the label source** |
| FERC Active Conduit Exemptions (downloaded) | ferc.gov ActiveExemption_4.8.2025.xlsx | 222 conduit exemptions; authorized capacity (kW), state, waterway | **No** — capacity only |
| FERC Active Licenses (downloaded) | ferc.gov ActiveLicense_4.8.2025.xlsx | 1,016 active licenses; authorized capacity, state, waterway | **No** — capacity only |
| FERC Qualifying Conduit NOIs (post-2013 HREA) | ferc.gov qualifying-conduit page | ~30–50 NOIs; some Federal Register notices include **estimated** annual generation | **No** — engineering estimates, not measured |
| Hydropower eLibrary (PNNL/DOE) | hydropowerelibrary.pnnl.gov | FERC hydropower dockets | **No** — FERC metadata only |
| data.ferc.gov | data.ferc.gov | Structured FERC datasets | No hydropower generation tables |
| ORNL Conduit Potential PDF (already on SANDISK) | info.ornl.gov/sites/publications/Files/Pub176069.pdf | ESTIMATED potential — not actual generation | **No** |

### FERC measured-generation verdict

**FERC carries authorized capacity only — no measured operating generation.** FERC is a permitting system. Annual generation is reported to EIA (Form 923), which feeds EHA — already on SANDISK. This is the same finding as USBR RISE (Jun-30 journal). Pursuing FERC for energy labels is a dead end.

---

## 3. The EHA FcDocket Cross-Link

Joining EHA `Canal/Conduit` plants to the EHA CF workbook via `EHA_PtID` yields:

| Bucket | Plants | Plant-years | Notes |
|---|---|---|---|
| All Canal/Conduit in EHA | 338 | — | |
| With measured generation (CF workbook, latest nonzero year) | **115** | 1,725 | any scale |
| ≤ 5 MW (Capacity_MW) | **80** | — | primary WOWERS scale |
| ≤ 1 MW | **6** | — | closest to WWTP outfall scale |
| Already in Jun-30 combined_ground_truth (by EIA_PtID) | **103** | — | previously counted |
| **Genuinely new** (not in combined) | **11** | — | **the real number** |

---

## 4. Gate Arithmetic — Corrected

| Claim | Value |
|---|---|
| Gate threshold | ≥ 50 new usable sites |
| Sites with capacity + measured generation (any scale) | 115 |
| Of which already in Jun-30 combined ground truth | 103 |
| **Genuinely new sites** | **11** |
| Gate result | **FAILS (11 < 50)** |
| Phase 5 recommendation | **Decision unchanged** — full Phase 5 ML not worth training as product |

The letter of the gate (≥50 sites with capacity + energy) was satisfied by a re-slice of existing data. The spirit (new evidence sufficient to flip the Jul-2 kill decision) was not.

---

## 5. Point Loma — Flagged Offline; Not a Live Anchor

Point Loma (hc2003_p01, San Diego CA) was cited as the flagship WWTP wastewater outfall analog. **It is not a usable label:**

| Year | Net_Generation_MWh |
|---|---|
| 2005 | 5,422 |
| 2006 | 5,040 |
| 2007 | 13,388 |
| 2008 | 0 |
| 2009–2017 | variable |
| **2018** | **0** |
| **2019** | **0** |
| **2020** | **0** |
| **2021** | **0** |
| **2022** | **0** |

Plant appears offline since 2018. The "latest nonzero year" recipe silently selected 2017 (2,515 MWh) and masked this. Citing Point Loma as a live WWTP analog in any pitch would be incorrect.

**WWTP specificity of the 115 labels (corrected):**
- 1 true wastewater (Point Loma — offline since 2018, label stale)
- 3 municipal drinking water (R E Badger CA, Manitou Springs CO, Ruxton Park CO — active, but drinking water ≠ WWTP outfall)
- 111 irrigation canal drops

---

## 6. What the Labels Have and Don't Have

### Have (required for the letter of the gate)
- ✅ Installed capacity (kW) — EHA plant inventory `CH_MW`
- ✅ Measured annual energy (kWh/yr) — EHA CF workbook `Net_Generation_MWh` × 1,000
- ✅ State, lat/lon, plant name

### Don't Have (gaps that keep the kill decision in place)
- ❌ **Head (m)** and **flow (m³/s)** — absent; ARCH §5.4 physics-vs-real check still cannot run
- ❌ **Sub-1 MW scale** — 6 plants ≤ 1 MW; WOWERS viable sites median ~3.8 kW, far below
- ❌ **WWTP-specific** — 1 wastewater (offline), 3 drinking water, 111 irrigation canal
- ❌ **New evidence** — 103/115 already known; only 11 new, all ≥ 1 MW irrigation canal drops

---

## 7. Go/No-Go Recommendation

**Decision unchanged from Jul-2:** Full Phase 5 ML not worth training as a product deliverable.

The only already-approved next step is the **internal smoke-test** (pipeline proof only — numbers stay internal, never in director/pitch material): LightGBM on the 1,360 combined labels via existing rails. This was pre-approved in the Jul-2 session and is unchanged by this hunt.

The next real unblock for Phase 5 ML is micro-scale labels with head/flow — sub-MW WWTP or conduit plants, measured. No bulk-download source exists. Manual collection from municipal utility reports / WWTP energy audits is the only path.

---

## 8. Reproduction

```bash
cd "/Users/tomsmacbookpro/Desktop/Temp/WOWERS /wowers"

python -c "
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
result = conduit.join(cf_latest.select(['EHA_PtID','Net_Generation_MWh','Capacity_MW','Year']),
                       on='EHA_PtID', how='inner').filter(pl.col('Net_Generation_MWh')>0)
combined = pl.read_parquet('data/raw/ground_truth/combined_ground_truth.parquet')
conduit_eia = plant.filter(pl.col('Mode')=='Canal/Conduit').select(['EHA_PtID','EIA_PtID'])
result_eia = result.join(conduit_eia, on='EHA_PtID', how='left')
new_codes = set(result_eia.filter(pl.col('EIA_PtID').is_not_null())['EIA_PtID'].cast(pl.Int64).to_list())
old_codes = set(combined['source_plant_code'].drop_nulls().to_list())
print(f'Any-scale: {result.height}, <=5MW: {result.filter(pl.col(\"Capacity_MW\")<=5).height}')
print(f'Already owned: {len(new_codes & old_codes)}, Genuinely new: {len(new_codes - old_codes)}')
# Point Loma 2022
pl_gen = cf.filter((pl.col('EHA_PtID')=='hc2003_p01') & (pl.col('Year')==2022))['Net_Generation_MWh']
print(f'Point Loma 2022 MWh: {pl_gen.to_list()}')
"
# Expected: Any-scale: 115, <=5MW: 80
#           Already owned: 103, Genuinely new: 11
#           Point Loma 2022 MWh: [0.0]
```

---

## 9. Files Written

| Location | File | Contents |
|---|---|---|
| `/Volumes/SANDISK/.../FERC_Conduit/` | `ferc_conduit_candidates_2026-07-04.csv` | 115-row candidate table (includes Point Loma, flagged offline via is_wwtp_type + Year=2017 indicating stale label) |
| `/Volumes/SANDISK/.../FERC_Conduit/` | `ferc_active_conduit_exemptions_2025-04-08.xlsx` | FERC conduit exemptions source (222 active) |
| `/Volumes/SANDISK/.../FERC_Conduit/` | `ferc_active_licenses_2025-04-08.xlsx` | FERC active licenses source (1,016) |
| `data/raw/ground_truth/` | `ferc_conduit_candidates.parquet` | Same in polars parquet (gitignored) |
| repo root | `FERC_CONDUIT_LABEL_REPORT.md` | This report |
| repo root | `FERC_REVIEW_PROMPT.md` | Reviewer verification prompt |

Note: `.gitignore` also has one additive change (`.gstack/` added by the browse skill preamble). No Phase 1–4 source code or parquets modified.
