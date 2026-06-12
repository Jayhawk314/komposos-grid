# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Download EIA-930 six-month bulk files (keyless).

    python -m domains.grid.fetch_eia930 --year 2025
    python -m domains.grid.fetch_eia930 --year 2025 --kind BALANCE

Files land in domains/grid/data/ with EIA's own names, e.g.
EIA930_INTERCHANGE_2025_Jan_Jun.csv (~100 MB each). Existing complete
files are kept; partial downloads resume via HTTP Range.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles"
DEFAULT_DATA_DIR = Path("domains/grid/data")
HALVES = ("Jan_Jun", "Jul_Dec")
CHUNK = 1 << 20  # 1 MiB


def fetch_year(
    year: int,
    kind: str = "INTERCHANGE",
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> list[Path]:
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for half in HALVES:
        name = f"EIA930_{kind}_{year}_{half}.csv"
        paths.append(_fetch_file(f"{BASE_URL}/{name}", data_dir / name))
    return paths


def _remote_size(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return int(resp.headers.get("Content-Length", 0))


def _fetch_file(url: str, dest: Path) -> Path:
    total = _remote_size(url)
    have = dest.stat().st_size if dest.exists() else 0
    if total and have == total:
        print(f"{dest.name}: complete ({have:,} bytes)")
        return dest
    headers = {}
    mode = "wb"
    if 0 < have < total:
        headers["Range"] = f"bytes={have}-"
        mode = "ab"
        print(f"{dest.name}: resuming at {have:,}/{total:,}")
    else:
        print(f"{dest.name}: downloading {total:,} bytes")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp, \
                dest.open(mode) as out:
            while True:
                chunk = resp.read(CHUNK)
                if not chunk:
                    break
                out.write(chunk)
    except urllib.error.HTTPError as err:
        if err.code == 416:  # range not satisfiable: already complete
            return dest
        raise
    print(f"{dest.name}: done ({dest.stat().st_size:,} bytes)")
    return dest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Fetch EIA-930 bulk files")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--kind", default="INTERCHANGE",
                        choices=["INTERCHANGE", "BALANCE", "SUBREGION"])
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    args = parser.parse_args(argv)
    fetch_year(args.year, args.kind, args.data_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
