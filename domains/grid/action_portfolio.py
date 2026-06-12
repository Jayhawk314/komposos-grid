# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Decision portfolio built from the unified grid waste ledger."""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from domains.grid.waste_ledger import EVIDENCE_ORDER, WasteClaim


STATUS_ORDER = {
    "ready_for_scoping": 5,
    "policy_design": 4,
    "validate_proxy": 3,
    "review_required": 2,
    "attach_evidence": 1,
}


@dataclass(frozen=True)
class PortfolioAction:
    action_id: str
    title: str
    decision_status: str
    problem: str
    geography: str
    evidence_level: str
    claim_ids: List[str]
    measured_value_usd: float = 0.0
    proxy_value_usd: float = 0.0
    upper_bound_value_usd: float = 0.0
    quantity_summary: str = ""
    priority_score: float = 0.0
    next_step: str = ""
    rationale: str = ""
    caveat: str = ""

    @property
    def reported_value_usd(self) -> float:
        return self.measured_value_usd + self.proxy_value_usd + self.upper_bound_value_usd

    def to_row(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "title": self.title,
            "decision_status": self.decision_status,
            "problem": self.problem,
            "geography": self.geography,
            "evidence_level": self.evidence_level,
            "claim_ids": "; ".join(self.claim_ids),
            "measured_value_usd": self.measured_value_usd,
            "proxy_value_usd": self.proxy_value_usd,
            "upper_bound_value_usd": self.upper_bound_value_usd,
            "reported_value_usd": self.reported_value_usd,
            "quantity_summary": self.quantity_summary,
            "priority_score": self.priority_score,
            "next_step": self.next_step,
            "rationale": self.rationale,
            "caveat": self.caveat,
        }


