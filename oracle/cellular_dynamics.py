from ._base import OracleStrategy, path_to
from .prediction import PredictionType


class CellularDynamicsStrategy(OracleStrategy):
    strategy_name = "cellular_dynamics"

    def __init__(self, category, steps=5, beta=0.5, gamma=0.1):
        super().__init__(category)
        self.steps = steps
        self.beta = beta
        self.gamma = gamma

    def predict(self, source, target):
        path = path_to(self.category, source, target, max_length=self.steps)
        if path is None or self.beta < 0.05:
            return []
        confidence = min(1.0, path.weight * self.beta * max(self.steps, 1))
        return [self._prediction(source, target, "adopted_by_diffusion", PredictionType.CELLULAR, confidence)]

