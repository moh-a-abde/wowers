# WOWERS Dashboard — Front-End Implementation Plan

**Goal:** Build a web dashboard that displays the WOWERS portfolio analysis across three
views — a national opportunity map, a state/portfolio analysis page, and a per-plant
detail report — matching the supplied mockups.

**Owner:** Mohamed
**Branch:** `front-end`
**Status:** Planning complete. **Data layer (phases 1–4) regenerated and verified** — ready to scaffold the frontend.
**Created:** 2026-06-23 · **Updated:** 2026-06-23 (post-regeneration)

---

## 0. Locked decisions

| Decision | Choice | Rationale |
|---|---|---|
| Frontend stack | **React + Vite + TypeScript** (static SPA) | Matches the custom branded mockups exactly; deploys as static files (cheap/free hosting); handles thousands of map points client-side. |
| Map provider | **MapLibre GL JS + free satellite tiles** (ESRI World Imagery) | No account, token, or usage billing. Near-identical look to the Mapbox mockup. |
| Data delivery | **Static pre-exported JSON / GeoJSON** | No live backend to build or host. The full dataset is small enough to ship as static files. |
| Data source | **Regenerated phases 3 & 4** (recovery was not possible — see §1) | Prior outputs were unrecoverable; the pipeline was re-run on this machine. |

---

## 1. Current-state findings

The Python pipeline (phases 1–5) is mature — code complete, 427 tests passing. When this
work began, **only phases 1 and 2 had output on disk**; the dashboard depends heavily on
phases 3 & 4, which had code but no persisted output. After confirming the outputs were
unrecoverable, **phases 2, 3 and 4 were regenerated** (phase 2 was also stale and had to be
re-run so its schema matched the current phase-3 code).

### Recovery investigation (result: not recoverable — so we regenerated)

- `data/` is fully gitignored → phase 3/4 outputs were **never committed** to git history.
- No phase 3/4/5 checkpoints existed (only phase 1 in `data/checkpoints/`).
- The files existed **nowhere** in the Fowler OneDrive tree.
- The DIRECTOR_BRIEF (Jun 24) cites real phase-4 numbers, so a run happened — but on another
  machine/session and was not persisted here.

### Regeneration outcome (the data layer is now complete)

| Phase | File | Rows | Status |
|---|---|---|---|
| 1 | `data/processed/phase1/ranked_candidates.parquet` | 17,163 | ✅ existing |
| 2 | `data/processed/phase2/energy_yield_estimates.parquet` | 17,163 | ✅ **regenerated** (added `excluded`, `head_m_p50` columns) |
| 3 | `data/processed/phase3/turbine_sizing.parquet` | 5,403 | ✅ **regenerated** (55 cols; 3,760 turbine-viable; 3,691 with USGS 3DEP head) |
| 4 | `data/processed/phase4/financial_scorecards.parquet` | 3,760 | ✅ **regenerated** (46 cols) |

**Headline portfolio numbers from the latest run:**
- 3,760 turbine-viable sites scored
- 1,177 investment-ready (Tier A) sites → 393 GWh/yr
- Median payback (viable): 9.9 years
- Total portfolio CapEx $331.5M; total revenue $46.2M/yr

**Fixes applied during regeneration:**
- Installed missing runtime deps into `.venv` (`httpx`, `requests`, `tqdm`, `pandas`, `pandera`, `numpy-financial`).
- Symlinked `data/raw/npdes_downloads/NPDES_PERM_FEATURE_COORDS.csv` → `extracted/…` so outfall
  coordinates load and **USGS 3DEP head calculation activates** (previously fell back to literature for all).
- The USGS elevation cache (`data/elevation_cache`) is now populated, so future phase-3 re-runs are fast.

---

## 2. Field-by-field mapping (mockup → data source)

All field names below are **verified against the regenerated parquet schemas.**
Legend: ① phase 1 · ② phase 2 · ③ phase 3 · ④ phase 4 · ⚙️ static/config.

### Mockup A — National Map (landing)

