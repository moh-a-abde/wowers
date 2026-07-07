# P1-COORD-GUARD — Coding-Agent Prompt

**Task ID:** P1-COORD-GUARD
**Repo:** WOWERS, branch `tom`
**Scope:** Add a coordinate-validity guard to Phase 1 (`src/phase1/filter_potw.py`), re-run the pipeline, regenerate the GeoJSON export, update the two affected reports and all hardcoded test counts.
**Python:** `/opt/miniconda3/bin/python` (polars, pytest available).

---

## 1. Background

The Jul-6 P4-TIER review found `WI0025194` (Racine Wastewater Utility) with `latitude = 4.4` in `data/processed/phase1/ranked_candidates.parquet` — a corrupt value inherited from EPA ECHO `ICIS_FACILITIES.CSV` (`GEOCODE_LATITUDE`). It renders as a dot in the ocean off Colombia on the frontend map, and — worse — its Phase 2/3 head estimate was computed at that garbage location, so its entire scorecard (currently **Tier A, project_viable, 342,800 kWh/yr**) is untrustworthy.

A pre-scoping probe (2026-07-06) found this is **not** a single-row problem. **10 rows** in the current `ranked_candidates.parquet` have coordinates outside any US NPDES territory:

| npdes_id  | facility_name                  | state | latitude   | longitude   | error class |
|-----------|--------------------------------|-------|------------|-------------|-------------|
| WYG589102 | GREAT PLAINS LAGOON            | WY    | 42.9741    | **+108.477**  | lon sign flip |
| MS0061671 | ABBEVILLE POTW                 | MS    | 34.504633  | **+89.504902**| lon sign flip |
| TX0137146 | CANUTILLO MIDDLE SCHOOL WWTP   | TX    | 31.926388  | **+106.608888**| lon sign flip |
| NJ0020371 | CAPE MAY REG WTF               | NJ    | **8.943708**  | -74.961818  | truncated lat (~38.9) |
| WI0025194 | RACINE WASTEWATER UTILITY      | WI    | **4.4**       | -87.766667  | corrupt lat (~42.7) |
| SC0047457 | BOARD OF PUBLIC WORKS CANOE CR | SC    | 35.116885  | **+81.533247**| lon sign flip |
| MS0024589 | QUITMAN POTW                   | MS    | **3.339083**  | -88.737083  | corrupt lat (~32.0) |
| PR0026042 | VILLAS DEL GIGANTE, CAROLINA   | PR    | 18.0       | **-56.166667**| corrupt lon (~-66) |
| MS0052477 | BYHALIA POTW                   | MS    | **-34.904056**| -89.699667  | lat sign flip |
| MS0020575 | ACKERMAN POTW                  | MS    | 33.307778  | **+89.189139**| lon sign flip |

Downstream presence (verified against current parquets):
- All 10 are in `ranked_candidates.parquet` (17,158 rows) and `phase2/energy_yield_estimates.parquet` (17,158).
- 4 of them are in the Phase 3 outputs (5,468 rows): `NJ0020371`, `WI0025194`, `MS0024589`, `MS0052477`.
- 3 are in `phase4/financial_scorecards.parquet` (3,783 rows): `NJ0020371` (non-viable, C), `WI0025194` (**viable, A**), `MS0024589` (non-viable, C).

## 2. Design decisions — already made, do not relitigate

1. **Reject, don't fix.** Rows failing the guard get their coordinates nulled and are dropped (the existing null-coordinate drop in `_join` already handles the drop, or drop directly — your choice, but log it distinctly). Do **not** auto-correct longitude sign flips or guess digits, even where the fix looks obvious. Hand-corrections without an authoritative source = hidden data divergence (Jul-6 session decision). Auto-rescue of sign-flips is a documented **non-goal** (may be a future enhancement; note it in the module docstring or a comment if you like).
2. **Band whitelist, not `lat < 15` rejection.** The journal backlog line "reject lat < 15°" is **wrong** and must not be implemented literally: Guam is at ~13.4°N and American Samoa at ~−14.3°S — both have NPDES permits present in the data (`GU`, `AS`, `MP` all appear in `state_code`). Use inclusive validity bands instead:
   - latitude valid iff in `[-14.8, -10.8]` (American Samoa) **or** `[13.0, 71.5]` (Guam/CNMI → Puerto Rico/USVI → Hawaii → CONUS → Alaska)
   - longitude valid iff in `[-180.0, -64.4]` (Western Hemisphere US incl. USVI east end at ~−64.56) **or** `[144.5, 146.2]` (Guam/CNMI)
   - A row is valid only if **both** coordinates fall in a whitelisted band. No cross-field check against `state_code` (out of scope).
   - These exact bands catch exactly the 10 rows above and pass all legitimate territories (verified in the probe). Preserve that property.
3. **Config-driven with hardcoded fallbacks**, matching the existing pattern in `filter_potw.py` (`_MAX_FLOW_MGD`, `_DMR_DESIGN_RATIO_CAP`). Add to `config/settings.yaml` under the existing `processing:` block (~line 241):
   ```yaml
   coord_lat_valid_bands: [[-14.8, -10.8], [13.0, 71.5]]   # US NPDES territories: AS | GU/MP..AK
   coord_lon_valid_bands: [[-180.0, -64.4], [144.5, 146.2]] # W-hemisphere US | GU/MP
   ```
4. **Placement:** new private function `_drop_invalid_coords(df)` in `src/phase1/filter_potw.py`, called from `load_potw_facilities` between `_join` and `_cast_schema`. Log a warning with the summary count **and per-row detail** (npdes_id, state_code, lat, lon) — 10 rows is small enough to log all; cap detail at 20 rows if you're defensive.
5. **Additive only.** No changes to Phase 2/3/4/5 logic, no changes to other Phase 1 functions beyond the one call site. Phase 3's outfall-coordinate path (`src/phase3/outfall_coords.py`) is explicitly out of scope.

