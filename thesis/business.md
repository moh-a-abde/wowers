# WOWERS — Business Plan Working Document

**Status:** working document, drafted 2026-07-31. Feeds work package **J1 · Ch3 Business Model**.
**Owners:** Tom + Mohamed (J1 is a joint work package).

> **This file is an internal development artifact, not a citable source.** Per the rule at the top of
> `THESIS_BREAKDOWN.md`, no Markdown file in this repo may appear in the thesis reference list or in an
> inline citation. Numbers below are either (a) this project's own generated results — reported in the
> thesis as our findings — or (b) claims traceable to an external source, which must be verified and
> cited from that original source. Items needing verification before they enter the thesis are marked
> **[VERIFY]**.

**Number provenance.** Everything quantitative here is recomputed from `exports/viable_sites.geojson`
(1,138 features, post-P2-SEED baseline) and the calibration multipliers in `CF_CALIBRATION_REPORT.md`.
The scenario table in §2.4 uses a reconstruction of the Phase 4 NPV formula (30 yr life, 0.2 %/yr
degradation, opex flat) that reproduces the pipeline's reported `npv_usd` to a median relative error of
0.000 — but it is a reconstruction, not a pipeline run. **Before any of §2.4 enters the thesis, re-run
Phase 4 properly with the alternative discount rate and the calibrated energy column.**

---

## 1. The business in one paragraph

WOWERS is a national screening and deal-origination layer for micro-hydropower energy recovery at
water infrastructure. We ingested ~279 million EPA DMR records covering 17,148 active POTWs, estimated
per-site energy with a Monte-Carlo physics model, matched commercially available turbines, and scored
every site on NPV, IRR and payback. The output is 1,138 investment-ready sites — a **0.76 % hit rate**
for the sites that actually carry the value. We do not manufacture turbines, install them, or own the
assets. We sell the answer to the question that costs everyone else eighteen months: *which of these
17,148 plants is worth a site visit.*

---

## 2. What the numbers actually support

### 2.1 The funnel

| Stage | Sites | Gate |
|---|---:|---|
| Active POTWs screened | 17,148 | EPA ICIS-NPDES, active permit |
| Flow data sufficient | 5,464 | usable DMR flow record |
| Head + coordinates resolved | 4,860 | USGS 3DEP + outfall coords |
| Turbine-viable | 3,778 | turbine match, physics gate |
| **Investment-ready** | **1,138** | NPV > 0, payback ≤ 20 yr, real IRR |

Headline energy: **409.2 GWh/yr** at the Phase 2 physics ceiling. Portfolio NPV **$310.1M**, portfolio
CapEx **$211.3M**, median payback **9.8 yr**.

### 2.2 The portfolio is extremely concentrated

This is the single most important fact for the business model, and it is not visible in the headline.

| Cut | Sites | Energy | NPV | Share of NPV | CapEx | Median payback |
|---|---:|---:|---:|---:|---:|---:|
| All investment-ready | 1,138 | 409.2 GWh/yr | $310.1M | 100 % | $211.3M | 9.8 yr |
| Top 100 by NPV | 100 | 238.1 GWh/yr | $249.2M | 80.4 % | $83.5M | — |
| Sites ≥ 100 kW | 131 | 270.3 GWh/yr | $252.6M | 81.4 % | $99.8M | **5.5 yr** |
| Sites ≥ 25 kW | 308 | 343.9 GWh/yr | $283.5M | 91.4 % | $163.1M | 8.4 yr |
| Sites < 25 kW | 830 | — | ~$25M | ~8 % | — | — |

Median investment-ready site: **13 kW · $66.4k CapEx · $8.6k/yr revenue · $29.7k NPV · 9.8 yr payback.**
Median site ≥ 100 kW: **$543.8k CapEx · $116.5k/yr revenue · 5.5 yr payback.**

**131 sites carry 81 % of the value.** Everything downstream — pricing, sales motion, pilot selection —
follows from this.

### 2.3 Composition of the viable set

