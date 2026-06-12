from ._base import OracleStrategy, objects
from .prediction import PredictionType


class FibrationLiftStrategy(OracleStrategy):
    strategy_name = "fibration_lift"

    def predict(self, source, target):
        obj = objects(self.category)
        if source not in obj or target not in obj:
            return []
        source_type = obj[source].type_name
        for other_name, other in obj.items():
            if other_name == source or other.type_name != source_type:
                continue
            for mor in self.category.morphisms_from(other_name):
                if mor.target == target:
                    confidence = min(0.7, mor.confidence * 0.8)
                    return [self._prediction(source, target, "cartesian_lift", PredictionType.CARTESIAN_LIFT, confidence, via=other_name)]
        return []


def create_all_strategies(category, embeddings=None):
    from .boundary_detection import BoundaryDetectionStrategy
    from .cubical_gap_filling_strategy import CubicalGapFillingStrategy
    from .game_strategy import GameStrategy
    from .streaming_forecast import StreamingForecastStrategy
    from .topological_anomaly import TopologicalAnomalyStrategy
    from .topos_strategy import ToposLogicStrategy

    return [
        CubicalGapFillingStrategy(category),
        BoundaryDetectionStrategy(category),
        FibrationLiftStrategy(category),
        TopologicalAnomalyStrategy(category),
        GameStrategy(category),
        ToposLogicStrategy(category),
        StreamingForecastStrategy(category),
    ]

