# WOWERS — Business Plan Working Document

**Status:** working document, drafted 2026-07-31; §2 and §7 re-derived from real pipeline output
2026-08-06. Feeds work package **J1 · Ch3 Business Model**.
**Owners:** Tom + Mohamed (J1 is a joint work package).

> **This file is an internal development artifact, not a citable source.** Per the rule at the top of
> `THESIS_BREAKDOWN.md`, no Markdown file in this repo may appear in the thesis reference list or in an
> inline citation. Numbers below are either (a) this project's own generated results — reported in the
> thesis as our findings — or (b) claims traceable to an external source, which must be verified and
> cited from that original source. Items needing verification before they enter the thesis are marked
> **[VERIFY]**.

**Number provenance (revised 2026-08-06).** Everything quantitative in §2 and §7 is now computed from
`data/processed/phase4/financial_scorecards.parquet` (3,778 turbine-viable sites, post-P2-SEED
baseline) and re-scored through `src.phase4.financials.compute_scorecard` — the same function Phase 4
itself calls — by `scripts/tier_ladder_whatif.py`. Full output: `TIER_LADDER_REPORT.md`. The harness
reproduces the published baseline exactly (1,138 viable · 409.17 GWh/yr · $310.13M · 9.83 yr), so the
scenario table in §2.4 is pipeline output, not a reconstruction.

**Two corrections this superseded.** The earlier draft of this file derived its numbers from
`exports/viable_sites.geojson`, which rounds `rated_power_kw` to integer kW. That rounding moved two
sites across the 100 kW boundary (giving 131 where the parquet says **129**) and shifted every size
band in §2.3. The parquet is authoritative; the geojson is a display artifact. Separately, the old
§2.4 reconstruction capped its universe at the 1,138 sites already viable at 6 %, so no scenario could
ever exceed 1,138 — which silently truncated every public-finance row. Both are fixed below.

**Multiplier ≠ capacity factor.** `config/settings.yaml phase4.cf_calibration` stores *multipliers*
(tier CF ÷ 0.872, the Phase 2 implied fleet-median CF), not capacity factors. 0.447 is a multiplier;
its capacity factor is 0.390. The earlier draft reported multipliers as CFs. Every tier below now
carries both numbers.

---

## 1. The business in one paragraph

WOWERS is a national screening and deal-origination layer for micro-hydropower energy recovery at
water infrastructure. We ingested ~279 million EPA DMR records covering 17,148 active POTWs, estimated
per-site energy with a Monte-Carlo physics model, matched commercially available turbines, and scored
every site on NPV, IRR and payback. The output is 1,138 investment-ready sites, of which the **129**
that clear 100 kW carry 81 % of the portfolio value — a **0.75 % hit rate** on the sites that actually
matter. We do not manufacture turbines, install them, or own the assets. We sell the answer to the
question that costs everyone else eighteen months: *which of these 17,148 plants is worth a site
visit.*

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

Headline energy: **409.2 GWh/yr** at the Phase 2 physics ceiling, against a calibrated band of
**89.8–281 GWh/yr** (§2.4). The ceiling is never quoted alone. Portfolio NPV **$310.1M**, portfolio
CapEx **$211.3M**, median payback **9.8 yr** — all three at the ceiling energy tier and 6 % commercial
finance.

### 2.2 The portfolio is extremely concentrated

This is the single most important fact for the business model, and it is not visible in the headline.
All rows are the viable cohort only, at the ceiling energy tier and r = 6 %.

| Cut | Sites | Energy | NPV | Share of NPV | CapEx | Median payback |
|---|---:|---:|---:|---:|---:|---:|
| All investment-ready | 1,138 | 409.2 GWh/yr | $310.1M | 100 % | $211.3M | 9.8 yr |
| Top 100 by NPV | 100 | 238.1 GWh/yr | $249.2M | 80.4 % | $83.5M | 4.7 yr |
| Sites ≥ 100 kW | **129** | 268.8 GWh/yr | $252.1M | **81.3 %** | $98.9M | **5.5 yr** |
| Sites ≥ 25 kW | 304 | 343.2 GWh/yr | $283.1M | 91.3 % | $162.7M | 8.4 yr |
| Sites < 25 kW | 834 | 66.0 GWh/yr | $27.0M | 8.7 % | $48.6M | 10.1 yr |

Median investment-ready site: **13.0 kW · $66.4k CapEx · $8.6k/yr revenue · $29.7k NPV · 9.8 yr
payback.** Median site ≥ 100 kW: **169.0 kW · $552.1k CapEx · $119.2k/yr revenue · 5.5 yr payback.**

**129 sites carry 81.3 % of the value.** Everything downstream — pricing, sales motion, pilot selection
— follows from this. Note that the concentration claim is *unchanged* by the correction from 131 to 129;
what changed is that the count is now traceable to the parquet rather than to a rounded export.

### 2.3 Composition of the viable set

| Dimension | Breakdown |
|---|---|
| Size bands | < 10 kW: 415 · 10–25 kW: 419 · 25–100 kW: 175 · 100–250 kW: 87 · 250–1,000 kW: 37 · > 1,000 kW: 5 |
| Permitting tier | qualified facility 834 · small FERC 262 · full NEPA 42 |
| Turbine type | Crossflow 654 · Kaplan 256 · Francis 228 |
| Head confidence | high-confidence viable 848 of 1,138 |
| Top states | CA 147 · TX 102 · MA 62 · OH 53 · PA 53 · CT 47 · IL 47 · NY 45 · NC 44 · NJ 38 |