## 3. Implementation spec

- `config/settings.yaml` — the two keys above, under `processing:`, with a one-line comment each.
- `src/phase1/filter_potw.py`:
  - Module constants `_COORD_LAT_VALID_BANDS`, `_COORD_LON_VALID_BANDS` via `config.get(...)` with the hardcoded defaults from §2.3 (so absent keys = same behavior, matching the `_MAX_FLOW_MGD` pattern).
  - `_drop_invalid_coords(df: pl.DataFrame) -> pl.DataFrame` — pure, testable without IO. Docstring must state the rationale (US NPDES territory bands; why naive `lat < 15` is wrong; reject-don't-fix decision).
  - One call in `load_potw_facilities`.
- Re-run the pipeline in order: `python -m src.phase1.run`, then phase2, phase3, phase4 runners (check each module's `__main__` / run entry — do not invent flags). Snapshot `financial_scorecards.parquet` before the re-run (copy to scratchpad) and diff after: all surviving rows must be value-identical on all columns except any rank/ordinal columns that legitimately shift when rows are removed. Report any other diff as a failure.
- Regenerate the GeoJSON: `python scripts/export_geojson.py` → `exports/viable_sites.geojson` (git-tracked; commit the regenerated file).

## 4. Expected impact — hard invariants

These are **exact expectations** from the probe. If any number differs after your re-run, **STOP and report the discrepancy instead of adjusting the expectation to match**:

| Artifact | Before | After |
|---|---|---|
| `ranked_candidates.parquet` rows | 17,158 | **17,148** (−10) |
| `phase2/energy_yield_estimates.parquet` rows | 17,158 | **17,148** |
| `phase3/*.parquet` (5,468-row files) | 5,468 | **5,464** (−4) |
| `phase4/financial_scorecards.parquet` rows | 3,783 | **3,780** (−3) |
| `project_viable` count | 1,141 | **1,140** (−1: WI0025194) |
| Viable fleet energy (`annual_energy_kwh` sum) | 409.1405 GWh | **408.7977 GWh** |
| `exports/viable_sites.geojson` features | 1,141 | **1,140** (no ocean dot) |

Calibrated-tier fleet sums scale with the new viable energy (multipliers 0.291 / 0.447 / 0.688 unchanged): recompute and report them (expect ≈ 118.96 / 182.73 / 281.25 GWh — verify live, don't copy).

Intermediate funnel stats (e.g. head_valid 4,864) shift too — recompute live, don't assume.

## 5. Tests

- **New unit tests** for `_drop_invalid_coords` (synthetic frames, no IO): Guam (13.44, 144.8) passes; American Samoa (−14.3, −170.7) passes; Alaska (71.3, −156.8) passes; Key West (24.55, −81.8) passes; each of the 5 error classes from §1 fails (use the real bad values); band boundary values behave inclusively; empty frame no-op; all-valid frame unchanged.
- **Update hardcoded counts** — enumerated so nothing is missed:
  - `tests/test_phase4/test_calib_cols.py:192` — `3783` → `3780`; `:198` — `1141` → `1140`; fleet-sum assertions to the new live values; comment at `:125`.
  - `tests/test_scripts/test_export_geojson.py:358-362` — `test_geojson_1141_features` → 1,140 (rename the test accordingly).
  - Grep the whole of `tests/` for `17158|17,158|3783|3,783|1141|1,141|5468|5,468|4864|409.1` and fix anything else that asserts pipeline counts (integration smoke tests included).
- Full suite must pass: baseline is **644 passed / 1 skipped**. Report your final counts (expect 644 + your new tests, same skip).

## 6. Docs and reports to update

- `EXCLUSION_FUNNEL_REPORT.md` — funnel headline and counts (17,158 → … → 1,140 viable / 408.8 GWh). Recompute every number you touch from the regenerated parquets.
- `CF_CALIBRATION_REPORT.md` — §6 fleet application sums (409.1 ceiling → 408.8; calibrated tiers accordingly). The EHA-derived multipliers themselves are untouched.
- Docstring/header count references: `src/phase5/features.py` (17,158 → 17,148, two places + line 8's 3,783), `scripts/export_geojson.py` header (1,141 / 3,783), `scripts/cf_calibration.py` header (409.1 / 1,141).
- `DIRECTOR_BRIEF_2026-06-24.md` and the journal are **historical — do not touch**.

## 7. Non-goals

- No auto-correction of recoverable coordinates (sign flips, digit errors).
- No `state_code` ↔ coordinate cross-consistency check.
- No guard in Phase 3 outfall coords (`NPDES_PERM_FEATURE_COORDS.csv` path).
- No changes to ranking logic, thresholds, or any Phase 2–5 computation.
- No commits — leave the working tree for Tom's review.

## 8. Deliverables

1. Code + config + tests per §3/§5.
2. Regenerated parquets + `exports/viable_sites.geojson`.
3. Updated reports per §6.
4. **`P1_COORD_GUARD_REVIEW_PROMPT.md`** (repo root) — a verification prompt for an independent reviewer. **Every numeric claim in it must come from a command you actually ran, with the exact command and its output pasted.** Two previous review prompts contained falsified claims written without running the repro (P5-SMOKE check E: booster feature names; P4-TIER check D: coordinate-range check that silently excluded AK/HI/GU) — both were caught by the reviewer and cost a correction round. Include: the §4 invariant table with live verification commands, the snapshot-diff result, the 10 dropped npdes_ids as logged by the new guard, test-suite counts, and a scope check (git diff --stat against the pre-session commit).
