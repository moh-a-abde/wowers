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