| Dimension | Breakdown |
|---|---|
| Size bands | < 10 kW: 391 · 10–25 kW: 439 · 25–100 kW: 177 · 100–250 kW: 89 · 250–1,000 kW: 37 · > 1,000 kW: 5 |
| Permitting tier | qualified facility 834 · small FERC 262 · full NEPA 42 |
| Turbine type | Crossflow 654 · Kaplan 256 · Francis 228 |
| Head confidence | high-confidence viable 848 of 1,138 |
| Top states | CA 147 · TX 102 · MA 62 · OH 53 · PA 53 · CT 47 · IL 47 · NY 45 · NC 44 · NJ 38 |

Geographic concentration matters commercially: CA + TX + the Northeast corridor (MA/CT/NY/NJ/PA) hold a
large share of viable sites, which makes a regional pilot campaign cheap relative to a national one.

### 2.4 Public-sector finance is the correct lens — and it rescues the long tail

The Phase 4 model uses `discount_rate: 0.06`, a commercial rate. A public owner borrows on tax-exempt
municipal debt at roughly 3.5 % **[VERIFY: current municipal utility revenue-bond yields]** and, for
water infrastructure, often at 0–2 % through the Clean Water State Revolving Fund, sometimes with
principal forgiveness. Re-scoring at a municipal cost of capital, and against the calibrated energy
tiers rather than the physics ceiling:

**Tier labels follow the thesis as re-labeled on 25 July 2026, not `CF_CALIBRATION_REPORT.md`, which is
stale.** CF 0.60 is the **optimistic** upper tier resting on the Conduit 3 design projection, not a
central estimate. The tier the thesis treats as evidenced is the **floor**, and the metered conduit
record from EIA-923 lands at CF 0.2439 (114.4 GWh/yr) with Point Loma — the only metered treated-
wastewater conduit plant in the country — at CF 0.1914 (89.8 GWh/yr). Both metered rows sit at or below
the floor. Any business case must be shown at the metered tier, not just the optimistic one.

| Scenario | Viable | Portfolio NPV | Median payback | ≥ 100 kW |
|---|---:|---:|---:|---:|
| **Commercial finance (r = 6 %, no grant)** | | | | |
| Ceiling CF 0.872 (Phase 2 as-modeled) | 1,137 | $310.1M | 9.7 yr | 131 |
| Optimistic CF 0.600 (Conduit 3 proj.) | 439 | $152.6M | 10.3 yr | 119 |
| Floor p50 CF 0.447 | 129 | $59.4M | 10.6 yr | 66 |
| Measured all-conduit CF 0.2439 | **24** | $16.9M | 10.4 yr | 23 |
| Measured Point Loma CF 0.1914 | **12** | $7.1M | 11.3 yr | 12 |
| **Municipal finance (r = 3.5 % + 50 % grant)** | | | | |
| Optimistic CF 0.600 | 1,138 | $357.6M | 7.5 yr | 131 |
| Floor p50 CF 0.447 | 1,041 | $179.3M | 12.4 yr | 131 |
| **Measured all-conduit CF 0.2439** | **282** | **$71.4M** | 12.7 yr | **104** |
| Measured Point Loma CF 0.1914 | 141 | $40.8M | 13.3 yr | 67 |

Three conclusions, and the first is uncomfortable:

1. **At the only metered evidence we have, the commercial case nearly disappears — 24 sites, not 1,138.**
   Do not build a pitch on the ceiling or the optimistic tier. The defensible commercial claim is roughly
   **two dozen sites nationally** under conventional finance.
2. **Public finance is what makes the portfolio exist at all.** The same metered tier goes from 24 to
   **282 sites** once municipal debt and a 50 % capital subsidy are applied. That is not a marketing
   gloss; it is the difference between the business existing and not existing, and it makes §6.1 the most
   important section of this document.
3. **The ≥ 100 kW cohort survives every tier.** 23 of the 24 commercially viable sites at the metered CF
   are ≥ 100 kW, as are 104 of the 282 under public finance. The concentration argument in §2.2 is robust
   to the harshest energy assumption in the thesis — the long tail is not. Target the head at every tier.

The existing `npv_with_50pct_grant_usd` column corroborates the subsidy direction independently:
portfolio NPV rises from $310.1M to $415.8M at the ceiling energy tier under 50 % grant.

