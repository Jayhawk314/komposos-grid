"""
PRONOIA L1 - scalar sheaf contradiction audit.

A cellular sheaf assigns each node a stalk and each edge a restriction map,
then asks whether there is a global assignment compatible with every local
constraint.

This prototype uses the scalar rank-1 case: each node carries one number and
each edge asserts a scaled relation

    x_v = efficiency * x_u

with a positive confidence weight. The sheaf Laplacian is

    L = sum_e w_e b_e b_e^T, where b_e = e_v - efficiency * e_u.

The smallest eigenvalue is the global energy leak. A zero value means the
constraints have a compatible global section; per-edge residuals localize the
constraints responsible for any obstruction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np


@dataclass(frozen=True)
class EnergyEdge:
    u: str
    v: str
    efficiency: float
    weight: float = 1.0


@dataclass(frozen=True)
class ThermodynamicAudit:
    energy_leak: float
    stable: bool
    edge_residuals: List[Tuple[EnergyEdge, float]]
    assignment: Dict[str, float]

    @property
    def asefficiencyment(self) -> Dict[str, float]:
        """Compatibility alias for older generated code."""
        return self.assignment


class ThermodynamicSheaf:
    """Scalar cellular sheaf over a scaled, weighted graph."""

    def __init__(self) -> None:
        self._nodes: List[str] = []
        self._index: Dict[str, int] = {}
        self._edges: List[EnergyEdge] = []

    def add_node(self, name: str) -> None:
        if name not in self._index:
            self._index[name] = len(self._nodes)
            self._nodes.append(name)

    def add_flow(self, u: str, v: str, efficiency: float, weight: float = 1.0) -> None:
        if not (0 <= efficiency <= 1.0):
            raise ValueError("efficiency must be in [0, 1]")
        if weight <= 0:
            raise ValueError("weight must be positive")
        self.add_node(u)
        self.add_node(v)
        self._edges.append(EnergyEdge(u, v, float(efficiency), float(weight)))

    def laplacian(self) -> np.ndarray:
        """Build L = sum_e w_e b_e b_e^T in O(E) entry updates."""
        n = len(self._nodes)
        L = np.zeros((n, n))
        for e in self._edges:
            iu, iv = self._index[e.u], self._index[e.v]
            w, s = e.weight, e.efficiency
            # For b = e_v - s e_u, b b^T has (v,v)=1, (u,u)=s^2,
            # and symmetric off-diagonal entries -s.
            L[iv, iv] += w
            L[iu, iu] += s * s * w
            L[iv, iu] += -s * w
            L[iu, iv] += -s * w
        return L

    def audit(self) -> ThermodynamicAudit:
        """Find the minimal-disagreement assignment and localize residuals."""
        n = len(self._nodes)
        if n == 0:
            return ThermodynamicAudit(0.0, True, [], {})

        L = self.laplacian()
        vals, vecs = np.linalg.eigh(L)
        energy_leak = float(max(0.0, vals[0]))
        x = vecs[:, 0]
        if np.sum(x) < 0:
            x = -x

        residuals: List[Tuple[EnergyEdge, float]] = []
        for e in self._edges:
            iu, iv = self._index[e.u], self._index[e.v]
            disagreement = x[iv] - e.efficiency * x[iu]
            residuals.append((e, float(e.weight * disagreement * disagreement)))
        residuals.sort(key=lambda er: er[1], reverse=True)

        assignment = {name: float(x[self._index[name]]) for name in self._nodes}
        stable = energy_leak < 1e-8
        return ThermodynamicAudit(
            energy_leak=energy_leak,
            stable=stable,
            edge_residuals=residuals,
            assignment=assignment,
        )
