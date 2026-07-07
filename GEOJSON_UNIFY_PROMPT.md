# GEOJSON-UNIFY — Coding-Agent Prompt

**Task ID:** GEOJSON-UNIFY (single task, two parts — exporter first, frontend second).
**Repo:** WOWERS, branch `tom` (start from commit `e40a3c9`).
**Python:** `/opt/miniconda3/bin/python` (polars, numpy, pytest available).
**Node:** `frontend/node_modules` already installed; `npm run build` currently passes.
**Baseline test suite:** 701 passed / 1 skipped (`/opt/miniconda3/bin/python -m pytest tests/ -q`).

---

## Context

The frontend (`frontend/`, vite + react + maplibre) currently fetches four kinds of
static files from `frontend/public/data/` — `plants.geojson` (all 3,778 scored sites),
`national.json`, `portfolio/<STATE>.json`, and `plants/<npdes_id>.json` — all generated
by `scripts/export_web_data.py`, which requires all four production parquets. Two
problems:

1. **Non-viable sites are displayed.** `plants.geojson` includes all 3,778 scored
   sites; sites with payback > 20 yr (or no payback at all) render as grey
   "nonviable" dots, and `NationalMap.tsx:29` even includes null-payback sites when
   the payback slider sits at its default of 20.
2. **The data layer is not git-tracked.** `frontend/public/data/` is gitignored;
   anyone cloning the repo must run the Python exporter (and therefore have the
   parquets) before the frontend shows anything.

**Goal:** make the git-tracked `exports/viable_sites.geojson` (1,138 project-viable
sites) the frontend's *only* data source. Extend the exporter so the file carries
every field the frontend renders; rewrite the frontend data layer to derive the
national / portfolio / detail shapes client-side from that one file. After this task,
`git clone` + `cd frontend && npm install && npm run dev` shows the full dashboard
with zero Python steps, and non-viable sites are gone by construction.

Current production state (all committed at `e40a3c9`):

| Artifact | Value |
|---|---|
| `phase1/ranked_candidates.parquet` | 17,148 rows |
| `phase2/energy_yield_estimates.parquet` | 17,148 rows; `excluded==False` → 5,464 |
| `phase3/turbine_sizing.parquet` | 5,464 rows; `head_valid` → 4,860 |
| `phase4/financial_scorecards.parquet` | 3,778 rows; viable 1,138; 409.1695 GWh |
| `exports/viable_sites.geojson` | 1,138 features, 24 properties each |

Reference cross-check values (computed 2026-07-06 by `scripts/export_web_data.py`
from the same parquets; see `frontend/public/data/national.json`):

| Aggregate over the 1,138 viable sites | Value |
|---|---|
| Σ `npv_usd` | $310,133,617 |
| Σ `total_capex_usd` | $211,325,214 |
| Σ `annual_revenue_usd` | $41,234,512 |
| Σ `annual_energy_kwh` / 1e3 | 409,170 MWh |
| median `payback_years` | 9.8 |
| count `project_viable_high_confidence` | 848 |
| count `site_tier == "A"` | 1,138 |

---

## Process rules — read before anything else

- **STOP-on-surprise.** Any invariant miss, crash, or unexpected number: stop,
  document exactly what you saw, and end the session with a report. Do NOT
  improvise workarounds, do NOT hand-edit parquets or the geojson, do NOT
  regenerate any parquet. This task reads parquets; it never writes them.
- **`data/processed/**` and `data/checkpoints/**` are read-only.** Take SHA-256
  of every file under `data/processed/` before starting; verify identical at the
  end and paste both digests in your report.
- **No pipeline runs.** Do not invoke `src.phase*.run` or any phase module's CLI.
  The only script you run against the parquets is `scripts/export_geojson.py`.
- **No background/orphaned processes.** Foreground only, generous timeouts.
- **No commits. No edits to `WOWERS_PROJECT_JOURNAL.md`.** Tom reviews first.
- **Do not delete or modify `scripts/export_web_data.py`** or anything under
  `frontend/public/data/` — the old path stays intact until Tom retires it.
