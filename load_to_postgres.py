"""
load_to_postgres.py
---------------------
Loads output/stations.json and output/readings.jsonl into your Postgres
database (Neon, Vercel Postgres, or any Postgres). Uses COPY for the
readings table since it has ~44 million rows -- regular INSERT statements
would take hours; COPY handles this in a few minutes.

Before running:
  1. Run schema.sql against your database first (via Neon's SQL Editor
     or psql) to create the tables.
  2. Set your connection string below or via the DATABASE_URL env var.
  3. pip install psycopg2-binary
"""

import json
import os
import sys
from io import StringIO
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "PASTE_YOUR_NEON_CONNECTION_STRING_HERE"
)

STATIONS_PATH = Path("output/stations.json")
READINGS_PATH = Path("output/readings_weekly.jsonl")

STATION_COLUMNS = [
    "station_code", "station_name", "parameter", "state", "district",
    "tehsil", "block", "latitude", "longitude", "agency", "well_type",
    "aquifer_type", "well_depth", "data_status",
]


def clean_numeric(value):
    """Convert placeholder junk like '-', '', 'NA' into None so Postgres
    numeric columns don't choke on them."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return value
    s = str(value).strip()
    if s in ("-", "", "NA", "N/A", "NO DATA", "null", "None"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


NUMERIC_COLUMNS = {"latitude", "longitude", "well_depth"}


def load_stations(conn):
    print("Loading stations...")
    stations = json.loads(STATIONS_PATH.read_text())
    print(f"  {len(stations)} stations found in file")

    rows = []
    for s in stations:
        row = []
        for col in STATION_COLUMNS:
            val = s.get(col)
            if col in NUMERIC_COLUMNS:
                val = clean_numeric(val)
            row.append(val)
        rows.append(tuple(row))

    with conn.cursor() as cur:
        # ON CONFLICT so re-running this script is safe (upserts, no dupes)
        query = f"""
            INSERT INTO stations ({', '.join(STATION_COLUMNS)})
            VALUES %s
            ON CONFLICT (station_code) DO UPDATE SET
                station_name = EXCLUDED.station_name,
                parameter = EXCLUDED.parameter,
                state = EXCLUDED.state,
                district = EXCLUDED.district,
                tehsil = EXCLUDED.tehsil,
                block = EXCLUDED.block,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                agency = EXCLUDED.agency,
                well_type = EXCLUDED.well_type,
                aquifer_type = EXCLUDED.aquifer_type,
                well_depth = EXCLUDED.well_depth,
                data_status = EXCLUDED.data_status
        """
        execute_values(cur, query, rows, page_size=1000)
    conn.commit()
    print(f"  Inserted/updated {len(rows)} stations.\n")


def load_readings(conn):
    print("Loading readings (this is the big one, using COPY)...")

    BATCH_SIZE = 500_000
    total_loaded = 0
    batch = []

    def flush_batch(cur, batch):
        if not batch:
            return 0
        buf_lines = []
        for station_code, date, parameter, value in batch:
            buf_lines.append(f"{station_code}\t{date}\t{parameter}\t{value}")
        buf = "\n".join(buf_lines)
        cur.copy_expert(
            "COPY readings (station_code, date, parameter, value) FROM STDIN WITH (FORMAT text)",
            StringIO(buf)
        )
        return len(batch)

    with conn.cursor() as cur, open(READINGS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            batch.append((r["station_code"], r["date"], r["parameter"], r["value"]))

            if len(batch) >= BATCH_SIZE:
                total_loaded += flush_batch(cur, batch)
                conn.commit()
                print(f"  ...{total_loaded} readings loaded so far", flush=True)
                batch = []

        total_loaded += flush_batch(cur, batch)
        conn.commit()

    print(f"  Done. {total_loaded} total readings loaded.\n")


def main():
    if DATABASE_URL == "PASTE_YOUR_NEON_CONNECTION_STRING_HERE":
        print("ERROR: set DATABASE_URL env var or edit the script with your")
        print("Neon connection string before running.")
        sys.exit(1)

    conn = psycopg2.connect(DATABASE_URL)
    try:
        load_stations(conn)
        load_readings(conn)
    finally:
        conn.close()

    print("All done. Data is now in Postgres.")


if __name__ == "__main__":
    main()
