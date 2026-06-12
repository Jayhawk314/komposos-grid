# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Dual-Engine (ZFC + CAT) verification of plant->BA assignments.

The level-2 coherence check found that accounting datasets and EIA-930
telemetry disagree identically for ~11 BAs, implicating the plant->BA
*assignment functor* (registration vs metered footprint) rather than
the measurements. This module submits that structural claim to the
ZFC/CAT dual engine (zfc/bridge.py):

- **registered query**  (plant, registered_ba, "in_ba"): is the recorded
  assignment logically entailed (ZFC) and compositionally supported (CAT)?
- **counterfactual query** (plant, neighbor_ba, "in_ba"): with interchange
  ties present, does the structure also support the plant sitting in an
  adjacent BA's footprint? For a crisp assignment the counterfactual
  should find no support; "leaky" assignments admit it.

Verdicts use the bridge's delta classification (AGREE / ORPHAN /
HOLLOW / REJECT), and every query is recorded as a System 3 episode,
so the engine *learns* the disputed-territory pattern.

The verification category is a focused subgraph (disputed + control
BAs, sampled plants, optional BA-BA ties) so the ZFC universe stays
small and queries stay fast.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence

from core.category import Category
from zfc.bridge import DualEngineBridge
from zfc.store_adapter import StoreAdapter

from domains.grid.flow_geometry import TieLine
from domains.grid.sources.base import PlantRecord

# BAs the level-2 check found in identical accounting-vs-telemetry
# contradiction (2023). Override via the runner's --disputed.
DISPUTED_BAS_2023 = [
    "CPLW", "WAUW", "GRID", "WALC", "GCPD", "PGE", "PSEI", "PACW", "SPA", "HST",
]
# Large ISOs whose BA sections glued: the statistical control group.
CONTROL_BAS = ["ERCO", "CISO", "PJM", "MISO", "ISNE"]


def build_verification_category(
    records: Iterable[PlantRecord],
    bas: Sequence[str],
    ties: Optional[List[TieLine]] = None,
    max_plants_per_ba: int = 25,
    seed: int = 11,
    db_path: str = ":memory:",
) -> Category:
    """Focused subgraph: sampled plants of the named BAs (+ optional ties)."""
    rng = random.Random(seed)
    by_ba: Dict[str, List[PlantRecord]] = {ba: [] for ba in bas}
    for rec in records:
        if rec.balancing_authority in by_ba:
            by_ba[rec.balancing_authority].append(rec)

    # Full-fleet generation per BA (before sampling): the physical scale
    # against which tie flows are measured.
    ba_generation = {
        ba: sum(r.net_generation_mwh or 0.0 for r in recs)
        for ba, recs in by_ba.items()
    }

    category = Category(name="grid_verify", db_path=db_path)
    for ba, recs in by_ba.items():
        if len(recs) > max_plants_per_ba:
            recs = rng.sample(recs, max_plants_per_ba)
        for rec in recs:
            category.connect(
                f"plant:{rec.plant_id}", f"ba:{ba}", name="in_ba", confidence=1.0
            )

    if ties:
        names = {f"ba:{ba}" for ba in bas}
        for t in ties:
            a, b = f"ba:{t.ba_a}", f"ba:{t.ba_b}"
            if a not in names or b not in names:
                continue
            # Directed tie confidence = the fraction of the source BA's own
            # generation the tie could carry away. ~1 means the BA's entire
            # output could sit in the neighbor's metered footprint (the
            # registration-vs-footprint signature); ~0 means the tie is
            # negligible against the BA's size.
            for src, tgt, src_code in ((a, b, t.ba_a), (b, a, t.ba_b)):
                gen = ba_generation.get(src_code, 0.0)
                conf = min(1.0, t.gross_mwh / gen) if gen > 0 else 1.0
                category.connect(
                    src, tgt, name="interchange",
                    confidence=max(conf, 1e-3), gross_mwh=t.gross_mwh,
                )
    return category


