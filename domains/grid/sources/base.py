# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Base types for grid data sources.

A source is a *section* of the plant-data presheaf: it assigns values
(net generation, emissions, ...) to the subset of plants it covers.
The EIA plant ID (ORIS code) is the shared key across eGRID, EIA-923,
EPA CEMS (via the CAMD-EIA crosswalk), and PUDL -- it is what makes
the sheaf gluing condition checkable at all.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PlantRecord:
    """One plant-year observation, normalized across datasets.

    plant_id is the EIA ORIS code as a string (e.g. "3470").
    net_generation_mwh is annual net generation in MWh.
    """

    plant_id: str
    name: str = ""
    state: str = ""
    balancing_authority: str = ""
    primary_fuel: str = ""
    net_generation_mwh: Optional[float] = None
    year: int = 0
    source: str = ""
    metadata: Dict = field(default_factory=dict)


class InMemorySource:
    """A source backed by already-loaded records.

    Used to avoid re-parsing large workbooks, and as the base for
    synthetic fixtures. Duck-types GridDataSource.
    """

    def __init__(self, name: str, records: List[PlantRecord]):
        self.name = name
        self._records = records

    def load(self) -> List[PlantRecord]:
        return self._records

    section = None  # assigned below to share GridDataSource.section


class GridDataSource(ABC):
    """A dataset that reports plant-level values.

    Subclasses implement ``load()`` returning normalized PlantRecords.
    ``section()`` exposes the source as a presheaf section: a partial
    function from plant IDs to the measured value.
    """

    #: short identifier used as the Category object name ("source:<name>")
    name: str = "abstract"

    @abstractmethod
    def load(self) -> List[PlantRecord]:
        """Load and normalize the dataset into PlantRecords."""

    def section(self) -> Dict[str, float]:
        """Plant ID -> net generation MWh, over this source's coverage.

        Plants with no reported generation are excluded (no value in
        the section, rather than a value of zero -- absence and zero
        are different statements).
        """
        return {
            rec.plant_id: rec.net_generation_mwh
            for rec in self.load()
            if rec.net_generation_mwh is not None
        }


InMemorySource.section = GridDataSource.section
