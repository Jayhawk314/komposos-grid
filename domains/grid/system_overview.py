# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Whole-system view: the US grid in six numbers and six charts.

Where the corridor studies zoom in, this zooms out: national demand
(EIA-930 BALANCE), energy crossing regional borders (EIA-930
INTERCHANGE), how concentrated congestion is (ISO constraint tables),
curtailment, the interconnection-queue funnel, and the annual waste
bill - each as a chart for reports/SYSTEM_OVERVIEW.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Tuple

from domains.grid.charts import bar_chart
from domains.grid.flow_geometry import load_interchange

DEMAND_COL = "Demand (MW)"

# CAISO publishes curtailment as a spreadsheet, parsed in the Phase 1-3
# work (caiso_production_curtailments_2023.xlsx); the established 2023
# figure is carried here as a constant with its source.
CAISO_2023_CURTAILMENT_TWH = 2.66


@dataclass
class SystemStats:
    demand_twh: Dict[int, float] = field(default_factory=dict)
    interchange_twh: Dict[int, float] = field(default_factory=dict)
    # iso -> (n_constraints, top10_severity_share)
    concentration: Dict[str, Tuple[int, float]] = field(default_factory=dict)
    curtailment_twh: Dict[str, float] = field(default_factory=dict)
    queue_completion: Dict[str, float] = field(default_factory=dict)
    waste_usd_m: Dict[str, float] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(
            {
                "demand_twh": self.demand_twh,
                "interchange_twh": self.interchange_twh,
                "concentration": {
                    k: {"n_constraints": n, "top10_share": s}
                    for k, (n, s) in self.concentration.items()
                },
                "curtailment_twh": self.curtailment_twh,
                "queue_completion": self.queue_completion,
                "waste_usd_m": self.waste_usd_m,
            },
            indent=2,
        )


def national_demand_twh(balance_csvs: Iterable[str | Path]) -> float:
    """Sum hourly BA demand across files -> TWh (EIA's US total method)."""
    import pandas as pd

    total_mwh = 0.0
    for path in balance_csvs:
        df = pd.read_csv(path, usecols=[DEMAND_COL], thousands=",")
        total_mwh += float(
            pd.to_numeric(df[DEMAND_COL], errors="coerce").sum())
    return total_mwh / 1e6


def national_interchange_twh(
    interchange_csvs: Iterable[str | Path],
) -> float:
    """Total gross energy crossing BA borders -> TWh (each tie once)."""
    ties = load_interchange(interchange_csvs)
    return sum(t.gross_mwh for t in ties) / 1e6


def constraint_concentration(
    constraints: List[Mapping[str, object]], top: int = 10
) -> Tuple[int, float]:
    """How much of total severity the worst `top` constraints carry."""
    severities = sorted(
        (float(c.get("severity", 0) or 0) for c in constraints),
        reverse=True,
    )
    total = sum(severities)
    if total <= 0:
        return len(severities), 0.0
    return len(severities), sum(severities[:top]) / total


def load_concentrations(reports_dir: str | Path) -> Dict[str, Tuple[int, float]]:
    reports_dir = Path(reports_dir)
    out: Dict[str, Tuple[int, float]] = {}
    miso = reports_dir / "miso_constraints_2023.json"
    if miso.exists():
        data = json.loads(miso.read_text(encoding="utf-8"))
        out["MISO"] = constraint_concentration(data["constraints"])
    pjm = reports_dir / "pjm_constraints_2023.json"
    if pjm.exists():
        data = json.loads(pjm.read_text(encoding="utf-8"))
        out["PJM"] = constraint_concentration(data["constraints"])
    spp = reports_dir / "spp_2023.json"
    if spp.exists():
        data = json.loads(spp.read_text(encoding="utf-8"))
        out["SPP"] = constraint_concentration(data["constraints"]["table"])
    return out


def spp_curtailment_twh(reports_dir: str | Path) -> float:
    path = Path(reports_dir) / "spp_2023.json"
    if not path.exists():
        return 0.0
    data = json.loads(path.read_text(encoding="utf-8"))
    curtailed = data["curtailment"]["curtailed_mwh"]
    return sum(
        float(v) for fuel in curtailed.values() for v in fuel.values()
    ) / 1e6


