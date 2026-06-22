"""Phase 5 ground-truth ingestion — EIA-860 + EIA-923 hydropower labels.

Builds the labeled dataset the Phase 5 ML model trains against: real
US hydropower plants with known installed capacity and annual energy output.
See ``ARCHITECTURE.md`` §5.2–5.3 for the schema and the (later) spatial/fuzzy
matching strategy to ECHO POTW plants.

Source
------
EIA Form 860 (generator inventory) + EIA Form 923 (generation), both already
on disk under the configured ``phase5.eia_data_dir``:

  EIA860_<year>/2___Plant_Y<year>.xlsx        plant lat/lon/name/state
  EIA860_<year>/3_1_Generator_Y<year>.xlsx    per-generator nameplate + prime mover
  EIA923_<year>/EIA923_Schedules_2_3_4_5...xlsx  per-plant annual net generation

Three EIA gotchas this module handles:
  1. The generator workbook's first sheet is "Proposed" (no nameplate). We read
     the **"Operable"** sheet.
  2. EIA workbooks have title rows above the header: Form-860 header is row 2,
     Form-923 "Page 1" header is row 6.
  3. Form-923 reports multiple rows per plant (one per prime mover / fuel). We
     filter to ``Reported Prime Mover == HY`` and sum to plant level so the
     energy label isolates hydro at mixed-technology plants.

KNOWN BIAS — large hydro
------------------------
EIA-860 only inventories generators of roughly **>= 1 MW** nameplate, so this
ground-truth set skews to utility-scale conventional hydro and is **not
representative of the WWTP micro-scale** sites WOWERS targets (most < 1 MW).
This is the ARCHITECTURE.md §risk row on label bias. Use it to train the
physics-correction relationship energy = f(capacity, head, flow); supplement
with FERC conduit / DOE HydroSource small-scale labels (downloaded to the
external drive under Phase5_ML_GroundTruth/) before trusting micro-scale
predictions. Future small-scale sources append to the same canonical schema
via additional ingest functions — do not change the schema to fit one source.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import polars as pl

from src.common import config, io, logging_setup

logging_setup.setup_run_log("phase5")
log = logging_setup.get("wowers.phase5")

# ── Canonical ground-truth schema (source-agnostic) ──────────────────────────
# Defined once. FERC / DOE HydroSource ingests must emit these same columns.
CANONICAL_SCHEMA: dict[str, pl.DataType] = {
    "ground_truth_source": pl.Utf8,        # "EIA", later "FERC", "EHA", ...
    "facility_name": pl.Utf8,              # for later fuzzy match to ECHO
    "state_code": pl.Utf8,                 # 2-letter, for later spatial match
    "latitude": pl.Float64,                # decimal degrees (nullable)
    "longitude": pl.Float64,               # decimal degrees (nullable)
    "actual_annual_energy_kwh": pl.Float64,  # TARGET label
    "actual_installed_kw": pl.Float64,     # secondary label
    "actual_head_m": pl.Float64,           # null for EIA (not reported)
    "actual_flow_m3s": pl.Float64,         # null for EIA (not reported)
    "source_plant_code": pl.Int64,         # EIA plant code — provenance / join key
    "source_year": pl.Int64,
}

HYDRO_PRIME_MOVER = "HY"  # conventional hydro; PS / HPS (pumped storage) excluded
MW_TO_KW = 1_000.0
MWH_TO_KWH = 1_000.0

OUTPUT_PATH: Path = config.raw_data_dir() / "ground_truth" / "eia_hydro_ground_truth.parquet"


# ── Column-name helpers (EIA names drift slightly across years) ───────────────
def _norm(name: str) -> str:
    """Lowercase, collapse whitespace/newlines, strip — for tolerant matching."""
    return re.sub(r"\s+", " ", str(name).replace("\n", " ")).strip().lower()


def _find_col(columns: list[str], *substrings: str) -> str:
    """Return the first column whose normalized name contains ALL substrings.

    Raises KeyError if none match, so a silent column rename in a future EIA
    vintage fails loudly rather than producing a wrong label.
    """
    subs = [s.lower() for s in substrings]
    for c in columns:
        n = _norm(c)
        if all(s in n for s in subs):
            return c
    raise KeyError(f"no column matching {substrings!r} in {columns!r}")


# ── Pure transforms (no IO — unit-tested on synthetic frames) ─────────────────
# These operate on STANDARDIZED column names produced by the IO layer:
#   generators: plant_code, prime_mover, nameplate_mw
#   generation: plant_code, prime_mover, net_gen_mwh
#   plants:     plant_code, plant_name, state_code, latitude, longitude
def aggregate_capacity_kw(generators: pl.DataFrame) -> pl.DataFrame:
    """Filter to hydro generators, sum nameplate MW to plant level, convert kW.

    Returns columns: plant_code, actual_installed_kw.
    """
    return (
        generators.filter(pl.col("prime_mover") == HYDRO_PRIME_MOVER)
        .group_by("plant_code")
        .agg((pl.col("nameplate_mw").cast(pl.Float64).sum() * MW_TO_KW).alias("actual_installed_kw"))
    )


def aggregate_generation_kwh(generation: pl.DataFrame) -> pl.DataFrame:
    """Filter to hydro rows, sum annual net generation MWh to plant level, to kWh.

    Returns columns: plant_code, actual_annual_energy_kwh.
    """
    return (
        generation.filter(pl.col("prime_mover") == HYDRO_PRIME_MOVER)
        .group_by("plant_code")
        .agg((pl.col("net_gen_mwh").cast(pl.Float64).sum() * MWH_TO_KWH).alias("actual_annual_energy_kwh"))
    )


def assemble_ground_truth(
    generators: pl.DataFrame,
    generation: pl.DataFrame,
    plants: pl.DataFrame,
    year: int,
) -> pl.DataFrame:
    """Join hydro capacity + generation + plant metadata into canonical schema.

    Drops plants missing a positive capacity OR a positive generation (cannot be
    a usable label). Returns a DataFrame with exactly CANONICAL_SCHEMA columns.
    """
    cap = aggregate_capacity_kw(generators)
    gen = aggregate_generation_kwh(generation)

    df = (
        cap.join(gen, on="plant_code", how="inner")
        .join(
            plants.select(
                "plant_code", "plant_name", "state_code", "latitude", "longitude"
            ),
            on="plant_code",
            how="left",
        )
        .filter(
            (pl.col("actual_installed_kw") > 0) & (pl.col("actual_annual_energy_kwh") > 0)
        )
        .with_columns(
            pl.lit("EIA").alias("ground_truth_source"),
            pl.col("plant_name").alias("facility_name"),
            pl.lit(None, dtype=pl.Float64).alias("actual_head_m"),
            pl.lit(None, dtype=pl.Float64).alias("actual_flow_m3s"),
            pl.col("plant_code").cast(pl.Int64).alias("source_plant_code"),
            pl.lit(year, dtype=pl.Int64).alias("source_year"),
        )
    )
    # Project to canonical column order + dtypes.
    return df.select(
        [
            pl.col(name).cast(dtype).alias(name)
            for name, dtype in CANONICAL_SCHEMA.items()
        ]
    )


# ── IO layer ──────────────────────────────────────────────────────────────────
def _resolve_eia_dir() -> Path:
    raw = config.get("phase5.eia_data_dir")
    if not raw:
        raise FileNotFoundError(
            "config phase5.eia_data_dir is not set — cannot locate EIA-860/923 data."
        )
    d = Path(raw)
    if not d.is_dir():
        raise FileNotFoundError(
            f"EIA data dir not mounted/found: {d}. Connect the external drive or "
            "override phase5.eia_data_dir in config/settings.yaml."
        )
    return d


def _latest_year(eia_dir: Path) -> int:
    """Newest year with BOTH an EIA860_<y> and EIA923_<y> folder present."""
    y860 = {
        int(m.group(1))
        for p in eia_dir.glob("EIA860_*")
        if (m := re.search(r"EIA860_(\d{4})", p.name))
    }
    y923 = {
        int(m.group(1))
        for p in eia_dir.glob("EIA923_*")
        if (m := re.search(r"EIA923_(\d{4})", p.name))
    }
    common = sorted(y860 & y923)
    if not common:
        raise FileNotFoundError(f"no matching EIA860_/EIA923_ year pair under {eia_dir}")
    return common[-1]


def _read_excel(path: Path, sheet: str, header_row: int) -> pl.DataFrame:
    """Read one EIA sheet (header_row is 0-based)."""
    return pl.read_excel(path, sheet_name=sheet, read_options={"header_row": header_row})


def _load_generators(eia_dir: Path, year: int) -> pl.DataFrame:
    path = next(eia_dir.glob(f"EIA860_{year}/3_1_Generator_Y{year}.xlsx"))
    raw = _read_excel(path, sheet="Operable", header_row=1)  # NB: "Operable", not sheet 0
    cols = raw.columns
    return raw.select(
        pl.col(_find_col(cols, "plant", "code")).cast(pl.Int64).alias("plant_code"),
        pl.col(_find_col(cols, "prime", "mover")).cast(pl.Utf8).str.strip_chars().alias("prime_mover"),
        pl.col(_find_col(cols, "nameplate", "capacity")).cast(pl.Float64, strict=False).alias("nameplate_mw"),
    )


def _load_plants(eia_dir: Path, year: int) -> pl.DataFrame:
    path = next(eia_dir.glob(f"EIA860_{year}/2___Plant_Y{year}.xlsx"))
    raw = _read_excel(path, sheet="Plant", header_row=1)
    cols = raw.columns
    return raw.select(
        pl.col(_find_col(cols, "plant", "code")).cast(pl.Int64).alias("plant_code"),
        pl.col(_find_col(cols, "plant", "name")).cast(pl.Utf8).alias("plant_name"),
        pl.col(_find_col(cols, "state")).cast(pl.Utf8).alias("state_code"),
        pl.col(_find_col(cols, "latitude")).cast(pl.Float64, strict=False).alias("latitude"),
        pl.col(_find_col(cols, "longitude")).cast(pl.Float64, strict=False).alias("longitude"),
    )


def _load_generation(eia_dir: Path, year: int) -> pl.DataFrame:
    path = next(eia_dir.glob(f"EIA923_{year}/EIA923_Schedules_2_3_4_5*{year}*.xlsx"))
    raw = _read_excel(path, sheet="Page 1 Generation and Fuel Data", header_row=5)
    cols = raw.columns
    return raw.select(
        pl.col(_find_col(cols, "plant", "id")).cast(pl.Int64).alias("plant_code"),
        pl.col(_find_col(cols, "reported", "prime", "mover")).cast(pl.Utf8).str.strip_chars().alias("prime_mover"),
        pl.col(_find_col(cols, "net generation", "megawatthours")).cast(pl.Float64, strict=False).alias("net_gen_mwh"),
    )


def ingest_eia_year(year: int | None = None) -> pl.DataFrame:
    """Load EIA-860 + EIA-923 for ``year`` (default: latest present) and return
    the canonical hydro ground-truth DataFrame. Reads the external drive."""
    eia_dir = _resolve_eia_dir()
    if year is None:
        year = config.get("phase5.eia_year") or _latest_year(eia_dir)
    log.info("Ingesting EIA hydro ground truth for year %d from %s", year, eia_dir)
    generators = _load_generators(eia_dir, year)
    plants = _load_plants(eia_dir, year)
    generation = _load_generation(eia_dir, year)
    return assemble_ground_truth(generators, generation, plants, year)


# ── Runner ─────────────────────────────────────────────────────────────────────
def _summary(df: pl.DataFrame) -> None:
    n = df.height
    log.info("EIA hydro ground-truth plants: %d", n)
    if n:
        cap = df["actual_installed_kw"]
        en = df["actual_annual_energy_kwh"]
        log.info("  installed_kw  range: %.0f – %.0f (median %.0f)", cap.min(), cap.max(), cap.median())
        log.info("  annual_kwh    range: %.3g – %.3g (median %.3g)", en.min(), en.max(), en.median())
        log.info("  total fleet GWh/yr: %.1f", en.sum() / 1e6)


def run(year: int | None = None) -> Path:
    df = ingest_eia_year(year)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    io.write_parquet(df, OUTPUT_PATH)
    _summary(df)
    log.info("Wrote %s", OUTPUT_PATH)
    return OUTPUT_PATH


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 5 — ingest EIA hydro ground truth.")
    ap.add_argument("--year", type=int, default=None, help="EIA data year (default: latest present)")
    args = ap.parse_args()
    run(args.year)


if __name__ == "__main__":
    main()
