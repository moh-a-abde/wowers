"""Capture the two live-app screenshots used in Section 4.6 (Frontend
Visualization System): the National Opportunity Map (fig_m1_nationalmap.png)
and a Plant Detail view (fig_m1_plantdetail.png).

Unlike the other thesis figures, these are not derived from a parquet/geojson
— they are real screenshots of the running dashboard, captured headlessly so
the exact pixels are reproducible rather than hand-taken. Requires the Vite
dev server running at localhost:5173 and Playwright with the Chromium
browser installed (`pip install playwright && playwright install chromium`).

Run from the repository root, with the dev server already up in a second
terminal (`cd frontend && npm run dev`):
    python3 thesis/figures/make_fig_m1_screenshots.py
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent
URL = "http://localhost:5173"
PLANT_ID = "OH0024732"  # Jackson Pike Water Resource Recovery Facility, Columbus OH


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 950}, device_scale_factor=2)

        page.goto(f"{URL}/", wait_until="networkidle")
        page.wait_for_timeout(2500)  # let MapLibre finish painting raster tiles
        page.screenshot(path=str(OUT / "fig_m1_nationalmap.png"))
        print("saved fig_m1_nationalmap.png")

        page.goto(f"{URL}/plant/{PLANT_ID}", wait_until="networkidle")
        page.wait_for_timeout(1500)
        page.screenshot(path=str(OUT / "fig_m1_plantdetail.png"))
        print(f"saved fig_m1_plantdetail.png (plant {PLANT_ID})")

        browser.close()


if __name__ == "__main__":
    main()