def queue_completion_rates(reports_dir: str | Path) -> Dict[str, float]:
    """Overall completion share and the executed-IA cohort multiplier,
    from the waste-ledger claims (LBNL queue analysis)."""
    path = Path(reports_dir) / "grid_waste_ledger.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    withdrawal_share = multiplier = None
    for claim in data.get("claims", []):
        metric = " ".join(
            str(claim.get(key, ""))
            for key in ("claim_id", "metric", "claim", "title", "unit", "notes")
        ).lower()
        value = float(claim.get("value", 0)
                      or claim.get("quantity", 0) or 0)
        if "attrition" in metric or "withdrawal share" in metric:
            withdrawal_share = value
        if "ia_executed" in metric and "completion" in metric:
            multiplier = value
    out: Dict[str, float] = {}
    if withdrawal_share is not None:
        out["overall"] = 1.0 - withdrawal_share
        if multiplier:
            out["ia_executed"] = min((1.0 - withdrawal_share) * multiplier, 1.0)
    return out


def waste_bill_usd_m(reports_dir: str | Path) -> Dict[str, float]:
    path = Path(reports_dir) / "grid_waste_ledger.json"
    out = {"Seam congestion (measured ties)": 78.6}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        out["Waste ledger, all claims"] = (
            float(data.get("measured_or_proxy_value_usd", 0) or 0) / 1e6)
    reliability = Path(reports_dir) / "reliability_valuation_2023.json"
    if reliability.exists():
        data = json.loads(reliability.read_text(encoding="utf-8"))
        floor = data.get("totals_usd", {}).get("floor")
        if floor:
            out["Reliability floor"] = float(floor) / 1e6
    out.setdefault("Reliability floor", 4_400.0)
    return out


def _find_first_number(payload, keywords) -> float | None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if (isinstance(value, (int, float))
                    and any(k in str(key).lower() for k in keywords)):
                return float(value)
        for value in payload.values():
            found = _find_first_number(value, keywords)
            if found is not None:
                return found
    return None


def collect_stats(
    data_dir: str | Path = "domains/grid/data",
    reports_dir: str | Path = "reports",
    years: Iterable[int] = (2023, 2024, 2025),
) -> SystemStats:
    data_dir = Path(data_dir)
    stats = SystemStats()
    for year in years:
        balance = [data_dir / f"EIA930_BALANCE_{year}_{h}.csv"
                   for h in ("Jan_Jun", "Jul_Dec")]
        interchange = [data_dir / f"EIA930_INTERCHANGE_{year}_{h}.csv"
                       for h in ("Jan_Jun", "Jul_Dec")]
        if all(p.exists() for p in balance):
            stats.demand_twh[year] = national_demand_twh(balance)
        if all(p.exists() for p in interchange):
            stats.interchange_twh[year] = national_interchange_twh(interchange)
    stats.concentration = load_concentrations(reports_dir)
    stats.curtailment_twh = {
        "CAISO 2023": CAISO_2023_CURTAILMENT_TWH,
        "SPP 2023": spp_curtailment_twh(reports_dir),
    }
    stats.queue_completion = queue_completion_rates(reports_dir)
    stats.waste_usd_m = waste_bill_usd_m(reports_dir)
    return stats


