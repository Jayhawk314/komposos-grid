# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Unified ledger of grid-waste claims across evidence layers."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence


EVIDENCE_ORDER = {
    "measured": 4,
    "measured_proxy": 3,
    "validated_hypothesis": 2,
    "structural_only": 1,
}


@dataclass(frozen=True)
class WasteClaim:
    claim_id: str
    problem: str
    title: str
    geography: str
    evidence_level: str
    estimate_kind: str
    quantity: float
    unit: str
    value_usd: float = 0.0
    confidence: str = ""
    source: str = ""
    source_report: str = ""
    recommended_action: str = ""
    notes: str = ""

    def to_row(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "problem": self.problem,
            "title": self.title,
            "geography": self.geography,
            "evidence_level": self.evidence_level,
            "estimate_kind": self.estimate_kind,
            "quantity": self.quantity,
            "unit": self.unit,
            "value_usd": self.value_usd,
            "confidence": self.confidence,
            "source": self.source,
            "source_report": self.source_report,
            "recommended_action": self.recommended_action,
            "notes": self.notes,
        }


@dataclass
class WasteLedger:
    claims: List[WasteClaim]

    def ranked(self) -> List[WasteClaim]:
        return sorted(
            self.claims,
            key=lambda c: (
                EVIDENCE_ORDER.get(c.evidence_level, 0),
                c.value_usd,
                c.quantity,
            ),
            reverse=True,
        )

    def total_value_usd(self, evidence_levels: Iterable[str]) -> float:
        levels = set(evidence_levels)
        return sum(c.value_usd for c in self.claims if c.evidence_level in levels)

    def counts_by_evidence(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for claim in self.claims:
            counts[claim.evidence_level] = counts.get(claim.evidence_level, 0) + 1
        return dict(sorted(counts.items()))

    def summary(self, top: int = 12) -> str:
        counts = ", ".join(
            f"{level}={count}" for level, count in self.counts_by_evidence().items()
        )
        lines = [
            f"Grid waste ledger: {len(self.claims)} claims ({counts})",
            "  reported/proxy dollar total: "
            f"${self.total_value_usd(['measured', 'measured_proxy']):,.0f}",
            "  top claims:",
        ]
        for claim in self.ranked()[:top]:
            value = f", ${claim.value_usd:,.0f}" if claim.value_usd else ""
            lines.append(
                f"    [{claim.evidence_level}] {claim.title} "
                f"({claim.geography}): {claim.quantity:,.2f} {claim.unit}{value}"
            )
        return "\n".join(lines)

    def to_rows(self) -> List[Dict[str, Any]]:
        return [claim.to_row() for claim in self.ranked()]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_claims": len(self.claims),
            "counts_by_evidence": self.counts_by_evidence(),
            "measured_value_usd": self.total_value_usd(["measured"]),
            "measured_or_proxy_value_usd": self.total_value_usd([
                "measured",
                "measured_proxy",
            ]),
            "claims": self.to_rows(),
        }

    def to_markdown(self) -> str:
        lines = [
            "# Grid Waste Ledger",
            "",
            "## Summary",
            "",
            f"- Claims: **{len(self.claims)}**",
            f"- Evidence mix: **{self.counts_by_evidence()}**",
            f"- Measured/upper-bound dollar total: "
            f"**${self.total_value_usd(['measured']):,.0f}**",
            f"- Reported/proxy dollar total: "
            f"**${self.total_value_usd(['measured', 'measured_proxy']):,.0f}**",
            "",
            "## Claims",
            "",
            "| Evidence | Problem | Geography | Claim | Quantity | Value | Action |",
            "|---|---|---|---|---:|---:|---|",
        ]
        for claim in self.ranked():
            value = f"${claim.value_usd:,.0f}" if claim.value_usd else ""
            lines.append(
                f"| {claim.evidence_level} | {claim.problem} | "
                f"{claim.geography} | {claim.title} | "
                f"{claim.quantity:,.2f} {claim.unit} | {value} | "
                f"{claim.recommended_action} |"
            )
        return "\n".join(lines) + "\n"

    def to_html(self, title: str = "Grid Waste Ledger Dashboard") -> str:
        counts = self.counts_by_evidence()
        metrics = [
            _metric("Claims", str(len(self.claims)), "all evidence levels"),
            _metric(
                "Measured/upper-bound value",
                f"${self.total_value_usd(['measured']):,.0f}",
                "direct dollar claims and labeled upper bounds",
            ),
            _metric(
                "Reported/proxy value",
                f"${self.total_value_usd(['measured', 'measured_proxy']):,.0f}",
                "includes explicit price-spread proxies",
            ),
            _metric(
                "Structural only",
                str(counts.get("structural_only", 0)),
                "not counted as measured waste",
            ),
        ]
        rows = [
            [
                claim.evidence_level,
                claim.problem,
                claim.geography,
                claim.title,
                f"{claim.quantity:,.2f} {claim.unit}",
                f"${claim.value_usd:,.0f}" if claim.value_usd else "",
                claim.recommended_action,
            ]
            for claim in self.ranked()
        ]
        body = [
            '<section class="band summary">'
            "<h2>Evidence-separated waste claims</h2>"
            '<div class="chips">'
            + "".join(
                f'<span class="chip">{escape(level)}: {count}</span>'
                for level, count in counts.items()
            )
            + "</div></section>",
            '<section class="metrics">' + "".join(metrics) + "</section>",
            _section(
                "Claims",
                _table(
                    [
                        "Evidence",
                        "Problem",
                        "Geography",
                        "Claim",
                        "Quantity",
                        "Value",
                        "Action",
                    ],
                    rows,
                    "No claims available.",
                ),
            ),
        ]
        return _page(title, "Measured, proxy, hypothesis, and structural claims", body)

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


