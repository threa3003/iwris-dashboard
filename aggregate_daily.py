"""
aggregate_daily.py
--------------------
Collapses readings.jsonl (which has multiple sub-daily rows per station,
e.g. rainfall recorded every 3 hours) into ONE row per
(station_code, date, parameter):
  - rainfall_mm: SUMMED across the day (total rainfall that day)
  - groundwater_level_m: kept as-is (already ~daily in the source data,
    but if duplicates exist we average them)

This cuts row count roughly 6-8x for rainfall, which is most of the
dataset -- makes it fit free database tiers and is more useful for a
dashboard anyway (daily granularity is what you'd actually visualize).

Uses a dict accumulator streamed from disk -- watch memory while this
runs; if it climbs too high, let me know and we'll switch to a
sort-based external aggregation instead.
"""

import json
from pathlib import Path

IN_PATH = Path("output/readings.jsonl")
OUT_PATH = Path("output/readings_daily.jsonl")


def main():
    # key = (station_code, date, parameter) -> [sum, count]
    acc = {}

    print("Reading and aggregating...", flush=True)
    with open(IN_PATH, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            key = (r["station_code"], r["date"], r["parameter"])
            if key not in acc:
                acc[key] = [0.0, 0]
            acc[key][0] += r["value"]
            acc[key][1] += 1

            if i % 2_000_000 == 0:
                print(f"  ...read {i} lines, {len(acc)} unique keys so far", flush=True)

    print(f"\nFinished reading. {len(acc)} unique station/date/parameter combos.", flush=True)
    print("Writing aggregated output...", flush=True)

    with open(OUT_PATH, "w", encoding="utf-8") as out:
        for (station_code, date, parameter), (total, count) in acc.items():
            if parameter == "rainfall_mm":
                value = total  # sum for the day
            else:
                value = total / count  # average for groundwater (usually count=1 anyway)
            out.write(json.dumps({
                "station_code": station_code,
                "date": date,
                "parameter": parameter,
                "value": round(value, 3),
            }) + "\n")

    print(f"Done. Wrote {len(acc)} aggregated rows to {OUT_PATH}")
    print(f"(original had many more rows per station-day for rainfall; "
          f"this file should be substantially smaller)")


if __name__ == "__main__":
    main()
