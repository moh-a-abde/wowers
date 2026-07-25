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

### Session: 2026-07-25 — T6 · Ch5 Results — Tom

**Work package:** T6 — Chapter 5 lead-in, §5.1.1 Best Case and Expected System Performance, §5.1.2 Site Exclusion Funnel, §5.1.3 Energy and Financial Results, §5.1.4 Capacity-Factor Calibration, §5.1.5 Machine-Learning Feasibility

**What was written:**
- Chapter 5 lead-in. Names the only measured inputs in the whole work — DMR discharge records and 3DEP elevations — and states that everything downstream is modelled and no site has been built or metered.
- §5.1.1. The two parallel tables the format demands, identical columns, one assumption apart. Ideal is the pipeline under its own assumptions; Expected is the same 1,138 sites with energy at the 0.688 central calibration factor and every cash flow recomputed. Explains why the fleet capacity factor reads 0.7972 here and 0.8725 in §4.4.1 — different denominators, one against the Phase 3 rating and one against median-condition power at mean flow.
- §5.1.2. Funnel table and figure by count and by energy, the exclusion-class rollup, and the selection-bias answer. Contains the stage decomposition §4.3.3 promised: 699.18 → 641.90 → 619.32 → 514.87 → 409.17 GWh/yr, with the 104.44 GWh/yr step called out as a model change rather than a site drop.
- §5.1.3. Portfolio shape (concentration, tier split), per-site medians, the three-dimensional econ gradient across all 3,778 scored sites, and the two qualifiers on the viable cohort: 848 of 1,138 carry a measured flow duration curve, and 360 still carry the Phase 2 archetype head and hold 27.0 % of the portfolio energy.
- §5.1.4. The calibration as a result, plus a computation this work had not done before: re-scoring every site through the full 30-year cash-flow model at each calibration tier. Contains the discrepancy paragraph §4.4.1 and T5 promised.
- §5.1.5. The Phase 5 negative result with its metric table, the finding that LightGBM does not clearly beat a capacity-factor baseline, the leakage-guard demonstration, and the one-sentence transferable conclusion: the asset class lacks measured plants, not modelling capacity.

**Numbers — all recomputed live from parquet this session:**
- Funnel 17,148 → 5,464 → 4,860 → 3,778 → 1,138; drops 11,684 / 604 / 1,082 / 2,640; rollup 12,288 data gap (76.8 %), 1,082 physics floor (6.8 %), 2,640 economics (16.5 %) of 16,010.
- Energy chain 699.18 / 641.90 / 619.32 / 514.87 / 409.17 GWh/yr. Data-and-physics stages cost 79.86 GWh (11.4 %) while removing 30.9 % of sites; the Phase 3 re-estimate costs a further 104.44 GWh (16.9 %).
- Ideal table: 834 / 262 / 42 sites by tier; 9.16 / 23.16 / 26.26 MW; CF 0.8215 / 0.8098 / 0.7777; 65.95 / 164.30 / 178.91 GWh/yr; $6.32M / $16.12M / $18.79M revenue; NPV $27.01M / $93.92M / $189.21M. Totals 1,138 · 58.59 MW · CF 0.7972 · 409.17 GWh/yr · $41.23M/yr · $310.13M.
- Expected table (same sites, ×0.688, cash flows recomputed): CF 0.5652 / 0.5571 / 0.5350; 45.37 / 113.04 / 123.09 GWh/yr; NPV $0.40M / $26.09M / $110.16M; totals CF 0.5485 · 281.51 GWh/yr · $28.37M/yr · $136.65M, with 439 of the 1,138 still clearing the gate (261 / 136 / 42 by tier).
- Re-score at every tier through the real DCF (`compute_scorecard`, 3,778 sites per scenario): ceiling 1,138 sites / 409.17 GWh / $310.13M; central 439 / 213.80 / $152.64M; p50 floor 129 / 95.98 / $59.44M; p25 floor 27 / 30.01 / $19.03M. Median payback of the surviving cohort 9.83 / 10.39 / 10.73 / 10.57 yr.
- Viable-cohort medians: 12.96 kW, 93,350 kWh/yr, payback 9.8262 yr, IRR 9.40 %, LCOE $0.0683/kWh, CapEx $66,421, NPV $29,693, energy offset 2.0155 %. Concentration: top 10 sites 18.9 %, top 100 60.4 %, top 250 80.4 % of viable energy; the 42 full-licensing plants hold 43.7 % of energy and 61.0 % of NPV on 3.7 % of the sites.
- Cohort composition: 848 dmr / 165 design_only / 125 actual_avg_only; head 778 3DEP and 360 archetype, the archetype cohort holding 110.29 GWh (27.0 %); machines 654 Crossflow (47.48 GWh), 256 Kaplan (240.51), 228 Francis (121.18).
- Non-viable scored cohort: 2,640 sites, 105.70 GWh/yr, $142.18M CapEx, median rated 2.61 kW, median NPV −$11,305, 823 sentinel paybacks.
- Geography: 51 states and territories with viable sites, 54 scored. CA 147 sites / 67.98 GWh, NY 45 / 40.02, TX 102 / 38.95, IL 47 / 34.91, WA 7 / 20.32. Map frame excludes 52 scored (28 PR, 10 AK, 6 HI, 3 GU, 2 MP, 2 AS, 1 VI) of which 27 are viable.
- Smoke test re-run live (`python -m src.phase5.train`, seed 0) under **LightGBM 4.7.0**, versus 4.6.0 in the original run: rmse_log 0.9165 ± 0.0763, R² 0.7775 ± 0.0336, Spearman 0.9137 ± 0.0124, MAPE 987 % ± 1,353 %; mean baseline 1.9486 / −0.0012 / NaN / 4,263 %; CF baseline 0.9326 / 0.7703 / 0.9092 / 1,743 %. Every figure matched the recorded run to four decimals, so the determinism claim now holds across a LightGBM minor version. Leakage guard fired with the exact recorded message.

