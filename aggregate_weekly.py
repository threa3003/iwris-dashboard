"""
aggregate_weekly.py
---------------------
Takes output/readings_daily.jsonl (already collapsed from sub-daily to
daily) and collapses it further into ONE row per
(station_code, week_start_date, parameter):
  - rainfall_mm: SUMMED across the week (total rainfall that week)
  - groundwater_level_m: AVERAGED across the week

week_start_date is the Monday of that ISO week, stored as a normal DATE
so the dashboard can still plot a real timeline, just at weekly
resolution instead of daily.
"""

import json
from datetime import date, timedelta
from pathlib import Path

IN_PATH = Path("output/readings_daily.jsonl")
OUT_PATH = Path("output/readings_weekly.jsonl")


def week_start(date_str):
    d = date.fromisoformat(date_str)
    monday = d - timedelta(days=d.weekday())
    return monday.isoformat()


def main():
    acc = {}  # (station_code, week_start, parameter) -> [sum, count]

    print("Reading and aggregating to weekly...", flush=True)
    with open(IN_PATH, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            wk = week_start(r["date"])
            key = (r["station_code"], wk, r["parameter"])
            if key not in acc:
                acc[key] = [0.0, 0]
            acc[key][0] += r["value"]
            acc[key][1] += 1

            if i % 1_000_000 == 0:
                print(f"  ...read {i} lines, {len(acc)} unique keys so far", flush=True)

    print(f"\nFinished reading. {len(acc)} unique station/week/parameter combos.", flush=True)
    print("Writing weekly output...", flush=True)

    with open(OUT_PATH, "w", encoding="utf-8") as out:
        for (station_code, wk, parameter), (total, count) in acc.items():
            if parameter == "rainfall_mm":
                value = total
            else:
                value = total / count
            out.write(json.dumps({
                "station_code": station_code,
                "date": wk,
                "parameter": parameter,
                "value": round(value, 3),
            }) + "\n")

    print(f"Done. Wrote {len(acc)} weekly rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
