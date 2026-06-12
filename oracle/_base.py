from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable

from .prediction import Prediction, PredictionType


class OracleStrategy:
    strategy_name = "oracle"

    def __init__(self, category, *args, **kwargs):
        self.category = category

    def _prediction(self, source, target, relation, ptype, confidence, reasoning="", **evidence):
        return Prediction(
            source=str(source),
            target=str(target),
            predicted_relation=str(relation),
            prediction_type=ptype,
            strategy_name=self.strategy_name,
            confidence=_clip(confidence),
            reasoning=reasoning,
            evidence=evidence,
        )


def _clip(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def objects(category):
    return {obj.name: obj for obj in category.objects()}


def morphisms(category):
    return list(category.morphisms())


def direct_morphisms(category, source, target):
    return [m for m in morphisms(category) if m.source == source and m.target == target]


def has_edge(category, source, target):
    return bool(direct_morphisms(category, source, target))


def path_to(category, source, target, max_length=4):
    paths = category.find_paths(source, target, max_length=max_length)
    return max(paths, key=lambda p: p.weight) if paths else None


def graph_neighbors(category, node):
    neigh = set()
    for m in morphisms(category):
        if m.source == node:
            neigh.add(m.target)
        if m.target == node:
            neigh.add(m.source)
    return neigh


def reachable(category, source, target, max_depth=4):
    queue = deque([(source, 0)])
    seen = {source}
    while queue:
        current, depth = queue.popleft()
        if current == target and depth > 0:
            return True
        if depth >= max_depth:
            continue
        for m in morphisms(category):
            if m.source == current and m.target not in seen:
                seen.add(m.target)
                queue.append((m.target, depth + 1))
    return False


def outgoing_by_target(category):
    out = defaultdict(list)
    for m in morphisms(category):
        out[m.target].append(m)
    return out

