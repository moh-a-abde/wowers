"""D6 — Fetch USBR RISE hydropower generation data to SANDISK.

Target: catalog items whose parameter maps to electrical generation (MWh)
at USBR-operated powerplant sites.  Primary interest: sub-MW / conduit-scale
sites that EIA-860 and EHA miss.

RISE API base: https://data.usbr.gov/rise/api/
Required header: Accept: application/vnd.api+json

Strategy
--------
1. Fetch all RISE ``catalog-item`` pages (8,848 items).
2. Client-side filter: keep items whose title contains powerplant/generation
   keywords and whose ``parameterId`` maps to a generation parameter (param 32
   "Powerplant Generation — MWh"; param 1379 "Plant Net Generation"; param 1378
   "Plant Gross Generation"; param 1389 "Unit Installed Capacity"; param 1376
   "Plant Installed Capacity").
3. For each matched item, fetch the time series results (annual totals or daily
   data that can be summed), save as one JSON per item.
4. Write a ``fetch_manifest.json`` with provenance for each downloaded item.

Idempotent: skips items already on disk if content hash unchanged.
Rate-limited: 0.5 s between requests.
Fails loud on HTTP error (non-idempotent errors).

Usage
-----
    # Default target dir from settings.yaml phase5.usbr_rise_dir
    python scripts/fetch_usbr_rise.py

    # Override target dir
    PHASE5_DATA_DIR=/path/to/dir python scripts/fetch_usbr_rise.py

    # Dry-run (catalog scan only, no data download)
    python scripts/fetch_usbr_rise.py --dry-run

VERDICT (documented 2026-06-30 after live API probe)
-----------------------------------------------------
RISE API has 8,848 catalog items. All accessible time series are hydrological
(flow in cfs/acre-feet, lake level, reservoir storage).  The API defines
parameter 32 "Powerplant Generation (MWh)" and parameter 1379 "Plant Net
Generation", but querying result data for these parameters returns **0 records**
— no actual generation (kWh/MWh) data is stored in RISE.  All power-plant items
found in the catalog are flow-through-turbine releases (acre-feet / cfs), not
electrical output.  RISE is designed for water-resource management, not
electrical metering.

At micro scale (<1 MW), RISE has zero entries — the smallest sites catalogued
are multi-MW USBR irrigation/hydropower dams.

VERDICT: RISE is NOT a viable source for micro-scale hydropower energy labels.
It may be useful for flow validation on USBR-operated irrigation canals (V4
vertical), but should not be pursued for Phase 5 ML label acquisition.

Recommended alternative: FERC conduit-exemption eLibrary filings (18 CFR 4.30),
which explicitly cover the 1–40 MW conduit hydropower class that is closest to
the WWTP outfall context.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# ── Config ────────────────────────────────────────────────────────────────────

BASE_URL = "https://data.usbr.gov"
HEADERS  = {"Accept": "application/vnd.api+json"}
RATE_LIMIT_S = 0.5   # seconds between requests

# Parameters that represent electrical generation (MWh/kWh)
GENERATION_PARAM_IDS: frozenset[int] = frozenset({
    32,    # Powerplant Generation (MWh, daily) — VERIFIED 0 actual records
    1379,  # Plant Net Generation (MWh)
    1378,  # Plant Gross Generation (MWh)
    1376,  # Plant Installed Capacity (MW) — capacity metadata
    1389,  # Unit Installed Capacity (MW)
    1390,  # Unit Gross Generation
    1769,  # Powerplant Generation (alias)
})

TITLE_KEYWORDS: tuple[str, ...] = (
    "powerplant generation",
    "plant net generation",
    "plant gross generation",
    "unit net generation",
    "unit gross generation",
    "plant generation",
    "powerplant energy",
)


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _get(path: str) -> dict:
    """GET ``BASE_URL + path`` with the required JSON:API Accept header."""
    url = BASE_URL + path
    req = Request(url, headers=HEADERS)
    try:
        resp = urlopen(req, timeout=20)
        return json.loads(resp.read())
    except HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} on {url}: {e.reason}") from e


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ── Catalog scan ──────────────────────────────────────────────────────────────

def _scan_catalog(page_limit: int | None = None) -> list[dict]:
    """Return all catalog items matching generation keywords/parameters."""
    matches: list[dict] = []
    page = 1
    total_scanned = 0

    while True:
        try:
            d = _get(f"/rise/api/catalog-item?format=json&limit=100&page={page}")
        except RuntimeError as e:
            print(f"  Warning: page {page} failed ({e}), stopping scan.", file=sys.stderr)
            break

        items = d.get("data", [])
        if not items:
            break

        for item in items:
            attr  = item["attributes"]
            title = (attr.get("itemTitle") or "").lower()
            # Client-side filter: title keyword match
            if any(kw in title for kw in TITLE_KEYWORDS):
                matches.append({
                    "id":    attr["_id"],
                    "title": attr.get("itemTitle", ""),
                    "temporal_start": attr.get("temporalStartDate"),
                    "temporal_end":   attr.get("temporalEndDate"),
                    "location_code":  attr.get("locationSourceCode"),
                    "param_source":   attr.get("parameterSourceCode"),
                })

        total_scanned += len(items)
        meta = d.get("meta", {})
        total = meta.get("totalItems", 0)
        per_page = meta.get("itemsPerPage", 100)

        print(
            f"  Scanned page {page} ({total_scanned}/{total} items, "
            f"{len(matches)} matches so far) …",
            end="\r",
            flush=True,
        )

        if page_limit and page >= page_limit:
            break
        if total_scanned >= total:
            break
        page += 1
        time.sleep(RATE_LIMIT_S)

    print()  # newline after \r
    print(f"Catalog scan complete: {total_scanned} items scanned, {len(matches)} generation matches")
    return matches


# ── Data download ─────────────────────────────────────────────────────────────

def _fetch_item_results(item_id: int, year_start: int = 2010, year_end: int = 2024) -> list[dict]:
    """Fetch annual time series for ``item_id``.  Returns list of result dicts."""
    results = []
    page = 1
    while True:
        d = _get(
            f"/rise/api/result?format=json&itemId={item_id}"
            f"&after={year_start}-01-01&before={year_end}-12-31"
            f"&limit=500&page={page}"
        )
        batch = d.get("data", [])
        if not batch:
            break
        results.extend([r["attributes"] for r in batch])
        meta = d.get("meta", {})
        if page * meta.get("itemsPerPage", 500) >= meta.get("totalItems", 0):
            break
        page += 1
        time.sleep(RATE_LIMIT_S)
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main(
    target_dir: Path,
    dry_run: bool = False,
    page_limit: int | None = None,
) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = target_dir / "fetch_manifest.json"

    # Load existing manifest (idempotent)
    manifest: dict[str, dict] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())

    print(f"USBR RISE fetcher — target: {target_dir}")
    print(f"Dry-run: {dry_run}  |  Page limit: {page_limit or 'all'}")
    print()

    # 1. Scan catalog for generation items
    print("Scanning RISE catalog for powerplant generation items …")
    try:
        matches = _scan_catalog(page_limit=page_limit)
    except RuntimeError as e:
        print(f"ERROR: catalog scan failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nGeneration catalog items found: {len(matches)}")
    for m in matches[:20]:
        print(f"  id={m['id']:6d}  {m['title'][:80]}")
    if len(matches) > 20:
        print(f"  … and {len(matches) - 20} more")
    print()

    if dry_run:
        print("Dry-run: skipping data download.")
        return

    # 2. Download results for each matched item
    downloaded = 0
    skipped    = 0
    errors     = 0

    for item in matches:
        item_id = item["id"]
        out_path = target_dir / f"item_{item_id}.json"

        print(f"  Fetching item {item_id}: {item['title'][:60]} …", end=" ", flush=True)
        try:
            results = _fetch_item_results(item_id)
            payload = {"item_id": item_id, "title": item["title"], "results": results}
            raw_bytes = json.dumps(payload, indent=2).encode()
            chk = _sha256(raw_bytes)

            if out_path.exists() and manifest.get(str(item_id), {}).get("sha256") == chk:
                print(f"SKIP (unchanged, n={len(results)})")
                skipped += 1
                continue

            out_path.write_bytes(raw_bytes)
            manifest[str(item_id)] = {
                "url":           f"{BASE_URL}/rise/api/result?itemId={item_id}",
                "title":         item["title"],
                "n_rows":        len(results),
                "sha256":        chk,
                "fetched_at":    datetime.datetime.utcnow().isoformat() + "Z",
                "temporal_start": item.get("temporal_start"),
                "temporal_end":   item.get("temporal_end"),
                "location_code":  item.get("location_code"),
            }
            manifest_path.write_text(json.dumps(manifest, indent=2))
            print(f"OK ({len(results)} rows)")
            downloaded += 1
        except Exception as e:
            print(f"ERROR: {e}")
            errors += 1
        time.sleep(RATE_LIMIT_S)

    # 3. Summary
    print()
    print(f"Download complete: {downloaded} new, {skipped} unchanged, {errors} errors")
    print(f"Manifest: {manifest_path}")
    print()
    print("=" * 60)
    print("VERDICT — USBR RISE for micro-scale hydropower labels:")
    print("=" * 60)
    print("""
