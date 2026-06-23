# WOWERS Dashboard — Front-End Implementation Plan

**Goal:** Build a web dashboard that displays the WOWERS portfolio analysis across three
views — a national opportunity map, a state/portfolio analysis page, and a per-plant
detail report — matching the supplied mockups.

**Owner:** Mohamed
**Branch:** `front-end`
**Status:** Planning complete. Not yet started.
**Created:** 2026-06-23

---

## 0. Locked decisions

| Decision | Choice | Rationale |
|---|---|---|
| Frontend stack | **React + Vite + TypeScript** (static SPA) | Matches the custom branded mockups exactly; deploys as static files (cheap/free hosting); handles 17k map points client-side. |
| Map provider | **MapLibre GL JS + free satellite tiles** (ESRI World Imagery) | No account, token, or usage billing. Near-identical look to the Mapbox mockup. |
| Data delivery | **Static pre-exported JSON / GeoJSON** | No live backend to build or host. The full dataset is small enough to ship as static files. |
| Data recovery | **Regenerate phases 3 & 4** (recovery not possible — see §1) | Prior outputs are unrecoverable; the pipeline must be re-run. |

---

## 1. Current-state findings (why this is two projects, not one)

The Python pipeline (phases 1–5) is mature — code complete, 427 tests passing — but **only
phases 1 and 2 have generated output on disk.** The dashboard depends heavily on phases 3 & 4,
which have code but **no persisted output**.

### What exists

| Phase | File | Rows | Key fields the mockups use |
|---|---|---|---|
| 1 ✅ | `data/processed/phase1/ranked_candidates.parquet` | 17,163 | `npdes_id`, `facility_name`, `city`, `state_code`, `zip`, `latitude`, `longitude`, `major_minor`, `design_flow_mgd`, `mean_flow_mgd`, `p10/p25/p75/p90_flow_mgd`, `n_months_data`, `data_quality`, `utilization_ratio`, `ranking_score`, `rank` |
| 2 ✅ | `data/processed/phase2/energy_yield_estimates.parquet` | 15,691 | `archetype`, `head_assumed_low/mode/high_m`, `power_p50_kw`, `energy_p10/p50/p90_kwh_yr`, `energy_mean_kwh_yr`, `capacity_factor_p50`, `equivalent_homes_p50` |

### What is missing (empty output dirs)

| Phase | Expected file | Provides |
|---|---|---|
| 3 ❌ | `data/processed/phase3/turbine_sizing.parquet` | net head, head source, facility/outfall elevation, **recommended turbine type**, rated power/flow, efficiency, `turbine_viable` |
| 4 ❌ | `data/processed/phase4/financial_scorecards.parquet` | **NPV, IRR, payback, LCOE**, equipment/install/interconnection/permitting CapEx, **annual savings/revenue**, viability tier, sensitivity, energy-offset % |

### Recovery investigation (result: not recoverable)

- `data/` is fully gitignored → phase 3/4 outputs were **never committed** to git history.
- No phase 3/4/5 checkpoints exist (only phase 1 in `data/checkpoints/`).
- The files exist **nowhere** in the Fowler OneDrive tree, Downloads, Desktop, or Documents.
- The DIRECTOR_BRIEF (Jun 24) cites real phase-4 numbers (1,141 viable, $353.5M CapEx), so a
  run happened — but on another machine/session and was not persisted here.

**Conclusion:** ~60% of the fields in the mockups (everything financial + turbine + elevation)
require **re-running phases 3 & 4** before the dashboard can show real data.

### Key risk: the elevation run

Phase 3 derives head from USGS 3DEP elevations (`https://epqs.nationalmap.gov`). The local cache
(`data/raw/elevation_cache`) is **empty (0 files)**, so a clean phase-3 run must make on the order
of **17k–34k rate-limited API calls** (facility + outfall coordinates). This is the single largest
time/reliability risk in the project. The cache persists once populated, so it is a one-time cost.

---

## 2. Field-by-field mapping (mockup → data source)

Legend: ✅ ready (phase 1/2) · 🔧 needs phase 3 · 💲 needs phase 4 · ⚙️ static/config · ❓ verify field exists