**Correction made to an earlier work package:**
- §4.3.6 (T4) described `$3,676/kW` as the viable cohort's "median all-in cost". It is the median **equipment** cost per kilowatt; `capex_per_kw` in the scorecard is the power-law equipment figure, not the four-component total. The all-in median is **$5,577/kW**. The sentence now reports both. No other number in T4 was affected — the portfolio totals were already computed from the four CapEx columns directly.

**Figures and tables produced:**
- **Figure 9** `figures/fig09_exclusion_funnel.png` — funnel by count with each drop coloured by class, plus the energy chain including the model-change step. Regenerator `thesis/figures/make_fig09_exclusion_funnel.py`.
- **Figure 10** `figures/fig10_national_map.png` — every scored plant at its permitted coordinate, marker area by rated power, plus the top-ten states by viable energy. No basemap is drawn; the site cloud is the map, so nothing is interpolated. Regenerator `thesis/figures/make_fig10_national_map.py`.
- **Tables 11–15** — ideal performance; expected performance; funnel with drop classes; portfolio re-scored at each calibration tier; smoke-test metrics.
- Figures 9 and 10 need only the repository parquets (unlike Figures 7–8, which need SANDISK).

**Environment note:**
- `scipy`, `lightgbm`, and `scikit-learn` were missing from the active interpreter and were installed with pip (scipy 1.18.0, lightgbm 4.7.0, scikit-learn 1.9.0). All three are declared in `pyproject.toml`. `fastexcel` was installed in the previous session for the same reason.

**Verification:**
- `tectonic -X compile thesis_tom.tex` → 0 errors, 0 undefined references, 75 pages (was 67). No overfull hboxes in the T6 range after the three new tables were set at `\footnotesize` with shortened headers.
- Pages carrying Tables 11–12, Figure 9, Figure 10, Table 14, and Table 15 were rendered and inspected. Sequential numbering intact: Tables 1–15, Figures 1–10.
- Every claim of the form "x % of y" in the chapter was checked against the recomputed totals; one first-draft figure (31.5 % of sites removed by the two data stages) was wrong and is now 30.9 %.

**Scope note — word count:**
- T6 came in at **2,224 words against the ~3,000 allotted**, which is under budget rather than over for the first time in Track T. Chapters 1–6 now hold 14,940 words including the remaining `\wptodo` stub text, with T7, M1, M2 and all four Joint packages unwritten. At the planned allotments that projects to roughly 23,800–24,200 words, so the body is now near but no longer clearly above the 24,000 ceiling. The J5 trim list from the T5 entry still stands as insurance.

**Open items / follow-ups:**
- §5.1.1 and §5.1.4 both lean on the re-score computation; it lives only in this session's scratch script. If the numbers are ever challenged, fold that script into `scripts/` as a read-only companion to `cf_calibration.py` so it is reproducible from the repository alone.
- §5.1.3 reports that 360 viable sites still carry the archetype head. T7's appendix should list them, or at least their count by state, so the claim is auditable.
- The smoke-test artefacts under `data/processed/phase5/models/` were overwritten by this session's re-run. They are gitignored and byte-equivalent in metrics; no action needed unless someone was relying on the 4.6.0 booster file.
- J4's integration test must not re-derive the funnel; it should assert the same 1,138 / 409.17 / $310.1M / 9.8 yr chain across the export boundary and cite §5.1.2 rather than repeat it.

**Breakdown updated:**
- §3 T6 checkbox → `[x]`; §7 T6 status → ☑

**Next work package suggested:**
- T7 · Appendices A–C (~800 w plus tables) — the 58-property data dictionary, the full funnel tables, and the Monte-Carlo and calibration captures. That closes Track T; Mohamed's M1/M2 and the Joint packages are then the remaining work.

### Session: 2026-07-25 — T7 · Appendices A–C — Tom

**Work package:** T7 — Appendix A (data dictionary + funnel tables), Appendix B (calibration and sensitivity captures), Appendix C (Monte-Carlo distributions). Track T is now first-drafted end to end.

**What was written:**
- **Appendix A.** Table 16 is the full 58-property data dictionary as a `longtable` that breaks across pages with a repeated header: property, type, units, rounding class, source phase, and null count over the 3,778 scored features. Prose flags the three entries a consumer can misread — the 10^6 payback/LCOE sentinel, the 974 plants with no flow percentiles, and the 225 with no outfall elevation. Table 17 is the funnel with the pipeline's own reason strings and the energy after each stage; Table 18 is the three-dimensional economic gradient in full; Table 19 distributes the 360 archetype-head viable sites by state, which closes the audit item T6 left open.
- **Appendix B.** Table 20 is the recomputed EHA capacity-factor distribution for all three buckets with the WOWERS implied row beneath it for comparison; Table 21 gives the calibration band from both buckets side by side; Table 22 is the sensitivity capture behind Figure 6, with the low/base/high portfolio NPV and the swing per input.
- **Appendix C.** Figure 11 plus Table 23. The closing paragraph is the one piece of new analysis in this work package: the P90:P10 band is uniform at 2.24–2.47× across the entire fleet and separates into exactly three clusters, because its width is set by the three head archetypes rather than by anything measured. Stated plainly — the Monte-Carlo band quantifies the head assumption, not the uncertainty of the estimate.

