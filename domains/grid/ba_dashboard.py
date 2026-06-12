# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Static HTML dashboards for BA footprint correction evidence."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Iterable, List, Sequence

from domains.grid.ba_footprint_report import BAFootprintReport
from domains.grid.ba_review import BAFootprintReview, ReviewedMove


def footprint_report_to_html(
    report: BAFootprintReport,
    title: str = "BA Footprint Correction Dashboard",
    top: int = 15,
) -> str:
    """Render a before/after BA footprint report as a standalone HTML page."""
    metrics = [
        _metric(
            "BA agreement",
            _pct(report.after_agreement_rate),
            before=_pct(report.before_agreement_rate),
            detail="telemetry vs corrected accounting",
        ),
        _metric(
            "Contradictions",
            str(report.after_contradictions),
            before=str(report.before_contradictions),
            detail=f"{report.contradiction_reduction} resolved",
        ),
        _metric(
            "Absolute BA error",
            _twh(report.crosswalk.after_score.abs_error_mwh),
            before=_twh(report.crosswalk.before_score.abs_error_mwh),
            detail=_signed_twh(report.crosswalk.improvement_mwh) + " improvement",
        ),
        _metric(
            "Sheaf H1 leak",
            f"{report.after_sheaf.energy_leak:.3e}",
            before=f"{report.before_sheaf.energy_leak:.3e}",
            detail="global obstruction after correction",
        ),
    ]
    accepted_rows = [
        [
            move.entity,
            move.state,
            move.from_ba,
            move.to_ba,
            _mwh(move.value_mwh),
            _mwh(validated.improvement_mwh),
            f"{move.confidence:.2f}",
        ]
        for validated in report.crosswalk.accepted[:top]
        for move in [validated.move]
    ]
    rejected_rows = [
        [
            move.entity,
            move.from_ba,
            move.to_ba,
            "; ".join(validated.reasons),
        ]
        for validated in report.crosswalk.rejected[:top]
        for move in [validated.move]
    ]
    unresolved_rows = [
        [
            ba,
            _mwh(delta),
            "telemetry higher" if delta > 0 else "accounting higher",
        ]
        for ba, delta in report.unresolved_deltas(top)
    ]

    body = [
        _summary_band(
            "Validated footprint corrections",
            [
                f"{len(report.crosswalk.accepted)} accepted",
                f"{len(report.crosswalk.rejected)} rejected",
                f"{report.crosswalk.after_score.outside_tolerance} BAs still outside tolerance",
            ],
        ),
        _metric_grid(metrics),
        _section(
            "Accepted Corrections",
            _table(
                ["Entity", "State", "From BA", "To BA", "MWh", "Improvement", "Confidence"],
                accepted_rows,
                empty="No accepted corrections.",
            ),
        ),
        _section(
            "Rejected Candidates",
            _table(
                ["Entity", "From BA", "To BA", "Reason"],
                rejected_rows,
                empty="No rejected candidates.",
            ),
        ),
        _section(
            "Remaining Largest BA Deltas",
            _table(
                ["BA", "Delta MWh", "Interpretation"],
                unresolved_rows,
                empty="No unresolved BA deltas.",
            ),
        ),
    ]
    return _page(title, "Before/after proof for BA footprint corrections", body)


def export_footprint_report_html(
    report: BAFootprintReport,
    path: str | Path,
    title: str = "BA Footprint Correction Dashboard",
    top: int = 15,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        footprint_report_to_html(report, title=title, top=top),
        encoding="utf-8",
    )


