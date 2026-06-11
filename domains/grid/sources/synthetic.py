# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Synthetic plant data for tests and demos.

Generates a ground-truth fleet, then derives "datasets" from it with
controllable noise and injected contradictions -- so the coherence
checker can be validated against known-good and known-bad overlaps
before touching real federal data.
"""

from __future__ import annotations

import random
from typing import List, Tuple

from domains.grid.sources.base import InMemorySource, PlantRecord

_STATES = ["TX", "CA", "PA", "IL", "FL"]
_BAS = {"TX": "ERCO", "CA": "CISO", "PA": "PJM", "IL": "MISO", "FL": "FPL"}
_FUELS = ["GAS", "WIND", "SOLAR", "COAL", "NUCLEAR"]


class SyntheticSource(InMemorySource):
    pass


def make_fleet(n_plants: int = 50, seed: int = 7) -> List[PlantRecord]:
    rng = random.Random(seed)
    fleet = []
    for i in range(n_plants):
        state = rng.choice(_STATES)
        fleet.append(
            PlantRecord(
                plant_id=str(1000 + i),
                name=f"Plant {1000 + i}",
                state=state,
                balancing_authority=_BAS[state],
                primary_fuel=rng.choice(_FUELS),
                net_generation_mwh=rng.uniform(5_000, 2_000_000),
                year=2023,
                source="truth",
            )
        )
    return fleet


def make_synthetic_pair(
    n_plants: int = 50,
    noise: float = 0.01,
    n_contradictions: int = 3,
    overlap: float = 0.8,
    seed: int = 7,
) -> Tuple[SyntheticSource, SyntheticSource, List[str]]:
    """Two sources derived from one fleet, with known contradictions.

    Returns (source_a, source_b, contradicted_plant_ids). Source B
    covers only ``overlap`` of the fleet, carries ``noise`` relative
    measurement error, and misreports ``n_contradictions`` plants by
    a factor large enough that no tolerance setting should glue them.
    """
    rng = random.Random(seed + 1)
    fleet = make_fleet(n_plants, seed)

    a_records = [
        PlantRecord(**{**rec.__dict__, "source": "synthetic_a"}) for rec in fleet
    ]

    b_fleet = rng.sample(fleet, int(n_plants * overlap))
    contradicted = [rec.plant_id for rec in rng.sample(b_fleet, n_contradictions)]
    b_records = []
    for rec in b_fleet:
        gen = rec.net_generation_mwh * rng.uniform(1 - noise, 1 + noise)
        if rec.plant_id in contradicted:
            gen *= 3.0
        b_records.append(
            PlantRecord(
                **{**rec.__dict__, "source": "synthetic_b", "net_generation_mwh": gen}
            )
        )

    return (
        SyntheticSource("synthetic_a", a_records),
        SyntheticSource("synthetic_b", b_records),
        contradicted,
    )