### 2.5 Why the small sites still don't become customers

| Cohort | n | Median revenue | Median opex | **Median net cash flow** |
|---|---:|---:|---:|---:|
| < 25 kW | 830 | $6,427/yr | $787/yr | **$5,590/yr** |
| ≥ 100 kW | 131 | $116,542/yr | $6,440/yr | **$109,558/yr** |

A 13 kW project and a 500 kW project require the same interconnection study, the same procurement, the
same council approval, the same FERC conduit filing, and the same maintenance visit to a debris-laden
effluent stream. That fixed overhead does not scale down. $5,590/yr does not fund a maintenance
contract; $109,558/yr does.

**Empirical confirmation from our own data:** Point Loma WWTP (San Diego, CA) — the largest single NPV
in our screen and the only U.S. wastewater conduit plant with measured generation in the DOE EHA record
— was built and has been **offline since 2018**. Somebody's business case penciled and the plant stopped
anyway. That is an O&M and attention failure, not an NPV failure. It belongs in the risk section, not
buried.

---

## 3. Who pays

The buyer is not the municipality first. Municipal capital cycles run 18–36 months, and at 3 %
origination the median site yields WOWERS about $2k — less than the cost of the sales call that wins it.

| Buyer | What they buy | Why they move | Cycle | Priority |
|---|---|---|---|---|
| **Turbine OEMs** (Rentricity, InPipe, CINK, Ossberger, Canyon Hydro, Mavel, Natel) | Qualified national lead flow | Their entire U.S. addressable pipeline is 131 sites and they currently find them one at a time | weeks | **1** |
| **ESCOs / energy consultants** (Veolia, Trane, Honeywell, Siemens, Ameresco) | Screening layer inside water-sector audits | They already sell into these plants; micro-hydro is a line item they cannot currently source | 1–3 months | **1** |
| **State energy offices / EPA regions / DOE WPTO** | State-level data layer + methodology | Planning and program design; they fund studies as a matter of course | 3–9 months | **2** |
| **Large POTW operators** (metro districts, county utilities) | Site-specific feasibility screen | Only worth direct sale in the ≥ 100 kW cohort | 12–36 months | **3** |
| **Project developers / IPPs** | Origination pipeline | Would own assets and take the yield risk | months | **3**, later |

Note the reframe: **LucidEnergy, Rentricity, InPipe and CINK are channel, not competition.** Every one of
them sells hardware and each does its own site hunting; none publishes a national screen. The real
competitors are ESCO in-house audits and, overwhelmingly, **doing nothing**.

---

## 4. Sales model

### 4.1 Three motions, in sequence

**Motion 1 — Publish, then harvest inbound (months 0–6, cost ≈ $0).**
Release the screened dataset publicly (GeoJSON + methodology) and keep the existing React/MapLibre
dashboard live. Present the methodology to EPA Region 5, DOE Water Power Technologies Office, and 1–2
academic groups (ORNL Water Power, NREL). Open data is the cheapest lead generator available to us: it
produces citations, agency inbound, and OEM inquiries without a sales team. Gate the *analysis service*,
never the data.

**Motion 2 — OEM and ESCO channel deals (months 3–12).**
Route matched sites to the OEM whose product line fits the recommended turbine type. `turbine_type` maps
directly: Crossflow → Ossberger, CINK, Canyon Hydro; Kaplan/Francis → Mavel, GUGLER, Voith; in-conduit
micro → Rentricity, InPipe, LucidEnergy. Deliverable per lead is a one-page technical sheet carrying
exactly what an OEM needs to quote: rated kW, net head, design flow, FDC summary, recommended turbine
type, location, permit tier, and the NPDES permit contact already present in EPA ECHO. Target: 3 signed
channel partners.

**Motion 3 — Direct paid engagements (months 6–24).**
Screening reports and origination fees against the ≥ 100 kW cohort, sold either directly to the utility
or jointly with the ESCO partner from Motion 2. This is where revenue per deal becomes real.

### 4.2 Funnel arithmetic (planning assumption, not a forecast)

Start from the 131 sites ≥ 100 kW, concentrated in ~10 states.