**Correction made to T6 (§5.1.2) — the funnel's exclusion classes were wrong:**
- The draft committed yesterday followed `EXCLUSION_FUNNEL_REPORT.md` in labelling all 11,684 Phase 2 drops a "data gap", giving a headline of "76.8 % of exclusions are missing data". That is not what the pipeline recorded. Phase 2 writes a reason string per excluded plant: **10,182 `small_potw`** (mean flow below the 0.5 MGD viability threshold), **1,496 `no_usable_flow`**, and **6 `sparse_dmr_artifact`**. Only the latter two are missing data; the first is a scope threshold that has flow records behind it.
- Corrected rollup over the 16,010 excluded sites: **scale threshold 10,182 (63.6 %), data gap 2,106 (13.2 %), physics floor 1,082 (6.8 %), economics 2,640 (16.5 %)**. The selection-bias argument survives and is now stated more precisely — 83.5 % of exclusions happened before any cash flow existed to reject — but the "76.8 % missing data" phrasing is retired.
- Fixed in three places: the §5.1.2 prose, Table 13, and Figure 9, whose Phase 2 bar is now split into a scale-threshold segment and a data-gap segment, with the split read from the parquet reason column rather than hardcoded. §4.3.3 (T3) already described the three-test gate correctly and needed no change.
- **`EXCLUSION_FUNNEL_REPORT.md` still carries the old rollup** and is used for director/pitch material. It is an internal artefact so the thesis does not cite it, but the number in it is misleading and should be corrected at source before it is quoted again.

**Numbers — recomputed live this session:**
- Data dictionary generated from `PROPERTIES` and the rounding sets in `scripts/export_geojson.py` plus a live null count per property over `scored_sites.geojson`; nothing hand-typed. Nulls: `city` 1, `p10_flow_mgd`/`p90_flow_mgd` 974 each, `utilization_ratio` 192, `elevation_m` 3, `elev_outfall_m` 225, everything else 0.
- Phase 2 exclusion reasons 10,182 / 1,496 / 6. Archetype-head viable sites 360 in 45 states holding 110.29 GWh/yr; CA 51 (13.88), PA 44 (11.82), WA 2 (9.38), MO 7 (6.78), TX 18 (6.36), IL 26 (6.01).
- Monte-Carlo fleet totals P10/P50/P90 = 444.31 / 699.18 / 1,002.13 GWh/yr; median plant 15,347 / 24,146 / 35,041 kWh/yr; P90:P10 ratio p10 2.243, median 2.276, p90 2.409, max 2.470; by archetype large 2.243 (919 plants), medium 2.275 (3,454), small 2.409 (1,091).
- Sensitivity capture on the 848-plant physical cohort: base $116.51M, head −$17.27M/$250.29M, rate $45.53M/$187.49M, flow $75.73M/$133.55M.

**Figures and tables produced:**
- **Figure 11** `figures/fig11_mc_bands.png` — per-site P10–P90 band on a log axis across all 5,464 retained plants, plus the histogram of band width. Regenerator `thesis/figures/make_fig11_mc_bands.py`.
- **Tables 16–23.** Table 16 is the document's first `longtable`; `longtable` was added to the preamble with a single-spacing hook so the 58 rows break cleanly with a repeated header.
- Figure 9 regenerated after the exclusion-class correction.

**Verification:**
- `tectonic -X compile thesis_tom.tex` → 0 errors, 0 undefined references, 80 pages (was 75). No overfull hboxes anywhere in the appendix range.
- Appendix A opening, the first dictionary page, and Appendix B were rendered and inspected. Sequential numbering runs unbroken into the appendix as the format requires: Tables 1–23, Figures 1–11.

**Scope note — word count:**
- T7 prose is **763 words against the ~800 allotted**, plus eight tables and one figure. Chapters 1–6 hold 15,020 words with M1, M2 and the four Joint packages unwritten; at their planned allotments the body lands near 23,500, inside the 18,000–24,000 window. Track T is complete and no longer at risk of pushing the document over.

**Open items / follow-ups:**
- Correct the "76.8 % data gap" rollup in `EXCLUSION_FUNNEL_REPORT.md`, or retire the file, before it feeds another pitch deck.
- Appendix A promises the dictionary is generated from the exporter; the generator script lives in this session's scratch directory only. Fold it into `thesis/figures/` (or `scripts/`) so the table can be regenerated when the contract changes.
- Table 19 lists the top twelve states and aggregates the remaining 33. If a reviewer wants the full list, it is one query away.
- The appendix has no bill-of-materials equivalent for the turbine vendor matrix; if the format's Appendix A expectation is read strictly, a vendor spec table could be added at J5 from `data/turbines/turbine_manufacturers.csv`.

**Breakdown updated:**
- §3 T7 checkbox → `[x]`; §7 T7 status → ☑

