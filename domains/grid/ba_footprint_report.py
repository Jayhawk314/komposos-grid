# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Audience-facing before/after report for BA footprint corrections."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from domains.grid.ba_footprint_crosswalk import BAFootprintCrosswalk
from domains.grid.coherence import (
    CONTRADICT,
    CoherenceReport,
    GridCoherenceChecker,
    Section,
    pushforward,
)
from domains.grid.sheaf_audit import GridSheafAudit, sheaf_audit


@dataclass
class BAFootprintReport:
    """Before/after evidence for a validated BA footprint crosswalk."""

    telemetry: Section
    accounting: Section
    before_section: Section
    after_section: Section
    crosswalk: BAFootprintCrosswalk
    before_coherence: CoherenceReport
    after_coherence: CoherenceReport
    before_sheaf: GridSheafAudit
    after_sheaf: GridSheafAudit

    @property
    def before_contradictions(self) -> int:
        return _contradiction_count(self.before_coherence)

    @property
    def after_contradictions(self) -> int:
        return _contradiction_count(self.after_coherence)

    @property
    def contradiction_reduction(self) -> int:
        return self.before_contradictions - self.after_contradictions

    @property
    def before_agreement_rate(self) -> float:
        return _agreement_rate(self.before_coherence)

    @property
    def after_agreement_rate(self) -> float:
        return _agreement_rate(self.after_coherence)

    def unresolved_deltas(self, top: int = 10) -> List[tuple[str, float]]:
        return sorted(
            self.crosswalk.after_score.deltas_mwh.items(),
            key=lambda item: abs(item[1]),
            reverse=True,
        )[:top]

    def summary(self) -> str:
        return (
            "BA footprint proof report\n"
            f"  accepted corrections: {len(self.crosswalk.accepted)}\n"
            f"  BA agreement: {self.before_agreement_rate:.1%} -> "
            f"{self.after_agreement_rate:.1%}\n"
            f"  contradictions: {self.before_contradictions} -> "
            f"{self.after_contradictions} "
            f"({self.contradiction_reduction} resolved)\n"
            f"  absolute BA error: "
            f"{self.crosswalk.before_score.abs_error_mwh / 1e6:,.1f} TWh -> "
            f"{self.crosswalk.after_score.abs_error_mwh / 1e6:,.1f} TWh\n"
            f"  sheaf H^1 leak: {self.before_sheaf.energy_leak:.3e} -> "
            f"{self.after_sheaf.energy_leak:.3e}"
        )

    def to_markdown(self, top: int = 10) -> str:
        lines = [
            "# BA Footprint Correction Report",
            "",
            "## Result",
            "",
            f"- Accepted corrections: **{len(self.crosswalk.accepted)}**",
            f"- Rejected candidates: **{len(self.crosswalk.rejected)}**",
            f"- BA agreement: **{self.before_agreement_rate:.1%} -> "
            f"{self.after_agreement_rate:.1%}**",
            f"- BA contradictions: **{self.before_contradictions} -> "
            f"{self.after_contradictions}**",
            f"- Absolute BA error: **{self.crosswalk.before_score.abs_error_mwh / 1e6:,.1f} "
            f"TWh -> {self.crosswalk.after_score.abs_error_mwh / 1e6:,.1f} TWh**",
            f"- Sheaf H^1 leak: **{self.before_sheaf.energy_leak:.3e} -> "
            f"{self.after_sheaf.energy_leak:.3e}**",
            "",
            "## Accepted Corrections",
            "",
            "| Entity | State | From BA | To BA | MWh | Improvement MWh | Confidence |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        if not self.crosswalk.accepted:
            lines.append("| None |  |  |  |  |  |  |")
        for validated in self.crosswalk.accepted[:top]:
            move = validated.move
            lines.append(
                f"| {move.entity} | {move.state} | {move.from_ba} | {move.to_ba} | "
                f"{move.value_mwh:,.0f} | {validated.improvement_mwh:,.0f} | "
                f"{move.confidence:.2f} |"
            )

        lines.extend([
            "",
            "## Rejected Candidates",
            "",
            "| Entity | From BA | To BA | Reason |",
            "|---|---:|---:|---|",
        ])
        if not self.crosswalk.rejected:
            lines.append("| None |  |  |  |")
        for validated in self.crosswalk.rejected[:top]:
            move = validated.move
            lines.append(
                f"| {move.entity} | {move.from_ba} | {move.to_ba} | "
                f"{'; '.join(validated.reasons)} |"
            )

        lines.extend([
            "",
            "## Remaining Largest BA Deltas",
            "",
            "| BA | Delta MWh | Interpretation |",
            "|---|---:|---|",
        ])
        for ba, delta in self.unresolved_deltas(top):
            interpretation = "telemetry higher" if delta > 0 else "accounting higher"
            lines.append(f"| {ba} | {delta:,.0f} | {interpretation} |")
        return "\n".join(lines) + "\n"

    def to_dict(self, top: int = 25) -> Dict[str, Any]:
        return {
            "telemetry_source": self.telemetry.source,
            "accounting_source": self.accounting.source,
            "accepted_corrections": len(self.crosswalk.accepted),
            "rejected_candidates": len(self.crosswalk.rejected),
            "before": {
                "agreement_rate": self.before_agreement_rate,
                "contradictions": self.before_contradictions,
                "abs_error_mwh": self.crosswalk.before_score.abs_error_mwh,
                "outside_tolerance": self.crosswalk.before_score.outside_tolerance,
                "sheaf_energy_leak": self.before_sheaf.energy_leak,
            },
            "after": {
                "agreement_rate": self.after_agreement_rate,
                "contradictions": self.after_contradictions,
                "abs_error_mwh": self.crosswalk.after_score.abs_error_mwh,
                "outside_tolerance": self.crosswalk.after_score.outside_tolerance,
                "sheaf_energy_leak": self.after_sheaf.energy_leak,
            },
            "accepted": [
                _validated_payload(validated)
                for validated in self.crosswalk.accepted[:top]
            ],
            "rejected": [
                _validated_payload(validated)
                for validated in self.crosswalk.rejected[:top]
            ],
            "unresolved_deltas_mwh": [
                {"ba": ba, "delta_mwh": delta}
                for ba, delta in self.unresolved_deltas(top)
            ],
        }

    def export_markdown(self, path: str | Path, top: int = 10) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(top=top), encoding="utf-8")

    def export_json(self, path: str | Path, top: int = 25) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(top=top), indent=2), encoding="utf-8")


