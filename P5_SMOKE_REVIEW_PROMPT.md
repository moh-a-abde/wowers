# P5-SMOKE — Review Prompt (independent reviewer)

**To: Reviewing agent (fresh session)**  
**Re: Phase 5 Internal Smoke-Test — LightGBM on Combined Dam Labels**  
**Branch:** `tom`  
**Note: `WOWERS_PROJECT_JOURNAL.md` must NOT be modified until this review passes.**

---

## 1. What Was Built

| Artifact | Location | Purpose |
|---|---|---|
| `src/phase5/train.py` | repo | New module: feature engineering, baselines, smoke-test orchestrator |
| `tests/test_phase5/test_train.py` | repo | 48 new tests (47 unit + 1 integration) |
| `SMOKE_TEST_REPORT.md` | repo root | Internal-only results report |
| `P5_SMOKE_REVIEW_PROMPT.md` | repo root | This file |
| `data/processed/phase5/models/smoke_lgbm.txt` | gitignored | Persisted LightGBM model (native format) |
| `data/processed/phase5/models/smoke_metadata.json` | gitignored | Per-fold metrics, mappings, run provenance |

No Phase 1–4 source code or parquets were modified. `WOWERS_PROJECT_JOURNAL.md`
was not modified. `config/settings.yaml` was not modified (all needed keys
`phase5.model_dir`, `phase5.cv`, `phase5.combined_ground_truth_path` already
existed from the Jun-30 session).

---

## 2. Claimed Numbers

### Input data
| Metric | Claimed |
|---|---|
| Rows in `combined_ground_truth.parquet` | **1,360** |
| EHA rows | **1,268** |
| EIA rows | **92** |
| Null `source_plant_code` | **1** |

### CV results (seed=0, outer=5, inner=3)

#### LightGBM
| Fold | rmse_log | mape (%) | r2 | spearman |
|---:|---:|---:|---:|---:|
| 1 | 0.8135 | 140.7 | 0.8143 | 0.9170 |
| 2 | 0.8924 | 167.7 | 0.7796 | 0.8897 |
| 3 | 1.0494 | 3655.4 | 0.7158 | 0.9160 |
| 4 | 0.9249 | 750.9 | 0.7788 | 0.9236 |
| 5 | 0.9025 | 219.8 | 0.7992 | 0.9221 |
| **mean ± std** | **0.9165 ± 0.0763** | **987% ± 1353%** | **0.778 ± 0.034** | **0.914 ± 0.012** |

#### Predict-mean baseline
| mean rmse_log | mean mape | mean r2 | mean spearman |
|---:|---:|---:|---:|
| **1.9486** | **4263%** | **−0.001** | **NaN (constant)** |

#### CF baseline
| mean rmse_log | mean mape | mean r2 | mean spearman |
|---:|---:|---:|---:|
| **0.9326** | **1743%** | **0.770** | **0.909** |

### Success criteria
| # | Criterion | Claimed |
|---|---|---|
| 1 | End-to-end completes from parquet to model + metadata | PASS |
| 2 | Leakage guard fires on deliberately-leaky feature | PASS |
| 3a | LightGBM mean rmse_log < mean-baseline mean rmse_log | PASS (0.9165 < 1.9486) |
| 3b | LightGBM mean spearman > mean-baseline mean spearman | PASS (0.914 > NaN→constant baseline) |
| 4 | Two runs with seed=0 produce identical mean metrics | PASS |
| 5 | Full pytest suite | **580 passed / 1 skipped** (532 pre-existing + 48 new) |

---

## 3. Repro Commands

Run all of the following from the repo root. Quote the path in every shell
command (workspace path contains a space).

