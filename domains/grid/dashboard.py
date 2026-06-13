# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Static public dashboard for the grid-waste findings.

Renders one self-contained HTML page (no server, no JavaScript
dependencies) from the committed report artifacts:

- reports/energy_solution_cards.json   ranked corridors
- reports/energy_solution_studies.json priority studies
- reports/project_cost_results.csv     real-project B/C verdicts
- reports/chpe_event_study.json        CHPE natural experiment

Built for GitHub Pages: write to docs/index.html and the repo serves
it. Regenerate whenever the underlying reports change (the runner is
cheap; it only reads files already in the repo).
"""

from __future__ import annotations

import csv
import json
import re
from datetime import date
from html import escape
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from domains.grid.charts import bar_chart, line_chart

REPO_URL = "https://github.com/Jayhawk314/komposos-grid"

_TREND_RE = re.compile(r"(20\d{2}) \$([\d.]+)/MWh")


def parse_trend_summary(text: str) -> List[tuple[int, float]]:
    """Extract (year, $/MWh) pairs from a card's trend_summary string."""
    return [(int(y), float(v)) for y, v in _TREND_RE.findall(str(text))]


def load_inputs(reports_dir: str | Path = "reports") -> Dict[str, Any]:
    reports_dir = Path(reports_dir)

    def _json(name: str) -> Any:
        path = reports_dir / name
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    project_rows: List[Dict[str, str]] = []
    project_path = reports_dir / "project_cost_results.csv"
    if project_path.exists():
        with project_path.open(newline="", encoding="utf-8") as handle:
            project_rows = list(csv.DictReader(handle))

    return {
        "cards": (_json("energy_solution_cards.json") or {}).get("cards", []),
        "studies": (_json("energy_solution_studies.json") or {}).get("studies", []),
        "projects": project_rows,
        "chpe": _json("chpe_event_study.json"),
    }


def fmt_money(value: float) -> str:
    value = float(value)
    if abs(value) >= 1e9:
        return f"${value / 1e9:,.1f}B"
    if abs(value) >= 1e6:
        return f"${value / 1e6:,.1f}M"
    return f"${value:,.0f}"


def build_dashboard_html(
    cards: Sequence[Mapping[str, Any]],
    studies: Sequence[Mapping[str, Any]],
    projects: Sequence[Mapping[str, Any]],
    chpe: Mapping[str, Any] | None,
    generated: date | None = None,
) -> str:
    generated = generated or date.today()
    metrics = _metric_cards(studies, projects, chpe)
    sections = []
    trend_svg = seam_trend_chart(cards)
    if trend_svg:
        sections.append(_band(
            "The trend, drawn",
            "<p>Congestion spread per seam, by year — the New York seam "
            "is the steep one.</p>" + trend_svg,
        ))
    sections.append(_band("Corridors, ranked",
                          _corridor_table(cards, studies)))
    project_body = _project_table(projects)
    bc_svg = project_bc_chart(projects)
    if bc_svg:
        project_body += ("<p>Above the dashed line, a project pays for "
                         "itself on seam congestion value alone.</p>"
                         + bc_svg)
    sections.append(_band(
        "Real projects vs the congestion they would relieve", project_body))
    if chpe:
        sections.append(_band("The CHPE natural experiment", _chpe_section(chpe)))
    sections.append(_band("Read this before quoting numbers", _trust_note()))

    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>US Grid Waste — Public Findings</title>"
        f"<style>{_CSS}</style></head><body><main class=\"shell\">"
        "<header><h1>US Grid Waste — Public Findings</h1>"
        "<p>Where the US electric grid loses money, what would fix it, "
        "and whether the fix pays for itself — from public data only. "
        '<a href="network_map.html">Explore the interactive grid map</a> · '
        f'<a href="{REPO_URL}">Code &amp; data</a> · '
        f'<a href="{REPO_URL}/blob/master/reports/MASTER_GUIDE.md">'
        "Plain-English guide</a> · "
        f'<a href="{REPO_URL}/blob/master/REPRODUCE.md">'
        "Reproduce these numbers yourself</a></p>"
        "</header>"
        f"<section class=\"metrics\">{''.join(metrics)}</section>"
        f"{''.join(sections)}"
        f"<footer><p>Generated {generated.isoformat()}. Every number is "
        "reproducible from keyless public sources; methods and caveats in "
        "the guide. Spread = hourly price gap between regions; B/C &gt; 1 "
        "means a fix pays for itself on congestion value alone.</p></footer>"
        "</main></body></html>\n"
    )


