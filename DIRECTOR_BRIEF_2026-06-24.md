# Director Meeting Brief — Wed Jun 24, 2026

**Topic:** F4-INSTALL — installation cost decision + scope confirmation
**Prepared:** Jun 21, 2026 (Tom)
**Production state:** Phase 1–4 complete, 427 tests pass. Viability gate = NPV>0 AND payback≤20yr AND real IRR (MINREV floor removed Jun 12).

---

## Quick Recap — What I Got Done Since Last Wednesday (Jun 17–21)

Here's the plain-English version of where the week went, so the technical sections below make sense.

**1. Made the cost model more honest by adding installation cost.**
Up until now the model basically pretended that installing the turbines was free — it added up equipment, grid hookup, and permitting, but had no line at all for the actual labor of putting the thing in the ground. That's obviously not realistic. So I added an installation cost, modeled as a percentage of the equipment price (your 15–20% suggestion), since real install quotes are impossible to get out of government contractors. That's the decision slide right below — I need you to lock in the exact percentage.

**2. Brought our main "how did you exclude everyone else?" report up to date.**
That report was still showing old numbers (355 viable sites). After we removed the revenue floor and added install cost, the real number is now 1,141 viable sites / 409 GWh per year. I rewrote the report so it tells the current story, and added a "profitability gradient" — basically sorting every site into buckets by payback, profit, and return — instead of just a yes/no on viability.