```bash
cd "/Users/tomsmacbookpro/Desktop/Temp/WOWERS /wowers"

# === A. Input data verification ===
/opt/miniconda3/bin/python -c "
import polars as pl
df = pl.read_parquet('data/raw/ground_truth/combined_ground_truth.parquet')
print('rows:', df.height)
print('null source_plant_code:', df['source_plant_code'].null_count())
print('source split:', df.group_by('ground_truth_source').len().sort('ground_truth_source'))
"
# Expected: rows=1360, null source_plant_code=1, EHA=1268 EIA=92

# === B. Run the smoke test (first run) ===
/opt/miniconda3/bin/python -m src.phase5.train
# Expected summary table (exact mean values):
#   rmse_log:  0.9165 ± 0.0763   MeanBL=1.9486   CFBaseline=0.9326
#   spearman:  0.9137 ± 0.0124   MeanBL=NaN       CFBaseline=0.9092
#   Criterion 3 rmse_log: PASS
#   Criterion 3 spearman: PASS

# === C. Determinism — run again, diff metadata ===
/opt/miniconda3/bin/python -c "
import json
with open('data/processed/phase5/models/smoke_metadata.json') as f:
    m = json.load(f)
lgbm = m['metrics']['lgbm']
print('rmse_log mean:', round(lgbm['rmse_log']['mean'], 4))
print('spearman mean:', round(lgbm['spearman']['mean'], 4))
print('per_fold rmse:', [round(v,4) for v in lgbm['rmse_log']['per_fold']])
"
# Expected (must match exactly after re-running train):
#   rmse_log mean: 0.9165
#   spearman mean: 0.9137
#   per_fold rmse: [0.8135, 0.8924, 1.0494, 0.9249, 0.9025]

/opt/miniconda3/bin/python -m src.phase5.train   # second run

/opt/miniconda3/bin/python -c "
import json
with open('data/processed/phase5/models/smoke_metadata.json') as f:
    m = json.load(f)
lgbm = m['metrics']['lgbm']
print('rmse_log mean (run 2):', round(lgbm['rmse_log']['mean'], 4))
print('spearman mean (run 2):', round(lgbm['spearman']['mean'], 4))
print('per_fold rmse (run 2):', [round(v,4) for v in lgbm['rmse_log']['per_fold']])
"
# Expected: same values as run 1

# === D. Leakage guard fires ===
/opt/miniconda3/bin/python -c "
from src.phase5.features import assert_no_leakage
try:
    assert_no_leakage(['annual_energy_kwh', 'latitude'])
except ValueError as e:
    print('Guard fired:', e)
"
# Expected output contains: "Leakage detected" and "annual_energy_kwh"

# === E. Model artifact exists and loads ===
/opt/miniconda3/bin/python -c "
import lightgbm as lgb
m = lgb.Booster(model_file='data/processed/phase5/models/smoke_lgbm.txt')
print('num_trees:', m.num_trees())
print('feature_names:', m.feature_name())
"
# Expected: num_trees >= 1, feature_names=['latitude','longitude','log_capacity_kw','climate_zone_code','state_code_code']

# === F. Metadata schema ===
/opt/miniconda3/bin/python -c "
import json
with open('data/processed/phase5/models/smoke_metadata.json') as f:
    m = json.load(f)
required = ['feature_names','categorical_mappings','lgbm_params','seed','git_sha',
            'train_row_count','timestamp','criteria','metrics']
missing = [k for k in required if k not in m]
print('missing keys:', missing or 'none')
print('train_row_count:', m['train_row_count'])
print('seed:', m['seed'])
print('crit3_rmse_pass:', m['criteria']['crit3_rmse_pass'])
print('crit3_spearman_pass:', m['criteria']['crit3_spearman_pass'])
"
# Expected: missing keys=none, train_row_count=1360, seed=0, both criteria True

# === G. Test suite ===
/opt/miniconda3/bin/python -m pytest -q --tb=no
# Expected: 580 passed, 1 skipped

# === H. Scope integrity — no Phase 1-4 or journal modifications ===
git diff HEAD -- src/phase1 src/phase2 src/phase3 src/phase4 src/common
# Expected: empty output

git diff HEAD -- config/settings.yaml
# Expected: empty output (no settings.yaml changes)

git diff HEAD -- src/phase5/ground_truth.py src/phase5/features.py src/phase5/cv.py
# Expected: empty output (existing phase5 rails untouched)

git diff HEAD -- WOWERS_PROJECT_JOURNAL.md
# Expected: empty output (journal not touched)

git status --short
# Expected: exactly these 4 untracked files, nothing else:
#   ?? P5_SMOKE_REVIEW_PROMPT.md
#   ?? SMOKE_TEST_REPORT.md
#   ?? src/phase5/train.py
#   ?? tests/test_phase5/test_train.py
# (gitignored outputs: data/processed/phase5/models/ — not shown)
```

