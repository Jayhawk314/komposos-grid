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
from domains.grid.ba_repair import BARepairReport, EntityMove
from domains.grid.ba_footprint_crosswalk import BAFootprintCrosswalk, BAErrorScore
from domains.grid.ba_footprint_report import BAFootprintReport
from domains.grid.ba_review import BAFootprintReview, ReviewDecision, ReviewedMove
from domains.grid.ba_dashboard import (
    export_footprint_report_html,
    export_review_html,
)
from domains.grid.flow_report import FlowBottleneckReport, FlowBottleneck
from domains.grid.congestion_evidence import (
    CongestionEvidenceReport,
    CongestionEvidence,
    CongestionClaim,
)
from domains.grid.outages import OutageReport
from domains.grid.waste_ledger import WasteLedger, WasteClaim
from domains.grid.action_portfolio import ActionPortfolio, PortfolioAction
from domains.grid.ingest import GridCategoryBuilder
from domains.grid.sources.base import GridDataSource, PlantRecord

__all__ = [
    "GridCoherenceChecker",
    "CoherenceReport",
    "Section",
    "BARepairReport",
    "EntityMove",
    "BAFootprintCrosswalk",
    "BAErrorScore",
    "BAFootprintReport",
    "BAFootprintReview",
    "ReviewDecision",
    "ReviewedMove",
    "export_footprint_report_html",
    "export_review_html",
    "FlowBottleneckReport",
    "FlowBottleneck",
    "CongestionEvidenceReport",
    "CongestionEvidence",
    "CongestionClaim",
    "OutageReport",
    "WasteLedger",
    "WasteClaim",
    "ActionPortfolio",
    "PortfolioAction",
    "GridCategoryBuilder",
    "GridDataSource",
    "PlantRecord",
]
