"""Shared prediction contracts used by OPERADUM and PRONOIA adapters.

This module is intentionally small. It supplies the data shapes expected by the
PHARM integration when an external ``domain_core`` checkout is not available.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class Candidate:
    identifier: str
    name: str = ""
    kind: str = "candidate"
    target: str = ""
    claim: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            object.__setattr__(self, "name", self.identifier)
        if not self.claim:
            target = f" -> {self.target}" if self.target else ""
            object.__setattr__(self, "claim", f"{self.name}{target}")


@dataclass(frozen=True)
class EvidenceItem:
    source: str
    claim: str
    score: float = 0.0
    weight: float = 1.0
    provenance: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def as_text(self) -> str:
        parts = [self.source, self.claim, f"score={float(self.score):.4f}"]
        if self.provenance:
            parts.append(f"provenance={self.provenance}")
        return " | ".join(parts)


@dataclass(frozen=True)
class EvidencePacket:
    candidate: Candidate
    task: str
    items: Sequence[EvidenceItem] = field(default_factory=tuple)
    context: Mapping[str, Any] = field(default_factory=dict)

    def as_text(self) -> str:
        header = f"task={self.task}\ncandidate={self.candidate.claim}"
        body = "\n".join(item.as_text() for item in self.items)
        return f"{header}\n{body}" if body else header


@dataclass(frozen=True)
class TraceStep:
    op: str
    justification: str = ""
    output: str = ""


@dataclass(frozen=True)
class PredictionReport:
    candidate: Candidate
    task: str
    decision: str
    score: float
    honest: bool
    abstained: bool
    explanation: str
    evidence: EvidencePacket
    trace: Sequence[TraceStep] = field(default_factory=tuple)
    metrics: Mapping[str, float] = field(default_factory=dict)


class EvidenceProvider(Protocol):
    def evidence_for(self, candidate: Candidate, task: str) -> EvidencePacket:
        ...