| Element | Source field(s) |
|---|---|
| KPI: Plants Analyzed | ① count |
| KPI: Viable Projects / Portfolio Value / Median Payback | ④ aggregates (`project_viable`, `total_capex_usd`, `payback_years`) |
| Map markers (lat/long) | ① `latitude`, `longitude` |
| Marker color = viability band | ④ `payback_years` band |
| Marker popup: energy, payback, turbine | ④ `annual_energy_kwh`, `payback_years`; ③ `turbine_type` |
| Filters: State / Turbine / Payback / High-confidence / DMR | ① `state_code`, `data_quality`; ③ `turbine_type`; ④ `payback_years`, `project_viable_high_confidence`, `data_quality_tier` |
| Top-5 Opportunities | ① name/city; ④ rank by `npv_usd` / `annual_energy_kwh` |
| "Viable Sites by State" bar chart | ④ per-state `project_viable` counts |

### Mockup B — State Portfolio

| Element | Source field(s) |
|---|---|
| Header: N viable, combined NPV, $/yr savings | ④ filtered aggregates |
| Table: Rank/Plant/City/Flow | ① `rank`, `facility_name`, `city`, `mean_flow_mgd` |
| Table: Turbine / CapEx / Annual Savings / Payback / NPV / Confidence | ③ `turbine_type`; ④ `total_capex_usd`, `annual_revenue_usd`, `payback_years`, `npv_usd`, `data_quality_tier`+`project_viable` |
| "Annual Energy by Site" bar chart | ④ `annual_energy_kwh` |
| "Risk vs Return" scatter (NPV vs payback) | ④ `npv_usd`, `payback_years`, `data_quality_tier` |
| Portfolio Summary sidebar | ④ aggregates |

### Mockup C — Plant Detail

| Element | Source field(s) |
|---|---|
| Header: name, city, NPDES, mean flow, confidence, DMR | ① `facility_name`, `city`, `npdes_id`, `mean_flow_mgd`; ④ `data_quality_tier`; ③ `head_source` |
| Satellite thumbnail + marker | ① lat/long + map tiles |
| Energy Recovery gauge: P10/P50/P90 | ② `energy_p10/p50/p90_kwh_yr` |
| Flow Data: mean/P10/P90, months DMR, utilization | ① `mean_flow_mgd`, `p10/p90_flow_mgd`, `n_months_data`, `utilization_ratio` |
| Elevation: head source, net head, facility/outfall elev | ③ `head_source`, `head_net_m`, `elevation_m`, `elev_outfall_m` |
| Recommended Turbine: type, rated power/flow, efficiency | ③ `turbine_type`, `rated_power_kw`, `q_rated_m3s`, `peak_efficiency_pct` |
| Efficiency Curve | ③ synthesize from turbine-type curve around `q_rated_m3s` / `peak_efficiency_pct` |
| Financial Scorecard: NPV, IRR, payback, install cost, annual savings, lifetime | ④ `npv_usd`, `irr`, `payback_years`, `installation_capex_usd`, `annual_revenue_usd`; ⚙️ lifetime (30 yr) |
| Sensitivity tornado (head/flow/rate → NPV) | ④ `sensitivity_head_npv_low/high`, `sensitivity_flow_npv_low/high`, `sensitivity_rate_npv_low/high`, `dominant_sensitivity` |
| Next-steps buttons | ⚙️ static |

**Confidence definition:** map `data_quality_tier` + `project_viable` / `project_viable_high_confidence`
→ High / Medium / Lower. **DMR-backed badge:** from ① `data_quality` / `n_months_data`.

---

## 3. Architecture

### Pillar A — Data layer ✅ (pipeline done; export step remains)

1. ~~Run phase 3~~ ✅ → `turbine_sizing.parquet` (elevation cache populated).
2. ~~Run phase 4~~ ✅ → `financial_scorecards.parquet` (includes energy-offset columns from
   `src/phase4/plant_consumption.py`).
