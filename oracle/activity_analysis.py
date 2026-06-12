from ._base import OracleStrategy
from .prediction import PredictionType


class ActivityAnalysisStrategy(OracleStrategy):
    strategy_name = "activity_analysis"

    def predict(self, source, target):
        if len(self.category.morphisms()) < 3:
            return []
        return [self._prediction(source, target, "activity_tension", PredictionType.STRUCTURAL_HOLE, 0.4)]

