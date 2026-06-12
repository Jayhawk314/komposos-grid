# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Queue-to-bottleneck matching: stalled projects as missing intermediates.

The categorical idea, made operational: a congested seam is a morphism
whose hom-value no existing object improves -- OPTIMUS found no
factorization. But the interconnection queue holds ~1,700 GW of
*proposed* objects, each with a location and capacity: pre-specified
candidate intermediates. This module matches them.

Matching rules (screening-grade, every assumption explicit):

- Power flows toward the high-price side, so the *importing* endpoint
  of a tie (target of ``net_direction``) is where new **generation**
  relieves the seam by displacing imports; the *exporting* endpoint is
  where **storage** absorbs energy the wires cannot carry out.
- A project matches an endpoint BA when its state lies in that BA's
  generation footprint (from eGRID plant records) AND its queue region
  is compatible with that BA (its ISO's BA code, or a non-ISO region
  like 'west'/'southeast' for non-ISO BAs).
- Relief energy = capacity x fuel capacity-factor x 8760h, scaled by
  the BA's share of generation in the project's state, capped at the
  tie's annual gross flow.
- Relief value = relief energy x the tie's *measured congestion
  component* spread ($/MWh). Ties without measured evidence match
  projects but carry $0 -- structural candidates, not claims.

These are screening estimates that rank candidates; they are not
production-cost simulations. Aggregate tie relief is capped at
gross_mwh x spread (you cannot relieve more congestion than exists).
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from domains.grid.sources.base import PlantRecord
from domains.grid.sources.lbnl_queue import QueueProject

HOURS_PER_YEAR = 8760.0

# Annual capacity factors by LBNL type_clean (screening values)
CAPACITY_FACTOR = {
    "solar": 0.25, "solar_battery": 0.25, "solar_wind_battery": 0.30,
    "wind": 0.35, "wind_battery": 0.35, "offshore_wind": 0.45,
    "gas": 0.55, "coal": 0.55, "nuclear": 0.90, "hydro": 0.40,
    "geothermal": 0.80, "other": 0.30, "other_battery": 0.30,
}
# Pure storage: annual throughput ~ 4h duration x ~300 cycles
STORAGE_MWH_PER_MW = 1200.0

# queue region -> the BA code it corresponds to (ISOs); non-ISO regions
# are compatible with any BA *not* claimed by an ISO region.
REGION_BA = {
    "miso": "MISO", "spp": "SWPP", "pjm": "PJM", "nyiso": "NYIS",
    "caiso": "CISO", "ercot": "ERCO", "iso_ne": "ISNE",
}
ISO_BAS = set(REGION_BA.values())
NON_ISO_REGIONS = {"west", "southeast"}

MIN_STATE_SHARE = 0.05  # ignore states <5% of a BA's generation


def build_ba_state_footprint(
    records: Iterable[PlantRecord],
) -> Dict[str, Dict[str, float]]:
    """ba -> {state: MWh of the BA's generation in that state}.

    Raw MWh (not shares): weights across BAs for one state must compare
    generation, not per-BA-normalized fractions. States under
    MIN_STATE_SHARE of a BA's total are dropped as footprint noise.
    """
    totals: Dict[str, float] = defaultdict(float)
    by_state: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for rec in records:
        ba, state = rec.balancing_authority, rec.state
        gen = rec.net_generation_mwh or 0.0
        if not ba or ba == "nan" or not state or state == "nan" or gen <= 0:
            continue
        totals[ba] += gen
        by_state[ba][state] += gen
    return {
        ba: {
            s: v
            for s, v in states.items()
            if v / totals[ba] >= MIN_STATE_SHARE
        }
        for ba, states in by_state.items()
        if totals[ba] > 0
    }


def state_ba_weight(
    footprint: Dict[str, Dict[str, float]], state: str, ba: str
) -> float:
    """Fraction of the state's footprint generation belonging to this
    BA -- how much of a project in that state to attribute to it."""
    ba_gen = footprint.get(ba, {}).get(state, 0.0)
    if ba_gen <= 0:
        return 0.0
    total = sum(states.get(state, 0.0) for states in footprint.values())
    return ba_gen / total if total > 0 else 0.0


