from collections import defaultdict

from ._base import OracleStrategy
from .prediction import PredictionType


class EvidenceCombinationStrategy(OracleStrategy):
    strategy_name = "evidence_combination"

    def __init__(self, category, other_strategies=None):
        super().__init__(category)
        self._other_strategies = list(other_strategies or [])

    def predict(self, source, target):
        grouped = defaultdict(list)
        for strategy in self._other_strategies:
            for pred in strategy.predict(source, target):
                grouped[pred.predicted_relation].append(pred)
        if not grouped:
            return []
        relation, preds = max(grouped.items(), key=lambda item: (len(item[1]), sum(p.confidence for p in item[1])))
        confidence = sum(p.confidence for p in preds) / len(preds)
        return [self._prediction(source, target, relation, PredictionType.ENSEMBLE, confidence, members=len(preds))]