3. **Export script** `scripts/export_web_data.py` (TODO) joins phases 1–4 and writes web artifacts:
   - `frontend/public/data/plants.geojson` — all viable plants as points; compact summary props
     for the map + filters (id, name, city, state, lat/lon, `annual_energy_kwh`, `payback_years`,
     `npv_usd`, `turbine_type`, viability band, confidence, `data_quality_tier`).
   - `frontend/public/data/national.json` — national KPIs + viable-by-state histogram + top-5.
   - `frontend/public/data/portfolio/{state}.json` — per-state portfolio table + aggregates.
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
      MapView.tsx         # MapLibre GL, geojson source, viability color
      FilterPanel.tsx
      DataTable.tsx       # sortable/filterable portfolio table
      charts/             # EnergyBar, RiskReturnScatter, Gauge, EfficiencyCurve, Tornado
    views/
      NationalMap.tsx     # Mockup A
      StatePortfolio.tsx  # Mockup B
      PlantDetail.tsx     # Mockup C
  public/data/...         # exported artifacts
```

- **Charts:** Recharts (bar, scatter, line/efficiency, horizontal-bar tornado) + a small custom
  SVG gauge for the energy-recovery dial.
- **Map:** MapLibre GL JS (via `react-map-gl/maplibre`), ESRI World Imagery raster basemap,
  single GeoJSON source with a circle layer colored by viability band; popup on click.
- **Routing:** React Router. Map → click plant → detail; state filter → portfolio.

---

## 4. Work breakdown

| # | Task | Output | Status |
|---|---|---|---|
| A0 | Run phase 3 (elevation + turbine) | `turbine_sizing.parquet` | ✅ done |
| A1 | Run phase 4 (financials) | `financial_scorecards.parquet` | ✅ done |
| A2 | Verify phase 3/4 fields vs §2 | confirmed schema | ✅ done |
| A3 | `scripts/export_web_data.py` | geojson + json artifacts | ⏭️ next |
| B0 | Vite + React + TS scaffold, branding, shell/nav | running app shell | |
| B1 | National Map view (Mockup A) | map + KPIs + filters + top-5 + state chart | |
| B2 | State Portfolio view (Mockup B) | table + bar + scatter + summary | |
| B3 | Plant Detail view (Mockup C) | gauge, flow, elevation, turbine, scorecard, tornado | |
| B4 | Polish: responsive, Export-to-CSV, PDF/report, empty/loading states | | |
| B5 | Deploy (static host) | live URL | Netlify/Vercel/GitHub Pages |

Suggested sequencing: **A3 first** (now that the pipeline is done), then **B0–B3** building each
view against the real exported data, then **B4–B5**.

---

## 5. Risks & open items

1. **Install % pending Director** — phase 4 portfolio totals shift with the committed install %
   (15–20% band; currently 17.5%). Re-run phase 4 + re-export after the value is locked.
2. **Static payload size** — ~3,760 per-plant JSON files. Acceptable on static hosts (lazy-loaded);
   alternative is per-state detail bundles if file count becomes unwieldy.
3. **Map tile licensing/attribution** — ESRI World Imagery is free with attribution; keep the
   credit visible (as the mockup does).
4. **Efficiency curve** — phase 3 emits a rated point (`q_rated_m3s`, `peak_efficiency_pct`), not a
   full curve; synthesize the curve shape per turbine type for the detail-page chart.
5. **Data freshness** — exported JSON must be rebuilt whenever the pipeline re-runs; wire the
   export into a Makefile / pipeline target.

## 6. Known data gap (non-blocking)

- **Turbine manufacturer name** (Mockup C "Canyon Hydro / CINK" line) requires a
  `data/turbines/turbine_manufacturers.csv` lookup that does not currently exist. Turbine *type*
  and sizing are unaffected. Build this lookup later if the field is wanted.

---

## 7. What we can claim when this is done

> "An interactive dashboard over the full WOWERS analysis: a national map of all ~17,000 POTWs
> colored by investment viability, a state-level portfolio view with ranked opportunities and
> risk/return analysis, and a per-plant report card with energy recovery, recommended turbine,
> and a full financial scorecard — all generated from the EPA-data pipeline and served as static
> files."