def review_to_html(
    review: BAFootprintReview,
    reviewed_report: BAFootprintReport | None = None,
    title: str = "BA Footprint Review Dashboard",
    top: int = 15,
) -> str:
    """Render a curated review result as a standalone HTML page."""
    before = review.curated_crosswalk.before_score
    machine_after = review.source_crosswalk.after_score
    reviewed_after = review.curated_crosswalk.after_score
    metrics = [
        _metric(
            "Approved corrections",
            str(len(review.approved)),
            before=f"{len(review.source_crosswalk.accepted)} machine accepted",
            detail=f"{len(review.needs_review)} still need review",
        ),
        _metric(
            "Reviewed BA error",
            _twh(reviewed_after.abs_error_mwh),
            before=_twh(before.abs_error_mwh),
            detail=_signed_twh(review.improvement_mwh) + " approved improvement",
        ),
        _metric(
            "Machine BA error",
            _twh(machine_after.abs_error_mwh),
            before=_twh(before.abs_error_mwh),
            detail="if all machine-accepted corrections were applied",
        ),
        _metric(
            "Outside tolerance",
            str(reviewed_after.outside_tolerance),
            before=str(before.outside_tolerance),
            detail=f"{reviewed_after.tolerance:.1%} BA tolerance",
        ),
    ]
    if reviewed_report is not None:
        metrics.extend([
            _metric(
                "Reviewed agreement",
                _pct(reviewed_report.after_agreement_rate),
                before=_pct(reviewed_report.before_agreement_rate),
                detail="approved-only report",
            ),
            _metric(
                "Reviewed H1 leak",
                f"{reviewed_report.after_sheaf.energy_leak:.3e}",
                before=f"{reviewed_report.before_sheaf.energy_leak:.3e}",
                detail="approved-only sheaf obstruction",
            ),
        ])

    body = [
        _summary_band(
            "Curated correction review",
            [
                f"{len(review.approved)} approved",
                f"{len(review.rejected)} rejected",
                f"{len(review.needs_review)} need review",
            ],
        ),
        _metric_grid(metrics),
        _section(
            "Approved Corrections",
            _review_table(review.approved[:top]),
        ),
        _section(
            "Deferred Or Rejected",
            _review_table([item for item in review.reviewed if not item.applied][:top]),
        ),
    ]
    return _page(title, "Approved-only BA footprint correction evidence", body)


def export_review_html(
    review: BAFootprintReview,
    path: str | Path,
    reviewed_report: BAFootprintReport | None = None,
    title: str = "BA Footprint Review Dashboard",
    top: int = 15,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        review_to_html(review, reviewed_report=reviewed_report, title=title, top=top),
        encoding="utf-8",
    )


def _review_table(items: Sequence[ReviewedMove]) -> str:
    rows = []
    for item in items:
        move = item.validated.move
        rows.append([
            move.entity,
            move.state,
            move.from_ba,
            move.to_ba,
            item.decision.status,
            "yes" if item.applied else "no",
            item.decision.reviewer,
            item.decision.note or "; ".join(item.review_reasons),
            _mwh(move.value_mwh),
        ])
    return _table(
        [
            "Entity",
            "State",
            "From BA",
            "To BA",
            "Decision",
            "Applied",
            "Reviewer",
            "Note",
            "MWh",
        ],
        rows,
        empty="No rows in this review state.",
    )


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
        '    <header class="topbar">\n'
        f"      <h1>{escape(title)}</h1>\n"
        f"      <p>{escape(subtitle)}</p>\n"
        "    </header>\n"
        f"    {''.join(sections)}\n"
        "  </main>\n"
        "</body>\n"
        "</html>\n"
    )


def _summary_band(title: str, facts: Sequence[str]) -> str:
    chips = "".join(f'<span class="chip">{escape(fact)}</span>' for fact in facts)
    return (
        '<section class="band summary">'
        f"<h2>{escape(title)}</h2>"
        f'<div class="chips">{chips}</div>'
        "</section>"
    )


def _metric(label: str, value: str, before: str, detail: str) -> str:
    return (
        '<article class="metric">'
        f"<span>{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        f"<small>Before: {escape(before)}</small>"
        f"<em>{escape(detail)}</em>"
        "</article>"
    )


def _metric_grid(metrics: Sequence[str]) -> str:
    return '<section class="metrics">' + "".join(metrics) + "</section>"


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
    body_rows: List[str] = []
    for row in rows:
        body_rows.append(
            "<tr>"
            + "".join(f"<td>{escape(str(cell))}</td>" for cell in row)
            + "</tr>"
        )
    return (
        '<div class="table-wrap">'
        "<table>"
        f"<thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
        "</div>"
    )


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _mwh(value: float) -> str:
    return f"{value:,.0f}"


def _twh(value: float) -> str:
    return f"{value / 1e6:,.1f} TWh"


def _signed_twh(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}{abs(value) / 1e6:,.1f} TWh"


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
  --red: #c2413a;
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
.topbar {
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
  color: var(--ink);
  padding: 6px 10px;
  white-space: nowrap;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 12px;
  margin: 16px 0;
}
.metric {
  min-height: 148px;
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
.metric:nth-child(5n) { border-top-color: var(--red); }
.metric span {
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
}
.metric strong {
  font-size: 26px;
  line-height: 1.05;
  letter-spacing: 0;
}
.metric small, .metric em {
  color: var(--muted);
  font-style: normal;
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
  .metric { min-height: 126px; }
  .metric strong { font-size: 22px; }
}
"""
