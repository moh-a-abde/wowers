# Plant Energy-Consumption Research Plan

**Goal:** Produce a defensible, citable estimate of how much electricity each of the
~17,000 US POTWs consumes per year, so we can compute what fraction of each plant's
power bill a WOWERS turbine offsets.

**Core method:** Energy intensity (kWh per million gallons treated). We already have
flow for every plant. The only unknown is the right kWh/MG number per plant.

```
estimated_consumption_kwh_yr = mean_flow_mgd × 365 × energy_intensity_kwh_per_MG
```

**Owner:** Mohamed
**Status:** Steps 1–6 complete (research + config + validation). Step 7 (Phase 4 production code) pending.
**Completed:** 2026-06-08

> **Key validation finding:** the WEF Table 5-4 treatment×size grid (the originally
> planned basis) under-estimates by ~2× nationally and ~40% on large plants. The
> point estimate was switched to EPRI Table 5-1 **observed** flow-band averages,
> which validate to within 18% nationally and −6% on MWRA Deer Island. Table 5-4
> curves are retained for the low/high sensitivity band. See
> `ENERGY_CONSUMPTION_SOURCES.md` → Validation Results.

---

## Final Deliverables (what exists when this is done)

1. **`config/energy_intensity.yaml`** — the lookup table of kWh/MG by plant size × treatment
   type, each value tagged with its source citation (report + table + page).
2. **`ENERGY_CONSUMPTION_SOURCES.md`** — a one-page evidence log: every number, where it
   came from, and the assumption made where data was missing.
3. **A treatment-type assignment rule** — how we decide each plant's treatment category
   from EPA permit data, and the default used when unknown.
4. **A documented uncertainty statement** — the ±X% we can defend and why.

Everything else (applying the table to 17,000 plants) is code I wire up afterward.

---

## STEP 1 — Acquire the source documents

Get the actual PDFs. Do not work from summaries or memory.

| # | Document | Where to find it | What it gives us |
|---|----------|-----------------|------------------|
| 1.1 | **EPRI 2013** — "Electricity Use and Management in the Municipal Water Supply and Wastewater Industries" (Report 3002001433, authors Pabi, Amarnath, Goldstein, Reekie) | Google the exact title; EPRI public summary + the widely-mirrored PDF. WRF/water-utility sites host copies. | The primary kWh/MG grid by size and process; the aeration/pumping breakdown |
| 1.2 | **EPA 2013** — "Energy Efficiency in Water and Wastewater Facilities" (EPA 832-R-10-005, Local Government Climate & Energy Strategy Series) | Search EPA.gov for the report number | Government-citable corroborating kWh/MG by size |
| 1.3 | **EPA ENERGY STAR — Wastewater Treatment Technical Reference** | Search "ENERGY STAR wastewater treatment technical reference PDF" | A *regression* (energy vs. flow + load + treatment level) — the gold-standard model if we want Tier 3 |
| 1.4 | (Optional) **NYSERDA** "Statewide Assessment of Energy Use by the Municipal Water and Wastewater Sector" | NYSERDA.ny.gov | Real per-plant distributions to validate our averages |

**Action:** Download all four. Save to `data/raw/literature/energy_intensity/` with the
filenames `epri_2013.pdf`, `epa_2013.pdf`, `energystar_wwt_ref.pdf`, `nyserda.pdf`.

**Checkpoint:** You physically have the PDFs open before going further.

---

## STEP 2 — Extract the energy-intensity grid (the main event)

This is the number that drives everything. From **EPRI 2013** (primary) and **EPA 2013**
(check):

**2.1 — Find the master table.** Look for a table titled something like "Energy intensity
of wastewater treatment by plant size and treatment process" (wording varies). It will be
a grid: treatment types down the side, plant sizes across the top, kWh/MG in the cells.

**2.2 — Transcribe it exactly.** For every cell, record:
- Treatment type (e.g. trickling filter, conventional activated sludge, advanced/BNR, MBR)
- Size band (e.g. 1 MGD, 5 MGD, 10 MGD, 20 MGD, 50 MGD, 100 MGD — use whatever the report uses)
- kWh/MG value
- **Exact table number and page number** ← this is what makes it defensible

**2.3 — Record the process-step breakdown.** Find the figure/table showing where energy
goes (aeration ___%, pumping ___%, solids ___%, other ___%). Note the page.

**2.4 — Cross-check against EPA 2013.** Find the equivalent numbers. If EPA and EPRI agree
within ~15%, mark the number "corroborated." If they disagree, note both and use EPRI as
primary (flag the discrepancy).

**Output of this step:** a filled grid like:

| Treatment type | 1 MGD | 10 MGD | 100 MGD | Source |
|----------------|-------|--------|---------|--------|
| Trickling filter | ___ | ___ | ___ | EPRI Tbl _, p_ |
| Conventional activated sludge | ___ | ___ | ___ | EPRI Tbl _, p_ |
| Advanced / nutrient removal | ___ | ___ | ___ | EPRI Tbl _, p_ |
| MBR | ___ | ___ | ___ | EPRI Tbl _, p_ |

