# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Civilian Nuclear Enrichment and Fuel Cycle Domain.

This package uses standard categorical and flow geometry tools to model
capacities, bottlenecks, and logistics claims in the civilian nuclear
fuel cycle supply chain.
"""

from domains.nuclear.ingest import NuclearCategoryBuilder
from domains.nuclear.flow_geometry import analyze_enrichment_geometry

__all__ = [
    "NuclearCategoryBuilder",
    "analyze_enrichment_geometry",
]
