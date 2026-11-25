#!/usr/bin/env python3
"""
Reverse-geocode photo GPS coordinates using Nominatim.

Usage:
    python3 scripts/reverse_geocode.py [--detail] [--db PATH] [--limit N] [--dry-run]

Two modes, each with its own table:

  (default)  geo_places         coordinates rounded to 3 decimals (~110 m cells), zoom 14.
                                Gives a city / neighbourhood level name.
  --detail   geo_places_detail  coordinates rounded to 5 decimals (~1 m), zoom 18.
                                Gives the nearest street, house number and named feature.

The script:
  1. Selects distinct GPS coordinates from exif at the mode's rounding
  2. Skips cells already present in the mode's table (idempotent / resumable)
  3. Calls Nominatim /reverse at no more than 1 request per second
  4. Stores one row per cell, keyed on (lat_r, lon_r)

Run it where the authoritative database lives (the Mac Studio), because
scripts/sync-from-studio.sh overwrites the local mediameta.db.

Note: --detail sends near-exact photo coordinates to the public Nominatim server.

Place data (c) OpenStreetMap contributors, ODbL. Nominatim usage policy:
https://operations.osmfoundation.org/policies/nominatim/

Environment:
    NOMINATIM_USER_AGENT   Override the User-Agent (default: photomanage-reverse-geocode/1.0)
"""

import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "mediameta.db"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = os.environ.get("NOMINATIM_USER_AGENT", "photomanage-reverse-geocode/1.0")
MIN_INTERVAL = 1.1  # seconds between requests; policy maximum is 1 req/s

# Keys in Nominatim's "address" object that describe a named feature at the point
# (a shop, restaurant, building, ...). The first one present is stored as feature_name.
FEATURE_KEYS = (
    "amenity", "shop", "tourism", "leisure", "building", "office", "historic",
    "man_made", "craft", "healthcare", "aeroway", "railway", "natural",
)

COARSE = {
    "table": "geo_places",
    "digits": 3,
    "zoom": 14,
    "schema": """
        CREATE TABLE IF NOT EXISTS geo_places (
            lat_r         REAL NOT NULL,
            lon_r         REAL NOT NULL,
            display_name  TEXT,
            neighbourhood TEXT,
            city          TEXT,
            county        TEXT,
            state         TEXT,
            country       TEXT,
            raw_json      TEXT,
            fetched_at    TEXT,
            PRIMARY KEY (lat_r, lon_r)
        )""",
}

DETAIL = {
    "table": "geo_places_detail",
    "digits": 5,
    "zoom": 18,
    "schema": """
        CREATE TABLE IF NOT EXISTS geo_places_detail (
            lat_r         REAL NOT NULL,
            lon_r         REAL NOT NULL,
            display_name  TEXT,
            feature_name  TEXT,
            house_number  TEXT,
            road          TEXT,
            neighbourhood TEXT,
            city          TEXT,
            postcode      TEXT,
            raw_json      TEXT,
            fetched_at    TEXT,
            PRIMARY KEY (lat_r, lon_r)
        )""",
}


def pending_sql(cfg):
    return """
        SELECT DISTINCT round(GPSLatitude, {d}) AS lat_r, round(GPSLongitude, {d}) AS lon_r
        FROM exif
        WHERE typeof(GPSLatitude) IN ('real', 'integer')
          AND typeof(GPSLongitude) IN ('real', 'integer')
          AND NOT (GPSLatitude = 0 AND GPSLongitude = 0)  -- 0,0 is a bogus "null island" fix
          AND NOT EXISTS (
              SELECT 1 FROM {t} g
              WHERE g.lat_r = round(exif.GPSLatitude, {d}) AND g.lon_r = round(exif.GPSLongitude, {d})
          )
        ORDER BY lat_r, lon_r
    """.format(d=cfg["digits"], t=cfg["table"])


