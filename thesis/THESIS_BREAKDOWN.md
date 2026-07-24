# WOWERS Thesis — Work Breakdown & Ownership Plan

---

## ⚠️ AGENT — READ THIS FIRST BEFORE WRITING ANYTHING

You are helping write a Master's thesis one piece at a time. Do the onboarding, then draft
exactly one work package. Do not skip steps and do not batch multiple parts.

**STEP 1 — Understand the project.** Read `WOWERS_PROJECT_JOURNAL.md` (repo root) fully,
top to bottom. It is the complete decision trail for the whole project.

**STEP 2 — Understand the system.** Skim the rest of the repo so you can write about it
accurately: `ARCHITECTURE.md`, `src/phase1..phase5/`, `config/settings.yaml`, the
`*_REPORT.md` files (`CF_CALIBRATION_REPORT.md`, `EXCLUSION_FUNNEL_REPORT.md`,
`FERC_CONDUIT_LABEL_REPORT.md`, `SMOKE_TEST_REPORT.md`), `exports/*.geojson`, and
`frontend/src/`. You do not need to read every line — open what the work package you are
about to write lists under **Feeds**.

**STEP 3 — Learn the required format.** Read `thesis/thesis_format_prompt.md` fully. It
defines the mandatory skeleton, voice, tense, citation style, and figure/table rules. The
draft you produce MUST obey it (as remapped for software in §0 below).

**STEP 4 — Read this whole breakdown file** (§0–§7) so you know the ownership split, the
shared conventions (§5), and where your work package fits.

**RULE — ONE PART AT A TIME.** Write only a single work package per session (one row from
§3 / §7, e.g. "T1" or "M1"). Draft that section against the format, then STOP. Do not write
the next chapter, do not draft the whole thesis, do not offer to continue into other parts.
If the user did not name a work package, write the next unchecked one in §7 and confirm
which one you picked at the top of your reply.

**RULE — LOG WHEN DONE.** After finishing a work package you MUST do both:
1. In THIS file, tick that work package's checkbox in §3 and change its `☐` to `☑` in the
   §7 status table.
2. Append a session entry to `thesis/THESIS_JOURNAL.md` following the structure defined at
   the top of that file. Only append to the bottom; never rewrite a past entry.

---

> **Purpose.** Split the thesis defined by `thesis_format_prompt.md` into small,
> independently-writable work packages so no one has to draft the whole thing in one
> pass. Tom writes the data/backend track, Mohamed writes the frontend track, and the
> business + framing chapters are written jointly. Each work package (WP) is sized for
> roughly one sitting and lists exactly which repo artifacts feed it.
>
> **How to use.** Pick a WP, open the source artifacts listed for it, and write only
> that section against the shared conventions in §5. Tick the checkbox when a first
> draft exists. Do not start the "combine" work packages (Track J) until both technical
> tracks are drafted.

---

## 0. The one thing to read first — format is hardware-shaped, WOWERS is software

`thesis_format_prompt.md` was written for a hardware proof-of-concept (FPGA inference,
drone input, custom PCB, thermal and power-rail design). WOWERS has **no custom
hardware**. Do **not** invent PCB / thermal / power-routing chapters. Instead we keep the
*format's skeleton, voice, and honesty rules* and remap the hardware subsystems onto the
WOWERS software/data system. The remap is the table below. Everything else in the format
prompt (voice, tense, citation style, figure/table discipline, intellectual-honesty
habits) applies **unchanged**.

### Skeleton remap (format section → WOWERS content)

| Format skeleton section | WOWERS equivalent | Owner |
|---|---|---|
| 4.1 System Overview + block diagram | Whole-platform dataflow: public data → 4-phase pipeline → geojson → dashboard | Joint |
| 4.2 Input Acquisition Subsystem (hardware + SDK) | **Data Acquisition:** EPA ECHO/ICIS ingest, ~279M DMR rows, USGS 3DEP, EIA/EHA | Tom |
| 4.3 Data Transport Subsystem (protocols) | **Processing Pipeline:** Phase 1 filter/features/ranking, Phase 2 MC energy, Phase 3 head/turbine, Phase 4 cost/financials | Tom |
| 4.4 Core Compute Design (toolchain stages) | **Calibration & Validation:** CF-calibration band, Phase 5 ML kill (honest negative result) | Tom |
| 4.5 Custom Hardware Schematic Design | **Data Export / Serving Layer:** `export_geojson.py`, the 58-property data contract, determinism | Tom |
| 4.6 Custom Hardware Physical Design | **Frontend Visualization System:** React + MapLibre, 7 views, state/URL, build/deploy | Mohamed |
| 5.1.x per-subsystem results | Same order as Ch4: energy tables, funnel, calibration, negative result, then frontend perf | Tom + Mohamed |
| Appendix A: Bill of materials | **Data dictionary** (58 geojson props) + exclusion-funnel tables | Tom |
| Appendix B: Raw measurement captures | Calibration captures (implied-CF vs EHA-CF), sensitivity bands | Tom |
| Appendix C: Simulation output figures | Monte-Carlo P10/P50/P90 distributions | Tom |

