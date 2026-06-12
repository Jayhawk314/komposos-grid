# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Build the unified grid waste ledger from existing proof artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from domains.grid.waste_ledger import build_waste_ledger


DEFAULTS = {
    "ba_footprint_report": Path("reports/ba_footprint_report.json"),
    "congestion_report": Path("reports/congestion_evidence_report.json"),
    "flow_report": Path("reports/flow_bottleneck_report.json"),
    "outage_report": Path("reports/outage_reliability_report.json"),
    "caiso_curtailment": Path("domains/grid/data/caiso_production_curtailments_2023.xlsx"),
    "queue_workbook": Path("domains/grid/data/LBNL_Ix_Queue_Data_File_thru2026.xlsx"),
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Unified grid waste ledger")
    parser.add_argument("--ba-footprint-report", default=str(DEFAULTS["ba_footprint_report"]))
    parser.add_argument("--congestion-report", default=str(DEFAULTS["congestion_report"]))
    parser.add_argument("--flow-report", default=str(DEFAULTS["flow_report"]))
    parser.add_argument("--outage-report", default=str(DEFAULTS["outage_report"]))
    parser.add_argument("--caiso-curtailment", default=str(DEFAULTS["caiso_curtailment"]))
    parser.add_argument("--curtailment-avg-price", type=float, default=64.85)
    parser.add_argument("--queue", default=str(DEFAULTS["queue_workbook"]))
    parser.add_argument("--queue-min-cohort", type=int, default=30)
    parser.add_argument("--no-raw-workbooks", action="store_true",
                        help="use only existing JSON/CSV reports; skip CAISO/LBNL workbooks")
    parser.add_argument("--report-csv", default="reports/grid_waste_ledger.csv")
    parser.add_argument("--report-json", default="reports/grid_waste_ledger.json")
    parser.add_argument("--report-md", default="reports/grid_waste_ledger.md")
    parser.add_argument("--report-html", default="reports/grid_waste_dashboard.html")
    args = parser.parse_args(argv)

    caiso = None if args.no_raw_workbooks else _existing(args.caiso_curtailment)
    queue = None if args.no_raw_workbooks else _existing(args.queue)
    ledger = build_waste_ledger(
        ba_footprint_report=_existing(args.ba_footprint_report),
        congestion_report=_existing(args.congestion_report),
        flow_report=_existing(args.flow_report),
        outage_report=_existing(args.outage_report),
        caiso_curtailment=caiso,
        curtailment_avg_price=args.curtailment_avg_price,
        queue_workbook=queue,
        queue_min_cohort=args.queue_min_cohort,
    )
    print(ledger.summary())
    ledger.export_csv(args.report_csv)
    ledger.export_json(args.report_json)
    ledger.export_markdown(args.report_md)
    ledger.export_html(args.report_html)
    print(f"wrote grid waste ledger CSV: {args.report_csv}")
    print(f"wrote grid waste ledger JSON: {args.report_json}")
    print(f"wrote grid waste ledger report: {args.report_md}")
    print(f"wrote grid waste dashboard: {args.report_html}")
    return 0


def _existing(path: str | None):
    if not path:
        return None
    p = Path(path)
    return p if p.exists() else None


if __name__ == "__main__":
    sys.exit(main())
