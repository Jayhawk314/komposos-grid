from ._base import OracleStrategy
from .prediction import PredictionType


class StreamingForecastStrategy(OracleStrategy):
    strategy_name = "streaming_forecast"

    def __init__(self, category, decay_rate=0.0, min_confidence=0.3):
        super().__init__(category)
        self.decay_rate = decay_rate
        self.min_confidence = min_confidence
        self._observations = {}

    def observe(self, source, target, weight=1.0):
        self._observations[(source, target)] = float(weight)

    def predict(self, source, target):
        weight = self._observations.get((source, target))
        if weight is None or weight < self.min_confidence:
            return []
        return [self._prediction(source, target, "stream_forecast", PredictionType.STREAMING_FORECAST, weight)]