| Stage | Conversion | Count |
|---|---:|---:|
| Bankable sites identified | — | 131 |
| Reachable in first-wave states (CA, TX, MA, IL, OH, PA, NY, CT, NJ, NC) | ~70 % | ~92 |
| Contacted, first meeting held | 40 % | ~37 |
| Paid screening engagement | 30 % | ~11 |
| Reaches financial close within 5 yr | 25 % | ~3 |

Three closed projects over five years, at median $543.8k CapEx, is $1.6M of hardware moved. Add screening
fees and channel subscriptions and the five-year revenue picture is roughly **$0.5–1.2M** — a consulting
and data business for two people, not a venture-scale company. §7 says this out loud rather than hiding
it.

### 4.3 Who does what

- **Tom** — pipeline, data refresh cadence (EPA republishes DMR annually, typically February), report
  generation, methodology defense in technical meetings.
- **Mohamed** — the customer-facing dashboard, per-client deliverables, demo in every sales conversation.
- **Both** — outreach. The single highest-value unstarted action in the whole project remains the
  customer-validation calls scoped in the journal: 3 utility operations directors, 2 ESCO
  business-development leads, 2 turbine OEMs, 2 state energy offices, 1 EPA/DOE contact. Ten
  conversations decide whether §4 is a plan or a fantasy.

---

## 5. Pricing

Every price is derived from something, never invented. The derivation sentence is mandatory in the
thesis (format §3.5).

| Product | Price | Derivation |
|---|---|---|
| **Screening report** — per-utility custom run, per-site detail, sensitivity bands, methodology appendix | $8–15k | Roughly 1 % of the median NPV of a 100–250 kW site (~$1.1M); benchmarked against a typical ESCO energy audit at $15–50k **[VERIFY: current audit price range]** |
| **Data subscription** — filtered national database access for OEMs, ESCOs, consultants | $1–2k/month | Value ceiling of ~30 qualified leads/yr at $3k per qualified lead ≈ $90k/yr; priced well under that to make the buy trivial |
| **Origination success fee** — paid on financial close | 2–4 % of project CapEx | Standard developer origination fee band **[VERIFY]**; at the median ≥ 100 kW CapEx of $543.8k this is $11–22k per closed project |
| **State / agency data layer** — GIS exports, white-label report, state-specific overlays | $25–75k per engagement | Scaled to typical state energy-office study procurement **[VERIFY against a real state RFP]** |
| **Grant-funded methodology work** | $50–275k | NSF SBIR Phase I is ~$275k over ~6 months **[VERIFY current award ceiling]** |

### On Energy-as-a-Service

The Fowler judges liked the EaaS payment model, and it should be treated carefully rather than adopted.
Under EaaS, WOWERS carries the energy-yield risk on a model whose own calibration spans a factor of 4.6
— from the 409.2 GWh/yr ceiling down to the 89.8 GWh/yr implied by the only metered treated-wastewater
conduit plant in the country — and which has **zero** wastewater-specific ground truth. The Phase 5 ML
effort was killed precisely because only 11 new conduit labels exist nationally, and that one wastewater
plant has been offline since 2018. Signing a generation guarantee against that uncertainty would be
underwriting a risk the thesis explicitly says it cannot quantify.

**Recommended position:** fee-based revenue until a metered pilot exists. Offer EaaS only on sites where
a first year of metered generation has been recorded, and price the contract on the measured capacity
factor rather than the modeled one. Stating this in Ch3 demonstrates that the business model respects
the technical uncertainty documented in Ch4.4 — an argument that reads as strength, not retreat.

---

## 6. Where the money comes from

Two distinct questions that pitch decks routinely conflate. Keep them separate.

### 6.1 Capital that funds the *projects* (customer-side)

This is what makes the 7.5 yr payback in §2.4 real. Selling the funding path is a large part of selling
the project.