def region_compatible(region: str, ba: str) -> bool:
    mapped = REGION_BA.get(region)
    if mapped is not None:
        return mapped == ba
    if region in NON_ISO_REGIONS:
        return ba not in ISO_BAS
    return False


def project_role_and_potential(p: QueueProject) -> Tuple[str, float]:
    """('generation'|'storage', annual MWh potential)."""
    if p.mw is None or p.mw <= 0:
        return "generation", 0.0
    if p.fuel == "battery":
        return "storage", p.mw * STORAGE_MWH_PER_MW
    cf = CAPACITY_FACTOR.get(p.fuel, 0.30)
    return "generation", p.mw * cf * HOURS_PER_YEAR


@dataclass
class ProjectMatch:
    q_id: str
    fuel: str
    state: str
    region: str
    mw: float
    status: str
    role: str                 # generation | storage
    side: str                 # BA code the project supports
    ba_weight: float
    relief_mwh: float
    relief_value_usd: float


@dataclass
class TieMatches:
    ba_a: str
    ba_b: str
    evidence_status: str
    gross_mwh: float
    congestion_spread: float          # $/MWh, 0 if unmeasured
    importing_side: str
    exporting_side: str
    matches: List[ProjectMatch] = field(default_factory=list)

    @property
    def tie_value_cap_usd(self) -> float:
        return self.gross_mwh * self.congestion_spread

    def total(self, status: str) -> Tuple[int, float, float]:
        """(n, GW, capped relief value) for active|withdrawn matches."""
        rows = [m for m in self.matches if m.status == status]
        value = min(sum(m.relief_value_usd for m in rows), self.tie_value_cap_usd)
        return len(rows), sum(m.mw for m in rows) / 1000.0, value

    def top(self, status: str, n: int = 5) -> List[ProjectMatch]:
        rows = [m for m in self.matches if m.status == status]
        return sorted(rows, key=lambda m: -m.relief_value_usd)[:n]


@dataclass
class QueueMatchReport:
    ties: List[TieMatches]

    def summary(self, top: int = 5) -> str:
        measured = [t for t in self.ties if t.congestion_spread > 0]
        lines = [
            "Queue-to-bottleneck matching "
            f"({len(self.ties)} ties, {len(measured)} with measured spreads)"
        ]
        for t in sorted(measured, key=lambda t: -t.tie_value_cap_usd):
            n_act, gw_act, val_act = t.total("active")
            n_wd, gw_wd, val_wd = t.total("withdrawn")
            lines.append(
                f"  {t.ba_a}--{t.ba_b} (cap ${t.tie_value_cap_usd/1e6:,.1f}M/yr, "
                f"gen side {t.importing_side}, storage side {t.exporting_side}):"
            )
            lines.append(
                f"    active: {n_act} projects, {gw_act:,.1f} GW, capped relief "
                f"${val_act/1e6:,.1f}M/yr | withdrawn (lost): {n_wd} projects, "
                f"{gw_wd:,.1f} GW, ${val_wd/1e6:,.1f}M/yr"
            )
            for m in t.top("active", top):
                lines.append(
                    f"      {m.q_id} [{m.fuel} {m.mw:,.0f}MW {m.state} "
                    f"{m.role}->{m.side}] relief ${m.relief_value_usd/1e6:,.2f}M/yr"
                )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "ties": [
                {
                    "ba_a": t.ba_a,
                    "ba_b": t.ba_b,
                    "evidence_status": t.evidence_status,
                    "congestion_spread_usd_mwh": t.congestion_spread,
                    "tie_value_cap_usd": t.tie_value_cap_usd,
                    "importing_side": t.importing_side,
                    "exporting_side": t.exporting_side,
                    "active": dict(zip(("n", "gw", "capped_value_usd"),
                                       t.total("active"))),
                    "withdrawn": dict(zip(("n", "gw", "capped_value_usd"),
                                          t.total("withdrawn"))),
                    "top_active": [vars(m) for m in t.top("active", 10)],
                    "top_withdrawn": [vars(m) for m in t.top("withdrawn", 10)],
                }
                for t in self.ties
            ]
        }

    def export_json(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(self.to_dict(), indent=1), encoding="utf-8"
        )

    def export_csv(self, path: str | Path) -> None:
        import csv

        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow([
                "ba_a", "ba_b", "q_id", "status", "fuel", "state", "mw",
                "role", "side", "ba_weight", "relief_mwh", "relief_value_usd",
            ])
            for t in self.ties:
                for m in sorted(t.matches, key=lambda m: -m.relief_value_usd):
                    writer.writerow([
                        t.ba_a, t.ba_b, m.q_id, m.status, m.fuel, m.state,
                        m.mw, m.role, m.side, round(m.ba_weight, 3),
                        round(m.relief_mwh, 1), round(m.relief_value_usd, 2),
                    ])


