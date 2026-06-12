# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Natural-experiment-style relief curves for PLAN D8.

The project already has three ingredients:

* priced seam/tie evidence from ``congestion_evidence_report``;
* queue-to-bottleneck matches that identify plausible candidate supply;
* constraint reports that show where congestion pressure persists.

This module turns those into screening curves under explicit interventions.
It uses ``pronoia.scm.SCM`` so each point is a do-query:
``do(capacity_mw = x)``. The structural equations are deliberately simple
and capped by the measured annual tie value. This is not a production-cost
simulation or a causal estimate from randomized capacity additions.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

import numpy as np
from pronoia.scm import SCM


HOURS_PER_YEAR = 8760.0


@dataclass(frozen=True)
class CostBenchmark:
    name: str
    annualized_cost_usd_per_mw_year: float
    effective_mwh_per_mw_year: float
    source: str
    notes: str = ""

    def to_row(self) -> Dict[str, Any]:
        return {
            "benchmark": self.name,
            "annualized_cost_usd_per_mw_year": self.annualized_cost_usd_per_mw_year,
            "effective_mwh_per_mw_year": self.effective_mwh_per_mw_year,
            "source": self.source,
            "notes": self.notes,
        }


DEFAULT_BENCHMARKS = [
    CostBenchmark(
        name="transmission_capacity",
        annualized_cost_usd_per_mw_year=150_000.0,
        effective_mwh_per_mw_year=HOURS_PER_YEAR,
        source="screening default; replace with project-specific transmission estimate",
        notes="Represents firm transfer capability; cost is annualized and user-overridable.",
    ),
    CostBenchmark(
        name="grid_storage_4h",
        annualized_cost_usd_per_mw_year=187_500.0,
        effective_mwh_per_mw_year=1_200.0,
        source="NREL ATB utility-scale battery methodology, annualized screening default",
        notes="Uses a 4-hour storage throughput proxy consistent with existing queue matching.",
    ),
    CostBenchmark(
        name="flexible_load",
        annualized_cost_usd_per_mw_year=70_000.0,
        effective_mwh_per_mw_year=600.0,
        source="screening default; replace with customer/program bid data",
        notes="Represents dispatchable load shape relief, not firm transmission capacity.",
    ),
]


