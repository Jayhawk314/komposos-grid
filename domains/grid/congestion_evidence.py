# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Join structural BA flow bottlenecks to measured congestion evidence."""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence


@dataclass(frozen=True)
class FlowBottleneckRecord:
    ba_a: str
    ba_b: str
    curvature: float
    gross_mwh: float
    net_mwh: float
    net_direction: str
    gross_share: float
    priority_score: float

    @property
    def key(self) -> tuple[str, str]:
        return tie_key(self.ba_a, self.ba_b)


@dataclass(frozen=True)
class CongestionEvidence:
    ba_a: str
    ba_b: str
    evidence_source: str = ""
    mean_price_spread_usd_mwh: float = 0.0
    max_price_spread_usd_mwh: float = 0.0
    congestion_cost_usd: float = 0.0
    hours_observed: float = 0.0
    notes: str = ""

    @property
    def key(self) -> tuple[str, str]:
        return tie_key(self.ba_a, self.ba_b)

    @property
    def has_measured_cost(self) -> bool:
        return self.congestion_cost_usd > 0

    @property
    def has_price_spread(self) -> bool:
        return self.mean_price_spread_usd_mwh > 0 or self.max_price_spread_usd_mwh > 0


@dataclass(frozen=True)
class CongestionClaim:
    bottleneck: FlowBottleneckRecord
    evidence: CongestionEvidence | None = None

    @property
    def evidence_status(self) -> str:
        if self.evidence is None:
            return "structural_only"
        if self.evidence.has_measured_cost:
            return "measured_cost"
        if self.evidence.has_price_spread:
            return "price_spread_proxy"
        return "evidence_attached"

    @property
    def estimated_value_usd(self) -> float:
        if self.evidence is None:
            return 0.0
        if self.evidence.congestion_cost_usd > 0:
            return self.evidence.congestion_cost_usd
        if self.evidence.mean_price_spread_usd_mwh > 0:
            return self.evidence.mean_price_spread_usd_mwh * self.bottleneck.gross_mwh
        return 0.0

    @property
    def combined_priority(self) -> float:
        """Measured value first, structural score as a tie-breaker."""
        if self.estimated_value_usd > 0:
            return self.estimated_value_usd + math.log1p(self.bottleneck.priority_score)
        return self.bottleneck.priority_score


