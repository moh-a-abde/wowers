# WOWERS — Team Setup Guide

**Waste Outfall Water Energy Recovery System**
University of St. Thomas · May 2026

---

## ⚡ Option A — Let AI Set It Up For You (Recommended)

If you have **Claude Code** or any AI coding assistant, skip this entire guide.
Copy the prompt below, paste it into your AI assistant, and it handles everything automatically.

```
Install Claude Code (if you don't have it):
npm install -g @anthropic-ai/claude-code
Then run: claude
```

### 📋 Copy This Prompt Into Claude Code

```
You are setting up the WOWERS project on a new machine. Complete ALL of the
following steps in order without asking for confirmation between steps. If a
step fails, diagnose and fix it before continuing. Report a summary at the end.

STEP 1 — CLONE THE REPO
Clone the WOWERS GitHub repository into the current directory. If the user has
not provided the repo URL, ask for it once before proceeding.

STEP 2 — PYTHON ENVIRONMENT
Check that Python 3.11+ is available. Create a virtual environment named .venv
inside the project folder. Activate it. Run: pip install -e . and confirm all
packages install without errors.

STEP 3 — VERIFY TESTS
Run: python -m pytest tests/ -v
Expected result: 237 passed.
If any tests fail, diagnose and fix the issue before continuing. Do not proceed
past this step if tests are failing.

STEP 4 — RAW DATA
Ask the user: "Where is your EPA raw data stored? Provide the full path to the
folder containing the DMR ZIPs and ICIS CSVs."
Once they provide the path, create the data/raw/ directory structure and set up
symlinks or update config/settings.yaml so the pipeline can find the data.
Verify by listing the files through the resolved paths.

STEP 5 — VERIFY DATA PATHS
Confirm these files are accessible:
- ICIS_FACILITIES.CSV
- ICIS_PERMITS.CSV
- At least one DMR ZIP (e.g. npdes_dmrs_fy2024.zip)
- NPDES_PERM_FEATURE_COORDS.csv
- npdes_outfalls_layer.csv (External Outfall coordinates — required for Phase 3)
List them and confirm their sizes are non-zero.

STEP 6 — SMOKE TEST
Confirm the pipeline entry points are importable without errors:
python -c "from src.phase1 import run; from src.phase2 import run;
from src.phase3 import run; from src.phase4 import run;
print('All phases importable ✓')"

STEP 7 — REPORT
Print a setup summary showing: Python version, virtual env path, number of
tests passed, which data files were found, which were missing, and the exact
commands needed to run each pipeline phase.
```

> 💡 **How to use:** Open Claude Code in your terminal inside the project folder. Paste the entire prompt above as your first message. The AI will guide you through the rest with one command.

---

---

## Option B — Manual Setup

Follow the steps below if you prefer to set things up yourself.

---

## Requirements

| Requirement | Version | How to Check |
|---|---|---|
| Python | 3.11 or higher | `python --version` or `python3 --version` |
| Git | Any recent version | `git --version` |
| pip | Comes with Python | `pip --version` |
| Disk space | At least 15 GB free | Raw data is ~10 GB, expands to ~13 GB processed |
| Internet | Required for Phase 3 | Phase 3 calls the USGS 3DEP elevation API |

> 💡 **Mac vs Windows:** This guide uses Mac/Linux paths (forward slashes). On Windows replace forward slashes with backslashes and use Command Prompt or PowerShell. All Python commands are identical on both platforms.

---

## Step 1 — Clone the Repository

```bash
# Navigate to wherever you keep your projects
cd ~/Documents

# Clone the repo (replace with actual URL)
git clone https://github.com/YOUR_ORG/wowers.git

# Move into the project folder
cd wowers

# Verify the structure looks right
ls
# You should see: src/  config/  tests/  data/  pyproject.toml  ARCHITECTURE.md
```

---

## Step 2 — Create a Python Virtual Environment