@dataclass(frozen=True)
class ConstraintReference:
    iso: str
    constraint_name: str
    binding_hours: float
    severity: float

    def to_text(self) -> str:
        return (
            f"{self.iso}:{self.constraint_name} "
            f"({self.binding_hours:,.0f} h, severity {self.severity:,.0f})"
        )

    def to_row(self) -> Dict[str, Any]:
        return {
            "iso": self.iso,
            "constraint_name": self.constraint_name,
            "binding_hours": self.binding_hours,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class ReliefPoint:
    ba_a: str
    ba_b: str
    benchmark: str
    intervention_mw: float
    relief_mwh: float
    residual_spread_usd_mwh: float
    relief_value_usd: float
    annual_cost_usd: float
    benefit_cost_ratio: float
    cost_per_relieved_dollar: float

    def to_row(self) -> Dict[str, Any]:
        return {
            "ba_a": self.ba_a,
            "ba_b": self.ba_b,
            "benchmark": self.benchmark,
            "intervention_mw": self.intervention_mw,
            "relief_mwh": self.relief_mwh,
            "residual_spread_usd_mwh": self.residual_spread_usd_mwh,
            "relief_value_usd": self.relief_value_usd,
            "annual_cost_usd": self.annual_cost_usd,
            "benefit_cost_ratio": self.benefit_cost_ratio,
            "cost_per_relieved_dollar": self.cost_per_relieved_dollar,
        }


@dataclass(frozen=True)
class ReliefOpportunity:
    ba_a: str
    ba_b: str
    evidence_status: str
    baseline_spread_usd_mwh: float
    gross_mwh: float
    tie_value_cap_usd: float
    active_queue_gw: float
    withdrawn_queue_gw: float
    active_queue_value_cap_usd: float
    withdrawn_queue_value_cap_usd: float
    constraints: List[ConstraintReference]
    points: List[ReliefPoint]

    @property
    def best_point(self) -> ReliefPoint | None:
        if not self.points:
            return None
        return max(
            self.points,
            key=lambda p: (p.benefit_cost_ratio, p.relief_value_usd),
        )

    @property
    def priority_score(self) -> float:
        best = self.best_point
        constraint_pressure = sum(c.severity for c in self.constraints)
        bcr = best.benefit_cost_ratio if best else 0.0
        return bcr * 100.0 + math.log1p(self.tie_value_cap_usd) + math.log1p(constraint_pressure)

    def to_row(self) -> Dict[str, Any]:
        best = self.best_point
        return {
            "ba_a": self.ba_a,
            "ba_b": self.ba_b,
            "evidence_status": self.evidence_status,
            "baseline_spread_usd_mwh": self.baseline_spread_usd_mwh,
            "gross_mwh": self.gross_mwh,
            "tie_value_cap_usd": self.tie_value_cap_usd,
            "active_queue_gw": self.active_queue_gw,
            "withdrawn_queue_gw": self.withdrawn_queue_gw,
            "active_queue_value_cap_usd": self.active_queue_value_cap_usd,
            "withdrawn_queue_value_cap_usd": self.withdrawn_queue_value_cap_usd,
            "best_benchmark": best.benchmark if best else "",
            "best_intervention_mw": best.intervention_mw if best else 0.0,
            "best_relief_value_usd": best.relief_value_usd if best else 0.0,
            "best_annual_cost_usd": best.annual_cost_usd if best else 0.0,
            "best_benefit_cost_ratio": best.benefit_cost_ratio if best else 0.0,
            "best_cost_per_relieved_dollar": (
                best.cost_per_relieved_dollar if best else 0.0
            ),
            "priority_score": self.priority_score,
            "constraints": "; ".join(c.to_text() for c in self.constraints),
        }


@dataclass
class ReliefCurveReport:
    opportunities: List[ReliefOpportunity]
    benchmarks: List[CostBenchmark]
    mw_steps: List[float]

    def ranked(self) -> List[ReliefOpportunity]:
        return sorted(self.opportunities, key=lambda o: o.priority_score, reverse=True)

    def all_points(self) -> List[ReliefPoint]:
        points: List[ReliefPoint] = []
        for opportunity in self.ranked():
            points.extend(opportunity.points)
        return points

    def summary(self, top: int = 8) -> str:
        lines = [
            "Grid relief curves",
            f"  priced ties: {len(self.opportunities)}",
            f"  benchmarks: {', '.join(b.name for b in self.benchmarks)}",
            "  top opportunities:",
        ]
        for opportunity in self.ranked()[:top]:
            best = opportunity.best_point
            if best is None:
                continue
            lines.append(
                f"  {opportunity.ba_a}-{opportunity.ba_b}: {best.benchmark} "
                f"{best.intervention_mw:,.0f} MW, relief ${best.relief_value_usd:,.0f}/yr, "
                f"cost ${best.annual_cost_usd:,.0f}/yr, B/C {best.benefit_cost_ratio:.2f}"
            )
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mw_steps": self.mw_steps,
            "benchmarks": [b.to_row() for b in self.benchmarks],
            "opportunities": [
                {
                    **o.to_row(),
                    "constraints_detail": [c.to_row() for c in o.constraints],
                    "curve_points": [p.to_row() for p in o.points],
                }
                for o in self.ranked()
            ],
        }

    def to_rows(self) -> List[Dict[str, Any]]:
        return [o.to_row() for o in self.ranked()]

    def to_markdown(self, top: int = 25) -> str:
        lines = [
            "# Grid Relief Curves",
            "",
            "## Method",
            "",
            "Each curve evaluates a deterministic structural causal model under "
            "`do(capacity_mw = x)`. Relief is capped by the priced annual tie "
            "value and should be read as screening-grade, not a production-cost simulation.",
            "",
            "## Benchmarks",
            "",
            "| Benchmark | Annualized Cost $/MW-yr | Effective MWh/MW-yr | Source |",
            "|---|---:|---:|---|",
        ]
        for benchmark in self.benchmarks:
            lines.append(
                f"| {benchmark.name} | "
                f"${benchmark.annualized_cost_usd_per_mw_year:,.0f} | "
                f"{benchmark.effective_mwh_per_mw_year:,.0f} | "
                f"{benchmark.source} |"
            )

        lines.extend([
            "",
            "## Ranked Opportunities",
            "",
            "| Tie | Spread $/MWh | Value Cap | Active Queue | Best Benchmark | Relief | Annual Cost | B/C | Constraints |",
            "|---|---:|---:|---:|---|---:|---:|---:|---|",
        ])
        for opportunity in self.ranked()[:top]:
            best = opportunity.best_point
            constraints = "; ".join(c.to_text() for c in opportunity.constraints[:3])
            lines.append(
                f"| {opportunity.ba_a}-{opportunity.ba_b} | "
                f"{opportunity.baseline_spread_usd_mwh:.2f} | "
                f"${opportunity.tie_value_cap_usd:,.0f} | "
                f"{opportunity.active_queue_gw:,.1f} GW | "
                f"{best.benchmark if best else ''} | "
                f"${best.relief_value_usd:,.0f} | "
                f"${best.annual_cost_usd:,.0f} | "
                f"{best.benefit_cost_ratio:.2f} | {constraints} |"
            )
        return "\n".join(lines) + "\n"

    def export_json(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    def export_csv(self, path: str | Path) -> None:
        _write_csv(path, self.to_rows())

    def export_points_csv(self, path: str | Path) -> None:
        _write_csv(path, [p.to_row() for p in self.all_points()])

    def export_markdown(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(), encoding="utf-8")


def build_relief_curve_report(
    queue_match_path: str | Path,
    congestion_report_path: str | Path | None = None,
    constraint_reports: Mapping[str, str | Path] | None = None,
    benchmarks: Sequence[CostBenchmark] | None = None,
    mw_steps: Sequence[float] = (50.0, 100.0, 250.0, 500.0, 1000.0),
) -> ReliefCurveReport:
    queue_ties = json.loads(Path(queue_match_path).read_text(encoding="utf-8")).get("ties", [])
    congestion = _load_congestion_by_key(congestion_report_path) if congestion_report_path else {}
    constraints = _load_constraint_reports(constraint_reports or {})
    benchmarks = list(benchmarks or DEFAULT_BENCHMARKS)
    steps = [float(step) for step in mw_steps if float(step) > 0]

    opportunities: List[ReliefOpportunity] = []
    for tie in queue_ties:
        spread = _float(tie.get("congestion_spread_usd_mwh"))
        value_cap = _float(tie.get("tie_value_cap_usd"))
        if spread <= 0 or value_cap <= 0:
            continue
        ba_a, ba_b = str(tie.get("ba_a", "")), str(tie.get("ba_b", ""))
        key = _tie_key(ba_a, ba_b)
        gross_mwh = value_cap / spread if spread > 0 else _float(
            congestion.get(key, {}).get("gross_mwh")
        )
        if gross_mwh <= 0:
            continue

        points: List[ReliefPoint] = []
        for benchmark in benchmarks:
            scm = build_relief_scm(spread, gross_mwh, benchmark)
            for mw in steps:
                points.append(
                    evaluate_relief_point(ba_a, ba_b, scm, benchmark, mw)
                )

        active = tie.get("active", {})
        withdrawn = tie.get("withdrawn", {})
        opportunities.append(
            ReliefOpportunity(
                ba_a=ba_a,
                ba_b=ba_b,
                evidence_status=str(tie.get("evidence_status", "")),
                baseline_spread_usd_mwh=spread,
                gross_mwh=gross_mwh,
                tie_value_cap_usd=value_cap,
                active_queue_gw=_float(active.get("gw")),
                withdrawn_queue_gw=_float(withdrawn.get("gw")),
                active_queue_value_cap_usd=_float(active.get("capped_value_usd")),
                withdrawn_queue_value_cap_usd=_float(withdrawn.get("capped_value_usd")),
                constraints=_constraints_for_tie(ba_a, ba_b, constraints),
                points=points,
            )
        )

    return ReliefCurveReport(
        opportunities=opportunities,
        benchmarks=benchmarks,
        mw_steps=steps,
    )


def build_relief_scm(
    baseline_spread_usd_mwh: float,
    gross_mwh: float,
    benchmark: CostBenchmark,
) -> SCM:
    """Build a deterministic SCM for one tie and benchmark."""

    gross = max(float(gross_mwh), 1.0)
    spread = max(float(baseline_spread_usd_mwh), 0.0)
    cost_per_mw = max(float(benchmark.annualized_cost_usd_per_mw_year), 0.0)
    mwh_per_mw = max(float(benchmark.effective_mwh_per_mw_year), 0.0)

    model = SCM()
    model.add("capacity_mw", [], lambda _d, _r, n: np.zeros(n))
    model.add(
        "effective_mwh",
        ["capacity_mw"],
        lambda d, _r, _n: d["capacity_mw"] * mwh_per_mw,
    )
    model.add(
        "relief_mwh",
        ["effective_mwh"],
        lambda d, _r, _n: gross * (1.0 - np.exp(-d["effective_mwh"] / gross)),
    )
    model.add(
        "residual_spread",
        ["relief_mwh"],
        lambda d, _r, _n: spread * np.maximum(0.0, 1.0 - d["relief_mwh"] / gross),
    )
    model.add(
        "relief_value_usd",
        ["relief_mwh"],
        lambda d, _r, _n: d["relief_mwh"] * spread,
    )
    model.add(
        "annual_cost_usd",
        ["capacity_mw"],
        lambda d, _r, _n: d["capacity_mw"] * cost_per_mw,
    )
    return model


def evaluate_relief_point(
    ba_a: str,
    ba_b: str,
    scm: SCM,
    benchmark: CostBenchmark,
    intervention_mw: float,
) -> ReliefPoint:
    data = scm.do({"capacity_mw": intervention_mw}).sample(1, seed=0)
    relief_value = float(data["relief_value_usd"][0])
    annual_cost = float(data["annual_cost_usd"][0])
    bcr = relief_value / annual_cost if annual_cost > 0 else 0.0
    return ReliefPoint(
        ba_a=ba_a,
        ba_b=ba_b,
        benchmark=benchmark.name,
        intervention_mw=float(intervention_mw),
        relief_mwh=float(data["relief_mwh"][0]),
        residual_spread_usd_mwh=float(data["residual_spread"][0]),
        relief_value_usd=relief_value,
        annual_cost_usd=annual_cost,
        benefit_cost_ratio=bcr,
        cost_per_relieved_dollar=(annual_cost / relief_value if relief_value > 0 else math.inf),
    )


def _load_congestion_by_key(path: str | Path | None) -> Dict[tuple[str, str], Dict[str, Any]]:
    if path is None or not Path(path).exists():
        return {}
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        _tie_key(str(row.get("ba_a", "")), str(row.get("ba_b", ""))): row
        for row in payload.get("claims", [])
    }