The size bands sum to 1,138 and are computed on unrounded `rated_power_kw`. The earlier
geojson-derived bands (391 / 439 / 177 / 89 / 37 / 5) also summed to 1,138, which is exactly why the
rounding error survived a total check — the sites moved between adjacent bands rather than disappearing.

Geographic concentration matters commercially: CA + TX + the Northeast corridor (MA/CT/NY/NJ/PA) hold a
large share of viable sites, which makes a regional pilot campaign cheap relative to a national one.

### 2.4 Public-sector finance is the correct lens — and it rescues the long tail

The Phase 4 model uses `discount_rate: 0.06`, a commercial rate. A public owner borrows on tax-exempt
municipal debt and, for water infrastructure, often at 0–2 % through the Clean Water State Revolving
Fund, sometimes with principal forgiveness. `scripts/tier_ladder_whatif.py` re-scores all 3,778
turbine-viable sites through the pipeline's own financial model across six energy tiers × four discount
rates × two subsidy levels.

**Rate correction (verified 2026-08-06).** The earlier draft used 3.5 % as "the" municipal rate. That is
**not** the current market rate: the AAA 30-year municipal benchmark was **4.25 %** in April 2026, and
AA-category water/sewer revenue bonds trade at a **40–60 bp** spread over MMD AA, putting a real
30-year municipal water/sewer revenue bond near **4.6–4.9 %**. The ladder therefore now runs four rates:
6.0 % commercial · **4.75 % market municipal** · 3.5 % below-market/partially-subsidised · 0 % CWSRF with
principal forgiveness. Quote 4.75 % as the municipal market case and reserve 3.5 % and 0 % for the
subsidised cases they actually represent. Because bond yields move daily, the thesis must cite a **dated**
MMD or Bond Buyer observation rather than a standing number.

**The tier ladder.** Tier labels follow the thesis as re-labeled on 25 July 2026, not
`CF_CALIBRATION_REPORT.md`, which is stale. CF 0.60 is the **optimistic** upper tier resting on the
Conduit 3 *design projection*, not a central estimate.

| Tier | CF | Multiplier | Band energy | Evidence |
|---|---:|---:|---:|---|
| Ceiling (Phase 2 as-modeled) | 0.8720 | 1.0000 | 409.2 GWh/yr | none — physics upper bound |
| Optimistic (Conduit 3 proj.) | 0.5999 | 0.6880 | 281.5 GWh/yr | one design projection, never metered |
| River-hydro median | 0.3898 | 0.4470 | 182.9 GWh/yr | 629 EHA river plants, wrong plant class |
| River-hydro p25 | 0.2538 | 0.2910 | 119.1 GWh/yr | 629 EHA river plants, p25 |
| Measured all-conduit | 0.2439 | 0.2797 | 114.4 GWh/yr | **115 metered EIA-923 conduit plants** |
| **Band floor — measured Point Loma** | **0.1914** | **0.2195** | **89.8 GWh/yr** | **only metered treated-wastewater conduit plant in the U.S.** |

**Band-floor decision (Tom, 2026-08-06): the reported band moves to 89.8–281 GWh/yr.** The previously
reported 119–281 rested on the river-hydro p25 — a plant class that is not ours. Point Loma is the only
metered treated-wastewater conduit plant in the country, so it becomes the floor. Note this also
*strengthens* the double-sourcing argument rather than weakening it: the two independent datasets
(river-hydro p25 at 119.1 and metered all-conduit at 114.4) still agree to 4.7 GWh/yr, and the new floor
sits below both. **Advisor sign-off is still outstanding on this** — it was the recorded precondition,
and it must be settled before Ch3 is submitted, not merely before it is drafted.

**Band energy vs re-scored energy — do not swap these.** "Band energy" applies the multiplier to the
fixed 409.17 GWh/yr baseline cohort; that is the calibration band. "Viable GWh" below is the energy of
the sites that remain *viable at that tier*, which is smaller because harsh tiers eject sites from the
portfolio entirely. The old draft of this file blurred the two.

**Commercial finance — r = 6 %, no grant.**

| Tier | Viable | Viable GWh | Portfolio NPV | Median payback | ≥ 100 kW |
|---|---:|---:|---:|---:|---:|
| Ceiling | 1,138 | 409.2 | $310.1M | 9.8 yr | 129 |
| Optimistic | 439 | 213.8 | $152.6M | 10.4 yr | 117 |
| River-hydro median | 129 | 96.0 | $59.4M | 10.7 yr | 66 |
| River-hydro p25 | 27 | 30.0 | $19.0M | 10.6 yr | 26 |
| Measured all-conduit | **24** | 28.2 | $16.9M | 11.0 yr | 23 |
| **Band floor (Point Loma)** | **12** | 14.9 | $7.1M | 11.6 yr | 12 |

**Market municipal finance — r = 4.75 % + 50 % grant.** This is the realistic public-owner case and the
one to lead with.

| Tier | Viable | Viable GWh | Portfolio NPV | Median payback | ≥ 100 kW |
|---|---:|---:|---:|---:|---:|
| Ceiling | 3,095 | 504.0 | $533.8M | 8.2 yr | 131 |
| Optimistic | **1,938** | 326.2 | $302.2M | 9.8 yr | 131 |
| River-hydro median | 822 | 167.8 | $141.0M | 11.2 yr | 127 |
| River-hydro p25 | 240 | 77.8 | $59.2M | 11.3 yr | 99 |
| Measured all-conduit | 216 | 71.3 | $54.2M | 11.3 yr | 88 |
| **Band floor (Point Loma)** | **107** | 44.1 | $30.4M | 12.3 yr | 59 |

**Deeply-subsidised municipal finance — r = 3.5 % + 50 % grant.** Use only where a state SRF actually
lends below market.

