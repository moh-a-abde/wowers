# Energy Consumption Sources and Assumptions

Evidence log for `config/energy_intensity.yaml`. Every number is either cited or flagged as an assumption.

---

## Primary Source

**EPRI 3002001433** — "Electricity Use and Management in the Municipal Water Supply and Wastewater Industries"
Authors: S. Pabi, A. Amarnath, R. Goldstein (EPRI); L. Reekie (Water Research Foundation)
Final Report, November 2013. File: `data/raw/literature/energy_intensity/epri_2013.pdf`

## Secondary Source (corroboration)

**EPA (2013)** — "Energy Efficiency in Water and Wastewater Facilities"
Local Government Climate and Energy Strategy Series, U.S. EPA.
File: `data/raw/literature/energy_intensity/epa_2013.pdf`

**Assessment:** The EPA 2013 guide is a policy/planning document. It does not contain an independent kWh/MG grid by treatment type and plant size. It references the same EPRI and WEF sources. It confirms the ~30 TWh/yr national wastewater total and corroborates the energy breakdown (aeration dominant). It is not suitable as a primary grid source and has not been used to fill any cells in the YAML.

---

## Cited Numbers

### kWh/MG grid by treatment type × plant size

| Treatment type | 1 MGD | 5 MGD | 10 MGD | 20 MGD | 50 MGD | 100 MGD | Source |
|---|---|---|---|---|---|---|---|
| Trickling Filter | 1,811 | 978 | 852 | 750 | 687 | 673 | EPRI Tbl 5-4, p.5-15 |
| Conventional Activated Sludge | 2,236 | 1,369 | 1,203 | 1,114 | 1,051 | 1,028 | EPRI Tbl 5-4, p.5-15 |
| Advanced w/o Nitrification | 2,596 | 1,573 | 1,408 | 1,303 | 1,216 | 1,188 | EPRI Tbl 5-4, p.5-15 |
| Advanced w/ Nitrification (BNR) | 2,951 | 1,926 | 1,791 | 1,676 | 1,588 | 1,588 | EPRI Tbl 5-4, p.5-15 |

Table 5-4 itself cites: *Energy Conservation in Water and Wastewater Treatment Facilities*, WEF Manual of Practice 32, WEF Press, Alexandria VA, 2009.

**Cross-check with EPRI's own data (Table 5-1, p.5-6):** EPRI Table 5-1 gives weighted-average energy intensity from the EPA Energy Star Portfolio Manager dataset (analyzed by Lawrence Berkeley National Laboratory). These values (3,300 kWh/MG for <2 MGD down to 1,600 kWh/MG for 101–330 MGD) are treatment-type-agnostic flow-band averages. They are broadly consistent with the Table 5-4 activated sludge column, confirming the order of magnitude. No discrepancy requires a flag.

### Observed flow-band intensity (POINT-ESTIMATE BASIS)

| Flow band (MGD) | kWh/MG | | Flow band (MGD) | kWh/MG |
|---|---|---|---|---|
| <2 | 3,300 | | 16–46 | 1,700 |
| 2–4 | 3,000 | | 46–100 | 1,700 |
| 4–7 | 2,400 | | ≥100 | 1,600 |
| 7–16 | 2,000 | | | |

Source: EPRI 3002001433, Table 5-1, p.5-6 (EPA Energy Star Portfolio Manager dataset, analyzed by Lawrence Berkeley National Laboratory, Oct 2012). These are **observed** weighted averages. Validation (below) showed they reproduce published utility consumption and the national total far better than the theoretical treatment grid, so they are used for the point estimate.

### Process-step breakdown

Aeration 52%, Biosolids Processing 30%, Pumping 12%, RAS Pumping 3%, Misc. 3%.
Source: EPRI 3002001433, Figure 5-2, p.5-4 (Hazen & Sawyer energy audit averages).

### National total (Step 6.2 sanity check target)

**30.2 TWh/year** (0.8% of total US electricity, 2011).
Source: EPRI 3002001433, Table 5-5, p.5-16 and Executive Summary p.ix.

---

## Assumptions and Gaps

| Gap | What's Missing | Assumption | Justification |
|---|---|---|---|
| Treatment type unknown | All 17,163 plants (no permit field exists) | Point estimate uses treatment-agnostic observed flow-band averages (Table 5-1); treatment-type spread shown via low/high band | Observed averages validate better than guessing a type; band exposes the residual uncertainty |
| MBR full-plant, all sizes | Only one full-plant MBR example in EPRI (3 MGD = 4,910 kWh/MG, Tbl 5-3 p.5-12) | Hold 4,910 kWh/MG constant across all size bands | Sparse data; MBR is a small fraction of US POTWs. Flag plants assigned MBR |
| Plants <1 MGD | Below smallest table size point | Clamp to 1 MGD value | No published data below 1 MGD in EPRI or WEF source |
| Plants >100 MGD | Above largest table size point | Clamp to 100 MGD value | EPRI Figure 5-4 shows intensity is roughly flat above ~20 MGD |
| Data age | Reports are 2013 (EPRI) and 2009 (WEF MOP 32 underlying data) | Use as-is | Still the standard references cited industry-wide; no more recent comprehensive grid exists |
| MBR cross-check | Table 5-4 has no MBR row | Derived from Table 5-3 composite example | Only option available in EPRI; flag as high-uncertainty |

---

## Treatment-Type Assignment (Step 3)

**Finding:** Treatment level is **not recorded in any EPA permit field**. Verified across `ICIS_PERMITS` (28 cols), `ICIS_FACILITIES` (14 cols), `NPDES_PERM_COMPONENTS`, `NPDES_NAICS`, and `NPDES_SICS`. Available fields describe permit *program* category (POTW, biosolids, pretreatment, stormwater) and permit *form* (general vs. individual), never the treatment *process*.

