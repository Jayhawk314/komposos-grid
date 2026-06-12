# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Pull CAISO OASIS settlement data and produce CISO-SRP seam evidence.

    python -m domains.grid.run_caiso_oasis_evidence ^
        --cache domains\\grid\\data\\oasis\\cache ^
        --out reports\\ciso_srp_oasis_evidence.csv

Defaults to SP15 vs the Palo Verde scheduling point over Apr-Dec 2023
(the part of the ledger year OASIS still retains; ~39-month window).
The output CSV is compatible with run_congestion_evidence --evidence-csv.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date

from domains.grid.sources.caiso_oasis import (
    NODE_PALO_VERDE,
    NODE_SP15,
    fetch_range,
    seam_spread,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="CAISO OASIS seam evidence")
    parser.add_argument("--cache", default=r"domains\grid\data\oasis\cache")
    parser.add_argument("--node-a", default=NODE_SP15)
    parser.add_argument("--node-b", default=NODE_PALO_VERDE)
    parser.add_argument("--ba-a", default="CISO")
    parser.add_argument("--ba-b", default="SRP")
    parser.add_argument("--start", default="2023-04-01")
    parser.add_argument("--end", default="2024-01-01")
    parser.add_argument("--out", help="write evidence CSV row to this path")
    args = parser.parse_args(argv)

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    df_a = fetch_range(args.node_a, start, end, args.cache)
    df_b = fetch_range(args.node_b, start, end, args.cache)
    result = seam_spread(df_a, df_b, args.node_a, args.node_b)
    print(result.summary())

    if args.out:
        row = result.to_evidence_row(args.ba_a, args.ba_b)
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)
        print(f"wrote evidence CSV: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