**Keep the format's quirks:** flat-decimal numbering (`4.4.8`), Chapter 5 starts at
`5.1.1` (no `5.1`), figures captioned below / tables captioned above, technical half ≈
3× the business half.

---

## 1. Section 0 variables — pre-filled (confirm before drafting)

Fill these into the top of the eventual thesis. Draft values proposed from the repo:

| Variable | Proposed value |
|---|---|
| `COMPANY_NAME` | WOWERS |
| `THESIS_TITLE` | *WOWERS: A Proof-of-Concept Infrastructure-Intelligence Platform for National Screening of Micro-Hydropower Recovery at Wastewater Outfalls* |
| `AUTHORS` | XINSHENG (TOM) TANG · MOHAMED ABDEL HAMID |
| `UNIVERSITY` | University of St. Thomas |
| `SCHOOL_OR_COLLEGE` | School of Engineering *(confirm exact name)* |
| `DEGREE` | Master of Science |
| `MONTH_YEAR` | *(confirm — target defense month)* |
| `PROBLEM_DOMAIN` | Energy recovery at U.S. wastewater treatment plant (WWTP) outfalls |
| `CORE_TECHNOLOGY` | Public-data national screening + Monte-Carlo energy modeling + calibrated bounds |
| `DATA_SOURCE_HARDWARE` | *(N/A — replace with "public regulatory data": EPA ECHO/ICIS-NPDES, USGS 3DEP, EIA/EHA)* |
| `TARGET_METRICS` | 17,148 POTWs screened → 1,138 project-viable; 409.2 GWh/yr physics ceiling; **calibrated band 119–281 GWh/yr**; portfolio NPV $310.1M; median payback 9.8 yr |
| `TOTAL_LENGTH` | 18,000–24,000 words body |

---

## 2. Ownership tracks

Three tracks run in parallel, then merge:

- **Track T — Tom (data/backend).** Ch2 background, the whole Ch4 technical core except
  the frontend section, and Ch5 quantitative results. ~65% of body words.
- **Track M — Mohamed (frontend).** Ch4.6 frontend subsystem + its Ch5 results. ~12%.
- **Track J — Joint.** Ch1 intro, Ch3 business model, Ch6 conclusion, front matter,
  integration-test section, reference merge, and final stitch/honesty pass. ~23%.

> **Adjustable calls (change if you two disagree):** Ch2 background is assigned to Tom
> because it is technical/literature; Ch1 + Ch6 are Joint with Tom drafting first. If
> Mohamed would rather own the "current practice / competition landscape" reading, move
> §2.2 to him.

---

## 3. Work packages

Legend: **Words** = target draft length · **Feeds** = repo artifacts to open ·
**Fig/Tab** = deliverables to produce for §4 inventory.

### Track T — Tom (data / backend)

- [ ] **T1 · Ch2 Background & Prior Work** — ~2,400 w
  - **Feeds:** `WOWERS_PROJECT_JOURNAL.md` (turbine research, energy sources),
    `ENERGY_CONSUMPTION_RESEARCH_PLAN.md`, `ENERGY_CONSUMPTION_SOURCES.md`, ORNL national
    conduit assessment, `CF_CALIBRATION_REPORT.md` §4 (real installs).
  - **Beats:** 2.1 WWTP outfall energy loss + the failure/limitation modes as a numbered
    set; 2.2 current practice (LucidPipe Portland, Rentricity, CINK) — what exists, what
    it misses; 2.3 first-principles primer on hydropower screening (P = η·ρ·g·Q·H, public
    regulatory data); 2.4 the literature-review peak — prior national assessments,
    Monte-Carlo energy estimation, calibration against real capacity factors. **This is
    the biggest missing piece per the journal readiness map — expect real lit search.**
  - **Fig/Tab:** scale/prior-work comparison table.

