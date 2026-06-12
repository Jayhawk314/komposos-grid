# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""OPTIMUS factorization of interconnection queue outcomes.

Every queue project is a morphism  queue:proposed -> outcome, and the
direct morphism  proposed -> operational  carries the overall completion
rate (~13%) as its hom-value. OPTIMUS's categorical gradient asks:
through which intermediate object does this morphism factor with higher
confidence?

    proposed --1.0--> cohort:B --P(operational | B, decided)--> operational

A cohort (fuel type, region, entry era, size class, IA milestone) whose
conditional completion rate beats the direct rate is a discovered
intermediate -- the observable that mediates completion. The dual run
against outcome:withdrawn finds what mediates failure.

Honesty notes:
- rates are computed over *decided* projects only (operational or
  withdrawn); active/suspended projects are censored, not failures.
- cohorts below ``min_cohort`` decided projects carry no morphism, so
  OPTIMUS cannot factor through statistical noise.
- a discovered intermediate is descriptive mediation, not causation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from core.category import Category
from core.optimus import OptimusEngine

from domains.grid.sources.lbnl_queue import OPERATIONAL, WITHDRAWN, QueueProject

PROPOSED = "queue:proposed"
OP = "outcome:operational"
WD = "outcome:withdrawn"


def _era(year: Optional[int]) -> Optional[str]:
    if year is None:
        return None
    if year < 2010:
        return "pre2010"
    if year < 2015:
        return "2010_2014"
    if year < 2020:
        return "2015_2019"
    return "2020_plus"


def _size(mw: Optional[float]) -> Optional[str]:
    if mw is None:
        return None
    if mw < 50:
        return "lt50mw"
    if mw < 200:
        return "50_200mw"
    if mw < 500:
        return "200_500mw"
    return "gt500mw"


def _cohorts(p: QueueProject) -> List[str]:
    out = [f"fuel:{p.fuel}", f"region:{p.region}"]
    era = _era(p.q_year)
    if era:
        out.append(f"era:{era}")
    size = _size(p.mw)
    if size:
        out.append(f"size:{size}")
    if p.ia_status:
        out.append(f"ia:{p.ia_status}")
    return out


def build_queue_category(
    projects: List[QueueProject],
    min_cohort: int = 30,
    db_path: str = ":memory:",
) -> Category:
    decided = [p for p in projects if p.decided]
    if not decided:
        raise ValueError("no decided (operational/withdrawn) projects")

    tally: Dict[str, Tuple[int, int]] = {}  # cohort -> (n_decided, n_operational)
    for p in decided:
        for cohort in _cohorts(p):
            n, ops = tally.get(cohort, (0, 0))
            tally[cohort] = (n + 1, ops + (1 if p.status == OPERATIONAL else 0))

    category = Category(name="queue", db_path=db_path)
    overall = sum(1 for p in decided if p.status == OPERATIONAL) / len(decided)
    category.connect(PROPOSED, OP, name="completes",
                     confidence=max(overall, 1e-6), n=len(decided))
    category.connect(PROPOSED, WD, name="withdraws",
                     confidence=max(1 - overall, 1e-6), n=len(decided))

    for cohort, (n, ops) in tally.items():
        if n < min_cohort:
            continue
        rate = ops / n
        category.connect(PROPOSED, cohort, name="has_attribute", confidence=1.0)
        category.connect(cohort, OP, name="completes",
                         confidence=max(rate, 1e-6), n=n)
        category.connect(cohort, WD, name="withdraws",
                         confidence=max(1 - rate, 1e-6), n=n)
    return category


@dataclass
class QueueFactorization:
    overall_completion: float
    n_decided: int
    operational_intermediates: List[Tuple[str, float, int]]  # cohort, rate, n
    withdrawal_intermediates: List[Tuple[str, float, int]]
    optimus_discovered_op: List[str]
    optimus_discovered_wd: List[str]

    def summary(self, top: int = 8) -> str:
        lines = [
            f"Queue factorization: {self.n_decided} decided projects, "
            f"overall completion {self.overall_completion:.1%}",
            "  OPTIMUS intermediates for proposed -> operational "
            f"(direct w={self.overall_completion:.3f}):",
        ]
        for cohort, rate, n in self.operational_intermediates[:top]:
            flag = " *" if cohort in self.optimus_discovered_op else ""
            lines.append(
                f"    {cohort}: completion {rate:.1%} "
                f"({rate / self.overall_completion:.1f}x direct, n={n}){flag}"
            )
        lines.append("  OPTIMUS intermediates for proposed -> withdrawn:")
        for cohort, rate, n in self.withdrawal_intermediates[:top]:
            flag = " *" if cohort in self.optimus_discovered_wd else ""
            lines.append(
                f"    {cohort}: withdrawal {rate:.1%} (n={n}){flag}"
            )
        lines.append("  (* = surfaced by OptimusEngine.discover_intermediates)")
        return "\n".join(lines)


def analyze_queue(
    projects: List[QueueProject],
    min_cohort: int = 30,
    category: Optional[Category] = None,
) -> QueueFactorization:
    category = category or build_queue_category(projects, min_cohort=min_cohort)
    engine = OptimusEngine(category, max_depth=2)

    discovered_op = engine.discover_intermediates(PROPOSED, OP, depth=2)
    discovered_wd = engine.discover_intermediates(PROPOSED, WD, depth=2)

    def rates_to(outcome: str, name: str):
        rows = []
        for mor in category.morphisms_to(outcome):
            if mor.name != name or mor.source == PROPOSED:
                continue
            rows.append(
                (mor.source, mor.confidence, int(mor.metadata.get("n", 0)))
            )
        rows.sort(key=lambda r: -r[1])
        return rows

    direct = next(
        m for m in category.morphisms_to(OP)
        if m.source == PROPOSED and m.name == "completes"
    )

    return QueueFactorization(
        overall_completion=direct.confidence,
        n_decided=int(direct.metadata.get("n", 0)),
        operational_intermediates=rates_to(OP, "completes"),
        withdrawal_intermediates=rates_to(WD, "withdraws"),
        optimus_discovered_op=list(discovered_op),
        optimus_discovered_wd=list(discovered_wd),
    )