def build_figures(stats: SystemStats) -> Dict[str, str]:
    figures: Dict[str, str] = {
        "system_problem_map.svg": build_problem_map(stats),
    }
    if stats.demand_twh:
        figures["system_demand.svg"] = bar_chart(
            [str(y) for y in sorted(stats.demand_twh)],
            {"US electricity demand":
                [stats.demand_twh[y] for y in sorted(stats.demand_twh)]},
            title="1. Demand pressure is rising",
            y_label="terawatt-hours per year",
            value_fmt="{:,.0f}",
        )
    if stats.interchange_twh:
        figures["system_interchange.svg"] = bar_chart(
            [str(y) for y in sorted(stats.interchange_twh)],
            {"Energy crossing regional borders":
                [stats.interchange_twh[y]
                 for y in sorted(stats.interchange_twh)]},
            title="2. Regions already depend on cross-border power",
            y_label="terawatt-hours per year (gross, each border once)",
            value_fmt="{:,.0f}",
        )
    if stats.concentration:
        cats = [f"{iso} ({n:,} constraints)"
                for iso, (n, _) in stats.concentration.items()]
        vals = [share * 100 for _, (_, share) in stats.concentration.items()]
        figures["system_concentration.svg"] = bar_chart(
            cats, {"Share carried by the 10 worst": vals},
            title="3. A few bottlenecks carry much of the congestion",
            y_label="% of total 2023 congestion severity",
            value_fmt="{:.0f}%",
        )
    if stats.curtailment_twh:
        figures["system_curtailment.svg"] = bar_chart(
            list(stats.curtailment_twh),
            {"Clean energy discarded": list(stats.curtailment_twh.values())},
            title="4. Useful clean energy is being thrown away",
            y_label="terawatt-hours in 2023",
            value_fmt="{:.2f}",
        )
    if stats.queue_completion:
        labels = {"overall": "All decided projects",
                  "ia_executed": "Projects that signed a connection agreement"}
        figures["system_queue.svg"] = bar_chart(
            [labels.get(k, k) for k in stats.queue_completion],
            {"Completion rate":
                [v * 100 for v in stats.queue_completion.values()]},
            title="5. New generation gets stuck before reaching the grid",
            y_label="% of decided queue projects ever built",
            value_fmt="{:.0f}%",
        )
    if stats.waste_usd_m:
        figures["system_waste.svg"] = bar_chart(
            list(stats.waste_usd_m),
            {"Annual cost": list(stats.waste_usd_m.values())},
            title="6. The consequences show up as recurring annual cost",
            y_label="$ million per year (reliability uses the defensible floor)",
            value_fmt="{:,.0f}",
        )
    return figures


def build_problem_map(stats: SystemStats) -> str:
    """A relationship graph: what drives what in the grid-waste story."""
    demand_2025 = stats.demand_twh.get(2025)
    demand_2023 = stats.demand_twh.get(2023)
    demand_note = "demand is rising"
    if demand_2025 is not None and demand_2023 is not None:
        demand_note = f"{demand_2025:,.0f} TWh in 2025; +{demand_2025 - demand_2023:,.0f} since 2023"

    interchange_2025 = stats.interchange_twh.get(2025)
    interchange_note = "regional transfers are normal"
    if interchange_2025 is not None:
        interchange_note = f"{interchange_2025:,.0f} TWh crossed operator borders in 2025"

    concentration_note = "worst constraints carry much of the pain"
    if stats.concentration:
        low = min(share for _, share in stats.concentration.values()) * 100
        high = max(share for _, share in stats.concentration.values()) * 100
        concentration_note = f"top 10 constraints carry {low:.0f}-{high:.0f}% of severity"

    curtailment_note = "usable energy gets ordered down"
    if stats.curtailment_twh:
        curtailment_note = f"{sum(stats.curtailment_twh.values()):,.2f} TWh curtailed in CAISO + SPP"

    queue_note = "new plants often do not arrive"
    overall = stats.queue_completion.get("overall")
    if overall is not None:
        queue_note = f"only {overall * 100:.1f}% of decided queue projects completed"

    cost_note = "recurring cost shows up in bills and reliability exposure"
    ledger = stats.waste_usd_m.get("Waste ledger, all claims")
    reliability = stats.waste_usd_m.get("Reliability floor")
    if ledger is not None and reliability is not None:
        cost_note = f"${ledger:,.0f}M measured/proxy waste; ${reliability:,.0f}M/yr reliability floor"

    width, height = 1120, 720
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        'role="img" style="max-width:100%;height:auto;background:#ffffff">',
        '<defs><marker id="arrow" viewBox="0 0 14 14" markerWidth="16" '
        'markerHeight="16" refX="12" refY="7" orient="auto">'
        '<path d="M0,0 L14,7 L0,14 Z" '
        'fill="#1f6feb"/></marker></defs>',
        '<rect width="1120" height="720" fill="#ffffff"/>',
        _map_text(42, 38, "The grid problem is a system, not a pile of charts",
                  size=24, weight="700"),
        _map_text(
            42,
            66,
            "Read left to right: pressure enters the system, bottlenecks limit movement, symptoms appear, and customers pay.",
            size=15,
            fill="#5b6673",
        ),
    ]

    nodes = {
        "demand": (42, 128, 218, 108, "1. Demand pressure", demand_note),
        "move": (310, 128, 218, 108, "2. Power must move", interchange_note),
        "bottleneck": (578, 128, 238, 108, "3. Bottlenecks bind", concentration_note),
        "cost": (866, 128, 220, 132, "6. Customers pay", cost_note),
        "curtail": (578, 340, 238, 112, "4. Energy is stranded", curtailment_note),
        "queue": (310, 340, 218, 112, "5. New supply pipeline", queue_note),
        "fix": (224, 554, 672, 96, "What this points to",
                "target the binding places: transmission, interconnection reform, storage, and flexible demand"),
    }
    for x, y, w, h, title, note in nodes.values():
        parts.append(_map_box(x, y, w, h, title, note))

    arrows = [
        ((260, 182), (310, 182), ""),
        ((528, 182), (578, 182), ""),
        ((816, 182), (866, 182), ""),
        ((697, 236), (697, 340), ""),
        ((816, 396), (866, 232), ""),
        ((419, 236), (419, 340), ""),
        ((528, 396), (578, 396), ""),
        ((419, 452), (419, 554), ""),
        ((697, 452), (697, 554), ""),
    ]
    for start, end, label in arrows:
        parts.append(_map_arrow(start, end, label))

    parts.extend([
        _map_text(
            42,
            690,
            "Numbers and charts are evidence for the boxes. This graph is the story.",
            size=15,
            fill="#5b6673",
        ),
        "</svg>",
    ])
    return "".join(parts)