- Seven previous review rounds caught claims written without running the repro.
  Every numeric claim in your report and review prompt must come from a command
  you actually ran, with output pasted.

---

## Part 1 — Extend `scripts/export_geojson.py`

### 1.1 New joins

`load_and_join()` currently joins P4 scorecard ← P1 (`facility_name`, `city`,
`latitude`, `longitude`). Extend it to also left-join (all on `npdes_id`):

- **P1** `data/processed/phase1/ranked_candidates.parquet` — add `mean_flow_mgd`,
  `p10_flow_mgd`, `p90_flow_mgd`, `n_months_data`, `utilization_ratio`.
- **P2** `data/processed/phase2/energy_yield_estimates.parquet` — add
  `energy_p10_kwh_yr`, `energy_p50_kwh_yr`, `energy_p90_kwh_yr`,
  `equivalent_homes_p50`. New CLI arg `--p2` (default path as above), same
  pattern as the existing `--p1`.
- **P3** `data/processed/phase3/turbine_sizing.parquet` — add `head_net_m`,
  `head_gross_m`, `elevation_m`, `elev_outfall_m`, `head_source`,
  `head_confidence`, `q_rated_m3s`, `peak_efficiency_pct`. New CLI arg `--p3`.

All of these column names are proven to exist — `scripts/export_web_data.py`
selects the identical names and ran successfully on 2026-07-06. If any column is
missing at runtime, that is a STOP-on-surprise, not a rename-and-guess.

### 1.2 New properties

Append to `PROPERTIES` (keep the existing 24 first, in their current order):

| New property | Source | Rounding class |
|---|---|---|
| `mean_flow_mgd`, `p10_flow_mgd`, `p90_flow_mgd` | P1 | 1 d.p. |
| `n_months_data` | P1 | int |
| `utilization_ratio` | P1 | ratio (4 d.p.) |
| `energy_p10_kwh_yr`, `energy_p50_kwh_yr`, `energy_p90_kwh_yr` | P2 | int |
| `equivalent_homes_p50` | P2 | int |
| `head_net_m`, `head_gross_m`, `elevation_m`, `elev_outfall_m` | P3 | 1 d.p. |
| `head_source`, `head_confidence` | P3 | string passthrough |
| `q_rated_m3s` | P3 | 1 d.p. |
| `peak_efficiency_pct` | P3 | 1 d.p. |
| `npv_with_50pct_grant_usd`, `annual_opex_usd` | P4 | int |
| `elec_rate_per_kwh` | P4 | ratio (4 d.p.) |
| `equipment_capex_usd`, `installation_capex_usd`, `interconnection_capex_usd`, `permitting_capex_usd` | P4 | int |
| `permitting_tier` | P4 | string passthrough |
| `sensitivity_head_npv_low`, `sensitivity_head_npv_high`, `sensitivity_flow_npv_low`, `sensitivity_flow_npv_high`, `sensitivity_rate_npv_low`, `sensitivity_rate_npv_high` | P4 | int |
| `dominant_sensitivity` | P4 | string passthrough |
| `data_quality` | P4 | string passthrough |
| `project_viable_high_confidence` | P4 | bool passthrough |

That is 34 new properties → 58 total. Implement the 1 d.p. class as a new
frozenset (e.g. `_DP1_COLS`) handled in `round_property()` alongside the existing
`_INT_COLS` / `_RATIO_COLS`; NaN/inf → `None` exactly like the other classes.

### 1.3 Top-level `meta` member

Add a foreign member (RFC 7946 §6.1 permits it) to the FeatureCollection:

```json
"meta": {
  "plants_analyzed": 17148,
  "scored_sites": 3778,
  "baseline": "P2-SEED re-baseline 2026-07-06"
}
```

`plants_analyzed` = row count of the P1 parquet; `scored_sites` = row count of the
P4 scorecard — **computed, not hardcoded** (the string literal above shows the
expected values, which the tests then assert). No timestamps — output must be
byte-deterministic across runs.

### 1.4 Validation + tests