@dataclass
class BAVerification:
    ba: str
    group: str                       # "disputed" or "control"
    n_plants: int
    registered_deltas: Dict[str, int] = field(default_factory=dict)
    counterfactual_weight: float = 0.0  # summed enriched path weights
    counterfactual_total: int = 0

    @property
    def leakiness(self) -> float:
        """Mean enriched weight of counterfactual assignment paths.

        The weight of plant -> registered_ba -> neighbor under the
        quantale is conf(in_ba) * conf(interchange); with flow-scaled
        tie confidences this measures how much of the BA's output the
        structure permits to sit in a neighbor's footprint.
        """
        if not self.counterfactual_total:
            return 0.0
        return self.counterfactual_weight / self.counterfactual_total


@dataclass
class VerificationReport:
    results: List[BAVerification]
    n_episodes: int
    system3_report: str

    def group_leakiness(self, group: str) -> float:
        rows = [r for r in self.results if r.group == group and r.counterfactual_total]
        if not rows:
            return 0.0
        return sum(r.leakiness for r in rows) / len(rows)

    def summary(self) -> str:
        lines = ["Dual-Engine verification of plant->BA assignments"]
        for group in ("disputed", "control"):
            rows = [r for r in self.results if r.group == group]
            lines.append(f"  {group} BAs:")
            for r in rows:
                deltas = ", ".join(
                    f"{k}:{v}" for k, v in sorted(r.registered_deltas.items())
                )
                lines.append(
                    f"    {r.ba}: {r.n_plants} plants, registered [{deltas}], "
                    f"counterfactual leakiness {r.leakiness:.0%} "
                    f"({r.counterfactual_total} paths)"
                )
            lines.append(
                f"  -> mean counterfactual leakiness ({group}): "
                f"{self.group_leakiness(group):.0%}"
            )
        lines.append(f"  System 3: {self.n_episodes} episodes recorded")
        return "\n".join(lines)


def verify_assignments(
    category: Category,
    disputed: Sequence[str],
    control: Sequence[str],
    queries_per_ba: int = 10,
    seed: int = 13,
) -> VerificationReport:
    rng = random.Random(seed)
    bridge = DualEngineBridge(StoreAdapter(category), category=category)

    ba_neighbors: Dict[str, List[tuple]] = {}
    for mor in category.morphisms():
        if mor.name == "interchange":
            ba_neighbors.setdefault(mor.source, []).append(
                (mor.target, mor.confidence)
            )
    # Strongest ties first: those are the footprint-leak candidates
    for nbrs in ba_neighbors.values():
        nbrs.sort(key=lambda tc: -tc[1])

    results: List[BAVerification] = []
    n_episodes = 0
    for group, bas in (("disputed", disputed), ("control", control)):
        for ba in bas:
            ba_obj = f"ba:{ba}"
            plants = [
                m.source for m in category.morphisms_to(ba_obj) if m.name == "in_ba"
            ]
            if not plants:
                continue
            sample = (
                rng.sample(plants, queries_per_ba)
                if len(plants) > queries_per_ba
                else plants
            )
            row = BAVerification(ba=ba, group=group, n_plants=len(plants))

            for plant in sample:
                res = bridge.query(plant, ba_obj, "in_ba", domain="grid")
                n_episodes += 1
                key = res.delta_type.name
                row.registered_deltas[key] = row.registered_deltas.get(key, 0) + 1

                for neighbor, tie_conf in ba_neighbors.get(ba_obj, [])[:2]:
                    cf = bridge.query(plant, neighbor, "in_ba", domain="grid")
                    n_episodes += 1
                    row.counterfactual_total += 1
                    if cf.cat_says:
                        # enriched path weight: in_ba (1.0) x flow-scaled tie
                        row.counterfactual_weight += tie_conf
            results.append(row)

    return VerificationReport(
        results=results,
        n_episodes=n_episodes,
        system3_report=str(bridge.system3_report()),
    )