| Source | What it is | Fit | Notes |
|---|---|---|---|
| **EPA Clean Water State Revolving Fund (CWSRF)** | State-administered revolving loans for wastewater capital; below-market or 0 % interest, principal forgiveness available in many states | **Primary.** This is the money that actually buys POTW capital equipment | Energy efficiency at treatment works is an explicitly eligible category **[VERIFY current eligibility language and state-by-state forgiveness terms]** |
| **EPA WIFIA** | Low-cost federal direct loans for larger water infrastructure | Only for the top of the portfolio | Minimum project size makes it irrelevant below ~$20M **[VERIFY threshold]** |
| **USDA Rural Development — Water & Waste Disposal Loan & Grant** | Grants + loans for water systems in communities under 10,000 population | Fits a meaningful slice of the small-site tail | Grant share can be substantial for low-income communities **[VERIFY]** |
| **IRA elective ("direct") pay for clean-energy tax credits** | Lets tax-exempt entities receive the value of the ITC/PTC as a cash payment | Potentially the single largest lever — it is what converts a tax credit into usable money for a municipality | **[VERIFY — highest priority.** Confirm current statutory status, whether conduit/small hydro qualifies, applicable credit percentage, and any 2025–2026 legislative changes before this appears anywhere in the thesis or a pitch.] |
| **State energy office programs / utility rebates / on-bill financing** | State-level capital grants and utility efficiency incentives | Varies enormously by state; CA, MA, NY are strongest | Check per state against the top-10 list in §2.3 |
| **ESPC / ESCO performance contract** | ESCO funds the capital and is repaid from verified savings | Removes the municipal capital request entirely | Reinforces the ESCO-as-channel strategy in §3 |
| **Third-party PPA / developer ownership** | A developer owns the asset, the utility buys the power | Bypasses municipal capital cycles | Requires a developer partner willing to take yield risk |

**Pitch consequence:** never lead with "the project costs $544k." Lead with "the project costs $544k, of
which a CWSRF loan at 0–2 % covers the whole amount, with principal forgiveness available, and pays for
itself in 7.5 years against a 30-year asset life."

### 6.2 Capital that funds *WOWERS* (company-side)

The honest recommendation is **non-dilutive first, and probably non-dilutive only.**

| Source | Amount | Why it fits |
|---|---|---|
| **NSF SBIR Phase I** | ~$275k **[VERIFY]** | The methodology *is* the proposal. 427 passing tests, a documented calibration band, and a published negative result are exactly the reproducibility posture these programs reward |
| **DOE Water Power Technologies Office** | larger, more competitive | Directly on-mission; the national conduit-hydro resource question is theirs |
| **EPA / state energy R&D programs** | $25–100k | Smaller, faster, and a credible first non-dilutive win |
| **University channels** — St. Thomas, Fowler follow-on, regional competitions | $5–50k | Already partly won; cheapest capital available |
| **Revenue** | — | Screening engagements and channel subscriptions fund the business directly. This is the realistic path |
| **Venture capital** | — | **Do not pursue at current scope.** A $211.3M one-time hardware market, of which we touch single-digit percent, does not clear a venture return threshold. Raising against it would require inflating numbers this project has spent a year making honest |

If a venture-scale story is ever wanted, the honest route is the multi-vertical expansion already scoped
in the journal — water-utility PRVs, industrial cooling discharge, irrigation canal drops, mine
dewatering. Each reuses the pipeline with a new ingest module. **None of it is built.** Size it
separately, label it as unbuilt, and do not blend it into the POTW numbers.

---

## 7. The pitch

### 7.1 Positioning line

> "We screened every wastewater treatment plant in the United States for hydropower energy recovery —
> 17,148 plants, 279 million discharge records — and found 131 sites that carry 81 % of the value. We
> don't build turbines. We tell you which of the seventeen thousand is worth a site visit."

### 7.2 Five-slide structure

1. **The number nobody has.** 17,148 POTWs, 279M DMR rows, 409.2 GWh/yr of physically recoverable energy
   at the modeled ceiling — and, once real capacity factors are substituted in, an evidenced floor near
   119 GWh/yr with the metered conduit record landing at 114.4. We report the floor, not the ceiling.
   Nobody else has computed either.
2. **Why it hasn't been done.** The hit rate is 0.76 %. See §7.3.
3. **The concentrated prize.** 131 sites, $99.8M CapEx, $252.6M owner NPV, median payback 5.5 yr — and
   7.5 yr even at the conservative energy tier once municipal financing is applied. Show the funnel and
   the concentration table.
