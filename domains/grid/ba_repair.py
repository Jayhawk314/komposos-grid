# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Candidate repair for the plant-to-BA footprint map.

The BA-level coherence check tells us *where* accounting registrations and
EIA-930 telemetry disagree. This module turns that diagnosis into an actionable
hypothesis: which plant/facility registrations could be moved from surplus BAs
to deficit BAs to reduce the mismatch while conserving total generation.

This is a proposal generator, not an authority. A proposed move means "this
registration change reduces the observed BA imbalance"; it still needs domain
review against BA footprint documents, telemetry boundaries, and plant records.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set, Tuple

from domains.grid.coherence import Section, is_valid_ba_code, pushforward
from domains.grid.ingest import plant_obj


@dataclass
class EntityMove:
    entity: str
    from_ba: str
    to_ba: str
    value_mwh: float
    improvement_mwh: float
    confidence: float
    state: str = ""


@dataclass
class BARepairReport:
    reference_source: str
    n_entities: int
    initial_abs_error_mwh: float
    repaired_abs_error_mwh: float
    remaining_delta_mwh: Dict[str, float]
    moves: List[EntityMove] = field(default_factory=list)
    skipped_entities: List[str] = field(default_factory=list)

    @property
    def improvement_mwh(self) -> float:
        return self.initial_abs_error_mwh - self.repaired_abs_error_mwh

    @property
    def improvement_rate(self) -> float:
        if self.initial_abs_error_mwh <= 0:
            return 0.0
        return self.improvement_mwh / self.initial_abs_error_mwh

    def summary(self, top: int = 10) -> str:
        lines = [
            "BA footprint repair candidates (state-footprint constrained)",
            f"  source scale: {self.reference_source}; entities considered: {self.n_entities}",
            "  absolute BA error: "
            f"{self.initial_abs_error_mwh / 1e6:,.1f} TWh -> "
            f"{self.repaired_abs_error_mwh / 1e6:,.1f} TWh "
            f"({self.improvement_rate:.1%} improvement)",
        ]
        if not self.moves:
            lines.append("  no conservative single-entity moves reduced the mismatch")
        for move in self.moves[:top]:
            state = f" ({move.state})" if move.state else ""
            lines.append(
                f"  move {move.entity}{state}: {move.from_ba} -> {move.to_ba}, "
                f"{move.value_mwh / 1e6:,.2f} TWh, "
                f"improves {move.improvement_mwh / 1e6:,.2f} TWh "
                f"(confidence {move.confidence:.2f})"
            )

        unresolved = sorted(
            self.remaining_delta_mwh.items(),
            key=lambda item: abs(item[1]),
            reverse=True,
        )
        if unresolved:
            lines.append("  largest unresolved BA deltas after proposed moves:")
            for ba, delta in unresolved[:5]:
                direction = "telemetry higher" if delta > 0 else "accounting higher"
                lines.append(f"    {ba}: {delta / 1e6:+,.2f} TWh ({direction})")
        return "\n".join(lines)


def consensus_accounting(
    sections: Iterable[Section],
    records_by_source: Dict[str, list],
    source: str = "accounting_consensus",
) -> Tuple[Section, Dict[str, str], List[str]]:
    """Average reconciled plant/facility values and choose a consensus BA map."""
    values: Dict[str, List[float]] = defaultdict(list)
    ba_votes: Dict[str, List[str]] = defaultdict(list)

    for section in sections:
        for entity, value in section.values.items():
            values[entity].append(value)

        by_id = {
            rec.plant_id: str(rec.balancing_authority).strip()
            for rec in records_by_source.get(section.source, [])
            if is_valid_ba_code(rec.balancing_authority)
        }
        for entity in section.values:
            ba = by_id.get(entity)
            if ba:
                ba_votes[entity].append(ba)

    consensus_values = {
        entity: sum(entity_values) / len(entity_values)
        for entity, entity_values in values.items()
    }
    mapping: Dict[str, str] = {}
    conflicts: List[str] = []
    for entity, votes in ba_votes.items():
        counts = Counter(votes)
        winner, _ = counts.most_common(1)[0]
        mapping[entity] = winner
        if len(counts) > 1:
            conflicts.append(entity)

    return Section(source=source, values=consensus_values), mapping, conflicts


def consensus_entity_states(
    sections: Iterable[Section],
    records_by_source: Dict[str, list],
    entity_to_ba: Dict[str, str],
) -> Tuple[Dict[str, str], Dict[str, Set[str]]]:
    """Choose consensus entity states and derive each BA's state footprint."""
    state_votes: Dict[str, List[str]] = defaultdict(list)
    entities = set()
    for section in sections:
        entities.update(section.values)
        by_id = {
            rec.plant_id: rec.state
            for rec in records_by_source.get(section.source, [])
            if rec.state and rec.state != "nan"
        }
        for entity in section.values:
            state = by_id.get(entity)
            if state:
                state_votes[entity].append(state)

    entity_state: Dict[str, str] = {}
    ba_states: Dict[str, Set[str]] = defaultdict(set)
    for entity in entities:
        votes = state_votes.get(entity, [])
        if not votes:
            continue
        state = Counter(votes).most_common(1)[0][0]
        entity_state[entity] = state
        ba = entity_to_ba.get(entity)
        if ba:
            ba_states[ba].add(state)
    return entity_state, dict(ba_states)


