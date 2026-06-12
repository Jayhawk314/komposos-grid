"""Adapter from shared evidence packets into PRONOIA prediction reports."""

from __future__ import annotations

from typing import Sequence

from domain_core import EvidencePacket, PredictionReport, TraceStep

from .honesty_mdl import ReasoningStep, sincerity
from .mdl_ranker import Hypothesis, compression_gain


class PronoiaPredictor:
    """Score a candidate by evidence compression and grounding.

    The adapter is deliberately deterministic: evidence text is compressed with
    the candidate claim as the model, while grounding is the weighted mean of
    evidence-item scores. Downstream domain loops can rescale the report.
    """

    def __init__(self, *, min_grounding: float = 0.2) -> None:
        self.min_grounding = float(min_grounding)

    def predict(self, packet: EvidencePacket) -> PredictionReport:
        evidence_text = packet.as_text()
        hypothesis = Hypothesis(packet.candidate.name, packet.candidate.claim)
        gain, cost, residual = compression_gain(
            evidence_text.encode("utf-8"),
            hypothesis.claim.encode("utf-8"),
        )
        grounding = _grounding(packet)
        trace = _trace(packet, gain, grounding)
        stated = (
            ReasoningStep("score_evidence", "rank by MDL gain", f"gain={gain:.1f}"),
            ReasoningStep("check_grounding", "mean evidence score", f"grounding={grounding:.3f}"),
        )
        honesty = sincerity(
            tuple(ReasoningStep(t.op, t.justification, t.output) for t in trace),
            stated,
        )
        score = max(0.0, float(gain)) * max(0.0, grounding)
        abstained = grounding < self.min_grounding or score <= 0.0
        decision = "BACK" if not abstained else "ABSTAIN"
        metrics = {
            "gain_bits": round(float(gain), 4),
            "hypothesis_cost_bits": round(float(cost), 4),
            "residual_bits": round(float(residual), 4),
            "grounding": round(float(grounding), 6),
            "fabricated_bits": float(honesty.fabricated_bits),
            "hidden_bits": float(honesty.hidden_bits),
            "sincerity": float(honesty.sincerity),
        }
        explanation = (
            f"PRONOIA score {score:.2f}: gain {gain:.1f} bits, "
            f"grounding {grounding:.3f}."
        )
        return PredictionReport(
            candidate=packet.candidate,
            task=packet.task,
            decision=decision,
            score=round(score, 4),
            honest=bool(honesty.honest and not abstained),
            abstained=abstained,
            explanation=explanation,
            evidence=packet,
            trace=trace,
            metrics=metrics,
        )


def _grounding(packet: EvidencePacket) -> float:
    items = tuple(packet.items or ())
    if not items:
        return 0.0
    weighted = 0.0
    total_weight = 0.0
    for item in items:
        weight = max(0.0, float(getattr(item, "weight", 1.0) or 0.0))
        weighted += max(0.0, min(1.0, float(item.score or 0.0))) * weight
        total_weight += weight
    return weighted / total_weight if total_weight > 0.0 else 0.0


def _trace(packet: EvidencePacket, gain: float, grounding: float) -> Sequence[TraceStep]:
    steps = [
        TraceStep("collect_evidence", packet.task, f"items={len(tuple(packet.items or ())) }"),
        TraceStep("score_evidence", "rank by MDL gain", f"gain={gain:.1f}"),
        TraceStep("check_grounding", "mean evidence score", f"grounding={grounding:.3f}"),
    ]
    return tuple(steps)


__all__ = ["PronoiaPredictor"]