### Mockup A — National Map (landing)

| Element | Source |
|---|---|
| KPI: Plants Analyzed (17,158) | ✅ count of phase 1 |
| KPI: Viable Projects / Portfolio Value / Median Payback | 💲 phase 4 aggregates |
| Map markers (lat/long) | ✅ phase 1 |
| Marker color = viability band | 💲 phase 4 payback band |
| Marker popup: energy MWh/yr | ✅ phase 2 |
| Marker popup: payback, turbine | 💲🔧 phase 4 / 3 |
| Filter: State | ✅ · Turbine Type 🔧 · Payback slider 💲 · High-confidence ✅+💲 · DMR-backed ✅ (`data_quality`) |
| Top-5 Opportunities (name/city/energy) | ✅ + 💲 payback |
| "Viable Sites by State" bar chart | 💲 phase 4 viability counts |

### Mockup B — State Portfolio

| Element | Source |
|---|---|
| Header: N viable, combined NPV, $/yr savings | 💲 phase 4 |
| Table: Rank/Plant/City/Flow | ✅ · Turbine 🔧 · CapEx/Savings/Payback/NPV 💲 · Confidence ✅+💲 |
| "Annual Energy by Site" bar chart | ✅ phase 2 |
| "Risk vs Return" scatter (NPV vs payback) | 💲 phase 4 |
| Portfolio Summary sidebar (counts, totals, averages) | 💲 phase 4 |

### Mockup C — Plant Detail

| Element | Source |
|---|---|
| Header: name, city, NPDES, mean flow, confidence, DMR | ✅ phase 1 |
| Satellite thumbnail + marker | ✅ lat/long + map tiles |
| Energy Recovery gauge: P10/P50/P90 MWh/yr | ✅ phase 2 |
| Flow Data: mean/P10/P90, months DMR, utilization | ✅ phase 1 |
| Elevation: head source, net head, facility/outfall elev | 🔧 phase 3 |
| Recommended Turbine: type, rated power/flow, efficiency | 🔧 phase 3 · manufacturer ⚙️ config ❓ |
| Efficiency Curve | 🔧 phase 3 ❓ (may need to synthesize from turbine-type curve) |
| Financial Scorecard: NPV, IRR, payback, install cost, annual savings, lifetime | 💲 phase 4 · lifetime ⚙️ (30 yr) |
| Sensitivity tornado (head/flow/rate ±20% → NPV) | 💲 phase 4 `sensitivity.py` ❓ verify per-plant output |
| Next-steps buttons | ⚙️ static |

**Verification items (resolve during Pillar A):** efficiency-curve points per plant; per-plant
sensitivity tornado values; turbine manufacturer source; precise "confidence" definition
(map `data_quality` + viability tier → High/Medium/Lower).

---

## 3. Architecture

### Pillar A — Data layer

1. **Run phase 3** (`python -m src.phase3.run`) → `turbine_sizing.parquet`. Populates the
   elevation cache (the slow step). Verify `head_source`, `turbine_type`, `rated_power_kw`,
   `net_head_m`, `turbine_viable`.
2. **Run phase 4** (`python -m src.phase4.run`) → `financial_scorecards.parquet`. Uses
   `config/settings.yaml` install % (currently 17.5%). Includes the energy-offset column from
   this session's `src/phase4/plant_consumption.py`.
3. **Export script** `scripts/export_web_data.py` joins phases 1–4 and writes web artifacts:
   - `frontend/public/data/plants.geojson` — all plants as points; compact summary props for the
     map + filters (id, name, city, state, lat/lon, energy_p50_mwh, payback_years, npv_usd,
     turbine_type, viability_band, confidence, dmr_backed).
   - `frontend/public/data/portfolio/{state}.json` — per-state portfolio table + aggregates
     (loaded when entering a state view).
   - `frontend/public/data/national.json` — national KPIs + viable-by-state histogram + top-5.
   - `frontend/public/data/plants/{npdes_id}.json` — per-plant detail (lazy-loaded on detail view).

   Rationale: one global geojson for the map, per-state bundles for tables, per-plant files for
   detail — keeps every initial payload small and the whole thing backend-free.

