# SMOKE_TEST_REPORT — Phase 5 LightGBM on Combined Dam Labels

> **INTERNAL — pipeline proof only. These numbers must never appear in**
> **director, pitch, or competition material.**

Generated: 2026-07-06  
Git SHA: `ad14c7c483bdda7aae8d022c10160f18025cd88a`  
Run command: `python -m src.phase5.train`  
Seed: 0  
Artifact path: `data/processed/phase5/models/` (gitignored)

---

## §1 — What this smoke test is and is not

A **smoke test** verifies that the code pipeline runs end-to-end without errors and
produces plausible output. It does **not** produce a deployable model and its
metrics have no product significance.

The framing was set on 2026-06-24 (director brief) and confirmed in the
2026-07-02 strategy session (WOWERS_PROJECT_JOURNAL.md): training a full
Phase 5 ML model on current data was declared not worth doing as a product
deliverable. The 2026-07-04 FERC conduit label hunt formally confirmed this:
11 genuinely new conduit-scale labels found vs. the ≥ 50 gate threshold —
gate fails, Phase 5 product model formally killed.

What survives is this smoke test: train LightGBM on the 1,360 combined dam
labels purely to verify that the rails (combine → feature engineering →
leakage lock → nested CV → train → persist) work end-to-end.

---

## §2 — Data used

| Property | Value |
|---|---|
| Source parquet | `data/raw/ground_truth/combined_ground_truth.parquet` |
| Total rows | 1,360 |
| EHA rows | 1,268 |
| EIA rows | 92 |
| Null `source_plant_code` rows | 1 (EHA-only site; sentinel group key assigned) |
| Target | `ln(actual_annual_energy_kwh)` |
| Null target values | 0 |
| Null `actual_head_m` | 1,360 (100% — not a feature) |
| Null `actual_flow_m3s` | 1,360 (100% — not a feature) |

### Features (5 total, all Float64)

| Column | Description | Encoding |
|---|---|---|
| `latitude` | Decimal degrees | raw float |
| `longitude` | Decimal degrees | raw float |
| `log_capacity_kw` | `ln(actual_installed_kw)` | raw float |
| `climate_zone_code` | 5-band Köppen proxy from latitude | int→float: 0=tropical, 1=subtropical, 2=temperate, 3=continental, 4=polar |
| `state_code_code` | Two-letter state code | sorted-unique → int index, cast to float |

`ground_truth_source` is deliberately excluded: it is a provenance tag
(EIA vs EHA) that could encode reporting artifacts, not physics.

### LightGBM hyper-parameters (fixed — no sweep by design)

```
n_estimators=400, learning_rate=0.05, num_leaves=31,
min_child_samples=20, n_jobs=1, deterministic=True,
force_row_wise=True, verbose=-1, random_state=0
```

### CV structure

Outer: 5-fold stratified by `state_code` (from `config/settings.yaml phase5.cv`)  
Inner: 3-fold group-aware by `source_plant_code` (no plant split across folds)

---

## §3 — Per-fold metric table

All metrics computed on held-out outer folds only. LightGBM is compared to
two baselines that use the **same outer splits** (identical seed/states).

**Predict-mean baseline:** each fold predicts the training-fold mean of
`log(energy)` for all validation rows.

**CF-baseline:** each fold predicts `log_capacity_kw + ln(8760) + ln(median_CF)`,
where `median_CF` is computed from the training fold only. This is the "capacity
× 8760 × capacity-factor" energy model, with CF anchored to the real dam fleet.

### rmse_log (RMSE on log-energy — primary metric)

| Fold | LightGBM | MeanBaseline | CF-Baseline |
|---:|---:|---:|---:|
| 1 | 0.8135 | 1.8907 | 0.8527 |
| 2 | 0.8924 | 1.9010 | 0.8670 |
| 3 | 1.0494 | 1.9684 | 1.0362 |
| 4 | 0.9249 | 1.9665 | 0.9442 |
| 5 | 0.9025 | 2.0164 | 0.9629 |
| **mean ± std** | **0.9165 ± 0.0763** | **1.9486 ± 0.0468** | **0.9326 ± 0.0670** |

### mape (Mean Absolute Percentage Error on raw kWh)

| Fold | LightGBM | MeanBaseline | CF-Baseline |
|---:|---:|---:|---:|
| 1 | 140.7% | 592.0% | 161.8% |
| 2 | 167.7% | 433.9% | 182.3% |
| 3 | 3655.4% | 14773.7% | 6935.8% |
| 4 | 751.0% | 3240.1% | 1004.9% |
| 5 | 219.8% | 2277.3% | 430.7% |
| **mean ± std** | **987% ± 1353%** | **4263% ± 5359%** | **1743% ± 2614%** |

> **Note on high MAPE:** dam labels span six orders of magnitude (small
> irrigation canals to Hoover Dam). Fold 3 contains several large-hydro outliers
> that dominate the mean MAPE via the percentage formula. Median MAPE across
> folds 1–2 and 5 is ~170%; fold 3's outliers inflate the mean. This is a
> data-coverage artefact, not a model bug. RMSE-log is the more appropriate
> primary metric.

### R² (coefficient of determination on log-energy)