- [ ] **T2 · Ch4.1 (draft w/ Joint) + Ch4.2 Data Acquisition** — ~1,600 w
  - **Feeds:** `ARCHITECTURE.md`, `src/phase1/ingest.py`, `filter_potw.py`,
    `dmr_timeseries.py`, `src/phase3/elevation.py`, `src/phase5/ground_truth.py` (EIA/EHA),
    `config/settings.yaml`.
  - **Beats:** where the data comes from (ECHO/ICIS, ~279M DMR rows FY09–24, USGS 3DEP,
    EIA/EHA); options considered per source; the acquisition honesty paragraph (999
    sentinels, GPD/MGD unit errors, coordinate corruption).
  - **Fig/Tab:** system block diagram (**Figure 1**, joint), data-source inventory table.

- [ ] **T3 · Ch4.3 Processing Pipeline — Phases 1–2** — ~2,200 w
  - **Feeds:** `src/phase1/flow_features.py`, `ranking.py`, `src/phase2/energy_physics.py`,
    `monte_carlo.py`, `head_assumptions.py`, `PHASE1_REPORT.md`, `PHASE2_REPORT.md`.
  - **Beats:** POTW filter + active-permit logic; flow-feature statistics; composite
    ranking (weights, min-max norm); Monte-Carlo energy engine (site-keyed seeding,
    P10/P50/P90). Options-considered → chosen → how-built → limitations for each.
  - **Fig/Tab:** ranking-weight table, MC distribution figure.

- [ ] **T4 · Ch4.3 Processing Pipeline — Phases 3–4** — ~2,400 w
  - **Feeds:** `src/phase3/head_estimation.py`, `outfall_coords.py`, `turbine_selection.py`,
    `data/turbines/turbine_manufacturers.csv`, `src/phase4/cost_models.py`, `financials.py`,
    `revenue.py`, `plant_consumption.py`, `sensitivity.py`, `EXCLUSION_FUNNEL_REPORT.md`.
  - **Beats:** head estimation (DEM proxy + plausibility gate — flag as **largest
    methodological assumption**, per readiness map); turbine matching rules; CapEx bands +
    install cost + ORNL BCM recalibration; NPV/IRR/payback; econ-category gradient.
  - **Fig/Tab:** turbine selection chart, CapEx-vs-capacity scatter w/ vendor bands,
    sensitivity tornado.

- [ ] **T5 · Ch4.4 Calibration & Validation + Ch4.5 Export Layer** — ~2,000 w
  - **Feeds:** `scripts/cf_calibration.py`, `CF_CALIBRATION_REPORT.md`, `src/phase5/*`
    (train/cv/features), `FERC_CONDUIT_LABEL_REPORT.md`, `scripts/export_geojson.py`,
    `exports/viable_sites.geojson` + `scored_sites.geojson`.
  - **Beats:** implied-CF vs EHA-CF calibration → the 119–281 GWh band (**strongest single
    element**); the Phase-5 ML **kill as honest negative result** (only 11 conduit labels
    found, Point Loma offline since 2018 — must be reported, not hidden); the 58-property
    geojson data contract + byte-determinism.
  - **Fig/Tab:** implied-CF vs EHA-CF overlay, calibration-band bar.

- [ ] **T6 · Ch5 Results — energy, funnel, calibration, negative result** — ~3,000 w
  - **Feeds:** all Phase-4 parquets, `EXCLUSION_FUNNEL_REPORT.md`, `CF_CALIBRATION_REPORT.md`,
    `SMOKE_TEST_REPORT.md`, `FERC_CONDUIT_LABEL_REPORT.md`.
  - **Beats:** **5.1.1 Ideal vs Expected** (two parallel tables: 409.2 GWh physics ceiling
    vs calibrated 119–281 GWh band — same columns, differing assumptions); exclusion funnel
    (17,148 → 5,464 → 4,860 → 3,778 → 1,138); calibration result + discrepancy paragraph;
    selection-bias defense (76.8% data-gap vs 16.5% economics); the negative ML result.
    **Every measured≠expected gap needs the mandatory discrepancy paragraph (§5).**
  - **Fig/Tab:** national site map, funnel diagram, ideal + expected tables, calibration table.

- [ ] **T7 · Appendices A–C** — ~800 w + tables
  - **Feeds:** geojson property list, funnel tables, sensitivity/MC captures.
  - **Beats:** data dictionary (58 props), funnel tables, MC/calibration raw captures.

### Track M — Mohamed (frontend)

