# SPDX-License-Identifier: LicenseRef-Proprietary-Commercial
# SPDX-FileCopyrightText: 2026 James Hawkins <jhawk314@gmail.com>

"""
Game Theory Strategy - Nash Equilibrium

When multiple strategies give different predictions, find Nash equilibrium
(stable point where no strategy wants to change).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List
from collections import Counter
from oracle.prediction import Prediction, PredictionType, ConfidenceLevel
from oracle.strategies import InferenceStrategy
from core.category import Category


class NashEquilibriumStrategy(InferenceStrategy):
    """
    Find Nash equilibrium between competing predictions.

    When other strategies disagree, find stable answer.
    """

    name = "nash_equilibrium"

    def __init__(self, category: Category, other_strategies: List[InferenceStrategy] = None):
        super().__init__(category)
        self.other_strategies = other_strategies or []

    def predict(self, source: str, target: str) -> List[Prediction]:
        """Get predictions from all strategies, find equilibrium."""
        if not self.other_strategies:
            return []

        all_predictions = {}
        for strategy in self.other_strategies:
            preds = strategy.predict(source, target)
            if preds:
                all_predictions[strategy.name] = preds[0]

        if len(all_predictions) < 2:
            return []

        relations = [p.predicted_relation for p in all_predictions.values()]
        relation_counts = Counter(relations)
        consensus_relation = relation_counts.most_common(1)[0][0]

        consensus_preds = [p for p in all_predictions.values()
                          if p.predicted_relation == consensus_relation]
        avg_confidence = sum(p.confidence for p in consensus_preds) / len(consensus_preds)

        stability = len(consensus_preds) / len(all_predictions)

        if stability < 0.5:
            return []

        return [Prediction(
            source=source,
            target=target,
            predicted_relation=consensus_relation,
            confidence=avg_confidence * stability,
            confidence_level=ConfidenceLevel.HIGH if stability > 0.7 else ConfidenceLevel.MEDIUM,
            strategy_name=self.name,
            prediction_type=PredictionType.RELATION_INFERENCE,
            reasoning=f"Nash equilibrium: {len(consensus_preds)}/{len(all_predictions)} strategies agree on '{consensus_relation}'"
        )]
