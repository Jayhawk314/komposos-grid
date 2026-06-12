# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Extract same-year tie flows from EIA-930 INTERCHANGE files.

    python -m domains.grid.run_same_year_flows ^
        --interchange domains\\grid\\data\\EIA930_INTERCHANGE_2025_Jan_Jun.csv ^
                      domains\\grid\\data\\EIA930_INTERCHANGE_2025_Jul_Dec.csv ^
        --year 2025 --pairs NYIS-PJM --out reports\\same_year_flows.csv --append

Then feed the output to the solution studies:

    python -m domains.grid.run_solution_studies ^
        --same-year-flow reports\\same_year_flows.csv
"""

from __future__ import annotations

import argparse
import sys

from domains.grid.same_year_flows import (
    extract_same_year_flows,
    write_same_year_flow_csv,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Same-year BA tie flows from EIA-930 INTERCHANGE CSVs"
    )
    parser.add_argument("--interchange", nargs="+", required=True, metavar="CSV",
                        help="EIA-930 INTERCHANGE six-month CSVs for ONE year")
    parser.add_argument("--year", type=int, required=True,
                        help="calendar year the files cover")
    parser.add_argument("--pairs", nargs="+", required=True, metavar="BAA-BAB",
                        help="tie pairs to extract, e.g. NYIS-PJM MISO-SWPP")
    parser.add_argument("--out", default="reports/same_year_flows.csv")
    parser.add_argument("--append", action="store_true",
                        help="append to --out instead of overwriting")
    args = parser.parse_args(argv)

    flows = extract_same_year_flows(args.interchange, args.pairs, args.year)
    for flow in flows:
        print(f"{flow.geography} {flow.year}: gross {flow.gross_mwh:,.0f} MWh, "
              f"net {flow.net_mwh:,.0f} MWh")
    write_same_year_flow_csv(flows, args.out, append=args.append)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
