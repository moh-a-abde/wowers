# WOWERS Project Journal

---

## ⚠️ INSTRUCTION FOR AI AGENTS — READ THIS FIRST BEFORE DOING ANYTHING

**RULE 1 — READ BEFORE YOU RESPOND:**
Read this entire file from top to bottom before responding to anything. The session log at the bottom tells you exactly what has been done and what comes next. Do not skip this step.

**RULE 2 — NEVER TOUCH EXISTING CONTENT:**
Do NOT modify, rewrite, reformat, correct, or delete any content that already exists in this file. This includes previous session entries, project descriptions, team info, technical facts, or any other section. What is written stays written exactly as it is.

**RULE 3 — NEVER REWRITE A PAST SESSION:**
Previous session log entries are permanent records. You cannot go back and change what was written in a past session even if you think something is wrong or outdated. If something needs correcting, note it in the NEW session entry only.

**RULE 4 — ALWAYS LOG WHAT YOU DID:**
At the end of every conversation where work was done, you MUST append a new session entry to the bottom of the "Session Log" section. Follow this exact structure:

```
### Session: YYYY-MM-DD

**What was done:**
- [bullet list of everything accomplished this session]

**Files modified / created:**
- [list every file touched and what changed]

**Resources used:**
- [list every website, dataset, tool, or document referenced]

**Next steps after this session:**
1. [numbered list of what should happen next]
```

**RULE 5 — ONLY ADD TO THE BOTTOM:**
New session entries go at the very bottom of the file, below all previous entries. Never insert content anywhere else in the file.

---

## Project Overview

**Project Name:** WOWERS — Waste Outfall Water Energy Recovery System
**University:** University of St. Thomas (Minneapolis/St. Paul, MN)
**Competition Origin:** Fowler Business Concept Challenge (scored 33.25/40 average)
**Team:**
- Tom (Xinsheng) Tang — MS in Data Science
- Mohamed Abdel Hamid — MS in Artificial Intelligence

---

## What WOWERS Is

WOWERS is a data-driven infrastructure intelligence platform that identifies where micro-hydropower energy recovery is feasible at US wastewater treatment plant outfalls, estimates how much energy could be generated, recommends commercially available turbine systems, and quantifies operational cost savings for municipalities.

The platform is **not** a turbine hardware company. It is an analytics and decision-support system built on national-scale EPA wastewater data.

**Core value proposition to a municipality:**
> "Tell us your plant's flow data and outfall conditions — we show you which turbine to buy, how much energy it will generate, and what your payback period looks like."

---

## What WOWERS Is NOT

- Not a turbine manufacturer
- Not a construction or installation company
- Not a hardware prototype project
- Not limited to one city or region — national scale from day one

---

## Strategic Direction

The project shifted from "build a physical turbine prototype" to "build a data-driven infrastructure intelligence platform." This direction aligns with the team's software and data science strengths, available public data, and realistic proof-of-concept scope.

**Long-term goal:** Help municipalities and wastewater utilities understand:
- Whether energy recovery is viable at their specific plant
- How much electricity could realistically be generated
- Which commercially available turbine technology fits their conditions
- How much operational energy cost could be offset annually

---

## Data Pipeline Architecture (5 Phases)

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Rank candidate plants from EPA ECHO data | ✅ Complete |
| Phase 2 | Monte Carlo energy yield estimation | ✅ Complete |
| Phase 3 | Turbine sizing via USGS 3DEP elevation API | 🔲 Not started |
| Phase 4 | Financial scorecard (NPV, IRR, payback) | 🔲 Not started |
| Phase 5 | ML model trained on DOE/FERC ground truth | 🔲 Not started |

---

## Key Technical Facts

