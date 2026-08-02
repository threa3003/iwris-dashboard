"""
repair_files_libreoffice.py
----------------------------
Repairs corrupted IWRIS .xlsx files by round-tripping each one through
LibreOffice headless (soffice --convert-to xlsx). This strips broken
drawing/image XML the same way Excel's "repair" dialog does, but:
  - runs one fresh process per file (no shared state to crash)
  - if one file hangs or fails, it doesn't take down the rest
  - works unattended, no GUI popups

Requires LibreOffice installed (get it from libreoffice.org).
Default install path on Windows is:
  C:\\Program Files\\LibreOffice\\program\\soffice.exe
Adjust SOFFICE_PATH below if yours differs.
"""

import subprocess
import shutil
from pathlib import Path

SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"
RAW_DIR = Path("data-raw")
# Only repair the specific large GW files that hung during processing —
# rainfall is already done, no need to touch those 600+ files again.
FILES_TO_REPAIR = [
    RAW_DIR / "groundwater" / "Andhra Pradesh.xlsx",
    RAW_DIR / "groundwater" / "Bihar.xlsx",
    RAW_DIR / "groundwater" / "Chhattisgarh.xlsx",
    RAW_DIR / "groundwater" / "Gujarat.xlsx",
    RAW_DIR / "groundwater" / "Haryana.xlsx",
    RAW_DIR / "groundwater" / "Kerala.xlsx",
    RAW_DIR / "groundwater" / "Madhya Pradesh.xlsx",
    RAW_DIR / "groundwater" / "Maharashtra.xlsx",
    RAW_DIR / "groundwater" / "Odisha.xlsx",
    RAW_DIR / "groundwater" / "Punjab.xlsx",
    RAW_DIR / "groundwater" / "Rajasthan.xlsx",
    RAW_DIR / "groundwater" / "Telangana.xlsx",
    RAW_DIR / "groundwater" / "Uttar Pradesh.xlsx",
    RAW_DIR / "groundwater" / "West Bengal.xlsx",
]
TIMEOUT_SECONDS = 300  # large state files need more time to convert than small rainfall files


def repair_file(path: Path):
    """
    Convert path -> temp folder as .xlsx (forces LibreOffice to re-serialize
    the file cleanly), then replace the original with the clean version.
    """
    out_dir = path.parent / "_repaired_tmp"
    out_dir.mkdir(exist_ok=True)

    cmd = [
        SOFFICE_PATH,
        "--headless",
        "--norestore",
        "--convert-to", "xlsx",
        "--outdir", str(out_dir),
        str(path.resolve()),
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=TIMEOUT_SECONDS
        )
    except subprocess.TimeoutExpired:
        return False, "timed out"

    converted = out_dir / path.name
    if not converted.exists():
        return False, result.stderr.strip()[:200] or "no output file produced"

    # replace original with the repaired version
    shutil.move(str(converted), str(path))
    return True, None


def main():
    all_files = [f for f in FILES_TO_REPAIR if f.exists()]
    missing = [f for f in FILES_TO_REPAIR if not f.exists()]
    if missing:
        print("WARNING: these files were not found (check filenames/paths):")
        for f in missing:
            print("  -", f)
        print()

    print(f"Found {len(all_files)} files to repair.\n")

    ok_count, fail_count = 0, 0
    failed_files = []
    for i, f in enumerate(all_files, 1):
        success, err = repair_file(f)
        if success:
            ok_count += 1
            print(f"[{i}/{len(all_files)}] OK: {f.relative_to(RAW_DIR)}")
        else:
            fail_count += 1
            failed_files.append(f)
            print(f"[{i}/{len(all_files)}] FAILED: {f.relative_to(RAW_DIR)} -> {err}")

    # cleanup temp folders
    for tmp in (RAW_DIR / "groundwater").rglob("_repaired_tmp"):
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nDone. Repaired {ok_count}, failed {fail_count}.")
    if failed_files:
        print("\nFiles that still need attention:")
        for f in failed_files:
            print(" -", f.relative_to(RAW_DIR))


if __name__ == "__main__":
    main()
