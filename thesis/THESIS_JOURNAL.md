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