**Next work package suggested:**
- Track T is done. The remaining work is Mohamed's M1 (Ch4.6 frontend, ~2,000 w) and M2 (Ch5 frontend results, ~700 w), and the Joint packages J1–J5. Per §6 the combine gate holds J4 and J5 until both technical tracks are first-drafted, so the next Tom-side item is J1 or J2 with Mohamed, not another Track T package.

### Session: 2026-07-25 — J2 Ch1 Introduction — Joint (drafted by Tom)

**Work package:** J2 · Ch1 Introduction, §1.1 Thesis Statement, §1.2 Thesis Outline

**Note on process:** J2 and J3 were drafted in the same session at Tom's instruction, which departs from the one-work-package-per-session rule in `THESIS_BREAKDOWN.md`. They are logged as two entries. Both are short framing chapters that read as a pair, and both were written after Track T was complete so they point at real sections and real numbers rather than at intentions.

**What was written (~990 words against the ~1,100 allotted; format §5 asks for 900–1,200):**
- Opening on the macro trend with the hard number — 30.2 TWh/yr of POTW electricity use, about 0.8 % of national consumption, cited to EPRI rather than to any internal document.
- The scaling argument, which is framed deliberately: the constraint is not turbine technology or capital, it is the per-site cost of finding out. That framing is what makes a screening platform the product rather than an engineering service.
- The proposal paragraph in the format's required form, opening "We propose the creation of a company, WOWERS, to…".
- The end-state workflow as one paragraph walking the pipeline in order, written in the present tense as a description of the service rather than of this implementation.
- The technical-versus-logistical development split, with the logistical side naming customer discovery, the FERC conduit pathway, manufacturer relationships, municipal financing, and field validation — the four items the Fowler judges pressed on, so J1 has a hook to pick up.
- Closing sentence in the format's mandated wording.
- §1.1 Thesis Statement, one paragraph, stating the proposition as "commercially useful provided its uncertainty is stated rather than hidden", which is the honest form of the claim the rest of the document defends.
- §1.2 Thesis Outline, one paragraph walking Chapters 2–6 and the three appendices in order.

**Sources:** `ARCHITECTURE.md` for the pipeline order; Chapter 2 for the 30.2 TWh figure and its EPRI citation, kept consistent rather than re-derived; Chapters 4 and 5 for every number referenced. No new citations were needed.

**Verification:**
- `tectonic -X compile thesis_tom.tex` → 0 errors, 0 undefined references, 85 pages. No overfull hboxes in the Chapter 1 range; the two that report near it are pre-existing Chapter 2 boxes whose line numbers shifted.
- Chapter 1 opening page rendered and inspected.

**Open items / follow-ups:**
- ~~The intro claims a feasibility study "costs tens of thousands of dollars and takes weeks"~~ — **resolved 2026-07-25, same day.** A source search (small-hydro feasibility cost literature, ORNL cost models, USDA REAP feasibility-grant programme) produced no primary document stating a per-study cost or duration for small-hydro or conduit site assessment. The ORNL baseline cost models explicitly *exclude* licensing and financing from initial capital cost, and the REAP programme publishes grant caps rather than study costs, so neither supports the claim as written. Rather than attribute an unverifiable figure, the sentence was rewritten to drop the dollar and duration numbers entirely and rest the argument on this work's own measured result: the median viable site is a 12.96 kW machine at $66,421 all-in capital cost, so any per-site engineering assessment is a material fraction of the project it assesses. The scaling argument is unchanged and now carries no unsourced number. Ch1 is 1,056 words after the edit.
- §1.2 describes §4.6 and §5.1.6 as if they exist. They are Mohamed's M1 and M2 and are still stubs — the outline is correct about the finished document but will read oddly until those merge.

**Breakdown updated:**
- §3 J2 checkbox → `[x]`; §7 J2 status → ☑

**Next work package suggested:**
- J3 · Ch6 Conclusions (drafted in the same session; see the next entry)

### Session: 2026-07-25 — J3 Ch6 Conclusions and Future Work — Joint (drafted by Tom)

**Work package:** J3 · Ch6 Conclusions and Future Work

**What was written (~900 words, exactly the allotment; format §5 asks for 700–1,000):**
- Paragraph 1: what was designed and tested, then which MVP requirements it fulfils — screening, ranking, bounded estimate, delivery — and the one it does not: validation. Naming the unmet requirement in the first paragraph rather than the last is deliberate.
- Paragraph 2: the demonstration at full measured precision — 17,148 screened, the 5,464 / 4,860 / 3,778 / 1,138 chain, 58.59 MW, 409.17 GWh/yr, $211.33M CapEx, $41.23M/yr revenue, $310.13M NPV, 9.83 yr median payback, the 118.9–194.4 floor and 281.4 central band, and the re-scored 439 sites / $152.64M at the central tier. Ends on the sentence that the work stands behind the band and not its upper end.
- Paragraph 3: the three future-work themes in one sentence, then one paragraph each.
- Theme 1 (head): the sensitivity evidence (head dominant at 2,803 of 3,778 sites), the 2.44 m RMSE against a 4.144 m median head, the 360 archetype-head viable sites holding 27.0 % of portfolio energy, and three specific changes — NHD flowline snapping for the 1,203 impossible outfalls, a per-site error bound, and a surveyed sample to test for bias.
- Theme 2 (delivery): bundle splitting, marker clustering, a query service in place of the 6.13 MB static file, and a schema version on the contract. Written from the deferred items already on record so it does not depend on M2's numbers, which are not yet drafted.
- Theme 3 (validation): the 11-against-50 label result, Point Loma offline since 2018, and the single-pilot proposal — one instrumented outfall reporting head, flow, and generation for a year — stated as worth more than any further modelling.
- Closing paragraph positioning the work as the first step toward customer value, per the format.

