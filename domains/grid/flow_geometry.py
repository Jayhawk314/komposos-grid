# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Geometric analysis of the BA interchange flow graph.

Builds the balancing-authority flow graph from EIA-930 INTERCHANGE
files (nodes = BAs, edges weighted by annual gross interchange) and
runs the existing komposos_wesys geometry modules on it:

- Ollivier-Ricci curvature (geometry/grid_ricci.py): negative-curvature
  edges are tree-like passages whose endpoint neighborhoods do not
  overlap -- the structural bottlenecks where congestion concentrates
  and single failures partition the grid. Positive curvature marks
  redundantly meshed (resilient) regions.
- Spectral analysis (geometry/grid_spectral.py): the algebraic
  connectivity (Fiedler value) measures how hard the network is to cut;
  the Fiedler vector's sign pattern exhibits the weakest seam -- for
  the US grid this should recover the East/West interconnection split
  without being told it exists.

This targets the T&D-losses waste class: congestion price separation
(LMPs) happens across exactly these low-curvature, low-connectivity
edges, so geometry computed from public telemetry locates where
transmission investment relieves the most trapped energy.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from core.category import Category

BA_COLUMN = "Balancing Authority"
DIBA_COLUMN = "Directly Interconnected Balancing Authority"
FLOW_COLUMN = "Interchange (MW)"


@dataclass
class TieLine:
    ba_a: str
    ba_b: str
    gross_mwh: float   # sum of |hourly flow|: how much the tie is used
    net_mwh: float     # signed a->b annual net


def load_interchange(csv_paths: Iterable[str | Path]) -> List[TieLine]:
    """Aggregate hourly tie flows to annual per-pair totals.

    Every tie is reported by both endpoint BAs (with opposite signs);
    we keep each pair once, from the alphabetically-first reporter's
    perspective.
    """
    import pandas as pd

    pair_gross: Dict[Tuple[str, str], float] = {}
    pair_net: Dict[Tuple[str, str], float] = {}
    for path in csv_paths:
        df = pd.read_csv(
            path,
            usecols=[BA_COLUMN, DIBA_COLUMN, FLOW_COLUMN],
            thousands=",",
        )
        df[FLOW_COLUMN] = pd.to_numeric(df[FLOW_COLUMN], errors="coerce")
        df = df.dropna(subset=[FLOW_COLUMN])
        df = df[df[BA_COLUMN] < df[DIBA_COLUMN]]  # one reporter per pair
        grouped = df.groupby([BA_COLUMN, DIBA_COLUMN])[FLOW_COLUMN]
        for pair, gross in grouped.apply(lambda s: s.abs().sum()).items():
            pair_gross[pair] = pair_gross.get(pair, 0.0) + float(gross)
        for pair, net in grouped.sum().items():
            pair_net[pair] = pair_net.get(pair, 0.0) + float(net)

    return [
        TieLine(ba_a=a, ba_b=b, gross_mwh=g, net_mwh=pair_net[(a, b)])
        for (a, b), g in sorted(pair_gross.items())
    ]


def build_flow_category(
    ties: List[TieLine], db_path: str = ":memory:"
) -> Category:
    """BA flow graph as a Category: confidence = normalized gross flow."""
    category = Category(name="ba_flow", db_path=db_path)
    max_gross = max((t.gross_mwh for t in ties), default=1.0)
    for t in ties:
        src, tgt = (t.ba_a, t.ba_b) if t.net_mwh >= 0 else (t.ba_b, t.ba_a)
        category.connect(
            f"ba:{src}",
            f"ba:{tgt}",
            name="interchange",
            confidence=max(t.gross_mwh / max_gross, 1e-3),
            gross_mwh=t.gross_mwh,
            net_mwh=abs(t.net_mwh),
        )
    return category


class _CategoryStore:
    """Adapter: Category -> the store interface grid_ricci expects.

    grid_ricci uses edge weight as the metric distance d in
    kappa = 1 - W1/d. Flow magnitude is coupling strength, not distance
    (a heavy tie is *shorter*, and gross flows span six orders of
    magnitude), so curvature is computed on the unit-distance topology;
    flow weighting enters through the spectral Laplacian and the
    bottleneck ranking instead.
    """

    def __init__(self, category: Category):
        self.category = category

    def list_morphisms(self, limit: int = 100000):
        from types import SimpleNamespace

        return [
            SimpleNamespace(
                source_name=m.source, target_name=m.target, confidence=1.0
            )
            for m in self.category.morphisms()[:limit]
        ]


