# WOWERS Thesis Journal

Running log of thesis-writing sessions. One entry per work package drafted. This mirrors
`WOWERS_PROJECT_JOURNAL.md` but tracks the *paper*, not the code.

---

## ⚠️ INSTRUCTION FOR AI AGENTS — READ THIS FIRST

**RULE 0 — ONBOARD BEFORE WRITING.** Before drafting any part of the thesis, complete the
4-step onboarding at the top of `thesis/THESIS_BREAKDOWN.md` (read the project journal, skim
the repo, read `thesis/thesis_format_prompt.md`, read the breakdown). Do not write thesis
prose until you have done this.

**RULE 1 — ONE WORK PACKAGE PER SESSION.** Draft exactly one work package (e.g. `T1`, `M1`,
`J1`) from `THESIS_BREAKDOWN.md`. Do not batch multiple parts or write the whole thesis in
one pass. When that one part is done, stop.

**RULE 2 — LOG WHAT YOU WROTE.** At the end of every session where a work package was
drafted or revised, append a new entry to the Session Log at the bottom of this file, using
the exact structure below. Also update the checkbox and §7 status row for that work package
in `THESIS_BREAKDOWN.md`.

**RULE 3 — IDENTIFY THE AUTHOR.** Tag every session title with the owner of the work package
— `— Tom` for Track T packages, `— Mohamed` for Track M packages, `— Joint` for Track J
packages. If unsure who is at the keyboard, ask before logging.

**RULE 4 — NEVER REWRITE A PAST ENTRY.** Previous session entries are permanent records. Do
not modify, reformat, or delete them. If something needs correcting, note it in the NEW
entry only.

**RULE 5 — ONLY ADD TO THE BOTTOM.** New entries go at the very bottom of the Session Log,
below all previous entries.

### Session entry structure

```
### Session: YYYY-MM-DD — <WP id> <section name> — <Tom|Mohamed|Joint>

**Work package:** <e.g. T1 · Ch2 Background & Prior Work>

**What was drafted:**
- [what section(s) now have a first draft, and roughly how many words]

**Source artifacts used:**
- [every repo file, report, dataset, or external source the draft draws on]

**Figures / tables produced or specified:**
- [figure/table placeholders inserted, per the format's [FIGURE N] convention]

**Open items / follow-ups:**
- [anything left as TODO, e.g. missing citation, number to confirm, figure to build]

**Breakdown updated:**
- [confirm the §3 checkbox and §7 status row were ticked]

**Next work package suggested:**
- [which WP should be drafted next, per the §6 order]
```

---

## Section 0 baseline numbers (must be identical everywhere in the thesis)

Any draft that cites these must match exactly (P2-SEED re-baseline):

- POTWs screened: **17,148** → project-viable: **1,138**
- Physics ceiling: **409.2 GWh/yr** (409.17 GWh) · calibrated band: **119–281 GWh/yr**
- Portfolio NPV: **$310.1M** · CapEx: **$211.3M** · savings: **$41.2M/yr** · median payback:
  **9.8 yr**
- Exclusion funnel: 17,148 → 5,464 flow-valid → 4,860 head-valid → 3,778 scored → 1,138 viable

---

## Session Log

<!-- New entries go below this line, newest at the bottom. Do not edit entries above. -->

### Session: 2026-07-23 — T1 Ch2 Background & Prior Work — Tom

**Work package:** T1 · Ch2 Background & Prior Work

**What was drafted:**
- Full first draft of Chapter 2 in `thesis/thesis_tom.tex` (~2,280 words): opening + §§2.1–2.4
- §2.1 six numbered recovery limitations (unmeasured head, DMR corruption, river-CF misapplication, O&M/debris, site-by-site origination, economic opacity) each with quantified impact + citation
- §2.2 LucidPipe Portland (CF 0.628), Rentricity, CINK — what current practice catches vs misses
- §2.3 first-principles primer \(P=\eta\rho g Q H\), ECHO/ICIS + DMR + 3DEP + EHA scope
- §2.4 lit peak comparing DOE Hydropower Vision / ORNL NSD, HydroSource EHA CF, ORNL conduit/BCM, and WOWERS
- Seeded 14 IEEE-style `\bibitem`s used by Ch2 (J5 will still merge Track M/Joint refs later)

**Source artifacts used:**
- `WOWERS_PROJECT_JOURNAL.md` (turbine manufacturer research; LucidPipe / Rentricity / CINK; ORNL/HydroSource notes)
- `ENERGY_CONSUMPTION_RESEARCH_PLAN.md`, `ENERGY_CONSUMPTION_SOURCES.md` (EPRI 30.2 TWh, kWh/MG bands, offset sanity)
- `CF_CALIBRATION_REPORT.md` §§4–6 (WWTP vs river CF; LucidPipe anchor; 119–281 GWh band)
- `ARCHITECTURE.md` (pipeline/data sources overview)
- `thesis/thesis_format_prompt.md` §5 Ch2 rules (voice, numbered faults, lit density)

