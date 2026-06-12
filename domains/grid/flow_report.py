# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Audience reports for BA interchange flow-geometry bottlenecks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from domains.grid.flow_geometry import FlowGeometryReport, TieLine, analyze_flow_geometry


@dataclass(frozen=True)
class FlowBottleneck:
    """One structurally weak BA interchange tie."""

    ba_a: str
    ba_b: str
    curvature: float
    gross_mwh: float
    net_mwh: float
    gross_share: float

    @property
    def priority_score(self) -> float:
        """Flow-weighted negative curvature; larger means higher review priority."""
        return max(0.0, -self.curvature) * self.gross_mwh

    @property
    def net_direction(self) -> str:
        if self.net_mwh >= 0:
            return f"{self.ba_a} -> {self.ba_b}"
        return f"{self.ba_b} -> {self.ba_a}"


@dataclass
class FlowBottleneckReport:
    """Proof artifact for Ricci/spectral BA interchange bottlenecks."""

    geometry: FlowGeometryReport
    total_gross_mwh: float
    bottlenecks: List[FlowBottleneck]

    @property
    def hyperbolic_edges(self) -> int:
        reported = int(self.geometry.curvature_stats.get("n_hyperbolic", 0.0))
        return max(reported, len(self.bottlenecks))

    @property
    def hyperbolic_rate(self) -> float:
        return self.hyperbolic_edges / self.geometry.n_ties if self.geometry.n_ties else 0.0

    @property
    def top_bottleneck_gross_mwh(self) -> float:
        return sum(b.gross_mwh for b in self.bottlenecks[:10])

    @property
    def top_bottleneck_gross_share(self) -> float:
        if self.total_gross_mwh <= 0:
            return 0.0
        return self.top_bottleneck_gross_mwh / self.total_gross_mwh

    def bottleneck_gross_mwh(self, top: int = 10) -> float:
        return sum(b.gross_mwh for b in self.bottlenecks[:top])

    def bottleneck_gross_share(self, top: int = 10) -> float:
        if self.total_gross_mwh <= 0:
            return 0.0
        return self.bottleneck_gross_mwh(top) / self.total_gross_mwh

    @property
    def small_partition(self) -> List[str]:
        return self.geometry.fiedler_partition[0]

    @property
    def large_partition(self) -> List[str]:
        return self.geometry.fiedler_partition[1]

    def summary(self, top: int = 10) -> str:
        lines = [
            "BA interchange bottleneck proof report",
            f"  network: {self.geometry.n_bas} BAs, {self.geometry.n_ties} ties, "
            f"{self.total_gross_mwh / 1e6:,.1f} TWh gross interchange",
            f"  curvature: mean {self.geometry.curvature_stats.get('mean', 0.0):+.3f}; "
            f"{self.hyperbolic_edges} hyperbolic ties ({self.hyperbolic_rate:.1%})",
            f"  spectral coupling: {self.geometry.coupling} "
            f"(Fiedler {self.geometry.algebraic_connectivity:.4f})",
            f"  top {min(top, len(self.bottlenecks))} bottlenecks carry "
            f"{self.bottleneck_gross_mwh(top) / 1e6:,.1f} TWh "
            f"({self.bottleneck_gross_share(top):.1%} of gross interchange)",
        ]
        for item in self.bottlenecks[:top]:
            lines.append(
                f"  bottleneck {item.ba_a} -- {item.ba_b}: "
                f"curvature {item.curvature:+.3f}, gross {item.gross_mwh / 1e6:,.1f} TWh, "
                f"net {item.net_direction} {abs(item.net_mwh) / 1e6:,.1f} TWh"
            )
        small = ", ".join(sorted(self.small_partition)[:12])
        suffix = ", ..." if len(self.small_partition) > 12 else ""
        lines.append(
            f"  Fiedler seam: {{{small}{suffix}}} ({len(self.small_partition)} BAs) "
            f"vs {len(self.large_partition)} BAs"
        )
        return "\n".join(lines)

    def to_dict(self, top: int = 25) -> Dict[str, Any]:
        return {
            "n_bas": self.geometry.n_bas,
            "n_ties": self.geometry.n_ties,
            "total_gross_mwh": self.total_gross_mwh,
            "curvature": {
                **self.geometry.curvature_stats,
                "hyperbolic_edges": self.hyperbolic_edges,
                "hyperbolic_rate": self.hyperbolic_rate,
            },
            "spectral": {
                "algebraic_connectivity": self.geometry.algebraic_connectivity,
                "coupling": self.geometry.coupling,
                "fiedler_partition": {
                    "small": sorted(self.small_partition),
                    "large": sorted(self.large_partition),
                },
            },
            "top_bottleneck_gross_mwh": self.top_bottleneck_gross_mwh,
            "top_bottleneck_gross_share": self.top_bottleneck_gross_share,
            "bottlenecks": [
                _bottleneck_payload(item) for item in self.bottlenecks[:top]
            ],
            "meshed_edges": [
                {"ba_a": a, "ba_b": b, "curvature": kappa}
                for a, b, kappa in self.geometry.meshed[:top]
            ],
        }

    def to_markdown(self, top: int = 15) -> str:
        lines = [
            "# BA Interchange Bottleneck Report",
            "",
            "## Result",
            "",
            f"- BAs: **{self.geometry.n_bas}**",
            f"- Interchange ties: **{self.geometry.n_ties}**",
            f"- Gross interchange: **{self.total_gross_mwh / 1e6:,.1f} TWh**",
            f"- Hyperbolic ties: **{self.hyperbolic_edges} "
            f"({self.hyperbolic_rate:.1%})**",
            f"- Spectral coupling: **{self.geometry.coupling}**",
            f"- Fiedler value: **{self.geometry.algebraic_connectivity:.4f}**",
            f"- Top 10 bottleneck flow share: **{self.top_bottleneck_gross_share:.1%}**",
            "",
            "## Priority Bottlenecks",
            "",
            "| Tie | Curvature | Gross MWh | Gross Share | Net Direction | Net MWh | Priority |",
            "|---|---:|---:|---:|---|---:|---:|",
        ]
        if not self.bottlenecks:
            lines.append("| None |  |  |  |  |  |  |")
        for item in self.bottlenecks[:top]:
            lines.append(
                f"| {item.ba_a} - {item.ba_b} | {item.curvature:+.3f} | "
                f"{item.gross_mwh:,.0f} | {item.gross_share:.1%} | "
                f"{item.net_direction} | {abs(item.net_mwh):,.0f} | "
                f"{item.priority_score:,.0f} |"
            )

        small = ", ".join(sorted(self.small_partition))
        large = ", ".join(sorted(self.large_partition))
        lines.extend([
            "",
            "## Fiedler Seam",
            "",
            f"- Smaller side ({len(self.small_partition)} BAs): {small}",
            f"- Other side ({len(self.large_partition)} BAs): {large}",
            "",
            "## Most Meshed Ties",
            "",
            "| Tie | Curvature |",
            "|---|---:|",
        ])
        if not self.geometry.meshed:
            lines.append("| None |  |")
        for a, b, kappa in self.geometry.meshed[:top]:
            lines.append(f"| {a} - {b} | {kappa:+.3f} |")
        return "\n".join(lines) + "\n"

    def to_html(self, title: str = "BA Interchange Bottleneck Dashboard", top: int = 15) -> str:
        metrics = [
            _metric("BAs", str(self.geometry.n_bas), "nodes in interchange graph"),
            _metric("Interchange ties", str(self.geometry.n_ties), "weighted EIA-930 edges"),
            _metric("Gross interchange", _twh(self.total_gross_mwh), "annual tie usage"),
            _metric(
                "Hyperbolic ties",
                f"{self.hyperbolic_edges}",
                f"{self.hyperbolic_rate:.1%} of ties",
            ),
            _metric(
                "Spectral coupling",
                self.geometry.coupling,
                f"Fiedler {self.geometry.algebraic_connectivity:.4f}",
            ),
            _metric(
                "Top 10 flow share",
                f"{self.top_bottleneck_gross_share:.1%}",
                _twh(self.top_bottleneck_gross_mwh),
            ),
        ]
        bottleneck_rows = [
            [
                f"{item.ba_a} - {item.ba_b}",
                f"{item.curvature:+.3f}",
                _mwh(item.gross_mwh),
                f"{item.gross_share:.1%}",
                item.net_direction,
                _mwh(abs(item.net_mwh)),
            ]
            for item in self.bottlenecks[:top]
        ]
        meshed_rows = [
            [f"{a} - {b}", f"{kappa:+.3f}"]
            for a, b, kappa in self.geometry.meshed[:top]
        ]
        seam_rows = [
            ["Smaller side", str(len(self.small_partition)), ", ".join(sorted(self.small_partition))],
            ["Other side", str(len(self.large_partition)), ", ".join(sorted(self.large_partition))],
        ]
        body = [
            '<section class="band summary">'
            "<h2>Flow geometry proof</h2>"
            '<div class="chips">'
            f'<span class="chip">{escape(self.geometry.coupling)} coupling</span>'
            f'<span class="chip">{self.hyperbolic_edges} hyperbolic ties</span>'
            f'<span class="chip">{escape(_twh(self.total_gross_mwh))} gross interchange</span>'
            "</div>"
            "</section>",
            '<section class="metrics">' + "".join(metrics) + "</section>",
            _section(
                "Priority Bottlenecks",
                _table(
                    ["Tie", "Curvature", "Gross MWh", "Share", "Net Direction", "Net MWh"],
                    bottleneck_rows,
                    "No negative-curvature bottlenecks found.",
                ),
            ),
            _section(
                "Fiedler Seam",
                _table(["Side", "BAs", "Members"], seam_rows, "No spectral seam found."),
            ),
            _section(
                "Most Meshed Ties",
                _table(["Tie", "Curvature"], meshed_rows, "No positive-curvature ties found."),
            ),
        ]
        return _page(title, "Ricci bottlenecks and spectral seams from EIA-930 interchange", body)

    def export_markdown(self, path: str | Path, top: int = 15) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(top=top), encoding="utf-8")

    def export_json(self, path: str | Path, top: int = 25) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(top=top), indent=2), encoding="utf-8")

    def export_html(
        self,
        path: str | Path,
        title: str = "BA Interchange Bottleneck Dashboard",
        top: int = 15,
    ) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_html(title=title, top=top), encoding="utf-8")