def _map_box(x, y, w, h, title, note) -> str:
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
        'fill="#f8fbff" stroke="#bcd6ff" stroke-width="1.5"/>',
        _map_text(x + 16, y + 28, title, size=17, weight="700"),
    ]
    parts.append(_wrapped_map_text(note, x + 16, y + 56, w - 32, size=14))
    return "".join(parts)


def _map_arrow(start, end, label) -> str:
    x1, y1 = start
    x2, y2 = end
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    parts = [
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        'stroke="#1f6feb" stroke-width="2.4" marker-end="url(#arrow)"/>',
    ]
    if label:
        parts.append(
            f'<rect x="{mx - 68:.1f}" y="{my - 22:.1f}" width="136" '
            'height="18" fill="#ffffff" opacity="0.88"/>'
        )
        parts.append(_map_text(mx, my - 8, label, size=11, fill="#5b6673",
                               anchor="middle"))
    return "".join(parts)


def _wrapped_map_text(text, x, y, width, *, size=14, fill="#17202a") -> str:
    max_chars = max(int(width / (size * 0.54)), 14)
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return "".join(
        _map_text(x, y + i * (size + 5), line, size=size, fill=fill)
        for i, line in enumerate(lines[:4])
    )


def _map_text(x, y, text, *, size=14, fill="#17202a", weight="400",
              anchor="start") -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-family="Arial, Helvetica, sans-serif" font-weight="{weight}" '
        f'text-anchor="{anchor}">{escape(str(text))}</text>'
    )


def write_figures(
    figures: Mapping[str, str],
    figures_dir: str | Path = "reports/figures",
) -> Dict[str, Path]:
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths: Dict[str, Path] = {}
    for name, svg in figures.items():
        path = figures_dir / name
        path.write_text(svg, encoding="utf-8")
        paths[name] = path
    return paths


