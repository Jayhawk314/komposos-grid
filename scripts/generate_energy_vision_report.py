from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

import numpy as np

sys.path.append(os.path.join(os.getcwd(), "src"))

from komposos_wesys.alignment import AlignmentRecommendation, recommend_alignment
from komposos_wesys.adapter import WesysAdapter
from komposos_wesys.core.energy_coherence import (
    GrayCategoryLayer,
    GridCategoryBuilder,
    LOSS_CLASS,
)
from komposos_wesys.geometry.grid_spectral import SpectralGraphAnalyzer


DEFAULT_INPUT = "data/external/WESyS-Model-master/wesys/data/WESyS_Default_Inputs.xlsx"
DEFAULT_OUTPUT = "reports/california_energy_vision_audit.md"
SAVINGS_PER_FACILITY = 50000.0


@dataclass(frozen=True)
class SpectralSummary:
    fiedler_value: float
    component_count: int
    status: str


@dataclass(frozen=True)
class Hotspot:
    resource: str
    technology: str
    gap_type: str
    loss_class: str
    raw_gap_count: int
    raw_exposure: float
    conservative_exposure: float
    savings_per_facility: float
    alignment: AlignmentRecommendation

    @property
    def prototype_savings(self) -> float:
        return self.conservative_exposure * self.savings_per_facility


@dataclass(frozen=True)
class AuditSummary:
    input_path: str
    sheet_names: tuple[str, ...]
    snapshot_year: str
    object_count: int
    pathway_count: int
    spectral: SpectralSummary
    raw_gap_count: int
    raw_exposure: float
    conservative_exposure: float
    savings_per_facility: float
    top_k: int
    hotspots: tuple[Hotspot, ...]

    @property
    def raw_savings(self) -> float:
        return self.raw_exposure * self.savings_per_facility

    @property
    def conservative_savings(self) -> float:
        return self.conservative_exposure * self.savings_per_facility


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a WESyS energy vision and alignment report."
    )
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--savings-per-facility", type=float, default=SAVINGS_PER_FACILITY)
    args = parser.parse_args(argv)

    summary = run_audit(
        args.input,
        savings_per_facility=args.savings_per_facility,
        top_k=args.top_k,
    )
    report = render_report(summary)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


def run_audit(
    input_path: str,
    *,
    savings_per_facility: float = SAVINGS_PER_FACILITY,
    top_k: int = 8,
) -> AuditSummary:
    adapter = WesysAdapter()
    inputs = adapter.load_wesys_scenario(input_path)
    graph = adapter.build_resource_graph()

    spectral = spectral_summary(graph)
    gaps = coherence_gaps(graph)
    hotspots = rollup_hotspots(gaps, savings_per_facility=savings_per_facility)

    raw_exposure = sum(_gap_confidence(gap) for gap in gaps)
    conservative_exposure = sum(h.conservative_exposure for h in hotspots)

    return AuditSummary(
        input_path=input_path,
        sheet_names=tuple(inputs.keys()),
        snapshot_year=_detect_snapshot_year(graph),
        object_count=len(graph.objects()),
        pathway_count=len(graph.morphisms()),
        spectral=spectral,
        raw_gap_count=len(gaps),
        raw_exposure=raw_exposure,
        conservative_exposure=conservative_exposure,
        savings_per_facility=savings_per_facility,
        top_k=top_k,
        hotspots=tuple(hotspots),
    )


def spectral_summary(graph) -> SpectralSummary:
    analyzer = SpectralGraphAnalyzer(graph)
    analyzer.build_laplacian()
    vals = np.sort(np.linalg.eigvalsh(analyzer.laplacian))
    fiedler_value = float(vals[1]) if len(vals) > 1 else 0.0
    component_count = int(np.sum(vals < 1e-10))

    if component_count > 1:
        status = f"fragmented into {component_count} components"
    elif fiedler_value > 0.1:
        status = "tightly coupled"
    else:
        status = "weakly coupled"

    return SpectralSummary(fiedler_value, component_count, status)


def coherence_gaps(graph):
    builder = GridCategoryBuilder()
    nodes = [
        {"id": obj.name, "kind": obj.type_name, "privilege": 0}
        for obj in graph.objects()
    ]
    edges = [
        {"src": m.source, "dst": m.target, "label": m.name, "confidence": m.confidence}
        for m in graph.morphisms()
    ]
    builder.from_cfg(nodes, edges)
    return GrayCategoryLayer().scan_builder(builder)


def rollup_hotspots(
    gaps: Iterable,
    *,
    savings_per_facility: float = SAVINGS_PER_FACILITY,
) -> list[Hotspot]:
    grouped = defaultdict(list)
    for gap in gaps:
        resource, technology = _resource_technology(gap.source_2cell.source_morphism)
        grouped[(resource, technology, gap.gap_type.value)].append(gap)

    hotspots = []
    for (resource, technology, gap_type), group in grouped.items():
        raw_exposure = sum(_gap_confidence(gap) for gap in group)
        conservative = max(_gap_confidence(gap) for gap in group)
        loss_class = LOSS_CLASS.get(group[0].gap_type, "unknown")
        prototype_savings = conservative * savings_per_facility
        alignment = recommend_alignment(
            resource,
            technology,
            conservative_exposure=conservative,
            prototype_savings=prototype_savings,
            gap_type=gap_type,
        )
        hotspots.append(
            Hotspot(
                resource=resource,
                technology=technology,
                gap_type=gap_type,
                loss_class=str(loss_class),
                raw_gap_count=len(group),
                raw_exposure=raw_exposure,
                conservative_exposure=conservative,
                savings_per_facility=savings_per_facility,
                alignment=alignment,
            )
        )

    hotspots.sort(
        key=lambda h: (h.prototype_savings, h.raw_gap_count, h.raw_exposure),
        reverse=True,
    )
    return hotspots


