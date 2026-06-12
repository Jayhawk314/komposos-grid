# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Build corridor-specific energy solution studies."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from domains.grid.solution_studies import (
    DEFAULT_INTERVENTIONS,
    build_solution_study_report,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Energy solution studies")
    parser.add_argument("--solution-cards", default="reports/energy_solution_cards.json")
    parser.add_argument("--queue-match", default="reports/queue_match.json")
    parser.add_argument("--fixed-charge-rate", type=float, default=0.10)
    parser.add_argument("--top-projects", type=int, default=5)
    parser.add_argument("--report-md", default="reports/energy_solution_studies.md")
    parser.add_argument("--report-json", default="reports/energy_solution_studies.json")
    parser.add_argument("--report-csv", default="reports/energy_solution_studies.csv")
    parser.add_argument("--interventions-csv", default="reports/energy_solution_interventions.csv")
    parser.add_argument("--assumptions-csv", default="reports/energy_solution_cost_assumptions.csv")
    parser.add_argument("--memo-dir", default="reports/solution_studies")
    args = parser.parse_args(argv)

    for required in [args.solution_cards, args.queue_match]:
        path = Path(required)
        if not path.exists():
            parser.error(f"required input does not exist: {path}")

    report = build_solution_study_report(
        solution_cards_path=args.solution_cards,
        queue_match_path=args.queue_match,
        fixed_charge_rate=args.fixed_charge_rate,
        top_projects=args.top_projects,
    )
    print(report.summary())
    report.export_markdown(args.report_md)
    report.export_json(args.report_json)
    report.export_csv(args.report_csv)
    report.export_interventions_csv(args.interventions_csv)
    _export_assumptions(args.assumptions_csv)
    memo_paths = report.export_individual_memos(args.memo_dir)
    print(f"wrote solution studies report: {args.report_md}")
    print(f"wrote solution studies JSON: {args.report_json}")
    print(f"wrote solution studies CSV: {args.report_csv}")
    print(f"wrote intervention gates CSV: {args.interventions_csv}")
    print(f"wrote cost assumptions CSV: {args.assumptions_csv}")
    for path in memo_paths:
        print(f"wrote memo: {path}")
    return 0


def _export_assumptions(path: str | Path) -> None:
    import csv

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "intervention_id",
        "label",
        "capacity_mw",
        "effective_mwh_per_mw_year",
        "solution_type",
        "source",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in DEFAULT_INTERVENTIONS:
            writer.writerow({
                "intervention_id": item.intervention_id,
                "label": item.label,
                "capacity_mw": item.capacity_mw,
                "effective_mwh_per_mw_year": item.effective_mwh_per_mw_year,
                "solution_type": item.solution_type,
                "source": item.source,
                "notes": item.notes,
            })


if __name__ == "__main__":
    sys.exit(main())