@dataclass
class ActionPortfolio:
    actions: List[PortfolioAction]

    def ranked(self) -> List[PortfolioAction]:
        return sorted(
            self.actions,
            key=lambda action: (
                STATUS_ORDER.get(action.decision_status, 0),
                action.priority_score,
                action.reported_value_usd,
            ),
            reverse=True,
        )

    def counts_by_status(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for action in self.actions:
            counts[action.decision_status] = counts.get(action.decision_status, 0) + 1
        return dict(sorted(counts.items()))

    def totals(self) -> Dict[str, float]:
        return {
            "measured_value_usd": sum(a.measured_value_usd for a in self.actions),
            "proxy_value_usd": sum(a.proxy_value_usd for a in self.actions),
            "upper_bound_value_usd": sum(a.upper_bound_value_usd for a in self.actions),
            "reported_value_usd": sum(a.reported_value_usd for a in self.actions),
        }

    def summary(self, top: int = 10) -> str:
        totals = self.totals()
        counts = ", ".join(
            f"{status}={count}" for status, count in self.counts_by_status().items()
        )
        lines = [
            f"Grid action portfolio: {len(self.actions)} actions ({counts})",
            "  reported value: "
            f"${totals['reported_value_usd']:,.0f} "
            f"(measured ${totals['measured_value_usd']:,.0f}; "
            f"proxy ${totals['proxy_value_usd']:,.0f}; "
            f"upper bound ${totals['upper_bound_value_usd']:,.0f})",
            "  top actions:",
        ]
        for action in self.ranked()[:top]:
            value = (
                f", reported ${action.reported_value_usd:,.0f}"
                if action.reported_value_usd
                else ""
            )
            lines.append(
                f"    [{action.decision_status}] {action.title} "
                f"({action.geography}){value}"
            )
        return "\n".join(lines)

    def to_rows(self) -> List[Dict[str, Any]]:
        return [action.to_row() for action in self.ranked()]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_actions": len(self.actions),
            "counts_by_status": self.counts_by_status(),
            "totals": self.totals(),
            "actions": self.to_rows(),
        }

    def to_markdown(self) -> str:
        totals = self.totals()
        lines = [
            "# Grid Action Portfolio",
            "",
            "## Summary",
            "",
            f"- Actions: **{len(self.actions)}**",
            f"- Status mix: **{self.counts_by_status()}**",
            f"- Measured value: **${totals['measured_value_usd']:,.0f}**",
            f"- Proxy value: **${totals['proxy_value_usd']:,.0f}**",
            f"- Upper-bound value: **${totals['upper_bound_value_usd']:,.0f}**",
            f"- Reported value: **${totals['reported_value_usd']:,.0f}**",
            "",
            "## Actions",
            "",
            "| Status | Action | Geography | Evidence | Quantity | Reported Value | Next Step | Caveat |",
            "|---|---|---|---|---:|---:|---|---|",
        ]
        for action in self.ranked():
            value = f"${action.reported_value_usd:,.0f}" if action.reported_value_usd else ""
            lines.append(
                f"| {action.decision_status} | {action.title} | "
                f"{action.geography} | {action.evidence_level} | "
                f"{action.quantity_summary} | {value} | "
                f"{action.next_step} | {action.caveat} |"
            )
        return "\n".join(lines) + "\n"

    def to_html(self, title: str = "Grid Action Portfolio Dashboard") -> str:
        totals = self.totals()
        counts = self.counts_by_status()
        metrics = [
            _metric("Actions", str(len(self.actions)), "ranked decision items"),
            _metric("Measured value", f"${totals['measured_value_usd']:,.0f}", "direct measured dollars"),
            _metric("Proxy value", f"${totals['proxy_value_usd']:,.0f}", "LMP/component/hub proxies"),
            _metric("Upper-bound value", f"${totals['upper_bound_value_usd']:,.0f}", "labeled upper bounds"),
        ]
        rows = [
            [
                action.decision_status,
                action.title,
                action.geography,
                action.evidence_level,
                action.quantity_summary,
                f"${action.reported_value_usd:,.0f}" if action.reported_value_usd else "",
                action.next_step,
                action.caveat,
            ]
            for action in self.ranked()
        ]
        body = [
            '<section class="band summary">'
            "<h2>Actions separated by decision readiness</h2>"
            '<div class="chips">'
            + "".join(
                f'<span class="chip">{escape(status)}: {count}</span>'
                for status, count in counts.items()
            )
            + "</div></section>",
            '<section class="metrics">' + "".join(metrics) + "</section>",
            _section(
                "Actions",
                _table(
                    [
                        "Status",
                        "Action",
                        "Geography",
                        "Evidence",
                        "Quantity",
                        "Value",
                        "Next Step",
                        "Caveat",
                    ],
                    rows,
                    "No actions available.",
                ),
            ),
        ]
        return _page(title, "Decision portfolio derived from the grid waste ledger", body)

    def export_csv(self, path: str | Path) -> None:
        _write_csv(path, self.to_rows())

    def export_json(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    def export_markdown(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(), encoding="utf-8")

    def export_html(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_html(), encoding="utf-8")


def build_action_portfolio(ledger_path: str | Path) -> ActionPortfolio:
    claims = load_ledger_claims(ledger_path)
    by_id = {claim.claim_id: claim for claim in claims}
    actions: List[PortfolioAction] = []

    caiso_claims = [
        c for c in claims if c.claim_id in {
            "caiso_total_curtailment",
            "caiso_local_curtailment",
            "caiso_system_curtailment",
        }
    ]
    if caiso_claims:
        actions.append(_action_from_group(
            action_id="caiso_curtailment_package",
            title="Scope CAISO curtailment reduction package",
            decision_status="ready_for_scoping",
            problem="curtailment",
            geography="CISO",
            claims=caiso_claims,
            quantity_summary=_quantity_for(caiso_claims, "caiso_total_curtailment"),
            next_step="Design storage, flexible-load, and transmission screens around CAISO curtailment windows.",
            rationale="CAISO curtailment is measured and decomposed into local and system causes.",
            caveat="Dollar value is an annual-average-price upper bound, not realized market value.",
        ))

    reliability_claims = [c for c in claims if c.problem == "reliability"]
    if reliability_claims:
        actions.append(_action_from_group(
            action_id="reliability_hardening_package",
            title="Prioritize reliability hardening in highest-burden states",
            decision_status="ready_for_scoping",
            problem="reliability",
            geography="USVI, Maine, Puerto Rico, Michigan, Kentucky",
            claims=reliability_claims,
            quantity_summary=_quantity_for(reliability_claims, "eaglei_total_customer_hours"),
            next_step="Use EAGLE-I/MCC burden rankings to select outage-hardening and distribution-resilience targets.",
            rationale="Outage customer-hours and hours/customer are directly measured from complete 2023 EAGLE-I data.",
            caveat="Customer-hour burden is not monetized here.",
        ))

    queue_claims = [c for c in claims if c.problem == "interconnection_queue"]
    if queue_claims:
        actions.append(_action_from_group(
            action_id="queue_ia_reform_package",
            title="Target queue reform at IA-stage mediators",
            decision_status="policy_design",
            problem="interconnection_queue",
            geography="US interconnection queues",
            claims=queue_claims,
            quantity_summary=_quantity_for(queue_claims, "lbnl_queue_withdrawal_burden"),
            next_step="Study IA-executed completion structure and failure-path IA statuses before proposing process reform.",
            rationale="LBNL decided-project outcomes identify completion and withdrawal mediators.",
            caveat="Mediators are descriptive, not causal proof.",
        ))

    for claim in sorted(
        [c for c in claims if c.evidence_level == "measured_proxy"],
        key=lambda c: c.value_usd,
        reverse=True,
    ):
        is_component_proxy = claim.estimate_kind == "lmp_congestion_component_proxy"
        actions.append(_action_from_group(
            action_id=f"validate_{claim.claim_id}",
            title=f"Validate proxy congestion value for {claim.geography}",
            decision_status="validate_proxy",
            problem=claim.problem,
            geography=claim.geography,
            claims=[claim],
            quantity_summary=f"{claim.quantity:,.0f} {claim.unit}",
            next_step=(
                "Replace component-spread proxy with direct congestion-cost "
                "or flow-attribution evidence."
                if is_component_proxy
                else "Replace hub/price-spread proxy with nodal LMP or direct congestion-cost evidence."
            ),
            rationale=(
                "The corridor has settlement congestion-component evidence "
                "attached to a structural bottleneck."
                if is_component_proxy
                else "The corridor has measured price-spread evidence attached to a structural bottleneck."
            ),
            caveat=(
                "Component spread is stronger than hub price evidence, but "
                "still not direct settlement cost."
                if is_component_proxy
                else _hub_proxy_caveat(claim)
            ),
        ))

    ba_claim = by_id.get("ba_footprint_corrections")
    if ba_claim:
        actions.append(_action_from_group(
            action_id="review_ba_footprint_corrections",
            title="Review BA footprint correction candidates",
            decision_status="review_required",
            problem=ba_claim.problem,
            geography=ba_claim.geography,
            claims=[ba_claim],
            quantity_summary=f"{ba_claim.quantity:,.0f} {ba_claim.unit}",
            next_step="Have a domain reviewer approve, reject, or defer rows in ba_review_template.csv.",
            rationale="Machine validation reduces BA accounting/telemetry mismatch but still needs human approval.",
            caveat="Not an official BA registration change until reviewed.",
        ))

    structural_claims = [c for c in claims if c.evidence_level == "structural_only"]
    if structural_claims:
        actions.append(_action_from_group(
            action_id="attach_evidence_to_structural_bottlenecks",
            title="Attach evidence to remaining structural bottlenecks",
            decision_status="attach_evidence",
            problem="td_losses_congestion",
            geography=", ".join(c.geography for c in structural_claims[:4]),
            claims=structural_claims,
            quantity_summary=f"{sum(c.quantity for c in structural_claims):,.0f} MWh gross interchange under review",
            next_step="Pull nodal LMP, congestion-cost, outage, or planning evidence for the remaining corridors.",
            rationale="Negative-curvature, high-flow ties are plausible congestion candidates.",
            caveat="Topology-only evidence is not counted as measured waste.",
        ))

    return ActionPortfolio(actions=actions)


def load_ledger_claims(path: str | Path) -> List[WasteClaim]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [WasteClaim(**row) for row in payload.get("claims", [])]


def _action_from_group(
    action_id: str,
    title: str,
    decision_status: str,
    problem: str,
    geography: str,
    claims: List[WasteClaim],
    quantity_summary: str,
    next_step: str,
    rationale: str,
    caveat: str,
) -> PortfolioAction:
    measured, proxy, upper = _value_buckets(claims)
    evidence = _dominant_evidence(claims)
    score = _priority_score(decision_status, claims, measured, proxy, upper)
    return PortfolioAction(
        action_id=action_id,
        title=title,
        decision_status=decision_status,
        problem=problem,
        geography=geography,
        evidence_level=evidence,
        claim_ids=[claim.claim_id for claim in claims],
        measured_value_usd=measured,
        proxy_value_usd=proxy,
        upper_bound_value_usd=upper,
        quantity_summary=quantity_summary,
        priority_score=score,
        next_step=next_step,
        rationale=rationale,
        caveat=caveat,
    )


def _value_buckets(claims: List[WasteClaim]) -> tuple[float, float, float]:
    measured = proxy = upper = 0.0
    for claim in claims:
        if claim.evidence_level == "measured_proxy":
            proxy += claim.value_usd
        elif "upper_bound" in claim.estimate_kind:
            upper += claim.value_usd
        elif claim.evidence_level == "measured":
            measured += claim.value_usd
    return measured, proxy, upper


def _dominant_evidence(claims: List[WasteClaim]) -> str:
    return max(
        (claim.evidence_level for claim in claims),
        key=lambda level: EVIDENCE_ORDER.get(level, 0),
        default="structural_only",
    )


def _quantity_for(claims: List[WasteClaim], claim_id: str) -> str:
    for claim in claims:
        if claim.claim_id == claim_id:
            return f"{claim.quantity:,.2f} {claim.unit}"
    if not claims:
        return ""
    claim = claims[0]
    return f"{claim.quantity:,.2f} {claim.unit}"


def _priority_score(
    decision_status: str,
    claims: List[WasteClaim],
    measured: float,
    proxy: float,
    upper: float,
) -> float:
    status = STATUS_ORDER.get(decision_status, 0) * 100.0
    value = math.log10(measured + proxy + upper + 1.0) * 10.0
    evidence = max((EVIDENCE_ORDER.get(c.evidence_level, 0) for c in claims), default=0) * 5.0
    quantity = math.log10(sum(abs(c.quantity) for c in claims) + 1.0)
    return status + value + evidence + quantity


def _hub_proxy_caveat(claim: WasteClaim) -> str:
    base = (
        "Proxy value depends on hub-to-BA mapping and should not be "
        "treated as direct settlement cost."
    )
    notes = claim.notes.lower()
    if "alignment is weak" in notes:
        return f"Hub proxy has weak flow/price alignment; {base}"
    if "alignment is mixed" in notes:
        return f"Hub proxy has mixed flow/price alignment; {base}"
    if "alignment is directionally supportive" in notes:
        return f"Hub proxy is directionally supportive, but {base[0].lower()}{base[1:]}"
    return base


def _write_csv(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = _fields(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _fields(rows: List[Dict[str, Any]]) -> List[str]:
    preferred = [
        "action_id",
        "title",
        "decision_status",
        "problem",
        "geography",
        "evidence_level",
        "claim_ids",
        "measured_value_usd",
        "proxy_value_usd",
        "upper_bound_value_usd",
        "reported_value_usd",
        "quantity_summary",
        "priority_score",
        "next_step",
        "rationale",
        "caveat",
    ]
    seen = {field for row in rows for field in row}
    return [field for field in preferred if field in seen] + sorted(seen - set(preferred))


def _page(title: str, subtitle: str, sections: Iterable[str]) -> str:
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"  <title>{escape(title)}</title>\n"
        f"  <style>{_CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        '  <main class="shell">\n'
        "    <header>\n"
        f"      <h1>{escape(title)}</h1>\n"
        f"      <p>{escape(subtitle)}</p>\n"
        "    </header>\n"
        f"    {''.join(sections)}\n"
        "  </main>\n"
        "</body>\n"
        "</html>\n"
    )


def _metric(label: str, value: str, detail: str) -> str:
    return (
        '<article class="metric">'
        f"<span>{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        f"<small>{escape(detail)}</small>"
        "</article>"
    )


def _section(title: str, content: str) -> str:
    return (
        '<section class="band">'
        f"<h2>{escape(title)}</h2>"
        f"{content}"
        "</section>"
    )


def _table(headers: Sequence[str], rows: Sequence[Sequence[Any]], empty: str) -> str:
    if not rows:
        return f'<p class="empty">{escape(empty)}</p>'
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body = []
    for row in rows:
        body.append(
            "<tr>"
            + "".join(f"<td>{escape(str(cell))}</td>" for cell in row)
            + "</tr>"
        )
    return (
        '<div class="table-wrap">'
        "<table>"
        f"<thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body)}</tbody>"
        "</table>"
        "</div>"
    )


_CSS = """
:root {
  color-scheme: light;
  --ink: #17202a;
  --muted: #5b6673;
  --line: #d8dee6;
  --surface: #ffffff;
  --page: #f5f7fa;
  --blue: #1f6feb;
  --green: #1f8f5f;
  --amber: #b7791f;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--page);
  color: var(--ink);
  font: 14px/1.5 Arial, Helvetica, sans-serif;
}
.shell {
  width: min(1280px, calc(100vw - 32px));
  margin: 0 auto;
  padding: 28px 0 40px;
}
header {
  border-bottom: 1px solid var(--line);
  margin-bottom: 18px;
  padding-bottom: 16px;
}
h1 {
  font-size: clamp(26px, 4vw, 38px);
  line-height: 1.1;
  margin: 0 0 8px;
  letter-spacing: 0;
}
h2 {
  font-size: 18px;
  line-height: 1.25;
  margin: 0 0 14px;
  letter-spacing: 0;
}
p { margin: 0; color: var(--muted); }
.band {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  margin: 16px 0;
  padding: 18px;
}
.summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.summary h2 { margin: 0; }
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chip {
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #fbfcfe;
  padding: 6px 10px;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 12px;
  margin: 16px 0;
}
.metric {
  min-height: 128px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-top: 4px solid var(--blue);
  border-radius: 8px;
  padding: 14px;
  display: grid;
  gap: 6px;
  align-content: start;
}
.metric:nth-child(2n) { border-top-color: var(--green); }
.metric:nth-child(3n) { border-top-color: var(--amber); }
.metric span {
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
}
.metric strong {
  font-size: 24px;
  line-height: 1.05;
  letter-spacing: 0;
}
.metric small { color: var(--muted); }
.table-wrap { overflow-x: auto; }
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1040px;
}
th, td {
  border-bottom: 1px solid var(--line);
  padding: 9px 10px;
  text-align: left;
  vertical-align: top;
}
th {
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  background: #fbfcfe;
}
tr:hover td { background: #f9fbfd; }
.empty {
  border: 1px dashed var(--line);
  border-radius: 8px;
  padding: 14px;
}
@media (max-width: 640px) {
  .shell { width: min(100vw - 20px, 1280px); padding-top: 18px; }
  .band { padding: 14px; }
  .metric { min-height: 116px; }
  .metric strong { font-size: 21px; }
}
"""
