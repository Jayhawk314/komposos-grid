# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Run Dual-Engine verification of disputed plant->BA assignments.

    python -m domains.grid.run_verify_assignments ^
        --egrid domains\\grid\\data\\egrid2023_data_rev2.xlsx ^
        --interchange domains\\grid\\data\\EIA930_INTERCHANGE_2023_Jan_Jun.csv ^
                      domains\\grid\\data\\EIA930_INTERCHANGE_2023_Jul_Dec.csv
"""

from __future__ import annotations

import argparse
import sys

from domains.grid.flow_geometry import load_interchange
from domains.grid.sources.egrid import EGridSource
from domains.grid.verify_assignments import (
    CONTROL_BAS,
    DISPUTED_BAS_2023,
    build_verification_category,
    verify_assignments,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="ZFC/CAT Dual-Engine verification of plant->BA assignments"
    )
    parser.add_argument("--egrid", required=True,
                        help="eGRID data workbook (.xlsx)")
    parser.add_argument("--interchange", nargs="*", default=[], metavar="CSV",
                        help="EIA-930 INTERCHANGE CSVs (enables counterfactuals)")
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--disputed", nargs="*", default=DISPUTED_BAS_2023)
    parser.add_argument("--control", nargs="*", default=CONTROL_BAS)
    parser.add_argument("--queries-per-ba", type=int, default=10)
    args = parser.parse_args(argv)

    records = EGridSource(args.egrid, year=args.year).load()
    ties = load_interchange(args.interchange) if args.interchange else None

    category = build_verification_category(
        records, [*args.disputed, *args.control], ties=ties
    )
    report = verify_assignments(
        category, args.disputed, args.control,
        queries_per_ba=args.queries_per_ba,
    )
    print(report.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