- [ ] **M1 · Ch4.6 Frontend Visualization System** — ~2,000 w
  - **Feeds:** `frontend/src/` (App.tsx routing, `views/` × 7, `components/MapView.tsx`,
    `charts/`, `Gauge.tsx`, `SiteTable.tsx`, `lib/data.ts`, `colors.ts`, `csv.ts`,
    `vite.config.ts`), journal sessions 2026-07-06 PM#4/#5 + 2026-07-07.
  - **Beats:** what the frontend is responsible for; stack options considered (React +
    MapLibre + Vite + Recharts, TypeScript) and why; the single-file geojson data contract
    (`viable_sites.geojson?url`, no backend); the 7 views (NationalMap, StatePortfolio,
    PlantDetail, Opportunities, Plants, Analytics, Reports); client-side derivation of the
    four legacy shapes; URL-persisted filters; CSV export; interaction (zoom-to-state
    fitBounds, mini-map). Follow the same options→chosen→built→limitations shape.
  - **Fig/Tab:** app flow diagram (**Figure 2**), NationalMap screenshot description,
    PlantDetail screenshot description, view/route table.

- [ ] **M2 · Ch5 Frontend Results** — ~700 w
  - **Feeds:** journal 2026-07-06 PM#5 + 2026-07-07 verification notes, `npm run build`
    output.
  - **Beats:** build perf (vite 7.3.5, ~2.6 s, bundle sizes — maplibre 1.05 MB, index
    707 kB); headless + Chrome QA results; the discrepancy paragraph for the bundle-size /
    code-splitting deferral. Separate what was **measured** (build times, QA pass) from what
    is **deferred** (code-splitting, map clustering).
  - **Fig/Tab:** build/bundle size table, load-time note.

### Track J — Joint (business + framing + stitch)

- [ ] **J1 · Ch3 Business Model** — ~2,300 w *(this is "the business report part" you two discuss together)*
  - **Feeds:** `WOWERS_Project_Report.pdf`, `DIRECTOR_BRIEF_2026-06-24.md`,
    `WOWERS_Capital_and_Funding_Research.md`, Fowler feedback summary (journal), turbine
    manufacturer research (journal).
  - **Beats (8 subsections, 150–400 w each):** 3.1 problem + $ figure + 3 named
    complications; 3.2 the service; 3.3 one **real named** archetype plant (e.g. Stickney
    WRP or a real WWTP); 3.4 real competitors (LucidEnergy, Rentricity, CINK) + the gap;
    3.5 three price tiers + derivation sentence; 3.6 three marketing stages; 3.7 TAM→SAM→SOM
    arithmetic shown; 3.8 growth outlook + which milestone is built first.
    **Address the Fowler judge gaps here:** "why isn't this already done", logistics,
    named pilot, named government funding.

- [ ] **J2 · Ch1 Introduction** — ~1,100 w *(Tom drafts, both finalize)*
  - **Feeds:** `ARCHITECTURE.md`, journal overview, this file's §1.
  - **Beats:** macro trend + hard number; why current approach doesn't scale; "We propose
    the creation of a company, WOWERS, to…"; end-state workflow; split technical vs
    logistical development; 1.1 Thesis Statement; 1.2 Thesis Outline.

- [ ] **J3 · Ch6 Conclusions & Future Work** — ~900 w
  - **Beats:** what was designed/tested; restate headline metrics at full precision; three
    future-work themes — one Tom-side (validation ground truth / head-error analysis), one
    Mohamed-side (code-splitting, clustering, live backend), one joint (customer pilot);
    position as first step to customer value.

- [ ] **J4 · Ch5 Integration Test** — ~500 w
  - **Beats:** end-to-end: pipeline parquets → `export_geojson.py` → dashboard, with the
    P2-SEED baseline numbers matching across the boundary (1,138 viable / 409.17 GWh /
    $310.1M / 9.8 yr). Realistic stimulus = the real re-baselined parquets; say why that is
    representative.

- [ ] **J5 · Front matter + References merge + final stitch** — ~1,000 w + assembly
  - **Beats:** abstract (5 paragraphs, 350–450 w, per format §3.3); acknowledgements
    (advisor, business faculty, industry contacts); TOC / List of Figures / List of Tables;
    merge both tracks' reference lists into one IEEE-numbered list (target 40–50);
    renumber figures/tables sequentially across the whole doc; run the §5 honesty pass.

---

## 4. Figure & table master inventory (WOWERS-mapped)

Format demands ≥20 figures and ≥20 tables. Nearly all are derivable from current parquets
(journal readiness map: "~1 session with a figure script"). Assign as you draft:

**Figures (T = Tom, M = Mohamed):** 1 system block diagram (Joint) · 2 frontend app flow (M)
· 3–4 NationalMap + PlantDetail screenshots (M) · 5 pipeline dataflow (T) · 6 MC energy
distribution (T) · 7 national site map (T) · 8 exclusion-funnel diagram (T) · 9 implied-CF
vs EHA-CF overlay (T) · 10 CapEx-vs-capacity scatter w/ vendor bands (T) · 11 sensitivity
tornado (T) · 12 calibration-band bar (T) · 13 turbine selection chart (T) · 14–15 per-state
portfolio + analytics screenshots (M) · 16+ appendix figures (T).

