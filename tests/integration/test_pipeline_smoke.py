"""End-to-end smoke test for the Phase 1→4 pipeline.

Uses a tiny synthetic corpus of 8 facilities so the test runs in <30 s and
exercises every major transformation without hitting external APIs or large
data files.

Design decisions
----------------
* Phase 1 is tested via ``filter_potw`` directly (avoids disk I/O to ICIS CSVs).
* Phase 2 runs Monte Carlo with n_iterations=100 to keep wall-time low.
* Phase 3 wires synthetic elevation through ``estimate_head()`` (offline, deterministic).
* Phase 4 runs the full financial scorecard.

Key assertions
--------------
1. EPA 999 sentinel rows are nulled in Phase 1 output.
2. DMR/design 5× ratio cap nulls inflated actual_avg_flow_mgd.
3. Phase 2 excludes facilities whose flows were nulled by A1 (no_usable_flow).
4. Phase 2 emits head percentile columns (head_m_p10/p50/p90).
5. Phase 3 emits rated_power_kw (not p_rated_kw) in output schema.
6. Phase 4 payback sentinel is 1e6, not 999.
7. No negative or NaN energy for non-excluded facilities.
"""
from __future__ import annotations

import io
import math
from pathlib import Path
from unittest.mock import patch

import polars as pl
import pytest

# ── Synthetic POTW corpus ─────────────────────────────────────────────────────

# 8 facilities with varying flow / head / data quality profiles
_FACILITIES_CSV = """\
NPDES_ID,FACILITY_TYPE_CODE,FACILITY_NAME,CITY,STATE_CODE,ZIP,GEOCODE_LATITUDE,GEOCODE_LONGITUDE
TST000001,POT,Big Plant,Springfield,CA,90001,34.05,-118.25
TST000002,POT,Medium Plant,Shelbyville,TX,75001,32.78,-96.80
TST000003,POT,Small Plant,Capital City,OH,43201,39.96,-82.99
TST000004,POT,Sentinel Flow Plant,Anytown,FL,33101,25.77,-80.19
TST000005,POT,High Ratio Plant,Nowhere,WA,98001,47.60,-122.33
TST000006,POT,No Flow Plant,Emptyville,NY,10001,40.71,-74.01
TST000007,POT,Never Viable,Lossland,AK,99501,61.22,-149.90
TST000008,POT,Zero OpEx Plant,Coastal,CA,94101,37.77,-122.42
""".strip()

_PERMITS_CSV = """\
EXTERNAL_PERMIT_NMBR,FACILITY_TYPE_INDICATOR,TOTAL_DESIGN_FLOW_NMBR,ACTUAL_AVERAGE_FLOW_NMBR,MAJOR_MINOR_STATUS_FLAG,PERMIT_STATUS_CODE
TST000001,POTW,50.0,40.0,M,EFF
TST000002,POTW,5.0,3.5,m,EFF
TST000003,POTW,0.5,0.4,m,EFF
TST000004,POTW,999.0,999.0,M,EFF
TST000005,POTW,1.0,10.0,m,EFF
TST000006,POTW,2.0,,m,EFF
TST000007,POTW,0.1,0.05,m,EFF
TST000008,POTW,100.0,80.0,M,EFF
""".strip()


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def potw_df() -> pl.DataFrame:
    from src.phase1.filter_potw import load_potw_facilities
    fac_path = _write_tmp_csv(_FACILITIES_CSV, "facilities.csv")
    per_path = _write_tmp_csv(_PERMITS_CSV, "permits.csv")
    return load_potw_facilities(fac_path, per_path)


def _write_tmp_csv(content: str, name: str) -> Path:
    import tempfile
    p = Path(tempfile.gettempdir()) / f"wowers_smoke_{name}"
    p.write_text(content)
    return p


# ── Phase 1 tests ─────────────────────────────────────────────────────────────

class TestPhase1Smoke:
    def test_row_count(self, potw_df):
        # All 8 facilities have coordinates → 8 rows expected
        assert len(potw_df) == 8

    def test_sentinel_999_nulled(self, potw_df):
        """design_flow_mgd == 999.0 and actual_avg_flow_mgd == 999.0 must be null."""
        row = potw_df.filter(pl.col("npdes_id") == "TST000004")
        assert row["design_flow_mgd"][0] is None, "design_flow 999 not nulled"
        assert row["actual_avg_flow_mgd"][0] is None, "actual_avg_flow 999 not nulled"

    def test_dmr_ratio_cap_applied(self, potw_df):
        """actual_avg_flow > 5× design_flow must be nulled (TST000005: 10 > 5×1)."""
        row = potw_df.filter(pl.col("npdes_id") == "TST000005")
        # actual_avg_flow_mgd was 10.0, design was 1.0 → ratio = 10 → capped
        assert row["actual_avg_flow_mgd"][0] is None, "DMR ratio 10× not nulled"

    def test_normal_flows_preserved(self, potw_df):
        """Legitimate flows must pass through unchanged."""
        row = potw_df.filter(pl.col("npdes_id") == "TST000001")
        assert row["design_flow_mgd"][0] == pytest.approx(50.0)
        assert row["actual_avg_flow_mgd"][0] == pytest.approx(40.0)

    def test_schema_columns_present(self, potw_df):
        required = {"npdes_id", "design_flow_mgd", "actual_avg_flow_mgd",
                    "latitude", "longitude", "state_code", "major_minor"}
        assert required.issubset(set(potw_df.columns))


