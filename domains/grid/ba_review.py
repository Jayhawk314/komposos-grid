# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Human review workflow for BA footprint correction hypotheses."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from domains.grid.ba_footprint_crosswalk import (
    BAFootprintCrosswalk,
    ValidatedMove,
    score_ba_mapping,
)
from domains.grid.coherence import Section
from domains.grid.ingest import plant_obj


REVIEW_ACCEPTED = "accepted"
REVIEW_REJECTED = "rejected"
REVIEW_NEEDS_REVIEW = "needs_review"
REVIEW_STATUSES = {REVIEW_ACCEPTED, REVIEW_REJECTED, REVIEW_NEEDS_REVIEW}


@dataclass(frozen=True)
class ReviewDecision:
    """A reviewer decision for one proposed BA footprint move."""

    entity: str
    from_ba: str
    to_ba: str
    status: str = REVIEW_NEEDS_REVIEW
    reviewer: str = ""
    note: str = ""
    evidence: str = ""

    def __post_init__(self) -> None:
        normalized = normalize_review_status(self.status)
        object.__setattr__(self, "status", normalized)
        if normalized not in REVIEW_STATUSES:
            allowed = ", ".join(sorted(REVIEW_STATUSES))
            raise ValueError(f"unknown review status {self.status!r}; expected {allowed}")

    @property
    def key(self) -> str:
        return review_key(self.entity, self.from_ba, self.to_ba)


@dataclass
class ReviewedMove:
    """A machine-validated candidate plus its reviewer decision."""

    validated: ValidatedMove
    decision: ReviewDecision
    applied: bool
    review_reasons: List[str] = field(default_factory=list)


