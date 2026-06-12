# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Run the queue-to-bottleneck matching.

    python -m domains.grid.run_queue_match ^
        --egrid domains\\grid\\data\\egrid2023_data_rev2.xlsx ^
        --queue domains\\grid\\data\\LBNL_Ix_Queue_Data_File_thru2026.xlsx ^
        --evidence reports\\congestion_evidence_report.json ^
        --report-md reports\\queue_match_report.md ^
        --report-json reports\\queue_match.json ^
        --report-csv reports\\queue_match.csv
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from domains.grid.queue_match import (
    build_ba_state_footprint,
    match_queue_to_bottlenecks,
)
from domains.grid.sources.egrid import EGridSource
from domains.grid.sources.lbnl_queue import LBNLQueueSource


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Queue-to-bottleneck matching")
    parser.add_argument("--egrid", required=True)
    parser.add_argument("--queue", required=True)
    parser.add_argument("--evidence", required=True,
                        help="congestion_evidence_report.json")
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--report-md")
    parser.add_argument("--report-json")
    parser.add_argument("--report-csv")
    args = parser.parse_args(argv)

    footprint = build_ba_state_footprint(
        EGridSource(args.egrid, year=args.year).load()
    )
    projects = LBNLQueueSource(args.queue).load()
    claims = json.loads(Path(args.evidence).read_text(encoding="utf-8"))["claims"]

    report = match_queue_to_bottlenecks(claims, projects, footprint)
    summary = report.summary(top=args.top)
    print(summary)

    if args.report_md:
        Path(args.report_md).write_text(
            "# Queue-to-Bottleneck Matching\n\n"
            "Screening estimates: relief = capacity x capacity-factor x "
            "state-footprint weight, valued at the tie's measured congestion "
            "component, capped at the tie's annual gross flow. Not a "
            "production-cost simulation.\n\n```\n" + summary + "\n```\n",
            encoding="utf-8",
        )
    if args.report_json:
        report.export_json(args.report_json)
    if args.report_csv:
        report.export_csv(args.report_csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
