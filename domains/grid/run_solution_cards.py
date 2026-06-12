# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Build energy solution cards from current grid evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from domains.grid.solution_cards import build_energy_solution_report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Energy solution cards")
    parser.add_argument("--congestion-report", default="reports/congestion_evidence_report.json")
    parser.add_argument("--queue-match", default="reports/queue_match.json")
    parser.add_argument("--relief-curves", default="reports/grid_relief_curves.json")
    parser.add_argument("--miso-2024", default="reports/miso_seam_evidence_2024.csv")
    parser.add_argument("--nyiso-2024-2025", default="reports/nyiso_seam_2024_2025.txt")
    parser.add_argument("--ercot-spreads", default="reports/ercot_hub_spreads.json")
    parser.add_argument("--report-csv", default="reports/energy_solution_cards.csv")
    parser.add_argument("--report-json", default="reports/energy_solution_cards.json")
    parser.add_argument("--report-md", default="reports/energy_solution_cards.md")
    args = parser.parse_args(argv)

    for required in [args.congestion_report, args.queue_match, args.relief_curves]:
        path = Path(required)
        if not path.exists():
            parser.error(f"required input does not exist: {path}")

    report = build_energy_solution_report(
        congestion_report=args.congestion_report,
        queue_match=args.queue_match,
        relief_curves=args.relief_curves,
        miso_2024_evidence=_existing(args.miso_2024),
        nyiso_2024_2025=_existing(args.nyiso_2024_2025),
        ercot_spreads=_existing(args.ercot_spreads),
    )
    print(report.summary())
    report.export_csv(args.report_csv)
    report.export_json(args.report_json)
    report.export_markdown(args.report_md)
    print(f"wrote energy solution cards CSV: {args.report_csv}")
    print(f"wrote energy solution cards JSON: {args.report_json}")
    print(f"wrote energy solution cards report: {args.report_md}")
    return 0


def _existing(path: str | None):
    if not path:
        return None
    p = Path(path)
    return p if p.exists() else None


if __name__ == "__main__":
    sys.exit(main())