@dataclass
class CongestionEvidenceReport:
    """Structural bottlenecks annotated with measured congestion evidence."""

    source_flow_report: str
    claims: List[CongestionClaim]

    @property
    def matched_claims(self) -> List[CongestionClaim]:
        return [claim for claim in self.claims if claim.evidence is not None]

    @property
    def measured_claims(self) -> List[CongestionClaim]:
        return [
            claim
            for claim in self.claims
            if claim.evidence_status in {"measured_cost", "price_spread_proxy"}
        ]

    @property
    def structural_only_claims(self) -> List[CongestionClaim]:
        return [claim for claim in self.claims if claim.evidence is None]

    @property
    def total_estimated_value_usd(self) -> float:
        return sum(claim.estimated_value_usd for claim in self.measured_claims)

    def ranked_claims(self) -> List[CongestionClaim]:
        return sorted(
            self.claims,
            key=lambda claim: (
                claim.evidence is not None,
                claim.estimated_value_usd,
                claim.bottleneck.priority_score,
            ),
            reverse=True,
        )

    def summary(self, top: int = 10) -> str:
        lines = [
            "Congestion evidence report",
            f"  bottlenecks: {len(self.claims)}; evidence matched: "
            f"{len(self.matched_claims)}; measured/proxy claims: "
            f"{len(self.measured_claims)}",
            f"  estimated measured/proxy value: "
            f"${self.total_estimated_value_usd:,.0f}",
        ]
        if not self.measured_claims:
            lines.append(
                "  no measured LMP/congestion evidence attached yet; "
                "use the template CSV to create measured claims"
            )
        for claim in self.ranked_claims()[:top]:
            b = claim.bottleneck
            lines.append(
                f"  {b.ba_a} -- {b.ba_b}: {claim.evidence_status}, "
                f"curvature {b.curvature:+.3f}, gross {b.gross_mwh / 1e6:,.1f} TWh, "
                f"value ${claim.estimated_value_usd:,.0f}"
            )
        return "\n".join(lines)

    def to_rows(self, top: int | None = None) -> List[Dict[str, Any]]:
        claims = self.ranked_claims()
        if top is not None:
            claims = claims[:top]
        rows: List[Dict[str, Any]] = []
        for claim in claims:
            b = claim.bottleneck
            e = claim.evidence
            rows.append({
                "ba_a": b.ba_a,
                "ba_b": b.ba_b,
                "evidence_status": claim.evidence_status,
                "curvature": b.curvature,
                "gross_mwh": b.gross_mwh,
                "gross_share": b.gross_share,
                "net_direction": b.net_direction,
                "net_mwh": b.net_mwh,
                "structural_priority_score": b.priority_score,
                "combined_priority": claim.combined_priority,
                "estimated_value_usd": claim.estimated_value_usd,
                "evidence_source": e.evidence_source if e else "",
                "mean_price_spread_usd_mwh": (
                    e.mean_price_spread_usd_mwh if e else ""
                ),
                "max_price_spread_usd_mwh": e.max_price_spread_usd_mwh if e else "",
                "congestion_cost_usd": e.congestion_cost_usd if e else "",
                "hours_observed": e.hours_observed if e else "",
                "notes": e.notes if e else "",
            })
        return rows

    def to_dict(self, top: int = 50) -> Dict[str, Any]:
        return {
            "source_flow_report": self.source_flow_report,
            "n_bottlenecks": len(self.claims),
            "evidence_matched": len(self.matched_claims),
            "measured_or_proxy_claims": len(self.measured_claims),
            "total_estimated_value_usd": self.total_estimated_value_usd,
            "claims": self.to_rows(top=top),
        }

    def to_markdown(self, top: int = 25) -> str:
        lines = [
            "# Congestion Evidence Report",
            "",
            "## Result",
            "",
            f"- Structural bottlenecks: **{len(self.claims)}**",
            f"- Evidence matched: **{len(self.matched_claims)}**",
            f"- Measured/proxy claims: **{len(self.measured_claims)}**",
            f"- Estimated measured/proxy value: "
            f"**${self.total_estimated_value_usd:,.0f}**",
            "",
            "## Ranked Claims",
            "",
            "| Tie | Evidence | Curvature | Gross MWh | Estimated Value | Source | Notes |",
            "|---|---|---:|---:|---:|---|---|",
        ]
        if not self.claims:
            lines.append("| None |  |  |  |  |  |  |")
        for claim in self.ranked_claims()[:top]:
            b = claim.bottleneck
            e = claim.evidence
            lines.append(
                f"| {b.ba_a} - {b.ba_b} | {claim.evidence_status} | "
                f"{b.curvature:+.3f} | {b.gross_mwh:,.0f} | "
                f"${claim.estimated_value_usd:,.0f} | "
                f"{e.evidence_source if e else ''} | {e.notes if e else ''} |"
            )
        return "\n".join(lines) + "\n"

    def to_html(self, title: str = "Congestion Evidence Dashboard", top: int = 25) -> str:
        metrics = [
            _metric("Bottlenecks", str(len(self.claims)), "structural candidates"),
            _metric("Evidence matched", str(len(self.matched_claims)), "rows joined by BA tie"),
            _metric("Measured/proxy claims", str(len(self.measured_claims)), "cost or LMP spread"),
            _metric(
                "Estimated value",
                f"${self.total_estimated_value_usd:,.0f}",
                "sum of measured/proxy claims",
            ),
        ]
        rows = [
            [
                f"{row['ba_a']} - {row['ba_b']}",
                row["evidence_status"],
                f"{row['curvature']:+.3f}",
                _mwh(float(row["gross_mwh"])),
                f"${float(row['estimated_value_usd']):,.0f}",
                row["evidence_source"],
                row["notes"],
            ]
            for row in self.to_rows(top=top)
        ]
        body = [
            '<section class="band summary">'
            "<h2>Structural bottlenecks plus measured evidence</h2>"
            '<div class="chips">'
            f'<span class="chip">{len(self.matched_claims)} evidence matches</span>'
            f'<span class="chip">${self.total_estimated_value_usd:,.0f} estimated</span>'
            "</div>"
            "</section>",
            '<section class="metrics">' + "".join(metrics) + "</section>",
            _section(
                "Ranked Claims",
                _table(
                    ["Tie", "Evidence", "Curvature", "Gross MWh", "Value", "Source", "Notes"],
                    rows,
                    "No congestion evidence claims available.",
                ),
            ),
        ]
        return _page(
            title,
            "Flow bottlenecks joined to LMP spread or congestion-cost evidence",
            body,
        )

    def export_csv(self, path: str | Path, top: int | None = None) -> None:
        _write_csv(path, self.to_rows(top=top))

    def export_markdown(self, path: str | Path, top: int = 25) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(top=top), encoding="utf-8")

    def export_json(self, path: str | Path, top: int = 50) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(top=top), indent=2), encoding="utf-8")

    def export_html(
        self,
        path: str | Path,
        title: str = "Congestion Evidence Dashboard",
        top: int = 25,
    ) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_html(title=title, top=top), encoding="utf-8")


