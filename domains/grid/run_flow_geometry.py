# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Run Ricci/spectral bottleneck analysis on the BA interchange graph.

    python -m domains.grid.run_flow_geometry ^
        --interchange domains\\grid\\data\\EIA930_INTERCHANGE_2023_Jan_Jun.csv ^
                      domains\\grid\\data\\EIA930_INTERCHANGE_2023_Jul_Dec.csv

Interchange files: https://www.eia.gov/electricity/gridmonitor/
(sixMonthFiles/EIA930_INTERCHANGE_<year>_{Jan_Jun,Jul_Dec}.csv)
"""

from __future__ import annotations

import argparse
import sys

from domains.grid.flow_geometry import analyze_flow_geometry, load_interchange
from domains.grid.flow_report import build_flow_bottleneck_report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="BA flow graph geometry: Ricci bottlenecks + spectral seams"
    )
    parser.add_argument("--interchange", nargs="+", required=True,
                        metavar="CSV", help="EIA-930 INTERCHANGE six-month CSVs")
    parser.add_argument("--top", type=int, default=10,
                        help="bottleneck edges to display")
    parser.add_argument("--report-md",
                        help="write BA interchange bottleneck report to Markdown")
    parser.add_argument("--report-json",
                        help="write BA interchange bottleneck report to JSON")
    parser.add_argument("--report-html",
                        help="write BA interchange bottleneck dashboard to HTML")
    args = parser.parse_args(argv)

    ties = load_interchange(args.interchange)
    geometry = analyze_flow_geometry(ties)
    print(geometry.summary(top=args.top))

    if args.report_md or args.report_json or args.report_html:
        report = build_flow_bottleneck_report(ties, geometry=geometry)
        print()
        print(report.summary(top=args.top))
        if args.report_md:
            report.export_markdown(args.report_md, top=args.top)
            print(f"  wrote flow bottleneck report: {args.report_md}")
        if args.report_json:
            report.export_json(args.report_json, top=max(args.top, 25))
            print(f"  wrote flow bottleneck report JSON: {args.report_json}")
        if args.report_html:
            report.export_html(args.report_html, top=args.top)
            print(f"  wrote flow bottleneck dashboard: {args.report_html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
