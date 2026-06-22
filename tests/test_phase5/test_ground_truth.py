"""Phase 5 ground-truth ingest — unit tests on synthetic frames.

No external drive or Excel engine required: every test feeds standardized
in-memory polars frames to the pure transforms. One optional integration test
reads the real EIA file and skips when the drive/engine is absent.
"""

from __future__ import annotations

import math

import polars as pl
import pytest

from src.phase5 import ground_truth as gt


# ── Fixtures: standardized frames as produced by the IO layer ─────────────────
def _generators() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "plant_code": [1, 1, 2, 3, 4],
            "prime_mover": ["HY", "HY", "HY", "PS", "ST"],  # plant1 has 2 hydro gens
            "nameplate_mw": [10.0, 5.0, 2.0, 50.0, 100.0],
        }
    )


def _generation() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "plant_code": [1, 2, 3, 4, 1],
            "prime_mover": ["HY", "HY", "PS", "ST", "HY"],  # plant1 hydro on 2 rows
            "net_gen_mwh": [40_000.0, 8_000.0, -500.0, 250_000.0, 5_000.0],
        }
    )


def _plants() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "plant_code": [1, 2, 3, 4],
            "plant_name": ["Alpha Dam", "Beta Conduit", "Gamma PS", "Delta Coal"],
            "state_code": ["CA", "CO", "WA", "TX"],
            "latitude": [38.1, 39.2, 47.3, 31.4],
            "longitude": [-120.1, -105.2, -121.3, -97.4],
        }
    )


# ── prime-mover filter + capacity aggregation ─────────────────────────────────
class TestAggregateCapacity:
    def test_keeps_only_hydro_and_sums_to_plant_kw(self):
        out = gt.aggregate_capacity_kw(_generators()).sort("plant_code")
        # PS (plant3) and ST (plant4) dropped; plant1 = (10+5)*1000.
        assert out["plant_code"].to_list() == [1, 2]
        cap = dict(zip(out["plant_code"], out["actual_installed_kw"]))
        assert cap[1] == pytest.approx(15_000.0)
        assert cap[2] == pytest.approx(2_000.0)

    def test_pumped_storage_excluded(self):
        df = pl.DataFrame({"plant_code": [9], "prime_mover": ["PS"], "nameplate_mw": [30.0]})
        assert gt.aggregate_capacity_kw(df).height == 0


# ── generation aggregation ────────────────────────────────────────────────────
class TestAggregateGeneration:
    def test_keeps_only_hydro_and_sums_to_plant_kwh(self):
        out = gt.aggregate_generation_kwh(_generation()).sort("plant_code")
        assert out["plant_code"].to_list() == [1, 2]
        en = dict(zip(out["plant_code"], out["actual_annual_energy_kwh"]))
        assert en[1] == pytest.approx((40_000.0 + 5_000.0) * 1_000.0)  # two hydro rows
        assert en[2] == pytest.approx(8_000.0 * 1_000.0)

    def test_mwh_to_kwh_conversion(self):
        df = pl.DataFrame({"plant_code": [1], "prime_mover": ["HY"], "net_gen_mwh": [1.0]})
        out = gt.aggregate_generation_kwh(df)
        assert out["actual_annual_energy_kwh"][0] == pytest.approx(1_000.0)


# ── full assemble ─────────────────────────────────────────────────────────────
class TestAssemble:
    def test_schema_columns_and_dtypes(self):
        out = gt.assemble_ground_truth(_generators(), _generation(), _plants(), year=2019)
        assert out.columns == list(gt.CANONICAL_SCHEMA.keys())
        assert dict(out.schema) == dict(gt.CANONICAL_SCHEMA)

    def test_only_hydro_plants_with_both_labels_survive(self):
        out = gt.assemble_ground_truth(_generators(), _generation(), _plants(), year=2019).sort(
            "source_plant_code"
        )
        # Only plants 1 & 2 have both hydro capacity and hydro generation.
        assert out["source_plant_code"].to_list() == [1, 2]

    def test_label_values_and_metadata(self):
        out = gt.assemble_ground_truth(_generators(), _generation(), _plants(), year=2019).sort(
            "source_plant_code"
        )
        r0 = out.row(0, named=True)
        assert r0["actual_installed_kw"] == pytest.approx(15_000.0)
        assert r0["actual_annual_energy_kwh"] == pytest.approx(45_000_000.0)
        assert r0["ground_truth_source"] == "EIA"
        assert r0["facility_name"] == "Alpha Dam"
        assert r0["state_code"] == "CA"
        assert r0["latitude"] == pytest.approx(38.1)
        assert r0["source_year"] == 2019
        # EIA never reports head/flow.
        assert r0["actual_head_m"] is None
        assert r0["actual_flow_m3s"] is None

    def test_capacity_without_generation_dropped(self):
        # plant 5 has hydro capacity but no generation row → inner join drops it.
        gens = pl.DataFrame(
            {"plant_code": [5], "prime_mover": ["HY"], "nameplate_mw": [3.0]}
        )
        gens_no = pl.DataFrame(
            {"plant_code": [99], "prime_mover": ["HY"], "net_gen_mwh": [1.0]}
        )
        plants = pl.DataFrame(
            {
                "plant_code": [5],
                "plant_name": ["Orphan"],
                "state_code": ["NV"],
                "latitude": [1.0],
                "longitude": [2.0],
            }
        )
        out = gt.assemble_ground_truth(gens, gens_no, plants, year=2019)
        assert out.height == 0

    def test_zero_and_negative_labels_dropped(self):
        gens = pl.DataFrame(
            {"plant_code": [1, 2], "prime_mover": ["HY", "HY"], "nameplate_mw": [0.0, 5.0]}
        )
        gen = pl.DataFrame(
            {"plant_code": [1, 2], "prime_mover": ["HY", "HY"], "net_gen_mwh": [100.0, -10.0]}
        )
        plants = pl.DataFrame(
            {
                "plant_code": [1, 2],
                "plant_name": ["Z", "N"],
                "state_code": ["CA", "CA"],
                "latitude": [1.0, 2.0],
                "longitude": [1.0, 2.0],
            }
        )
        # plant1 zero capacity, plant2 negative generation → both dropped.
        out = gt.assemble_ground_truth(gens, gen, plants, year=2019)
        assert out.height == 0


# ── column-name matcher ───────────────────────────────────────────────────────
class TestFindCol:
    def test_matches_all_substrings_case_insensitive(self):
        cols = ["Plant Code", "Nameplate Capacity (MW)", "Reported\nPrime Mover"]
        assert gt._find_col(cols, "nameplate", "capacity") == "Nameplate Capacity (MW)"
        assert gt._find_col(cols, "prime", "mover") == "Reported\nPrime Mover"

    def test_raises_when_absent(self):
        with pytest.raises(KeyError):
            gt._find_col(["A", "B"], "nonexistent")


# ── optional real-file integration (skips without drive/engine) ───────────────
def _eia_available() -> bool:
    try:
        import fastexcel  # noqa: F401
    except ImportError:
        return False
    try:
        return gt._resolve_eia_dir().is_dir()
    except FileNotFoundError:
        return False


@pytest.mark.skipif(not _eia_available(), reason="EIA drive or fastexcel engine not available")
def test_integration_real_eia_ingest():
    df = gt.ingest_eia_year()
    assert df.columns == list(gt.CANONICAL_SCHEMA.keys())
    assert df.height > 0
    assert (df["actual_installed_kw"] > 0).all()
    assert (df["actual_annual_energy_kwh"] > 0).all()
