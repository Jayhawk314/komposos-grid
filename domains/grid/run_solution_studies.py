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
    load_project_cost_csv,
    load_same_year_flow_csv,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Energy solution studies")
    parser.add_argument("--solution-cards", default="reports/energy_solution_cards.json")
    parser.add_argument("--queue-match", default="reports/queue_match.json")
    parser.add_argument("--fixed-charge-rate", type=float, default=0.10)
    parser.add_argument("--top-projects", type=int, default=5)
    parser.add_argument("--same-year-flow", default=None)
    parser.add_argument("--project-costs", default=None)
    parser.add_argument("--report-md", default="reports/energy_solution_studies.md")
    parser.add_argument("--report-json", default="reports/energy_solution_studies.json")
    parser.add_argument("--report-csv", default="reports/energy_solution_studies.csv")
    parser.add_argument("--interventions-csv", default="reports/energy_solution_interventions.csv")
    parser.add_argument("--assumptions-csv", default="reports/energy_solution_cost_assumptions.csv")
    parser.add_argument("--flow-status-csv", default="reports/energy_solution_flow_status.csv")
    parser.add_argument("--same-year-flow-template-csv", default="reports/same_year_flow_template.csv")
    parser.add_argument("--project-cost-template-csv", default="reports/project_cost_template.csv")
    parser.add_argument("--project-cost-results-csv", default="reports/project_cost_results.csv")
    parser.add_argument("--memo-dir", default="reports/solution_studies")
    args = parser.parse_args(argv)

    for required in [args.solution_cards, args.queue_match]:
        path = Path(required)
        if not path.exists():
            parser.error(f"required input does not exist: {path}")
    for optional in [args.same_year_flow, args.project_costs]:
        if optional and not Path(optional).exists():
            parser.error(f"optional input does not exist: {optional}")

    same_year_flows = (
        load_same_year_flow_csv(args.same_year_flow) if args.same_year_flow else []
    )
    project_costs = (
        load_project_cost_csv(args.project_costs) if args.project_costs else []
    )

    report = build_solution_study_report(
        solution_cards_path=args.solution_cards,
        queue_match_path=args.queue_match,
        fixed_charge_rate=args.fixed_charge_rate,
        top_projects=args.top_projects,
        same_year_flows=same_year_flows,
        project_costs=project_costs,
    )
    print(report.summary())
    report.export_markdown(args.report_md)
    report.export_json(args.report_json)
    report.export_csv(args.report_csv)
    report.export_interventions_csv(args.interventions_csv)
    report.export_flow_status_csv(args.flow_status_csv)
    report.export_same_year_flow_template_csv(args.same_year_flow_template_csv)
    report.export_project_cost_template_csv(args.project_cost_template_csv)
    report.export_project_cost_results_csv(args.project_cost_results_csv)
    _export_assumptions(args.assumptions_csv)
    memo_paths = report.export_individual_memos(args.memo_dir)
    print(f"wrote solution studies report: {args.report_md}")
    print(f"wrote solution studies JSON: {args.report_json}")
    print(f"wrote solution studies CSV: {args.report_csv}")
    print(f"wrote intervention gates CSV: {args.interventions_csv}")
    print(f"wrote flow status CSV: {args.flow_status_csv}")
    print(f"wrote same-year flow template CSV: {args.same_year_flow_template_csv}")
    print(f"wrote project cost template CSV: {args.project_cost_template_csv}")
    print(f"wrote project cost results CSV: {args.project_cost_results_csv}")
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