**Consequence:** Treatment type is **known for 0 plants and assigned for all 17,163** (100%). The only discriminating signal available is plant size (`mean_flow_mgd`).

**Size distribution of candidates:**

| Size band (mean MGD) | Plants |
|---|---|
| <1 | 12,065 |
| 1–5 | 2,589 |
| 5–10 | 531 |
| 10–20 | 269 |
| 20–50 | 178 |
| 50–100 | 49 |
| >100 | 37 |
| zero/unknown flow | 1,445 |

**Rule adopted (CAS default + sensitivity band):**

- **Point estimate:** every plant → `conventional_activated_sludge`. This is EPRI's stated default — Table 5-5 assumes 80% of secondary flow uses activated sludge.
- **Sensitivity low bound:** `trickling_filter` (lowest-intensity common secondary process).
- **Sensitivity high bound:** `advanced_with_nitrification` (highest-intensity common process; MBR excluded as rare).
- Every plant is flagged `treatment_type_assumed = true`.

This avoids false precision: rather than guessing a specific type per plant from size alone, we report one defensible point value plus an honest range. The band width directly communicates how much the unknown treatment type matters for each plant.

---

## Interpolation Rules

**Point estimate (observed bands):** step / band lookup — a plant takes the kWh/MG of the flow band it falls in (Table 5-1 is published as discrete bands, not a continuous curve).

**Sensitivity band (treatment curves):** log-linear interpolation between size points. Rationale: EPRI Figure 5-4 and Table 5-1 both show a power-law (concave) relationship between flow and energy intensity — a straight line on log-log axes is a better fit than linear interpolation on the raw scale.

Formula for a plant of flow `Q` MGD between table points `Q_lo` and `Q_hi`:

```
intensity(Q) = intensity(Q_lo) * (intensity(Q_hi) / intensity(Q_lo)) ^ (log(Q/Q_lo) / log(Q_hi/Q_lo))
```

**Edge clamping:** For `Q < 1 MGD`, use the 1 MGD value. For `Q > 100 MGD`, use the 100 MGD value.

---

## Validation Results (Step 6)

Run via `scripts/validate_energy_intensity.py` against all 15,718 candidate plants with positive flow.

**6.1 — Spot-checks vs. published actuals** (point estimate at each plant's flow):

| Plant | Flow | Our estimate | Published actual | Error |
|---|---|---|---|---|
| MWRA Deer Island | 250 MGD | 146 GWh/yr | ~155 GWh/yr (18 MW demand, $16M bill) | **−6%** |
| DC Water Blue Plains | 290 MGD | 169 GWh/yr | ~240 GWh/yr (~30 MW; 10 MW = ⅓) | **−29%** |
| King County West Point | 90 MGD | 56 GWh/yr | no published figure found | — |

Both checks land within the ±30% target. Blue Plains is an exceptionally energy-intensive plant (advanced nitrification/denitrification + thermal hydrolysis, "the largest advanced wastewater plant in the world") and sits at the high edge — expected, and a reminder the point estimate under-reads the most advanced large plants.

**6.2 — National total:**

- Total candidate flow: **32,252 MGD** vs. EPRI national reference ~32,000–32,845 MGD — essentially exact.
- National consumption (point estimate): **24.9 TWh/yr** vs. EPRI/EPA reference **30.2 TWh/yr** → **within 18%**.
- The remaining gap is expected: EPRI's 30.2 TWh assumes ~51% of national flow receives energy-intensive "greater-than-secondary" treatment and adds reuse-pumping and no-discharge categories our flow dataset does not separately carry. 24.9 TWh is comfortably within screening tolerance.

> **Note on method change:** the original plan specified the WEF Table 5-4 treatment×size grid as the primary basis. Validation showed that grid produces only **15.3 TWh nationally (≈2× low)** and under-reads Deer Island by 40%. EPRI itself flags (p.5-15) that the Table 5-4 values run below observed values, especially above 10 MGD. We therefore switched the **point estimate** to the Table 5-1 **observed** flow-band averages (which validate well) and kept the Table 5-4 treatment curves only for the **sensitivity band**.

**6.3 — Offset sanity check** (turbine p50 yield ÷ estimated consumption, 15,691 plants):

- Median offset **0.80%**, p90 **1.49%**, p99 **3.95%**, max **5.00%**.
- All low single-digit percent, exactly as predicted. This confirms there is no unit error anywhere in the flow → consumption → offset chain (a unit slip would have produced offsets near 50% or 0.05%).

---

## Uncertainty Statement

This estimate is a **screening figure good to approximately ±30%**, consistent with EPRI's own characterization. Sources of uncertainty:

1. **Treatment type assignment** — treatment type is defaulted for **all 17,163 plants** (known for none; see Step 3). The true intensity could differ by up to ~50% per plant (trickling filter vs. advanced BNR span). This is the single largest source of uncertainty, and the reason the point estimate ships with an explicit low/high sensitivity band.
2. **Data age** — underlying WEF/EPRI data is from ~2009–2013. Efficiency improvements since then likely reduce actual consumption slightly; this estimate is therefore conservative (may overstate consumption).
3. **Unit process configuration** — plants with unusual configurations (e.g., lagoons, package plants) are not represented in the grid.
4. **Excluding collection system pump stations** — EPRI explicitly excludes pump stations located far from the treatment facility (EPRI p.5-16). Our estimate also excludes these.

This accuracy is sufficient to rank opportunities and state the share of each plant's bill that WOWERS offsets. Site energy audits would tighten it for final candidates.
