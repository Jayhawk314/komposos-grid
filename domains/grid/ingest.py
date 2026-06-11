# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Build a KOMPOSOS-IV Category from grid data sources.

Object naming convention (one namespace per type):
    plant:<oris_id>     type_name="plant"
    ba:<code>           type_name="balancing_authority"
    state:<abbrev>      type_name="state"
    fuel:<category>     type_name="fuel"
    source:<name>       type_name="data_source"

Morphisms:
    plant -in_ba-> ba                 structural membership
    plant -in_state-> state           structural membership
    plant -uses_fuel-> fuel           structural attribute
    source -reports-> plant           provenance; confidence 1.0 at ingest,
                                      downgraded later by the coherence check

This layout makes Yoneda fingerprints meaningful: two plants with the
same hom-pattern (same BA, fuel, coverage by the same sources) are
interchangeable for inference, which is what absorb()/transfer relies on.
"""

from __future__ import annotations

from typing import Dict, Iterable

from core.category import Category

from domains.grid.sources.base import GridDataSource


def plant_obj(plant_id: str) -> str:
    return f"plant:{plant_id}"


def source_obj(source_name: str) -> str:
    return f"source:{source_name}"


class GridCategoryBuilder:
    def __init__(self, category: Category):
        self.category = category

    def _ensure(self, name: str, type_name: str, **metadata) -> None:
        if self.category.get(name) is None:
            self.category.add(name, type_name=type_name, metadata=metadata)

    def add_source(self, source: GridDataSource) -> Dict[str, int]:
        """Ingest one data source. Returns counts for reporting."""
        src = source_obj(source.name)
        self._ensure(src, "data_source")

        n_plants = n_morphisms = 0
        for rec in source.load():
            plant = plant_obj(rec.plant_id)
            if self.category.get(plant) is None:
                self.category.add(
                    plant,
                    type_name="plant",
                    metadata={"name": rec.name, "year": rec.year},
                )
                n_plants += 1
                if rec.balancing_authority and rec.balancing_authority != "nan":
                    ba = f"ba:{rec.balancing_authority}"
                    self._ensure(ba, "balancing_authority")
                    self.category.connect(plant, ba, name="in_ba")
                    n_morphisms += 1
                if rec.state and rec.state != "nan":
                    st = f"state:{rec.state}"
                    self._ensure(st, "state")
                    self.category.connect(plant, st, name="in_state")
                    n_morphisms += 1
                if rec.primary_fuel and rec.primary_fuel != "nan":
                    fuel = f"fuel:{rec.primary_fuel}"
                    self._ensure(fuel, "fuel")
                    self.category.connect(plant, fuel, name="uses_fuel")
                    n_morphisms += 1

            self.category.connect(
                src,
                plant,
                name="reports",
                confidence=1.0,
                net_generation_mwh=rec.net_generation_mwh,
            )
            n_morphisms += 1

        return {"plants_created": n_plants, "morphisms": n_morphisms}

    def add_sources(self, sources: Iterable[GridDataSource]) -> Dict[str, Dict[str, int]]:
        return {s.name: self.add_source(s) for s in sources}