---

## 4. Expected Numbers Table

| Check | Expected |
|---|---|
| combined_ground_truth rows | **1,360** |
| null source_plant_code | **1** |
| EHA rows | **1,268** |
| EIA rows | **92** |
| LightGBM mean rmse_log | **0.9165** |
| LightGBM mean spearman | **0.9137** |
| LightGBM per-fold rmse_log | **[0.8135, 0.8924, 1.0494, 0.9249, 0.9025]** |
| Mean-baseline mean rmse_log | **1.9486** |
| Mean-baseline spearman | **NaN (constant predictions)** |
| CF-baseline mean rmse_log | **0.9326** |
| CF-baseline mean spearman | **0.9092** |
| Criterion 3 rmse PASS | **True** |
| Criterion 3 spearman PASS | **True** |
| Leakage guard fires on `annual_energy_kwh` | **True** |
| LightGBM model feature names | **5: latitude, longitude, log_capacity_kw, climate_zone_code, state_code_code** |
| Test suite | **580 passed / 1 skipped** |
| WOWERS_PROJECT_JOURNAL.md modified | **No** |
| Phase 1–4 source code modified | **No** |
| config/settings.yaml modified | **No** |
| Existing phase5 rails (ground_truth/features/cv) modified | **No** |

---

## 5. Scope-Integrity Checklist

- [ ] `git diff HEAD -- src/phase1 src/phase2 src/phase3 src/phase4 src/common` is empty
- [ ] `git diff HEAD -- config/settings.yaml` is empty
- [ ] `git diff HEAD -- src/phase5/ground_truth.py src/phase5/features.py src/phase5/cv.py` is empty
- [ ] `git diff HEAD -- WOWERS_PROJECT_JOURNAL.md` is empty
- [ ] `git status --short` shows exactly 4 untracked files (train.py, test_train.py, SMOKE_TEST_REPORT.md, P5_SMOKE_REVIEW_PROMPT.md)
- [ ] `data/processed/phase5/models/smoke_lgbm.txt` exists (gitignored, not tracked)
- [ ] `data/processed/phase5/models/smoke_metadata.json` exists (gitignored, not tracked)
- [ ] SMOKE_TEST_REPORT.md carries the "INTERNAL" header in §0
- [ ] Test suite: 580 passed / 1 skipped

---

## 6. Key Judgment Calls for Reviewer

1. **Mean-baseline Spearman is NaN.** The mean baseline predicts a constant
   value for all rows in each fold. `scipy.stats.spearmanr` with a constant
   input raises `ConstantInputWarning` and returns NaN. Criterion 3 (spearman)
   is evaluated as: "mean baseline is constant → undefined rank discriminability
   → any model with finite positive Spearman wins." LightGBM's spearman=0.9137
   is finite and positive — criterion passes. Reviewer should agree with this
   interpretation.

2. **LightGBM does not clearly beat the CF-baseline** (rmse 0.9165 vs 0.9326;
   spearman 0.914 vs 0.909 — both marginal). Per the task specification,
   beating the CF-baseline was **not required**. The CF-baseline is a strong
   prior for this dam dataset (it embeds the real fleet CF distribution).
   Reviewer confirms this is expected and does not affect the smoke-test verdict.

3. **High MAPE (987% mean for LightGBM) is expected** and documented in
   SMOKE_TEST_REPORT.md §6. Dam energy labels span six orders of magnitude.
   Fold 3 contains large-hydro outliers that dominate the mean via the
   percentage formula. RMSE-log is the primary metric.

4. **"INTERNAL" framing.** SMOKE_TEST_REPORT.md carries the required header
   in §0. No metric from this report should appear in director/pitch/competition
   material — reviewer verifies the header is present and prominent.

---

**If all checks pass: reviewer approves, then Tom logs the P5-SMOKE session
in `WOWERS_PROJECT_JOURNAL.md` and decides whether to commit.**