# ── Phase 2 tests ─────────────────────────────────────────────────────────────

def _make_phase2_input(potw_df: pl.DataFrame) -> pl.DataFrame:
    """Build a minimal ranked_candidates DataFrame for Phase 2.

    Preserves nulls from Phase 1 (e.g. sentinel-nulled flows) so that
    Phase 2 exclusion logic (no_usable_flow) is exercised end-to-end.
    """
    rows = []
    for i, r in enumerate(potw_df.iter_rows(named=True)):
        design_flow = r.get("design_flow_mgd")   # may be None (sentinel-nulled)
        actual_flow = r.get("actual_avg_flow_mgd")  # may be None
        # Derive mean_flow without inventing values for sentinel-nulled rows.
        if actual_flow is not None and actual_flow > 0:
            mean_flow = actual_flow
        elif design_flow is not None and design_flow > 0:
            mean_flow = design_flow * 0.75
        else:
            mean_flow = None  # Phase 2 will mark excluded=True (no_usable_flow)
        rows.append({
            "npdes_id":            r["npdes_id"],
            "facility_name":       r.get("facility_name", ""),
            "state_code":          r.get("state_code", "CA"),
            "latitude":            r.get("latitude", 34.0),
            "longitude":           r.get("longitude", -118.0),
            "design_flow_mgd":     design_flow,
            "actual_avg_flow_mgd": actual_flow,
            "mean_flow_mgd":       mean_flow,
            "flow_duration_curve": None,
            "ranking_score":       float(i) / 10.0,
            "rank":                i + 1,
        })
    return pl.DataFrame(rows)


@pytest.fixture(scope="module")
def phase2_df(potw_df) -> pl.DataFrame:
    from src.phase2.monte_carlo import estimate_all_facilities

    input_df = _make_phase2_input(potw_df)
    return estimate_all_facilities(input_df, n_iterations=200, seed=42)


class TestPhase2Smoke:
    def test_head_percentile_columns_present(self, phase2_df):
        for col in ("head_m_p10", "head_m_p50", "head_m_p90"):
            assert col in phase2_df.columns, f"Missing column: {col}"

    def test_no_negative_energy(self, phase2_df):
        non_excluded = phase2_df.filter(pl.col("excluded").is_null() | (~pl.col("excluded")))
        energies = non_excluded["energy_p50_kwh_yr"].drop_nulls()
        assert (energies >= 0).all(), "Negative energy values found"

    def test_sentinel_nulled_facility_excluded(self, phase2_df):
        """TST000004 had both flows sentinel-nulled (999→null) → mean_flow=null → excluded."""
        row = phase2_df.filter(pl.col("npdes_id") == "TST000004")
        assert len(row) == 1, "TST000004 must appear in Phase 2 output (even if excluded)"
        assert row["excluded"][0] is True, \
            "TST000004 should be excluded (sentinel-nulled flows → no_usable_flow)"

    def test_head_ordering(self, phase2_df):
        """For non-excluded rows, p10 ≤ p50 ≤ p90."""
        valid = phase2_df.filter(
            pl.col("excluded").is_null() | (~pl.col("excluded"))
        ).drop_nulls(subset=["head_m_p10", "head_m_p50", "head_m_p90"])
        for row in valid.iter_rows(named=True):
            assert row["head_m_p10"] <= row["head_m_p50"] + 1e-9
            assert row["head_m_p50"] <= row["head_m_p90"] + 1e-9


# ── Phase 3 tests ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def phase3_df(phase2_df, potw_df) -> pl.DataFrame:
    """Exercise estimate_head() then select_and_size_turbines().

    Uses synthetic elevation values (abs(lat) * 2.5 m) so the test is
    offline and deterministic while still calling the real head estimation
    code path.
    """
    from src.phase3 import turbine_selection, head_estimation

    non_excluded = phase2_df.filter(
        pl.col("excluded").is_null() | (~pl.col("excluded"))
    )
    if len(non_excluded) == 0:
        return pl.DataFrame()

    # Build elevation input expected by estimate_head():
    # join Phase 2 output with a synthetic elevation_m column.
    rows = []
    for row in non_excluded.iter_rows(named=True):
        p1_row = potw_df.filter(pl.col("npdes_id") == row["npdes_id"])
        lat = p1_row["latitude"][0] if len(p1_row) else 34.0
        lon = p1_row["longitude"][0] if len(p1_row) else -118.0
        mean_flow = (
            (p1_row["actual_avg_flow_mgd"][0] if len(p1_row) else None)
            or (p1_row["design_flow_mgd"][0] if len(p1_row) else None)
            or 1.0
        )
        rows.append({
            "npdes_id":      row["npdes_id"],
            "mean_flow_mgd": float(mean_flow),
            "elevation_m":   abs(float(lat)) * 2.5,   # synthetic elevation
            "head_m_p50":    row.get("head_m_p50"),
        })

    elev_df = pl.DataFrame(rows)
    head_df = head_estimation.estimate_head(elev_df)

    # Merge mean_flow_mgd back (estimate_head only adds head columns)
    head_df = head_df.join(
        elev_df.select(["npdes_id", "mean_flow_mgd"]),
        on="npdes_id",
        how="left",
    )

    return turbine_selection.select_and_size_turbines(head_df)


