from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class PredictionType(Enum):
    TYPE_CONSTRAINED = "type_constrained"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    ENSEMBLE = "ensemble"
    TRANSITIVE_CLOSURE = "transitive_closure"
    STRUCTURAL_SIMILARITY = "structural_similarity"
    COMPOSED_MORPHISM = "composed_morphism"
    CARTESIAN_LIFT = "cartesian_lift"
    FIBER_PREDICTION = "fiber_prediction"
    CURVATURE_BRIDGE = "curvature_bridge"
    STRUCTURAL_HOLE = "structural_hole"
    YONEDA_ANALOGY = "yoneda_analogy"
    GAME_THEORETIC = "game_theoretic"
    NATURALITY = "naturality"
    OPERADIC = "operadic"
    STREAMING_FORECAST = "streaming_forecast"
    TOPOLOGICAL = "topological"
    BOUNDARY = "boundary"
    CELLULAR = "cellular"
    TOPOS = "topos"
    GEOMETRIC_HOMOTOPY = "geometric_homotopy"


@dataclass(frozen=True)
class Prediction:
    source: str
    target: str
    predicted_relation: str
    prediction_type: PredictionType
    strategy_name: str
    confidence: float
    reasoning: str = ""
    evidence: Mapping[str, Any] = field(default_factory=dict)

