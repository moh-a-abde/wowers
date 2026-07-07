# P4-TIER + GEOJSON-EXPORT — Review Prompt (independent reviewer)

**To: Reviewing agent (fresh session)**  
**Re: Phase 4 CF-Calibrated Energy Columns + GeoJSON Frontend Export**  
**Branch:** `tom`  
**Note: `WOWERS_PROJECT_JOURNAL.md` must NOT be modified until this review passes.**

Every expected value in this prompt was verified by running the exact repro
command before writing it down (lesson from P5-SMOKE check-E failure).

---

## 1. What Was Built

### Part A — Three CF-calibrated energy columns in Phase 4 scorecard

| File | Change type | Summary |
|---|---|---|
| `config/settings.yaml` | Modified (additive) | Added `phase4.cf_calibration` block with three multipliers |
| `src/phase4/financials.py` | Modified (additive) | Added `add_calibrated_energy_cols()` function + `_CF_CALIB_DEFAULTS` + `import polars` |
| `src/phase4/run.py` | Modified (additive) | Import + one call: `out_df = add_calibrated_energy_cols(out_df)` |

### Part B — GeoJSON export script

| File | Change type | Summary |
|---|---|---|
| `scripts/export_geojson.py` | New | Exports 1,141 viable sites as GeoJSON FeatureCollection |
| `exports/viable_sites.geojson` | New (git-tracked) | Output file (776 KB, 1,141 features) |

### Tests

| File | Change type | Tests |
|---|---|---|
| `tests/test_phase4/test_calib_cols.py` | New | Calibrated-column unit + integration tests |
| `tests/test_scripts/__init__.py` | New | Package init |
| `tests/test_scripts/test_export_geojson.py` | New | GeoJSON unit + integration tests |

No Phase 1–3, Phase 5, `src/common/`, or `WOWERS_PROJECT_JOURNAL.md` modifications.

---

## 2. Claimed Numbers

| Check | Claimed value |
|---|---|
| Scorecard rows (new) | **3,783** |
| Scorecard columns (new) | **49** (was 46 + 3 new) |
| `project_viable` count | **1,141** |
| `annual_energy_kwh` fleet GWh (viable 1,141) | **409.1 GWh** |
| `energy_kwh_calib_floor_p25` fleet GWh | **119.1 GWh** |
| `energy_kwh_calib_floor_p50` fleet GWh | **182.9 GWh** |
| `energy_kwh_calib_central` fleet GWh | **281.5 GWh** |
| Old 46 columns value-identical to snapshot | **yes** |
| GeoJSON features | **1,141** |
| GeoJSON null-coord dropped | **0** |
| Spot-check `npdes_id` | **OH0024732** |
| Spot-check `annual_energy_kwh` (parquet) | **1,586,100** kWh |
| Spot-check `annual_energy_kwh` (GeoJSON) | **1586100** (int) |
| Spot-check `energy_kwh_calib_central` (parquet) | **1,091,236.8** kWh |
| Spot-check `energy_kwh_calib_central` (GeoJSON) | **1091237** (int, rounded) |
| Spot-check coords GeoJSON `[lon,lat]` | **[-83.01694, 39.91236]** |
| Spot-check `irr` (GeoJSON, 4 d.p.) | **0.2134** |
| Spot-check `project_viable` (GeoJSON) | **True** (bool) |
| Full pytest suite | **644 passed / 1 skipped** |

---

## 3. Repro Commands

Run all from repo root. Quote the path (contains a space).

