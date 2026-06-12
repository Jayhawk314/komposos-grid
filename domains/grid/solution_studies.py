# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Corridor solution studies for energy interventions.

Solution cards rank corridors. This module turns the top corridors into
audience-ready memos with:

* current seam value and year-over-year trend;
* top active/withdrawn queue projects, revalued at the current spread;
* named constraint evidence;
* project-cost break-even envelopes.

The break-even envelopes intentionally avoid fake precision. They answer:
"What annual cost or capital budget can this corridor support before the
solution stops clearing on congestion value alone?"
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence


HOURS_PER_YEAR = 8760.0
DEFAULT_FIXED_CHARGE_RATE = 0.10
DEFAULT_BASELINE_FLOW_YEAR = 2023


@dataclass(frozen=True)
class InterventionTemplate:
    intervention_id: str
    label: str
    capacity_mw: float
    effective_mwh_per_mw_year: float
    solution_type: str
    source: str
    notes: str = ""


DEFAULT_INTERVENTIONS = [
    InterventionTemplate(
        intervention_id="transfer_upgrade_50mw",
        label="50 MW targeted transfer upgrade",
        capacity_mw=50.0,
        effective_mwh_per_mw_year=HOURS_PER_YEAR,
        solution_type="transmission_or_grid_enhancing_transfer",
        source="cost-gate envelope; compare against developer/utility estimate",
        notes="Use for reconductoring, ratings, phase-angle control, or small transfer upgrades.",
    ),
    InterventionTemplate(
        intervention_id="transfer_upgrade_100mw",
        label="100 MW targeted transfer upgrade",
        capacity_mw=100.0,
        effective_mwh_per_mw_year=HOURS_PER_YEAR,
        solution_type="transmission_or_grid_enhancing_transfer",
        source="cost-gate envelope; compare against developer/utility estimate",
        notes="Firm-transfer case; assumes relief is usable across the year.",
    ),
    InterventionTemplate(
        intervention_id="transfer_upgrade_250mw",
        label="250 MW targeted transfer upgrade",
        capacity_mw=250.0,
        effective_mwh_per_mw_year=HOURS_PER_YEAR,
        solution_type="transmission_or_grid_enhancing_transfer",
        source="cost-gate envelope; compare against developer/utility estimate",
        notes="Larger transfer case; capped by the current annual seam value.",
    ),
    InterventionTemplate(
        intervention_id="storage_4h_100mw",
        label="100 MW / 4-hour storage siting screen",
        capacity_mw=100.0,
        effective_mwh_per_mw_year=1200.0,
        solution_type="storage",
        source=(
            "NREL ATB utility-scale battery storage methodology "
            "(https://atb.nrel.gov/electricity/2024/utility-scale_battery_storage); "
            "cost-gate envelope here is derived from local seam value"
        ),
        notes="Throughput proxy matches queue matching: 4h duration and about 300 cycles/year.",
    ),
    InterventionTemplate(
        intervention_id="flex_load_100mw",
        label="100 MW flexible-load program",
        capacity_mw=100.0,
        effective_mwh_per_mw_year=600.0,
        solution_type="flexible_load",
        source="cost-gate envelope; compare against program bids",
        notes="Critical-window dispatch proxy, not firm transfer capability.",
    ),
]


DEFAULT_EFFECTIVE_MWH_PER_MW_YEAR = {
    "transmission_or_grid_enhancing_transfer": HOURS_PER_YEAR,
    "transfer": HOURS_PER_YEAR,
    "grid_enhancing_transfer": HOURS_PER_YEAR,
    "storage": 1200.0,
    "flexible_load": 600.0,
    "demand_response": 600.0,
}


@dataclass(frozen=True)
class QueueCandidate:
    q_id: str
    status: str
    fuel: str
    state: str
    region: str
    mw: float
    role: str
    side: str
    relief_mwh: float
    relief_value_usd: float

    def to_row(self) -> Dict[str, Any]:
        return {
            "q_id": self.q_id,
            "status": self.status,
            "fuel": self.fuel,
            "state": self.state,
            "region": self.region,
            "mw": self.mw,
            "role": self.role,
            "side": self.side,
            "relief_mwh": self.relief_mwh,
            "relief_value_usd": self.relief_value_usd,
        }


