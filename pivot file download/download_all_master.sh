#!/usr/bin/env bash
# ============================================================
# download_all_master.sh
# WOWERS Pivot Verticals — complete dataset downloader
#
# Downloads all bulk-downloadable datasets for all 4 verticals:
#   V1 — Water Utility PRVs
#   V2 — Industrial Cooling-Water Discharge
#   V3 — Mine Dewatering
#   V4 — Irrigation Canal Drops (no bulk downloads — API/manual only)
#
# Total expected download: ~25 GB
# Time estimate: 2–6 hours depending on connection speed
#
# Run from your Mac Terminal:
#   chmod +x /Volumes/SANDISK/WOWERS_Pivot_Data/download_all_master.sh
#   /Volumes/SANDISK/WOWERS_Pivot_Data/download_all_master.sh
#
# The script is safe to re-run — files larger than 512 KB are skipped.
# ============================================================

set -euo pipefail

# Change BASE to the actual path on your machine where you want to save the files
BASE="/Volumes/SANDISK/WOWERS_Pivot_Data"
V1="$BASE/V1_Water_Utility_PRVs"
V2="$BASE/V2_Industrial_Cooling_Water_Discharge"
V3="$BASE/V3_Mine_Dewatering"
V4="$BASE/V4_Irrigation_Canal_Drops"

MIN_SIZE=524288   # 512 KB — anything smaller is treated as a failed/error download
PASS=0
FAIL=0
SKIP=0

# ── helpers ──────────────────────────────────────────────────
dl() {
  local url="$1"
  local dest="$2"

  if [[ -f "$dest" ]]; then
    local sz
    sz=$(stat -f%z "$dest" 2>/dev/null || stat -c%s "$dest" 2>/dev/null || echo 0)
    if (( sz > MIN_SIZE )); then
      echo "  ✓ SKIP  $(basename "$dest")  ($(( sz / 1048576 )) MB)"
      (( SKIP++ )) || true
      return
    fi
  fi

  echo "  → GET   $(basename "$dest")"
  if curl --fail -L --retry 3 --progress-bar -o "$dest" "$url"; then
    local sz
    sz=$(stat -f%z "$dest" 2>/dev/null || stat -c%s "$dest" 2>/dev/null || echo 0)
    if (( sz > MIN_SIZE )); then
      echo "  ✓ OK    $(basename "$dest")  ($(( sz / 1048576 )) MB)"
      (( PASS++ )) || true
    else
      echo "  ✗ SMALL $(basename "$dest")  (${sz} bytes)"
      (( FAIL++ )) || true
    fi
  else
    echo "  ✗ FAIL  $(basename "$dest")"
    (( FAIL++ )) || true
  fi
}

section() { echo ""; echo "========================================================"; echo " $*"; echo "========================================================"; }

# ── create folders ───────────────────────────────────────────
mkdir -p "$V1" "$V2" "$V3" "$V4"

# ============================================================
section "V1 — Water Utility PRVs"
# ============================================================

# ── SDWA (Safe Drinking Water Act data) ─────────────────────
section "  V1.1  SDWA"
dl "https://echo.epa.gov/files/echodownloads/SDWA_latest_downloads.zip" \
   "$V1/SDWA_latest_downloads.zip"

# ── EIA-861 (Annual Electric Power Industry Report) ─────────
# Naming convention changed at 2012: pre-2012 uses 2-digit year codes.
section "  V1.2  EIA-861  (2009-2024)"
dl "https://www.eia.gov/electricity/data/eia861/archive/zip/861_2009.zip"   "$V1/EIA861_2009.zip"
dl "https://www.eia.gov/electricity/data/eia861/archive/zip/861_2010.zip"   "$V1/EIA861_2010.zip"
dl "https://www.eia.gov/electricity/data/eia861/archive/zip/861_2011.zip"   "$V1/EIA861_2011.zip"
for year in 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023; do
  dl "https://www.eia.gov/electricity/data/eia861/archive/zip/f861${year}.zip" \
     "$V1/EIA861_${year}.zip"
done
dl "https://www.eia.gov/electricity/data/eia861/zip/f8612024.zip"           "$V1/EIA861_2024.zip"

# ── NHDPlus V2 National Seamless Geodatabase (~7.3 GB) ──────
section "  V1.3  NHDPlus V2 (~7 GB — this will take a while)"
dl "https://dmap-data-commons-ow.s3.amazonaws.com/NHDPlusV21/Data/NationalData/NHDPlusV21_NationalData_Seamless_Geodatabase_Lower48_07.7z" \
   "$V1/NHDPlusV2_National_Seamless_Lower48.7z"

# ============================================================
section "V2 — Industrial Cooling-Water Discharge"
# ============================================================

# ── ECHO NPDES ───────────────────────────────────────────────
section "  V2.1  ECHO NPDES facilities, effluent, outfalls, FRS"
dl "https://echo.epa.gov/files/echodownloads/npdes_downloads.zip"           "$V2/ECHO_NPDES_facilities.zip"
dl "https://echo.epa.gov/files/echodownloads/npdes_eff_downloads.zip"       "$V2/ECHO_NPDES_effluent_violations.zip"
dl "https://echo.epa.gov/files/echodownloads/npdes_outfalls_layer.zip"      "$V2/ECHO_NPDES_outfall_locations.zip"
dl "https://echo.epa.gov/files/echodownloads/frs_downloads.zip"             "$V2/ECHO_FRS.zip"