### Pillar B — Frontend

```
frontend/
  index.html
  package.json            # vite + react + typescript
  src/
    main.tsx
    App.tsx               # router: / (map), /state/:code (portfolio), /plant/:npdes (detail)
    lib/                  # data fetching, formatting, types, color scales
    components/
      Shell.tsx           # sidebar nav + header (WOWERS branding)
      KpiTile.tsx
      MapView.tsx         # MapLibre GL, 17k-point geojson source, viability color
      FilterPanel.tsx
      DataTable.tsx       # sortable/filterable portfolio table
      charts/             # EnergyBar, RiskReturnScatter, Gauge, EfficiencyCurve, Tornado
    views/
      NationalMap.tsx     # Mockup A
      StatePortfolio.tsx  # Mockup B
      PlantDetail.tsx     # Mockup C
    public/data/...       # exported artifacts
```

- **Charts:** Recharts (bar, scatter, line/efficiency, horizontal-bar tornado) + a small custom
  SVG gauge for the energy-recovery dial.
- **Map:** MapLibre GL JS (via `react-map-gl/maplibre`), ESRI World Imagery raster basemap,
  single GeoJSON source with a circle layer colored by viability band; popup on click.
- **Routing:** React Router. Map → click plant → detail; state filter → portfolio.

---

## 4. Work breakdown

| # | Task | Output | Notes |
|---|---|---|---|
| A0 | Run phase 3 (elevation + turbine) | `turbine_sizing.parquet` | Slow — elevation API run |
| A1 | Run phase 4 (financials) | `financial_scorecards.parquet` | Confirm install % with Director first |
| A2 | Verify phase 3/4 fields vs §2 verification items | notes | Resolve efficiency-curve & tornado gaps |
| A3 | `scripts/export_web_data.py` | geojson + json artifacts | Backend-free data layer |
| B0 | Vite + React + TS scaffold, branding, shell/nav | running app shell | |
| B1 | National Map view (Mockup A) | map + KPIs + filters + top-5 + state chart | |
| B2 | State Portfolio view (Mockup B) | table + bar + scatter + summary | |
| B3 | Plant Detail view (Mockup C) | gauge, flow, elevation, turbine, scorecard, tornado | |
| B4 | Polish: responsive, Export-to-CSV, PDF/report, empty/loading states | | |
| B5 | Deploy (static host) | live URL | Netlify/Vercel/GitHub Pages |

Suggested sequencing: **A0–A1 in parallel with B0–B2** (build UI against phase 1/2 real data +
phase 3/4 placeholders), then A2–A3 to swap in real numbers, then B3–B5.

---

## 5. Risks & open items

1. **Elevation run** — 17k–34k rate-limited USGS calls; time + reliability. Mitigation: run once,
   cache persists; checkpoint; consider an overnight/background run.
2. **Pipeline reproducibility on this machine** — confirm phases 3/4 run clean here
   (dependencies, `settings.yaml`). 427 tests pass on logic, but a full run hasn't been verified.
3. **Mockup fields not guaranteed per-plant** — efficiency curve, sensitivity tornado, turbine
   manufacturer. Verify in A2; synthesize from config where the pipeline only emits a summary.
4. **Static payload size** — ~15k per-plant JSON files. Acceptable on static hosts (lazy-loaded);
   alternative is per-state detail bundles if file count becomes unwieldy.
5. **Map tile licensing/attribution** — ESRI World Imagery is free with attribution; keep the
   credit visible (as the mockup does).
6. **Install % pending Director** — phase 4 portfolio totals shift with the committed install %
   (15–20% band). Re-export after the value is locked.

---

## 6. What we can claim when this is done

> "An interactive dashboard over the full WOWERS analysis: a national map of all ~17,000 POTWs
> colored by investment viability, a state-level portfolio view with ranked opportunities and
> risk/return analysis, and a per-plant report card with energy recovery, recommended turbine,
> and a full financial scorecard — all generated from the EPA-data pipeline and served as static
> files."