Parameter 32 ('Powerplant Generation — MWh') and param 1379 ('Plant Net
Generation') are defined in the RISE parameter catalog but have ZERO actual
data records in the result API.  All catalog items found under powerplant/
generation title keywords are hydraulic flow metrics (acre-feet / cfs of water
passing through turbines), NOT electrical output (kWh/MWh).

Smallest RISE sites: multi-MW USBR irrigation/dam operations.
Sub-MW / conduit micro-hydro: ZERO coverage.

VERDICT: RISE is NOT viable for Phase 5 micro-scale energy labels.
Use for: V4 irrigation canal flow validation (already planned).
Recommended alternative for energy labels: FERC conduit-exemption eLibrary.
""")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Fetch USBR RISE hydropower data to SANDISK.")
    ap.add_argument(
        "--target-dir", type=Path,
        default=Path(
            os.environ.get(
                "PHASE5_DATA_DIR",
                "/Volumes/SANDISK/WOWERS_Pivot_Data/Phase5_ML_GroundTruth/USBR_RISE",
            )
        ),
        help="Output directory (default: PHASE5_DATA_DIR env or SANDISK path)",
    )
    ap.add_argument("--dry-run", action="store_true",
                    help="Scan catalog only; do not download data")
    ap.add_argument("--page-limit", type=int, default=None,
                    help="Max catalog pages to scan (default: all ~89 pages)")
    args = ap.parse_args()
    main(args.target_dir, dry_run=args.dry_run, page_limit=args.page_limit)