@dataclass(frozen=True)
class InterventionCase:
    intervention_id: str
    label: str
    solution_type: str
    capacity_mw: float
    relief_mwh: float
    relief_value_usd: float
    break_even_annual_cost_usd: float
    break_even_capex_usd: float
    break_even_capex_usd_per_kw: float
    fixed_charge_rate: float
    source: str
    notes: str = ""

    def to_row(self) -> Dict[str, Any]:
        return {
            "intervention_id": self.intervention_id,
            "label": self.label,
            "solution_type": self.solution_type,
            "capacity_mw": self.capacity_mw,
            "relief_mwh": self.relief_mwh,
            "relief_value_usd": self.relief_value_usd,
            "break_even_annual_cost_usd": self.break_even_annual_cost_usd,
            "break_even_capex_usd": self.break_even_capex_usd,
            "break_even_capex_usd_per_kw": self.break_even_capex_usd_per_kw,
            "fixed_charge_rate": self.fixed_charge_rate,
            "source": self.source,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class SameYearFlowEvidence:
    geography: str
    ba_a: str
    ba_b: str
    year: int
    gross_mwh: float
    net_mwh: float = 0.0
    source: str = ""
    notes: str = ""

    def to_row(self) -> Dict[str, Any]:
        return {
            "geography": self.geography,
            "ba_a": self.ba_a,
            "ba_b": self.ba_b,
            "year": self.year,
            "gross_mwh": self.gross_mwh,
            "net_mwh": self.net_mwh,
            "source": self.source,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ProjectCostInput:
    project_id: str
    project_name: str
    geography: str
    ba_a: str
    ba_b: str
    solution_type: str
    capacity_mw: float
    effective_mwh_per_mw_year: float
    capex_usd: float
    annual_om_usd: float = 0.0
    annual_cost_usd: float = 0.0
    fixed_charge_rate: float = DEFAULT_FIXED_CHARGE_RATE
    in_service_year: int = 0
    owner: str = ""
    source: str = ""
    notes: str = ""

    def to_row(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "geography": self.geography,
            "ba_a": self.ba_a,
            "ba_b": self.ba_b,
            "solution_type": self.solution_type,
            "capacity_mw": self.capacity_mw,
            "effective_mwh_per_mw_year": self.effective_mwh_per_mw_year,
            "capex_usd": self.capex_usd,
            "annual_om_usd": self.annual_om_usd,
            "annual_cost_usd": self.annual_cost_usd,
            "fixed_charge_rate": self.fixed_charge_rate,
            "in_service_year": self.in_service_year,
            "owner": self.owner,
            "source": self.source,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ProjectCostResult:
    project_id: str
    project_name: str
    geography: str
    solution_type: str
    capacity_mw: float
    effective_mwh_per_mw_year: float
    capex_usd: float
    annualized_capex_usd: float
    annual_om_usd: float
    annual_cost_usd: float
    fixed_charge_rate: float
    relief_mwh: float
    relief_value_usd: float
    benefit_cost_ratio: float
    net_annual_value_usd: float
    clears_congestion_value: bool
    cost_method: str
    source: str
    notes: str = ""

    def to_row(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "geography": self.geography,
            "solution_type": self.solution_type,
            "capacity_mw": self.capacity_mw,
            "effective_mwh_per_mw_year": self.effective_mwh_per_mw_year,
            "capex_usd": self.capex_usd,
            "annualized_capex_usd": self.annualized_capex_usd,
            "annual_om_usd": self.annual_om_usd,
            "annual_cost_usd": self.annual_cost_usd,
            "fixed_charge_rate": self.fixed_charge_rate,
            "relief_mwh": self.relief_mwh,
            "relief_value_usd": self.relief_value_usd,
            "benefit_cost_ratio": self.benefit_cost_ratio,
            "net_annual_value_usd": self.net_annual_value_usd,
            "clears_congestion_value": self.clears_congestion_value,
            "cost_method": self.cost_method,
            "source": self.source,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class CorridorStudy:
    study_id: str
    title: str
    geography: str
    current_year: int
    current_spread_usd_mwh: float
    annual_value_usd: float
    gross_flow_mwh: float
    flow_year: int
    flow_basis: str
    same_year_flow_status: str
    same_year_flow_source: str
    trend_summary: str
    evidence_basis: str
    constraints: List[str]
    active_queue_gw: float
    withdrawn_queue_gw: float
    top_active: List[QueueCandidate]
    top_withdrawn: List[QueueCandidate]
    interventions: List[InterventionCase]
    recommended_path: str
    next_action: str
    caveat: str
    project_cost_results: List[ProjectCostResult] = field(default_factory=list)

    @property
    def best_intervention(self) -> InterventionCase | None:
        if not self.interventions:
            return None
        return max(self.interventions, key=lambda item: item.relief_value_usd)

    def to_row(self) -> Dict[str, Any]:
        best = self.best_intervention
        return {
            "study_id": self.study_id,
            "title": self.title,
            "geography": self.geography,
            "current_year": self.current_year,
            "current_spread_usd_mwh": self.current_spread_usd_mwh,
            "annual_value_usd": self.annual_value_usd,
            "gross_flow_mwh": self.gross_flow_mwh,
            "flow_year": self.flow_year,
            "same_year_flow_status": self.same_year_flow_status,
            "flow_basis": self.flow_basis,
            "same_year_flow_source": self.same_year_flow_source,
            "active_queue_gw": self.active_queue_gw,
            "withdrawn_queue_gw": self.withdrawn_queue_gw,
            "best_intervention": best.label if best else "",
            "best_relief_value_usd": best.relief_value_usd if best else 0.0,
            "best_break_even_capex_usd": best.break_even_capex_usd if best else 0.0,
            "best_break_even_capex_usd_per_kw": (
                best.break_even_capex_usd_per_kw if best else 0.0
            ),
            "recommended_path": self.recommended_path,
            "next_action": self.next_action,
            "caveat": self.caveat,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.to_row(),
            "trend_summary": self.trend_summary,
            "evidence_basis": self.evidence_basis,
            "constraints": self.constraints,
            "top_active": [item.to_row() for item in self.top_active],
            "top_withdrawn": [item.to_row() for item in self.top_withdrawn],
            "interventions": [item.to_row() for item in self.interventions],
            "project_cost_results": [
                item.to_row() for item in self.project_cost_results
            ],
        }

    def to_markdown(self) -> str:
        lines = [
            f"# {self.title}",
            "",
            "## Decision Frame",
            "",
            f"- Corridor: **{self.geography}**",
            f"- Current evidence year: **{self.current_year}**",
            f"- Current congestion spread: **${self.current_spread_usd_mwh:.2f}/MWh**",
            f"- Annual value at current spread: **${self.annual_value_usd:,.0f}/yr**",
            (
                f"- Gross flow basis: **{self.gross_flow_mwh:,.0f} MWh** "
                f"({self.flow_year}; {self.same_year_flow_status})"
            ),
            f"- Trend: {self.trend_summary}",
            f"- Recommended path: {self.recommended_path}",
            f"- Next action: {self.next_action}",
            f"- Caveat: {self.caveat}",
            "",
            "## Constraints",
            "",
        ]
        if self.constraints:
            lines.extend(f"- {constraint}" for constraint in self.constraints)
        else:
            lines.append("- Not attached yet.")

        lines.extend([
            "",
            "## Project-Cost Gates",
            "",
            "A project clears on congestion value alone only if its real annual "
            "cost is below the break-even annual cost below. Capital envelopes "
            f"use a {self.interventions[0].fixed_charge_rate:.0%} fixed-charge rate.",
            "",
            "| Intervention | Capacity | Relief Value | Break-Even Annual Cost | Break-Even Capex | Capex $/kW |",
            "|---|---:|---:|---:|---:|---:|",
        ])
        for case in self.interventions:
            lines.append(
                f"| {case.label} | {case.capacity_mw:,.0f} MW | "
                f"${case.relief_value_usd:,.0f}/yr | "
                f"${case.break_even_annual_cost_usd:,.0f}/yr | "
                f"${case.break_even_capex_usd:,.0f} | "
                f"${case.break_even_capex_usd_per_kw:,.0f}/kW |"
            )

        lines.extend([
            "",
            "## Quoted Project Costs",
            "",
        ])
        if self.project_cost_results:
            lines.extend([
                "| Project | Type | Capacity | Annual Cost | Relief Value | B/C | Net Value |",
                "|---|---|---:|---:|---:|---:|---:|",
            ])
            for result in self.project_cost_results:
                lines.append(
                    f"| {result.project_name or result.project_id} | "
                    f"{result.solution_type} | {result.capacity_mw:,.0f} MW | "
                    f"${result.annual_cost_usd:,.0f}/yr | "
                    f"${result.relief_value_usd:,.0f}/yr | "
                    f"{result.benefit_cost_ratio:.2f} | "
                    f"${result.net_annual_value_usd:,.0f}/yr |"
                )
        else:
            lines.append("- No quoted project costs supplied yet.")

        lines.extend([
            "",
            "## Active Queue Candidates",
            "",
            "| Queue ID | Fuel | MW | State | Role | Side | Relief Value |",
            "|---|---|---:|---|---|---|---:|",
        ])
        for item in self.top_active:
            lines.append(
                f"| {item.q_id} | {item.fuel} | {item.mw:,.0f} | {item.state} | "
                f"{item.role} | {item.side} | ${item.relief_value_usd:,.0f}/yr |"
            )
        if not self.top_active:
            lines.append("| None |  |  |  |  |  |  |")

        lines.extend([
            "",
            "## Withdrawn Opportunity",
            "",
            "| Queue ID | Fuel | MW | State | Role | Side | Lost Relief Value |",
            "|---|---|---:|---|---|---|---:|",
        ])
        for item in self.top_withdrawn:
            lines.append(
                f"| {item.q_id} | {item.fuel} | {item.mw:,.0f} | {item.state} | "
                f"{item.role} | {item.side} | ${item.relief_value_usd:,.0f}/yr |"
            )
        if not self.top_withdrawn:
            lines.append("| None |  |  |  |  |  |  |")
        return "\n".join(lines) + "\n"


@dataclass
class SolutionStudyReport:
    studies: List[CorridorStudy]

    def ranked(self) -> List[CorridorStudy]:
        return sorted(self.studies, key=lambda item: item.annual_value_usd, reverse=True)

    def summary(self) -> str:
        lines = [f"Solution studies: {len(self.studies)}"]
        for study in self.ranked():
            best = study.best_intervention
            lines.append(
                f"  {study.geography}: ${study.annual_value_usd:,.0f}/yr, "
                f"best gate {best.label if best else 'none'} "
                f"${best.break_even_capex_usd:,.0f} capex"
            )
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_studies": len(self.studies),
            "studies": [study.to_dict() for study in self.ranked()],
        }

    def to_rows(self) -> List[Dict[str, Any]]:
        return [study.to_row() for study in self.ranked()]

    def to_intervention_rows(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for study in self.ranked():
            for case in study.interventions:
                rows.append({
                    "study_id": study.study_id,
                    "geography": study.geography,
                    **case.to_row(),
                })
        return rows

    def to_flow_status_rows(self) -> List[Dict[str, Any]]:
        return [
            {
                "study_id": study.study_id,
                "geography": study.geography,
                "current_year": study.current_year,
                "current_spread_usd_mwh": study.current_spread_usd_mwh,
                "gross_flow_mwh": study.gross_flow_mwh,
                "flow_year": study.flow_year,
                "same_year_flow_status": study.same_year_flow_status,
                "annual_value_usd": study.annual_value_usd,
                "flow_basis": study.flow_basis,
                "same_year_flow_source": study.same_year_flow_source,
            }
            for study in self.ranked()
        ]

    def to_project_cost_rows(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for study in self.ranked():
            for result in study.project_cost_results:
                rows.append({"study_id": study.study_id, **result.to_row()})
        return rows

    def with_project_costs(
        self, project_costs: Sequence[ProjectCostInput]
    ) -> "SolutionStudyReport":
        return SolutionStudyReport(
            studies=[
                replace(
                    study,
                    project_cost_results=_project_cost_results_for_study(
                        study, project_costs
                    ),
                )
                for study in self.studies
            ]
        )

    def to_markdown(self) -> str:
        lines = [
            "# Energy Solution Studies",
            "",
            "## Summary",
            "",
            "| Corridor | Value | Current Spread | Active Queue | Best Cost Gate | Next Action |",
            "|---|---:|---:|---:|---:|---|",
        ]
        for study in self.ranked():
            best = study.best_intervention
            lines.append(
                f"| {study.geography} | ${study.annual_value_usd:,.0f}/yr | "
                f"${study.current_spread_usd_mwh:.2f}/MWh | "
                f"{study.active_queue_gw:,.1f} GW | "
                f"${best.break_even_capex_usd:,.0f} | {study.next_action} |"
            )
        lines.extend([
            "",
            "## Flow Evidence Status",
            "",
            "| Corridor | Price Year | Flow Year | Status | Gross Flow | Annual Value |",
            "|---|---:|---:|---|---:|---:|",
        ])
        for study in self.ranked():
            lines.append(
                f"| {study.geography} | {study.current_year} | {study.flow_year} | "
                f"{study.same_year_flow_status} | "
                f"{study.gross_flow_mwh:,.0f} MWh | "
                f"${study.annual_value_usd:,.0f}/yr |"
            )
        lines.append("")
        for study in self.ranked():
            lines.append(study.to_markdown())
        return "\n".join(lines)

    def export_json(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    def export_csv(self, path: str | Path) -> None:
        _write_csv(path, self.to_rows())

    def export_interventions_csv(self, path: str | Path) -> None:
        _write_csv(path, self.to_intervention_rows())

    def export_flow_status_csv(self, path: str | Path) -> None:
        _write_csv(path, self.to_flow_status_rows())

    def export_project_cost_results_csv(self, path: str | Path) -> None:
        _write_csv_with_fields(
            path,
            self.to_project_cost_rows(),
            PROJECT_COST_RESULT_FIELDS,
        )

    def export_project_cost_template_csv(self, path: str | Path) -> None:
        rows: List[Dict[str, Any]] = []
        for study in self.ranked():
            ba_a, ba_b = _ba_pair_from_geography(study.geography)
            for solution_type in [
                "transmission_or_grid_enhancing_transfer",
                "storage",
                "flexible_load",
            ]:
                rows.append({
                    "project_id": "",
                    "project_name": "",
                    "geography": study.geography,
                    "ba_a": ba_a,
                    "ba_b": ba_b,
                    "solution_type": solution_type,
                    "capacity_mw": "",
                    "effective_mwh_per_mw_year": (
                        DEFAULT_EFFECTIVE_MWH_PER_MW_YEAR[solution_type]
                    ),
                    "capex_usd": "",
                    "annual_om_usd": "",
                    "annual_cost_usd": "",
                    "fixed_charge_rate": DEFAULT_FIXED_CHARGE_RATE,
                    "in_service_year": "",
                    "owner": "",
                    "source": "",
                    "notes": "",
                })
        _write_csv_with_fields(path, rows, PROJECT_COST_INPUT_FIELDS)

    def export_same_year_flow_template_csv(self, path: str | Path) -> None:
        rows: List[Dict[str, Any]] = []
        for study in self.ranked():
            ba_a, ba_b = _ba_pair_from_geography(study.geography)
            rows.append({
                "geography": study.geography,
                "ba_a": ba_a,
                "ba_b": ba_b,
                "year": study.current_year,
                "gross_mwh": "",
                "net_mwh": "",
                "source": "",
                "notes": "Fill from same-year EIA-930 INTERCHANGE or ISO flow evidence.",
                "current_fallback_flow_year": study.flow_year,
                "current_fallback_gross_mwh": study.gross_flow_mwh,
                "current_status": study.same_year_flow_status,
            })
        _write_csv_with_fields(path, rows, SAME_YEAR_FLOW_TEMPLATE_FIELDS)

    def export_markdown(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(), encoding="utf-8")

    def export_individual_memos(self, directory: str | Path) -> List[Path]:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        paths: List[Path] = []
        for study in self.ranked():
            path = directory / f"{study.study_id}.md"
            path.write_text(study.to_markdown(), encoding="utf-8")
            paths.append(path)
        return paths


def build_solution_study_report(
    solution_cards_path: str | Path,
    queue_match_path: str | Path,
    interventions: Sequence[InterventionTemplate] | None = None,
    fixed_charge_rate: float = DEFAULT_FIXED_CHARGE_RATE,
    top_projects: int = 5,
    same_year_flows: Sequence[SameYearFlowEvidence] | None = None,
    project_costs: Sequence[ProjectCostInput] | None = None,
    baseline_flow_year: int = DEFAULT_BASELINE_FLOW_YEAR,
) -> SolutionStudyReport:
    cards = _load_solution_cards(solution_cards_path)
    queue = _load_queue(queue_match_path)
    interventions = list(interventions or DEFAULT_INTERVENTIONS)
    flow_map = _same_year_flow_map(same_year_flows or [])
    target_geographies = {"NYIS-PJM", "MISO-SWPP"}
    studies: List[CorridorStudy] = []
    for card in cards:
        geography = str(card.get("geography", ""))
        if geography not in target_geographies:
            continue
        key = _key_from_geography(geography)
        queue_row = queue.get(key, {})
        studies.append(
            _build_study(
                card,
                queue_row,
                interventions,
                fixed_charge_rate,
                top_projects,
                flow_map.get((key, int(_float(card.get("current_year"))))),
                baseline_flow_year,
            )
        )
    report = SolutionStudyReport(studies=studies)
    if project_costs:
        report = report.with_project_costs(project_costs)
    return report


def _build_study(
    card: Mapping[str, Any],
    queue_row: Mapping[str, Any],
    interventions: Sequence[InterventionTemplate],
    fixed_charge_rate: float,
    top_projects: int,
    same_year_flow: SameYearFlowEvidence | None,
    baseline_flow_year: int,
) -> CorridorStudy:
    geography = str(card.get("geography", ""))
    spread = _float(card.get("spread_usd_mwh"))
    annual_value = _float(card.get("annual_value_usd"))
    gross_mwh = annual_value / spread if spread > 0 else 0.0
    current_year = int(_float(card.get("current_year")))
    flow_year = baseline_flow_year
    flow_source = "inferred from current card value and 2023 EIA-930 flow baseline"
    flow_basis = "current spread applied to existing baseline gross flow"
    same_year_flow_status = (
        "same_year_flow"
        if current_year == baseline_flow_year
        else "needs_same_year_flow"
    )
    if same_year_flow and same_year_flow.gross_mwh > 0:
        gross_mwh = same_year_flow.gross_mwh
        annual_value = gross_mwh * spread
        flow_year = same_year_flow.year
        flow_source = same_year_flow.source
        flow_basis = "same-year gross flow multiplied by current spread"
        same_year_flow_status = "same_year_flow"
    constraints = _split_semicolon(card.get("constraints"))
    top_active = _project_candidates(
        queue_row.get("top_active", []),
        spread,
        top=top_projects,
    )
    top_withdrawn = _project_candidates(
        queue_row.get("top_withdrawn", []),
        spread,
        top=top_projects,
    )
    cases = [
        _intervention_case(template, spread, gross_mwh, fixed_charge_rate)
        for template in interventions
    ]
    study_id = geography.lower().replace("-", "_")
    recommended_path, next_action, caveat = _study_guidance(
        geography, same_year_flow_status
    )
    return CorridorStudy(
        study_id=study_id,
        title=_study_title(geography),
        geography=geography,
        current_year=current_year,
        current_spread_usd_mwh=spread,
        annual_value_usd=annual_value,
        gross_flow_mwh=gross_mwh,
        flow_year=flow_year,
        flow_basis=flow_basis,
        same_year_flow_status=same_year_flow_status,
        same_year_flow_source=flow_source,
        trend_summary=str(card.get("trend_summary", "")),
        evidence_basis=str(card.get("evidence_basis", "")),
        constraints=constraints,
        active_queue_gw=_float(card.get("active_queue_gw")),
        withdrawn_queue_gw=_float(card.get("withdrawn_queue_gw")),
        top_active=top_active,
        top_withdrawn=top_withdrawn,
        interventions=cases,
        recommended_path=recommended_path,
        next_action=next_action,
        caveat=caveat,
    )


def load_same_year_flow_csv(path: str | Path) -> List[SameYearFlowEvidence]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    flows: List[SameYearFlowEvidence] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            year = int(_float(row.get("year")))
            gross_mwh = _float(row.get("gross_mwh"))
            if year <= 0 or gross_mwh <= 0:
                continue
            geography = str(row.get("geography") or row.get("corridor") or "")
            ba_a = str(row.get("ba_a") or "")
            ba_b = str(row.get("ba_b") or "")
            if not geography and ba_a and ba_b:
                geography = f"{ba_a}-{ba_b}"
            if not ba_a or not ba_b:
                ba_a, ba_b = _ba_pair_from_geography(geography)
            if not geography or not ba_a or not ba_b:
                continue
            flows.append(
                SameYearFlowEvidence(
                    geography=geography,
                    ba_a=ba_a,
                    ba_b=ba_b,
                    year=year,
                    gross_mwh=gross_mwh,
                    net_mwh=_float(row.get("net_mwh")),
                    source=str(row.get("source") or ""),
                    notes=str(row.get("notes") or ""),
                )
            )
    return flows


def load_project_cost_csv(path: str | Path) -> List[ProjectCostInput]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    costs: List[ProjectCostInput] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            capacity_mw = _float(row.get("capacity_mw"))
            capex_usd = _float(row.get("capex_usd"))
            annual_om_usd = _float(row.get("annual_om_usd"))
            annual_cost_usd = _float(row.get("annual_cost_usd"))
            if (
                capacity_mw <= 0
                or (capex_usd <= 0 and annual_om_usd <= 0 and annual_cost_usd <= 0)
            ):
                continue
            geography = str(row.get("geography") or row.get("corridor") or "")
            ba_a = str(row.get("ba_a") or "")
            ba_b = str(row.get("ba_b") or "")
            if not geography and ba_a and ba_b:
                geography = f"{ba_a}-{ba_b}"
            if not ba_a or not ba_b:
                ba_a, ba_b = _ba_pair_from_geography(geography)
            solution_type = str(
                row.get("solution_type")
                or "transmission_or_grid_enhancing_transfer"
            )
            fixed_charge_rate = (
                _float(row.get("fixed_charge_rate")) or DEFAULT_FIXED_CHARGE_RATE
            )
            effective_mwh = (
                _float(row.get("effective_mwh_per_mw_year"))
                or _effective_mwh_per_mw_year(solution_type)
            )
            costs.append(
                ProjectCostInput(
                    project_id=str(row.get("project_id") or ""),
                    project_name=str(row.get("project_name") or ""),
                    geography=geography,
                    ba_a=ba_a,
                    ba_b=ba_b,
                    solution_type=solution_type,
                    capacity_mw=capacity_mw,
                    effective_mwh_per_mw_year=effective_mwh,
                    capex_usd=capex_usd,
                    annual_om_usd=annual_om_usd,
                    annual_cost_usd=annual_cost_usd,
                    fixed_charge_rate=fixed_charge_rate,
                    in_service_year=int(_float(row.get("in_service_year"))),
                    owner=str(row.get("owner") or ""),
                    source=str(row.get("source") or ""),
                    notes=str(row.get("notes") or ""),
                )
            )
    return costs


def _same_year_flow_map(
    flows: Sequence[SameYearFlowEvidence],
) -> Dict[tuple[tuple[str, str], int], SameYearFlowEvidence]:
    out: Dict[tuple[tuple[str, str], int], SameYearFlowEvidence] = {}
    for flow in flows:
        key = _tie_key(flow.ba_a, flow.ba_b)
        out[(key, flow.year)] = flow
    return out


def _project_cost_results_for_study(
    study: CorridorStudy,
    project_costs: Sequence[ProjectCostInput],
) -> List[ProjectCostResult]:
    results: List[ProjectCostResult] = []
    for cost in project_costs:
        if not _cost_matches_study(cost, study):
            continue
        annualized_capex = cost.capex_usd * cost.fixed_charge_rate
        if cost.annual_cost_usd > 0:
            annual_cost = cost.annual_cost_usd
            cost_method = "explicit_annual_cost"
        else:
            annual_cost = annualized_capex + cost.annual_om_usd
            cost_method = "capex_fixed_charge_plus_om"
        relief_mwh = min(
            cost.capacity_mw * cost.effective_mwh_per_mw_year,
            study.gross_flow_mwh,
        )
        relief_value = relief_mwh * study.current_spread_usd_mwh
        bcr = relief_value / annual_cost if annual_cost > 0 else 0.0
        results.append(
            ProjectCostResult(
                project_id=cost.project_id,
                project_name=cost.project_name,
                geography=study.geography,
                solution_type=cost.solution_type,
                capacity_mw=cost.capacity_mw,
                effective_mwh_per_mw_year=cost.effective_mwh_per_mw_year,
                capex_usd=cost.capex_usd,
                annualized_capex_usd=annualized_capex,
                annual_om_usd=cost.annual_om_usd,
                annual_cost_usd=annual_cost,
                fixed_charge_rate=cost.fixed_charge_rate,
                relief_mwh=relief_mwh,
                relief_value_usd=relief_value,
                benefit_cost_ratio=bcr,
                net_annual_value_usd=relief_value - annual_cost,
                clears_congestion_value=bcr >= 1.0,
                cost_method=cost_method,
                source=cost.source,
                notes=cost.notes,
            )
        )
    return sorted(results, key=lambda item: item.benefit_cost_ratio, reverse=True)


def _intervention_case(
    template: InterventionTemplate,
    spread_usd_mwh: float,
    gross_mwh: float,
    fixed_charge_rate: float,
) -> InterventionCase:
    relief_mwh = min(template.capacity_mw * template.effective_mwh_per_mw_year, gross_mwh)
    relief_value = relief_mwh * spread_usd_mwh
    capex = relief_value / fixed_charge_rate if fixed_charge_rate > 0 else 0.0
    capex_per_kw = capex / (template.capacity_mw * 1000.0) if template.capacity_mw > 0 else 0.0
    return InterventionCase(
        intervention_id=template.intervention_id,
        label=template.label,
        solution_type=template.solution_type,
        capacity_mw=template.capacity_mw,
        relief_mwh=relief_mwh,
        relief_value_usd=relief_value,
        break_even_annual_cost_usd=relief_value,
        break_even_capex_usd=capex,
        break_even_capex_usd_per_kw=capex_per_kw,
        fixed_charge_rate=fixed_charge_rate,
        source=template.source,
        notes=template.notes,
    )


def _project_candidates(
    rows: Any,
    spread_usd_mwh: float,
    top: int,
) -> List[QueueCandidate]:
    candidates: List[QueueCandidate] = []
    for row in rows if isinstance(rows, list) else []:
        relief_mwh = _float(row.get("relief_mwh"))
        candidates.append(
            QueueCandidate(
                q_id=str(row.get("q_id", "")),
                status=str(row.get("status", "")),
                fuel=str(row.get("fuel", "")),
                state=str(row.get("state", "")),
                region=str(row.get("region", "")),
                mw=_float(row.get("mw")),
                role=str(row.get("role", "")),
                side=str(row.get("side", "")),
                relief_mwh=relief_mwh,
                relief_value_usd=relief_mwh * spread_usd_mwh,
            )
        )
    return sorted(candidates, key=lambda item: item.relief_value_usd, reverse=True)[:top]


def _cost_matches_study(cost: ProjectCostInput, study: CorridorStudy) -> bool:
    if cost.geography:
        return _key_from_geography(cost.geography) == _key_from_geography(study.geography)
    return _tie_key(cost.ba_a, cost.ba_b) == _key_from_geography(study.geography)


def _effective_mwh_per_mw_year(solution_type: str) -> float:
    normalized = solution_type.strip().lower()
    if normalized in DEFAULT_EFFECTIVE_MWH_PER_MW_YEAR:
        return DEFAULT_EFFECTIVE_MWH_PER_MW_YEAR[normalized]
    if "storage" in normalized:
        return DEFAULT_EFFECTIVE_MWH_PER_MW_YEAR["storage"]
    if "flex" in normalized or "demand" in normalized:
        return DEFAULT_EFFECTIVE_MWH_PER_MW_YEAR["flexible_load"]
    return DEFAULT_EFFECTIVE_MWH_PER_MW_YEAR[
        "transmission_or_grid_enhancing_transfer"
    ]


def _study_guidance(
    geography: str, same_year_flow_status: str = "needs_same_year_flow"
) -> tuple[str, str, str]:
    if geography == "NYIS-PJM":
        if same_year_flow_status == "same_year_flow":
            caveat = (
                "Value uses same-year gross flow. CHPE (1,250 MW HVDC into "
                "NYC) entered commercial operation 2026-05-13 and should "
                "compress this seam's spread going forward, so the 2025 "
                "spread-based value is an upper bound for post-2026 cases; "
                "rerun seam evidence on post-CHPE months before committing."
            )
        else:
            caveat = (
                "The 2025 value is strong, but the current gross-flow "
                "baseline still needs a 2025 evidence rerun before a final "
                "investment case."
            )
        return (
            "Start with a 50-100 MW transfer-relief or queue-rescue package; storage clears only if it is paid for by more than seam congestion.",
            "Price the top PJM-side active projects and a small transfer upgrade against the break-even capex envelope.",
            caveat,
        )
    if geography == "MISO-SWPP":
        return (
            "Start with targeted transfer relief around the wind-belt constraints, then test storage only where it also captures local energy or capacity value.",
            "Map CHAWATCHAPAT and Charlie Creek-Watford to upgrade candidates and price a 50-100 MW relief package.",
            "MISO-side and SPP-side seam evidence corroborate the problem; do not double-count them as separate benefits.",
        )
    return (
        "Build project-specific cost evidence before scoping.",
        "Attach named projects and quotes.",
        "Screening only.",
    )


def _study_title(geography: str) -> str:
    if geography == "NYIS-PJM":
        return "PJM-NYIS 2025 Solution Memo"
    if geography == "MISO-SWPP":
        return "MISO-SWPP Wind-Belt Solution Memo"
    return f"{geography} Solution Memo"


def _load_solution_cards(path: str | Path) -> List[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(payload.get("cards", []))


def _load_queue(path: str | Path) -> Dict[tuple[str, str], Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        _tie_key(row.get("ba_a", ""), row.get("ba_b", "")): row
        for row in payload.get("ties", [])
    }


def _key_from_geography(geography: str) -> tuple[str, str]:
    if "-" not in geography:
        return ("", "")
    left, right = geography.split("-", 1)
    return _tie_key(left, right)


def _ba_pair_from_geography(geography: str) -> tuple[str, str]:
    if "-" not in geography:
        return ("", "")
    left, right = geography.split("-", 1)
    return (left.strip(), right.strip())


def _tie_key(ba_a: Any, ba_b: Any) -> tuple[str, str]:
    return tuple(sorted((str(ba_a).strip(), str(ba_b).strip())))


def _split_semicolon(value: Any) -> List[str]:
    return [part.strip() for part in str(value or "").split(";") if part.strip()]


def _float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    text = str(value).strip().replace(",", "").replace("$", "")
    if not text:
        return 0.0
    try:
        out = float(text)
    except ValueError:
        return 0.0
    return 0.0 if math.isnan(out) else out


def _write_csv(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = _fieldnames(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_csv_with_fields(
    path: str | Path,
    rows: List[Dict[str, Any]],
    fieldnames: Sequence[str],
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


def _fieldnames(rows: List[Dict[str, Any]]) -> List[str]:
    if not rows:
        return ["status"]
    seen = {field for row in rows for field in row}
    preferred = [
        "study_id",
        "title",
        "geography",
        "current_year",
        "current_spread_usd_mwh",
        "annual_value_usd",
        "gross_flow_mwh",
        "flow_year",
        "same_year_flow_status",
        "flow_basis",
        "same_year_flow_source",
        "active_queue_gw",
        "withdrawn_queue_gw",
        "best_intervention",
        "best_relief_value_usd",
        "best_break_even_capex_usd",
        "best_break_even_capex_usd_per_kw",
        "recommended_path",
        "next_action",
        "caveat",
        "intervention_id",
        "label",
        "solution_type",
        "capacity_mw",
        "relief_mwh",
        "relief_value_usd",
        "break_even_annual_cost_usd",
        "break_even_capex_usd",
        "break_even_capex_usd_per_kw",
        "fixed_charge_rate",
        "source",
        "notes",
        "project_id",
        "project_name",
        "effective_mwh_per_mw_year",
        "capex_usd",
        "annualized_capex_usd",
        "annual_om_usd",
        "annual_cost_usd",
        "benefit_cost_ratio",
        "net_annual_value_usd",
        "clears_congestion_value",
        "cost_method",
    ]
    return [field for field in preferred if field in seen] + sorted(seen - set(preferred))


PROJECT_COST_INPUT_FIELDS = [
    "project_id",
    "project_name",
    "geography",
    "ba_a",
    "ba_b",
    "solution_type",
    "capacity_mw",
    "effective_mwh_per_mw_year",
    "capex_usd",
    "annual_om_usd",
    "annual_cost_usd",
    "fixed_charge_rate",
    "in_service_year",
    "owner",
    "source",
    "notes",
]


PROJECT_COST_RESULT_FIELDS = [
    "study_id",
    "project_id",
    "project_name",
    "geography",
    "solution_type",
    "capacity_mw",
    "effective_mwh_per_mw_year",
    "capex_usd",
    "annualized_capex_usd",
    "annual_om_usd",
    "annual_cost_usd",
    "fixed_charge_rate",
    "relief_mwh",
    "relief_value_usd",
    "benefit_cost_ratio",
    "net_annual_value_usd",
    "clears_congestion_value",
    "cost_method",
    "source",
    "notes",
]


SAME_YEAR_FLOW_TEMPLATE_FIELDS = [
    "geography",
    "ba_a",
    "ba_b",
    "year",
    "gross_mwh",
    "net_mwh",
    "source",
    "notes",
    "current_fallback_flow_year",
    "current_fallback_gross_mwh",
    "current_status",
]