A virtual environment keeps all project packages separate from your system Python. **Always do this step.**

### Mac / Linux

```bash
# From inside the wowers folder
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Your terminal prompt will now show (.venv) at the front
# Example:  (.venv) user@machine wowers %
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

> ⚠️ **Every session:** Every time you open a new terminal to work on WOWERS, run the activate command above first. If you see `ModuleNotFoundError`, the virtual environment is not active.

---

## Step 3 — Install All Dependencies

With the virtual environment activated:

```bash
# Install the project and all dependencies
pip install -e .

# The -e means 'editable install' — changes to src/ take effect immediately

# Verify key packages installed correctly
pip list | grep polars      # should show polars 0.20+
pip list | grep numpy       # should show numpy 1.26+
pip list | grep lightgbm    # should show lightgbm 4.0+
```

### What Gets Installed

| Package | Version | What It Does in WOWERS |
|---|---|---|
| `polars` | 0.20+ | Reads and filters the 279 million raw DMR rows |
| `numpy` | 1.26+ | Vectorized math — 10,000 Monte Carlo simulations per plant |
| `scipy` | 1.12+ | Statistics and IRR calculation (Brent's method) |
| `pyarrow` | 14.0+ | Reads and writes Parquet files between phases |
| `httpx` | 0.27+ | Async HTTP — calls the USGS 3DEP elevation API |
| `lightgbm` | 4.0+ | Machine learning — used in Phase 5 |
| `pyyaml` | 6.0+ | Reads `config/settings.yaml` and electricity rates |
| `numpy-financial` | 1.0+ | NPV, IRR, and payback period calculations |

---

## Step 4 — Run the Test Suite

Before touching any real data, confirm everything works:

```bash
python -m pytest tests/ -v

# Expected output at the bottom:
# ============== 237 passed in X.XXs ==============
```

If tests fail, check these things:
- Virtual environment is activated (the `(.venv)` prefix is visible)
- `pip install -e .` completed without errors
- Python version is 3.11 or higher: `python --version`

> ✅ **Pass criteria:** `237 passed` with no failures or errors. Do not proceed to Step 5 until all 237 pass.

---

## Step 5 — Set Up the Raw Data

The pipeline needs four data sources. The raw files are **not** in the Git repo. Choose one option below.

> ⚠️ **Size warning:** The full DMR dataset is 16 ZIP files, approximately 600 MB each, totaling ~10 GB. Option A (fresh download) takes 30–90 minutes. Option B (symlink from a drive) is much faster.

---

### Option A — Download Fresh from EPA

All sources are free, public, and updated weekly by the US government.

#### A1: Create folder structure

```bash
mkdir -p data/raw/dmr
mkdir -p data/raw/npdes_downloads
mkdir -p data/raw/npdes_outfalls
```

#### A2: Download ICIS facility and permit data (~320 MB)

```bash
cd data/raw/npdes_downloads

# Mac/Linux
curl -L -o npdes_downloads.zip \
  https://echo.epa.gov/files/echodownloads/npdes_downloads.zip
unzip npdes_downloads.zip

# Windows PowerShell
Invoke-WebRequest -Uri https://echo.epa.gov/files/echodownloads/npdes_downloads.zip `
  -OutFile npdes_downloads.zip

cd ../../..
```

#### A3: Download NPDES outfalls layer (~46 MB) — Required for Phase 3

This file contains GPS coordinates of actual discharge pipe locations. Phase 3 uses it as the primary coordinate source for elevation lookups. **Without this file, Phase 3 falls back to facility centroids and produces less accurate head estimates.**

```bash
cd data/raw/npdes_outfalls

# Mac/Linux
curl -L -o npdes_outfalls_layer.zip \
  https://echo.epa.gov/files/echodownloads/npdes_outfalls_layer.zip
unzip npdes_outfalls_layer.zip

# Windows PowerShell
Invoke-WebRequest -Uri https://echo.epa.gov/files/echodownloads/npdes_outfalls_layer.zip `
  -OutFile npdes_outfalls_layer.zip

