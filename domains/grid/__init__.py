# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""KOMPOSOS-IV grid domain: categorical analysis of US electrical grid waste.

Three waste bottlenecks drive the domain design:

1. **Curtailment** -- excess renewable energy discarded when the grid
   cannot absorb or store it.
2. **T&D losses** -- energy dissipating as heat through structural
   inefficiency, phase imbalance, and congestion.
3. **Peaker reliance** -- inefficient fossil plants firing to cover
   demand spikes that better-aligned flexible load could absorb.

Before any optimization, the data itself must cohere: each dataset
(eGRID, EIA-923, CEMS, EIA-930, ...) is a *section* over the set of
plants it covers, and the sheaf gluing condition -- sections agree on
overlaps -- is the categorical statement of "the data is trustworthy".
That check is the first runnable artifact of this domain.

See ``domains/grid/README.md`` and ``sources/registry.py`` for the
dataset-to-waste-problem map.
"""

from domains.grid.coherence import GridCoherenceChecker, CoherenceReport, Section
from domains.grid.ingest import GridCategoryBuilder
from domains.grid.sources.base import GridDataSource, PlantRecord

__all__ = [
    "GridCoherenceChecker",
    "CoherenceReport",
    "Section",
    "GridCategoryBuilder",
    "GridDataSource",
    "PlantRecord",
]
