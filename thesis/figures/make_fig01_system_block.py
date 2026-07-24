#!/usr/bin/env python3
"""Regenerate thesis/figures/fig01_system_block.png (WOWERS system block diagram)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).with_name("fig01_system_block.png")


def main() -> None:
    fig, ax = plt.subplots(figsize=(11.2, 6.6), dpi=220)
    ax.set_xlim(0, 112)
    ax.set_ylim(0, 66)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    def box(x, y, w, h, text, *, fc="#efefef", ec="#1a1a1a", lw=1.25, fs=7.6, dashed=False):
        style = (0, (2.5, 2)) if dashed else "solid"
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.12,rounding_size=0.35",
                facecolor=fc,
                edgecolor=ec,
                linewidth=lw,
                linestyle=style,
                zorder=2,
            )
        )
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=fs,
            family="sans-serif",
            color="#666" if dashed else "#111",
            linespacing=1.28,
            zorder=3,
        )

    def arr(x1, y1, x2, y2, *, dashed=False):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color="#222",
                lw=1.2,
                linestyle=(0, (3, 2)) if dashed else "solid",
                shrinkA=1.5,
                shrinkB=1.5,
            ),
            zorder=1,
        )

    ax.text(56, 63.5, "Public / agency inputs", ha="center", fontsize=9, color="#555", family="sans-serif")
    ax.text(
        46,
        43.6,
        "Offline Python screening pipeline (Phases 1–4)",
        ha="center",
        fontsize=9,
        color="#555",
        family="sans-serif",
    )
    ax.text(56, 16.2, "Export / serving / visualization", ha="center", fontsize=9, color="#555", family="sans-serif")

    sw, sh = 23, 9.5
    ys = 51
    box(4, ys, sw, sh, "EPA ECHO\nICIS facilities + permits", fc="#e6e6e6")
    box(31, ys, sw, sh, "EPA DMR param 50050\nFY2009–24 (~279M rows)", fc="#e6e6e6")
    box(58, ys, sw, sh, "USGS 3DEP EPQS\nelevations (DEM head)", fc="#e6e6e6")
    box(85, ys, sw, sh, "DOE EHA / EIA-860/923\nCF & generation labels", fc="#e6e6e6")

    pw, ph = 21, 11
    yp = 28.5
    fill = "#dcdcdc"
    box(3.5, yp, pw, ph, "Phase 1\nPOTW filter · FDC\nranking\n→ ranked_candidates", fc=fill)
    box(30.5, yp, pw, ph, "Phase 2\nMonte-Carlo energy\nP10 / P50 / P90\n→ energy_yield", fc=fill)
    box(57.5, yp, pw, ph, "Phase 3\n3DEP head proxy\nturbine match\n→ turbine_sizing", fc=fill)
    box(84.5, yp, pw, ph, "Phase 4\nCapEx · NPV · payback\necon gates\n→ scorecards", fc=fill)

    box(85, 40.2, 23, 7.3, "CF calibration\n119–281 GWh/yr band\n(side analysis)", fc="#fff")
    box(84.5, 17.8, 21, 7.0, "Phase 5 ML — killed\n(only 11 FERC labels)", fc="#fafafa", dashed=True, fs=7.2)

    bw, bh = 29, 9.5
    by = 3.8
    box(5, by, bw, bh, "export_geojson.py\n58-property contract\nbyte-deterministic", fc="#fff")
    box(41.5, by, bw, bh, "scored_sites.geojson\n(+ viable_sites.geojson)\n1,138 project-viable", fc="#fff")
    box(78, by, bw, bh, "React + MapLibre UI\n7 views · static build\nno live backend", fc="#fff")

    arr(4 + sw / 2, ys, 3.5 + pw * 0.35, yp + ph)
    arr(31 + sw / 2, ys, 3.5 + pw * 0.65, yp + ph)
    arr(58 + sw / 2, ys, 57.5 + pw / 2, yp + ph)
    arr(85 + sw / 2, ys, 85 + 23 / 2, 47.5)
    arr(85, 43.5, 51.5, yp + ph, dashed=True)

    arr(3.5 + pw, yp + ph / 2, 30.5, yp + ph / 2)
    arr(30.5 + pw, yp + ph / 2, 57.5, yp + ph / 2)
    arr(57.5 + pw, yp + ph / 2, 84.5, yp + ph / 2)

    arr(3.5 + pw / 2, yp, 5 + bw * 0.25, by + bh)
    arr(30.5 + pw / 2, yp, 5 + bw * 0.45, by + bh)
    arr(57.5 + pw / 2, yp, 5 + bw * 0.65, by + bh)
    arr(84.5 + pw / 2, yp, 5 + bw * 0.85, by + bh)

    arr(5 + bw, by + bh / 2, 41.5, by + bh / 2)
    arr(41.5 + bw, by + bh / 2, 78, by + bh / 2)

    ax.text(
        56,
        0.9,
        "Config: settings.yaml   ·   Intermediates: data/processed/phase{1–4}/*.parquet",
        ha="center",
        fontsize=6.8,
        color="#666",
        family="sans-serif",
    )

    fig.savefig(OUT, bbox_inches="tight", facecolor="white", pad_inches=0.18)
    plt.close()
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
