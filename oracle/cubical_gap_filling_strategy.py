from ._base import OracleStrategy, direct_morphisms, path_to
from .prediction import PredictionType


class CubicalGapFillingStrategy(OracleStrategy):
    strategy_name = "cubical_gap_filling"

    def __init__(self, category, min_confidence=0.3):
        super().__init__(category)
        self.min_confidence = min_confidence

    def predict(self, source, target):
        if direct_morphisms(self.category, source, target):
            return []
        path = path_to(self.category, source, target, max_length=4)
        if path is None or path.length < 2:
            return []
        confidence = path.weight * 0.9
        if confidence < self.min_confidence:
            return []
        names = []
        for morphism_id in path.morphism_ids:
            mor = self.category.get_morphism(morphism_id)
            if mor:
                names.append(mor.name)
        relation = names[0] if names and all(name == names[0] for name in names) else "composed_morphism"
        return [self._prediction(source, target, relation, PredictionType.TRANSITIVE_CLOSURE, confidence, path=path.morphism_ids)]