- **Dataset processed:** ~279 million raw DMR rows, FY2009–FY2024, all 50 US states
- **Final POTW count:** 17,163 active wastewater treatment plants
- **National energy estimate (Phase 2 P50):** 697 GWh/yr — within DOE expected range of 500–5,000 GWh/yr
- **Top ranked plant:** MWRDGC Stickney WRP (IL), 1,200 MGD mean flow, 29.25 GWh/yr P50
- **Primary data source:** EPA ECHO / ICIS-NPDES (public)
- **Key output files:** `ranked_candidates.parquet`, `energy_yield_estimates.parquet`
- **Core physics:** P = η × ρ × g × Q × H (standard hydropower equation)
- **Turbine types modeled:** Kaplan, Francis, Pelton, Crossflow, in-conduit micro

---

## Key Files in the Codebase

| File | Purpose |
|---|---|
| `src/phase1/filter_potw.py` | Filters EPA ICIS data to active POTWs |
| `src/phase1/dmr_timeseries.py` | Parses ~279M DMR rows, extracts monthly flow |
| `src/phase1/flow_features.py` | Computes per-facility statistical flow features |
| `src/phase1/ranking.py` | Composite ranking score (weighted, min-max normalized) |
| `src/phase2/energy_physics.py` | Monte Carlo energy yield engine |
| `config/settings.yaml` | Central config — all thresholds, weights, physics constants |
| `ARCHITECTURE.md` | Full 5-phase system design |
| `PHASE1_REPORT.md` | Phase 1 results, data quality issues, validation |
| `PHASE2_REPORT.md` | Phase 2 results, Monte Carlo methodology, top 10 plants |
| `WOWERS_Capital_and_Funding_Research.md` | Detailed funding strategy, grant sources, comparable companies |

---

## Fowler Competition Feedback Summary

**Score:** 34.5 median / 33.25 average out of ~50 points

**Strengths noted by judges:**
- Strong originality and value proposition
- Clear social/sustainability impact
- Good payment model options (EaaS)

**Gaps to address:**
- "Why isn't this already done?" — needs clearer answer
- Manufacturing, shipping, and installation logistics need explanation
- Pilot strategy needs to be concrete and named
- Government funding sources should be named specifically

---

## Turbine Manufacturer Research (In Progress)

### Goal
Build a structured turbine database so WOWERS can recommend specific commercially available turbines to municipalities based on their plant's flow rate, hydraulic head, pipe diameter, and material requirements.

### Manufacturers Identified

| Manufacturer | Country | Turbine Types | Relevant Notes |
|---|---|---|---|
| CINK Hydro-Energy | Czech Republic | Crossflow, Kaplan, Pelton, Francis | Explicitly lists wastewater treatment plants as a use case. Runs at 6–100% of design flow. 450+ turbines in 50+ countries. |
| Canyon Hydro | USA | Francis, Pelton, Crossflow | Has dedicated conduit hydropower page. Installed turbines for City of Logan UT and City of Las Vegas. Provides data sheet for custom quotes. |
| Rentricity | USA | Reverse pump turbines (Francis-type) | NSF 61/372 certified for potable and wastewater. Real project data publicly listed: 2.4 MGD / 40 PSI / 32 kW and 2–12 MGD / 175–250 ft / 360 kW. |
| LucidEnergy | USA | Vertical axis spherical (in-pipe) | For large diameter pipes (24"–96"). Portland OR: 4 × 42" turbines = 200 kW, 1,100 MWh/yr. Works on effluent streams. |
| Turbulent | Belgium | Vortex (low head) | 15–90 kW range, rivers and canals, low head gravity flow. Relevant for gravity outfall archetype. |
| Ossberger GmbH | Germany | Crossflow | Original crossflow design, 0.5 kW–30 MW, 1–200 m head. Heavily cited in academic literature. |
| Gilbert Gilkes & Gordon | UK (est. 1853) | Pelton, Turgo | One of oldest hydro manufacturers. Well-documented spec sheets. |
| Emrgy | USA | Modular hydrokinetic | Canal-focused, spec sheet publicly available at emrgy.com. Raised $10–15M total. |
| Natel Energy | USA | FishSafe Kaplan variants | Fish-passage focused. Engineering services model, not direct hardware sales. |
| Andritz Hydro | Austria | Full turbine range | Large scale but publishes detailed turbine selection guides useful as reference. |

### Data Fields Needed Per Turbine

