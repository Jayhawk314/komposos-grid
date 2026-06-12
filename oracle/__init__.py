"""Lightweight categorical oracle compatibility package."""

from .prediction import Prediction, PredictionType
from .strategies import FibrationLiftStrategy, create_all_strategies


class CategoricalOracle:
    """Small strategy runner used by copied KOMPOSOS-IV call sites."""

    def __init__(self, category, embeddings=None):
        self.category = category
        self.embeddings = embeddings
        self.strategies = create_all_strategies(category, embeddings)

    def predict(self, source=None, target=None):
        out = []
        if source is not None and target is not None:
            for strategy in self.strategies:
                out.extend(strategy.predict(source, target))
        return sorted(out, key=lambda pred: pred.confidence, reverse=True)


__all__ = [
    "CategoricalOracle",
    "FibrationLiftStrategy",
    "Prediction",
    "PredictionType",
    "create_all_strategies",
]