def seam_trend_chart(cards: Sequence[Mapping[str, Any]]) -> str:
    """Line chart of congestion spread by year for every card with a trend."""
    per_seam: Dict[str, Dict[int, float]] = {}
    years: set[int] = set()
    for card in cards:
        points = parse_trend_summary(card.get("trend_summary", ""))
        if len(points) < 2:
            continue
        name = str(card.get("geography", ""))
        per_seam[name] = dict(points)
        years.update(y for y, _ in points)
    if not per_seam:
        return ""
    x_labels = sorted(years)
    series = {
        name: [vals.get(year) for year in x_labels]
        for name, vals in per_seam.items()
    }
    return line_chart(
        x_labels, series,
        title="Seam congestion spread by year",
        y_label="$/MWh (mean hourly congestion-component spread)",
    )


def study_value_overrides(
    studies: Sequence[Mapping[str, Any]],
) -> Dict[str, float]:
    """Same-year study values supersede card values for display.

    Cards value corridors on the inferred flow baseline; the studies
    re-value the priority corridors on same-year flows. Showing both
    side by side would look like a contradiction, so display always
    prefers the study number.
    """
    return {
        str(s.get("geography", "")): float(s.get("annual_value_usd", 0) or 0)
        for s in studies
        if float(s.get("annual_value_usd", 0) or 0) > 0
    }


def corridor_value_chart(
    cards: Sequence[Mapping[str, Any]],
    studies: Sequence[Mapping[str, Any]] = (),
) -> str:
    """Bar chart of annual congestion value per corridor, $M/yr."""
    overrides = study_value_overrides(studies)
    cats, vals = [], []
    for card in cards:
        geography = str(card.get("geography", ""))
        value = overrides.get(
            geography, float(card.get("annual_value_usd", 0) or 0))
        if value <= 0:
            continue
        cats.append(geography)
        vals.append(value / 1e6)
    if not cats:
        return ""
    return bar_chart(
        cats, {"Annual congestion value": vals},
        title="What each border bottleneck costs per year",
        y_label="$ million per year",
        value_fmt="{:.1f}",
    )


def project_bc_chart(projects: Sequence[Mapping[str, Any]]) -> str:
    """Bar chart of project benefit/cost ratios against the 1.0 line."""
    cats, vals = [], []
    for row in projects:
        bcr = float(row.get("benefit_cost_ratio", 0) or 0)
        if bcr <= 0:
            continue
        cats.append(str(row.get("project_name", row.get("project_id", ""))))
        vals.append(bcr)
    if not cats:
        return ""
    return bar_chart(
        cats, {"B/C on seam value alone": vals},
        title="Does the fix pay for itself?",
        y_label="benefit / cost per year",
        ref_line=1.0, ref_label="break-even",
    )


def chpe_chart(chpe: Mapping[str, Any]) -> str:
    """Grouped bars for the four event-study windows."""
    cats, lbmp, congestion = [], [], []
    for key in ("pre_2025", "post_2025", "pre_2026", "post_2026"):
        cell = chpe.get(key) or {}
        cats.append(str(cell.get("label", key)))
        lbmp.append(float(cell.get("mean_abs_lbmp_spread_usd_mwh", 0)))
        congestion.append(
            float(cell.get("mean_abs_congestion_spread_usd_mwh", 0)))
    return bar_chart(
        cats,
        {"Full price spread": lbmp, "Congestion component": congestion},
        title="PJM-NYIS seam, before and after CHPE (2025 = control)",
        y_label="$/MWh",
    )