**Figures / tables produced or specified:**
- Table `\ref{tab:prior_work}` — scale/prior-work comparison (DOE Vision, EHA CF, ORNL conduit/BCM, WOWERS)
- Equation `\eqref{eq:hydro}` — \(P=\eta\rho g Q H\)
- No new figures this WP (figure inventory items are later Track T packages)

**Open items / follow-ups:**
- Several web/vendor citations (`lucidpipe`, `rentricity`, `cink`, `osti3002705`) need stronger primary PDFs / DOIs before final stitch (J5)
- ORNL national conduit potential PDF (Pub176069) not opened from disk this session — table cites TM-2014/525 + OSTI cost tables; may add the conduit-potential report as a fifth row later
- Confirm MONTH_YEAR / School of Engineering naming still outstanding (Section 0)

**Breakdown updated:**
- §3 T1 checkbox → `[x]`; §7 T1 status → ☑

**Next work package suggested:**
- T2 · Ch4.1 System Overview + Ch4.2 Data Acquisition (~1,600 w)

### Session: 2026-07-24 — T2 Ch4.1–4.2 Overview + Acquisition — Tom

**Work package:** T2 · Ch4.1 (draft w/ Joint) + Ch4.2 Data Acquisition

**What was drafted:**
- §4.1 System Overview (~400 w): public data → 4-phase pipeline → GeoJSON → dashboard; P2-SEED headline numbers; mandatory honesty paragraph (DEM head, Phase-5 kill, static GeoJSON UI, modeled CapEx/revenue)
- §4.2 Data Acquisition (~1,150 w): ICIS facilities/permits, DMR FY2009–24 (~279M rows), USGS 3DEP EPQS, EHA/EIA calibration labels — each with ≥3 options → choice → how built → named limitation
- Acquisition honesty close: 999.0 sentinels, GPD/MGD unit slips, primary-outfall corruption, P1-COORD-GUARD reject-don't-fix
- Total ~1,550 words for 4.1+4.2 (on target for ~1,600)

**Source artifacts used:**
- `ARCHITECTURE.md` §1 (ECHO/DMR schema, unit pitfalls)
- `src/phase1/ingest.py`, `filter_potw.py`, `dmr_timeseries.py`
- `src/phase3/elevation.py` (EPQS URL, cache, ocean sentinel)
- `src/phase5/ground_truth.py` (EIA-860/923 + EHA canonical schema, ≥1 MW bias)
- `config/settings.yaml` (`epa.*`, `usgs.elevation_url`, `processing.*`, `phase5.eha_data_dir`)

**Figures / tables produced or specified:**
- Figure 1 placeholder retained (system block diagram — still to be drawn)
- Table `\ref{tab:data_sources}` — data-source inventory (ECHO ICIS, DMR, 3DEP, EHA/EIA)

**Open items / follow-ups:**
- Draw Figure 1 for real (Joint / later figure-script session)
- §4.3.4 will expand the DEM-proxy-as-largest-assumption thread flagged here
- Confirm exact “~279M rows” wording still matches latest DMR ingest log if re-run

**Breakdown updated:**
- §3 T2 checkbox → `[x]`; §7 T2 status → ☑

**Next work package suggested:**
- T3 · Ch4.3 Processing Pipeline — Phases 1–2 (~2,200 w)

### Session: 2026-07-24 — Rule-compliance pass on T1/T2 drafts — Tom

**Work package:** Compliance edit (not a new WP) — apply new THESIS_BREAKDOWN rules to existing T1/T2 prose

**What was drafted:**
- Removed all `\cite{cf_calib}` / `\bibitem{cf_calib}` that pointed at internal `CF_CALIBRATION_REPORT.md`; calibration band and CF tiers now attributed as this work’s results, with external anchors kept as `\cite{hydrosource_eha}` / `\cite{lucidpipe}`
- Replaced silent Figure-1 box with `\figpending` marker: `[FIGURE 1 PENDING — awaiting upload: system block diagram]`
- Updated LaTeX helper so future placeholders use the PENDING wording required by the images rule

**Source artifacts used:**
- `thesis/THESIS_BREAKDOWN.md` (new RULE — never cite internal `.md`; RULE — images/figures)

**Figures / tables produced or specified:**
- Figure 1 now explicitly pending user upload / draw (cannot fabricate)

**Open items / follow-ups:**
- Need user to provide or approve Figure 1 (system block diagram)
- Future WPs must cite only external sources; project numbers reported as our findings

**Breakdown updated:**
- No WP status change (T1/T2 already ☑)

**Next work package suggested:**
- T3 · Ch4.3 Processing Pipeline — Phases 1–2 (~2,200 w), after Figure 1 is resolved or explicitly deferred

### Session: 2026-07-24 — Figure 1 system block diagram — Tom

**Work package:** Figure deliverable for T2 (was PENDING)

**What was drafted:**
- Generated real rendered Figure 1 (`thesis/figures/fig01_system_block.png`) from the architecture/journal dataflow and embedded it in §4.1 via `\includegraphics`
- Diagram shows: EPA ECHO + DMR → Phase 1; 3DEP → Phase 3; EHA/EIA → CF calibration side analysis; Phases 1–4 chain; Phase 5 ML killed (dashed); export_geojson → scored/viable GeoJSON → React+MapLibre static dashboard
- Added regenerator script `thesis/figures/make_fig01_system_block.py`

