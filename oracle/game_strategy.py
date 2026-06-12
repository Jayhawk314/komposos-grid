from ._base import OracleStrategy, has_edge, outgoing_by_target
from .prediction import PredictionType


class GameStrategy(OracleStrategy):
    strategy_name = "game_strategy"

    def predict(self, source, target):
        for _shared, incoming in outgoing_by_target(self.category).items():
            sources = {m.source for m in incoming}
            if source in sources and target in sources and len(sources) > 1:
                relation = "cooperative_equilibrium" if has_edge(self.category, source, target) or has_edge(self.category, target, source) else "competitive_equilibrium"
                confidence = sum(m.confidence for m in incoming if m.source in {source, target}) / 2.0
                return [self._prediction(source, target, relation, PredictionType.GAME_THEORETIC, confidence)]
        return []

