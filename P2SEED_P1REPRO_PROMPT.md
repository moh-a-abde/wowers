# P2-SEED + P1-REPRO — Coding-Agent Prompt

**Task IDs:** P1-REPRO (Part 1), P2-SEED (Part 2) — execute in this order.
**Repo:** WOWERS, branch `tom` (start from commit `ca2b52e`).
**Python:** `/opt/miniconda3/bin/python` (polars, numpy, scipy, pytest available).
**Baseline test suite:** 685 passed / 1 skipped.

---

## Context

On 2026-07-06 the P1-COORD-GUARD session (see `P1_COORD_GUARD_REVIEW_PROMPT.md`,
"REVIEW OUTCOME" section) exposed two latent pipeline problems. This session fixes them.

1. **Phase 2 Monte-Carlo seeding is positional** (`seed + row_index`,
   `src/phase2/monte_carlo.py`). Removing 10 rows from the input re-drew ~4,656
   unrelated sites, changed 1,090 scorecard rows, and flipped 3 borderline
   viability calls. Fix: site-keyed seeding, then one deliberate fleet re-baseline.
2. **Phase 1 is not reproducible from raw data.** An orphaned `python -m
   src.phase1.run` on 2026-07-06 produced an 82.7M-row DMR timeseries (May-20
   baseline: 2,668,808 rows) and reportedly crashed mid-run with a `scipy.stats.linregress`
   edge case (claim unverified). Investigate both; fix only the crash.

Current production state (post-remediation, all committed at `ca2b52e`):

| Artifact | Value |
|---|---|
| `phase1/ranked_candidates.parquet` | 17,148 rows |
| `phase1/dmr_flow_timeseries.parquet` | 2,667,701 rows (single file, NOT a directory) |
| `phase2/energy_yield_estimates.parquet` | 17,148 rows; `excluded==False` → 5,464 |
| `phase3/turbine_sizing.parquet` | 5,464 rows; `head_valid` → 4,860 |
| `phase4/financial_scorecards.parquet` | 3,780 rows; viable 1,140; 408.7977 GWh |
| `exports/viable_sites.geojson` | 1,140 features |

---

## Process rules — read before anything else

- **STOP-on-surprise.** Any invariant miss, crash, or unexpected number: stop,
  document exactly what you saw, and end the session with a report. Do NOT
  improvise workarounds, do NOT hand-edit parquets, do NOT "restore from
  checkpoints" on your own judgment. The last two sessions' worst failures were
  improvised recoveries, not the original bugs.
- **No background/orphaned processes.** Run pipeline steps in the foreground
  with a generous timeout. If a step is too slow, stop and report — don't fork it.
- **No commits. No edits to `WOWERS_PROJECT_JOURNAL.md`.** Tom reviews first.
- Five previous review rounds caught claims written without running the repro
  (P5-SMOKE check-E; P4-TIER check-D; FERC Point Loma stale value; coord-guard
  "elevation non-determinism" — the real cause was positional seeding; coord-guard
  "3 sites changed" — actually 1,090). Every numeric claim you write must come
  from a command you actually ran, with output pasted.

---

## Part 1 — P1-REPRO (investigation + surgical fix; NO renumbering)

**Hard constraint:** `data/processed/**` must be byte-identical at the end of
Part 1. Take SHA-256 of every file under `data/processed/` before starting;
verify identical after. Do not run `python -m src.phase1.run` against the live
tree — all verification at unit level or against copies in the scratchpad.

### 1a. `linregress` crash — verify, then fix

- Claim from the previous agent (unverified): `src/phase1/flow_features.py:173`
  (`slope, _, _, _, _ = stats.linregress(t, flows_for_trend)`) raises when a
  facility has exactly 1 unique DMR timestamp after primary-outfall selection.
- Verify at unit level: build a synthetic facility frame with a single unique
  timestamp and call the enclosing function directly. Also test 2 identical
  timestamps (x-values constant → linregress returns nan or raises depending on
  scipy version — check ours).
- If confirmed: guard it — fewer than 2 *unique* timestamps → trend value
  becomes null/0.0 (match whatever the column's existing missing convention is;
  read how `flow_trend_mgd_per_year` nulls are handled downstream before choosing).
  Add regression tests (crash case + constant-x case + normal case).
- If NOT confirmed: no fix. Document exactly what happens instead.

### 1b. DMR 82.7M-row blow-up — root cause only, NO adoption

- Evidence on disk: `data/checkpoints/phase1_dmr_flow_timeseries_v009.parquet`
  (157 MB, written 2026-07-06 13:04 by the orphaned run) vs
  `phase1_dmr_flow_timeseries_v008.parquet` (18 MB, 2026-05-20, 2,668,808 rows).
- Diagnose the 31× growth: read `src/phase1/dmr_timeseries.py` (or wherever the
  ingest lives — locate it), find what raw files it globs, count raw rows on
  disk, compare v009 vs v008 schema + row counts + distinct npdes_id + date
  ranges + parameter codes. Likely candidates: new raw DMR files downloaded
  since May 20; a filter (parameter/outfall/date) not applied; dedup regression.
