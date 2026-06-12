from ._base import OracleStrategy
from .prediction import PredictionType


class NaturalTransformationStrategy(OracleStrategy):
    strategy_name = "natural_transformation"

    def __init__(self, category, threshold=0.5):
        super().__init__(category)
        self.threshold = threshold

    def predict(self, source, target):
        paths = [p for p in self.category.find_paths(source, target, max_length=3) if p.length > 1]
        if len(paths) < 2:
            return []
        paths = sorted(paths, key=lambda p: p.weight, reverse=True)[:2]
        confidence = min(paths[0].weight, paths[1].weight) / max(paths[0].weight, paths[1].weight, 1e-9)
        if confidence < self.threshold:
            return []
        return [self._prediction(source, target, "natural_transform", PredictionType.NATURALITY, confidence)]