def build_flow_bottleneck_report(
    ties: List[TieLine],
    geometry: FlowGeometryReport | None = None,
) -> FlowBottleneckReport:
    geometry = geometry or analyze_flow_geometry(ties)
    total_gross = sum(t.gross_mwh for t in ties)
    tie_lookup = {frozenset((t.ba_a, t.ba_b)): t for t in ties}
    bottlenecks: List[FlowBottleneck] = []
    for ba_a, ba_b, curvature, gross in geometry.bottlenecks:
        tie = tie_lookup.get(frozenset((ba_a, ba_b)))
        bottlenecks.append(
            FlowBottleneck(
                ba_a=ba_a,
                ba_b=ba_b,
                curvature=curvature,
                gross_mwh=gross,
                net_mwh=tie.net_mwh if tie else 0.0,
                gross_share=(gross / total_gross) if total_gross > 0 else 0.0,
            )
        )
    bottlenecks.sort(key=lambda item: item.priority_score, reverse=True)
    return FlowBottleneckReport(
        geometry=geometry,
        total_gross_mwh=total_gross,
        bottlenecks=bottlenecks,
    )


def _bottleneck_payload(item: FlowBottleneck) -> Dict[str, Any]:
    return {
        "ba_a": item.ba_a,
        "ba_b": item.ba_b,
        "curvature": item.curvature,
        "gross_mwh": item.gross_mwh,
        "net_mwh": item.net_mwh,
        "net_direction": item.net_direction,
        "gross_share": item.gross_share,
        "priority_score": item.priority_score,
    }


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


def _twh(value: float) -> str:
    return f"{value / 1e6:,.1f} TWh"


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