def render_report(summary: AuditSummary) -> str:
    lines = [
        "# California Energy Vision Audit",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## What This Is",
        "",
        "This report turns the WESyS audit into an energy alignment view: "
        "physical hotspots, human incentive bottlenecks, and candidate contract "
        "or constraint designs that could make repair practical.",
        "",
        "This is a prototype report. The dollar values are planning estimates, "
        "not validated savings claims.",
        "",
        "## Data Loaded",
        "",
        f"- Input workbook: `{summary.input_path}`",
        f"- Sheets: {', '.join(summary.sheet_names)}",
        f"- Snapshot year: {summary.snapshot_year}",
        f"- Resource nodes: {summary.object_count}",
        f"- Infrastructure pathways: {summary.pathway_count}",
        "",
        "## System Health",
        "",
        f"- Algebraic connectivity: {summary.spectral.fiedler_value:.4f}",
        f"- Component count: {summary.spectral.component_count}",
        f"- Status: {summary.spectral.status}",
        "",
        "Interpretation: a fragmented or weakly coupled graph suggests the model "
        "has separated energy islands. That can indicate physical fragmentation, "
        "data partitioning, or missing cross-system links that should be checked.",
        "",
        "## Coherence Findings",
        "",
        f"- Raw coherence gaps: {summary.raw_gap_count}",
        f"- Raw gap-weighted exposure: {summary.raw_exposure:.0f} facility-equivalents",
        f"- Rolled-up conservative exposure: {summary.conservative_exposure:.0f} facility-equivalents",
        f"- Raw prototype savings estimate: {_money(summary.raw_savings)} per year",
        f"- Conservative rolled-up estimate: {_money(summary.conservative_savings)} per year",
        f"- Savings assumption: {_money(summary.savings_per_facility)} per facility-equivalent per year",
        "",
        "The raw estimate counts every detected gap. The conservative estimate "
        "groups repeated findings by resource, technology, and gap type, then "
        "uses the largest facility exposure in each group. The conservative "
        "number is better for early conversations.",
        "",
        "## Priority Hotspots",
        "",
    ]

    if not summary.hotspots:
        lines.extend(["No coherence hotspots were detected.", ""])
    else:
        for index, hotspot in enumerate(summary.hotspots[: summary.top_k], 1):
            lines.extend(render_hotspot(index, hotspot))

    lines.extend(
        [
            "## Alignment Roadmap",
            "",
            "1. Validate whether each top hotspot is a physical issue, a model "
            "partition, or a missing data link.",
            "2. Identify payer, beneficiary, maintainer, regulator, and community "
            "for each hotspot.",
            "3. Choose the smallest contract design that aligns those actors.",
            "4. Add measurement before making strong savings claims.",
            "5. Feed measured outcomes back into WESyS assumptions.",
            "",
            "## Limits",
            "",
            "- Facility counts are used as prototype exposure weights.",
            "- The current coherence scan can emit repeated raw gaps for the same "
            "resource pathway.",
            "- Contract recommendations are templates, not legal advice.",
            "- Savings estimates need measured energy, maintenance, emissions, and "
            "reliability data before becoming audit-grade claims.",
            "",
            "## Next Implementation Targets",
            "",
            "- Add actor templates for LF, POTW, CAFO, utility, city, and community.",
            "- Attach actual WESyS energy units where available instead of facility "
            "count proxies.",
            "- Store measured repair outcomes and compare them with predicted value.",
            "- Produce a community-facing version that explains energy flows in plain "
            "language.",
            "",
        ]
    )
    return "\n".join(lines)


def render_hotspot(index: int, hotspot: Hotspot) -> list[str]:
    alignment = hotspot.alignment

    lines = [
        f"### {index}. {hotspot.resource} -> {hotspot.technology}",
        "",
        f"- Gap type: `{hotspot.gap_type}`",
        f"- Loss class: `{hotspot.loss_class}`",
        f"- Alignment tier: `{alignment.confidence_tier}`",
        f"- Raw repeated gaps: {hotspot.raw_gap_count}",
        f"- Raw exposure: {hotspot.raw_exposure:.0f} facility-equivalents",
        f"- Conservative exposure: {hotspot.conservative_exposure:.0f} facility-equivalents",
        f"- Conservative prototype savings: {_money(hotspot.prototype_savings)} per year",
        "",
        "Actors:",
        "",
    ]
    for actor in alignment.actors:
        lines.append(
            f"- {actor.name}: {actor.role}; interest: {actor.likely_interest}; "
            f"constraint: {actor.likely_constraint}"
        )
    lines.extend(
        [
            "",
            f"Activity diagnosis: {alignment.activity_diagnosis}",
            "",
            f"Game diagnosis: {alignment.game_diagnosis}",
            "",
            f"Contract path: {alignment.contract_path}",
            "",
            f"Constraints to design around: {alignment.constraints_text()}",
            "",
            f"Measurement needs: {alignment.measurement_text()}",
            "",
        ]
    )
    return lines


def _resource_technology(label: str) -> tuple[str, str]:
    parts = str(label).split("_", 1)
    if len(parts) == 1:
        return parts[0], "unknown"
    return parts[0], parts[1]


def _gap_confidence(gap) -> float:
    return float(getattr(gap.source_2cell, "confidence", 0.0) or 0.0)


def _detect_snapshot_year(graph) -> str:
    years = set()
    for morphism in graph.morphisms():
        metadata = getattr(morphism, "metadata", {}) or {}
        year = metadata.get("year")
        if year:
            years.add(str(year))
    return ", ".join(sorted(years)) if years else "2026"


def _money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.0f}"


if __name__ == "__main__":
    raise SystemExit(main())