def build_waste_ledger(
    ba_footprint_report: str | Path | None = None,
    congestion_report: str | Path | None = None,
    flow_report: str | Path | None = None,
    outage_report: str | Path | None = None,
    caiso_curtailment: str | Path | None = None,
    curtailment_avg_price: float | None = None,
    queue_workbook: str | Path | None = None,
    queue_min_cohort: int = 30,
) -> WasteLedger:
    claims: List[WasteClaim] = []
    if ba_footprint_report and Path(ba_footprint_report).exists():
        claims.extend(claims_from_ba_footprint(ba_footprint_report))
    if congestion_report and Path(congestion_report).exists():
        claims.extend(claims_from_congestion_report(congestion_report))
    elif flow_report and Path(flow_report).exists():
        claims.extend(claims_from_flow_report(flow_report))
    if outage_report and Path(outage_report).exists():
        claims.extend(claims_from_outage_report(outage_report))
    if caiso_curtailment and Path(caiso_curtailment).exists():
        claims.extend(
            claims_from_curtailment(
                caiso_curtailment,
                avg_price_usd_mwh=curtailment_avg_price,
            )
        )
    if queue_workbook and Path(queue_workbook).exists():
        claims.extend(
            claims_from_queue(queue_workbook, min_cohort=queue_min_cohort)
        )
    return WasteLedger(claims=claims)


def claims_from_ba_footprint(path: str | Path) -> List[WasteClaim]:
    payload = _read_json(path)
    before = payload.get("before", {})
    after = payload.get("after", {})
    improvement = float(before.get("abs_error_mwh", 0.0)) - float(
        after.get("abs_error_mwh", 0.0)
    )
    return [
        WasteClaim(
            claim_id="ba_footprint_corrections",
            problem="data_coherence",
            title="BA footprint correction reduces accounting/telemetry mismatch",
            geography="US balancing authorities",
            evidence_level="validated_hypothesis",
            estimate_kind="accounting_error_reduction",
            quantity=improvement,
            unit="MWh BA absolute-error reduction",
            confidence=(
                f"{payload.get('accepted_corrections', 0)} accepted machine "
                f"candidates; human review pending"
            ),
            source="eGRID/EIA-923/EIA-930 coherence",
            source_report=str(path),
            recommended_action="Review BA correction template and approve defensible rows.",
            notes=(
                f"Agreement {float(before.get('agreement_rate', 0.0)):.1%} -> "
                f"{float(after.get('agreement_rate', 0.0)):.1%}; "
                f"contradictions {before.get('contradictions')} -> "
                f"{after.get('contradictions')}."
            ),
        )
    ]