class TestPhase3Smoke:
    def test_rated_power_kw_not_p_rated_kw(self, phase3_df):
        """Column must be rated_power_kw, not p_rated_kw."""
        assert "rated_power_kw" in phase3_df.columns, "rated_power_kw column missing"
        assert "p_rated_kw" not in phase3_df.columns, "deprecated p_rated_kw still present"

    def test_positive_power_for_viable(self, phase3_df):
        viable = phase3_df.filter(pl.col("turbine_viable") == True)  # noqa: E712
        if len(viable) == 0:
            pytest.skip("No viable turbines in synthetic corpus")
        powers = viable["rated_power_kw"].drop_nulls()
        assert (powers > 0).all()

    def test_no_unknown_turbine_types(self, phase3_df):
        valid_types = {"Pelton", "Francis", "Kaplan", "in_conduit_micro"}
        types = set(phase3_df["turbine_type"].drop_nulls().to_list())
        assert types.issubset(valid_types), f"Unknown turbine types: {types - valid_types}"


# ── Phase 4 tests ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def phase4_df(phase3_df) -> pl.DataFrame:
    from src.phase4.financials import compute_scorecard
    from src.phase4.cost_models import total_capex, annual_opex
    from src.phase4.revenue import annual_revenue, electricity_rate

    viable = phase3_df.filter(
        (pl.col("turbine_viable") == True)  # noqa: E712
        & pl.col("rated_power_kw").is_not_null()
        & (pl.col("rated_power_kw") > 0)
    )
    if len(viable) == 0:
        return pl.DataFrame()

    rows = []
    for r in viable.iter_rows(named=True):
        t_type   = r.get("turbine_type", "Kaplan")
        rated_kw = float(r["rated_power_kw"])
        energy_kwh = float(r.get("annual_energy_mwh") or 0) * 1000
        if energy_kwh <= 0:
            continue
        cap_usd  = total_capex(t_type, rated_kw)
        opex_usd = annual_opex(t_type, cap_usd)
        rev_usd  = annual_revenue(energy_kwh, "CA")
        elec     = electricity_rate("CA")
        sc       = compute_scorecard(
            annual_energy_kwh=energy_kwh,
            elec_rate_per_kwh=elec,
            annual_opex_usd=opex_usd,
            total_capex_usd=cap_usd,
            annual_revenue_usd=rev_usd,
        )
        rows.append({"npdes_id": r["npdes_id"], **sc})

    return pl.DataFrame(rows) if rows else pl.DataFrame()


class TestPhase4Smoke:
    def test_inf_sentinel_is_1e6(self, phase4_df):
        """Payback/LCOE sentinel must be 1e6, not 999.0."""
        from src.phase4.financials import _INF_SENTINEL
        assert _INF_SENTINEL == 1e6, f"Sentinel is {_INF_SENTINEL}, expected 1e6"

    def test_non_viable_payback_is_1e6_not_999(self):
        """Forcing zero-revenue through compute_scorecard must yield payback == 1e6."""
        from src.phase4.financials import compute_scorecard, _INF_SENTINEL
        sc = compute_scorecard(
            annual_energy_kwh=0.0,
            elec_rate_per_kwh=0.10,
            annual_opex_usd=50_000.0,
            total_capex_usd=1_000_000.0,
            annual_revenue_usd=0.0,
        )
        assert sc["payback_years"] == _INF_SENTINEL, \
            f"Expected {_INF_SENTINEL}, got {sc['payback_years']} — sentinel migration broken"
        assert sc["payback_years"] != 999.0, "Old 999 sentinel still in use"

    def test_viable_sites_positive_npv(self, phase4_df):
        if len(phase4_df) == 0:
            pytest.skip("No scored facilities")
        viable = phase4_df.filter(pl.col("project_viable") == True)  # noqa: E712
        if len(viable) == 0:
            return
        assert (viable["npv_usd"] > 0).all()

    def test_payback_finite_for_viable(self, phase4_df):
        if len(phase4_df) == 0:
            pytest.skip("No scored facilities")
        viable = phase4_df.filter(pl.col("project_viable") == True)  # noqa: E712
        if len(viable) == 0:
            return
        assert (viable["payback_years"] < 1e6).all()
