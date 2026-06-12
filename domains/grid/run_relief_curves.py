# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Run natural-experiment-style grid relief curves (PLAN D8)."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from domains.grid.relief_curves import build_relief_curve_report


DEFAULT_CONSTRAINTS = {
    "MISO": Path("reports/miso_constraints_2023.json"),
    "PJM": Path("reports/pjm_constraints_2023.json"),
    "SPP": Path("reports/spp_2023.json"),
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Grid relief curves")
    parser.add_argument("--queue-match", default="reports/queue_match.json")
    parser.add_argument("--congestion-report", default="reports/congestion_evidence_report.json")
    parser.add_argument("--miso-constraints", default=str(DEFAULT_CONSTRAINTS["MISO"]))
    parser.add_argument("--pjm-constraints", default=str(DEFAULT_CONSTRAINTS["PJM"]))
    parser.add_argument("--spp-constraints", default=str(DEFAULT_CONSTRAINTS["SPP"]))
    parser.add_argument(
        "--mw-steps",
        nargs="*",
        type=float,
        default=[50.0, 100.0, 250.0, 500.0, 1000.0],
    )
    parser.add_argument("--report-json", default="reports/grid_relief_curves.json")
    parser.add_argument("--report-csv", default="reports/grid_relief_curves.csv")
    parser.add_argument("--points-csv", default="reports/grid_relief_curve_points.csv")
    parser.add_argument("--report-md", default="reports/grid_relief_curves.md")
    args = parser.parse_args(argv)

    queue_match = Path(args.queue_match)
    if not queue_match.exists():
        parser.error(
            f"queue match report does not exist: {queue_match}. "
            "Run domains.grid.run_queue_match first."
        )

    constraints = {
        "MISO": args.miso_constraints,
        "PJM": args.pjm_constraints,
        "SPP": args.spp_constraints,
    }
    report = build_relief_curve_report(
        queue_match_path=queue_match,
        congestion_report_path=args.congestion_report,
        constraint_reports=constraints,
        mw_steps=args.mw_steps,
    )
    print(report.summary())
    report.export_json(args.report_json)
    report.export_csv(args.report_csv)
    report.export_points_csv(args.points_csv)
    report.export_markdown(args.report_md)
    print(f"wrote relief curves JSON: {args.report_json}")
    print(f"wrote relief curves CSV: {args.report_csv}")
    print(f"wrote relief curve points CSV: {args.points_csv}")
    print(f"wrote relief curves report: {args.report_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
