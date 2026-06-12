from ._base import OracleStrategy, has_edge, reachable
from .prediction import PredictionType


class TopologicalAnomalyStrategy(OracleStrategy):
    strategy_name = "topological_anomaly"

    def __init__(self, category, min_confidence=0.5):
        super().__init__(category)
        self.min_confidence = min_confidence

    def predict(self, source, target):
        if has_edge(self.category, source, target):
            return []
        if reachable(self.category, source, target) or reachable(self.category, target, source):
            return [self._prediction(source, target, "topological_fill", PredictionType.TOPOLOGICAL, self.min_confidence)]
        return []

