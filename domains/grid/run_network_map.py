# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Build the interactive, zoomable BA interchange network map.

    python -m domains.grid.run_network_map ^
        --interchange domains\\grid\\data\\EIA930_INTERCHANGE_2023_Jan_Jun.csv ^
                      domains\\grid\\data\\EIA930_INTERCHANGE_2023_Jul_Dec.csv ^
        --out docs\\network_map.html

Open the resulting file in any browser - no server needed.
Interchange files: https://www.eia.gov/electricity/gridmonitor/
"""

from __future__ import annotations

import argparse
import sys

from pathlib import Path

from domains.grid.network_map import build_multiyear, build_network, write_map
from domains.grid.flow_geometry import load_interchange

DEFAULT_EGRID = r"domains\grid\data\egrid2023_data_rev2.xlsx"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Interactive zoomable network map of the BA interchange grid"
    )
    parser.add_argument("--interchange", nargs="+", required=True,
                        metavar="CSV", help="EIA-930 INTERCHANGE six-month CSVs")
    parser.add_argument("--all-years", action="store_true",
                        help="discover every complete INTERCHANGE year in the "
                             "data dir and add a year selector to the map")
    parser.add_argument("--egrid", default=DEFAULT_EGRID,
                        help="eGRID workbook for geographic placement "
                             "(omit/empty to skip the geographic view)")
    parser.add_argument("--balance", nargs="+", metavar="CSV",
                        help="EIA-930 BALANCE CSVs for per-BA demand/generation "
                             "(default: INTERCHANGE siblings)")
    parser.add_argument("--reports-dir", default="reports",
                        help="report JSONs for per-BA/per-tie click-through")
    parser.add_argument("--out", default="docs/network_map.html",
                        help="output HTML path")
    parser.add_argument("--title", default="US Grid — Interactive Network Map")
    args = parser.parse_args(argv)

    egrid = args.egrid if args.egrid else None

    if args.all_years:
        from domains.grid.run_daily_update import all_interchange_years
        data_dir = Path(args.interchange[0]).parent
        years = all_interchange_years(data_dir)
        if not years:
            print("no complete INTERCHANGE years found in", data_dir)
            return 1
        path = build_multiyear(
            years, path=args.out, title=args.title,
            egrid_workbook=egrid, reports_dir=args.reports_dir)
        print(f"wrote multi-year map ({'/'.join(years)}): {path}")
        return 0

    balance = args.balance or [
        s.replace("INTERCHANGE", "BALANCE") for s in args.interchange
    ]
    ties = load_interchange(args.interchange)
    network = build_network(
        ties, egrid_workbook=egrid,
        reports_dir=args.reports_dir, balance_csvs=balance,
    )
    path = write_map(network, path=args.out, title=args.title)

    print(
        f"{len(network.nodes)} BAs ({network.geo_coverage} geo-placed), "
        f"{len(network.edges)} ties, "
        f"{network.total_gross_mwh / 1e6:,.0f} TWh gross, "
        f"{network.n_bottlenecks} bottleneck ties, coupling {network.coupling}"
    )
    print(f"wrote interactive map: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