```bash
cd "/Users/tomsmacbookpro/Desktop/Temp/WOWERS /wowers"

# === A. Snapshot and re-run Phase 4 ===
cp data/processed/phase4/financial_scorecards.parquet /tmp/scorecard_review_snapshot.parquet

/opt/miniconda3/bin/python -m src.phase4.run

# === B. Part A verification: column counts, identical old columns, fleet sums ===
/opt/miniconda3/bin/python -c "
import polars as pl

new = pl.read_parquet('data/processed/phase4/financial_scorecards.parquet')
old = pl.read_parquet('/tmp/scorecard_review_snapshot.parquet')

print('rows:', new.height)
print('cols:', len(new.columns))
print('project_viable:', new['project_viable'].sum())

# Old columns all present?
missing = [c for c in old.columns if c not in new.columns]
print('missing old columns:', missing or 'none')

# Old column values identical?
for col in old.columns:
    if old[col].dtype in (pl.Float64, pl.Float32):
        diff = (old[col] - new[col]).abs().max()
        if diff and diff > 1e-6:
            print(f'DIFF {col}: {diff}')
    else:
        ne = (old[col] != new[col]).sum()
        if ne: print(f'DIFF {col}: {ne} mismatches')
print('old columns value-identical: PASS (no output above means clean)')

# Fleet sums
viable = new.filter(pl.col('project_viable'))
print('viable rows:', viable.height)
print('annual_energy_kwh GWh:', round(viable['annual_energy_kwh'].sum()/1e6, 1))
print('calib_floor_p25  GWh:', round(viable['energy_kwh_calib_floor_p25'].sum()/1e6, 1))
print('calib_floor_p50  GWh:', round(viable['energy_kwh_calib_floor_p50'].sum()/1e6, 1))
print('calib_central    GWh:', round(viable['energy_kwh_calib_central'].sum()/1e6, 1))
"
# Expected:
#   rows: 3783
#   cols: 49
#   project_viable: 1141
#   missing old columns: none
#   old columns value-identical: PASS (no DIFF lines)
#   viable rows: 1141
#   annual_energy_kwh GWh: 409.1
#   calib_floor_p25  GWh: 119.1
#   calib_floor_p50  GWh: 182.9
#   calib_central    GWh: 281.5

# === C. GeoJSON export ===
/opt/miniconda3/bin/python scripts/export_geojson.py
# Expected:
#   Features written  : 1,141
#   Dropped (no coord): 0
#   Output            : .../exports/viable_sites.geojson

# === D. GeoJSON validation ===
/opt/miniconda3/bin/python -c "
import json
with open('exports/viable_sites.geojson') as f:
    fc = json.load(f)
print('type:', fc['type'])
print('features:', len(fc['features']))
# WGS84 validity check (lon -180..180, lat -90..90)
invalid_wgs84 = [ft for ft in fc['features']
    if not (-180 <= ft['geometry']['coordinates'][0] <= 180
            and -90 <= ft['geometry']['coordinates'][1] <= 90)]
print('invalid WGS84 coords:', len(invalid_wgs84))
# Non-continental US territories (lon outside -130..-60):
#   Alaska 10 sites (lon -152..-131), Hawaii 4 (lon -159..-158), Guam 2 (lon +144)
#   All are legitimate NPDES-permitted US facilities — not coordinate errors.
non_cont = [ft for ft in fc['features']
    if not (-130 <= ft['geometry']['coordinates'][0] <= -60)]
states = {}
for ft in non_cont:
    s = ft['properties']['state_code']
    states[s] = states.get(s, 0) + 1
print('non-continental US sites:', len(non_cont), '— by state:', states)
# Bool type check
bools = [ft for ft in fc['features']
         if not isinstance(ft['properties']['project_viable'], bool)]
print('project_viable non-bool:', len(bools))
# Int type check for energy
non_int = [ft for ft in fc['features']
           if not isinstance(ft['properties']['annual_energy_kwh'], int)]
print('annual_energy_kwh non-int:', len(non_int))
"
# Expected:
#   type: FeatureCollection
#   features: 1141
#   invalid WGS84 coords: 0
#   non-continental US sites: 16 — by state: {'AK': 10, 'GU': 2, 'HI': 4}
#     (all legitimate — prior prompt incorrectly used -130..-60 continental-only range)
#   project_viable non-bool: 0
#   annual_energy_kwh non-int: 0

# === E. Spot-check: OH0024732 parquet vs GeoJSON ===
/opt/miniconda3/bin/python -c "
import json, polars as pl
sc = pl.read_parquet('data/processed/phase4/financial_scorecards.parquet')
p1 = pl.read_parquet('data/processed/phase1/ranked_candidates.parquet').select(
    ['npdes_id','facility_name','city','latitude','longitude'])
joined = sc.filter(pl.col('project_viable')).join(p1, on='npdes_id', how='left')
row = joined.filter(pl.col('npdes_id')=='OH0024732').row(0, named=True)
print('Parquet annual_energy_kwh:', row['annual_energy_kwh'])
print('Parquet calib_central:', row['energy_kwh_calib_central'])
print('Parquet lat/lon:', row['latitude'], row['longitude'])

with open('exports/viable_sites.geojson') as f:
    fc = json.load(f)
ft = next(f for f in fc['features'] if f['properties']['npdes_id']=='OH0024732')
lon, lat = ft['geometry']['coordinates']
print('GeoJSON annual_energy_kwh:', ft['properties']['annual_energy_kwh'])
print('GeoJSON calib_central:', ft['properties']['energy_kwh_calib_central'])
print('GeoJSON coords [lon,lat]:', [lon, lat])
print('GeoJSON irr:', ft['properties']['irr'])
print('GeoJSON project_viable:', ft['properties']['project_viable'])
"
# Expected:
#   Parquet annual_energy_kwh: 1586100.0
#   Parquet calib_central: 1091236.8
#   Parquet lat/lon: 39.91236 -83.01694
#   GeoJSON annual_energy_kwh: 1586100   (int)
#   GeoJSON calib_central: 1091237       (int, rounded)
#   GeoJSON coords [lon,lat]: [-83.01694, 39.91236]
#   GeoJSON irr: 0.2134                  (4 d.p.)
#   GeoJSON project_viable: True         (bool)

# === F. Test suite ===
/opt/miniconda3/bin/python -m pytest -q --tb=no
# Expected: 644 passed, 1 skipped

# === G. Scope integrity ===
git diff HEAD -- src/phase1 src/phase2 src/phase3 src/phase5 src/common
# Expected: empty output

git diff HEAD -- WOWERS_PROJECT_JOURNAL.md
# Expected: empty output

git status --short
# Expected:
#    M config/settings.yaml
#    M src/phase4/financials.py
#    M src/phase4/run.py
#   ?? exports/
#   ?? scripts/export_geojson.py
#   ?? tests/test_phase4/test_calib_cols.py
#   ?? tests/test_scripts/
#   ?? P4_TIER_EXPORT_REVIEW_PROMPT.md
```

