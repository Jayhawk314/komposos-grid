# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Join BA flow bottlenecks to LMP or congestion-cost evidence."""

from __future__ import annotations

import argparse
import sys

from domains.grid.congestion_evidence import (
    build_congestion_evidence_report,
    export_evidence_template_csv,
    load_congestion_evidence_csv,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Join flow bottlenecks to congestion evidence"
    )
    parser.add_argument(
        "--flow-report",
        required=True,
        help="flow bottleneck JSON from run_flow_geometry --report-json",
    )
    parser.add_argument(
        "--evidence-csv",
        nargs="+",
        metavar="CSV",
        help="CSV rows keyed by ba_a/ba_b with LMP spread or congestion cost",
    )
    parser.add_argument(
        "--template-csv",
        help="write an editable congestion evidence template CSV",
    )
    parser.add_argument("--report-csv", help="write joined report rows to CSV")
    parser.add_argument("--report-md", help="write joined report to Markdown")
    parser.add_argument("--report-json", help="write joined report to JSON")
    parser.add_argument("--report-html", help="write joined report dashboard to HTML")
    parser.add_argument("--top", type=int, default=25, help="rows to display/export")
    args = parser.parse_args(argv)

    if args.template_csv:
        export_evidence_template_csv(args.flow_report, args.template_csv, top=args.top)
        print(f"wrote congestion evidence template: {args.template_csv}")

    evidence = (
        load_congestion_evidence_csv(args.evidence_csv)
        if args.evidence_csv
        else {}
    )
    report = build_congestion_evidence_report(args.flow_report, evidence)
    print(report.summary(top=min(args.top, 10)))

    if args.report_csv:
        report.export_csv(args.report_csv, top=args.top)
        print(f"wrote congestion evidence CSV: {args.report_csv}")
    if args.report_md:
        report.export_markdown(args.report_md, top=args.top)
        print(f"wrote congestion evidence report: {args.report_md}")
    if args.report_json:
        report.export_json(args.report_json, top=max(args.top, 50))
        print(f"wrote congestion evidence JSON: {args.report_json}")
    if args.report_html:
        report.export_html(args.report_html, top=args.top)
        print(f"wrote congestion evidence dashboard: {args.report_html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