def _metric_cards(
    studies: Sequence[Mapping[str, Any]],
    projects: Sequence[Mapping[str, Any]],
    chpe: Mapping[str, Any] | None,
) -> List[str]:
    out: List[str] = []
    for study in studies:
        out.append(_metric(
            escape(str(study.get("geography", ""))),
            f"{fmt_money(study.get('annual_value_usd', 0))}/yr",
            f"congestion value, {study.get('current_year', '')} spread "
            f"x {study.get('flow_year', '')} flow "
            f"({str(study.get('same_year_flow_status', '')).replace('_', ' ')})",
        ))
    named = [
        float(row.get("benefit_cost_ratio", 0) or 0)
        for row in projects
        if str(row.get("geography")) == "MISO-SWPP"
    ]
    if named:
        out.append(_metric(
            "Named fix B/C",
            f"{min(named):.2f}–{max(named):.2f}",
            "Patent Gate–Pioneer 345 kV vs MISO-SWPP seam value alone",
        ))
    if chpe:
        did = float(chpe.get("did_congestion_usd_mwh", 0))
        out.append(_metric(
            "CHPE effect so far",
            f"{did:+.2f} $/MWh",
            "spread change beyond seasonality, first post-COD month",
        ))
    return out


def _corridor_table(
    cards: Sequence[Mapping[str, Any]],
    studies: Sequence[Mapping[str, Any]] = (),
) -> str:
    if not cards:
        return "<p>No corridor cards available.</p>"
    overrides = study_value_overrides(studies)
    rows = []
    for card in cards:
        geography = str(card.get("geography", ""))
        value = overrides.get(
            geography, float(card.get("annual_value_usd", 0) or 0))
        rows.append([
            geography,
            str(card.get("solution_status", "")).replace("_", " "),
            str(card.get("current_year", "")),
            f"${float(card.get('spread_usd_mwh', 0)):.2f}/MWh",
            f"{fmt_money(value)}/yr" if value > 0 else "—",
            str(card.get("trend_summary", "")),
        ])
    return _table(
        ["Corridor", "Status", "Year", "Congestion spread", "Annual value",
         "Trend"],
        rows,
    )


def _project_table(projects: Sequence[Mapping[str, Any]]) -> str:
    if not projects:
        return ("<p>No costed projects yet — see the guide for how to "
                "submit project costs.</p>")
    rows = []
    for row in projects:
        bcr = float(row.get("benefit_cost_ratio", 0) or 0)
        clears = str(row.get("clears_congestion_value", "")).lower() == "true"
        rows.append([
            str(row.get("project_name", "")),
            str(row.get("geography", "")),
            fmt_money(float(row.get("capex_usd", 0) or 0)),
            f"{fmt_money(float(row.get('annual_cost_usd', 0) or 0))}/yr",
            f"{fmt_money(float(row.get('relief_value_usd', 0) or 0))}/yr",
            f"{bcr:.2f}" + (" ✓ clears" if clears else ""),
        ])
    return _table(
        ["Project", "Corridor", "Capex", "Annual cost", "Relief value",
         "B/C on seam value alone"],
        rows,
    )