def tie_key(ba_a: str, ba_b: str) -> tuple[str, str]:
    return tuple(sorted((str(ba_a).strip(), str(ba_b).strip())))


def load_flow_bottlenecks(path: str | Path) -> List[FlowBottleneckRecord]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    records: List[FlowBottleneckRecord] = []
    for row in payload.get("bottlenecks", []):
        records.append(
            FlowBottleneckRecord(
                ba_a=str(row["ba_a"]),
                ba_b=str(row["ba_b"]),
                curvature=float(row.get("curvature", 0.0)),
                gross_mwh=float(row.get("gross_mwh", 0.0)),
                net_mwh=float(row.get("net_mwh", 0.0)),
                net_direction=str(row.get("net_direction", "")),
                gross_share=float(row.get("gross_share", 0.0)),
                priority_score=float(row.get("priority_score", 0.0)),
            )
        )
    return records


def load_congestion_evidence_csv(paths: Iterable[str | Path]) -> Dict[tuple[str, str], CongestionEvidence]:
    evidence: Dict[tuple[str, str], CongestionEvidence] = {}
    for path in paths:
        with Path(path).open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                item = evidence_from_row(row)
                if item.key in evidence:
                    evidence[item.key] = merge_evidence(evidence[item.key], item)
                else:
                    evidence[item.key] = item
    return evidence


def evidence_from_row(row: Mapping[str, Any]) -> CongestionEvidence:
    ba_a = _first(row, ["ba_a", "source_ba", "from_ba", "ba1", "source"])
    ba_b = _first(row, ["ba_b", "target_ba", "to_ba", "ba2", "target"])
    if not ba_a or not ba_b:
        raise ValueError("congestion evidence rows require ba_a/ba_b or source/target columns")
    return CongestionEvidence(
        ba_a=ba_a,
        ba_b=ba_b,
        evidence_source=_first(row, ["evidence_source", "source_name", "dataset"]),
        mean_price_spread_usd_mwh=_float(
            _first(row, [
                "mean_price_spread_usd_mwh",
                "avg_price_spread_usd_mwh",
                "price_spread_usd_mwh",
                "mean_lmp_spread",
            ])
        ),
        max_price_spread_usd_mwh=_float(
            _first(row, ["max_price_spread_usd_mwh", "max_lmp_spread"])
        ),
        congestion_cost_usd=_float(
            _first(row, ["congestion_cost_usd", "annual_congestion_cost_usd", "cost_usd"])
        ),
        hours_observed=_float(_first(row, ["hours_observed", "hours", "n_hours"])),
        notes=_first(row, ["notes", "note", "comment"]),
    )


