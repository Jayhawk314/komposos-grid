# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Generate Western ICE hub-price audit evidence for BA bottlenecks."""

from __future__ import annotations

import argparse
import csv
import json
from html import escape
from pathlib import Path
import sys

from domains.grid.sources.ice import build_western_hub_audits


DEFAULT_ICE = Path("domains/grid/data/ice_electric-2023final.xlsx")
DEFAULT_INTERCHANGE = [
    Path("domains/grid/data/EIA930_INTERCHANGE_2023_Jan_Jun.csv"),
    Path("domains/grid/data/EIA930_INTERCHANGE_2023_Jul_Dec.csv"),
]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Western hub proxy evidence audit")
    parser.add_argument("--ice-workbook", default=str(DEFAULT_ICE))
    parser.add_argument("--interchange", nargs="+", default=[str(p) for p in DEFAULT_INTERCHANGE])
    parser.add_argument("--evidence-csv", default="reports/western_hub_evidence.csv")
    parser.add_argument("--audit-csv", default="reports/western_hub_audit.csv")
    parser.add_argument("--audit-json", default="reports/western_hub_audit.json")
    parser.add_argument("--audit-md", default="reports/western_hub_audit.md")
    parser.add_argument("--audit-html", default="reports/western_hub_audit.html")
    args = parser.parse_args(argv)

    audits = build_western_hub_audits(args.ice_workbook, args.interchange)
    print(_summary(audits))
    _write_csv(args.evidence_csv, [a.to_evidence_row() for a in audits])
    _write_csv(args.audit_csv, [a.to_row() for a in audits])
    _write_json(args.audit_json, {"audits": [a.to_row() for a in audits]})
    _write_text(args.audit_md, _markdown(audits))
    _write_text(args.audit_html, _html(audits))
    print(f"wrote Western hub evidence CSV: {args.evidence_csv}")
    print(f"wrote Western hub audit CSV: {args.audit_csv}")
    print(f"wrote Western hub audit JSON: {args.audit_json}")
    print(f"wrote Western hub audit report: {args.audit_md}")
    print(f"wrote Western hub audit dashboard: {args.audit_html}")
    return 0


def _summary(audits) -> str:
    lines = ["Western hub evidence audit"]
    for audit in audits:
        lines.append(
            f"  {audit.ba_a}-{audit.ba_b}: conservative "
            f"${audit.conservative_spread_usd_mwh:.2f}/MWh; "
            f"daily mean |spread| ${audit.daily_mean_abs_spread_usd_mwh:.2f}/MWh; "
            f"flow alignment {audit.flow_alignment_weighted_share:.1%}"
        )
    return "\n".join(lines)


def _write_csv(path: str | Path, rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: str | Path, payload: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _markdown(audits) -> str:
    lines = [
        "# Western Hub Evidence Audit",
        "",
        "## Summary",
        "",
        "| Tie | Conservative Spread | Daily Mean Abs Spread | Overlap Days | Flow Alignment | Note |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for audit in audits:
        lines.append(
            f"| {audit.ba_a} - {audit.ba_b} | "
            f"${audit.conservative_spread_usd_mwh:.2f}/MWh | "
            f"${audit.daily_mean_abs_spread_usd_mwh:.2f}/MWh | "
            f"{audit.overlap_days:,} | "
            f"{audit.flow_alignment_weighted_share:.1%} | "
            f"{audit.alignment_note}. {audit.note} |"
        )
    lines.extend([
        "",
        "The evidence CSV keeps the conservative annual volume-weighted hub spread "
        "as the dollar proxy. The daily overlap and flow-alignment metrics are "
        "diagnostics: they indicate whether the proxy is directionally credible, "
        "but they are not treated as direct settlement cost.",
        "",
    ])
    return "\n".join(lines)


def _html(audits) -> str:
    rows = [
        [
            f"{a.ba_a} - {a.ba_b}",
            f"${a.conservative_spread_usd_mwh:.2f}/MWh",
            f"${a.daily_mean_abs_spread_usd_mwh:.2f}/MWh",
            f"{a.overlap_days:,}",
            f"{a.flow_alignment_weighted_share:.1%}",
            f"{a.alignment_note}. {a.note}",
        ]
        for a in audits
    ]
    weak = sum(1 for a in audits if a.flow_alignment_weighted_share < 0.45)
    mixed = sum(1 for a in audits if 0.45 <= a.flow_alignment_weighted_share < 0.65)
    supportive = sum(1 for a in audits if a.flow_alignment_weighted_share >= 0.65)
    metrics = [
        _metric("Audited ties", str(len(audits)), "Western hub proxy rows"),
        _metric("Supportive", str(supportive), "flow/price alignment >= 65%"),
        _metric("Mixed", str(mixed), "flow/price alignment 45-65%"),
        _metric("Weak", str(weak), "flow/price alignment < 45%"),
    ]
    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Western Hub Evidence Audit</title>"
        f"<style>{_CSS}</style></head><body><main class=\"shell\">"
        "<header><h1>Western Hub Evidence Audit</h1>"
        "<p>ICE daily hub spreads checked against EIA-930 interchange direction.</p>"
        "</header>"
        f"<section class=\"metrics\">{''.join(metrics)}</section>"
        f"<section class=\"band\"><h2>Proxy Diagnostics</h2>{_table(rows)}</section>"
        "</main></body></html>\n"
    )


def _metric(label: str, value: str, detail: str) -> str:
    return (
        '<article class="metric">'
        f"<span>{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        f"<small>{escape(detail)}</small>"
        "</article>"
    )


def _table(rows: list[list[str]]) -> str:
    headers = [
        "Tie",
        "Conservative Spread",
        "Daily Mean Abs",
        "Overlap Days",
        "Flow Alignment",
        "Note",
    ]
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body = []
    for row in rows:
        body.append(
            "<tr>" + "".join(f"<td>{escape(str(cell))}</td>" for cell in row) + "</tr>"
        )
    return (
        '<div class="table-wrap"><table>'
        f"<thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body)}</tbody>"
        "</table></div>"
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
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 12px;
  margin: 16px 0;
}
.metric, .band {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 14px;
}
.metric {
  min-height: 124px;
  border-top: 4px solid var(--blue);
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
.band { margin: 16px 0; }
.table-wrap { overflow-x: auto; }
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 860px;
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
@media (max-width: 640px) {
  .shell { width: min(100vw - 20px, 1180px); padding-top: 18px; }
  .metric strong { font-size: 21px; }
}
"""


if __name__ == "__main__":
    sys.exit(main())
