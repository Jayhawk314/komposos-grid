# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Validated crosswalk for plant/facility registrations to BA footprints."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

from domains.grid.ba_repair import BARepairReport, EntityMove
from domains.grid.coherence import Section, pushforward, relative_discrepancy
from domains.grid.ingest import plant_obj


@dataclass
class BAErrorScore:
    """Error between BA telemetry and accounting pushed through a BA map."""

    tolerance: float
    deltas_mwh: Dict[str, float]
    abs_error_mwh: float
    max_abs_delta_mwh: float
    outside_tolerance: int

    @property
    def n_bas(self) -> int:
        return len(self.deltas_mwh)

    def summary(self) -> str:
        return (
            f"{self.abs_error_mwh / 1e6:,.1f} TWh absolute error across "
            f"{self.n_bas} BAs; {self.outside_tolerance} outside "
            f"{self.tolerance:.1%} tolerance"
        )


@dataclass
class ValidatedMove:
    move: EntityMove
    accepted: bool
    reasons: List[str]
    before_abs_error_mwh: float
    after_abs_error_mwh: float
    improvement_mwh: float


@dataclass
class BAFootprintCrosswalk:
    """Accepted BA footprint corrections plus rejected review candidates."""

    source_report: BARepairReport
    before_score: BAErrorScore
    after_score: BAErrorScore
    accepted: List[ValidatedMove] = field(default_factory=list)
    rejected: List[ValidatedMove] = field(default_factory=list)

    @property
    def moves(self) -> List[EntityMove]:
        return [validated.move for validated in self.accepted]

    @property
    def improvement_mwh(self) -> float:
        return self.before_score.abs_error_mwh - self.after_score.abs_error_mwh

    @property
    def improvement_rate(self) -> float:
        if self.before_score.abs_error_mwh <= 0:
            return 0.0
        return self.improvement_mwh / self.before_score.abs_error_mwh

    def apply_mapping(self, base_mapping: Dict[str, str]) -> Dict[str, str]:
        mapping = dict(base_mapping)
        for move in self.moves:
            mapping[move.entity] = move.to_ba
        return mapping

    def apply(
        self,
        section: Section,
        base_mapping: Dict[str, str],
        source: str | None = None,
    ) -> Section:
        return pushforward(
            section,
            self.apply_mapping(base_mapping),
            source=source or f"{section.source}@ba_footprint",
        )

    def summary(self, top: int = 10) -> str:
        lines = [
            "Validated BA footprint crosswalk",
            f"  accepted {len(self.accepted)} of "
            f"{len(self.accepted) + len(self.rejected)} candidate moves",
            "  before: " + self.before_score.summary(),
            "  after : " + self.after_score.summary(),
            f"  improvement: {self.improvement_mwh / 1e6:,.1f} TWh "
            f"({self.improvement_rate:.1%})",
        ]
        for validated in self.accepted[:top]:
            move = validated.move
            state = f" ({move.state})" if move.state else ""
            lines.append(
                f"  accept {move.entity}{state}: {move.from_ba} -> {move.to_ba}, "
                f"{move.value_mwh / 1e6:,.2f} TWh, "
                f"local improvement {validated.improvement_mwh / 1e6:,.2f} TWh"
            )
        if self.rejected:
            lines.append("  rejected examples:")
            for validated in self.rejected[: min(5, top)]:
                move = validated.move
                lines.append(
                    f"    reject {move.entity}: {move.from_ba} -> {move.to_ba} "
                    f"({'; '.join(validated.reasons)})"
                )
        return "\n".join(lines)

    def to_rows(
        self,
        records_by_source: Dict[str, list] | None = None,
        sections: Iterable[Section] | None = None,
    ) -> List[Dict[str, Any]]:
        names = _entity_names(records_by_source or {})
        source_values = _source_values(sections or [])
        rows: List[Dict[str, Any]] = []
        for status, items in (("accepted", self.accepted), ("rejected", self.rejected)):
            for validated in items:
                move = validated.move
                row: Dict[str, Any] = {
                    "status": status,
                    "entity": move.entity,
                    "name": names.get(move.entity, ""),
                    "state": move.state,
                    "from_ba": move.from_ba,
                    "to_ba": move.to_ba,
                    "value_mwh": move.value_mwh,
                    "candidate_improvement_mwh": move.improvement_mwh,
                    "validated_improvement_mwh": validated.improvement_mwh,
                    "confidence": move.confidence,
                    "before_abs_error_mwh": validated.before_abs_error_mwh,
                    "after_abs_error_mwh": validated.after_abs_error_mwh,
                    "reasons": "; ".join(validated.reasons),
                }
                for source, values in source_values.items():
                    row[f"{source}_mwh"] = values.get(move.entity, "")
                rows.append(row)
        return rows

    def export_csv(
        self,
        path: str | Path,
        records_by_source: Dict[str, list] | None = None,
        sections: Iterable[Section] | None = None,
    ) -> None:
        rows = self.to_rows(records_by_source, sections)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        base_fields = [
            "status",
            "entity",
            "name",
            "state",
            "from_ba",
            "to_ba",
            "value_mwh",
            "candidate_improvement_mwh",
            "validated_improvement_mwh",
            "confidence",
            "before_abs_error_mwh",
            "after_abs_error_mwh",
            "reasons",
        ]
        extra_fields = sorted(
            {key for row in rows for key in row if key not in base_fields}
        )
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=base_fields + extra_fields)
            writer.writeheader()
            writer.writerows(rows)

    def export_json(
        self,
        path: str | Path,
        records_by_source: Dict[str, list] | None = None,
        sections: Iterable[Section] | None = None,
    ) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "before": _score_payload(self.before_score),
            "after": _score_payload(self.after_score),
            "improvement_mwh": self.improvement_mwh,
            "improvement_rate": self.improvement_rate,
            "candidates": self.to_rows(records_by_source, sections),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def score_ba_mapping(
    telemetry: Section,
    accounting: Section,
    entity_to_ba: Dict[str, str],
    tolerance: float = 0.05,
) -> BAErrorScore:
    accounting_ba = pushforward(accounting, entity_to_ba, source=f"{accounting.source}@ba")
    bas = telemetry.coverage | accounting_ba.coverage
    deltas = {
        ba: telemetry.values.get(ba, 0.0) - accounting_ba.values.get(ba, 0.0)
        for ba in sorted(bas)
    }
    outside = sum(
        1
        for ba in bas
        if relative_discrepancy(
            telemetry.values.get(ba, 0.0),
            accounting_ba.values.get(ba, 0.0),
        )
        > tolerance
    )
    return BAErrorScore(
        tolerance=tolerance,
        deltas_mwh=deltas,
        abs_error_mwh=sum(abs(v) for v in deltas.values()),
        max_abs_delta_mwh=max((abs(v) for v in deltas.values()), default=0.0),
        outside_tolerance=outside,
    )


