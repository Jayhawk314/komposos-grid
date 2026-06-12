from ._base import OracleStrategy, direct_morphisms
from .prediction import PredictionType


class OperadicDecompositionStrategy(OracleStrategy):
    strategy_name = "operadic_decomposition"

    def predict(self, source, target):
        direct = direct_morphisms(self.category, source, target)
        if not direct:
            return []
        paths = [p for p in self.category.find_paths(source, target, max_length=4) if p.length > 1]
        if paths:
            best = max(paths, key=lambda p: p.weight)
            return [self._prediction(source, target, "operadic_decomposition", PredictionType.OPERADIC, best.weight)]
        return [self._prediction(source, target, "genuine_primitive", PredictionType.OPERADIC, direct[0].confidence)]