def _load_constraint_reports(
    paths: Mapping[str, str | Path],
    top: int = 5,
) -> Dict[str, List[ConstraintReference]]:
    reports: Dict[str, List[ConstraintReference]] = {}
    for iso, raw_path in paths.items():
        path = Path(raw_path)
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("constraints")
        if isinstance(rows, dict):
            rows = rows.get("table", [])
        if not rows:
            continue
        refs = [
            ConstraintReference(
                iso=iso,
                constraint_name=str(row.get("constraint_name", "")),
                binding_hours=_float(row.get("binding_hours")),
                severity=_float(row.get("severity")),
            )
            for row in rows[:top]
        ]
        reports[iso.upper()] = refs
    return reports


def _constraints_for_tie(
    ba_a: str,
    ba_b: str,
    reports: Mapping[str, List[ConstraintReference]],
    top: int = 6,
) -> List[ConstraintReference]:
    refs: List[ConstraintReference] = []
    for ba in (ba_a.upper(), ba_b.upper()):
        refs.extend(reports.get(ba, []))
        if ba == "SWPP":
            refs.extend(reports.get("SPP", []))
    # Preserve order while removing duplicate constraint names.
    seen = set()
    out = []
    for ref in refs:
        key = (ref.iso, ref.constraint_name)
        if key in seen:
            continue
        seen.add(key)
        out.append(ref)
    return sorted(out, key=lambda r: r.severity, reverse=True)[:top]


