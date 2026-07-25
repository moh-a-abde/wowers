"""Render Figure 8 — the capacity-factor calibration band on portfolio energy.

Each bar is the 1,138-site portfolio energy after substituting a capacity factor
for the Phase 2 implied median of 0.8725. Multipliers are CF / 0.8725, so the
top bar is the unmodified physics estimate. Markers show the same tiers computed
from the narrower 0.1-1 MW EHA bucket.

Requires the EHA workbook on SANDISK (same default path as scripts/cf_calibration.py).

Run from the repository root:
    PYTHONPATH=. python3 thesis/figures/make_fig08_calibration_band.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "fig08_calibration_band.png"

sys.path.insert(0, str(ROOT / "scripts"))
from cf_calibration import (  # noqa: E402
    _DEFAULT_EHA_DIR,
    _load_eha_cf,
    bucket_stats,
    calibration_band,
    phase2_viable_cf_stats,
    WWTP_CENTRAL_CF,
)

INK = "#1f2933"
FLOOR_C = "#c1553b"
CENTRAL_C = "#3f7d4f"
CEILING_C = "#4a7fb5"
SUB_C = "#6b7280"

LABELS = [
    "Floor, river-hydro p25",
    "Floor, river-hydro p50",
    "Floor, river-hydro p75",
    "Central, WWTP-appropriate",
    "Physics ceiling, Phase 2",
]


def main() -> None:
    cf_df = _load_eha_cf(_DEFAULT_EHA_DIR)
    b5 = bucket_stats(cf_df, max_mw=5.0)
    b1 = bucket_stats(cf_df, max_mw=1.0)

    p2 = pl.read_parquet(ROOT / "data/processed/phase2/energy_yield_estimates.parquet")
    p4 = pl.read_parquet(ROOT / "data/processed/phase4/financial_scorecards.parquet")
    stats = phase2_viable_cf_stats(p2, p4)

    band5 = calibration_band(stats["headline_gwh"], stats["cf_p50"], b5, WWTP_CENTRAL_CF)
    band1 = calibration_band(stats["headline_gwh"], stats["cf_p50"], b1, WWTP_CENTRAL_CF)

    plt.rcParams.update({"font.size": 11, "axes.labelsize": 11, "axes.titlesize": 11})
    fig, ax = plt.subplots(figsize=(9.0, 3.4))

    ypos = np.arange(len(band5))[::-1]
    colours = [FLOOR_C, FLOOR_C, FLOOR_C, CENTRAL_C, CEILING_C]
    for y, row, colour in zip(ypos, band5, colours):
        ax.barh(y, row["gwh"], color=colour, height=0.58, alpha=0.9)
        ax.text(row["gwh"] + 6, y, f"{row['gwh']:,.1f} GWh/yr", fontsize=9,
                color=INK, va="center")
        ax.text(6, y, f"CF {row['cf']:.3f}  ($\\times${row['multiplier']:.3f})",
                fontsize=8.5, color="white", va="center")

    for y, row in zip(ypos[:3], band1[:3]):
        ax.plot([row["gwh"]], [y - 0.36], marker="d", color=SUB_C, markersize=6)
    ax.plot([], [], marker="d", color=SUB_C, linestyle="none", markersize=6,
            label=f"same tier from the 0.1--1 MW bucket ({b1['n_plants']} plants)")

    ax.set_yticks(ypos)
    ax.set_yticklabels(LABELS, fontsize=9)
    ax.set_xlim(0, 470)
    ax.set_xlabel("Portfolio energy across the 1,138 project-viable sites (GWh/yr)")
    ax.legend(fontsize=8, frameon=False, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=9, colors=INK)

    fig.tight_layout()
    fig.savefig(OUT, dpi=200)

    print(f"wrote {OUT}")
    print(f"headline {stats['headline_gwh']} GWh/yr from {stats['n_viable_sites']} sites, "
          f"implied CF median {stats['cf_p50']}")
    print(f"0.1-5 MW bucket: {b5['n_plants']} plants / {b5['n_plant_years']:,} plant-years")
    print(f"0.1-1 MW bucket: {b1['n_plants']} plants / {b1['n_plant_years']:,} plant-years")
    for row5, row1 in zip(band5, band1):
        print(f"  {row5['tier']:28s} 0.1-5MW cf={row5['cf']:.4f} x{row5['multiplier']:.3f} "
              f"= {row5['gwh']:7.1f} GWh | 0.1-1MW cf={row1['cf']:.4f} x{row1['multiplier']:.3f} "
              f"= {row1['gwh']:7.1f} GWh")


if __name__ == "__main__":
    main()