**Source artifacts used:**
- `ARCHITECTURE.md` phase dataflow; `scripts/export_geojson.py` (58-prop contract); project journal Phase 5 kill / CF calibration outcomes (read only, not cited)

**Figures / tables produced or specified:**
- Figure 1 — System block diagram of the WOWERS platform (embedded; no longer PENDING)

**Open items / follow-ups:**
- None for Figure 1

**Breakdown updated:**
- No WP status change

**Next work package suggested:**
- T3 · Ch4.3 Processing Pipeline — Phases 1–2 (~2,200 w)

### Session: 2026-07-24 — Figure 1 switched to self-contained TikZ — Tom

**Work package:** Figure 1 Overleaf paste-ability fix

**What was drafted:**
- Replaced `\includegraphics{...png}` with inline TikZ in `thesis_tom.tex` so pasting the `.tex` into Overleaf renders Figure 1 with no PNG upload
- PNG + regenerator kept under `thesis/figures/` as optional reference only

**Source artifacts used:**
- Same architecture/dataflow as prior Figure 1 session

**Figures / tables produced or specified:**
- Figure 1 now TikZ-native in the `.tex`

**Open items / follow-ups:**
- None

**Breakdown updated:**
- No WP status change

**Next work package suggested:**
- T3 · Ch4.3 Processing Pipeline — Phases 1–2 (~2,200 w)

### Session: 2026-07-24 — T3 Ch4.3 Processing Pipeline (Phases 1–2) — Tom

**Work package:** T3 · Ch4.3 Processing Pipeline — Phases 1–2

**What was drafted:**
- §4.3 opening (~150 w): pipeline responsibility, four-phase parquet-handoff structure, split of T3 (Phases 1–2) vs T4 (Phases 3–4), and the five-part subsystem shape used throughout
- §4.3.1 POTW Filtering and Flow Features (~900 w): flow-signal options (design scalar / DMR mean / 20-point FDC) and primary-outfall options (sum / max-mean / most-non-null non-CSO); build detail for `filter_potw.py` + `flow_features.py`; data-quality tier counts (11,555 dmr / 607 dmr_limited / 2,779 actual_avg_only / 2,207 design_only of 17,148); the per-reading-vs-aggregate outlier finding (435 sites nulled, median 110 months, 407 recovered, 20 correctly nulled); three named limitations
- §4.3.2 Composite Ranking (~450 w): three ranking options; weight table; min-max normalisation with 1e-12 guard, null→0 rather than mid-score, explicit-zero design flow zeroed (KYP000044) but null design flow left ranked (~2,106 sites); limitations — weights are judgment not fitted, score is fleet-relative, ranking is not a gate so weight error costs review order not exclusion
- §4.3.3 Monte-Carlo Energy Estimation (~950 w): three uncertainty options; triangular head/efficiency/availability sampling, trapezoidal FDC integration, vectorised 10,000×20 matrix, ProcessPoolExecutor; site-keyed seeding with the positional-seed failure reported in full (17,158→17,148 shifted seeds, 1,090 scorecards re-drawn, 3 viability flips); exclusion gate counts (1,496 / 10,182 / 6 → 5,464 retained); fleet P10/P50/P90 = 444.31 / 699.18 / 1,002.13 GWh/yr, median site 24,146 kWh/yr, median P90:P10 = 2.28; explicit paragraph separating the 699.18 GWh/yr screening intermediate from the 409.2 GWh/yr headline; four named limitations ending on the implausible implied CF (0.869 retained fleet, 0.872 viable cohort) that motivates §4.4 calibration
- Total ~2,360 words for 4.3–4.3.3 (target ~2,200)