Leave a cell blank if the report doesn't give it — do NOT invent it. Blanks are handled
in Step 5.

---

## STEP 3 — Decide how to assign a treatment type to each plant

The reports tell us what each *type* uses; they don't tell us which type each of our
plants is. This is the biggest judgment call, so decide the rule explicitly.

**3.1 — Check what's in our EPA permit data.** Open `ranked_candidates.parquet` (or the
upstream ICIS_PERMITS / ICIS_FACILITIES files) and look for any field indicating treatment
level — narrative, SIC/NAICS, permit type, or a treatment-description column. List which
fields exist and how populated they are.

**3.2 — Build the assignment rule.** In priority order:
1. If a permit field directly states treatment level → use it.
2. If not, infer from size (larger metro plants are more likely advanced/BNR; small rural
   plants more likely lagoon/trickling filter) — but flag this as inferred.
3. If nothing is known → assign the **default = conventional activated sludge** (the most
   common US secondary process) and flag the plant `treatment_type_assumed = true`.

**3.3 — Quantify the guess.** Count how many plants get a real treatment type vs. the
default. Report this number — e.g. "treatment type known for N plants, assumed for M."
That fraction is a direct measure of how much we're guessing.

---

## STEP 4 — Decide the size-interpolation rule

Plants are continuous sizes; the table has discrete size points.

**4.1 — Rule:** for a plant between two table sizes, linearly interpolate the kWh/MG
between the two bracketing points (in log-flow space, since the relationship is a power
law — straight-line interpolate on a log scale).

**4.2 — Edge handling:** for plants smaller than the smallest table point or larger than
the largest, clamp to the nearest table value (do not extrapolate beyond the data).

**4.3 — Write these two rules down** in the sources doc so the interpolation is auditable.

---

## STEP 5 — Fill gaps and document every assumption

For each blank cell or missing case, write the assumption explicitly in
`ENERGY_CONSUMPTION_SOURCES.md`:

| Gap | What's missing | Assumption we make | Justification |
|-----|---------------|-------------------|---------------|
| Treatment type unknown | ~M plants | Default = conventional activated sludge | Most common US secondary process |
| MBR row missing a size | e.g. 1 MGD MBR | Use nearest published MBR value | Sparse category |
| Plant <1 MGD | below table | Clamp to smallest band | No data below |
| Date | reports are 2013 | Use as-is, note ~10yr old | Still the standard references |

The rule: **every number is either cited or flagged as an assumption. Nothing is silently
guessed.**

---

## STEP 6 — Validate against reality

Sanity-check before trusting it.

**6.1 — Spot-check 3–5 known plants.** Find a few plants that publish their actual energy
use (some large utilities publish sustainability reports — Deer Island/MWRA, DC Water,
King County all do). Compute our estimate for them and compare. We want to be within
~30%. Record the comparison.

**6.2 — National sanity check.** Sum estimated consumption across all plants. US POTWs
collectively use roughly **30–40 billion kWh/year** (a widely cited EPRI/EPA figure — verify
the exact number from the reports). If our total lands in that range, the method holds. If
it's 2× off, something in the grid or the flow units is wrong.

**6.3 — Cross-check the offset.** Our turbine output (Phase 3) divided by estimated
consumption should land in the low single-digit percent for most plants. If it's coming out
at 50%, a unit error exists somewhere.

---

## STEP 7 — Hand off to code

Once Steps 1–6 are done, the deliverables are:
- `config/energy_intensity.yaml` — the grid + interpolation rules
- `ENERGY_CONSUMPTION_SOURCES.md` — the evidence log
- The treatment-assignment rule

I then build `src/phase4/plant_consumption.py` to add two columns to the financial
scorecard:

| Column | Formula |
|--------|---------|
| `est_plant_consumption_kwh_yr` | `mean_flow_mgd × 365 × intensity(size, treatment_type)` |
| `energy_offset_pct` | `annual_energy_kwh / est_plant_consumption_kwh_yr × 100` |

---

## What we can claim when this is finished

> "We estimate each plant's baseline electricity use from EPRI (2013) and EPA energy-
> intensity benchmarks — kWh per million gallons — adjusted for plant size and treatment
> process. Category averages are cited to specific tables; treatment-type assignment is
> known for N plants and defaulted for M. The estimate is a screening figure good to
> roughly ±30%, validated against published consumption for several large utilities and
> against the national POTW electricity total. It is sufficient to rank opportunities and
> state the share of each plant's bill our turbine offsets; site energy audits would tighten
> it for final candidates."

---

## Effort estimate

| Step | Time |
|------|------|
| 1 — Acquire PDFs | 30 min |
| 2 — Extract grid | 2–3 hrs (careful transcription) |
| 3 — Treatment assignment rule | 1–2 hrs (depends on permit data) |
| 4 — Interpolation rule | 30 min |
| 5 — Document gaps | 1 hr |
| 6 — Validation | 1–2 hrs |
| **Total** | **~1 focused day** |