@dataclass
class BAFootprintReview:
    """Curated review result and approved crosswalk."""

    source_crosswalk: BAFootprintCrosswalk
    curated_crosswalk: BAFootprintCrosswalk
    reviewed: List[ReviewedMove]

    @property
    def approved(self) -> List[ReviewedMove]:
        return [item for item in self.reviewed if item.applied]

    @property
    def rejected(self) -> List[ReviewedMove]:
        return [
            item
            for item in self.reviewed
            if item.decision.status == REVIEW_REJECTED and not item.applied
        ]

    @property
    def needs_review(self) -> List[ReviewedMove]:
        return [
            item
            for item in self.reviewed
            if item.decision.status == REVIEW_NEEDS_REVIEW or item.review_reasons
        ]

    @property
    def improvement_mwh(self) -> float:
        return (
            self.curated_crosswalk.before_score.abs_error_mwh
            - self.curated_crosswalk.after_score.abs_error_mwh
        )

    @property
    def improvement_rate(self) -> float:
        before = self.curated_crosswalk.before_score.abs_error_mwh
        return self.improvement_mwh / before if before > 0 else 0.0

    def summary(self, top: int = 10) -> str:
        lines = [
            "BA footprint correction review",
            f"  approved {len(self.approved)} of {len(self.reviewed)} candidates; "
            f"{len(self.rejected)} rejected; {len(self.needs_review)} need review",
            "  before: " + self.curated_crosswalk.before_score.summary(),
            "  machine after: " + self.source_crosswalk.after_score.summary(),
            "  reviewed after: " + self.curated_crosswalk.after_score.summary(),
            f"  reviewed improvement: {self.improvement_mwh / 1e6:,.1f} TWh "
            f"({self.improvement_rate:.1%})",
        ]
        for item in self.approved[:top]:
            move = item.validated.move
            reviewer = f", reviewer {item.decision.reviewer}" if item.decision.reviewer else ""
            lines.append(
                f"  approve {move.entity}: {move.from_ba} -> {move.to_ba}, "
                f"{move.value_mwh / 1e6:,.2f} TWh{reviewer}"
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
        for item in self.reviewed:
            validated = item.validated
            move = validated.move
            row: Dict[str, Any] = {
                "entity": move.entity,
                "name": names.get(move.entity, ""),
                "state": move.state,
                "from_ba": move.from_ba,
                "to_ba": move.to_ba,
                "machine_status": "accepted" if validated.accepted else "rejected",
                "machine_reasons": "; ".join(validated.reasons),
                "review_status": item.decision.status,
                "applied": str(item.applied).lower(),
                "reviewer": item.decision.reviewer,
                "review_note": item.decision.note,
                "review_evidence": item.decision.evidence,
                "review_reasons": "; ".join(item.review_reasons),
                "value_mwh": move.value_mwh,
                "candidate_improvement_mwh": move.improvement_mwh,
                "validated_improvement_mwh": validated.improvement_mwh,
                "confidence": move.confidence,
                "before_abs_error_mwh": validated.before_abs_error_mwh,
                "after_abs_error_mwh": validated.after_abs_error_mwh,
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
        _write_csv(path, self.to_rows(records_by_source, sections))

    def export_json(
        self,
        path: str | Path,
        records_by_source: Dict[str, list] | None = None,
        sections: Iterable[Section] | None = None,
    ) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "before": _score_payload(self.curated_crosswalk.before_score),
            "machine_after": _score_payload(self.source_crosswalk.after_score),
            "reviewed_after": _score_payload(self.curated_crosswalk.after_score),
            "approved": len(self.approved),
            "rejected": len(self.rejected),
            "needs_review": len(self.needs_review),
            "reviewed_improvement_mwh": self.improvement_mwh,
            "reviewed_improvement_rate": self.improvement_rate,
            "candidates": self.to_rows(records_by_source, sections),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def review_key(entity: str, from_ba: str, to_ba: str) -> str:
    return f"{entity}|{from_ba}|{to_ba}"


def normalize_review_status(status: str | None) -> str:
    value = (status or REVIEW_NEEDS_REVIEW).strip().lower().replace("-", "_")
    aliases = {
        "": REVIEW_NEEDS_REVIEW,
        "approve": REVIEW_ACCEPTED,
        "approved": REVIEW_ACCEPTED,
        "accept": REVIEW_ACCEPTED,
        "accepted": REVIEW_ACCEPTED,
        "reject": REVIEW_REJECTED,
        "rejected": REVIEW_REJECTED,
        "decline": REVIEW_REJECTED,
        "needs review": REVIEW_NEEDS_REVIEW,
        "needs_review": REVIEW_NEEDS_REVIEW,
        "review": REVIEW_NEEDS_REVIEW,
        "defer": REVIEW_NEEDS_REVIEW,
        "deferred": REVIEW_NEEDS_REVIEW,
    }
    return aliases.get(value, value)


def review_template_rows(
    crosswalk: BAFootprintCrosswalk,
    records_by_source: Dict[str, list] | None = None,
    sections: Iterable[Section] | None = None,
) -> List[Dict[str, Any]]:
    """Return editable review rows for a validated BA footprint crosswalk."""
    rows: List[Dict[str, Any]] = []
    for row in crosswalk.to_rows(records_by_source, sections):
        machine_status = str(row.pop("status"))
        machine_reasons = str(row.pop("reasons"))
        row = {
            "review_status": (
                REVIEW_NEEDS_REVIEW
                if machine_status == "accepted"
                else REVIEW_REJECTED
            ),
            "reviewer": "",
            "review_note": "",
            "review_evidence": "",
            "machine_status": machine_status,
            "machine_reasons": machine_reasons,
            **row,
        }
        rows.append(row)
    return rows


def export_review_template_csv(
    crosswalk: BAFootprintCrosswalk,
    path: str | Path,
    records_by_source: Dict[str, list] | None = None,
    sections: Iterable[Section] | None = None,
) -> None:
    _write_csv(path, review_template_rows(crosswalk, records_by_source, sections))


def export_review_template_json(
    crosswalk: BAFootprintCrosswalk,
    path: str | Path,
    records_by_source: Dict[str, list] | None = None,
    sections: Iterable[Section] | None = None,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "instructions": (
            "Set review_status to accepted, rejected, or needs_review. "
            "Only accepted rows are applied to the curated BA crosswalk."
        ),
        "candidates": review_template_rows(crosswalk, records_by_source, sections),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_review_decisions(path: str | Path) -> Dict[str, ReviewDecision]:
    """Load review decisions from a CSV or JSON review template."""
    path = Path(path)
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            rows = (
                payload.get("decisions")
                or payload.get("candidates")
                or payload.get("rows")
                or []
            )
        else:
            rows = payload
    else:
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

    decisions: Dict[str, ReviewDecision] = {}
    for row in rows:
        decision = decision_from_row(row)
        if decision.key in decisions:
            raise ValueError(f"duplicate review decision for {decision.key}")
        decisions[decision.key] = decision
    return decisions


def decision_from_row(row: Mapping[str, Any]) -> ReviewDecision:
    status = row.get("review_status")
    if status is None and row.get("status") in REVIEW_STATUSES:
        status = row.get("status")
    return ReviewDecision(
        entity=str(row.get("entity", "")).strip(),
        from_ba=str(row.get("from_ba", "")).strip(),
        to_ba=str(row.get("to_ba", "")).strip(),
        status=str(status or REVIEW_NEEDS_REVIEW),
        reviewer=str(row.get("reviewer", "") or "").strip(),
        note=str(row.get("review_note", row.get("note", "")) or "").strip(),
        evidence=str(row.get("review_evidence", row.get("evidence", "")) or "").strip(),
    )


def apply_review_decisions(
    crosswalk: BAFootprintCrosswalk,
    decisions: Mapping[str, ReviewDecision] | Iterable[ReviewDecision],
    telemetry: Section,
    accounting: Section,
    entity_to_ba: Dict[str, str],
    tolerance: float = 0.05,
    allow_machine_rejected: bool = False,
) -> BAFootprintReview:
    """Apply reviewer decisions and return the curated crosswalk."""
    decision_map = _decision_map(decisions)
    reviewed: List[ReviewedMove] = []
    approved: List[ValidatedMove] = []

    for validated in _all_validated_moves(crosswalk):
        move = validated.move
        decision = decision_map.get(
            review_key(move.entity, move.from_ba, move.to_ba),
            _default_decision(validated),
        )
        reasons: List[str] = []
        applied = False
        if decision.status == REVIEW_ACCEPTED:
            if validated.accepted or allow_machine_rejected:
                applied = True
                approved.append(validated)
            else:
                reasons.append("machine-rejected candidate needs override evidence")
        elif decision.status == REVIEW_NEEDS_REVIEW:
            reasons.append("awaiting reviewer approval")

        reviewed.append(
            ReviewedMove(
                validated=validated,
                decision=decision,
                applied=applied,
                review_reasons=reasons,
            )
        )

    reviewed_mapping = dict(entity_to_ba)
    for item in reviewed:
        if item.applied:
            move = item.validated.move
            reviewed_mapping[move.entity] = move.to_ba

    reviewed_after = score_ba_mapping(
        telemetry,
        accounting,
        reviewed_mapping,
        tolerance=tolerance,
    )
    rejected = [item.validated for item in reviewed if not item.applied]
    curated = BAFootprintCrosswalk(
        source_report=crosswalk.source_report,
        before_score=crosswalk.before_score,
        after_score=reviewed_after,
        accepted=approved,
        rejected=rejected,
    )
    return BAFootprintReview(
        source_crosswalk=crosswalk,
        curated_crosswalk=curated,
        reviewed=reviewed,
    )


def write_review_to_category(category, review: BAFootprintReview) -> None:
    """Write reviewer decisions back to the Category as explicit evidence."""
    for item in review.reviewed:
        move = item.validated.move
        src = plant_obj(move.entity)
        dst = f"ba:{move.to_ba}"
        if category.get(src) is None:
            category.add(src, type_name="plant")
        if category.get(dst) is None:
            category.add(dst, type_name="balancing_authority")
        category.connect(
            src,
            dst,
            name=(
                "reviewed_footprint_correction"
                if item.applied
                else "footprint_review"
            ),
            confidence=move.confidence,
            from_ba=move.from_ba,
            state=move.state,
            value_mwh=move.value_mwh,
            candidate_improvement_mwh=move.improvement_mwh,
            validated_improvement_mwh=item.validated.improvement_mwh,
            machine_status="accepted" if item.validated.accepted else "rejected",
            machine_reasons="; ".join(item.validated.reasons),
            review_status=item.decision.status,
            review_reasons="; ".join(item.review_reasons),
            reviewer=item.decision.reviewer,
            review_note=item.decision.note,
            review_evidence=item.decision.evidence,
            applied=item.applied,
        )


def _all_validated_moves(crosswalk: BAFootprintCrosswalk) -> List[ValidatedMove]:
    return list(crosswalk.accepted) + list(crosswalk.rejected)


def _default_decision(validated: ValidatedMove) -> ReviewDecision:
    move = validated.move
    return ReviewDecision(
        entity=move.entity,
        from_ba=move.from_ba,
        to_ba=move.to_ba,
        status=REVIEW_NEEDS_REVIEW if validated.accepted else REVIEW_REJECTED,
    )


def _decision_map(
    decisions: Mapping[str, ReviewDecision] | Iterable[ReviewDecision],
) -> Dict[str, ReviewDecision]:
    if isinstance(decisions, Mapping):
        return dict(decisions)
    return {decision.key: decision for decision in decisions}


def _write_csv(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = _ordered_fields(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _ordered_fields(rows: List[Dict[str, Any]]) -> List[str]:
    preferred = [
        "review_status",
        "applied",
        "reviewer",
        "review_note",
        "review_evidence",
        "review_reasons",
        "machine_status",
        "machine_reasons",
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
    ]
    seen = {field for row in rows for field in row}
    return [field for field in preferred if field in seen] + sorted(seen - set(preferred))


def _entity_names(records_by_source: Dict[str, list]) -> Dict[str, str]:
    names: Dict[str, str] = {}
    for records in records_by_source.values():
        for rec in records:
            if getattr(rec, "name", "") and rec.plant_id not in names:
                names[rec.plant_id] = rec.name
    return names


def _source_values(sections: Iterable[Section]) -> Dict[str, Dict[str, float]]:
    return {section.source: dict(section.values) for section in sections}


def _score_payload(score) -> Dict[str, Any]:
    return {
        "tolerance": score.tolerance,
        "abs_error_mwh": score.abs_error_mwh,
        "max_abs_delta_mwh": score.max_abs_delta_mwh,
        "outside_tolerance": score.outside_tolerance,
        "deltas_mwh": score.deltas_mwh,
    }
