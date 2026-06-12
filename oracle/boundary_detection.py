from ._base import OracleStrategy, graph_neighbors, objects
from .prediction import PredictionType


class BoundaryDetectionStrategy(OracleStrategy):
    strategy_name = "boundary_detection"

    def predict(self, source, target):
        obj = objects(self.category)
        if source not in obj or target not in obj:
            return []
        if obj[source].type_name == obj[target].type_name:
            return []
        shared = graph_neighbors(self.category, source) & graph_neighbors(self.category, target)
        if not shared:
            return []
        confidence = max(0.3, min(1.0, len(shared) / max(len(graph_neighbors(self.category, source)), 1)))
        return [self._prediction(source, target, "boundary_bridge", PredictionType.BOUNDARY, confidence, shared=sorted(shared))]