def fetch(lat, lon, zoom):
    """Return the parsed Nominatim response, or None on a non-retryable failure."""
    params = urllib.parse.urlencode(
        {"format": "jsonv2", "zoom": zoom, "addressdetails": 1, "lat": lat, "lon": lon}
    )
    req = urllib.request.Request(f"{NOMINATIM_URL}?{params}", headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wait = 30 * (attempt + 1)
                print(f"  HTTP {e.code}; backing off {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"  HTTP {e.code} for {lat},{lon}; skipping", file=sys.stderr)
            return None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"  {e!r} for {lat},{lon}; retrying", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    return None


def _city(addr):
    return next(
        (addr[k] for k in ("city", "town", "village", "hamlet", "municipality") if addr.get(k)), None
    )


def _neighbourhood(addr):
    return addr.get("neighbourhood") or addr.get("suburb") or addr.get("quarter")


def parse_coarse(result):
    addr = result.get("address", {})
    return {
        "display_name": result.get("display_name"),
        "neighbourhood": _neighbourhood(addr),
        "city": _city(addr),
        "county": addr.get("county"),
        "state": addr.get("state"),
        "country": addr.get("country"),
    }


def parse_detail(result):
    addr = result.get("address", {})
    feature = next((addr[k] for k in FEATURE_KEYS if addr.get(k)), None)
    # For building-type features Nominatim often puts a type word ("yes", "house") in the
    # address key; only keep the feature when it is a real name.
    if feature and feature.lower() in {"yes", "house", "residential", "apartments", "detached", "terrace"}:
        feature = None
    return {
        "display_name": result.get("display_name"),
        "feature_name": feature or result.get("name") or None,
        "house_number": addr.get("house_number"),
        "road": addr.get("road"),
        "neighbourhood": _neighbourhood(addr),
        "city": _city(addr),
        "postcode": addr.get("postcode"),
    }


def store(conn, cfg, lat, lon, result, fields):
    cols = ["lat_r", "lon_r"] + list(fields) + ["raw_json", "fetched_at"]
    placeholders = ", ".join(["?"] * (len(cols) - 1)) + ", datetime('now')"
    conn.execute(
        f"INSERT OR REPLACE INTO {cfg['table']} ({', '.join(cols)}) VALUES ({placeholders})",
        [lat, lon] + list(fields.values()) + [json.dumps(result)],
    )
    conn.commit()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default=str(DB_PATH), help=f"Path to mediameta.db (default: {DB_PATH})")
    parser.add_argument("--detail", action="store_true",
                        help="Street-level mode: ~1 m cells, zoom 18, stored in geo_places_detail")
    parser.add_argument("--limit", type=int, help="Geocode at most N new locations")
    parser.add_argument("--dry-run", action="store_true", help="Show how many locations are pending, then exit")
    args = parser.parse_args()

    if not Path(args.db).is_file():
        print(f"Error: database not found: {args.db}", file=sys.stderr)
        sys.exit(1)

    cfg = DETAIL if args.detail else COARSE
    parse = parse_detail if args.detail else parse_coarse

    conn = sqlite3.connect(args.db, timeout=60)
    conn.execute(cfg["schema"])
    pending = conn.execute(pending_sql(cfg)).fetchall()
    if args.limit is not None:
        pending = pending[: args.limit]
    print(f"{len(pending)} location(s) to geocode into {cfg['table']} (zoom {cfg['zoom']})")
    if args.dry_run or not pending:
        return

    done = failed = 0
    last_request = 0.0
    try:
        for i, (lat, lon) in enumerate(pending, 1):
            wait = MIN_INTERVAL - (time.monotonic() - last_request)
            if wait > 0:
                time.sleep(wait)

            result = fetch(lat, lon, cfg["zoom"])
            # Stamp after fetch() returns so retries/backoff inside it count toward the
            # interval; the next request waits MIN_INTERVAL after the *final* attempt.
            last_request = time.monotonic()
            if result is None:
                failed += 1
                continue
            # An "error" response (e.g. "Unable to geocode", open ocean) is stored as an
            # empty row so we don't re-ask on every run.
            fields = parse({} if "error" in result else result)
            store(conn, cfg, lat, lon, result, fields)
            done += 1
            if i % 25 == 0 or i == len(pending):
                label = fields.get("road") or fields.get("city") or fields["display_name"]
                print(f"  {i}/{len(pending)} ({label})")
    except KeyboardInterrupt:
        print("\nInterrupted; progress is saved, re-run to resume.")

    print(f"Done: {done} stored, {failed} failed (re-run to retry failures)")


if __name__ == "__main__":
    main()