**Verification:**
- Compile clean as above; no overfull hboxes in the Chapter 6 range. Every number restated in Chapter 6 was checked against Chapter 5 rather than retyped from memory.

**Open items / follow-ups:**
- Theme 2 is written without M2's measured build numbers. When M2 merges, check that the deferred items named here match the ones Mohamed reports as deferred, and add his figures if they sharpen the paragraph.
- Chapter 6 currently reads as Tom's conclusion. Mohamed should review the delivery-layer theme before J5, since it is his subsystem.
- The conclusion asserts the platform "now is" credible within named bounds. If a reviewer challenges any single claim in Chapter 5, this sentence is where it lands — worth re-reading last during the J5 honesty pass.

**Breakdown updated:**
- §3 J3 checkbox → `[x]`; §7 J3 status → ☑

**Next work package suggested:**
- J1 · Ch3 Business Model (~2,300 w) — needs both authors in the room. J4 and J5 remain gated on Mohamed's M1 and M2 per the §6 combine gate.

### Session: 2026-07-25 — Acronym expansion at first use — Tom

**Work package:** Editorial fix (not a new WP)

**What was changed:**
- The thesis never expanded WOWERS anywhere: not on the title page, not in Chapter 1, not in Chapter 2. Added the expansion at first use in the Chapter 1 proposal paragraph — "a company, WOWERS --- the Waste Outfall Water Energy Recovery System ---".
- Form used is **Recovery**, not Recovering. Tom stated the name as "Waste Outfall Water Energy Recovering System" in conversation, but every existing occurrence in the repository uses Recovery: `ARCHITECTURE.md:5`, `SETUP.md:3`, `pyproject.toml:8`, `config/settings.yaml:3`, and `WOWERS_PROJECT_JOURNAL.md:51`. Recovery is also the standard construction. Flagged to Tom; if the official Fowler-registered name really is Recovering, six occurrences change together, not one.

**Verification:**
- `tectonic -X compile thesis_tom.tex` → 0 errors, 0 undefined references, 85 pages.

**Open items / follow-ups:**
- J5 must carry the expansion into the abstract on first use there as well, since the abstract is read standalone. The title page keeps the bare acronym followed by the descriptive subtitle, which is conventional and needs no change.
- If a List of Abbreviations is ever added at J5, WOWERS, POTW, DMR, NPDES, FDC, EHA, and BCM are the candidates.

### Session: 2026-07-25 — Review-response editorial pass (spelling, figure order, em-dashes, LucidPipe citation, four new figures) — Tom

**Work package:** Editorial fix pass against a full-draft review (not a new WP). Five items were
scoped as fix-now; the rest were logged for J5 and are listed at the bottom of this entry.

**1. Spelling unified to US English.**
- Chapter 2 was American; Chapters 1, 3--6 and the appendices were British. The format prompt
  itself is written in US spelling (`labeled`, `summarizing`, `Organization`), and the degree is
  from a US university, so US was the target.
- 30 word families converted: metre(s), modelled/modelling, utilisation, artefact(s),
  programme(s), licence(s), honours, centreline, visualisation(s), normalised/normalisation,
  optimisation/optimiser/optimising, labelled, defence, fulfil, summarised, analysed,
  behaviour(s), authorised, levelised, maximising, pressurised, serialisation, vectorised.
- Two words that look British but are correct and were deliberately left alone: `optimism`
  (4 occurrences, not a British -ise form) and `exercised` / `supervised`.
- Verified no British form sat inside a `\texttt{}` literal, a `\label`, a `\ref`, or a URL
  before running the pass, so no code identifier was renamed. `sparse_dmr_artifact` was already
  US in code; the prose describing it in the funnel table said "artefact" and is now consistent
  with the identifier.
- BSD `sed` on macOS does not honour `\b`, so the first attempt silently changed nothing. The
  pass was redone in `perl -i -pe` with explicit word boundaries. Worth remembering for any
  future find-replace in this repo.