| Tier | Viable | Viable GWh | Portfolio NPV | Median payback | ≥ 100 kW |
|---|---:|---:|---:|---:|---:|
| Ceiling | 3,354 | 507.3 | $646.0M | 8.7 yr | 131 |
| Optimistic | **2,272** | 335.4 | $374.2M | 10.6 yr | 131 |
| River-hydro median | 1,050 | 181.5 | $179.3M | 12.6 yr | 129 |
| River-hydro p25 | 316 | 83.1 | $77.4M | 13.0 yr | 106 |
| Measured all-conduit | 280 | 77.5 | $71.2M | 12.9 yr | 104 |
| **Band floor (Point Loma)** | **142** | 47.9 | $41.1M | 13.6 yr | 67 |

The full 48-scenario grid, including the 0 % CWSRF rows, is in `TIER_LADDER_REPORT.md`.

Four conclusions, and the first is uncomfortable:

1. **At the only metered evidence we have, the commercial case nearly disappears — 12 sites, not 1,138.**
   Do not build a pitch on the ceiling or the optimistic tier. The defensible commercial claim at the
   band floor is **twelve sites nationally** under conventional finance, or two dozen at the metered
   all-conduit median.
2. **Public finance is what makes the portfolio exist at all**, and by more than the old draft claimed.
   At the realistic market municipal rate with a 50 % subsidy, the band floor goes from 12 to **107
   sites** and the optimistic tier from 439 to **1,938** — figures the old reconstruction could not
   produce because it capped its universe at 1,138. That is the difference between the business existing
   and not existing, and it makes §6.1 the most important section of this document. Note the subsidy, not
   the rate, is doing most of the work: dropping 6.0 % → 4.75 % alone moves the floor from 12 to 17 sites,
   while adding the 50 % grant at 4.75 % moves it from 17 to 107.
3. **The ≥ 100 kW cohort survives every tier.** All 12 commercially viable sites at the band floor are
   ≥ 100 kW, as are 59 of the 107 under market municipal finance. The concentration argument in §2.2 is
   robust to the harshest energy assumption in the thesis — the long tail is not. Target the head at
   every tier.
4. **Subsidy moves site count; discount rate moves NPV.** Payback is undiscounted, so the rate does not
   touch it at all — only the grant does. Any claim of the form "municipal financing shortens payback to
   X" is wrong on the model's own terms unless the X comes from the subsidy. This is the specific error
   the old draft made (see §7.2).

The existing `npv_with_50pct_grant_usd` column corroborates the subsidy direction independently, and the
two ways of reading it are both correct provided the cohort is stated: over the fixed 1,138
baseline-viable sites, NPV rises $310.1M → **$415.8M**; over the 2,751 sites that *become* viable at the
ceiling tier once the grant applies, it is **$444.5M**. Quote one or the other with its cohort named,
never the larger number against the smaller cohort's site count.

### 2.5 Why the small sites still don't become customers

| Cohort | n | Median revenue | Median opex | **Median net cash flow** |
|---|---:|---:|---:|---:|
| < 25 kW | 834 | $6,436/yr | $789/yr | **$5,610/yr** |
| ≥ 100 kW | 129 | $119,192/yr | $6,537/yr | **$112,842/yr** |

A 13 kW project and a 500 kW project require the same interconnection study, the same procurement, the
same council approval, the same FERC conduit filing, and the same maintenance visit to a debris-laden
effluent stream. That fixed overhead does not scale down. $5,610/yr does not fund a maintenance
contract; $112,842/yr does.

And these are the *ceiling-tier* cash flows. At the band floor the median sub-25 kW site earns **$1,413
of revenue and $593 of net cash flow per year** — because the constant O&M line eats a far larger share
of a smaller revenue, the net collapses to about a ninth of its ceiling-tier value while revenue falls
only to a fifth. $593/yr is not a business for anyone, at any discount rate, under any subsidy. The long
tail is not a market that public finance rescues; it is a market that does not exist once the energy
assumption is honest.

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

Start from the 129 sites ≥ 100 kW, concentrated in ~10 states. Every conversion rate below is an
assumption, not an observation — the ten calls in §4.3 are what would replace them with evidence.

| Stage | Conversion | Count |
|---|---:|---:|
| Bankable sites identified | — | 129 |
| Reachable in first-wave states (CA, TX, MA, IL, OH, PA, NY, CT, NJ, NC) | ~70 % | ~90 |
| Contacted, first meeting held | 40 % | ~36 |
| Paid screening engagement | 30 % | ~11 |
| Reaches financial close within 5 yr | 25 % | ~3 |

Three closed projects over five years, at the median ≥ 100 kW CapEx of $552.1k, is $1.7M of hardware
moved. Add screening fees and channel subscriptions and the five-year revenue picture is roughly
**$0.5–1.2M** — a consulting and data business for two people, not a venture-scale company. §7 says this
out loud rather than hiding it.