def build_ba_footprint_crosswalk(
    report: BARepairReport,
    telemetry: Section,
    accounting: Section,
    entity_to_ba: Dict[str, str],
    entity_state: Dict[str, str] | None = None,
    ba_states: Dict[str, Set[str]] | None = None,
    interchange_neighbors: Dict[str, Set[str]] | None = None,
    tolerance: float = 0.05,
    min_confidence: float = 0.25,
    min_improvement_mwh: float = 0.0,
) -> BAFootprintCrosswalk:
    """Promote repair candidates into a validated crosswalk."""
    base_mapping = dict(entity_to_ba)
    current_mapping = dict(entity_to_ba)
    before_score = score_ba_mapping(telemetry, accounting, base_mapping, tolerance)
    accepted: List[ValidatedMove] = []
    rejected: List[ValidatedMove] = []

    for move in report.moves:
        validation = _validate_move(
            move=move,
            telemetry=telemetry,
            accounting=accounting,
            current_mapping=current_mapping,
            entity_state=entity_state or {},
            ba_states=ba_states or {},
            interchange_neighbors=interchange_neighbors,
            tolerance=tolerance,
            min_confidence=min_confidence,
            min_improvement_mwh=min_improvement_mwh,
        )
        if validation.accepted:
            current_mapping[move.entity] = move.to_ba
            accepted.append(validation)
        else:
            rejected.append(validation)

    after_score = score_ba_mapping(telemetry, accounting, current_mapping, tolerance)
    return BAFootprintCrosswalk(
        source_report=report,
        before_score=before_score,
        after_score=after_score,
        accepted=accepted,
        rejected=rejected,
    )