---

## 4. Expected Numbers Table

| Check | Expected |
|---|---|
| Scorecard rows | **3,783** |
| Scorecard columns | **49** |
| `project_viable` count | **1,141** |
| New columns | `energy_kwh_calib_floor_p25`, `energy_kwh_calib_floor_p50`, `energy_kwh_calib_central` |
| Fleet GWh — `annual_energy_kwh` | **409.1** |
| Fleet GWh — `calib_floor_p25` | **119.1** |
| Fleet GWh — `calib_floor_p50` | **182.9** |
| Fleet GWh — `calib_central` | **281.5** |
| Old 46 columns value-identical | yes (no DIFF lines) |
| GeoJSON feature count | **1,141** |
| GeoJSON null-coord dropped | **0** |
| Spot-check `OH0024732` `annual_energy_kwh` | **1,586,100 kWh → 1586100 (int)** |
| Spot-check `OH0024732` `energy_kwh_calib_central` | **1,091,236.8 → 1091237 (int)** |
| Spot-check `OH0024732` coords | **[-83.01694, 39.91236] (lon first)** |
| Spot-check `OH0024732` `irr` | **0.2134 (4 d.p.)** |
| Spot-check `OH0024732` `project_viable` | **True (bool, not string)** |
| Non-continental US sites in GeoJSON | **16 (AK=10, HI=4, GU=2) — all legitimate** |
| Invalid WGS84 coordinates | **0** |
| Pytest suite | **644 passed / 1 skipped** |
| `WOWERS_PROJECT_JOURNAL.md` modified | **No** |
| Phase 1–3, Phase 5, `src/common/` modified | **No** |

---

## 7. Known Upstream Data Issue — Racine WI (WI0025194)