Note the funnel starts from the *ceiling-tier* bankable set. At the band floor under market municipal
finance the ≥ 100 kW bankable count is **59**, not 129, and the same conversion chain yields roughly one
closed project rather than three. Both versions belong in the thesis; only the second one is defensible
without an energy assumption we cannot evidence.

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
| **Screening report** — per-utility custom run, per-site detail, sensitivity bands, methodology appendix | $8–15k | Roughly 1 % of the median NPV of a 100–250 kW site (~$1.1M). **Audit benchmark corrected:** an ASHRAE Level 2 energy audit runs ~$1.8–10k, not the $15–50k previously claimed, so the audit comparison no longer supports this price — see note below |
| **Data subscription** — filtered national database access for OEMs, ESCOs, consultants | $1–2k/month | Value ceiling of ~30 qualified leads/yr at $3k per qualified lead ≈ $90k/yr; priced well under that to make the buy trivial. The $3k/lead figure is still an assumption, not a sourced market rate |
| **Origination success fee** — paid on financial close | 2–4 % of project CapEx | Claimed as a standard developer origination band; **no authoritative public source found** — treat as an assumption until a real term sheet or trade-association schedule is obtained. At the corrected median ≥ 100 kW CapEx of **$552.1k** the band is **$11.0–22.1k** per closed project |
| **State / agency data layer** — GIS exports, white-label report, state-specific overlays | $25–75k per engagement | Scaled to typical state energy-office study procurement; **still unverified** — settle by pulling two real state energy-office RFPs and citing their award values |
| **Grant-funded methodology work** | $50–305k | **Verified:** NSF SBIR Phase I awards are **$305,000** (NSF America's Seed Fund Phase I awardee record, 2025 awards); Phase II up to $1,250,000 |

**On the screening-report price.** The audit benchmark was the weaker of the two derivations and it did
not survive verification: published ASHRAE Level 2 audit pricing is roughly $1.8–10k for commercial
buildings and around $10k for industrial facilities. The $15–50k figure most likely described an
*investment-grade audit* for a performance contract, which is a different product — but we could not
source that either, so it must not be quoted. The price should stand on the NPV-share derivation alone
(1 % of ~$1.1M median NPV for a 100–250 kW site), which is intact, or be re-anchored against a sourced
investment-grade-audit or feasibility-study price. Do not present a corrected number as if the original
benchmark had held.

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
| **EPA Clean Water State Revolving Fund (CWSRF)** | State-administered revolving loans for wastewater capital; below-market or 0 % interest, principal forgiveness available in many states | **Primary.** This is the money that actually buys POTW capital equipment | **Verified:** EPA lists energy efficiency/conservation at POTWs as an eligible category, and the eligible-project list explicitly includes **"onsite renewable energy"**. **Precision required:** the examples given are wind and solar — hydropower is *not* named. Claim eligibility under "onsite renewable energy", never claim hydro is explicitly enumerated. State-by-state principal-forgiveness terms remain unverified |
| **EPA WIFIA** | Low-cost federal direct loans for larger water infrastructure | Only for the top of the portfolio — in practice, none of it | **Verified:** minimum project size is **$20M for large communities and $5M for small communities (population ≤ 25,000)**; WIFIA funds at most 49 % of eligible costs, total federal assistance ≤ 80 %. Our largest single site is $3.7M of CapEx, so **WIFIA is out of reach for every individual site** — it is only relevant to a bundled multi-site program |
| **USDA Rural Development — Water & Waste Disposal Loan & Grant** | Grants + loans for water systems in communities under 10,000 population | Fits a meaningful slice of the small-site tail | **Verified:** serves communities of **10,000 or fewer**; grant share is needs-based (median household income plus a project financial analysis), with the poorest communities eligible for up to **75 %** grant. Not a fixed percentage — do not quote one |
| **IRA elective ("direct") pay for clean-energy tax credits** | Lets tax-exempt entities receive the value of the ITC/PTC as a cash payment | **Confirmed as the single largest lever, and it survived the 2025 legislation.** | **Verified, and better than we assumed.** (1) Elective pay under IRC §6417 is live; applicable entities include state/local governments and tax-exempt organisations, with mandatory IRS pre-filing registration. (2) Hydropower **retained full §48E eligibility** under the One Big Beautiful Bill Act (2025): 100 % of the credit if construction begins by end-2033, phasing 75 %/50 % in 2034/2035 and expiring for 2036 starts. (3) The §48E rate is **30 %** with prevailing-wage and apprenticeship compliance — and facilities with maximum net output **under 1 MW (AC) are exempt from the PWA requirement**, so they reach 30 % without it. (4) **The domestic-content phaseout on elective pay also exempts sub-1 MW facilities.** See the note below — this is the most consequential thing verified in this pass |
| **State energy office programs / utility rebates / on-bill financing** | State-level capital grants and utility efficiency incentives | Varies enormously by state; CA, MA, NY are strongest | Check per state against the top-10 list in §2.3 |
| **ESPC / ESCO performance contract** | ESCO funds the capital and is repaid from verified savings | Removes the municipal capital request entirely | Reinforces the ESCO-as-channel strategy in §3 |
| **Third-party PPA / developer ownership** | A developer owns the asset, the utility buys the power | Bypasses municipal capital cycles | Requires a developer partner willing to take yield risk |

### 6.1.1 The 1 MW threshold is the most valuable single fact in this document

Elective pay carries a phaseout: an applicable entity claiming an ITC or PTC gets a **reduced** credit if
the facility "does not satisfy the domestic content requirement **or** does not have maximum net output of
less than 1 megawatt." Read the disjunction carefully — a facility **under 1 MW (AC) is outside the
domestic-content phaseout entirely**, and separately is exempt from the prevailing-wage and apprenticeship
requirement while still reaching the full 30 % rate.

**This is decisive for WOWERS, because the portfolio is almost entirely sub-1 MW.** Of 1,138
investment-ready sites, **1,133 are under 1 MW** and only 5 exceed it. So:

- For 1,133 of 1,138 sites, a municipal owner can stack a **0–2 % CWSRF loan with principal forgiveness**
  *and* a **30 % §48E credit paid in cash via elective pay**, with **no domestic-content exposure and no
  prevailing-wage compliance burden** — and the European supply chain named in §7.3 as a schedule risk
  creates no tax-credit risk at this scale.
- For the 5 sites above 1 MW — including **both marquee pitch sites, Stickney (2,644 kW) and Point Loma
  (1,579 kW)** — the domestic-content phaseout and the PWA requirement both bite, and a European turbine
  becomes a live tax-credit problem, not just a lead-time problem. IRS Notice 2024-84 extends a transition
  attestation for construction beginning before the later of 1 January 2027 or further guidance, and
  statutory exceptions exist where domestic products would raise construction cost by more than 25 % or
  are unavailable in sufficient quantity or quality.
- Independently, hydro projects commencing construction in **2026 or later** must comply with "material
  assistance" restrictions on prohibited foreign entities to keep §48E eligibility. This is a
  supplier-nationality compliance question and is **not** answered by the sub-1 MW exemptions above.
  **[VERIFY]** the precise material-assistance thresholds against statutory text before any pitch relies
  on a specific supplier.

The uncomfortable symmetry is worth stating plainly: the small sites get the cleanest tax treatment and
have no economics; the large sites have the economics and inherit the full compliance load.

**Pitch consequence:** never lead with "the project costs $552k." Lead with "the project costs $552k, of
which a CWSRF loan at 0–2 % covers the whole amount, principal forgiveness is available in many states,
and against a 30-year asset life the median site of this size pays back in **4.1 years at the optimistic
energy tier and 10.5 years at the evidenced floor** — both with a 50 % capital subsidy applied."

Quote the pair, never the single number. The spread *is* the honest content: it tells the owner the
project is robust under a subsidy and tells them exactly which assumption they are betting on. Note
also that payback is undiscounted in this model, so the loan rate changes the NPV and the *affordability*
of the capital request, not the payback year — say so rather than implying cheap debt shortens payback.

### 6.2 Capital that funds *WOWERS* (company-side)

The honest recommendation is **non-dilutive first, and probably non-dilutive only.**

| Source | Amount | Why it fits |
|---|---|---|
| **NSF SBIR Phase I** | **$305k** (verified) | The methodology *is* the proposal. 736 passing tests, a documented calibration band, and a published negative result are exactly the reproducibility posture these programs reward. Phase II follows at up to $1.25M |
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
> 17,148 plants, 279 million discharge records — and found 129 sites that carry 81 % of the value. We
> don't build turbines. We tell you which of the seventeen thousand is worth a site visit."

### 7.2 Five-slide structure

1. **The number nobody has.** 17,148 POTWs, 279M DMR rows, 409.2 GWh/yr of physically recoverable energy
   at the modeled ceiling — and, once real capacity factors are substituted in, a calibrated band of
   **89.8–281 GWh/yr**, floored on the only metered treated-wastewater conduit plant in the country and
   corroborated by 115 metered conduit plants at 114.4. We report the band, not the ceiling. Nobody else
   has computed either.
2. **Why it hasn't been done.** The hit rate is 0.75 %. See §7.3.
3. **The concentrated prize.** 129 sites, $98.9M CapEx, $252.1M owner NPV, median payback 5.5 yr at the
   ceiling tier. Under municipal finance with a 50 % subsidy that cohort's median payback is **4.1 yr at
   the optimistic tier and 10.5 yr at the band floor**, and 67 of the sites stay viable even at the floor.
   Show the funnel and the concentration table, and show the floor row — a deck that shows only the
   ceiling row will not survive a technical question.
4. **How we make money.** Channel first (OEM/ESCO), reports and origination fees second. Show §5 with the
   derivations visible.
5. **What we've actually built vs. what we haven't.** A running 4-phase pipeline, 736 passing tests, a
   published calibration band, a live national dashboard — and no measured wastewater ground truth, no
   pilot, no signed channel partner yet. Naming the gaps is what makes the rest believable.

### 7.3 Answers to the four Fowler gaps

**"Why isn't this already done?"** — Now answerable with evidence rather than assertion:

1. The hit rate is **129 in 17,148 = 0.75 %**. Until public bulk data and cheap compute existed, the
   search cost exceeded the prize. Screening one plant by consultant costs thousands; screening all of
   them now costs roughly nothing.
2. A nationwide search of FERC and DOE EHA records found **exactly one** wastewater conduit plant with
   measured generation — Point Loma — and it has been offline since 2018. The category is genuinely
   unexploited, and the absence of records is itself the finding.
3. **73.3 % of paper-viable sites are under 25 kW.** Anyone who looked at the aggregate saw a market of
   thousands of tiny uneconomic projects and rationally walked away. The value is concentrated in a head
   that only appears once you rank the whole population — which is what we did.

**"Manufacturing, shipping, installation logistics?"** — We are not in that path. Equipment comes from
existing OEMs with existing U.S. channels; our CapEx model carries equipment, installation at 17.5 % of
equipment, interconnection, and permitting as separate lines totaling $353.5M across the scored set. The
honest constraint to state: the micro-hydro supply chain is thin, with 12–18 month lead times from small
European manufacturers. That is a schedule risk we disclose, not one we solve. It is **only** a schedule
risk below 1 MW — the sub-1 MW domestic-content exemption (§6.1.1) means a European turbine costs a small
site nothing in tax credit. Above 1 MW it becomes a tax-credit risk as well, which is a second reason the
two marquee sites need different handling from the other 1,133.

**"Named pilot?"** — See §8. Name a real plant, with its real modeled numbers.

**"Named government funding?"** — See §6.1, now verified rather than asserted. Lead with the stack that
actually applies to 1,133 of the 1,138 sites: a **CWSRF** loan at 0–2 % with principal forgiveness
available in many states (energy conservation at POTWs is an eligible category, and "onsite renewable
energy" is an enumerated eligible project type), plus a **30 % §48E credit taken as cash through IRA
elective pay** — with no domestic-content exposure and no prevailing-wage burden below 1 MW. Add **USDA
Rural Development** for communities of 10,000 or fewer, where needs-based grants reach up to 75 %. Name
**DOE WPTO** for methodology funding. **Do not** name WIFIA as a project funding source: its minimum
project size is $20M ($5M for communities ≤ 25,000) and our largest single site is $3.7M of CapEx, so it
cannot fund any individual project. State-by-state SRF forgiveness terms still need per-state verification.

### 7.4 Five things never to say

- Do not quote $310.1M as "our market." It is the net present value accruing to *plant owners*, not
  revenue to WOWERS. Conflating them is the fastest way to lose a technical audience.
- Do not quote the 409.2 GWh/yr ceiling without the calibrated band beside it. Ch4.4 exists; a business
  chapter that ignores it contradicts the thesis it sits in.
- Do not present Point Loma as a live flagship installation. It is offline. It is a cautionary case and
  should be presented as one.
- Do not attach a site count to one energy tier and a payback or NPV to another. Every quoted number
  carries a tier and a finance assumption; the 2026-08-06 re-run exists because the previous draft of
  this file attached a ceiling-tier payback (7.5 yr) to a floor-tier argument.
- Do not quote any figure derived from `exports/viable_sites.geojson`. It rounds `rated_power_kw` to
  integer kW, which is how "131 sites" entered this document. The parquet is the source of record.

---

## 8. Named pilot targets

Selection criteria: ≥ 100 kW, high head confidence, payback under 5 years at the ceiling tier, and a
large operator with in-house engineering capacity.

Payback is shown at three assumptions: the ceiling tier at 6 % (**Ceil**), the band floor at 6 % with no
subsidy (**Floor**), and the band floor under municipal finance with a 50 % capital subsidy (**Floor+**).

| Site | State | Rated | CapEx | Revenue | Ceil | Floor | Floor+ | Role in the pitch |
|---|---|---:|---:|---:|---:|---:|---:|---|
| **Fall River WWTP** | MA | 169.0 kW | $538k | $179k/yr | 3.1 yr | 16.8 yr | **8.3 yr** | **Primary pilot candidate.** Mid-market, high head confidence, Northeast cluster |
| Lowell Regional WW Utility | MA | 124.9 kW | $482k | $131k/yr | 3.8 yr | 21.2 yr | 10.5 yr | Second Northeast target; same regional visit |
| Seneca Water Resource Recovery Facility | MD | 215.5 kW | $681k | $172k/yr | 4.1 yr | 23.3 yr | 11.5 yr | Mid-Atlantic, near federal agency contacts. Disambiguate from MET COUNCIL – SENECA WWTP (MN) |
| Jackson Pike WRRF | OH | 206.1 kW | $581k | $133k/yr | 4.6 yr | 27.8 yr | 13.6 yr | Midwest anchor |
| South Austin Regional WWTP | TX | 216.9 kW | $684k | $138k/yr | 5.3 yr | never | 15.5 yr | Large municipal operator, second-largest state cohort |
| **MWRDGC Stickney WRP** | IL | 2,644.2 kW | $2,836k | $1,404k/yr | 2.1 yr | 11.2 yr | 5.6 yr | Marquee scale case — largest treatment plant in the country by design flow. **Not high head confidence** |
| **Point Loma WWTP** | CA | 1,579.5 kW | $3,691k | $1,834k/yr | 2.1 yr | 10.8 yr | 5.4 yr | **Cautionary case only.** Built, then abandoned; offline since 2018. **Not high head confidence** |

All figures are modeled outputs of this project, not measured performance, and must be labeled as such
wherever they appear.

**Two things this table says that the pitch must not hide.**

1. **None of the five mid-market candidates survives the band floor on commercial terms.** Fall River
   goes from 3.1 yr to 16.8 yr; South Austin never pays back inside 30 years. Every one of them returns
   to a defensible payback *only* once a 50 % capital subsidy is applied — which is precisely why §6.1 is
   load-bearing and why the first pilot must come with a funding path attached, not after one.
2. **The two sites that survive the floor unaided are the two that fail the head-confidence criterion.**
   Stickney and Point Loma clear the floor at 11.2 yr and 10.8 yr, but both are outside the
   `project_viable_high_confidence` set, so their head estimates rest on the DEM proxy without measured
   corroboration. The scale that makes them robust to the energy assumption is not matched by confidence
   in the head assumption. Do not resolve this tension by dropping the criterion — state it, and make a
   head survey the first deliverable at either site.

Fall River remains the recommended primary pilot: it is the best combination of high head confidence,
mid-market scale, and a Northeast cluster that makes a single trip cover two candidates. But it is a
pilot that needs CWSRF or an equivalent subsidy in the conversation from the first meeting.

---

## 9. Risks, and how the business model prices around them

| Risk | Evidence | Mitigation built into the model |
|---|---|---|
| **Energy yield is overstated** | Implied CF of 0.872 vs. 0.39 median across 629 real small-hydro plants, and vs. 0.2439 median across 115 metered EIA-923 conduit plants. The CF 0.60 tier rests on the Conduit 3 *design projection*, not a measurement; Point Loma, the only metered wastewater conduit plant, runs 0.1914 and is now the reported band floor | Sell screening with bounds, never predicted output. Fee-based pricing, no EaaS before metered data. Show the floor tier in every deck. Quantified: at the floor, commercial viability falls to 12 sites (§2.4) — this is the risk that most moves the business |
| **Head estimation is the largest methodological assumption** | DEM-proxy head with a plausibility gate; 290 of 1,138 viable sites are not high-confidence — including both sites that survive the band floor unaided (§8) | Price a paid site-visit survey as the natural second engagement; disclose confidence tier on every site. Make a head survey the first deliverable at any large-plant pilot |
| **No wastewater ground truth exists** | Only 11 new conduit labels nationally; the single wastewater plant offline since 2018; Phase 5 ML killed as a result | Report the negative result openly. It is the reason a pilot with metering is the first commercial milestone |
| **O&M abandonment** | Point Loma | Do not sell projects whose net cash flow cannot fund maintenance. This is the real floor on site size, tighter than the NPV gate |
| **Municipal sales cycle 18–36 months** | Journal assessment | Channel-first go-to-market; the ESCO or OEM carries the cycle, not us |
| **ESCOs internalize this capability** | They already audit these plants | Narrow window. Publishing early and signing channel partners is the defense; a data moat that takes six months to rebuild is worth roughly one year of lead |
| **Thin supply chain** | 12–18 month OEM lead times | Disclose as schedule risk; it also makes OEM lead-flow more valuable to the OEM, not less |

---

## 10. Next actions

| # | Action | Owner | Effort | Blocking? |
|---|---|---|---|---|
| 1 | ~~Re-run Phase 4 across the full tier ladder and at both discount rates~~ **DONE 2026-08-06.** `scripts/tier_ladder_whatif.py`, 36 scenarios, output in `TIER_LADDER_REPORT.md`; baseline reproduces exactly. §2 and §7 rewritten against it | Tom | done | — |
| 1b | ~~Settle the band-floor decision (118.9 vs 89.8 GWh/yr)~~ **DECIDED 2026-08-06 (Tom): band moves to 89.8–281 GWh/yr.** Advisor sign-off still outstanding — was the recorded precondition and must land before Ch3 is submitted | Tom + advisor | 1 meeting | Yes — before submission |
| 1c | ~~Propagate the 89.8 floor beyond this file~~ **DONE 2026-08-06.** Added as a fourth pipeline tier rather than overwriting `floor_p25`: `settings.yaml` gains `measured_point_loma: 0.2195`, `add_calibrated_energy_cols` emits `energy_kwh_calib_measured_point_loma`, Phase 4 re-run (49 → 50 cols, all pre-existing columns byte-identical, baseline unchanged), both geojson files re-exported at **59 properties**, `test_calib_cols.py` + `test_export_geojson.py` + `frontend/src/lib/data.ts` updated, and 119–281 replaced throughout `thesis_tom.tex` (Ch2, Ch4.1, Ch4.4, Ch4.5, Ch5.1.4, Ch6, App. A) and `thesis_moh.tex` (contract count). Fleet floor = **89.81 GWh/yr**. Tests 737 pass; frontend builds | Tom | done | — |
| 2 | ~~Add discount rate as a documented sensitivity band (6 % / 3.5 % / 0 %)~~ **Data exists** in `TIER_LADDER_REPORT.md`; still needs writing up as a thesis sensitivity table in the install-% band's shape | Tom | small | No |
| 3 | ~~Verify every **[VERIFY]** item in §5 and §6~~ **7 of 10 verified 2026-08-06** (IRA elective pay + §48E + the 1 MW threshold, CWSRF eligibility, WIFIA thresholds, USDA RD grant share, NSF SBIR ceiling, municipal bond yields, ASHRAE audit pricing). **3 still open:** developer origination-fee band, state energy-office study procurement scale, and the $3k/qualified-lead assumption — none has an authoritative public source yet | Both | ~half session | Yes for the 3 open items |
| 3b | **Collect citable sources for the 7 verified items.** Each was verified from a primary or near-primary web source this session, but the thesis needs the formal citation (agency page, IRS notice, statute, NSF award record) captured with access date. Per the no-internal-citation rule, Ch3 cannot cite this file | Tom | 1–2 hours | Yes — before Ch3 submission |
| 3c | **Verify the §48E "material assistance" / prohibited-foreign-entity thresholds** for hydro construction starting 2026+ against statutory text. This is the one IRA question that the sub-1 MW exemptions do *not* answer, and it bears directly on recommending European OEMs | Tom | ~2 hours | Yes for any supplier-specific claim |
| 4 | Ten customer-validation calls per §4.3 | Both | 2 weeks | Yes for any claim that a buyer exists |
| 5 | One-page lead sheet template + per-OEM routing from `turbine_type` | Tom | 1–2 days | No |
| 6 | ~~Draft J1 · Ch3 against this document~~ **DONE 2026-08-06.** All 8 sections written into `thesis_tom.tex`, **2,283 words**, every section inside 150–400. 8 new bibliography entries for the funding claims; 29 cited keys / 29 bibitems, none missing or unused, no internal `.md` cited. Compiles: 0 errors, 0 undefined citations, 100 pages | Both | done | — |

---

## 10a. Verification log — 2026-08-06

What was checked, what it said, and what changed. **These are working notes, not citations.** Per the
no-internal-citation rule, Ch3 must cite the underlying agency page, statute, notice or award record
directly, with an access date — see next-action 3b.

| Claim as written before | Verified finding | Source consulted | Effect |
|---|---|---|---|
| CWSRF: "energy efficiency at treatment works is an explicitly eligible category" | True, and the eligible-project list includes "onsite renewable energy". Hydro is **not** named; examples given are wind and solar | EPA, *Clean Water State Revolving Fund (CWSRF): Energy Conservation* (page updated 2026-01-28) | Kept, with the precision that hydro qualifies *under* onsite renewable energy, not by name |
| WIFIA "irrelevant below ~$20M" | $20M minimum for large communities, **$5M for small communities (≤ 25,000 pop)**; ≤ 49 % of eligible costs from WIFIA, ≤ 80 % total federal | EPA, *What is WIFIA?* | Strengthened: our largest site is $3.7M CapEx, so WIFIA cannot fund **any** individual site |
| USDA RD "grant share can be substantial" | Communities ≤ 10,000; needs-based, up to **75 %** for the poorest communities; determined by income plus project financial analysis | USDA Rural Development, Water & Waste Disposal Loan & Grant Program | Quantified; flagged that no fixed percentage may be quoted |
| IRA elective pay — status unknown, flagged highest priority | Live under IRC §6417; pre-filing registration mandatory. §48E **retained in full for hydropower** under OBBBA (100 % if construction begins by end-2033). Rate **30 %** with PWA; **sub-1 MW exempt from PWA**. Elective-pay phaseout applies unless facility satisfies domestic content **or** is under 1 MW | IRS, *Elective pay and transferability*; IRS Notice 2024-84; IRS Pub. 5817-G; §48E PWA guidance; National Hydropower Association analysis of OBBBA | **Largest finding of the pass.** 1,133 of 1,138 sites are sub-1 MW → clean 30 % credit, no domestic-content exposure. New §6.1.1 |
| Municipal rate "roughly 3.5 %" | AAA 30-year municipal benchmark **4.25 %** (April 2026); AA water/sewer revenue bonds at **40–60 bp** over MMD AA → ~4.6–4.9 % | Municipal market commentary, 2026 | **Corrected.** Ladder re-run with a 4.75 % market-municipal rate; 3.5 % relabelled as below-market/subsidised |
| NSF SBIR Phase I "~$275k" | **$305,000**; Phase II up to $1,250,000 | NSF America's Seed Fund, Phase I awardee records (2025 awards) | Corrected upward |
| "typical ESCO energy audit at $15–50k" | ASHRAE Level 2 audits ~**$1.8–10k** commercial, ~$10k industrial. No source found for $15–50k | ASHRAE Level 2 audit pricing, multiple vendors | **Benchmark withdrawn.** Screening-report price now rests on the NPV-share derivation alone |
| Origination fee "2–4 %, standard band" | No authoritative public source found | — | Downgraded to a labelled assumption |
| State data layer "$25–75k, typical procurement" | No authoritative public source found | — | Downgraded; needs two real state RFPs |
| Data subscription "$3k per qualified lead" | Not verified | — | Labelled as an assumption |

Net: **7 of 10 verified, 2 corrected against us (muni rate, audit benchmark), 1 corrected strongly in our
favour (IRA elective pay), 3 still unsourced.** The pattern worth noting for the thesis: every number that
made the business look better than assumed came from a statute or agency page, and every number that made
it look worse came from a market rate we had guessed. That is the expected direction when guesses are
replaced by sources, and it is why §5's remaining three assumptions should be treated as probably
optimistic until sourced.

---

## 11. Consistency rules for J1

- Every dollar and energy figure in Ch3 must match the P2-SEED baseline used in Ch4 and Ch5: **17,148
  screened · 1,138 viable · 409.17 GWh/yr · $310.1M NPV · 9.8 yr median payback.**
- **Use the parquet, never the geojson.** `data/processed/phase4/financial_scorecards.parquet` is the
  source of record. `exports/viable_sites.geojson` rounds `rated_power_kw` to integer kW, which produced
  the wrong cohort counts (131 not 129) and the wrong size bands in the pre-2026-08-06 draft of this file.
- Wherever Ch3 uses an energy-derived dollar figure, **state which energy tier it rests on**, and give
  both the capacity factor and the multiplier so the two cannot be confused. Tier names per the 25 July
  2026 relabel: ceiling (CF 0.8720, ×1.0000) · optimistic, Conduit 3 projection (CF 0.5999, ×0.6880) ·
  river-hydro median (CF 0.3898, ×0.4470) · river-hydro p25 (CF 0.2538, ×0.2910) · measured all-conduit
  (CF 0.2439, ×0.2797) · **band floor, measured Point Loma (CF 0.1914, ×0.2195)**. Ch4.4 calls 0.60
  optimistic and treats the floor as the evidenced tier; §5.1.4 says the defensible planning figure is
  the floor. A Ch3 built silently on the ceiling — or on the word "central" — contradicts Ch4 and Ch5 and
  is the single largest internal-consistency risk in the thesis.
- **The reported band is 89.8–281 GWh/yr** as of 2026-08-06 (Tom's decision; advisor sign-off pending).
  Ch2/Ch4.1/Ch4.4/Ch4.5/Ch5.1.4/Ch6/App. A and the frontend chapter now all carry it, and the floor is a
  real pipeline column (`energy_kwh_calib_measured_point_loma`, fleet sum 89.81 GWh/yr) rather than a
  prose-only claim. Ch3 and Ch4 agree. What is *not* settled is the advisor sign-off.
- **Never mix cohorts across a single claim.** A site count, an energy figure, an NPV and a payback quoted
  in one sentence must all come from the same tier, the same discount rate, the same subsidy level, and
  the same viable set. Portfolio NPV in particular has two legitimate readings under a grant ($415.8M
  over the fixed 1,138; $444.5M over the 2,751 that become viable) and they are not interchangeable.
- **Payback is undiscounted in this model.** The discount rate moves NPV and IRR, never payback. Only the
  capital subsidy moves payback. Do not write "cheap municipal debt shortens payback."
- Label every business number as an estimate, per the intellectual-honesty rules in §5 of
  `THESIS_BREAKDOWN.md`.
- Ch3.3 requires one **real named** archetype plant — use Fall River WWTP, not a composite. Quote it at
  both the ceiling (3.1 yr) and the floor-with-subsidy (8.3 yr), never the ceiling alone.