- Extend `validate_geojson()` to assert the `meta` keys exist and are positive ints.
- Update `tests/test_scripts/test_export_geojson.py`: rounding tests for the new
  classes (1 d.p., new int/ratio members), property-count assertion (58),
  meta assertions (17,148 / 3,778), and keep the 1,138-feature assertion working.
- Regenerate `exports/viable_sites.geojson` via the script's CLI (no ad-hoc code)
  and confirm: 1,138 features, 0 dropped for null coords, each feature has 58
  properties. Run the exporter twice; the two outputs must be byte-identical.

### 1.5 Sanity cross-check (paste output in report)

With a short Python snippet over the regenerated geojson, verify against the
reference table in the Context section: Σ npv, Σ capex, Σ revenue within ±$1,500
of the reference values (per-site int rounding vs. sum-then-round tolerance);
Σ energy within ±600 kWh; counts (848 high-confidence, 1,138 tier A) exact;
median `payback_years` = 9.8 ±0.05; no `payback_years` ≥ 1e5 anywhere (the
sentinel must not appear among viable sites — if it does, STOP).

---

## Part 2 — Frontend: single-file data layer

### 2.1 Loading

Import the git-tracked file directly so there is exactly one copy in the repo:

```ts
// frontend/src/lib/data.ts
import sitesUrl from "../../../exports/viable_sites.geojson?url";
```

- Add a TS declaration for `*.geojson?url` (e.g. in `frontend/src/vite-env.d.ts`).
- Vite dev serves files outside `frontend/` via `/@fs` as long as they are inside
  the workspace root (the git root — true here); `vite build` copies the file into
  `dist/assets/` with a hash. Verify **both** `npm run dev` (fetch the URL with
  curl, confirm 200 + feature count) and `npm run build` (confirm the asset lands
  in `dist/assets/`). If dev-serving is blocked, add
  `server: { fs: { allow: [".."] } }` to `vite.config.ts` — do not copy the file.

### 2.2 Adapter (the core of Part 2)

Rewrite `frontend/src/lib/data.ts` to fetch `sitesUrl` **once** (module-level
cached promise) and derive all four legacy shapes from it client-side, so the
view components keep their existing prop types (`frontend/src/lib/types.ts`):

- **`fetchPlants(): PlantCollection`** — map each geojson feature to `MapProps`:
  `id` ← `npdes_id`, `name` ← `facility_name`, `state` ← `state_code`,
  `turbine` ← `turbine_type`, `rated_kw`, `energy_mwh` ← `annual_energy_kwh/1e3`
  (round 0), `payback` ← `payback_years` (round 2), `npv` ← `npv_usd`,
  `tier` ← `site_tier`, `viable` ← `project_viable`, `band` ← same thresholds as
  `export_web_data.viability_band` (<5 high, ≤15 moderate, ≤20 marginal, else
  nonviable), `confidence` ← same logic as `export_web_data.confidence`
  (`project_viable_high_confidence` or `data_quality=="dmr"` → High;
  `"dmr_limited"` → Medium; else Lower).
- **`fetchNational(): National`** — `plants_analyzed` / `scored_sites` from
  `meta`; everything else computed over the features: `viable_projects` = count,
  `tier_a_sites`, `high_confidence_sites`, Σ npv / capex / revenue, Σ energy MWh,
  median payback (1 d.p.), `by_state` sorted by viable count desc,
  `top_opportunities` = top 5 by npv.
- **`fetchPortfolio(state): Portfolio`** — filter features by state, sort by npv
  desc, build `TableRow`s (`flow_mgd` ← `mean_flow_mgd`, `annual_savings_usd` ←
  `annual_revenue_usd`, rank = 1-based index). Aggregates as in `National` but
  state-scoped. `n_scored`: no longer knowable from viable-only data — set it
  equal to `n_viable` and remove any UI text that implies a scored count
  (check `StatePortfolio.tsx`; currently it only displays `n_viable`, so this
  should be a type-level concern only). Unknown state → throw, so the existing
  "No portfolio data" error path still renders.
