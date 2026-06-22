# Director Meeting Brief — Wed Jun 24, 2026

**Topic:** F4-INSTALL — installation cost decision + scope confirmation
**Prepared:** Jun 21, 2026 (Tom)
**Production state:** Phase 1–4 complete, 427 tests pass. Viability gate = NPV>0 AND payback≤20yr AND real IRR (MINREV floor removed Jun 12).

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