| Fold | LightGBM | MeanBaseline | CF-Baseline |
|---:|---:|---:|---:|
| 1 | 0.814 | −0.003 | 0.796 |
| 2 | 0.780 | −0.000 | 0.792 |
| 3 | 0.716 | −0.000 | 0.723 |
| 4 | 0.779 | −0.000 | 0.770 |
| 5 | 0.799 | −0.003 | 0.771 |
| **mean ± std** | **0.778 ± 0.034** | **−0.001 ± 0.001** | **0.770 ± 0.026** |

### Spearman rank correlation

| Fold | LightGBM | MeanBaseline | CF-Baseline |
|---:|---:|---:|---:|
| 1 | 0.917 | NaN | 0.905 |
| 2 | 0.890 | NaN | 0.903 |
| 3 | 0.916 | NaN | 0.916 |
| 4 | 0.924 | NaN | 0.914 |
| 5 | 0.922 | NaN | 0.908 |
| **mean ± std** | **0.914 ± 0.012** | **NaN (constant)** | **0.909 ± 0.005** |

> **Note on mean-baseline Spearman:** the mean baseline predicts the same
> constant value for every validation row in a fold. Spearman rank correlation
> is undefined for a constant prediction vector
> (`scipy.stats.spearmanr` raises `ConstantInputWarning` and returns NaN).
> Criterion 3 handles this: a model with finite positive Spearman trivially
> beats a constant-prediction baseline.

---

## §4 — Success criteria verdicts

| # | Criterion | Verdict |
|---|---|---|
| **1** | End-to-end run completes from parquet to persisted model + metadata with `allow_physics_estimate_feature: false` semantics | **PASS** — `smoke_lgbm.txt` + `smoke_metadata.json` written |
| **2** | Leakage guard fires on a deliberately-leaky feature set (negative test) | **PASS** — see §5 |
| **3a** | LightGBM beats predict-mean on mean `rmse_log` (lower is better) | **PASS** — 0.9165 < 1.9486 |
| **3b** | LightGBM beats predict-mean on mean `spearman` (higher is better) | **PASS** — 0.914 > NaN (constant prediction; any finite positive model wins) |
| **4** | Determinism: two consecutive runs with seed=0 produce identical mean metrics | **PASS** — both runs: rmse_log=0.9165, spearman=0.9137 |
| **5** | Full pytest suite green | **PASS** — 580 passed / 1 skipped (532 pre-existing + 48 new) |

**Note on criterion 3 vs CF-baseline:** LightGBM does **not** clearly beat the
CF-baseline (rmse 0.9165 vs 0.9326 — marginal; spearman 0.914 vs 0.909 —
marginal). Beating the CF-baseline was explicitly **not required** per the task
specification. The CF-baseline embeds the real dam fleet's capacity-factor
distribution and is a strong prior for this particular training set. This
outcome does not affect the smoke-test result.

---

## §5 — Leakage-guard demonstration

The following Python fragment deliberately includes `annual_energy_kwh`
(a denylisted column that is a direct proxy for the training target) and
calls `assert_no_leakage`. The guard fires before any training occurs:

```python
from src.phase5.features import assert_no_leakage
assert_no_leakage(["annual_energy_kwh", "latitude", "longitude"])
# Raises:
```

**Actual ValueError text (from `demonstrate_leakage_guard()`):**

```
Leakage detected — the following feature(s) are in LEAKAGE_DENYLIST
and must be removed before training: ['annual_energy_kwh']
```

`nested_cv` also calls `assert_no_leakage(list(X.columns))` at entry as a
second guard — belt-and-braces. A leaky feature set will be rejected by
**either** guard before any estimator is fitted.

---

## §6 — Limitations

1. **Dam–WWTP domain gap (primary limitation):** training data are EIA/EHA
   conventional hydro plants (median ~8 MW, range ~100 kW – 6 GW). WOWERS
   targets WWTP outfalls (1–500 kW, near-constant municipal flow). A dam-trained
   model does not transfer to WWTP micro-scale. This was the Jul-2/Jul-4 kill
   decision rationale. The smoke test numbers have zero product relevance.

2. **No head or flow in labels:** `actual_head_m` and `actual_flow_m3s` are
   100% null (EIA/EHA do not report them). The model has only 5 features:
   lat/lon, log-capacity, climate zone, and state. This is the small
   transferable intersection identified in ARCHITECTURE.md §5 and the Jun-30
   features.py module docstring. ARCH §5.4 (physics-vs-real check) cannot run.

3. **Ordinal state/climate encoding:** `state_code_code` and `climate_zone_code`
   use sorted-index ordinal encoding. LightGBM treats them as ordinal numbers
   rather than unordered categories. A production model would declare them as
   native LightGBM categorical columns. Acceptable for a pipeline proof.

4. **High MAPE:** mean MAPE of ~987% is dominated by Fold 3 outliers (fold
   contains large-hydro plants whose energy is many orders of magnitude above
   the fold's training mean). Median MAPE across lower-variance folds is ~170%.
   RMSE-log (primary metric) is unaffected by these outliers.

5. **No HP tuning:** fixed n_estimators=400, lr=0.05, num_leaves=31 by design.
   A tuned model on this dataset would likely achieve lower rmse_log but the
   point is rails verification, not model quality.