def merge_evidence(a: CongestionEvidence, b: CongestionEvidence) -> CongestionEvidence:
    return CongestionEvidence(
        ba_a=a.ba_a,
        ba_b=a.ba_b,
        evidence_source="; ".join(x for x in [a.evidence_source, b.evidence_source] if x),
        mean_price_spread_usd_mwh=max(
            a.mean_price_spread_usd_mwh,
            b.mean_price_spread_usd_mwh,
        ),
        max_price_spread_usd_mwh=max(
            a.max_price_spread_usd_mwh,
            b.max_price_spread_usd_mwh,
        ),
        congestion_cost_usd=a.congestion_cost_usd + b.congestion_cost_usd,
        hours_observed=a.hours_observed + b.hours_observed,
        notes="; ".join(x for x in [a.notes, b.notes] if x),
    )


def build_congestion_evidence_report(
    flow_report_path: str | Path,
    evidence: Mapping[tuple[str, str], CongestionEvidence] | None = None,
) -> CongestionEvidenceReport:
    bottlenecks = load_flow_bottlenecks(flow_report_path)
    evidence = evidence or {}
    claims = [
        CongestionClaim(bottleneck=item, evidence=evidence.get(item.key))
        for item in bottlenecks
    ]
    return CongestionEvidenceReport(
        source_flow_report=str(flow_report_path),
        claims=claims,
    )


def evidence_template_rows(
    flow_report_path: str | Path,
    top: int = 25,
) -> List[Dict[str, Any]]:
    rows = []
    for item in load_flow_bottlenecks(flow_report_path)[:top]:
        rows.append({
            "ba_a": item.ba_a,
            "ba_b": item.ba_b,
            "curvature": item.curvature,
            "gross_mwh": item.gross_mwh,
            "gross_share": item.gross_share,
            "net_direction": item.net_direction,
            "net_mwh": item.net_mwh,
            "structural_priority_score": item.priority_score,
            "evidence_source": "",
            "mean_price_spread_usd_mwh": "",
            "max_price_spread_usd_mwh": "",
            "congestion_cost_usd": "",
            "hours_observed": "",
            "notes": "",
        })
    return rows


def export_evidence_template_csv(
    flow_report_path: str | Path,
    path: str | Path,
    top: int = 25,
) -> None:
    _write_csv(path, evidence_template_rows(flow_report_path, top=top))


def _first(row: Mapping[str, Any], keys: Sequence[str]) -> str:
    lower = {str(k).lower(): v for k, v in row.items()}
    for key in keys:
        value = lower.get(key.lower())
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _float(value: Any) -> float:
    if value is None:
        return 0.0
    text = str(value).strip().replace(",", "").replace("$", "")
    if not text:
        return 0.0
    return float(text)


def _write_csv(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = _fieldnames(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _fieldnames(rows: List[Dict[str, Any]]) -> List[str]:
    preferred = [
        "ba_a",
        "ba_b",
        "evidence_status",
        "curvature",
        "gross_mwh",
        "gross_share",
        "net_direction",
        "net_mwh",
        "structural_priority_score",
        "combined_priority",
        "estimated_value_usd",
        "evidence_source",
        "mean_price_spread_usd_mwh",
        "max_price_spread_usd_mwh",
        "congestion_cost_usd",
        "hours_observed",
        "notes",
    ]
    seen = {key for row in rows for key in row}
    return [key for key in preferred if key in seen] + sorted(seen - set(preferred))


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


def _table(headers: Sequence[str], rows: Sequence[Sequence[str]], empty: str) -> str:
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


def _mwh(value: float) -> str:
    return f"{value:,.0f}"


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
  width: min(1180px, calc(100vw - 32px));
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
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
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
  font-size: 25px;
  line-height: 1.05;
  letter-spacing: 0;
}
.metric small {
  color: var(--muted);
}
.table-wrap { overflow-x: auto; }
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
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
  .shell { width: min(100vw - 20px, 1180px); padding-top: 18px; }
  .band { padding: 14px; }
  .metric { min-height: 116px; }
  .metric strong { font-size: 22px; }
}
"""