**Finding (reviewer, round 1):** Site `WI0025194` (Racine, WI) has `latitude = 4.4`
in `ranked_candidates.parquet`. The correct latitude for Racine, WI is ~42.73;
longitude -87.77 is correct. The value 4.4 is a truncated/corrupt coordinate
inherited from the upstream ECHO ICIS_FACILITIES data — pre-existing Phase 1 issue,
not introduced by this task.

**Consequence:** This site renders in the ocean off Colombia (~4.4°N, 87.7°W) on
the frontend map. It is the only implausible coordinate among all 1,141 viable sites
(reviewer scanned all of them).

**Disposition: document, do not patch.** Hand-editing the GeoJSON would create hidden
data divergence from the Phase 1 parquet. The correct fix is a coordinate sanity guard
in `src/phase1/filter_potw.py` (reject lat < 15° for US-only NPDES permits) — backlog
item for a future Phase 1 session.

**Teammate notice:** One dot on the map (Racine WI, `WI0025194`) will appear far off
the US coast due to a corrupt latitude in the upstream EPA data. All other 1,140 sites
have correct coordinates. Do not use `WI0025194` for any site-specific demo or pitch
illustration until the Phase 1 coordinate guard is implemented.

---

## 5. Scope-Integrity Checklist

- [ ] `git diff HEAD -- src/phase1 src/phase2 src/phase3 src/phase5 src/common` is empty
- [ ] `git diff HEAD -- WOWERS_PROJECT_JOURNAL.md` is empty
- [ ] `git status --short` shows only: M config/settings.yaml, M src/phase4/financials.py, M src/phase4/run.py, ?? exports/, ?? scripts/export_geojson.py, ?? tests/test_phase4/test_calib_cols.py, ?? tests/test_scripts/, ?? P4_TIER_EXPORT_REVIEW_PROMPT.md
- [ ] Scorecard has 49 columns (46 + 3)
- [ ] All 46 pre-existing columns are value-identical to the pre-re-run snapshot
- [ ] Fleet GWh sums: 409.1 / 119.1 / 182.9 / 281.5
- [ ] `exports/viable_sites.geojson` exists and parses as FeatureCollection
- [ ] GeoJSON has 1,141 features, 0 dropped for null coords
- [ ] Coordinate order is [longitude, latitude] (continental US: first coord negative; AK/HI/GU also present)
- [ ] Invalid WGS84 coordinates: 0; non-continental sites: 16 (AK=10, HI=4, GU=2)
- [ ] Racine WI (WI0025194) latitude=4.4 upstream issue documented; not patched
- [ ] `annual_energy_kwh` in GeoJSON is int (not float)
- [ ] `project_viable` in GeoJSON is bool (not string)
- [ ] `irr` rounded to 4 decimal places
- [ ] Test suite: 644 passed / 1 skipped

---

## 6. Key Design Decisions for Reviewer

1. **Global fleet multipliers** (not per-site CF ratios). Multiplier = tier_CF / 0.872
   (Phase 2 fleet median). Matches CF_CALIBRATION_REPORT.md §6 exactly. Per-site spread
   is tight (p10–p90: 0.856–0.883) so site-level ratios give near-identical results.
   Documented in `add_calibrated_energy_cols` docstring.

2. **`add_calibrated_energy_cols` lives in `financials.py`** (not `run.py`). It is a
   financial column calculation; `run.py` remains the orchestrator with a single
   additive call. Pure function with no side effects — importable by tests without
   triggering Phase 4 I/O.

3. **GeoJSON compact format** (`separators=(",",":")`) — no extra whitespace. Saves
   ~15% file size vs pretty-print. Frontend JSON parsers handle this correctly.

4. **`exports/` is git-tracked** (not gitignored). The GeoJSON is the static data
   source for the frontend map demo. Tom commits it after review passes.

5. **`--all` flag** exports all 3,783 scored sites (not just viable). Default is
   viable-only (1,141). Useful for showing the full technical potential on the map.

---

**If all checks pass: reviewer approves, then Tom logs the P4-TIER session in
`WOWERS_PROJECT_JOURNAL.md` and decides whether to commit.**