4. **How we make money.** Channel first (OEM/ESCO), reports and origination fees second. Show §5 with the
   derivations visible.
5. **What we've actually built vs. what we haven't.** A running 4-phase pipeline, 427 passing tests, a
   published calibration band, a live national dashboard — and no measured wastewater ground truth, no
   pilot, no signed channel partner yet. Naming the gaps is what makes the rest believable.

### 7.3 Answers to the four Fowler gaps

**"Why isn't this already done?"** — Now answerable with evidence rather than assertion:

1. The hit rate is **131 in 17,148 = 0.76 %**. Until public bulk data and cheap compute existed, the
   search cost exceeded the prize. Screening one plant by consultant costs thousands; screening all of
   them now costs roughly nothing.
2. A nationwide search of FERC and DOE EHA records found **exactly one** wastewater conduit plant with
   measured generation — Point Loma — and it has been offline since 2018. The category is genuinely
   unexploited, and the absence of records is itself the finding.
3. **73 % of paper-viable sites are under 25 kW.** Anyone who looked at the aggregate saw a market of
   thousands of tiny uneconomic projects and rationally walked away. The value is concentrated in a head
   that only appears once you rank the whole population — which is what we did.

**"Manufacturing, shipping, installation logistics?"** — We are not in that path. Equipment comes from
existing OEMs with existing U.S. channels; our CapEx model carries equipment, installation at 17.5 % of
equipment, interconnection, and permitting as separate lines totaling $353.5M across the scored set. The
honest constraint to state: the micro-hydro supply chain is thin, with 12–18 month lead times from small
European manufacturers. That is a schedule risk we disclose, not one we solve.

**"Named pilot?"** — See §8. Name a real plant, with its real modeled numbers.

**"Named government funding?"** — See §6.1. Name CWSRF, USDA RD, DOE WPTO and the state programs
specifically, with the caveat that eligibility terms must be verified per state.

### 7.4 Three things never to say

- Do not quote $310.1M as "our market." It is the net present value accruing to *plant owners*, not
  revenue to WOWERS. Conflating them is the fastest way to lose a technical audience.
- Do not quote the 409.2 GWh/yr ceiling without the calibrated band beside it. Ch4.4 exists; a business
  chapter that ignores it contradicts the thesis it sits in.
- Do not present Point Loma as a live flagship installation. It is offline. It is a cautionary case and
  should be presented as one.

---

## 8. Named pilot targets

Selection criteria: ≥ 100 kW, high head confidence, payback under 5 years, and a large operator with
in-house engineering capacity.

| Site | State | Rated | CapEx | Revenue | Payback | Role in the pitch |
|---|---|---:|---:|---:|---:|---|
| **Fall River WWTP** | MA | 169 kW | $538k | $179k/yr | 3.1 yr | **Primary pilot candidate.** Mid-market, high head confidence, strong economics, Northeast cluster |
| Lowell Regional WW Utility | MA | 125 kW | $482k | $131k/yr | 3.8 yr | Second Northeast target; same regional visit |
| Seneca Water Resource Recovery Facility | MD | 215 kW | $681k | $172k/yr | 4.1 yr | Mid-Atlantic, near federal agency contacts |
| Jackson Pike WRRF | OH | 206 kW | $581k | $133k/yr | 4.6 yr | Midwest anchor |
| South Austin Regional WWTP | TX | 217 kW | $684k | $138k/yr | 5.3 yr | Large municipal operator, second-largest state cohort |
| **MWRDGC Stickney WRP** | IL | 2,644 kW | $2,836k | — | 2.1 yr | Marquee scale case — largest treatment plant in the country by design flow |
| **Point Loma WWTP** | CA | 1,579 kW | $3,691k | — | 2.1 yr | **Cautionary case only.** Built, then abandoned; offline since 2018 |

All figures are modeled outputs of this project at the physics-ceiling energy tier, not measured
performance, and must be labeled as such wherever they appear.

---

## 9. Risks, and how the business model prices around them