def claims_from_congestion_report(path: str | Path, top_structural: int = 8) -> List[WasteClaim]:
    payload = _read_json(path)
    claims: List[WasteClaim] = []
    structural_count = 0
    for row in payload.get("claims", []):
        status = str(row.get("evidence_status", "structural_only"))
        ba_a = row.get("ba_a", "")
        ba_b = row.get("ba_b", "")
        value = _float(row.get("estimated_value_usd"))
        if status == "measured_cost":
            evidence = "measured"
            kind = "measured_congestion_cost"
            action = "Prioritize transmission or operational mitigation; cost evidence attached."
        elif status == "lmp_component_proxy":
            evidence = "measured_proxy"
            kind = "lmp_congestion_component_proxy"
            action = "Validate flow attribution and replace proxy with direct congestion cost."
        elif status == "price_spread_proxy":
            evidence = "measured_proxy"
            kind = "lmp_spread_proxy"
            action = "Validate hub-to-BA mapping and replace proxy with direct congestion cost."
        else:
            structural_count += 1
            if structural_count > top_structural:
                continue
            evidence = "structural_only"
            kind = "flow_weighted_negative_curvature"
            action = "Attach LMP spread, congestion cost, outage, or planning evidence."
        claims.append(
            WasteClaim(
                claim_id=f"congestion_{ba_a}_{ba_b}".lower(),
                problem="td_losses_congestion",
                title=f"{ba_a}-{ba_b} congestion/bottleneck candidate",
                geography=f"{ba_a}-{ba_b}",
                evidence_level=evidence,
                estimate_kind=kind,
                quantity=_float(row.get("gross_mwh")),
                unit="MWh gross interchange",
                value_usd=value,
                confidence=status,
                source=str(row.get("evidence_source", "EIA-930 flow geometry")),
                source_report=str(path),
                recommended_action=action,
                notes=str(row.get("notes", "")),
            )
        )
    return claims


def claims_from_flow_report(path: str | Path, top: int = 8) -> List[WasteClaim]:
    payload = _read_json(path)
    claims: List[WasteClaim] = []
    for row in payload.get("bottlenecks", [])[:top]:
        ba_a, ba_b = row.get("ba_a", ""), row.get("ba_b", "")
        claims.append(
            WasteClaim(
                claim_id=f"flow_bottleneck_{ba_a}_{ba_b}".lower(),
                problem="td_losses_congestion",
                title=f"{ba_a}-{ba_b} structural flow bottleneck",
                geography=f"{ba_a}-{ba_b}",
                evidence_level="structural_only",
                estimate_kind="flow_weighted_negative_curvature",
                quantity=_float(row.get("gross_mwh")),
                unit="MWh gross interchange",
                confidence=f"curvature {_float(row.get('curvature')):+.3f}",
                source="EIA-930 interchange flow geometry",
                source_report=str(path),
                recommended_action="Attach LMP spread or congestion-cost evidence.",
                notes=f"Priority score {_float(row.get('priority_score')):,.0f}.",
            )
        )
    return claims


def claims_from_outage_report(path: str | Path, top_states: int = 5) -> List[WasteClaim]:
    payload = _read_json(path)
    claims = [
        WasteClaim(
            claim_id="eaglei_total_customer_hours",
            problem="reliability",
            title="Total customer-hours lost in EAGLE-I",
            geography="United States and territories",
            evidence_level="measured",
            estimate_kind="customer_hours",
            quantity=_float(payload.get("total_customer_hours")),
            unit="customer-hours",
            confidence=str(payload.get("coverage_note", "")),
            source="EAGLE-I outages with MCC denominators",
            source_report=str(path),
            recommended_action="Target reliability investments in highest burden states.",
            notes=(
                f"{payload.get('rows_processed', 0):,} rows; "
                f"{payload.get('first_timestamp')} -> {payload.get('last_timestamp')}."
            ),
        )
    ]
    for row in payload.get("states", [])[:top_states]:
        state = row.get("state", "")
        claims.append(
            WasteClaim(
                claim_id=f"outage_burden_{state}".lower().replace(" ", "_"),
                problem="reliability",
                title=f"{state} outage burden",
                geography=str(state),
                evidence_level="measured",
                estimate_kind="hours_per_customer",
                quantity=_float(row.get("hours_per_customer")),
                unit="hours/customer",
                confidence="normalized by MCC customer count",
                source="EAGLE-I outages with MCC denominators",
                source_report=str(path),
                recommended_action="Investigate storm hardening and distribution reliability programs.",
                notes=(
                    f"{_float(row.get('customer_hours')):,.0f} customer-hours; "
                    f"{_float(row.get('customer_hours_share')):.1%} of observed burden."
                ),
            )
        )
    return claims