**Source artifacts used:**
- `src/phase1/filter_potw.py`, `flow_features.py`, `ranking.py`, `run.py`
- `src/phase2/energy_physics.py`, `monte_carlo.py`, `head_assumptions.py`, `run.py`
- `config/settings.yaml` (`ranking.weights`, `ranking.fdc_exceedance_probs`, `physics.*`, `head_assumptions.*`, `phase2.min_viable_mean_flow_mgd`, `processing.*`)
- `EXCLUSION_FUNNEL_REPORT.md` (funnel cross-check only), project journal entries: W13 small-POTW filter (2026-05-20), DMR null-FDC bug + per-reading fix (2026-05-20), P2-SEED site-keyed seeding re-baseline (2026-07-06 PM#3)
- Live parquets for every reported statistic: `data/processed/phase1/ranked_candidates.parquet`, `data/processed/phase2/energy_yield_estimates.parquet`, `data/processed/phase4/financial_scorecards.parquet`
- No internal `.md` file is cited; the one new citation is external (EIA residential-consumption FAQ)

**Figures / tables produced or specified:**
- **Figure 2** — real rendered image `thesis/figures/fig02_mc_energy.png`, embedded via `\includegraphics`. Panel (a) = 10,000-sample MC energy distribution for PA0026280 (Lewistown STP) re-drawn with the production site-keyed seed 42, P10/P50/P90 = 15,528 / 24,173 / 34,951 kWh/yr; panel (b) = log-scale fleet distribution of per-site P50 energy for the 5,464 retained plants. Regenerator: `thesis/figures/make_fig02_mc_energy.py` (`PYTHONPATH=. python3 thesis/figures/make_fig02_mc_energy.py`)
- **Table 3** — Phase 1 composite ranking weights
- **Table 4** — Phase 2 head archetypes and triangular sampling parameters
- New `\bibitem{eia_household}` (EIA residential average 10,500 kWh/yr) for the equivalent-homes conversion

**Document-wide change made this session:**
- Figures and tables now number sequentially across the whole document (`chngcntr` + `\counterwithout`), per format §3.5/§7, instead of the LaTeX `report` default per-chapter numbering. Ch2/Ch4 references were all `\ref`-based, so nothing was hardcoded; renumbering verified in the compiled PDF (Table 1–4, Figure 1–2, appendix continues the sequence).

**Verification:**
- `tectonic -X compile thesis_tom.tex` succeeds; 0 errors, 0 unresolved `??` references, 34 pages. Remaining warnings are hbox over/underfull only.
- Every number in the draft was recomputed from parquet this session, not copied from a report.

**Open items / follow-ups:**
- Figure 2 is a PNG, so pasting `thesis_tom.tex` into Overleaf now requires uploading `figures/fig02_mc_energy.png` alongside it (Figure 1 remains TikZ-native).
- Head triangular archetypes are described honestly as engineering judgment; if a citable source for low-head gravity-outfall ranges is found, add it at J5.
- §4.3.3 forward-references §5.1.2 for the stage-by-stage decomposition of 699.18 → 409.2 GWh/yr; T6 must actually contain that decomposition.

**Breakdown updated:**
- §3 T3 checkbox → `[x]`; §7 T3 status → ☑

**Next work package suggested:**
- T4 · Ch4.3 Processing Pipeline — Phases 3–4 (~2,400 w): head estimation (DEM proxy as the largest methodological assumption), turbine selection, cost models and financial scorecard

### Session: 2026-07-24 — Document typography and front-matter formatting pass — Tom

**Work package:** Formatting pass (not a new WP) — page setup, pagination, TOC, figure layout

**What was changed:**
- Page setup set to graduate-thesis conventions after Tom's decision: `12pt` (was 11pt), `\doublespacing` via `setspace` (was single), and `left=1.5in, right/top/bottom=1in` binding margin (was `margin=1in`). Captions, `tabular` bodies, and `thebibliography` are held at single spacing via `\captionsetup{font=singlespacing}` and `etoolbox` `\AtBeginEnvironment` hooks.
- Front matter now uses lowercase roman pagination and the body restarts at arabic 1 (`\pagenumbering{roman}` after the title page, `\pagenumbering{arabic}` before Chapter 1). Previously the abstract was page 2 and Chapter 1 began on page 8.
- Abstract, Acknowledgements, List of Figures, and List of Tables are now listed in the Contents via `\addcontentsline`.
- Chapter lines in the TOC now carry dot leaders (`tocloft` `\cftchapleader`), per format §3.5; sections already had them.
- **Bug found and fixed:** loading `tocloft` suppresses the automatic page break before `\tableofcontents`, `\listoffigures`, and `\listoftables`. Contents was running on from the Acknowledgements page and List of Figures from the Contents page. Explicit `\clearpage` calls added; the front-matter lists are wrapped in `singlespace`.
- Figure 1 (TikZ) was re-laid out for the narrower 6.0 in text block: the Phase 5 "killed" box no longer overlaps Phase 4, the source row moved up so the CF-calibration box clears the EHA box, the pipeline band label moved beside the phase row instead of under the ECHO box, and the export row and config footnote moved down.
- Figure 2 regenerated at 9.0 × 3.7 in with 9–11 pt type so axis text stays legible at `\includegraphics[width=\linewidth]` instead of shrinking.

**Verification:**
- `tectonic -X compile thesis_tom.tex` → 0 errors, 0 unresolved `??`, 44 pages (was 34 at 11pt single-spaced).
- Front matter renders as title (unnumbered) → certification → Abstract ii → Acknowledgements iii → Contents iv–v → List of Figures vi → List of Tables vii → Chapter 1 page 1.
- Sequential numbering intact: Tables 1–4, Figures 1–3 (Figure 3 is the T6 exclusion-funnel stub).
- Pages rendered and inspected: front matter, Figure 1, Figure 2, and the Table 4 page.

**Open items / follow-ups:**
- `{{MONTH_YEAR}}` on the title page and the advisor name on the certification page are still placeholders (J5).
- Point size, spacing, and binding margin were chosen against common U.S. graduate-thesis practice; no University of St. Thomas School of Engineering format guide exists in the repo. If one is obtained, re-check these three settings first.
- Overfull-hbox warnings remain, mostly inside the red `\wptodo` stubs whose long underscore filenames cannot break; they disappear as work packages are written.

**Breakdown updated:**
- No WP status change

**Next work package suggested:**
- T4 · Ch4.3 Processing Pipeline — Phases 3–4 (~2,400 w)

### Session: 2026-07-24 — Figure 1 moved from inline TikZ to a rendered figure asset — Tom

**Work package:** Figure-pipeline change (not a new WP)

**What was changed:**
- Figure 1 (system block diagram) was inline TikZ drawn in `thesis_tom.tex`; it is now a rendered asset included the same way as Figure 2, so both figures come from `thesis/figures/` via `\includegraphics[width=\linewidth]`. The ~79-line `tikzpicture` block was deleted from the body (it remains in git history at commit 54a4d02 and earlier).
- New source of truth: `thesis/figures/fig01_system_block.drawio`, exported to `thesis/figures/fig01_system_block.pdf` with the draw.io desktop CLI (`drawio -x -f pdf --crop --embed-diagram`, draw.io 31.0.2). The export is true vector with embedded fonts, and `--embed-diagram` means the PDF carries its own editable XML.
- Diagram content is unchanged from the TikZ version (same four sources, four phases, CF-calibration side analysis, Phase 5 kill, export chain, config footnote). Two layout changes were made because orthogonal routing allows them: the four phase-to-export arrows are now drawn as one `*.parquet` bus instead of four crossing diagonals, and the tier labels sit in a left gutter clear of all edges. The one remaining edge crossing (CF calibration → Phase 2 over the 3DEP → Phase 3 feed) is drawn with an arc line-jump.
- The stale matplotlib version of this figure (`figures/fig01_system_block.png` + `make_fig01_system_block.py`) predates the 2026-07-24 re-layout and is no longer referenced by the document.

**Verification:**
- `tectonic -X compile thesis_tom.tex` → 0 errors, 0 undefined references, 44 pages (unchanged).
- Page 14 rendered and inspected: Figure 1 sits at the top of the page, caption below, legible at the 6.0 in text block; sequential figure numbering intact (Figure 1 in the List of Figures on page vi).
- Remaining warnings are the pre-existing over/underfull hboxes plus one new benign note from `xdvipdfmx`: the included PDF is version 1.7 while the output is set to 1.5.

**Open items / follow-ups:**
- Decide whether to delete `figures/fig01_system_block.png` and `figures/make_fig01_system_block.py`; they are dead once Figure 1 is the drawio asset.
- `\usepackage{tikz}` and `\usetikzlibrary{...}` are now unused in the preamble.
- Remaining diagram-shaped figures required by format §7 (application flow, state machine, core architecture, integrated + simplified block designs, two-lane operation flowchart, per-tool swimlane build flowchart, exclusion funnel) should be authored the same way, reusing this file's style values (fills `#EBEBEB` / `#DBDBDB` / white, stroke `#1A1A1A`, Helvetica) so all block diagrams match. Data charts stay in matplotlib.
- `graphviz` (`dot`) is not installed, so the drawio skill's `autolayout.py` is unavailable; the layout above is hand-placed, which is preferable for banded diagrams anyway.

**Breakdown updated:**
- No WP status change

**Next work package suggested:**
- T4 · Ch4.3 Processing Pipeline — Phases 3–4 (~2,400 w)

### Session: 2026-07-24 — T4 · Ch4.3 Processing Pipeline, Phases 3–4 — Tom

**Work package:** T4 — §4.3.4 Head Estimation, §4.3.5 Turbine Selection, §4.3.6 Cost Models and Financial Scorecard

**What was written:**
- §4.3.4 Head Estimation. Options considered were the Phase 2 archetype, the 3DEP elevation difference between plant and permitted outfall, and hydraulic computation from as-built drawings; the elevation proxy won on national availability and detectable failure. Documents the outfall-coordinate priority rules, the EPQS query and disk cache, the 0.15 loss fraction, and the four-branch plausibility gate (negative rejected, sub-1 m kept-but-invalid, divergence > 4× rejected, otherwise accepted). Flagged explicitly as the work's largest methodological assumption.
- §4.3.5 Turbine Selection. The H–Q decision tree, the five part-load efficiency curves with their caps, the rated-flow sweep under the 0.40 CF and 1 kW floors, and the manufacturer envelope match. Reports as a negative result that the sweep is nearly a no-op: 3,771 of 3,778 plants are rated at 100 % of design flow because the objective is energy rather than NPV.
- §4.3.6 Cost Models and Financial Scorecard. Power-law equipment cost with per-type clamps, the 17.5 % installation line (mechanical labour only, civil works excluded), behind-the-meter interconnection and conduit-NOI permitting tiers, OpEx as a share of equipment cost, and the 30-year DCF with the NPV/payback/real-IRR viability gate. Reports the vendor-band correction (1,019 of 3,783 → 0 flagged; +$7.2M honest CapEx), the rejection of the Ogayar-derived exponents for four of five machine types, the flat-BOS finding (a former $75,000 fixed overhead at 4.2× turbine cost), and the removed $20,000/yr revenue floor as a policy assumption that had been setting a headline result.

**Numbers — all recomputed live from parquet this session, none copied from a report:**
- Head: 5,464 into Phase 3 → 3,782 on 3DEP (69.2 %), 1,682 on archetype (30.8 %), 0 design fallback; head-valid 4,860; 604 sub-1 m readings kept but invalid (median 0.430 m). 3DEP valid head p10/p50/p90 = 1.617 / 4.144 / 12.217 m, max 40.647 m; archetype 2.772 / 4.695 / 7.230 m. Fallback attribution 1,203 negative / 286 no coordinate or elevation / 193 divergence.
- Turbines: 3,778 viable; Crossflow 2,765 (96.88 GWh/yr), Francis 454 (141.58), Kaplan 363 (269.08), in-conduit 196 (7.34), Pelton 0; total 514.87 GWh/yr; median rated 3.80 kW, p90 34.8 kW, max 2,644.2 kW; CINK 2,900 / Canyon 681 / Turbulent 113 / Emrgy 83 / Andritz 1. The 1,082 head-valid failures split 977 sub-1 kW (7 of them rounding-boundary) and 105 sub-0.40 CF.
- Economics: portfolio CapEx $353.5M = equipment $181.6M + installation $31.8M + interconnection $82.9M + permitting $57.2M; OpEx $4.08M/yr; `capex_outside_vendor_band` 0/3,778. Viable cohort (1,138): CapEx $211.3M, revenue $41.23M/yr, NPV $310.1M, median payback 9.83 yr, median IRR 9.40 %, median LCOE $0.0683/kWh, median $3,676/kW, median energy offset 2.016 %. Per-tier medians as in Table 8.
- Sensitivity: on the 848 viable sites carrying a measured FDC, base NPV $116.51M → −$17.27M at ×0.50 head and $250.29M at ×1.50; rate band $45.53M–$187.49M; flow band $75.73M–$133.55M. Head dominates at 2,803 of 3,778 sites.

**Figures and tables produced:**
- **Figure 3** `figures/fig03_head_estimation.png` — net head by source (log count axis, because the archetype takes three discrete values) plus the fallback-reason bars. Regenerator `thesis/figures/make_fig03_head_estimation.py`.
- **Figure 4** `figures/fig04_turbine_selection.png` — H–Q operating points against the selection boundaries, plus rated power by type. The archetype's three discrete heads are visible as horizontal stripes, which is a useful accident.
- **Figure 5** `figures/fig05_capex_vendor_band.png` — applied $/kW against the vendor envelope per machine type, with the unclamped power law and the clamps drawn. Typography enlarged after a first pass proved too small at `width=\linewidth`.
- **Figure 6** `figures/fig06_sensitivity_tornado.png` — portfolio NPV tornado plus dominant-input counts.
- **Tables 5–8** — head-source outcome; machine mix; equipment cost coefficients with anchoring; economics by permitting tier.
- All four regenerators run from the repository root as `PYTHONPATH=. python3 thesis/figures/make_figNN_*.py`.

**New citations (all external, verified):**
- `usgs_ned_accuracy` — Gesch, Oimoen & Evans, USGS Open-File Report 2014–1008. **Correction caught during drafting:** the commonly quoted 1.55 m RMSE for the national elevation data is not what this report gives. The overall absolute vertical accuracy is **2.44 m RMSE** against roughly 25,000 geodetic control points, verified by search before the number was used. This matters because head is a difference of two such elevations and the median accepted head is 4.144 m — the honest reading is that per-site head is an order-of-magnitude screen, not a measurement.
- `eia_rates` — EIA Electric Power Monthly Table 5.6.B, 2023 industrial averages (the provenance already recorded in `state_rates.yaml`).
- `ogayar2009` — Ogayar & Vidal, *Renewable Energy* 34(1):6–13, 2009, the source of the rejected equipment-cost fits.

**Verification:**
- `tectonic -X compile thesis_tom.tex` → 0 errors, 0 unresolved `??`, 56 pages (was 44). Zero overfull hboxes remain inside the T4 range after the four new tables were set at `\small` with trimmed outer padding and shortened tier labels; a first pass had four overfull tables and one overfull paragraph caused by an inline URL.
- Pages carrying Table 5, Figure 5 and Table 8, and Figure 6 were rendered and inspected; captions sit above tables and below figures, and sequential numbering is intact (Tables 1–8, Figures 1–6).

**Scope note — word count:**
- T4 came in at **3,452 words against the ~2,400 allotted**. Kept deliberately: T4 covers three subsystems rather than one, and the running total is 9,403 words against 8,600 planned for T1–T4, so the projected body lands near 22,700 words, inside the 18,000–24,000 window. Chapter 4 now holds 7,316 words and reaches the format's 9,000-word floor once M1 is merged. If the total later runs hot, §4.3.6's limitation paragraph and the cost-provenance narrative are the first candidates to cut.

**Open items / follow-ups:**
- The stale matplotlib Figure 1 assets (`figures/fig01_system_block.png`, `make_fig01_system_block.py`) are still on disk and unreferenced; `\usepackage{tikz}` is likewise now unused.
- §4.3.4 promises the head-error discussion that readiness-map item #3 asks for, but no per-site head error bound was computed — only the fleet-level RMSE argument. A real bound needs either surveyed outfall inverts or an NHD flowline-snap comparison.
- §4.3.6 forward-references §4.4 for the capacity-factor calibration; T5 must contain it.
- T6 must reproduce the 699.18 → 409.2 GWh/yr stage decomposition that §4.3.3 already promises, and its funnel numbers must match the 5,464 / 4,860 / 3,778 / 1,138 chain used here.

**Breakdown updated:**
- §3 T4 checkbox → `[x]`; §7 T4 status → ☑

**Next work package suggested:**
- T5 · Ch4.4 Calibration and Validation + Ch4.5 Export Layer (~2,000 w) — the implied-CF vs EHA-CF band, the Phase 5 ML kill as an honest negative result, and the 58-property GeoJSON contract

### Session: 2026-07-25 — T5 · Ch4.4 Calibration and Validation + Ch4.5 Export Layer — Tom

**Work package:** T5 — §4.4 opening, §4.4.1 Capacity-Factor Calibration, §4.4.2 Machine-Learning Feasibility, §4.5 Data Export and Serving Layer

**What was written:**
- §4.4 opening. States plainly that everything before it is modelled and that no WOWERS site has been instrumented, then frames the section as two attempts at comparison rather than as validation.
- §4.4.1 Capacity-Factor Calibration. Four options — direct measurement at an outfall, comparison against other modelled national assessments, re-tuning the Phase 2 sampling distributions, and benchmarking the implied capacity factor against measured plants. The fourth won because a published multiplier is reversible while a re-tuned distribution buries the correction inside the model. Documents the decomposition of the implied 0.8725 into availability 0.943 × flow-duration-curve utilisation 0.925, and separates the part that is real (flat municipal discharge) from the part that is optimistic (0.95 modal availability, no minimum-flow cutoff, no debris model). Then the recompute-and-clean method, the three EHA buckets, the LucidPipe anchor arithmetic, the band, and the three calibrated columns the band puts into the Phase 4 scorecard. Five named limitations, ending on the one that matters: this is calibration of a single scalar against somebody else's plants, not validation of any site in the portfolio.
- §4.4.2 Machine-Learning Feasibility. The Phase 5 kill written as a negative result against a gate fixed in advance (≥ 50 new usable labels). Records the sources searched and why each failed, the structural reason FERC cannot carry the labels (permitting system; generation is reported to EIA on Form 923, which is what EHA republishes), the 115 → 103 already owned → 11 genuinely new arithmetic, and the Point Loma correction, including that the first pass masked a plant offline since 2018 by selecting its latest non-zero year. Four reasons for the kill, then what survives: the rails, the leakage lock, and the smoke test whose metrics are deferred to §5.1.5 and labelled as having no product significance.
- §4.5 Data Export and Serving Layer. Four options — database plus API, four per-view JSON files, parquet-in-the-browser, one static GeoJSON with client-side derivation — and why the last won. Documents the join, the 58-property contract, RFC 7946 conformance (coordinate order, `meta` foreign member), the three rounding classes, the dual-file default write, the on-write validation, and byte determinism. Five named limitations: whole-file download at 6.13 MB, no schema version, the 10^6 payback sentinel, manual regeneration with no CI check, and lossy rounding that makes the file a reporting artefact rather than a reanalysis input.

**Numbers — all recomputed live this session, none copied from a report:**
- `scripts/cf_calibration.py` re-run end to end. Implied CF over the 1,138 viable sites: p10/p25/p50/p75/p90 = 0.8556 / 0.8651 / 0.8725 / 0.8810 / 0.8833 on a 409.2 GWh/yr headline. CF recompute vs the workbook string: n = 23,483, mean |diff| = 0.00250 (p25 0.00125, p75 0.00375).
- EHA buckets: 0.1–5 MW = 629 plants / 9,798 plant-years, p25/p50/p75 = 0.2535 / 0.3902 / 0.5409; 0.1–1 MW = 59 plants / 802 plant-years, 0.2676 / 0.4145 / 0.5457; 2013–2022 slice = 611 plants / 5,530 plant-years, p50 0.3817.
- Band on 409.2 GWh/yr: ×0.291 = 118.9, ×0.447 = 183.0, ×0.620 = 253.7, ×0.688 = 281.4 GWh/yr. Sub-bucket floors 125.5 and 194.4 GWh/yr. LucidPipe CF = 1,100,000 ÷ (200 × 8,760) = 0.6279.
- Phase 4 calibrated columns summed from parquet: viable cohort 119.07 / 182.90 / 281.51 GWh/yr against a 409.17 GWh/yr ceiling; all 3,778 scored 149.83 / 230.15 / 354.23 against 514.87.
- Ground-truth label set: 1,360 rows (1,268 EHA + 92 EIA), 250,643.66 GWh/yr measured, median installed 7,700 kW, range 100 kW – 6,495 MW, `actual_head_m` and `actual_flow_m3s` null in 1,360 of 1,360.
- Export: both tracked GeoJSON files re-exported to a scratch path and hashed. `viable_sites.geojson` 1,138 features / 1.85 MB / SHA-256 `f359b413…`; `scored_sites.geojson` 3,778 features / 6.13 MB / SHA-256 `420ad5f4…`. Two consecutive runs matched each other and matched the tracked files byte for byte. 58 properties on every feature, uniform key order, 0 features dropped for null coordinates, 823 payback sentinels in the scored file and 0 in the viable file, `meta` = {17148, 3778, P2-SEED re-baseline 2026-07-06}.
- Property-group counts in Table 10 were counted from `PROPERTIES` in the exporter, not estimated: 4 + 7 + 13 + 5 + 4 + 8 + 8 + 9 = 58, with the first three groups being the original 24.

**Figures and tables produced:**
- **Figure 7** `figures/fig07_cf_calibration.png` — measured EHA capacity factor against the modelled implied capacity factor as densities, with the LucidPipe and anchor lines, plus a p10–p90 spread panel for the three buckets and the WOWERS distribution. Regenerator `thesis/figures/make_fig07_cf_calibration.py`, which imports the loaders from `scripts/cf_calibration.py` so the figure cannot drift from the script.
- **Figure 8** `figures/fig08_calibration_band.png` — portfolio energy per tier with the capacity factor and multiplier written inside each bar, and the 0.1–1 MW variant marked. Regenerator `thesis/figures/make_fig08_calibration_band.py`.
- **Table 9** capacity-factor calibration band; **Table 10** GeoJSON property groups.
- Both regenerators need SANDISK mounted (they read the EHA workbook) and run from the repository root as `PYTHONPATH=. python3 thesis/figures/make_figNN_*.py`.

**New citations (all external):**
- `eia923` — EIA Form EIA-923 Power Plant Operations Report, cited for the claim that measured generation reaches the public record through EIA rather than FERC.
- `rfc7946` — Butler et al., IETF RFC 7946, for coordinate order (§3.1.1) and the `meta` foreign member (§6.1).
- `lightgbm` — Ke et al., NIPS 2017, for the estimator used in the smoke test.

**Environment note:**
- `fastexcel` (a declared dependency in `pyproject.toml`) was missing from the active interpreter, so `cf_calibration.py` could not read the EHA workbook. Installed `fastexcel 0.20.2` with pip; nothing else in the environment was touched. Anyone reproducing Figures 7 and 8 needs it.

**Verification:**
- `tectonic -X compile thesis_tom.tex` → 0 errors, 0 undefined references, 67 pages (was 56). Zero overfull hboxes inside the T5 range; the two that appeared on the first pass were fixed by setting Table 10 at `\footnotesize` with shorter examples and by wrapping the long calibrated-column names in `sloppypar`.
- Pages carrying Figure 7, Table 9, Figure 8, and Table 10 were rendered and inspected. Captions sit above tables and below figures and sequential numbering is intact (Tables 1–10, Figures 1–8, with the T6 funnel stub now Figure 9).

**Scope note — word count:**
- T5 came in at **3,269 words against the ~2,000 allotted** (§4.4 = 2,327, §4.5 = 942), after a trim pass that removed about 90 words of duplication. Like T4 it covers three subsystems rather than one. Chapters 1–6 now hold 12,847 words with T6, T7, M1, M2 and all four Joint packages still unwritten; at the remaining planned allotments that projects to roughly 25,100 words, which is **above the 24,000-word ceiling**. This needs a deliberate cut at J5 rather than drift: the first candidates are §4.3.6's cost-provenance narrative, the §4.4.1 capacity-factor decomposition paragraph, and §4.4.2's source-by-source hunt paragraph, which together are worth about 500 words without losing a required beat.

**Open items / follow-ups:**
- §4.4.1 forward-references §5.1.4 and §4.4.2 forward-references §5.1.5; T6 must contain both, and §5.1.4 must state what the band does to the Section 4.3.6 economics, which this section promises but does not do.
- The smoke-test metrics are marked internal in `SMOKE_TEST_REPORT.md`. They are reported in this thesis as a labelled pipeline proof with no product significance; if that framing is ever relaxed in §5.1.5 the internal marking should be revisited first.
- Figures 7 and 8 cannot be regenerated without the external drive. If the EHA bucket statistics are needed offline later, cache them to a small parquet under `data/` first.
- The 4 % gap between the 0.60 central anchor and the measured LucidPipe 0.628 is stated as a judgment. If a second real conduit or WWTP install with published annual energy is ever found, the anchor should be recomputed rather than kept.

**Breakdown updated:**
- §3 T5 checkbox → `[x]`; §7 T5 status → ☑

**Next work package suggested:**
- T6 · Ch5 Results (~3,000 w) — the parallel ideal-versus-expected tables, the 17,148 → 5,464 → 4,860 → 3,778 → 1,138 funnel with its selection-bias defence, the calibration result, and the machine-learning negative result
