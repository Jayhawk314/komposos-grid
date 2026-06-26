# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Flow geometry and curvature bottleneck analysis for the nuclear domain.

Uses Ollivier-Ricci curvature to find structural supply bottlenecks,
and spectral Fiedler seams to analyze capacity coupling or regulatory boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
from core.category import Category
from komposos_wesys.geometry.grid_ricci import OllivierRicciCurvature
from komposos_wesys.geometry.grid_spectral import SpectralGraphAnalyzer


class CategoryStoreAdapter:
    """Bridges Category to the expected geometry engine structure interface."""

    def __init__(self, category: Category):
        self.category = category

    def list_morphisms(self, limit: int = 100000):
        from types import SimpleNamespace
        return [
            SimpleNamespace(
                source_name=m.source, target_name=m.target, confidence=1.0
            )
            for m in self.category.morphisms()[:limit]
        ]


@dataclass
class EnrichmentGeometryReport:
    num_nodes: int
    num_edges: int
    edge_curvatures: List[Tuple[str, str, float]]  # source, target, curvature
    fiedler_value: float
    partition: Tuple[List[str], List[str]]


def analyze_enrichment_geometry(category: Category) -> EnrichmentGeometryReport:
    """Computes Ricci curvature and Fiedler partition on the nuclear category."""
    # 1. Ricci Curvature
    adapter = CategoryStoreAdapter(category)
    ricci = OllivierRicciCurvature(adapter, alpha=0.5)
    curvatures = ricci.compute_all_curvatures()

    edges_out = []
    seen = set()
    for (u, v), kappa in curvatures.edge_curvatures.items():
        key = frozenset((u, v))
        if key not in seen:
            seen.add(key)
            edges_out.append((u, v, kappa))

    # Sort bottlenecks: negative curvature first (most constrained)
    edges_out.sort(key=lambda x: x[2])

    # 2. Spectral Analysis
    spectral = SpectralGraphAnalyzer(category)
    spectral.build_laplacian()
    eigenvalues, eigenvectors = spectral.compute_spectrum()
    coupling = spectral.analyze_coupling()

    fiedler_val = float(coupling.get("algebraic_connectivity", 0.0))

    # Reconstruct Fiedler Partition
    fiedler_vec = eigenvectors[:, 1] if eigenvectors.shape[1] > 1 else eigenvectors[:, 0]
    names = list(spectral.node_names)
    neg_nodes = [names[i] for i, val in enumerate(fiedler_vec) if val < 0]
    pos_nodes = [names[i] for i, val in enumerate(fiedler_vec) if val >= 0]
    partition = (neg_nodes, pos_nodes)

    return EnrichmentGeometryReport(
        num_nodes=len(category.objects()),
        num_edges=len(category.morphisms()),
        edge_curvatures=edges_out,
        fiedler_value=fiedler_val,
        partition=partition,
    )