def build_ba_footprint_report(
    telemetry: Section,
    accounting: Section,
    base_mapping: Dict[str, str],
    crosswalk: BAFootprintCrosswalk,
    tolerance: float = 0.05,
) -> BAFootprintReport:
    before_section = pushforward(
        accounting,
        base_mapping,
        source=f"{accounting.source}@registered_ba",
    )
    after_section = crosswalk.apply(
        accounting,
        base_mapping,
        source=f"{accounting.source}@footprint_ba",
    )
    checker = GridCoherenceChecker(tolerance=tolerance)
    before_coherence = checker.check([telemetry, before_section])
    after_coherence = checker.check([telemetry, after_section])
    before_sheaf = sheaf_audit([telemetry, before_section])
    after_sheaf = sheaf_audit([telemetry, after_section])

    return BAFootprintReport(
        telemetry=telemetry,
        accounting=accounting,
        before_section=before_section,
        after_section=after_section,
        crosswalk=crosswalk,
        before_coherence=before_coherence,
        after_coherence=after_coherence,
        before_sheaf=before_sheaf,
        after_sheaf=after_sheaf,
    )


def _contradiction_count(report: CoherenceReport) -> int:
    return sum(len(pair.by_verdict(CONTRADICT)) for pair in report.pairs)


def _agreement_rate(report: CoherenceReport) -> float:
    if not report.pairs:
        return 1.0
    weighted = sum(pair.agreement_rate * pair.overlap_size for pair in report.pairs)
    total = sum(pair.overlap_size for pair in report.pairs)
    return weighted / total if total else 1.0


def _validated_payload(validated) -> Dict[str, Any]:
    move = validated.move
    return {
        "entity": move.entity,
        "state": move.state,
        "from_ba": move.from_ba,
        "to_ba": move.to_ba,
        "value_mwh": move.value_mwh,
        "confidence": move.confidence,
        "candidate_improvement_mwh": move.improvement_mwh,
        "validated_improvement_mwh": validated.improvement_mwh,
        "reasons": validated.reasons,
    }
