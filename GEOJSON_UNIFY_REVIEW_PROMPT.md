# GEOJSON-UNIFY — Review Prompt

---

## REVIEW OUTCOME (Tom, 2026-07-06 PM #5) — APPROVED, ZERO FALSIFIED CLAIMS

First fully clean round since the falsified-claim series began (7 prior instances).
Every claim below was independently reproduced against live code + parquets:

- **Data:** parquet baseline intact (17,148 / 5,464 / 3,778 / 1,138 / 409.1695 GWh —
  recomputed from parquets, not trusted from the agent's before-hash). GeoJSON:
  1,138 features · 58 props uniform · meta computed from `p1_full.height`/`p4.height`
  (code-inspected) · deterministic across two reviewer-run exports
  (SHA `f359b413…` reproduced). Aggregates: NPV diff $5, CapEx $1, revenue $32,
  energy exact, 848 high-conf, 1,138 tier A, median 9.8, 0 sentinels. Nulls only in
  legitimately-optional fields (p10/p90 flow 290, utilization 41, elevations 2/54).
- **Tests:** 717 passed / 1 skipped reproduced; new tests inspected — non-tautological.
- **Frontend:** `tsc -b --noEmit` clean; build clean (geojson asset 1,846,247 B in
  `dist/assets/`); dev server served the geojson via `/@fs` (200, 1,138 features).
- **Live QA (headless browser):** dashboard KPIs 17,148 / 1,138 / $310.1M / 9.8 yr;
  "1,138 sites shown"; Top-5 populated; plant detail (OH0024732) fully populated,
  all values match geojson; CA portfolio 147 sites / $125.9M with full table +
  summary. CA confidence pills (13 High / 134 Lower) verified identical to the old
  `export_web_data.py` output — not a regression.
- **Not verifiable headless:** maplibre map canvas (WebGL unavailable in headless
  Chromium/SwiftShader — environment limitation, not an app bug). MapView component
  is unchanged and receives the same MapProps shape; Tom should eyeball dot
  rendering once in a real browser.

**Nits (non-blocking, not fixed):**
1. `export_geojson.py` `load_and_join()` docstring references "§1.1" of the prompt
   file (meaningless to future readers) and says missing columns raise `KeyError` —
   polars raises `ColumnNotFoundError`.
2. Adapter (`data.ts`) has no sentinel-payback guard (old `map_props` nulled
   ≥1e5). Harmless for the viable-only file (0 sentinels verified); would show
   "1000000 yr" if someone ever pointed the frontend at an `--all` export.

Original agent-written review prompt preserved unmodified below.

---

**To: Independent reviewing agent (fresh session, full repo access)**  
**Branch:** `tom`  
**Starting commit:** `e40a3c9`  
**Note: `WOWERS_PROJECT_JOURNAL.md` must NOT be modified. Tom logs after review.**

Every numeric claim below was verified by running the exact command shown.
No claim was written without a pasted output.

---

## 1. What Was Built

### Part 1 — `scripts/export_geojson.py` extended

| Change | Detail |
|---|---|
| Properties | 24 → **58** (34 new: P1 flow stats, P2 MC energy, P3 elevation/turbine, P4 capex breakdown + sensitivity + grant/opex/rate + data\_quality + high-conf flag) |
| New rounding class `_DP1_COLS` | 1 d.p.: `mean_flow_mgd`, `p10_flow_mgd`, `p90_flow_mgd`, `head_net_m`, `head_gross_m`, `elevation_m`, `elev_outfall_m`, `q_rated_m3s`, `peak_efficiency_pct` |
| New joins | P2 (`energy_yield_estimates.parquet`) + P3 (`turbine_sizing.parquet`) via new `--p2` / `--p3` CLI args |
| `meta` foreign member | `{"plants_analyzed": 17148, "scored_sites": 3778, "baseline": "P2-SEED re-baseline 2026-07-06"}` — computed from parquet row counts, not hardcoded |
| `validate_geojson()` | Now asserts `meta` keys if present: positive int `plants_analyzed`/`scored_sites` + str `baseline` |
| Determinism | Two consecutive export runs produce byte-identical output |

### Part 2 — Frontend single-file data layer

| File | Change |
|---|---|
| `frontend/vite.config.ts` | Added `server.fs.allow: [".."]` (one new key) |
| `frontend/src/vite-env.d.ts` | **New** — `declare module "*.geojson?url"` type declaration |
| `frontend/src/lib/data.ts` | **Rewritten** — imports `sitesUrl` from `../../../exports/viable_sites.geojson?url`; module-level cached fetch; derives `PlantCollection`, `National`, `Portfolio`, `PlantDetail` client-side |
| `frontend/src/views/NationalMap.tsx` | Line 29: `return maxPayback >= 20` → `return false` (null-payback belt-and-braces; viable sites always have a payback) |

**Not changed:** `scripts/export_web_data.py`, `frontend/public/data/**` (untouched — gitignored by `frontend/.gitignore:9`), any Phase 1–5 source code, any parquet, journal.

---

## 2. Claims Table

Every claim below can be independently reproduced by running the command shown.

### Part 1 claims

| Claim | Repro command | Expected output |
|---|---|---|
| GeoJSON has 1,138 features, 0 dropped | `python scripts/export_geojson.py` | `Features written  : 1,138 / Dropped (no coord): 0` |
| 58 properties per feature | see § Repro A | `properties per feature: 58` |
| meta.plants_analyzed = 17,148 | see § Repro A | `meta.plants_analyzed=17148` |
| meta.scored_sites = 3,778 | see § Repro A | `meta.scored_sites=3778` |
| Run 1 SHA-256 | see § Repro B | `f359b413c1d38f80fbdb8ad8fcbb7d3ae7e16b6350dce57ffde1e0c51ef27d22` |
| Run 2 SHA-256 (identical = deterministic) | see § Repro B (run twice) | same hash |
| Σ npv_usd diff vs ref | see § Repro A | diff = 5 (within ±$1,500 tolerance) |
| Σ total_capex_usd diff | see § Repro A | diff = 1 |
| Σ annual_revenue_usd diff | see § Repro A | diff = 32 |
| Σ energy MWh diff | see § Repro A | diff = 0 |
| high_confidence_sites | see § Repro A | 848 (exact) |
| tier_A count | see § Repro A | 1,138 (exact) |
| median_payback | see § Repro A | 9.8 |
| sentinel paybacks in viable | see § Repro A | 0 (must be 0) |
| Pytest suite | `python -m pytest -q --tb=no` | **717 passed, 1 skipped** |
| data/processed/ SHA-256 unchanged | see § Repro C | matches before hash |

### Part 2 claims

| Claim | Repro command | Expected output |
|---|---|---|
| typecheck clean | `cd frontend && npx tsc -b --noEmit` | no error output |
| build clean; geojson asset in dist | `npm run build` | `dist/assets/viable_sites-*.geojson 1,846.25 kB` |
| dev root HTTP 200 | `curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/` (with dev server running) | `200` |
| geojson via @fs HTTP 200 | see § Repro D (with dev server running) | `200` |

---

## 3. Repro Commands

```bash
cd "/Users/tomsmacbookpro/Desktop/Temp/WOWERS /wowers"

# === Repro A — property count, meta, aggregate cross-checks ===
python scripts/export_geojson.py   # regenerate first if needed

/opt/miniconda3/bin/python -c "
import json, math
with open('exports/viable_sites.geojson') as f:
    fc = json.load(f)
feats = fc['features']
props = [f['properties'] for f in feats]
m = fc['meta']
print('properties per feature:', len(props[0]))
print(f'meta.plants_analyzed={m[\"plants_analyzed\"]}  meta.scored_sites={m[\"scored_sites\"]}')
print(f'meta.baseline={m[\"baseline\"]}')
npv   = sum(p['npv_usd'] or 0 for p in props)
capex = sum(p['total_capex_usd'] or 0 for p in props)
rev   = sum(p['annual_revenue_usd'] or 0 for p in props)
emwh  = sum((p['annual_energy_kwh'] or 0)/1e3 for p in props)
hc    = sum(1 for p in props if p.get('project_viable_high_confidence'))
ta    = sum(1 for p in props if p.get('site_tier') == 'A')
pbs   = sorted(p['payback_years'] for p in props if p.get('payback_years') is not None)
n = len(pbs); mid = n//2
med   = round(((pbs[mid-1]+pbs[mid])/2 if n%2==0 else pbs[mid]), 1)
sent  = sum(1 for p in props if p.get('payback_years') is not None and p['payback_years']>=1e5)
print(f'Σ npv_usd:       {npv:,}  ref=310,133,617  diff={abs(npv-310133617):,}')
print(f'Σ total_capex:   {capex:,}  ref=211,325,214  diff={abs(capex-211325214):,}')
print(f'Σ annual_rev:    {rev:,}  ref=41,234,512   diff={abs(rev-41234512):,}')
print(f'Σ energy MWh:    {emwh:.0f}  ref=409170')
print(f'high_conf={hc}  tier_A={ta}  median_pb={med}  sentinels={sent}')
"
# Expected:
#   properties per feature: 58
#   meta.plants_analyzed=17148  meta.scored_sites=3778
#   meta.baseline=P2-SEED re-baseline 2026-07-06
#   Σ npv_usd:       310,133,622  ref=310,133,617  diff=5
#   Σ total_capex:   211,325,213  ref=211,325,214  diff=1
#   Σ annual_rev:    41,234,480   ref=41,234,512   diff=32
#   Σ energy MWh:    409170  ref=409170
#   high_conf=848  tier_A=1138  median_pb=9.8  sentinels=0

# === Repro B — determinism (two runs byte-identical) ===
/opt/miniconda3/bin/python scripts/export_geojson.py
sha256sum exports/viable_sites.geojson
/opt/miniconda3/bin/python scripts/export_geojson.py
sha256sum exports/viable_sites.geojson
# Expected: f359b413c1d38f80fbdb8ad8fcbb7d3ae7e16b6350dce57ffde1e0c51ef27d22 both runs

# === Repro C — data/processed/ SHA-256 unchanged ===
/opt/miniconda3/bin/python -c "
import hashlib, os
d = hashlib.sha256(b''.join(
    open(os.path.join(r,fn),'rb').read()
    for r,ds,fs in os.walk('data/processed') for fn in sorted(fs) if fn.endswith('.parquet')
)).hexdigest()
print('SHA-256:', d)
print('Expected: 0af4c958938542c4e92f3da20bc53ded07848fa13abaa122ce33d9f27fd301df')
print('Match:', d == '0af4c958938542c4e92f3da20bc53ded07848fa13abaa122ce33d9f27fd301df')
"

# === Repro D — full pytest ===
/opt/miniconda3/bin/python -m pytest -q --tb=no
# Expected: 717 passed, 1 skipped

# === Repro E — typecheck ===
cd frontend && npx tsc -b --noEmit
# Expected: clean (no output)

# === Repro F — build ===
npm run build 2>&1 | grep -E "viable_sites|built in|✓"
# Expected: dist/assets/viable_sites-*.geojson  1,846.25 kB  / ✓ built

# === Repro G — dev server serving ===
npm run dev &
sleep 4
ROOT=$(pwd)/..
ROOT_ENC=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$ROOT/exports/viable_sites.geojson")
echo "root:" $(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/)
echo "geojson via @fs:" $(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5173/@fs${ROOT_ENC}")
kill %1
# Expected: root: 200 / geojson via @fs: 200

# === Repro H — scope check ===
cd ..
git diff HEAD --stat
# Expected: exactly these 6 files modified:
#   exports/viable_sites.geojson
#   frontend/src/lib/data.ts
#   frontend/src/views/NationalMap.tsx
#   frontend/vite.config.ts
#   scripts/export_geojson.py
#   tests/test_scripts/test_export_geojson.py
# Plus 2 untracked:
#   ?? GEOJSON_UNIFY_PROMPT.md
#   ?? frontend/src/vite-env.d.ts

git diff HEAD -- scripts/export_web_data.py frontend/public/data/
# Expected: empty (untouched)

git diff HEAD -- WOWERS_PROJECT_JOURNAL.md
# Expected: empty
```

---

## 4. What I Changed and Why (file by file)

### `scripts/export_geojson.py`
- **`PROPERTIES`** extended from 24 to 58 entries (34 new appended after the originals in the order specified in the prompt).
- **`_DP1_COLS`** new frozenset for 1 d.p. rounding (MGD flows, metres, m³/s, efficiency %). Handled in `round_property()` after `_RATIO_COLS` branch.
- **`_INT_COLS`** and **`_RATIO_COLS`** extended with new members.
- **`load_and_join()`** signature changed to `(scorecard_path, p1_path, p2_path=None, p3_path=None) -> tuple[pl.DataFrame, dict]`. Returns joined df + `meta` dict (computed from parquet row counts). P2 and P3 joins are conditional on args being non-None (clean skip if paths omitted).
- **`build_feature_collection()`** gains `meta: dict | None = None` kwarg; if present, adds `fc["meta"] = meta`.
- **`validate_geojson()`** checks `meta` keys if meta is present.
- **`export()`** updated to unpack `(df, meta)` tuple and pass `meta` through.
- **CLI** gains `--p2` / `--p3` args defaulting to the standard parquet paths.

### `tests/test_scripts/test_export_geojson.py`
- Imports `_DP1_COLS`, `_DEFAULT_P2`, `_DEFAULT_P3` from the updated module.
- New tests in `TestRoundProperty`: 1 d.p. class (including NaN/inf), new int cols (P2 energy, P4 capex/sensitivity), new ratio cols, bool passthrough for `project_viable_high_confidence`, string passthrough for new string props.
- New test `test_property_count_is_58` in `TestBuildFeature`.
- New tests in `TestValidateGeojson`: FC with meta passes, missing/zero/non-int meta fields raise.
- New integration tests `test_geojson_has_58_properties` and `test_geojson_meta_present_and_correct`.

### `frontend/vite.config.ts`
Added `server: { fs: { allow: [".."] } }`. Required for Vite's dev server to serve files from the repository root (one level above `frontend/`), so the `?url` import resolves at runtime.

### `frontend/src/vite-env.d.ts` (new)
`declare module "*.geojson?url"` — tells TypeScript that the `?url` import suffix returns a `string` (the URL). Without this, `tsc` would emit `Cannot find module '*.geojson?url'`.

### `frontend/src/lib/data.ts`
Fully rewritten as a single-file adapter:
1. Module-level `_cache: Promise<SiteCollection> | null` — the file is fetched only once per page load.
2. `fetchPlants()` maps raw `SiteProps` → `MapProps` (id, name, city, state, turbine, energy_mwh, payback, npv, tier, viable, band, confidence). Band/confidence logic mirrors `export_web_data.py`.
3. `fetchNational()` derives all KPIs from features + `meta` (plants_analyzed, scored_sites come from the meta foreign member; everything else computed over the 1,138 feature array).
4. `fetchPortfolio(state)` filters by `state_code`, throws on empty (matching the existing 404 error path), builds `TableRow[]` sorted by npv desc. `n_scored = n_viable` (see §5 judgment calls).
5. `fetchPlant(id)` finds by `npdes_id`, throws if not found, maps full `PlantDetail` shape. GeoJSON coordinates are `[lon, lat]` — extracted correctly.
6. `useAsync` hook unchanged.

### `frontend/src/views/NationalMap.tsx`
Single line: `if (p.payback == null) return maxPayback >= 20` → `return false`. Since the new data source exports only viable sites and all viable sites have a real payback (confirmed: 0 sentinel paybacks), a null payback is a bug and the site should not be shown. The old logic was a workaround for the non-viable grey dots that no longer exist.

---

## 5. Known Limitations / Judgment Calls

1. **`n_scored` in `Portfolio`**: set equal to `n_viable`. The GeoJSON only contains the 1,138 viable sites, so the 3,778 scored-but-not-viable count is unknowable client-side without the old `plants/{id}.json` files. This was explicitly specified in the prompt. The `StatePortfolio.tsx` component currently only displays `n_viable`, so there is no visible regression.

2. **Aggregate sum tolerances**: per-site rounding (integers) vs. sum-then-round produces small differences vs. the reference values computed by `export_web_data.py` (which uses raw floats throughout). The diffs (Σ npv: 5, Σ capex: 1, Σ revenue: 32) are well within the ±$1,500 tolerance specified in the prompt. This is expected and correct behavior.

3. **P2 / P3 joins for non-viable sites**: When `--all` is used, non-viable sites that didn't reach Phase 3 will have null for P3 columns (head, turbine detail). This is correct behavior for a left join and the frontend renders `—` for null values.

4. **GeoJSON size**: `viable_sites.geojson` is 1,846 kB in the build output. This is acceptable for a static single-page app demo. Vite applies gzip at the serving layer and the file loads once per session (module cache).

5. **`avg_payback` in `Portfolio`**: computed as the mean of non-null payback values (rounded to 1 d.p.). The `StatePortfolio.tsx` view displays this. No sentinel values exist among viable sites.

6. **`export_web_data.py` and `frontend/public/data/`**: left completely untouched per the process rules. Tom decides when to retire them.

---

## 6. Review Checklist (ordered by blast radius)

### A — Data correctness (highest blast radius)
- [ ] All 58 properties match the spec table in the prompt (§1.2)
- [ ] `meta.plants_analyzed` = P1 row count (not hardcoded) — Repro A
- [ ] `meta.scored_sites` = P4 row count (not hardcoded) — Repro A
- [ ] Aggregate sums within ±$1,500 tolerance — Repro A
- [ ] 0 sentinel paybacks in viable sites — Repro A
- [ ] `data/processed/` SHA-256 identical before/after — Repro C
- [ ] `export_web_data.py` and `frontend/public/data/` untouched — Repro H

### B — Exporter determinism
- [ ] Two export runs produce byte-identical SHA-256 — Repro B
- [ ] `round_property` handles NaN/inf → None for all three rounding classes (int, ratio, 1 d.p.)

### C — Adapter math (frontend derivations)
- [ ] `fetchNational().plants_analyzed` comes from `meta`, not hardcoded
- [ ] `fetchNational().viable_projects` = feature count (not meta)
- [ ] `fetchPortfolio("CA")` throws for unknown state; returns Portfolio for known state
- [ ] `fetchPlant("CA0107409")` returns PlantDetail with all required fields populated
- [ ] GeoJSON coord order `[lon, lat]` → `lat`/`lon` correctly swapped in `fetchPlant`
- [ ] `dmr_backed` uses `data_quality ∈ {dmr, dmr_limited}` (not `data_quality_tier`)
- [ ] `viabilityBand` thresholds: <5→high, ≤15→moderate, ≤20→marginal, else→nonviable
- [ ] `siteConfidence` logic matches `export_web_data.py`: `high_conf OR dmr → High`; `dmr_limited → Medium`; else `Lower`

### D — Build health
- [ ] `npx tsc -b --noEmit` clean — Repro E
- [ ] `npm run build` exits 0; geojson asset appears in `dist/assets/` — Repro F
- [ ] Dev server: root 200, geojson `@fs` URL 200 — Repro G

### E — Scope integrity
- [ ] `git diff HEAD --stat` shows exactly 6 modified files + 2 untracked — Repro H
- [ ] `scripts/export_web_data.py` diff is empty
- [ ] `frontend/public/data/**` diff is empty
- [ ] `WOWERS_PROJECT_JOURNAL.md` diff is empty
- [ ] pytest: 717 passed / 1 skipped — Repro D

---

**If all checks pass: reviewer approves; Tom logs GEOJSON-UNIFY in the journal and commits.**
