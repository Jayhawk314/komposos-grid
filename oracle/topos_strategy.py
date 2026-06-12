from ._base import OracleStrategy, direct_morphisms
from .prediction import PredictionType


class ToposLogicStrategy(OracleStrategy):
    strategy_name = "topos_logic"

    def predict(self, source, target):
        direct = direct_morphisms(self.category, source, target)
        if direct:
            best = max(direct, key=lambda m: m.confidence)
            return [self._prediction(source, target, "classically_true", PredictionType.TOPOS, best.confidence)]
        return []

