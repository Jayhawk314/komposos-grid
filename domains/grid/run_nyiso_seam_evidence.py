# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Generate NYISO seam congestion-component evidence for PJM-NYIS."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from html import escape
from pathlib import Path
import sys

from domains.grid.sources.nyiso import seam_component_spread


DEFAULT_CSV_DIR = Path("domains/grid/data/nyiso/csv")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="NYISO PJM seam LBMP/congestion-component evidence"
    )
    parser.add_argument("--csv-dir", default=str(DEFAULT_CSV_DIR))
    parser.add_argument("--proxy", default="PJM")
    parser.add_argument("--ba-a", default="PJM")
    parser.add_argument("--ba-b", default="NYIS")
    parser.add_argument("--evidence-csv", default="reports/nyiso_pjm_seam_evidence.csv")
    parser.add_argument("--report-json", default="reports/nyiso_pjm_seam_audit.json")
    parser.add_argument("--report-md", default="reports/nyiso_pjm_seam_audit.md")
    parser.add_argument("--report-html", default="reports/nyiso_pjm_seam_audit.html")
    args = parser.parse_args(argv)

    audit = seam_component_spread(args.csv_dir, proxy=args.proxy)
    row = audit.to_evidence_row(ba_a=args.ba_a, ba_b=args.ba_b)
    print(audit.summary())
    _write_csv(args.evidence_csv, [row])
    _write_json(args.report_json, {"audit": asdict(audit), "evidence_row": row})
    _write_text(args.report_md, _markdown(audit, row))
    _write_text(args.report_html, _html(audit, row))
    print(f"wrote NYISO seam evidence CSV: {args.evidence_csv}")
    print(f"wrote NYISO seam audit JSON: {args.report_json}")
    print(f"wrote NYISO seam audit report: {args.report_md}")
    print(f"wrote NYISO seam audit dashboard: {args.report_html}")
    return 0


def _write_csv(path: str | Path, rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
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


def _markdown(audit, row: dict) -> str:
    return "\n".join([
        "# NYISO PJM Seam Evidence Audit",
        "",
        "## Summary",
        "",
        f"- Hours observed: **{audit.hours:,}**",
        f"- Mean absolute LBMP spread: **${audit.mean_abs_lbmp_spread_usd_mwh:.2f}/MWh**",
        f"- Mean absolute congestion-component spread: "
        f"**${audit.mean_abs_congestion_spread_usd_mwh:.2f}/MWh**",
        f"- Mean absolute loss-component spread: "
        f"**${audit.mean_abs_loss_spread_usd_mwh:.2f}/MWh**",
        f"- Congestion component / LBMP spread: "
        f"**{audit.congestion_to_lbmp_ratio:.1%}**",
        f"- NYCA LBMP above PJM proxy: **{audit.share_lbmp_internal_above:.1%}**",
        "",
        "## Evidence Row",
        "",
        "| BA Tie | Method | Mean LBMP Spread | Mean Congestion Component | Hours | Notes |",
        "|---|---|---:|---:|---:|---|",
        f"| {row['ba_a']} - {row['ba_b']} | {row['evidence_method']} | "
        f"${row['mean_price_spread_usd_mwh']:.2f}/MWh | "
        f"${row['mean_congestion_component_spread_usd_mwh']:.2f}/MWh | "
        f"{row['hours_observed']:,} | {row['notes']} |",
        "",
    ])


def _html(audit, row: dict) -> str:
    metrics = [
        _metric("Hours", f"{audit.hours:,}", "hourly NYISO DAM zone rows"),
        _metric(
            "LBMP spread",
            f"${audit.mean_abs_lbmp_spread_usd_mwh:.2f}/MWh",
            "mean absolute NYCA vs PJM proxy",
        ),
        _metric(
            "Congestion spread",
            f"${audit.mean_abs_congestion_spread_usd_mwh:.2f}/MWh",
            "mean absolute settlement component",
        ),
        _metric(
            "Component share",
            f"{audit.congestion_to_lbmp_ratio:.1%}",
            "congestion/LBMP spread ratio",
        ),
    ]
    table = _table(
        ["Tie", "Method", "LBMP", "Congestion Component", "Loss Component", "Notes"],
        [[
            f"{row['ba_a']} - {row['ba_b']}",
            row["evidence_method"],
            f"${row['mean_price_spread_usd_mwh']:.2f}/MWh",
            f"${row['mean_congestion_component_spread_usd_mwh']:.2f}/MWh",
            f"${row['mean_loss_component_spread_usd_mwh']:.2f}/MWh",
            row["notes"],
        ]],
    )
    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>NYISO PJM Seam Evidence Audit</title>"
        f"<style>{_CSS}</style></head><body><main class=\"shell\">"
        "<header><h1>NYISO PJM Seam Evidence Audit</h1>"
        "<p>Hourly settlement component validation for the PJM-NYIS seam.</p>"
        "</header>"
        f"<section class=\"metrics\">{''.join(metrics)}</section>"
        f"<section class=\"band\"><h2>Evidence Row</h2>{table}</section>"
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


def _table(headers: list[str], rows: list[list[str]]) -> str:
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
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--page);
  color: var(--ink);
  font: 14px/1.5 Arial, Helvetica, sans-serif;
}
.shell {
  width: min(1100px, calc(100vw - 32px));
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
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
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
  min-height: 126px;
  border-top: 4px solid var(--blue);
  display: grid;
  gap: 6px;
  align-content: start;
}
.metric:nth-child(2n) { border-top-color: var(--green); }
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
@media (max-width: 640px) {
  .shell { width: min(100vw - 20px, 1100px); padding-top: 18px; }
  .metric strong { font-size: 21px; }
}
"""


if __name__ == "__main__":
    sys.exit(main())