- Deliverable: root cause + a recommendation (e.g. "raw dir gained files X, Y —
  next re-baseline will legitimately have N rows" or "bug in filter Z").
  **Do not change pipeline code or adopt the new data for 1b** — if you find a
  real bug, describe the fix in the report; Tom decides when to take the
  fleet-wide renumber that any DMR change implies.

### 1c. Checkpoint hygiene

- Read `src/common/io.py` (checkpoint + manifest mechanics) and
  `data/checkpoints/manifest.json` first. Then delete
  `phase1_dmr_flow_timeseries_v009.parquet` (157 MB orphan) and its manifest
  entry if one exists, such that the checkpoint loader still works (prove with
  a load of the latest version of that artifact).
- Do not delete anything else. Report disk reclaimed.
- Note: running pytest writes small throwaway checkpoint versions (observed
  v149–v178 for phase4, ~16 KB each). Known noise — ignore, don't clean.

### Part 1 deliverable

`P1_REPRO_REPORT.md` (repo root): 1a verification + fix, 1b root cause +
recommendation, 1c what was deleted, and the before/after SHA-256 proof that
`data/processed/` is untouched.

---

## Part 2 — P2-SEED (site-keyed seeding + one-time re-baseline)

Only start after Part 1 is complete and `data/processed/` is verified untouched.

### 2a. Seeding change

`src/phase2/monte_carlo.py` currently derives per-facility seeds positionally
in TWO places — the sequential path (`seed + i` in the enumerate loop) and the
parallel path (`_process_batch`: `base_seed + i` over batch offsets). Replace
both with the same site-keyed derivation:

```python
import hashlib
import numpy as np

def _site_seed_sequence(base_seed: int, npdes_id: str) -> np.random.SeedSequence:
    """Per-facility seed independent of row order and row count.

    sha256 (not builtin hash(), which is process-salted) so the draw for a
    given (base_seed, npdes_id) is reproducible across runs, processes, and
    Python versions, and removing/adding other rows never changes it.
    """
    site_key = int.from_bytes(
        hashlib.sha256(npdes_id.encode("utf-8")).digest()[:8], "big"
    )
    return np.random.SeedSequence([base_seed, site_key])
```

`_process_one` should build its rng from this (e.g.
`np.random.default_rng(_site_seed_sequence(base_seed, npdes_id))`). Keep the
CLI `--seed` (default 42) as `base_seed`. Update docstrings that describe the
old `seed + row_index` scheme (`run.py` line ~155 mentions it too — grep for it).

### 2b. Tests (the removal-invariance one is the entire point)

- Determinism: same base seed, two runs → identical outputs.
- **Removal invariance:** run the MC over synthetic facilities [A, B, C]; run
  again over [A, C]; A's and C's outputs must be identical between runs. This
  test must fail on the old positional scheme — state in the test docstring why
  it exists (cite the 2026-07-06 incident). Make sure it is a real assertion
  against concrete values, not a tautology (a previous agent gutted
  `test_report_fleet_sums` into `x*0.291 == x*0.291`; the reviewer checks for this).
- Insertion invariance (same idea, add a row instead of removing).
- Different base seed → different draws; different npdes_id → different draws.
- Sequential path and parallel path produce identical results for the same input.

### 2c. Re-baseline (deliberate, one-time fleet redraw)

- Snapshot `data/processed/phase4/financial_scorecards.parquet` to the
  scratchpad first.
- Run official runners in order, foreground: `python -m src.phase2.run`, then
  phase3, then phase4, then `python scripts/export_geojson.py`.
  **Do NOT re-run Phase 1** — `data/processed/phase1/` must not change at all.
- **Structural invariants (exact — STOP if any miss):**
  - phase2 rows 17,148; `excluded==False` count **5,464** (exclusion logic is
    data-driven, MC-independent — if this moves, something else changed)
  - phase3 rows 5,464; `head_valid==True` count **4,860**
- **Expected-to-change (report exact new values, don't force):** scored rows
  (≈3,780), viable count (≈1,140), viable GWh (≈408.8 ± a few), turbine-type
  mix, all financial columns. Every energy number shifts once — that is the
  accepted cost of this change.
- Diff vs the snapshot: how many rows changed values, viability churn (IDs in
  and out), energy delta. Goes in the report and review prompt.
- Determinism proof: run phase2 twice with seed 42; outputs byte-identical.

### 2d. Renumber docs + tests to the new baseline

- `EXCLUSION_FUNNEL_REPORT.md` — funnel counts, econ_cat tables, CapEx table,
  what-if band (re-run `scripts/install_cost_whatif.py`), reproducibility
  footer, median payback. Recompute every figure live from the new parquets.
- `CF_CALIBRATION_REPORT.md` — re-run `scripts/cf_calibration.py`; update the
  headline GWh, viable count, CF percentiles (§ implied-CF table), band tables,
  §8 scope row. The EHA-derived multipliers (0.291/0.447/0.620/0.688) do not change.
- Tests with hardcoded counts: `tests/test_phase4/test_calib_cols.py`
  (3780 / 1140 / 408.8 / 119.0 / 182.7 / 281.3), `tests/test_scripts/test_export_geojson.py`
  (1,140 features). Grep `tests/` for the old values (`3780|1140|408\.|1,140`)
  and update everything that asserts pipeline numbers to the new baseline.
- Docstring headers citing 408.8/1,140: `scripts/cf_calibration.py`,
  `scripts/export_geojson.py`.
- Full pytest suite green at the end; report counts (685 + your new tests expected).

---

## Deliverables

1. Part 1: `P1_REPRO_REPORT.md`, `flow_features.py` fix + tests (if confirmed),
   checkpoint cleanup, untouched `data/processed/` proof.
2. Part 2: seeding change + invariance tests, re-baselined parquets + GeoJSON,
   renumbered reports/tests, determinism proof, baseline-diff summary.
3. **`P2SEED_P1REPRO_REVIEW_PROMPT.md`** (repo root) for the independent
   reviewer. Every numeric claim paired with the exact executed command and its
   pasted output. Must include: Part 1 SHA-256 proof; the removal-invariance
   test source (so the reviewer can check it isn't a tautology); structural
   invariant checks; old→new headline diff; viability churn IDs; test counts;
   `git diff --stat ca2b52e` scope check.
4. No commits; leave the working tree for review.
