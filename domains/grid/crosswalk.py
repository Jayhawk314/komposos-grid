# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Facility crosswalk: discovered, not downloaded.

eGRID rolls some multi-block facilities into a single ORIS plant ID
while EIA-923 reports each block separately (Gila River, Mesquite,
Astoria, repowered FPL plants...). Neither eGRID's workbook nor EIA
publishes the facility-level mapping, so this module *discovers* it by
reconciliation:

For each CONTRADICT plant from the level-0 coherence check, take the
source reporting the lower value and search its residual plants --
those the other source does not cover at all, in the same state --
for the subset whose generation closes the gap. A merge is accepted
only if the merged sections glue within tolerance, so the crosswalk is
self-verifying: it can never *create* false coherence, it can only
recover gluing that the plant-ID identification broke.

Categorically: the crosswalk is a quotient map q : Plants -> Facilities,
and applying it to a section is the pushforward (left Kan extension
along q, which on discrete sites is fiberwise summation). Discovery is
intermediate-object search in the OPTIMUS sense -- find the facility
object through which both sources' reports factor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, Iterable, List, Optional, Tuple

from domains.grid.coherence import (
    CONTRADICT,
    CoherenceReport,
    Section,
    relative_discrepancy,
)
from domains.grid.ingest import plant_obj
from domains.grid.sources.base import PlantRecord

MAX_MEMBERS_PER_SEARCH = 3


@dataclass
class FacilityMerge:
    facility_id: str            # the primary plant ID (the aggregated record)
    high_source: str            # source reporting the facility as one record
    low_source: str             # source reporting it split across members
    members: List[str]          # plant IDs merged into the facility
    pre_discrepancy: float
    post_discrepancy: float


@dataclass
class FacilityCrosswalk:
    """plant_id -> facility_id quotient map, with provenance."""

    parent: Dict[str, str] = field(default_factory=dict)
    merges: List[FacilityMerge] = field(default_factory=list)

    def facility_of(self, plant_id: str) -> str:
        return self.parent.get(plant_id, plant_id)

    def apply(self, section: Section) -> Section:
        """Pushforward along the quotient: fiberwise sum onto facilities."""
        out: Dict[str, float] = {}
        for plant_id, value in section.values.items():
            fac = self.facility_of(plant_id)
            out[fac] = out.get(fac, 0.0) + value
        return Section(source=section.source, values=out)

    def apply_all(self, sections: Iterable[Section]) -> List[Section]:
        return [self.apply(s) for s in sections]


def _residual_pool(
    low_records: List[PlantRecord],
    low_section: Section,
    other_coverage: set,
    state: str,
) -> List[Tuple[str, float]]:
    """Plants the low source covers that the other source does not,
    restricted to the facility's state (unknown state matches all)."""
    pool = []
    for rec in low_records:
        if rec.plant_id in other_coverage:
            continue
        if rec.plant_id not in low_section.values:
            continue
        if state and rec.state and rec.state != state:
            continue
        pool.append((rec.plant_id, low_section.values[rec.plant_id]))
    return pool


def _best_combo(
    high_value: float,
    low_value: float,
    pool: List[Tuple[str, float]],
) -> Optional[Tuple[List[str], float]]:
    """Subset of pool minimizing post-merge discrepancy."""
    best_ids, best_disc = None, None
    for size in range(1, min(MAX_MEMBERS_PER_SEARCH, len(pool)) + 1):
        for combo in combinations(pool, size):
            merged = low_value + sum(v for _, v in combo)
            disc = relative_discrepancy(high_value, merged)
            if best_disc is None or disc < best_disc:
                best_ids = [pid for pid, _ in combo]
                best_disc = disc
    if best_ids is None:
        return None
    return best_ids, best_disc


def discover_crosswalk(
    report: CoherenceReport,
    sections: Dict[str, Section],
    records: Dict[str, List[PlantRecord]],
    tolerance: float = 0.01,
) -> FacilityCrosswalk:
    """Reconcile CONTRADICT plants into facilities.

    Greedy over contradictions in decreasing-gap order; each residual
    plant can be claimed by at most one facility. Merges that cannot
    reach ``tolerance`` are rejected -- those contradictions stand.
    """
    crosswalk = FacilityCrosswalk()
    states: Dict[str, Dict[str, str]] = {
        name: {r.plant_id: r.state for r in recs} for name, recs in records.items()
    }
    claimed: set = set()

    contradictions = [
        v for pair in report.pairs for v in pair.by_verdict(CONTRADICT)
    ]
    contradictions.sort(key=lambda v: -abs(v.value_a - v.value_b))

    for v in contradictions:
        if v.value_a >= v.value_b:
            high_src, high_val = v.source_a, v.value_a
            low_src, low_val = v.source_b, v.value_b
        else:
            high_src, high_val = v.source_b, v.value_b
            low_src, low_val = v.source_a, v.value_a

        state = states.get(high_src, {}).get(v.plant_id, "")
        pool = [
            (pid, val)
            for pid, val in _residual_pool(
                records[low_src],
                sections[low_src],
                sections[high_src].coverage,
                state,
            )
            if pid not in claimed
        ]
        found = _best_combo(high_val, low_val, pool)
        if found is None:
            continue
        member_ids, post_disc = found
        if post_disc > tolerance:
            continue  # reconciliation failed; the contradiction is real

        for pid in member_ids:
            crosswalk.parent[pid] = v.plant_id
            claimed.add(pid)
        crosswalk.merges.append(
            FacilityMerge(
                facility_id=v.plant_id,
                high_source=high_src,
                low_source=low_src,
                members=[v.plant_id] + member_ids,
                pre_discrepancy=v.discrepancy,
                post_discrepancy=post_disc,
            )
        )
    return crosswalk


def write_to_category(category, crosswalk: FacilityCrosswalk) -> None:
    """Materialize discovered facilities as categorical structure:

        plant:<member> -part_of-> facility:<primary>

    with the facility's reconciliation quality as morphism confidence.
    """
    for merge in crosswalk.merges:
        fac = f"facility:{merge.facility_id}"
        if category.get(fac) is None:
            category.add(
                fac,
                type_name="facility",
                metadata={
                    "discovered_by": "coherence_reconciliation",
                    "high_source": merge.high_source,
                    "low_source": merge.low_source,
                },
            )
        confidence = 1.0 - merge.post_discrepancy
        for pid in merge.members:
            member = plant_obj(pid)
            if category.get(member) is None:
                category.add(member, type_name="plant")
            category.connect(member, fac, name="part_of", confidence=confidence)