def _import_export_sides(claim: dict) -> Tuple[str, str]:
    """net_direction 'X -> Y' means net flow X to Y: Y imports."""
    direction = claim.get("net_direction", "")
    if "->" in direction:
        exp, imp = [s.strip() for s in direction.split("->")]
        return imp, exp
    return claim["ba_a"], claim["ba_b"]


def match_queue_to_bottlenecks(
    claims: List[dict],
    projects: List[QueueProject],
    footprint: Dict[str, Dict[str, float]],
    statuses: Tuple[str, ...] = ("active", "withdrawn"),
) -> QueueMatchReport:
    candidates = [
        p for p in projects
        if p.status in statuses and p.mw and p.mw > 0 and p.state
    ]

    ties: List[TieMatches] = []
    for claim in claims:
        importing, exporting = _import_export_sides(claim)
        spread = float(
            claim.get("mean_congestion_component_spread_usd_mwh")
            or 0.0
        )
        tie = TieMatches(
            ba_a=claim["ba_a"],
            ba_b=claim["ba_b"],
            evidence_status=str(claim.get("evidence_status", "")),
            gross_mwh=float(claim.get("gross_mwh", 0.0)),
            congestion_spread=spread,
            importing_side=importing,
            exporting_side=exporting,
        )

        for p in candidates:
            role, potential = project_role_and_potential(p)
            if potential <= 0:
                continue
            side = importing if role == "generation" else exporting
            if not region_compatible(p.region, side):
                continue
            weight = state_ba_weight(footprint, p.state, side)
            if weight <= 0:
                continue
            relief_mwh = min(potential * weight, tie.gross_mwh)
            tie.matches.append(
                ProjectMatch(
                    q_id=p.q_id, fuel=p.fuel, state=p.state, region=p.region,
                    mw=float(p.mw), status=p.status, role=role, side=side,
                    ba_weight=weight, relief_mwh=relief_mwh,
                    relief_value_usd=relief_mwh * spread,
                )
            )
        ties.append(tie)
    return QueueMatchReport(ties=ties)


def write_to_category(category, report: QueueMatchReport, top: int = 10) -> None:
    """Top candidates as structure: project -would_relieve-> tie, with
    confidence = relief value relative to the tie's cap."""
    for t in report.ties:
        if t.congestion_spread <= 0:
            continue
        tie_obj = f"tie:{t.ba_a}-{t.ba_b}"
        if category.get(tie_obj) is None:
            category.add(tie_obj, type_name="seam")
        for m in t.top("active", top):
            proj = f"queue:{m.q_id}"
            if category.get(proj) is None:
                category.add(proj, type_name="queue_project")
            cap = t.tie_value_cap_usd or 1.0
            category.connect(
                proj, tie_obj, name="would_relieve",
                confidence=max(min(m.relief_value_usd / cap, 1.0), 1e-6),
                relief_mwh=m.relief_mwh,
                relief_value_usd=m.relief_value_usd,
                role=m.role,
            )