def claims_from_curtailment(
    workbook_path: str | Path,
    avg_price_usd_mwh: float | None = None,
) -> List[WasteClaim]:
    from domains.grid.curtailment import load_caiso_report

    report = load_caiso_report(
        workbook_path,
        avg_price_usd_mwh=avg_price_usd_mwh,
    )
    total = report.total()
    local = report.by_reason("Local")
    system = report.by_reason("System")
    value = total * avg_price_usd_mwh if avg_price_usd_mwh else 0.0
    return [
        WasteClaim(
            claim_id="caiso_total_curtailment",
            problem="curtailment",
            title="CAISO renewable curtailment",
            geography=report.ba,
            evidence_level="measured",
            estimate_kind="energy_upper_bound_value" if value else "energy",
            quantity=total,
            unit="MWh curtailed renewable energy",
            value_usd=value,
            confidence="value is upper bound at annual average price" if value else "",
            source="CAISO production and curtailments workbook",
            source_report=str(workbook_path),
            recommended_action="Target storage, flexible load, and transmission for curtailment windows.",
            notes=(
                f"Solar share {report.share('solar'):.1%}; "
                f"wind share {report.share('wind'):.1%}."
            ),
        ),
        WasteClaim(
            claim_id="caiso_local_curtailment",
            problem="td_losses_congestion",
            title="CAISO local congestion-driven curtailment",
            geography=report.ba,
            evidence_level="measured",
            estimate_kind="curtailment_reason_local",
            quantity=local,
            unit="MWh locally constrained curtailment",
            source="CAISO production and curtailments workbook",
            source_report=str(workbook_path),
            recommended_action="Join local curtailment to flow bottlenecks and transmission constraints.",
            notes=f"{local / total:.1%} of total curtailment." if total else "",
        ),
        WasteClaim(
            claim_id="caiso_system_curtailment",
            problem="curtailment",
            title="CAISO system oversupply curtailment",
            geography=report.ba,
            evidence_level="measured",
            estimate_kind="curtailment_reason_system",
            quantity=system,
            unit="MWh system oversupply curtailment",
            source="CAISO production and curtailments workbook",
            source_report=str(workbook_path),
            recommended_action="Target storage and flexible demand during oversupply windows.",
            notes=f"{system / total:.1%} of total curtailment." if total else "",
        ),
    ]


def claims_from_queue(
    workbook_path: str | Path,
    min_cohort: int = 30,
) -> List[WasteClaim]:
    from domains.grid.queue_analysis import analyze_queue
    from domains.grid.sources.lbnl_queue import LBNLQueueSource

    report = analyze_queue(
        LBNLQueueSource(workbook_path).load(),
        min_cohort=min_cohort,
    )
    withdrawal_rate = 1.0 - report.overall_completion
    claims = [
        WasteClaim(
            claim_id="lbnl_queue_withdrawal_burden",
            problem="interconnection_queue",
            title="LBNL queue decided-project attrition",
            geography="US interconnection queues",
            evidence_level="measured",
            estimate_kind="withdrawal_rate_decided_projects",
            quantity=withdrawal_rate,
            unit="withdrawal share of decided projects",
            confidence=f"{report.n_decided:,} decided projects",
            source="LBNL Queued Up interconnection queue",
            source_report=str(workbook_path),
            recommended_action="Focus queue reform on cohorts that mediate withdrawal and completion.",
            notes=f"Overall completion {report.overall_completion:.1%}.",
        )
    ]
    if report.operational_intermediates:
        cohort, rate, n = report.operational_intermediates[0]
        claims.append(
            WasteClaim(
                claim_id="lbnl_queue_top_completion_mediator",
                problem="interconnection_queue",
                title=f"Top completion mediator: {cohort}",
                geography="US interconnection queues",
                evidence_level="measured",
                estimate_kind="completion_mediator",
                quantity=rate / report.overall_completion if report.overall_completion else 0.0,
                unit="x direct completion rate",
                confidence=f"n={n}; completion {rate:.1%}",
                source="LBNL Queued Up + OPTIMUS factorization",
                source_report=str(workbook_path),
                recommended_action="Study why this cohort completes and transfer the structure.",
                notes=f"Direct completion {report.overall_completion:.1%}.",
            )
        )
    if report.withdrawal_intermediates:
        cohort, rate, n = report.withdrawal_intermediates[0]
        claims.append(
            WasteClaim(
                claim_id="lbnl_queue_top_withdrawal_mediator",
                problem="interconnection_queue",
                title=f"Top withdrawal mediator: {cohort}",
                geography="US interconnection queues",
                evidence_level="measured",
                estimate_kind="withdrawal_mediator",
                quantity=rate,
                unit="withdrawal rate",
                confidence=f"n={n}",
                source="LBNL Queued Up + OPTIMUS factorization",
                source_report=str(workbook_path),
                recommended_action="Treat this queue state as a failure-path intervention target.",
                notes="Descriptive mediator, not causal proof.",
            )
        )
    return claims


def _read_json(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


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
        "claim_id",
        "problem",
        "title",
        "geography",
        "evidence_level",
        "estimate_kind",
        "quantity",
        "unit",
        "value_usd",
        "confidence",
        "source",
        "source_report",
        "recommended_action",
        "notes",
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
  min-width: 960px;
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