- Turbine type (Kaplan / Crossflow / Francis / Pelton / in-conduit / vortex)
- Min/max flow range (m³/s and MGD)
- Min/max head range (m)
- Rated power range (kW)
- Peak efficiency (%)
- Efficiency at part load (% of rated flow)
- Pipe diameter compatibility (for in-conduit systems)
- Material (316L stainless required for wastewater)
- Estimated cost range ($/kW or total $)
- Manufacturer name and contact / inquiry URL
- Real installation references (flow, head, kW output)
- Wastewater-certified / NSF rated (yes/no)

### Data Sources for Turbine Database

| Source | Type | URL |
|---|---|---|
| CINK references page | Real project specs | cink-hydro-energy.com/references |
| Canyon Hydro conduit page | Application guide + case studies | canyonhydro.com/projects/conduit.html |
| Rentricity featured projects | Real project specs (MGD, PSI, kW) | rentricity.com/featured-projects |
| Emrgy spec sheet | PDF with turbine specs | emrgy.com/wp-content/uploads/2021/06/Emrgy-Specifications.pdf |
| DOE HydroSource Database | Existing installations, ground truth | hydrosource.ornl.gov |
| FERC Conduit Exemption filings | Site-specific flow, head, equipment | ferc.gov |
| ORNL Conduit Hydropower Reports | Turbine selection charts, head/flow ranges | energy.gov |
| Energypedia Micro Hydro Manufacturers | Global manufacturer directory | energypedia.info |

---

## Session Log

---

### Session: 2026-05-17

**What was done:**
- Reviewed all existing project files: WOWERS.docx (original concept), Fowler feedback doc, follow-up pitch strategy doc, ARCHITECTURE.md, PHASE1_REPORT.md, PHASE2_REPORT.md, WOWERS_Capital_and_Funding_Research.md, and project codebase (all src/ files, config/settings.yaml, pyproject.toml, tests/)
- Confirmed Phase 1 and Phase 2 of the data pipeline are complete and validated
- Identified the next major feature: turbine recommendation engine requiring a structured turbine manufacturer database
- Researched turbine manufacturers relevant to low-head wastewater outfall conditions
- Identified 10 manufacturers across USA, Europe, covering Kaplan, Crossflow, Francis, Pelton, and in-conduit turbine types
- Identified 8 structured data sources to populate the turbine database (manufacturer reference pages, DOE HydroSource, FERC filings, ORNL reports)
- Defined the full set of data fields needed per turbine for the recommendation engine
- Created this project journal file (WOWERS_PROJECT_JOURNAL.md)

**Files modified / created:**
- `WOWERS_PROJECT_JOURNAL.md` — created (this file)

**Resources used:**
- EPA ECHO / ICIS-NPDES (existing pipeline data source)
- cink-hydro-energy.com (manufacturer research)
- canyonhydro.com (conduit hydropower case studies)
- rentricity.com (featured projects with real kW/MGD/PSI data)
- lucidenergy.com (in-pipe turbine specs)
- turbulent.be (vortex turbine specs)
- emrgy.com (spec sheet PDF)
- natelenergy.com (FishSafe turbine engineering)
- thecivilengineer.org (LucidPipe technical overview)
- ResearchGate (in-conduit hydropower market review paper)

**Next steps after this session:**
1. Build the turbine database — create `data/turbines/turbine_manufacturers.csv` (or `.parquet`) seeded with data from CINK references, Canyon Hydro conduit page, Rentricity featured projects, and the Emrgy spec PDF
2. Define the turbine recommendation logic in `src/phase3/turbine_selection.py` — rule-based matching on plant flow range vs. turbine min/max flow, plant head vs. turbine head range, pipe diameter compatibility, and wastewater material certification
3. Begin Phase 3 elevation queries using USGS 3DEP API (`src/phase3/elevation.py`) to replace literature-assumed head distributions with real site-specific head values
4. Contact Canyon Hydro and CINK Hydro directly using university research framing to request full spec catalogs or data sheets not publicly listed
5. Download and parse the Emrgy spec sheet PDF for structured turbine data

---