**2. LucidPipe citation replaced — and this turned out to be substantive, not cosmetic.**
The review flagged `\bibitem{lucidpipe}` ("project documentation and press materials; see also
thecivilengineer.org") as the weakest citation carrying the strongest claim. Chasing the primary
source found three separate factual problems in the draft, not just a formatting one:
- **Wrong project.** The draft called it the "Bull Run transmission main". The installation is the
  **Conduit 3 Hydroelectric Project**, FERC docket **P-14498**, on a pipeline at SE 147th Avenue
  and SE Powell Boulevard. Bull Run is a separate, much larger conventional hydro project. The
  wrong name was in the bibliography entry and in the Chapter 2 prose.
- **"Measured" was false.** The draft computed a *measured* capacity factor of 0.628 from
  1,100 MWh/yr ÷ 200 kW. Both numbers are design projections. The FERC application gives 170 kW
  nameplate and an estimated 1,200 MWh/yr; the as-built press figures are 200 kW and an expected
  1,100 MWh/yr. Every published figure is an expectation. There is no metered generation record
  because at 170--200 kW the plant is below the 1 MW threshold for Form EIA-923 reporting — which
  is the *same* reporting gap that killed Phase 5. Confirmed directly: searched
  `data/raw/ground_truth/combined_ground_truth.parquet` for "onduit", "ortland", "ucid",
  "ull Run" and for any Oregon plant under 300 kW. Nothing. The two Portland hits are Portland
  No. 1 and No. 2 at 23.7 MW and 11.8 MW.
- **The draft contradicted itself on the anchor margin.** Chapter 2 said CF 0.60 was "5 % below"
  0.628; Chapter 4 said "about 4 % below". The true figure is 4.46 %. The percentage framing is
  now gone, so the inconsistency goes with it.

Rewrite: the anchor is stated as a **range of 0.628--0.806** across the four filed/as-built
pairings, both endpoints labelled as design estimates rather than measurements, with the EIA-923
threshold given as the reason no measured value exists. **CF 0.60 is unchanged**, so no headline
number moved — 281.4 GWh/yr, 281.51, 136.65, 152.64 and every table all stand as drafted. The
justification is now that 0.60 sits below the *entire* documented range, which is a stronger and
more honest claim than sitting 5 % below a single false "measurement". Five passages were
rewritten (Ch 2 §2.1 twice, §2.2, §2.4, and Ch 4.4.1) plus the Ch 5 shorthand
"LucidPipe-anchored" → "Conduit 3-anchored".

Two bibitems replace the one: `ferc_p14498` (Federal Register vol. 78, no. 63, p. 19698,
2 April 2013 — a government primary source) and `lucidpipe` (D. Day, "Water pipe power: using
hydroturbines to harvest energy," *Treatment Plant Operator*, Oct. 2015 — a trade journal with a
real byline and date). Both carry `[Accessed 25 July 2026]`. Reference count 20 → 21.

**3. Figure order fixed.** `fig:cfcalib` (block preceded its first `\ref` by 8 lines) and
`fig:natmap` (by 8 lines) both moved below the naming paragraph. A scripted check now confirms
all 15 figures satisfy name-before-appear; `fig:mc_energy` was flagged by the review's grep but
was already correct — the pattern had missed the underscore in the label.

**4. Em-dash asides — scope was much smaller than the review reported.** The review counted
"dozens, 16 lines with 2+ pairs". That grep had counted `---` used as an empty-cell filler inside
`tabular` and `longtable` bodies, plus `%` comment rules and the `\newcommand` definitions. After
masking those out: **187 em-dashes across the document, but only 2 genuine prose paragraphs carry
two aside pairs, and no single sentence carries a nested aside at all.** Per Tom's decision
(convert nested/double only, accept single asides as a conscious deviation), both were converted
to parentheses: the WOWERS expansion in Ch 1 and the Phase 1--2 / Phase 3--4 pair in Ch 4.3. The
remaining single asides stand as an accepted, logged deviation from `thesis_format_prompt.md` §4.
**Note against the previous journal entry:** that entry recorded the WOWERS expansion as
`WOWERS --- the Waste Outfall Water Energy Recovery System ---`; it now reads
`WOWERS (the Waste Outfall Water Energy Recovery System)`. The expansion itself is unchanged and
the Recovery-vs-Recovering question raised in that entry is still open.

**5. Four new T-side figures built, all generated from the parquets rather than hard-coded.**
Figure count 11 → 15. Tables were already at 23.
- **Figure 12, `fig12_pipeline_dataflow.png`** — build-process flowchart, one swim lane per phase
  plus the export layer, each naming its modules, the parquet it writes, and the surviving count.
  Satisfies the format's mandatory build-process flowchart with per-tool swim lanes, and fills the
  "pipeline dataflow (T)" slot that BREAKDOWN §4 listed but the document never had. Placed in 4.1.
- **Figure 13, `fig13_site_state_machine.png`** — the mandatory state-machine figure, which nothing
  in the document previously satisfied. Named states along the retention spine, labelled
  transitions, and six terminal states carrying the pipeline's own reason strings. The script
  self-checks its arithmetic: 17,148 − 16,010 dropped = 1,138, matching Table `tab:funnel`
  exactly. Placed in 4.1.
- **Figure 14, `fig14_mc_by_tier.png`** — Appendix C second figure, so "Monte-Carlo Distribution
  Figures" is now plural. Keyed on `permitting_tier`, **not** `site_tier`: every one of the 1,138
  project-viable sites carries `site_tier = "A"`, so a site-tier split would have had no variance.
  Shows the three permitting tiers separated by about an order of magnitude in median energy per
  site (72 / 565 / 3,092 MWh/yr) and the count-against-energy inversion — 834 qualified-conduit
  sites are 73.3 % by count but 16.1 % of energy, while 42 full-NEPA sites are 3.7 % by count and
  43.7 % of energy. Tier energies sum to 409.16 GWh/yr against the 409.17 baseline.
- **Figure 15, `fig15_head_confidence.png`** — DEM head against archetype head, placed in 4.3.4 to
  make the "largest methodological assumption" visible instead of only asserted. This one earned
  its place by accident: the scatter resolves into **three vertical stripes**, because the
  archetype is indexed by design-flow band and therefore carries no site-specific information
  whatsoever. That reads as a stronger argument than a scatter cloud would have. 36.8 % of 3DEP
  estimates sit above the 1:1 line at a median ratio of 0.77×. Panel (b) reproduces
  Table `tab:head_outcome` exactly (3DEP n=3,178 at 1.617 / 4.144 / 12.217 m; archetype n=1,682 at
  2.772 / 4.695 / 7.230 m), which is a useful independent check that the table was right.

**Verification:**
- `tectonic -X compile thesis_tom.tex` → **0 errors, 0 undefined references, 0 undefined
  citations, 88 pages** (was 85; +3 from the four figures). List of Figures = 15 entries. All four
  new PNGs confirmed read by the engine.
- Only `tectonic` is installed on this machine — no `pdflatex`, `xelatex`, `lualatex` or
  `latexmk`. A `pdflatex` invocation exits 127 and leaves the previous log in place, which reads
  as a successful compile if you only check the log. Use `tectonic -X compile`.
- The long `tpomag` URL in the new bibitem initially overflowed the measure by 147 pt; wrapped in
  `\url{}` (hyperref is already loaded) and it now fits.
- The worst remaining overfull box, 189 pt at line 509, is pre-existing and lives inside the red
  `\wptodo` stub for J1 §3.4 — it disappears when the business chapter is written. The 126 pt box
  at line 941 is the unbreakable `\texttt{concurrent.futures.ProcessPoolExecutor}` token and is
  also pre-existing; left alone as cosmetic.

**Open items / follow-ups (deferred to J5 — logged here so they are not lost):**
- **Bibliography order violates "numbered by first appearance."** `epa2013` is [2] but is first
  cited near the end of Chapter 2, after sources numbered higher. Reorder all bibitems at merge
  time, after Mohamed's and the J1 references land — reordering before then would be wasted work.
- **`[Accessed DD Month YYYY]` missing on 7 web references** — `epa_echo`, `usgs_3dep`,
  `hydrosource_eha`, `rentricity`, `cink`, `eia_rates`, `eia923`. Deliberately not added this
  session: the dates should be re-verified at final stitch, not backdated now. The two new
  bibitems already carry theirs.
- **Reference count is 21 against a target of 40--50.** J1's business sources and Mohamed's stack
  citations have to carry most of that gap. **Flag to Mohamed now** so he collects citations while
  writing M1 rather than retrofitting them.
- **"P2-SEED" is used in 4.1 prose but never defined for the reader.** Either define the codename
  once at first use or say "the re-baselined 6 July 2026 run", which is how Chapter 5 phrases it.
- **4.3.1 and 4.3.2 end without a forward signpost**, against the §5 convention.
- **Four of the six limitation paragraphs in 2.1 do not end with a bracketed citation**, which the
  format asks for.
- **`{{MONTH_YEAR}}` placeholder still on the title page** (already tracked from an earlier
  session).
- **Figure count will be ~20 only if Mohamed delivers ~5.** Currently 15 T-side and Joint. His
  planned set is app flow diagram, NationalMap and PlantDetail screenshots, and per-state
  portfolio and analytics screenshots. If M1 ships fewer than 5, the shortfall lands back on
  Track T, and the cheapest remaining T-side additions would be a per-state choropleth and a
  CapEx-breakdown stacked bar. Worth telling Mohamed the count is load-bearing.

**Breakdown updated:**
- No work-package checkbox changed — this was an editorial pass, not a new WP. BREAKDOWN §4's
  figure inventory is now understated (it predates Figures 12--15); refresh it at J5 when figures
  are renumbered globally.

**Next work package suggested:**
- Unchanged from the previous entry: J1 · Ch3 Business Model (~2,300 w), needs both authors.
  J4 and J5 stay gated on M1 and M2 per the §6 combine gate.

### Session: 2026-07-25 — Calibration tier re-label: CF 0.60 demoted to optimistic, measured conduit tier added — Tom

**Work package:** Editorial + evidential revision to §4.4.1 and its dependents (not a new WP).
Follows directly from the LucidPipe citation fix logged in the previous entry, which exposed
this. Full code-side detail is in `WOWERS_PROJECT_JOURNAL.md` under the same date.

**Why this was needed.** The previous entry replaced a weak citation with two sound ones and
relabeled the Conduit 3 figures as projections. That fixed the citation but left the argument
standing on it: the calibration band's upper tier, CF 0.60, was still called the "plausible
central estimate" of the whole thesis while resting on one project's design projection. Then
`data/raw/ground_truth/ferc_conduit_candidates.parquet` turned out to hold 115 Canal/Conduit
plants with **metered** EIA-923 generation — gathered for the Phase-5 label hunt and rejected
there on newness, which is the right test for ML training data and the wrong one for a
capacity-factor benchmark. Their median CF is 0.2439, and the four plants carrying continuous
municipal or wastewater duty run 0.0242 / 0.1584 / 0.1914 / 0.3690. Point Loma, the only
metered treated-wastewater conduit plant in the country and thus the closest analog this
thesis has, sits at 0.1914.

**Decision recorded: re-label, do not re-center.** CF 0.60 stays at 0.60. Re-centering on the
measured figures was considered and rejected — n=4 for the on-point analogs, the Badger value
(297 MWh from 1,400 kW) looks like a partial or curtailed reporting year, and the seasonality
objection is legitimate for the 111 irrigation canals in the set. Re-centering on n=4 would
repeat the n=1 error at a different number. **No headline number moved**, and this was verified
rather than assumed (below).

**What changed in the draft:**
- **§4.4.1 — three new paragraphs** after the Conduit 3 passage: the metered evidence with all
  four plants named and valued; then the three consequences, written so they do not all point
  the same way (floor corroborated / upper tier unsupported / comparison genuinely not like for
  like at 500 kW minimum against a 12.96 kW median site); then the retention-and-relabel
  paragraph stating the design argument for 0.60 and calling it plausible and untested.
- **`tab:cfband` — two measured rows added** (Point Loma 0.1914 → 89.8 GWh/yr; all conduit
  0.2439 → 114.4) and the tier renamed "Central, WWTP-appropriate" → "Optimistic, Conduit 3
  proj." Footnote now says which rows rest on metered generation and which do not. The 0.1914
  row is labeled "Point Loma (WWTP)" and not "municipal conduit" on purpose: polars'
  nearest-rank quantile makes the 4-plant median coincidentally 0.1914 too, and attributing a
  single plant's value to a group median would have been misleading.
- **Limitation 2 of §4.4.1** now names the four metered municipal plants and their range, so
  the limitation carries the counter-evidence rather than only conceding thinness.
- **§2.1 and §2.4** — "central tier" → "optimistic upper tier", each with a forward pointer to
  the §4.4.1 measured benchmark.
- **§5.1.4** — the substitution paragraph now reports the 114.4 GWh/yr metered landing beside
  the 118.9 floor and states that the floor is the tier the chapter treats as evidenced.
  `tab:rescore` row renamed. The closing sentence, which read "the defensible planning figure
  is the central tier", was **directly contradicted** by the re-label and now reads that the
  defensible planning figure is the floor, with 281.4 as the ceiling of plausibility.
- **`tab:expected`** — caption and footnote now say "optimistic-tier", and the footnote points
  to `tab:rescore` for the floor-tier outcomes. Worth flagging: the format requires an
  "Expected system performance" table, and that table is built on the 0.688 multiplier, so
  after this re-label the format's "expected" case is this thesis's optimistic case. Resolved
  by labeling it explicitly rather than by moving numbers. **If the band floor is ever lowered,
  this table is the one that has to be rebuilt.**
- **Ch6** — "plausible central estimate" → the corroborated floor plus an optimistic upper
  scenario. The existing closing sentence, "the headline this work stands behind is the band
  and not its upper end", needed no change; Ch4 and Ch5 now match the posture it already had.
- **Appendix B — new `tab:conduit_measured`** with the four metered plants, the 115-plant
  quartiles, the Pearson r, and the smallest-quartile median, plus the Badger caveat.

**Verification:**
- `tectonic -X compile` → **0 errors, 0 undefined references, 0 undefined citations, 91 pages**
  (was 88; +3 from the new prose and table). Figures still 15, tables now 24.
- **No headline number moved.** Counted every key figure in the draft against `git show HEAD`:
  409.17, 409.2, 281.51, 310.13, 152.64, 136.65, 9.83, 58.59, 211.33, 17,148 all identical.
  281.4, 118.9, 194.4 and 1,138 rose in *count* only, from new prose referencing them; no
  occurrence changed value and no count fell.
- Every new number was taken from `scripts/cf_calibration.py` output, not transcribed by hand,
  and then re-checked: 409.2 × 0.2439/0.8725 = 114.39 → 114.4; × 0.1914/0.8725 = 89.77 → 89.8;
  floor agreement 118.9 − 114.39 = **4.51 GWh/yr**.
- `data/`, `config/`, `src/` confirmed untouched — `settings.yaml` multipliers 0.291 / 0.447 /
  0.688 unchanged, so no re-export and no geojson change. The three
  `energy_kwh_calib_*` property names were deliberately **not** renamed; they are part of the
  frozen 58-property contract and only the prose labels moved.

**Open items / follow-ups:**
- **Deferred decision, needs Tom + advisor:** whether to lower the reported band floor from
  118.9 to the 89.8 GWh/yr Point Loma implies. Argued both ways in §4.4.1 on purpose. If taken
  it is one line in `settings.yaml` plus a re-export, and `tab:expected` must be rebuilt.
- The abstract (J5) must describe the band as floor-plus-optimistic-scenario, not
  floor-plus-central-estimate. It is unwritten, so this is a constraint on J5 rather than a fix.
- Ch6's pilot-outfall future-work theme is now the thing that would resolve the weakest link in
  the headline. Worth sharpening that paragraph at J5 to say so explicitly.
- `CF_CALIBRATION_REPORT.md` is stale (old project name, "measured 0.628", central framing). It
  is an internal artifact and never cited, so it cannot leak into the thesis, but it should be
  annotated so the error is not reintroduced from it.
- All deferred items from the previous entry still stand: bibliography reordering, `[Accessed]`
  dates on 7 web refs, reference count now 21 against 40–50, "P2-SEED" undefined in 4.1,
  missing signposts in 4.3.1/4.3.2, 2.1 limitation citations, `{{MONTH_YEAR}}`, and the figure
  count depending on Mohamed delivering ~5.

**Breakdown updated:**
- No checkbox changed; this was a revision to already-drafted T5 and T6 content.

**Next work package suggested:**
- Unchanged: J1 · Ch3 Business Model, needs both authors. J4 and J5 stay gated on M1 and M2.