- **`fetchPlant(id): PlantDetail`** — find feature by `npdes_id`, populate the
  full `PlantDetail` shape: flow block (P1 fields), energy block
  (`p10/p50/p90_mwh` ← `energy_p*_kwh_yr/1e3`, `equivalent_homes`,
  `annual_kwh` ← `annual_energy_kwh`, `offset_pct` ← `energy_offset_pct`),
  elevation block (`facility_elev_m` ← `elevation_m`, `outfall_elev_m` ←
  `elev_outfall_m`, rest 1:1), turbine block (`rated_flow_m3s` ← `q_rated_m3s`),
  financial block incl. capex breakdown and
  `npv_with_grant_usd` ← `npv_with_50pct_grant_usd`, sensitivity block
  (`head/flow/rate` pairs + `dominant`), `dmr_backed` ←
  `data_quality ∈ {dmr, dmr_limited}`, `lat`/`lon` from geometry
  (remember GeoJSON order is `[lon, lat]`). Unknown id → throw (error path).
- `useAsync` stays as-is; the fetch functions keep their names and signatures so
  `NationalMap.tsx` / `StatePortfolio.tsx` / `PlantDetail.tsx` / `MapView.tsx`
  need **no changes** beyond the two below.

### 2.3 Two deliberate view fixes

1. **`NationalMap.tsx:29`** — change the null-payback branch to `return false;`
   (a viable site should always have a payback; belt-and-braces only).
2. Nothing else. Do not restyle, do not rename, do not "improve" components.
   The `nonviable` band stays in `colors.ts`/legend (it is now simply never
   populated) — removing it is Tom's call, not yours.

### 2.4 Frontend verification (paste output in report)

- `cd frontend && npx tsc -b --noEmit` (or the project's typecheck path) — clean.
- `npm run build` — clean; note the emitted geojson asset name + size.
- `npm run dev` in foreground long enough to `curl` the app root (200) and the
  `/@fs`-resolved geojson URL (200, then kill the dev server; no orphans).
- Node one-liner against `exports/viable_sites.geojson` reproducing the national
  KPI derivations (viable count, Σ npv, median payback) — values must match the
  Part 1.5 cross-check. This proves the adapter math is testable outside React.

---

## Acceptance invariants (all must hold; any miss = STOP + report)

1. `exports/viable_sites.geojson`: 1,138 features · 58 properties each · `meta`
   = {17,148 / 3,778 / baseline string} · byte-identical across two export runs.
2. Part 1.5 aggregate cross-checks within stated tolerances.
3. Full pytest suite ≥ 701 passed / 1 skipped, zero failures (new tests may push
   the passed count higher — state the final number).
4. `npm run build` + typecheck clean; dev server serves the geojson.
5. `data/processed/**` SHA-256 digests identical before/after.
6. `frontend/public/data/**` and `scripts/export_web_data.py` untouched
   (`git status` must show no changes there).

---

## Deliverables

1. Code: `scripts/export_geojson.py`, `tests/test_scripts/test_export_geojson.py`,
   `frontend/src/lib/data.ts`, `frontend/src/vite-env.d.ts` (or equivalent),
   `frontend/src/views/NationalMap.tsx` (one-line fix), `vite.config.ts` only if
   dev-serving required it.
2. Regenerated `exports/viable_sites.geojson`.
3. **`GEOJSON_UNIFY_REVIEW_PROMPT.md`** — written for Tom's reviewer (a separate
   Claude session with full repo access). It must contain:
   - A claims table: every numeric claim you make (feature count, property count,
     aggregate sums, test counts, build status) with the *exact* command a
     reviewer can rerun to verify each one from a clean checkout of your working
     tree — no reliance on your session state.
   - A "what I changed and why" file-by-file summary.
   - A "known limitations / judgment calls" section (e.g. the `n_scored`
     decision, tolerance rationale, anything you were unsure about).
   - A suggested review checklist ordered by blast radius (data correctness →
     exporter determinism → adapter math → build health).
   - Do NOT mark anything as verified that you did not verify with a pasted
     command output. The review prompt is the handoff artifact — Tom's reviewer
     checks the code and parquets, not your prose.

End your session by replying with the path to `GEOJSON_UNIFY_REVIEW_PROMPT.md`
plus your run report.
