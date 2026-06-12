# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Pull MISO DA ex-post LMPs and produce eastern-seam evidence rows.

    python -m domains.grid.run_miso_seam_evidence ^
        --out reports\\miso_seam_evidence.csv

Defaults to full-year 2023 for the MISO-SOCO (MS.HUB vs SOCO interface)
and MISO-SWPP (ARKANSAS.HUB vs SWPP interface) seams. Output rows are
compatible with run_congestion_evidence --evidence-csv.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date

from domains.grid.sources.miso import fetch_nodes_range, seam_spread

# (ba_a, ba_b, interface node, reference hub)
DEFAULT_SEAMS = [
    ("MISO", "SOCO", "SOCO", "MS.HUB"),
    ("MISO", "SWPP", "SWPP", "ARKANSAS.HUB"),
]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="MISO eastern seam evidence")
    parser.add_argument("--cache", default=r"domains\grid\data\miso\cache")
    parser.add_argument("--start", default="2023-01-01")
    parser.add_argument("--end", default="2024-01-01")
    parser.add_argument("--out", help="write evidence CSV rows to this path")
    args = parser.parse_args(argv)

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    nodes = sorted({n for _, _, iface, hub in DEFAULT_SEAMS for n in (iface, hub)})
    long_df = fetch_nodes_range(nodes, start, end, args.cache)

    rows = []
    for ba_a, ba_b, iface, hub in DEFAULT_SEAMS:
        result = seam_spread(long_df, iface, hub)
        print(result.summary())
        rows.append(result.to_evidence_row(ba_a, ba_b))

    if args.out and rows:
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"wrote evidence CSV: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
