"""
KOMPOSOS-III Geometry Layer

Implements geometric analysis of knowledge graphs using:
- Ollivier-Ricci curvature for local geometry detection
- Discrete Ricci flow for structure revelation
- Thurston-style geometric decomposition

Key insight: Different regions of a knowledge graph have different
natural geometries (hyperbolic for hierarchies, spherical for clusters,
euclidean for chains). This layer reveals that structure.
"""

from .ricci import (
    OllivierRicciCurvature,
    CurvatureResult,
    GeometryType,
    compute_graph_curvature,
)

from .flow import (
    DiscreteRicciFlow,
    DecompositionResult,
    GeometricRegion,
    FlowStep,
    run_ricci_flow,
)

__all__ = [
    # Curvature
    "OllivierRicciCurvature",
    "CurvatureResult",
    "GeometryType",
    "compute_graph_curvature",
    # Ricci Flow
    "DiscreteRicciFlow",
    "DecompositionResult",
    "GeometricRegion",
    "FlowStep",
    "run_ricci_flow",
]
