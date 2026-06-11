# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Sheaf coherence check for grid data sources.

Sheaf-theoretic framing
-----------------------
Take the discrete site whose points are plants (EIA ORIS codes). Each
dataset is a section of the net-generation presheaf over the subset of
plants it covers. The gluing condition -- sections agree on overlaps --
is the precise statement of "these datasets describe the same grid".

Level 0 (this module): pairwise overlap agreement at plant granularity.
Level 1 (planned, eia930): aggregate plant sections along the
plant -> balancing-authority functor (a pushforward / left Kan
extension along the projection) and compare against EIA-930's
BA-level sections. Disagreement *there* but not at level 0 localizes
the incoherence to the aggregation map itself (plant<->BA assignment
errors), not the measurements.

Verdicts per overlapping plant, by relative discrepancy:
    GLUE      <= tolerance          sections agree; gluable
    TENSION   <= 5x tolerance       known adjustments live here (CHP,
                                    station use, net-vs-gross)
    CONTRADICT > 5x tolerance       at least one source is wrong

When a Category is supplied, results are written back as structure:
    source:A -coheres_with-> source:B   confidence = agreement rate
    source:A -disputes-> plant:X        confidence = discrepancy, for
                                        every CONTRADICT plant
so downstream layers (COG verification, OPTIMUS refinement) see data
quality as hom-values, not as a side report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from domains.grid.ingest import plant_obj, source_obj

GLUE = "GLUE"
TENSION = "TENSION"
CONTRADICT = "CONTRADICT"


@dataclass
class Section:
    """A data source viewed as a presheaf section over its coverage."""

    source: str
    values: Dict[str, float]

    @property
    def coverage(self) -> set:
        return set(self.values)


@dataclass
class PlantVerdict:
    plant_id: str
    source_a: str
    source_b: str
    value_a: float
    value_b: float
    discrepancy: float
    verdict: str


@dataclass
class PairResult:
    source_a: str
    source_b: str
    overlap_size: int
    agreement_rate: float
    verdicts: List[PlantVerdict] = field(default_factory=list)

    def by_verdict(self, verdict: str) -> List[PlantVerdict]:
        return [v for v in self.verdicts if v.verdict == verdict]


@dataclass
class CoherenceReport:
    sections: Dict[str, int]            # source -> coverage size
    pairs: List[PairResult]
    tolerance: float

    @property
    def is_coherent(self) -> bool:
        return all(not p.by_verdict(CONTRADICT) for p in self.pairs)

    def summary(self) -> str:
        lines = [
            f"Sheaf coherence report (tolerance {self.tolerance:.1%})",
            "Sections: "
            + ", ".join(f"{s} ({n} plants)" for s, n in self.sections.items()),
        ]
        for p in self.pairs:
            n_glue = len(p.by_verdict(GLUE))
            n_tension = len(p.by_verdict(TENSION))
            contradictions = p.by_verdict(CONTRADICT)
            lines.append(
                f"  {p.source_a} x {p.source_b}: overlap {p.overlap_size}, "
                f"agreement {p.agreement_rate:.1%} "
                f"(glue {n_glue}, tension {n_tension}, contradict {len(contradictions)})"
            )
            for v in sorted(contradictions, key=lambda v: -v.discrepancy)[:10]:
                lines.append(
                    f"    CONTRADICT plant {v.plant_id}: "
                    f"{v.source_a}={v.value_a:,.0f} MWh vs "
                    f"{v.source_b}={v.value_b:,.0f} MWh "
                    f"(discrepancy {v.discrepancy:.1%})"
                )
        lines.append(
            "VERDICT: " + ("coherent -- sections glue" if self.is_coherent
                           else "INCOHERENT -- contradictions found")
        )
        return "\n".join(lines)


def relative_discrepancy(a: float, b: float) -> float:
    scale = max(abs(a), abs(b))
    if scale == 0:
        return 0.0
    return abs(a - b) / scale


class GridCoherenceChecker:
    """Pairwise gluing check over plant-keyed sections.

    tolerance is the relative discrepancy under which two reported
    values count as "the same measurement". 1% is strict; eGRID is
    derived from EIA-923, so their overlap should mostly GLUE, with
    TENSION concentrated in CHP/station-use adjusted plants.
    """

    def __init__(self, category=None, tolerance: float = 0.01):
        self.category = category
        self.tolerance = tolerance

    def check(self, sections: List[Section]) -> CoherenceReport:
        pairs: List[PairResult] = []
        for i in range(len(sections)):
            for j in range(i + 1, len(sections)):
                pairs.append(self._check_pair(sections[i], sections[j]))

        report = CoherenceReport(
            sections={s.source: len(s.values) for s in sections},
            pairs=pairs,
            tolerance=self.tolerance,
        )
        if self.category is not None:
            self._write_back(report)
        return report

    def _check_pair(self, sec_a: Section, sec_b: Section) -> PairResult:
        overlap = sec_a.coverage & sec_b.coverage
        verdicts: List[PlantVerdict] = []
        for plant_id in overlap:
            a, b = sec_a.values[plant_id], sec_b.values[plant_id]
            disc = relative_discrepancy(a, b)
            if disc <= self.tolerance:
                verdict = GLUE
            elif disc <= 5 * self.tolerance:
                verdict = TENSION
            else:
                verdict = CONTRADICT
            verdicts.append(
                PlantVerdict(
                    plant_id=plant_id,
                    source_a=sec_a.source,
                    source_b=sec_b.source,
                    value_a=a,
                    value_b=b,
                    discrepancy=disc,
                    verdict=verdict,
                )
            )
        n = len(verdicts)
        agreement = (
            sum(1 for v in verdicts if v.verdict == GLUE) / n if n else 1.0
        )
        return PairResult(
            source_a=sec_a.source,
            source_b=sec_b.source,
            overlap_size=n,
            agreement_rate=agreement,
            verdicts=verdicts,
        )

    def _write_back(self, report: CoherenceReport) -> None:
        for pair in report.pairs:
            src_a, src_b = source_obj(pair.source_a), source_obj(pair.source_b)
            self.category.connect(
                src_a,
                src_b,
                name="coheres_with",
                confidence=pair.agreement_rate,
                overlap=pair.overlap_size,
            )
            for v in pair.by_verdict(CONTRADICT):
                self.category.connect(
                    src_a,
                    plant_obj(v.plant_id),
                    name="disputes",
                    confidence=min(v.discrepancy, 1.0),
                    other_source=pair.source_b,
                    value_a=v.value_a,
                    value_b=v.value_b,
                )


def sections_from_sources(sources) -> List[Section]:
    return [Section(source=s.name, values=s.section()) for s in sources]


def sections_from_records(records: Dict[str, list]) -> List[Section]:
    """Build sections from pre-loaded PlantRecords (one parse per workbook)."""
    return [
        Section(
            source=name,
            values={
                r.plant_id: r.net_generation_mwh
                for r in recs
                if r.net_generation_mwh is not None
            },
        )
        for name, recs in records.items()
    ]
