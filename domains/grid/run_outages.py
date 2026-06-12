# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Run the EAGLE-I reliability waste analysis.

    python -m domains.grid.run_outages ^
        --outages domains\\grid\\data\\eaglei_outages_2023.csv ^
        --mcc domains\\grid\\data\\eaglei_mcc.csv

Data: figshare mirror of ORNL EAGLE-I (doi 10.6084/m9.figshare.24237376);
MCC.csv carries the modeled customer denominators.
"""

from __future__ import annotations

import argparse
import sys

from domains.grid.outages import aggregate_outages, load_mcc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="EAGLE-I reliability waste")
    parser.add_argument("--outages", required=True, help="eaglei_outages_<year>.csv")
    parser.add_argument("--mcc", required=True, help="MCC.csv customer denominators")
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--report-csv", help="write outage ranking to CSV")
    parser.add_argument("--report-md", help="write outage report to Markdown")
    parser.add_argument("--report-json", help="write outage report to JSON")
    parser.add_argument("--report-html", help="write outage dashboard to HTML")
    args = parser.parse_args(argv)

    mcc = load_mcc(args.mcc)
    report = aggregate_outages(args.outages, mcc, year=args.year)
    print(report.summary(top=args.top))
    if args.report_csv:
        report.export_csv(args.report_csv)
        print(f"wrote outage ranking CSV: {args.report_csv}")
    if args.report_md:
        report.export_markdown(args.report_md, top=args.top)
        print(f"wrote outage report: {args.report_md}")
    if args.report_json:
        report.export_json(args.report_json)
        print(f"wrote outage report JSON: {args.report_json}")
    if args.report_html:
        report.export_html(args.report_html, top=args.top)
        print(f"wrote outage dashboard: {args.report_html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