cd ../../..
```

#### A4: Download DMR fiscal year files (~600 MB each, 16 files, ~10 GB total)

```bash
cd data/raw/dmr

# Mac/Linux — loop through all 16 years
for year in 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024; do
  curl -L -o npdes_dmrs_fy${year}.zip \
    https://echo.epa.gov/files/echodownloads/npdes_dmrs_fy${year}.zip
done

# Windows PowerShell
foreach ($year in 2009..2024) {
  $url = "https://echo.epa.gov/files/echodownloads/npdes_dmrs_fy$year.zip"
  Invoke-WebRequest -Uri $url -OutFile "npdes_dmrs_fy$year.zip"
}

cd ../../..
```

---

### Option B — Symlink from a Teammate's Drive

If another team member has the data on an external drive, this is much faster.

#### B1: Find the drive mount point

```bash
# Mac — drives appear under /Volumes/
ls /Volumes/

# Windows — drives appear as a letter (D:\ or E:\)
# Open File Explorer to check
```

#### B2: Create symlinks (no copying needed)

```bash
# Mac/Linux
mkdir -p data/raw
ln -s "/Volumes/DriveName/DMR Datasets" data/raw/dmr
ln -s "/Volumes/DriveName/npdes_downloads" data/raw/npdes_downloads
ln -s "/Volumes/DriveName/npdes_outfalls" data/raw/npdes_outfalls

# Windows — run Command Prompt AS ADMINISTRATOR
mkdir data\raw
mklink /D data\raw\dmr "D:\DMR Datasets"
mklink /D data\raw\npdes_downloads "D:\npdes_downloads"
mklink /D data\raw\npdes_outfalls "D:\npdes_outfalls"
```

> ⚠️ **Drive must be connected:** If using symlinks, the external drive must be plugged in every time the pipeline runs.

#### B3: Alternative — use `--raw-dir` flag instead of symlinks

```bash
# Pass the data path directly at runtime
# Mac example
python -m src.phase1.run --skip-download --raw-dir "/Volumes/DriveName"

# Windows example
python -m src.phase1.run --skip-download --raw-dir "D:\wowers_data"
```

---

## Step 6 — Verify Data Paths

```bash
# Verify ICIS files
ls data/raw/npdes_downloads/
# Must show: ICIS_FACILITIES.CSV  ICIS_PERMITS.CSV

# Verify outfalls layer
ls data/raw/npdes_outfalls/
# Must show: npdes_outfalls_layer.csv