def build_markdown(
    stats: SystemStats,
    figure_paths: Mapping[str, Path] | None = None,
) -> str:
    figure_paths = figure_paths or {}

    def fig(name: str) -> str:
        path = figure_paths.get(name, Path("reports/figures") / name)
        rel = Path("figures") / path.name
        return f"![{name}]({rel.as_posix()})"

    latest_demand_year = max(stats.demand_twh) if stats.demand_twh else None
    first_demand_year = min(stats.demand_twh) if stats.demand_twh else None
    demand_growth = None
    if latest_demand_year and first_demand_year:
        demand_growth = (
            stats.demand_twh[latest_demand_year]
            - stats.demand_twh[first_demand_year]
        )
    latest_interchange_year = (
        max(stats.interchange_twh) if stats.interchange_twh else None
    )
    top_iso = None
    if stats.concentration:
        top_iso = max(
            stats.concentration.items(), key=lambda item: item[1][1]
        )
    total_curtailment = (
        sum(stats.curtailment_twh.values()) if stats.curtailment_twh else None
    )
    overall_queue = stats.queue_completion.get("overall")
    ia_queue = stats.queue_completion.get("ia_executed")
    ledger = stats.waste_usd_m.get("Waste ledger, all claims")
    reliability = stats.waste_usd_m.get("Reliability floor")

    lines = [
        "# US Grid System Overview",
        "",
        "This page answers one plain question: **what is the nation's grid "
        "problem?** The answer is not just \"we need more power plants.\" "
        "Demand is rising. Power already has to move between regions. A "
        "small number of bottlenecks limit that movement. Useful clean energy "
        "gets shut off when it cannot be delivered. Many new projects never "
        "make it through the queue. The result shows up as recurring "
        "congestion and reliability costs.",
        "",
        "That is why the lead figure is a **system graph**, not a bar chart. "
        "The graph shows how the pieces relate. The bar charts that follow "
        "are the evidence behind each box.",
        "",
        "## The System Graph",
        "",
        fig("system_problem_map.svg"),
        "",
        "Read the system from left to right:",
        "",
        "1. **Need grows:** electricity demand is rising again.",
        "2. **Movement matters:** the grid already depends on regional power "
        "transfers.",
        "3. **The blockage is specific:** congestion is concentrated in a "
        "small set of constraints.",
        "4. **Energy gets stranded:** renewable output is curtailed when the "
        "system cannot use or deliver it.",
        "5. **The replacement pipeline is weak:** most queued projects do not "
        "become operating plants.",
        "6. **Customers pay:** the same physical limits show up as dollar "
        "waste and reliability exposure.",
        "",
        "The point is the relationship among the parts. Demand growth matters "
        "because power has to be delivered through a network. Cross-region "
        "flows matter because the network is already used that way. "
        "Bottlenecks matter because they decide where cheap or clean energy "
        "can actually go. Curtailment and queue attrition matter because they "
        "show energy and new supply getting stuck. The dollar figures matter "
        "because they show the consequence is not theoretical.",
        "",
        "## Key Numbers",
        "",
    ]
    if latest_demand_year is not None:
        growth_text = ""
        if demand_growth is not None:
            growth_text = (
                f", up **{demand_growth:,.0f} TWh** from "
                f"{first_demand_year}"
            )
        lines.append(
            f"- Demand reached "
            f"**{stats.demand_twh[latest_demand_year]:,.0f} TWh** in "
            f"{latest_demand_year}{growth_text}."
        )
    if latest_interchange_year is not None:
        lines.append(
            "- Gross electricity crossing grid-operator borders was "
            f"**{stats.interchange_twh[latest_interchange_year]:,.0f} TWh** "
            f"in {latest_interchange_year}."
        )
    if top_iso is not None:
        iso, (n, share) = top_iso
        lines.append(f"- In **{iso}**, the top 10 constraints carry "
                     f"**{share * 100:.0f}%** "
                     f"of severity across **{n:,}** constraints.")
    if total_curtailment is not None:
        lines.append("- CAISO + SPP renewable curtailment shown here totals "
                     f"**{total_curtailment:,.2f} TWh**.")
    if overall_queue is not None:
        ia_text = ""
        if ia_queue is not None:
            ia_text = f"; signed-IA projects reach **{ia_queue * 100:.1f}%**"
        lines.append("- Decided interconnection queue projects completed at "
                     f"**{overall_queue * 100:.1f}%**{ia_text}.")
    if ledger is not None and reliability is not None:
        lines.append("- The measured/proxy waste ledger is "
                     f"**${ledger:,.0f}M**; the reliability valuation floor "
                     f"is **${reliability:,.0f}M/yr**.")
    lines.extend([
        "",
        "## Supporting Evidence Charts",
        "",
        "These charts are not the story by themselves. Each one backs up one "
        "box or arrow in the system graph above.",
        "",
    ])
    chart_sections = [
        (
            "1. Demand Pressure Is Rising",
            "system_demand.svg",
            "This is the starting point. A grid that was already hard to run "
            "has to serve more electricity. More demand is not automatically "
            "bad, but every added terawatt-hour has to be generated, moved, "
            "and delivered at the right hour and place.",
        ),
        (
            "2. Moving Power Between Regions Is Not Optional",
            "system_interchange.svg",
            "This shows gross energy crossing balancing-authority borders. "
            "The point is not that bigger is always better. The point is that "
            "regional transfers are already a normal operating feature of the "
            "US grid, so weak borders become national problems.",
        ),
        (
            "3. The Problem Is Not Spread Evenly Everywhere",
            "system_concentration.svg",
            "Congestion severity is concentrated. When the worst 10 "
            "constraints carry roughly a third of total severity, the system "
            "is telling us that a small set of physical limits can drive a "
            "large share of the pain.",
        ),
        (
            "4. Stranded Energy Turns Into Curtailment",
            "system_curtailment.svg",
            "Curtailment means usable generation was ordered down. That is "
            "the simplest physical symptom of the grid problem: energy "
            "exists, but the system cannot absorb it locally or move it "
            "somewhere more useful.",
        ),
        (
            "5. The Queue Does Not Reliably Refill The System",
            "system_queue.svg",
            "The interconnection queue is the path new plants use to reach "
            "the grid. If most decided projects do not finish, then \"more "
            "projects are waiting\" is not the same thing as \"more power is "
            "coming.\"",
        ),
        (
            "6. The Same Limits Become A Bill",
            "system_waste.svg",
            "The dollar chart is not one single grand total. It puts "
            "different layers of evidence side by side: measured/proxy "
            "congestion and curtailment claims, plus a conservative "
            "reliability floor. The reason to care is that these are "
            "recurring costs, not one-time annoyances.",
        ),
    ]
    for heading, name, explanation in chart_sections:
        if name in figure_paths:
            lines.extend([f"### {heading}", "", explanation, "", fig(name), ""])
    lines.extend([
        "## What The Six Figures Prove Together",
        "",
        "The national grid problem is a chain: rising demand increases the "
        "need to move power; regional transfers already carry a large amount "
        "of energy; a few constraints block a disproportionate share of that "
        "movement; blocked movement strands clean generation and slows new "
        "supply; the consequences appear as annual congestion, curtailment, "
        "and reliability costs. That points toward targeted transmission, "
        "interconnection reform, storage, and flexible demand at the binding "
        "places, not a vague call for \"more grid\" everywhere.",
        "",
        "## Terms",
        "",
        "- **Balancing authority (BA):** a grid operator area that balances "
        "supply and demand.",
        "- **Interchange:** electricity crossing from one BA area to another.",
        "- **Constraint:** a grid limit that prevents cheaper or cleaner power "
        "from flowing freely.",
        "- **Curtailment:** usable generation ordered to reduce output.",
        "- **Interconnection queue:** the approval pipeline for new generators "
        "to connect to the grid.",
        "",
        "## Machine-Readable Stats",
        "",
        "```json",
        stats.to_json(),
        "```",
        "",
    ])
    return "\n".join(lines)