def write_crosswalk_to_category(category, crosswalk: BAFootprintCrosswalk) -> None:
    """Write accepted footprint corrections back to the Category."""
    for validated in crosswalk.accepted:
        move = validated.move
        src = plant_obj(move.entity)
        dst = f"ba:{move.to_ba}"
        if category.get(src) is None:
            category.add(src, type_name="plant")
        if category.get(dst) is None:
            category.add(dst, type_name="balancing_authority")
        category.connect(
            src,
            dst,
            name="footprint_correction",
            confidence=move.confidence,
            from_ba=move.from_ba,
            state=move.state,
            value_mwh=move.value_mwh,
            candidate_improvement_mwh=move.improvement_mwh,
            validated_improvement_mwh=validated.improvement_mwh,
            before_abs_error_mwh=validated.before_abs_error_mwh,
            after_abs_error_mwh=validated.after_abs_error_mwh,
            evidence_source=crosswalk.source_report.reference_source,
        )


def interchange_neighbors_from_ties(ties: Iterable[Any]) -> Dict[str, Set[str]]:
    """Build BA adjacency from EIA-930 interchange tie records."""
    neighbors: Dict[str, Set[str]] = {}
    for tie in ties:
        a = getattr(tie, "ba_a")
        b = getattr(tie, "ba_b")
        neighbors.setdefault(a, set()).add(b)
        neighbors.setdefault(b, set()).add(a)
    return neighbors


def _validate_move(
    move: EntityMove,
    telemetry: Section,
    accounting: Section,
    current_mapping: Dict[str, str],
    entity_state: Dict[str, str],
    ba_states: Dict[str, Set[str]],
    interchange_neighbors: Dict[str, Set[str]] | None,
    tolerance: float,
    min_confidence: float,
    min_improvement_mwh: float,
) -> ValidatedMove:
    reasons: List[str] = []
    before = score_ba_mapping(telemetry, accounting, current_mapping, tolerance)
    trial_mapping = dict(current_mapping)

    if move.entity not in accounting.values:
        reasons.append("entity missing from accounting section")
    if move.entity not in current_mapping:
        reasons.append("entity missing from BA mapping")
    elif current_mapping[move.entity] != move.from_ba:
        reasons.append(
            f"current BA is {current_mapping[move.entity]}, not candidate source {move.from_ba}"
        )
    if move.confidence < min_confidence:
        reasons.append(f"confidence below {min_confidence:.2f}")

    state = move.state or entity_state.get(move.entity, "")
    if entity_state or ba_states:
        if not state:
            reasons.append("missing entity state")
        elif state not in ba_states.get(move.to_ba, set()):
            reasons.append(f"target BA has no observed {state} footprint")

    if interchange_neighbors is not None:
        neighbors = interchange_neighbors.get(move.from_ba, set())
        if move.to_ba not in neighbors and move.from_ba != move.to_ba:
            reasons.append("source and target BAs lack observed interchange tie")

    if not reasons:
        trial_mapping[move.entity] = move.to_ba
    after = score_ba_mapping(telemetry, accounting, trial_mapping, tolerance)
    improvement = before.abs_error_mwh - after.abs_error_mwh
    if not reasons and improvement <= min_improvement_mwh:
        reasons.append("does not improve validated BA score")

    accepted = not reasons
    return ValidatedMove(
        move=move,
        accepted=accepted,
        reasons=["accepted"] if accepted else reasons,
        before_abs_error_mwh=before.abs_error_mwh,
        after_abs_error_mwh=after.abs_error_mwh,
        improvement_mwh=improvement if accepted else 0.0,
    )


def _entity_names(records_by_source: Dict[str, list]) -> Dict[str, str]:
    names: Dict[str, str] = {}
    for records in records_by_source.values():
        for rec in records:
            if rec.name and rec.plant_id not in names:
                names[rec.plant_id] = rec.name
    return names


def _source_values(sections: Iterable[Section]) -> Dict[str, Dict[str, float]]:
    return {section.source: dict(section.values) for section in sections}


def _score_payload(score: BAErrorScore) -> Dict[str, Any]:
    return {
        "tolerance": score.tolerance,
        "abs_error_mwh": score.abs_error_mwh,
        "max_abs_delta_mwh": score.max_abs_delta_mwh,
        "outside_tolerance": score.outside_tolerance,
        "deltas_mwh": score.deltas_mwh,
    }