# Verify DMR ZIPs
ls data/raw/dmr/*.zip | wc -l
# Must show: 16

# Verify files are non-empty
python3 -c "
import os
files = [
  'data/raw/npdes_downloads/ICIS_FACILITIES.CSV',
  'data/raw/npdes_downloads/ICIS_PERMITS.CSV',
]
for f in files:
    size = os.path.getsize(f)
    print(f'{f}: {size:,} bytes OK' if size > 0 else f'ERROR: {f} is empty')
"
```

---

## Step 7 — Run the Pipeline

> ⏱️ **Time warning:** Phase 1 takes ~65 minutes (279 million rows). Phase 2 and 4 take under 5 minutes each. Phase 3 takes 30–60 minutes for USGS API calls. Total: 2–3 hours.

### Phase 1 — Rank Candidate Plants (~65 min)

```bash
python -m src.phase1.run --skip-download

# With custom data path (if not using symlinks):
python -m src.phase1.run --skip-download --raw-dir /path/to/your/data
```

**Output files:**
- `data/processed/phase1/potw_facilities.parquet`
- `data/processed/phase1/dmr_flow_timeseries.parquet`
- `data/processed/phase1/flow_features.parquet`
- `data/processed/phase1/ranked_candidates.parquet` ← main output

**Expected:** 17,158 facilities, 459 DMR artifact rows nulled

---

### Phase 2 — Energy Yield Estimation (~1 min)

```bash
python -m src.phase2.run
```

**Output:** `data/processed/phase2/energy_yield_estimates.parquet`

**Expected:** ~847 GWh/yr national P50 energy estimate

---

### Phase 3 — Turbine Sizing (~30–60 min)

```bash
# Quick smoke test first (recommended)
python -m src.phase3.run --top-n 10

# Full run
python -m src.phase3.run
```

**Output:** `data/processed/phase3/turbine_sizing.parquet`

**Expected:** 9,631 sites on real USGS 3DEP head (63.1%), 3,873 turbine-viable sites

---

### Phase 4 — Financial Scorecard (~2 min)

```bash
python -m src.phase4.run
```

**Output:** `data/processed/phase4/financial_scorecards.parquet`

**Expected:** 1,097 viable projects, $49.9M/yr revenue, 14.3-year median payback

---

## Step 8 — Verify Your Results

After all four phases complete, run these checks:

```python
python3

import polars as pl

# Phase 1
df1 = pl.read_parquet('data/processed/phase1/ranked_candidates.parquet')
print(f'Phase 1: {len(df1):,} facilities')          # expect: 17,158

# Phase 2
df2 = pl.read_parquet('data/processed/phase2/energy_yield_estimates.parquet')
national = df2['energy_p50_kwh_yr'].sum() / 1e9
print(f'Phase 2: {national:.1f} GWh/yr')             # expect: ~847 GWh

# Phase 3
df3 = pl.read_parquet('data/processed/phase3/turbine_sizing.parquet')
real_head = (df3['head_source'] == '3dep').sum()
print(f'Phase 3: {len(df3):,} sized, {real_head:,} on 3DEP head')  # expect: 3,873 / 9,631

# Phase 4
df4 = pl.read_parquet('data/processed/phase4/financial_scorecards.parquet')
viable = df4.filter(pl.col('project_viable') == True)
print(f'Phase 4: {len(viable):,} viable')            # expect: 1,097
print(f'Median payback: {viable["payback_years"].median():.1f} yrs')  # expect: ~14.3

exit()
```

---

## Step 9 — Finding Your Logs

Every pipeline run saves a timestamped log file automatically:

```bash
# List all run logs
ls logs/runs/
# Example: phase1_2026-05-19_23-12-00.log

# Read a log
cat logs/runs/phase1_2026-05-19_23-12-00.log | less

# Search for a specific plant
grep 'IL0028053' logs/runs/phase1_2026-05-19_23-12-00.log

# See last 50 lines
tail -50 logs/runs/phase4_2026-05-19_05-52-12.log
```

---

## Common Errors and Fixes

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'polars'` | Virtual environment not active | Run `source .venv/bin/activate` then `pip install -e .` |
| `FileNotFoundError: data/raw/dmr/...` | Pipeline cannot find EPA data | Check symlinks or pass `--raw-dir /path/to/data` |
| `FileNotFoundError: ICIS_FACILITIES.CSV` | ICIS data not downloaded | Complete Step A2 |
| `FileNotFoundError: npdes_outfalls_layer.csv` | Outfalls layer missing — required for Phase 3 | Complete Step A3. This file is essential for accurate head data. |
| `ConnectionError / USGS API timeout` | Phase 3 cannot reach USGS | Check internet connection. Pipeline retries automatically. |
| Tests: fewer than 237 passing | Wrong Python version or missing package | Confirm Python 3.11+ and re-run `pip install -e .` |
| Phase 3 shows 0% 3DEP head sites | Outfalls layer CSV not found | Verify `data/raw/npdes_outfalls/` contains the CSV |
| Phase 4 viable count much lower than 1,097 | Phase 3 ran without outfalls layer | Re-run Phase 3 after confirming the outfalls layer is in place |

---

## Project File Structure

```
wowers/
├── src/
│   ├── phase1/               # Plant ranking pipeline
│   │   ├── run.py            # python -m src.phase1.run
│   │   ├── filter_potw.py
│   │   ├── dmr_timeseries.py
│   │   ├── flow_features.py
│   │   └── ranking.py
│   ├── phase2/               # Energy yield estimation
│   │   ├── run.py            # python -m src.phase2.run
│   │   ├── energy_physics.py
│   │   └── monte_carlo.py
│   ├── phase3/               # Turbine sizing + elevation
│   │   ├── run.py            # python -m src.phase3.run
│   │   ├── elevation.py
│   │   ├── head_estimation.py
│   │   ├── turbine_selection.py
│   │   └── outfall_coords.py     ← uses External Outfall coords
│   ├── phase4/               # Financial scorecard
│   │   ├── run.py            # python -m src.phase4.run
│   │   ├── financials.py
│   │   ├── cost_models.py
│   │   └── revenue.py
│   └── common/               # Shared utilities (logging, config, I/O)
├── config/
│   ├── settings.yaml             # All thresholds, weights, physics constants
│   └── electricity_rates/
│       └── state_rates.yaml      # 2023 EIA rates for all 50 states + DC
├── data/
│   ├── raw/                      # EPA downloads — GITIGNORED, not in repo
│   │   ├── dmr/                  # 16 fiscal year ZIP files (FY2009–FY2024)
│   │   ├── npdes_downloads/      # ICIS_FACILITIES.CSV + ICIS_PERMITS.CSV
│   │   └── npdes_outfalls/       # npdes_outfalls_layer.csv
│   ├── processed/                # Pipeline outputs — GITIGNORED, not in repo
│   └── turbines/
│       └── turbine_manufacturers.csv   # Turbine product database
├── tests/                        # 237 automated tests
├── logs/runs/                    # Timestamped run logs — GITIGNORED
├── pyproject.toml                # Dependency list
└── ARCHITECTURE.md               # Full 5-phase technical specification
```

---

## Quick Command Reference

| What You Want To Do | Command |
|---|---|
| Activate virtual environment (Mac/Linux) | `source .venv/bin/activate` |
| Activate virtual environment (Windows) | `.venv\Scripts\activate` |
| Install / update all packages | `pip install -e .` |
| Run all 237 tests | `python -m pytest tests/ -v` |
| Run Phase 1 (~65 min) | `python -m src.phase1.run --skip-download` |
| Run Phase 2 (~1 min) | `python -m src.phase2.run` |
| Run Phase 3 smoke test (10 plants) | `python -m src.phase3.run --top-n 10` |
| Run Phase 3 full (~45 min) | `python -m src.phase3.run` |
| Run Phase 4 (~2 min) | `python -m src.phase4.run` |
| Run with custom data path | `python -m src.phase1.run --skip-download --raw-dir /path` |
| View recent run logs | `ls logs/runs/` |
| Pull latest code | `git pull origin main` |
| Check Python version | `python --version` |
| Check active virtual environment | `which python` (Mac) or `where python` (Windows) |

---

## Expected Pipeline Results

When everything is set up correctly, your results should match these canonical numbers:

| Phase | Metric | Expected Value |
|---|---|---|
| Phase 1 | Facilities identified | **17,158** |
| Phase 1 | DMR artifact rows nulled | **459** |
| Phase 2 | National P50 energy | **~847 GWh/yr** |
| Phase 3 | Sites on real USGS 3DEP head | **9,631 (63.1%)** |
| Phase 3 | Turbine-viable sites | **3,873** |
| Phase 4 | Viable projects (NPV+, payback ≤ 20yr) | **1,097** |
| Phase 4 | Median payback period | **14.3 years** |
| Phase 4 | Annual revenue potential | **$49.9M/yr** |

If your numbers differ significantly, re-check the data paths and re-run the affected phase.

---

*WOWERS · University of St. Thomas · May 2026 · Questions? Reach out to the project team.*