# ── ECHO DMRs ────────────────────────────────────────────────
section "  V2.2  ECHO NPDES DMRs  (pre-FY2009 + FY2009-FY2026)"
dl "https://echo.epa.gov/files/echodownloads/npdes_dmrs_prefy2009.zip"      "$V2/ECHO_NPDES_DMR_pre_FY2009.zip"
for year in 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026; do
  dl "https://echo.epa.gov/files/echodownloads/npdes_dmrs_fy${year}.zip" \
     "$V2/ECHO_NPDES_DMR_FY${year}.zip"
done

# ── EIA-860 (Power Plant Equipment) ─────────────────────────
section "  V2.3  EIA-860  (2009-2024)"
for year in 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023; do
  dl "https://www.eia.gov/electricity/data/eia860/archive/xls/eia860${year}.zip" \
     "$V2/EIA860_${year}.zip"
done
dl "https://www.eia.gov/electricity/data/eia860/xls/eia8602024.zip"         "$V2/EIA860_2024.zip"

# ── EIA-923 (Power Plant Operations) ────────────────────────
# 2009-2024 are in the archive folder; 2025 is still the current-year file.
section "  V2.4  EIA-923  (2009-2025)"
for year in 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024; do
  dl "https://www.eia.gov/electricity/data/eia923/archive/xls/f923_${year}.zip" \
     "$V2/EIA923_${year}.zip"
done
dl "https://www.eia.gov/electricity/data/eia923/xls/f923_2025.zip"          "$V2/EIA923_2025.zip"

# ── TRI Basic Plus ───────────────────────────────────────────
# URLs confirmed from EPA dropdown on 2026-05-22.
# 2010 has a _0 suffix; 2011 is in a different date folder.
# Raw EPA filenames (us_YEAR.zip) differ from local names (TRI_YEAR.zip).
section "  V2.5  TRI Basic Plus  (2009-2022)"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2009.zip"       "$V2/TRI_2009.zip"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2010_0.zip"     "$V2/TRI_2010.zip"
dl "https://www.epa.gov/system/files/other-files/2026-01/us_2011.zip"       "$V2/TRI_2011.zip"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2012.zip"       "$V2/TRI_2012.zip"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2013.zip"       "$V2/TRI_2013.zip"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2014.zip"       "$V2/TRI_2014.zip"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2015.zip"       "$V2/TRI_2015.zip"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2016.zip"       "$V2/TRI_2016.zip"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2017.zip"       "$V2/TRI_2017.zip"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2018.zip"       "$V2/TRI_2018.zip"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2019.zip"       "$V2/TRI_2019.zip"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2020.zip"       "$V2/TRI_2020.zip"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2021.zip"       "$V2/TRI_2021.zip"
dl "https://www.epa.gov/system/files/other-files/2025-11/us_2022.zip"       "$V2/TRI_2022.zip"

# ── BLS QCEW ─────────────────────────────────────────────────
section "  V2.6  BLS QCEW  (2009-2023)"
for year in 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023; do
  dl "https://data.bls.gov/cew/data/files/${year}/csv/${year}_annual_by_industry.zip" \
     "$V2/BLS_QCEW_${year}.zip"
done

# ============================================================
section "V3 — Mine Dewatering"
# ============================================================
# Note: there is no separate MinesSic download — SIC codes are inside Mines.csv.
# Employment/Production dataset is now called MinesProdYearly on MSHA's portal.
dl "https://arlweb.msha.gov/OpenGovernmentData/DataSets/Mines.zip"          "$V3/MSHA_Mines.zip"
dl "https://arlweb.msha.gov/OpenGovernmentData/DataSets/Accidents.zip"      "$V3/MSHA_Accidents.zip"
dl "https://arlweb.msha.gov/OpenGovernmentData/DataSets/Inspections.zip"    "$V3/MSHA_Inspections.zip"
dl "https://arlweb.msha.gov/OpenGovernmentData/DataSets/Violations.zip"     "$V3/MSHA_Violations.zip"
dl "https://arlweb.msha.gov/OpenGovernmentData/DataSets/MinesProdYearly.zip" \
   "$V3/MSHA_EmployerProd.zip"

# ============================================================
section "V4 — Irrigation Canal Drops"
# ============================================================
echo ""
echo "  V4 has no bulk-downloadable files."
echo "  NHDPlus V2 is shared from V1 — do not duplicate."
echo "  The following must be downloaded manually:"
echo "    • USBR RISE  → see $V4/USBR_RISE_instructions.txt"
echo "    • USDA NASS  → https://quickstats.nass.usda.gov/"
echo "    • CA DWR     → https://data.cnra.ca.gov/"

# ============================================================
section "SUMMARY"
# ============================================================
printf "  Passed: %d   Failed: %d   Skipped (already on disk): %d\n" "$PASS" "$FAIL" "$SKIP"
echo ""
echo "  Disk usage:"
for dir in V1_Water_Utility_PRVs V2_Industrial_Cooling_Water_Discharge V3_Mine_Dewatering V4_Irrigation_Canal_Drops; do
  sz=$(du -sh "$BASE/$dir" 2>/dev/null | cut -f1)
  echo "    $dir:  $sz"
done
echo "    Total: $(du -sh "$BASE" 2>/dev/null | cut -f1)"
echo ""

if (( FAIL > 0 )); then
  echo "  ✗ $FAIL download(s) failed — re-run the script to retry."
  exit 1
else
  echo "  ✓ All downloads complete."
fi