| Risk | Evidence | Mitigation built into the model |
|---|---|---|
| **Energy yield is overstated** | Implied CF of 0.872 vs. 0.39 median across 629 real small-hydro plants, and vs. 0.2439 median across 115 metered EIA-923 conduit plants. The CF 0.60 tier rests on the Conduit 3 *design projection*, not a measurement; Point Loma, the only metered wastewater conduit plant, runs 0.1914 | Sell screening with bounds, never predicted output. Fee-based pricing, no EaaS before metered data. Show the metered tier in every deck |
| **Head estimation is the largest methodological assumption** | DEM-proxy head with a plausibility gate; 290 of 1,138 viable sites are not high-confidence | Price a paid site-visit survey as the natural second engagement; disclose confidence tier on every site |
| **No wastewater ground truth exists** | Only 11 new conduit labels nationally; the single wastewater plant offline since 2018; Phase 5 ML killed as a result | Report the negative result openly. It is the reason a pilot with metering is the first commercial milestone |
| **O&M abandonment** | Point Loma | Do not sell projects whose net cash flow cannot fund maintenance. This is the real floor on site size, tighter than the NPV gate |
| **Municipal sales cycle 18–36 months** | Journal assessment | Channel-first go-to-market; the ESCO or OEM carries the cycle, not us |
| **ESCOs internalize this capability** | They already audit these plants | Narrow window. Publishing early and signing channel partners is the defense; a data moat that takes six months to rebuild is worth roughly one year of lead |
| **Thin supply chain** | 12–18 month OEM lead times | Disclose as schedule risk; it also makes OEM lead-flow more valuable to the OEM, not less |

---

## 10. Next actions

| # | Action | Owner | Effort | Blocking? |
|---|---|---|---|---|
| 1 | **Re-run Phase 4 across the full tier ladder (optimistic 0.688 / floor 0.447 / measured 0.280 / measured 0.219) and at both discount rates.** Replaces the §2.4 reconstruction with real pipeline output; produces the defensible Ch3 numbers | Tom | ~1 session | Yes — J1 depends on it |
| 1b | **Settle the band-floor decision (118.9 vs 89.8 GWh/yr)** with the advisor — it moves every Ch3 dollar figure | Tom + advisor | 1 meeting | Yes — J1 depends on it |
| 2 | Add discount rate as a documented sensitivity band (6 % / 3.5 % / 0 %), same table shape as the existing install-% band | Tom | small | No |
| 3 | Verify every **[VERIFY]** item in §5 and §6, especially IRA elective pay | Both | ~1 session | Yes for Ch3 funding claims |
| 4 | Ten customer-validation calls per §4.3 | Both | 2 weeks | Yes for any claim that a buyer exists |
| 5 | One-page lead sheet template + per-OEM routing from `turbine_type` | Tom | 1–2 days | No |
| 6 | Draft J1 · Ch3 against this document, 8 subsections, 150–400 words each, ~2,300 words | Both | 1 session | — |

---

## 11. Consistency rules for J1

- Every dollar and energy figure in Ch3 must match the P2-SEED baseline used in Ch4 and Ch5: **17,148
  screened · 1,138 viable · 409.17 GWh/yr · $310.1M NPV · 9.8 yr median payback.**
- Wherever Ch3 uses an energy-derived dollar figure, **state which energy tier it rests on** and use the
  25 July 2026 tier names: ceiling (CF 0.872) · optimistic, Conduit 3 projection (0.600) · floor
  (0.447 / 0.291) · measured all-conduit (0.2439) · measured Point Loma (0.1914). Ch4.4 now calls 0.60
  optimistic and treats the floor as the evidenced tier; §5.1.4 says the defensible planning figure is
  the floor. A Ch3 built silently on the ceiling — or on the word "central" — contradicts Ch4 and Ch5 and
  is the single largest internal-consistency risk in the thesis.
- If the deferred decision to lower the band floor from 118.9 to 89.8 GWh/yr is taken, every dollar
  figure in Ch3 moves with it. Settle that decision before J1 is drafted, not after.
- Label every business number as an estimate, per the intellectual-honesty rules in §5 of
  `THESIS_BREAKDOWN.md`.
- Ch3.3 requires one **real named** archetype plant — use Fall River WWTP, not a composite.