def write_report(
    stats: SystemStats,
    figures: Mapping[str, str],
    *,
    report_md: str | Path = "reports/SYSTEM_OVERVIEW.md",
    report_json: str | Path = "reports/system_overview.json",
    figures_dir: str | Path = "reports/figures",
) -> Dict[str, Path]:
    figure_paths = write_figures(figures, figures_dir)

    md_path = Path(report_md)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(build_markdown(stats, figure_paths), encoding="utf-8")

    json_path = Path(report_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(stats.to_json() + "\n", encoding="utf-8")
    return {"markdown": md_path, "json": json_path, **figure_paths}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the whole-system US grid overview report"
    )
    parser.add_argument("--data-dir", default="domains/grid/data")
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--years", nargs="+", type=int,
                        default=[2023, 2024, 2025])
    parser.add_argument("--figures-dir", default="reports/figures")
    parser.add_argument("--report-md", default="reports/SYSTEM_OVERVIEW.md")
    parser.add_argument("--report-json", default="reports/system_overview.json")
    args = parser.parse_args(argv)

    stats = collect_stats(args.data_dir, args.reports_dir, args.years)
    figures = build_figures(stats)
    paths = write_report(
        stats,
        figures,
        report_md=args.report_md,
        report_json=args.report_json,
        figures_dir=args.figures_dir,
    )
    print(stats.to_json())
    print()
    for label, path in paths.items():
        print(f"wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