def _tie_key(ba_a: str, ba_b: str) -> tuple[str, str]:
    return tuple(sorted((ba_a.strip(), ba_b.strip())))


def _float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    text = str(value).strip().replace(",", "").replace("$", "")
    if not text:
        return 0.0
    try:
        out = float(text)
    except ValueError:
        return 0.0
    return 0.0 if math.isnan(out) else out


def _write_csv(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = _fieldnames(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _fieldnames(rows: List[Dict[str, Any]]) -> List[str]:
    if not rows:
        return ["status"]
    seen = {field for row in rows for field in row}
    preferred = [
        "ba_a",
        "ba_b",
        "evidence_status",
        "benchmark",
        "baseline_spread_usd_mwh",
        "gross_mwh",
        "tie_value_cap_usd",
        "intervention_mw",
        "relief_mwh",
        "residual_spread_usd_mwh",
        "relief_value_usd",
        "annual_cost_usd",
        "benefit_cost_ratio",
        "cost_per_relieved_dollar",
        "active_queue_gw",
        "withdrawn_queue_gw",
        "best_benchmark",
        "best_intervention_mw",
        "best_relief_value_usd",
        "best_annual_cost_usd",
        "best_benefit_cost_ratio",
        "best_cost_per_relieved_dollar",
        "priority_score",
        "constraints",
    ]
    return [field for field in preferred if field in seen] + sorted(seen - set(preferred))