**3. Officially kicked off Phase 5 — the machine-learning part.**
The idea behind Phase 5 is to train a model on real hydropower plants where we already know exactly how much energy they produce, then use that to sanity-check and sharpen our own estimates. The catch: to train a model like that, you need real "ground truth" — actual plants with known output — and we had none in the project yet. So this week:
- I first checked whether we already had usable data sitting around. Turns out the external drive already had government EIA data (every US power plant's capacity and yearly generation) that we'd downloaded for something else — so that's reusable, no work needed.
- Then I downloaded the proper hydropower-specific datasets straight from the Dept of Energy's Oak Ridge lab: a full inventory of US hydro plants, their year-by-year generation, and a report on conduit/wastewater hydropower (the closest thing to what we do). Everything's saved and organized on the drive.
- Finally I built two automated tools that read all that messy government Excel data and turn it into one clean, labeled table the model can actually learn from. One pulls ~1,300 real hydro plants from the EIA data, the other ~1,300 from the DOE hydro data — each with real capacity and real annual energy.

**The one honest caveat on Phase 5:** this training data is mostly *big* hydro plants (1 megawatt and up), while our target sites are tiny by comparison. So it's a solid starting point, but the next step is hunting down small / conduit-scale project data to fill that gap before the model can be trusted on the little sites we care about.

**Bottom line:** the financials are more realistic now (install costs are in), the reporting reflects today's real numbers, and Phase 5 has officially started with real training data in hand.

---

## Heads-Up — The Roadblock Before We Can Train the ML Model

Phase 5 has started, but I want to flag a real problem honestly before we sink time into it, because part of the fix needs your help.

**First, what the ML model is even for.** Right now we estimate each site's energy with physics formulas. The machine-learning model is meant to learn from *real* hydropower plants — places where we already know how much electricity they actually produce — and use that to double-check and sharpen our estimates. Basically, "show the computer thousands of real plants so it learns the pattern, then let it grade our homework."

**To teach it, every training example needs two halves — like a flashcard.** The front is the *question* (the site's details: how much water, how big a drop, turbine size). The back is the *answer* (how much energy it really made). The model studies thousands of complete cards and learns the link.

**Here's the snag.** The answers we have are all from **big dams**, but our detailed question-data is for **wastewater treatment plants**. Those are totally different places, so I can't pair a dam's answer with a wastewater plant's question — they don't go on the same card. And the dam records only tell us the plant's size and energy, not the water-flow details, so even the answer side is thin. Two knock-on issues: (1) every plant we have an answer for is *large* (1 megawatt and up), while our real targets are *tiny* — a model that only ever saw big dams will guess badly for small sites; (2) we have to be careful not to accidentally let the model peek at the answer through a back door, which would make it look great in testing and fail in reality.

**What the datasets are, in plain terms:**
- **EIA data** (US Energy Information Administration) — the government's master list of every power plant: its size and how much energy it made each year. We already had this on our drive. Gave us ~1,300 real hydro plants. *Big plants.*
- **EHA / HydroSource data** (Dept. of Energy, Oak Ridge lab) — a hydropower-specific version of the same idea: an inventory of US hydro plants plus their yearly generation. I downloaded this last week. Another ~1,300 plants. *Also big plants.*
- **FERC conduit data** (the one we still need) — this is the list of small hydropower projects built on **man-made water channels, including wastewater and canal sites**. In other words, *exactly our kind of site, at our size.* This is the missing piece that would give us "answer cards" that actually match our "questions."

**So what's genuinely blocking us:** it's not the coding — it's getting the *right kind of training examples*. The EIA and EHA data we have are a fine starting point to prove the machinery works, but a model trained only on giant dams won't be trustworthy for small wastewater outfalls. The honest fix is to track down the small-site (FERC conduit) data.

**Where I could use your help / a decision:**
1. Do you (or anyone in your network at DOE / FERC / a utility) have a line on **real small-scale or wastewater hydropower project data** — actual sites with their measured energy output? That's the single thing that would unblock a trustworthy model.
2. Are you OK with me building a rough "test-run" model on the big-plant data first — purely to confirm the whole pipeline works end-to-end — as long as we treat its numbers as a smoke test, not a real result?

My plan unless you say otherwise: do the cheap setup now (merge our two answer-lists, build the question sheet, guard against the "peeking" problem), stand up that throwaway test model to prove the pipeline, and in parallel go hunting for the small-site data that makes the real model believable.

---

## Decision Slide — Installation Cost % → Viability

We added an installation/labor cost line to CapEx (previously implicitly $0). Modeled as **% of equipment cost** per your guidance — real install cost is unobtainable (gov procurement opacity). Production default is **17.5%** (midpoint of your 15–20% range), **pending your committed value.**

| Installation % | Investment-ready sites | Viable energy (GWh/yr) | Portfolio CapEx |
|---:|---:|---:|---:|
| 0% (no install line) | 1,374 | 428.2 | $321.7M |
| 15% | 1,172 | 411.7 | ~$349M |
| **17.5% (current default)** | **1,141** | **409.1** | **$353.5M** |
| 20% | 1,120 | 407.5 | ~$358M |

*Source: `scripts/install_cost_whatif.py` (read-only re-score). Viability drop is the intended consequence of higher CapEx — not a logic change.*

---

## Two Asks for the Director

1. **Commit the installation %.** Default 17.5% stands unless you set otherwise. The lever is `config/settings.yaml` → `cost_model.installation_pct_of_equipment`; reversible with no code change.
2. **Confirm scope.** Installation line = **mechanical install / labor only.** It does **not** include:
   - Civil works (deliberately excluded)
   - Interconnection (separate CapEx line — $82.8M)
   - Permitting (separate CapEx line — $57.3M)

   This is why 15–20% is far below the literature "total installed = 2–5× equipment" multiplier — that multiplier bundles civil + E&I + contingency + interconnection + permitting, most of which we already model as separate lines.

---

## CapEx Structure (at 17.5%)

| Component | $M |
|---|---:|
| Equipment (vendor-band clamped, equipment-only) | 181.6 |
| Installation (= equipment × 0.175, mechanical labor) | 31.8 |
| Interconnection (tiered by kW) | 82.8 |
| Permitting (FERC conduit-NOI / abbreviated / full-NEPA) | 57.3 |
| **Total** | **353.5** |

Vendor-band violations: **0 of 3,783** sites (check is on equipment $/kW; installation excluded).

---

## Talking Points / Anticipated Questions

- **"Why not use a real install quote?"** Vendors bid high on public contracts and never disclose true install cost — no citable US equipment-only install data exists at our scale (1–3,000 kW). A % of equipment is the defensible model; the band table shows sensitivity.
- **"Did removing the revenue floor inflate the count?"** No double-count. Floor removal (Jun 12) and install addition (Jun 20) are independent. At 0% install + no floor = 1,374; install at 17.5% trims to 1,141 honestly.
- **Headline for any external materials:** **1,141 viable / 409.1 GWh/yr** at 17.5% install. Drop the old "355" and the "42×" figure (correct swing was 3.9×, now realized not hypothetical).

---

## After the Meeting (capture)

- [ ] Director's committed installation % = ____ (update `settings.yaml` if ≠ 0.175)
- [ ] Scope confirmed mechanical-only? Y / N
- [ ] Re-run Phase 4 if % changed; refresh `EXCLUSION_FUNNEL_REPORT.md` headline