@dataclass
class FlowGeometryReport:
    n_bas: int
    n_ties: int
    bottlenecks: List[Tuple[str, str, float, float]]  # ba, ba, curvature, gross
    meshed: List[Tuple[str, str, float]]              # most positive curvature
    curvature_stats: Dict[str, float]
    algebraic_connectivity: float
    coupling: str
    fiedler_partition: Tuple[List[str], List[str]]

    def summary(self, top: int = 10) -> str:
        lines = [
            f"Flow geometry: {self.n_bas} BAs, {self.n_ties} ties",
            f"  curvature mean {self.curvature_stats.get('mean', 0):.3f}, "
            f"hyperbolic edges {len(self.bottlenecks)} "
            f"/ {self.n_ties}",
            f"  algebraic connectivity (Fiedler) {self.algebraic_connectivity:.4f} "
            f"-- coupling {self.coupling}",
            "  Bottlenecks (most negative Ollivier-Ricci, heaviest flow first):",
        ]
        for a, b, kappa, gross in self.bottlenecks[:top]:
            lines.append(
                f"    {a} -- {b}: curvature {kappa:+.3f}, "
                f"gross {gross/1e6:,.1f} TWh/yr"
            )
        small, large = self.fiedler_partition
        lines.append(
            f"  Fiedler seam: {{{', '.join(sorted(small)[:12])}"
            f"{', ...' if len(small) > 12 else ''}}} ({len(small)} BAs) "
            f"vs remaining {len(large)} BAs"
        )
        return "\n".join(lines)


def analyze_flow_geometry(ties: List[TieLine]) -> FlowGeometryReport:
    from komposos_wesys.geometry.grid_ricci import OllivierRicciCurvature
    from komposos_wesys.geometry.grid_spectral import SpectralGraphAnalyzer

    category = build_flow_category(ties)
    gross_by_pair = {
        frozenset((f"ba:{t.ba_a}", f"ba:{t.ba_b}")): t.gross_mwh for t in ties
    }

    ricci = OllivierRicciCurvature(_CategoryStore(category), alpha=0.5)
    curvatures = ricci.compute_all_curvatures()

    seen = set()
    edges = []
    for (u, v), kappa in curvatures.edge_curvatures.items():
        key = frozenset((u, v))
        if key in seen:
            continue
        seen.add(key)
        edges.append((u, v, kappa, gross_by_pair.get(key, 0.0)))

    hyperbolic = sorted(
        (e for e in edges if e[2] < 0), key=lambda e: (e[2], -e[3])
    )
    # Bottleneck = negative curvature carrying heavy flow: rank by gross
    bottlenecks = sorted(hyperbolic, key=lambda e: -e[3])
    meshed = sorted(edges, key=lambda e: -e[2])[:5]

    spectral = SpectralGraphAnalyzer(category)
    spectral.build_laplacian()
    eigenvalues, eigenvectors = spectral.compute_spectrum()
    coupling = spectral.analyze_coupling()

    fiedler = eigenvectors[:, 1] if eigenvectors.shape[1] > 1 else eigenvectors[:, 0]
    names = [n.replace("ba:", "") for n in spectral.node_names]
    neg = [n for n, x in zip(names, fiedler) if x < 0]
    pos = [n for n, x in zip(names, fiedler) if x >= 0]
    partition = (neg, pos) if len(neg) <= len(pos) else (pos, neg)

    return FlowGeometryReport(
        n_bas=len(category.objects()),
        n_ties=len(ties),
        bottlenecks=[
            (u.replace("ba:", ""), v.replace("ba:", ""), k, g)
            for u, v, k, g in bottlenecks
        ],
        meshed=[
            (u.replace("ba:", ""), v.replace("ba:", ""), k) for u, v, k, _ in meshed
        ],
        curvature_stats={
            **curvatures.statistics,
            "n_hyperbolic": float(max(curvatures.num_hyperbolic, len(hyperbolic))),
        },
        algebraic_connectivity=float(coupling["algebraic_connectivity"]),
        coupling=str(coupling.get("coupling_strength", coupling.get("coupling", ""))),
        fiedler_partition=partition,
    )