**Tables:** data-source inventory (T) · ranking weights (T) · funnel counts (T) · ideal
system performance (T) · expected system performance (T) · calibration band (T) · CapEx
cost breakdown (T) · sensitivity NPV bands (T) · turbine spec matrix (T) · frontend
view/route map (M) · build/bundle sizes (M) · data dictionary / 58 props (T, appendix) ·
economics-by-tier (T).

> **Format rule:** every figure/table named in prose *before* it appears; tables captioned
> above, figures below; sentence-case captions, no terminal period.

---

## 5. Shared conventions (both writers follow — condensed from `thesis_format_prompt.md`)

So neither of you has to re-read the whole format prompt each session:

- **Voice:** "we" for decisions/results (*we designed*, *we measured*); passive for process
  (*the routing was done…*); present tense for how it works, past for what was done. Never
  second person.
- **Signpost:** end major sections with a forward pointer ("…will now be discussed";
  "see section 5.1.3").
- **Numbers:** space before unit (`409.2 GWh/yr`, `9.8 yr`); report at measured precision,
  do not round (`119–281 GWh`, `$310.1M`); show arithmetic where trust is otherwise
  required; label every assumption inline.
- **Specificity:** name every tool, version, source (`polars`, `vite 7.3.5`, `USGS 3DEP`,
  `EPA ICIS-NPDES`, `LightGBM`), never "a library".
- **Subsystem shape (every Ch4 section):** (1) what it's responsible for → (2) ≥3 options
  considered → (3) why the choice won → (4) how it was built (rebuildable detail) → (5)
  named limitations deferred to future work.
- **Discrepancy paragraph (mandatory in Ch5 wherever measured ≠ expected):** (a) state the
  gap numerically, (b) name the mechanism, (c) say if acceptable for current scope, (d)
  name the specific change that would close it.
- **Intellectual honesty (non-negotiable, and WOWERS is strong here):** state the
  proposal↔implementation gap early; separate **simulated/estimated** from **measured**
  everywhere; report the Phase-5 kill and the missing WWTP ground truth openly; frame the
  whole study as *screening with calibrated bounds, never validated prediction* (readiness
  map item #2); label all business numbers as estimates.

---

## 6. Suggested order & combine gate

1. **Parallel drafting.** Tom runs T1→T7; Mohamed runs M1→M2. Independent — no shared
   files, no blocking. Business (J1) can start any time you two sit down together.
2. **Framing after cores exist.** J2 (intro) and J3 (conclusion) read best once T + M
   drafts exist, so they can point accurately at real sections/numbers.
3. **Combine gate — do not start J4/J5 until both technical tracks are first-drafted.**
   Then: stitch, renumber figures/tables globally, merge references, write the abstract
   last (it summarizes finished content), run the §5 honesty pass end to end.
4. **Consistency check:** the P2-SEED baseline numbers (17,148 / 1,138 / 409.17 GWh /
   $310.1M / 9.8 yr) must be **identical** everywhere they appear across both tracks.

---

## 7. Progress at a glance

| Track | WP | Section | Owner | Words | Status |
|---|---|---|---|---|---|
| T | T1 | Ch2 Background | Tom | 2,400 | ☐ |
| T | T2 | Ch4.1–4.2 Overview + Acquisition | Tom | 1,600 | ☐ |
| T | T3 | Ch4.3 Pipeline P1–P2 | Tom | 2,200 | ☐ |
| T | T4 | Ch4.3 Pipeline P3–P4 | Tom | 2,400 | ☐ |
| T | T5 | Ch4.4–4.5 Calibration + Export | Tom | 2,000 | ☐ |
| T | T6 | Ch5 Results (energy/funnel/calib) | Tom | 3,000 | ☐ |
| T | T7 | Appendices A–C | Tom | 800 | ☐ |
| M | M1 | Ch4.6 Frontend system | Mohamed | 2,000 | ☐ |
| M | M2 | Ch5 Frontend results | Mohamed | 700 | ☐ |
| J | J1 | Ch3 Business Model | Joint | 2,300 | ☐ |
| J | J2 | Ch1 Introduction | Joint | 1,100 | ☐ |
| J | J3 | Ch6 Conclusion | Joint | 900 | ☐ |
| J | J4 | Ch5 Integration test | Joint | 500 | ☐ |
| J | J5 | Front matter + refs + stitch | Joint | 1,000 | ☐ |

**Total target:** ~21,900 words body (inside the 18,000–24,000 window; technical:business ≈ 3:1). ✅