def propose_ba_footprint_repair(
    telemetry: Section,
    accounting: Section,
    entity_to_ba: Dict[str, str],
    entity_state: Dict[str, str] | None = None,
    ba_states: Dict[str, Set[str]] | None = None,
    tolerance: float = 0.05,
    min_entity_mwh: float = 10_000.0,
    max_moves: int = 25,
) -> BARepairReport:
    """Greedily propose entity moves that reduce BA-level absolute error.

    Delta convention: telemetry - accounting. Positive means telemetry sees
    more generation than registered accounting assigns to the BA; negative
    means accounting has surplus generation registered to that BA.
    """
    accounting_ba = pushforward(accounting, entity_to_ba, source=f"{accounting.source}@ba")
    bas = telemetry.coverage | accounting_ba.coverage
    delta = {
        ba: telemetry.values.get(ba, 0.0) - accounting_ba.values.get(ba, 0.0)
        for ba in bas
    }

    initial_error = sum(abs(v) for v in delta.values())
    candidate_entities = [
        (entity, entity_to_ba[entity], value)
        for entity, value in accounting.values.items()
        if entity in entity_to_ba and abs(value) >= min_entity_mwh and value > 0
    ]
    moved: set[str] = set()
    moves: List[EntityMove] = []

    def active_surplus(ba: str) -> bool:
        scale = max(abs(telemetry.values.get(ba, 0.0)), abs(accounting_ba.values.get(ba, 0.0)))
        return delta.get(ba, 0.0) < -max(tolerance * scale, min_entity_mwh)

    def active_deficit(ba: str) -> bool:
        scale = max(abs(telemetry.values.get(ba, 0.0)), abs(accounting_ba.values.get(ba, 0.0)))
        return delta.get(ba, 0.0) > max(tolerance * scale, min_entity_mwh)

    def target_state_allows(entity: str, to_ba: str) -> bool:
        if entity_state is None or ba_states is None:
            return True
        state = entity_state.get(entity)
        if not state:
            return False
        return state in ba_states.get(to_ba, set())

    for _ in range(max_moves):
        deficits = [ba for ba in bas if active_deficit(ba)]
        if not deficits:
            break

        best: EntityMove | None = None
        for entity, from_ba, value in candidate_entities:
            if entity in moved or not active_surplus(from_ba):
                continue
            old_from = abs(delta[from_ba])
            for to_ba in deficits:
                if to_ba == from_ba:
                    continue
                if not target_state_allows(entity, to_ba):
                    continue
                old_to = abs(delta[to_ba])
                new_from = abs(delta[from_ba] + value)
                new_to = abs(delta[to_ba] - value)
                improvement = (old_from + old_to) - (new_from + new_to)
                if improvement <= 0:
                    continue
                confidence = min(1.0, improvement / (2.0 * value))
                candidate = EntityMove(
                    entity=entity,
                    from_ba=from_ba,
                    to_ba=to_ba,
                    value_mwh=value,
                    improvement_mwh=improvement,
                    confidence=confidence,
                    state=(entity_state or {}).get(entity, ""),
                )
                if best is None or candidate.improvement_mwh > best.improvement_mwh:
                    best = candidate

        if best is None:
            break
        moves.append(best)
        moved.add(best.entity)
        delta[best.from_ba] += best.value_mwh
        delta[best.to_ba] -= best.value_mwh

    repaired_error = sum(abs(v) for v in delta.values())
    skipped = sorted(set(accounting.values) - set(entity_to_ba))
    return BARepairReport(
        reference_source=accounting.source,
        n_entities=len(candidate_entities),
        initial_abs_error_mwh=initial_error,
        repaired_abs_error_mwh=repaired_error,
        remaining_delta_mwh=dict(sorted(delta.items())),
        moves=moves,
        skipped_entities=skipped,
    )


def write_repair_to_category(category, report: BARepairReport) -> None:
    """Write proposed footprint corrections back as reviewable morphisms."""
    for move in report.moves:
        src = plant_obj(move.entity)
        dst = f"ba:{move.to_ba}"
        if category.get(src) is None:
            category.add(src, type_name="plant")
        if category.get(dst) is None:
            category.add(dst, type_name="balancing_authority")
        category.connect(
            src,
            dst,
            name="footprint_candidate",
            confidence=move.confidence,
            from_ba=move.from_ba,
            state=move.state,
            value_mwh=move.value_mwh,
            improvement_mwh=move.improvement_mwh,
            evidence_source=report.reference_source,
        )