def _chpe_section(chpe: Mapping[str, Any]) -> str:
    rows = []
    for key in ("pre_2025", "post_2025", "pre_2026", "post_2026"):
        cell = chpe.get(key) or {}
        rows.append([
            str(cell.get("label", key)),
            f"{cell.get('start', '')}..{cell.get('end', '')}",
            f"${float(cell.get('mean_abs_lbmp_spread_usd_mwh', 0)):.2f}",
            f"${float(cell.get('mean_abs_congestion_spread_usd_mwh', 0)):.2f}",
            f"{float(cell.get('share_lbmp_internal_above', 0)):.1%}",
        ])
    did = float(chpe.get("did_congestion_usd_mwh", 0))
    verdict = (
        "mild compression beyond seasonality — CHPE is helping, but the "
        "seam did not collapse" if did < 0
        else "no compression beyond seasonality yet"
    )
    return (
        "<p>A $6B, 1,250 MW power line from Quebec to NYC went live "
        "2026-05-13. Did it shrink the New York price gap? "
        "Before/after, against 2025 as the seasonal control:</p>"
        + _table(
            ["Window", "Dates", "Mean |spread|", "Congestion part",
             "NY more expensive"],
            rows,
        )
        + chpe_chart(chpe)
        + f"<p><strong>Difference-in-differences: {did:+.2f} $/MWh</strong> "
        f"— {verdict}. One month of data; the summer rerun decides.</p>"
    )


def _trust_note() -> str:
    return (
        "<p><strong>Measured</strong> numbers (seam spreads, corridor "
        "values) come from grid operators' own hourly settlement data "
        "times observed flows. <strong>Screening</strong> numbers (B/C "
        "brackets, assumed O&amp;M) are honest estimates with stated "
        "assumptions — good enough to rank options, not to commit money. "
        "Relief is always capped at the congestion that actually exists; "
        "the two sides of one border are never double-counted. Full trust "
        f'ledger: <a href="{REPO_URL}/blob/master/reports/MASTER_GUIDE.md">'
        "MASTER_GUIDE §6</a>.</p>"
    )


def _metric(label: str, value: str, detail: str) -> str:
    return (
        '<article class="metric">'
        f"<span>{label}</span>"
        f"<strong>{escape(value)}</strong>"
        f"<small>{escape(detail)}</small>"
        "</article>"
    )


def _band(title: str, body: str) -> str:
    return f'<section class="band"><h2>{escape(title)}</h2>{body}</section>'


def _table(headers: List[str], rows: List[List[str]]) -> str:
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(c))}</td>" for c in row) + "</tr>"
        for row in rows
    )
    return (
        '<div class="table-wrap"><table>'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


_CSS = """
:root {
  color-scheme: light;
  --ink: #17202a; --muted: #5b6673; --line: #d8dee6;
  --surface: #ffffff; --page: #f5f7fa; --blue: #1f6feb; --green: #1f8f5f;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--page); color: var(--ink);
  font: 15px/1.55 Arial, Helvetica, sans-serif; }
.shell { width: min(1100px, calc(100vw - 32px)); margin: 0 auto;
  padding: 28px 0 40px; }
header { border-bottom: 1px solid var(--line); margin-bottom: 18px;
  padding-bottom: 16px; }
h1 { font-size: clamp(26px, 4vw, 38px); line-height: 1.1; margin: 0 0 8px; }
h2 { font-size: 18px; margin: 0 0 14px; }
p { margin: 0 0 8px; color: var(--muted); }
a { color: var(--blue); }
.metrics { display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px; margin: 16px 0; }
.metric, .band { background: var(--surface); border: 1px solid var(--line);
  border-radius: 8px; padding: 14px; }
.metric { min-height: 120px; border-top: 4px solid var(--blue);
  display: grid; gap: 6px; align-content: start; }
.metric:nth-child(2n) { border-top-color: var(--green); }
.metric span { color: var(--muted); font-size: 12px;
  text-transform: uppercase; }
.metric strong { font-size: 26px; line-height: 1.05; }
.metric small { color: var(--muted); }
.band { margin: 16px 0; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; min-width: 760px; }
th, td { border-bottom: 1px solid var(--line); padding: 9px 10px;
  text-align: left; vertical-align: top; }
th { color: var(--muted); font-size: 12px; text-transform: uppercase;
  background: #fbfcfe; }
footer { color: var(--muted); font-size: 13px; margin-top: 18px; }
@media (max-width: 640px) {
  .shell { width: min(100vw - 20px, 1100px); padding-top: 18px; }
  .metric strong { font-size: 22px; }
}
"""
