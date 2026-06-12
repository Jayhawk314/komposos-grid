# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Build the grid methodology proof artifact for PLAN C5-C7."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from domains.grid.methodology import build_methodology_report


DEFAULT_LEGACY = [Path("reports/western_hub_evidence.csv")]
DEFAULT_CORRECTED = [Path("reports/congestion_evidence_report.json")]
DEFAULT_CONGESTION = Path("reports/congestion_evidence_report.json")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Grid methodology C5-C7 report")
    parser.add_argument(
        "--legacy-evidence",
        nargs="*",
        default=[str(p) for p in DEFAULT_LEGACY],
        help="legacy hub/proxy evidence CSV/JSON files",
    )
    parser.add_argument(
        "--corrected-evidence",
        nargs="*",
        default=[str(p) for p in DEFAULT_CORRECTED],
        help="corrected settlement/nodal evidence CSV/JSON files",
    )
    parser.add_argument("--congestion-report", default=str(DEFAULT_CONGESTION))
    parser.add_argument("--min-correction-ratio", type=float, default=2.0)
    parser.add_argument("--report-json", default="reports/grid_methodology_report.json")
    parser.add_argument("--report-md", default="reports/grid_methodology_report.md")
    parser.add_argument("--corrections-csv", default="reports/grid_methodology_corrections.csv")
    parser.add_argument("--bounds-csv", default="reports/grid_right_kan_bounds.csv")
    parser.add_argument("--warnings-csv", default="reports/grid_proxy_warnings.csv")
    args = parser.parse_args(argv)

    congestion = Path(args.congestion_report)
    if not congestion.exists():
        parser.error(
            f"congestion report does not exist: {congestion}. "
            "Run domains.grid.run_congestion_evidence first."
        )

    report = build_methodology_report(
        args.legacy_evidence,
        args.corrected_evidence,
        congestion_report=congestion,
        min_correction_ratio=args.min_correction_ratio,
    )
    print(report.summary())
    report.export_json(args.report_json)
    report.export_markdown(args.report_md)
    report.export_corrections_csv(args.corrections_csv)
    report.export_bounds_csv(args.bounds_csv)
    report.export_warnings_csv(args.warnings_csv)
    print(f"wrote methodology JSON: {args.report_json}")
    print(f"wrote methodology report: {args.report_md}")
    print(f"wrote correction 2-cell CSV: {args.corrections_csv}")
    print(f"wrote Right Kan bounds CSV: {args.bounds_csv}")
    print(f"wrote proxy warnings CSV: {args.warnings_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
