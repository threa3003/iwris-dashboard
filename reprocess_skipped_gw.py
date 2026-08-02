"""
reprocess_skipped_gw.py (v2 - no multiprocessing)
----------------------------------------------------
The earlier version wrapped each file in a subprocess with a timeout to
guard against hangs. Diagnostics proved these files actually parse in
under a second each -- the "hang" was a deadlock in the multiprocessing
Queue itself (classic Windows pitfall: child blocks on queue.put() when
the pipe fills before the parent reads it). Removing that wrapper entirely
fixes it, since there's no real hang risk left to guard against.
"""

import json
from pathlib import Path

from process_data import process_groundwater_file, stations

OUT_DIR = Path("output")
READINGS_PATH = OUT_DIR / "readings.jsonl"
STATIONS_PATH = OUT_DIR / "stations.json"

SKIPPED_FILES = [
    r"data-raw\groundwater\Andhra Pradesh.xlsx",
    r"data-raw\groundwater\Bihar.xlsx",
    r"data-raw\groundwater\Chhattisgarh.xlsx",
    r"data-raw\groundwater\Gujarat.xlsx",
    r"data-raw\groundwater\Haryana.xlsx",
    r"data-raw\groundwater\Kerala.xlsx",
    r"data-raw\groundwater\Madhya Pradesh.xlsx",
    r"data-raw\groundwater\Maharashtra.xlsx",
    r"data-raw\groundwater\Odisha.xlsx",
    r"data-raw\groundwater\Punjab.xlsx",
    r"data-raw\groundwater\Rajasthan.xlsx",
    r"data-raw\groundwater\Telangana.xlsx",
    r"data-raw\groundwater\Uttar Pradesh.xlsx",
    r"data-raw\groundwater\West Bengal.xlsx",
]


def main():
    existing_stations = {}
    if STATIONS_PATH.exists():
        for s in json.loads(STATIONS_PATH.read_text()):
            existing_stations[s["station_code"]] = s
    print(f"Loaded {len(existing_stations)} existing stations.\n")

    still_failed = []
    with open(READINGS_PATH, "a", encoding="utf-8") as readings_file:
        for i, path_str in enumerate(SKIPPED_FILES, 1):
            path = Path(path_str)
            if not path.exists():
                print(f"[{i}/{len(SKIPPED_FILES)}] MISSING FILE: {path_str}")
                still_failed.append(path_str)
                continue

            print(f"[{i}/{len(SKIPPED_FILES)}] processing: {path.name}", flush=True)
            try:
                process_groundwater_file(path, readings_file)
                readings_file.flush()
                print(f"    OK: {path.name} ({len(stations)} station entries so far)", flush=True)
            except Exception as e:
                print(f"    !! FAILED: {path.name} -> {e}", flush=True)
                still_failed.append(path_str)

    existing_stations.update(stations)
    STATIONS_PATH.write_text(
        json.dumps(list(existing_stations.values()), indent=2, default=str)
    )

    total_readings = sum(1 for _ in open(READINGS_PATH, encoding="utf-8"))
    print(f"\nDone. {len(existing_stations)} total stations, "
          f"{total_readings} total readings in readings.jsonl.")

    if still_failed:
        print(f"\n{len(still_failed)} files still failed:")
        for f in still_failed:
            print(" -", f)


if __name__ == "__main__":
    main()
