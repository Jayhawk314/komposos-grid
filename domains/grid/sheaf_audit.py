# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Cohomological coherence audit via the thermodynamic sheaf probe.

The pairwise checker (coherence.py) classifies each overlap entity
independently. This module upgrades that to a *global* statement using
the scalar cellular sheaf in komposos_wesys.validation.thermodynamic_probe:

- one gauge node per data source
- for each entity (plant, BA) shared by a pair of sources, one edge
  asserting x_low = (value_low / value_high) * x_high

The sheaf Laplacian's smallest eigenvalue is the H^1 obstruction: it is
~0 iff a single global calibration between the sources reproduces every
entity's ratio (sections glue up to one gauge), and the minimizing
eigenvector IS that calibration. Per-edge residuals localize exactly
which entities are incompatible with any global gauge -- a strictly
stronger statement than per-entity thresholding, and one that needs no
tolerance parameter.

Entities with non-positive values in either section (e.g. storage with
negative net generation) carry no multiplicative ratio and are excluded;
the count is reported.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from komposos_wesys.validation.thermodynamic_probe import ThermodynamicSheaf

from domains.grid.coherence import Section


@dataclass
class SheafOffender:
    entity: str
    source_high: str
    source_low: str
    ratio: float          # value_low / value_high, in (0, 1]
    residual: float       # energy contribution of this edge


@dataclass
class FusedEstimate:
    """One calibration-normalized estimate for an entity."""

    entity: str
    value: float
    n_sources: int
    relative_spread: float


@dataclass
class GridSheafAudit:
    energy_leak: float            # H^1 proxy: 0 iff sections glue up to gauge
    stable: bool
    n_edges: int
    n_skipped: int                # entities without a positive ratio
    gauge: Dict[str, float]       # source -> fused calibration value
    calibration: Dict[str, float] # source -> multiplier onto reference scale
    reference_source: str
    offenders: List[SheafOffender]
    fused_values: Dict[str, FusedEstimate]

    def summary(self, top: int = 5) -> str:
        worst_estimates = sorted(
            (e for e in self.fused_values.values() if e.n_sources > 1),
            key=lambda e: e.relative_spread,
            reverse=True,
        )
        lines = [
            f"Sheaf audit: H^1 energy leak {self.energy_leak:.3e} "
            f"({'stable -- a global calibration exists' if self.stable else 'obstructed'}); "
            f"{self.n_edges} ratio edges, {self.n_skipped} entities skipped (non-positive)",
            "  gauge: "
            + ", ".join(f"{s}={v:.4f}" for s, v in sorted(self.gauge.items())),
            f"  calibrated fusion: {len(self.fused_values)} entities on "
            f"{self.reference_source} scale"
            + (
                f"; worst calibrated spread {worst_estimates[0].relative_spread:.1%}"
                if worst_estimates else ""
            ),
        ]
        for off in self.offenders[:top]:
            lines.append(
                f"  obstruction {off.entity}: {off.source_low}/{off.source_high} "
                f"ratio {off.ratio:.3f}, residual {off.residual:.3e}"
            )
        return "\n".join(lines)


def _calibration_factors(
    gauge: Dict[str, float], reference_source: str
) -> Dict[str, float]:
    ref = gauge.get(reference_source)
    if ref is None or abs(ref) < 1e-12:
        ref = next((v for v in gauge.values() if abs(v) >= 1e-12), 1.0)
    return {
        source: (ref / value if abs(value) >= 1e-12 else 1.0)
        for source, value in gauge.items()
    }


def _fuse_values(
    sections: List[Section],
    calibration: Dict[str, float],
) -> Dict[str, FusedEstimate]:
    by_entity: Dict[str, List[float]] = {}
    for section in sections:
        factor = calibration.get(section.source, 1.0)
        for entity, value in section.values.items():
            by_entity.setdefault(entity, []).append(value * factor)

    fused: Dict[str, FusedEstimate] = {}
    for entity, values in by_entity.items():
        estimate = sum(values) / len(values)
        scale = max((abs(v) for v in values), default=0.0)
        spread = (max(values) - min(values)) / scale if scale else 0.0
        fused[entity] = FusedEstimate(
            entity=entity,
            value=estimate,
            n_sources=len(values),
            relative_spread=spread,
        )
    return fused


def sheaf_audit(
    sections: List[Section],
    stable_leak: float = 1e-6,
    reference_source: str | None = None,
) -> GridSheafAudit:
    """Audit sections for a global gauge; localize H^1 obstructions."""
    sheaf = ThermodynamicSheaf()
    for section in sections:
        sheaf.add_node(section.source)

    edge_meta: List[Tuple[str, str, str, float]] = []  # entity, high, low, ratio
    n_skipped = 0
    for i in range(len(sections)):
        for j in range(i + 1, len(sections)):
            sec_a, sec_b = sections[i], sections[j]
            for entity in sec_a.coverage & sec_b.coverage:
                va, vb = sec_a.values[entity], sec_b.values[entity]
                if va <= 0 or vb <= 0:
                    n_skipped += 1
                    continue
                if vb <= va:
                    high, low, ratio = sec_a.source, sec_b.source, vb / va
                else:
                    high, low, ratio = sec_b.source, sec_a.source, va / vb
                sheaf.add_flow(high, low, efficiency=ratio)
                edge_meta.append((entity, high, low, ratio))

    audit = sheaf.audit()
    reference = reference_source or (sections[0].source if sections else "")
    gauge = audit.assignment
    calibration = _calibration_factors(gauge, reference) if gauge else {}
    fused_values = _fuse_values(sections, calibration)

    # audit() preserves edge identity; map residuals back to entities
    by_id = {id(edge): meta for edge, meta in zip(sheaf._edges, edge_meta)}

    offenders = []
    for edge, residual in audit.edge_residuals:
        entity, high, low, ratio = by_id[id(edge)]
        offenders.append(
            SheafOffender(
                entity=entity,
                source_high=high,
                source_low=low,
                ratio=ratio,
                residual=residual,
            )
        )

    return GridSheafAudit(
        energy_leak=audit.energy_leak,
        stable=audit.energy_leak < stable_leak,
        n_edges=len(edge_meta),
        n_skipped=n_skipped,
        gauge=gauge,
        calibration=calibration,
        reference_source=reference,
        offenders=offenders,
        fused_values=fused_values,
    )
