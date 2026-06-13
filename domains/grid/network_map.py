# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Interactive, zoomable network map of the BA interchange grid.

The grid is a Category: objects are balancing authorities (the hubs)
and morphisms are interchange tie-lines (the paths). This module turns
that structure into one self-contained HTML page a non-expert can
explore. It offers two views of the same graph:

- Geographic: each BA at the generation-weighted centroid of the states
  it operates in (domains/grid/geo.py, from eGRID), Albers-projected.
  Placement is a representative point and ties are schematic connectors,
  not physical transmission routes.
- Spectral: node placement from the Laplacian eigenvectors of the flow
  graph (grid_spectral.py) - strongly coupled BAs sit together and the
  weak seam pulls apart. Derived from the measured interchange itself.

Edge colour encodes Ollivier-Ricci curvature (grid_ricci.py):
red = a structural bottleneck (negative curvature carrying real flow).

A what-if mode lets the user switch ties (or a whole BA) off and see the
live consequence: lost interchange, BAs cut off, and how the network
splits. The cheap structural metrics recompute in the browser; the
curvature/spectral ranking stays at its measured baseline (a full
geometry recompute needs the Python pipeline, e.g. the daily build).

Build:
    python -m domains.grid.run_network_map ^
        --interchange domains\\grid\\data\\EIA930_INTERCHANGE_2025_Jan_Jun.csv ^
                      domains\\grid\\data\\EIA930_INTERCHANGE_2025_Jul_Dec.csv ^
        --egrid domains\\grid\\data\\egrid2023_data_rev2.xlsx ^
        --out docs\\network_map.html
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import date
from html import escape
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Mapping, Tuple

from domains.grid.agent_contract import map_agent_payload
from domains.grid.flow_geometry import TieLine, build_flow_category, load_interchange


@dataclass
class MapNode:
    name: str           # BA code, e.g. "PJM"
    sx: float           # spectral layout coordinate, normalized [0,1]
    sy: float
    gx: float           # geographic layout coordinate, normalized [0,1]
    gy: float
    geo_known: bool     # True if gx/gy came from a real centroid
    gross_mwh: float    # total tie usage incident to this BA
    degree: int         # number of ties
    side: int           # Fiedler partition side (0 / 1)


@dataclass
class MapEdge:
    a: str
    b: str
    source: str         # net-flow direction source
    target: str
    gross_mwh: float
    net_mwh: float      # signed magnitude, source -> target
    curvature: float
    bottleneck: bool


@dataclass
class NetworkMap:
    nodes: List[MapNode] = field(default_factory=list)
    edges: List[MapEdge] = field(default_factory=list)
    total_gross_mwh: float = 0.0
    algebraic_connectivity: float = 0.0
    coupling: str = ""
    n_bottlenecks: int = 0
    geo_coverage: int = 0
    daily_date: str | None = None  # latest daily-pulse date attached, if any
    # per-BA and per-tie evidence for click-through (see map_overlays)
    node_facts: Dict[str, Dict] = field(default_factory=dict)
    edge_facts: Dict[Tuple[str, str], Dict] = field(default_factory=dict)


def _curvature_store(category):
    """Adapter giving grid_ricci unit-distance morphisms (see flow_geometry)."""

    class _Store:
        def list_morphisms(self, limit: int = 100000):
            return [
                SimpleNamespace(
                    source_name=m.source, target_name=m.target, confidence=1.0
                )
                for m in category.morphisms()[:limit]
            ]

    return _Store()


def _spectral_layout(category):
    """2-D coordinates from Laplacian eigenvectors 1 & 2, plus seam + coupling."""
    from komposos_wesys.geometry.grid_spectral import SpectralGraphAnalyzer

    spectral = SpectralGraphAnalyzer(category)
    spectral.build_laplacian()
    eigenvalues, eigenvectors = spectral.compute_spectrum()
    coupling = spectral.analyze_coupling()
    names = [n.replace("ba:", "") for n in spectral.node_names]
    n = len(names)

    cols = eigenvectors.shape[1]
    fx = eigenvectors[:, 1] if cols > 1 else eigenvectors[:, 0]
    fy = eigenvectors[:, 2] if cols > 2 else eigenvectors[:, 0]

    def _norm(vec):
        lo, hi = float(min(vec)), float(max(vec))
        if hi - lo < 1e-9:
            return None
        return [(float(v) - lo) / (hi - lo) for v in vec]

    nx, ny = _norm(fx), _norm(fy)
    positions: Dict[str, Tuple[float, float]] = {}
    if nx is None or ny is None:
        for i, name in enumerate(names):
            angle = 2 * math.pi * i / max(n, 1)
            positions[name] = (0.5 + 0.42 * math.cos(angle),
                               0.5 + 0.42 * math.sin(angle))
    else:
        for name, x, y in zip(names, nx, ny):
            positions[name] = (x, y)

    side = {name: (0 if float(v) < 0 else 1) for name, v in zip(names, fx)}
    return (
        positions, side,
        float(coupling["algebraic_connectivity"]),
        str(coupling.get("coupling_strength", "")),
    )


def compute_network(
    ties: List[TieLine],
    centroids: Mapping[str, Tuple[float, float]] | None = None,
    node_facts: Mapping[str, Dict] | None = None,
    edge_facts: Mapping[Tuple[str, str], Dict] | None = None,
) -> NetworkMap:
    """Build the renderable map: dual layout + curvature + flow stats.

    `centroids` is an optional BA -> (lat, lon) map (see geo.py). BAs
    without a centroid fall back to their spectral position so they
    still appear; only those with a real centroid are projected.
    `node_facts` / `edge_facts` are optional click-through evidence
    (see map_overlays.load_overlays).
    """
    from komposos_wesys.geometry.grid_ricci import OllivierRicciCurvature

    category = build_flow_category(ties)
    positions, side, fiedler, coupling = _spectral_layout(category)

    ricci = OllivierRicciCurvature(_curvature_store(category), alpha=0.5)
    curvatures = ricci.compute_all_curvatures()
    curv_by_pair: Dict[frozenset, float] = {}
    for (u, v), kappa in curvatures.edge_curvatures.items():
        curv_by_pair[frozenset((u.replace("ba:", ""), v.replace("ba:", "")))] = kappa

    gross_total: Dict[str, float] = {}
    degree: Dict[str, int] = {}
    edges: List[MapEdge] = []
    for t in ties:
        key = frozenset((t.ba_a, t.ba_b))
        kappa = curv_by_pair.get(key, 0.0)
        src, tgt = (t.ba_a, t.ba_b) if t.net_mwh >= 0 else (t.ba_b, t.ba_a)
        edges.append(MapEdge(
            a=t.ba_a, b=t.ba_b, source=src, target=tgt,
            gross_mwh=t.gross_mwh, net_mwh=abs(t.net_mwh),
            curvature=kappa, bottleneck=kappa < 0,
        ))
        for ba in (t.ba_a, t.ba_b):
            gross_total[ba] = gross_total.get(ba, 0.0) + t.gross_mwh
            degree[ba] = degree.get(ba, 0) + 1

    # Geographic layout: project only the BAs we both display and have a
    # centroid for, so out-of-frame footprints don't distort the frame.
    from domains.grid.geo import projected_positions

    centroids = centroids or {}
    present = {ba: centroids[ba] for ba in gross_total if ba in centroids}
    geo_pos = projected_positions(present)

    nodes: List[MapNode] = []
    for name in sorted(gross_total):
        sx, sy = positions.get(name, (0.5, 0.5))
        if name in geo_pos:
            gx, gy = geo_pos[name]
            geo_known = True
        else:
            gx, gy, geo_known = sx, sy, False
        nodes.append(MapNode(
            name=name, sx=sx, sy=sy, gx=gx, gy=gy, geo_known=geo_known,
            gross_mwh=gross_total.get(name, 0.0),
            degree=degree.get(name, 0), side=side.get(name, 0),
        ))

    return NetworkMap(
        nodes=nodes, edges=edges,
        total_gross_mwh=sum(t.gross_mwh for t in ties),
        algebraic_connectivity=fiedler, coupling=coupling,
        n_bottlenecks=sum(1 for e in edges if e.bottleneck),
        geo_coverage=sum(1 for n in nodes if n.geo_known),
        node_facts=dict(node_facts or {}),
        edge_facts=dict(edge_facts or {}),
    )


def _top_fuels(mix: Mapping[str, float], top: int = 3) -> List[Dict]:
    """Largest generation fuels for a BA as [{fuel, share}], share in [0,1]."""
    total = sum(mix.values())
    if total <= 0:
        return []
    ranked = sorted(mix.items(), key=lambda kv: kv[1], reverse=True)[:top]
    return [{"fuel": f, "share": v / total} for f, v in ranked]


def build_network(
    ties: List[TieLine],
    egrid_workbook: str | Path | None = None,
    reports_dir: str | Path | None = "reports",
    balance_csvs=None,
) -> NetworkMap:
    """Assemble a full map: ties + footprints + report/balance/daily overlays."""
    node_ids = {t.ba_a for t in ties} | {t.ba_b for t in ties}
    centroids = None
    ba_states = None
    fuel_mix: Dict[str, Dict[str, float]] = {}
    if egrid_workbook and Path(egrid_workbook).exists():
        from domains.grid.geo import load_or_build_footprints

        centroids, ba_states, fuel_mix = load_or_build_footprints(egrid_workbook)

    node_facts: Dict[str, Dict] = {}
    edge_facts: Dict[Tuple[str, str], Dict] = {}
    daily_date = None
    if reports_dir and Path(reports_dir).exists():
        from domains.grid.map_overlays import daily_overlays, load_overlays

        node_facts, edge_facts = load_overlays(
            reports_dir, node_ids, ba_states=ba_states)
        node_daily, edge_daily = daily_overlays(Path(reports_dir), node_ids)
        for ba, rec in node_daily.items():
            node_facts.setdefault(ba, {})["daily"] = rec
            daily_date = max(daily_date or rec["date"], rec["date"])
        for pair, rec in edge_daily.items():
            edge_facts.setdefault(pair, {})["daily"] = rec
            daily_date = max(daily_date or rec["date"], rec["date"])

    # Per-BA demand / generation / net interchange (all BAs) + fuel mix.
    if balance_csvs:
        from domains.grid.map_overlays import ba_balance_facts

        for ba, rec in ba_balance_facts(balance_csvs).items():
            if ba in node_ids:
                node_facts.setdefault(ba, {}).update(rec)
    for ba, mix in fuel_mix.items():
        if ba in node_ids and mix:
            node_facts.setdefault(ba, {})["fuel_mix"] = _top_fuels(mix)

    network = compute_network(
        ties, centroids=centroids,
        node_facts=node_facts, edge_facts=edge_facts)
    network.daily_date = daily_date
    return network


def _map_payload(network: NetworkMap) -> Dict:
    """JSON data island the browser renders, inspects, and recomputes."""
    return {
        "nodes": [
            {
                "id": n.name,
                "sx": round(n.sx, 5), "sy": round(n.sy, 5),
                "gx": round(n.gx, 5), "gy": round(n.gy, 5),
                "geo": n.geo_known,
                "gross_mwh": n.gross_mwh, "degree": n.degree, "side": n.side,
                "facts": network.node_facts.get(n.name, {}),
            }
            for n in network.nodes
        ],
        "edges": [
            {
                "a": e.a, "b": e.b, "source": e.source, "target": e.target,
                "gross_mwh": e.gross_mwh, "net_mwh": e.net_mwh,
                "curvature": round(e.curvature, 5), "bottleneck": e.bottleneck,
                "share": (e.gross_mwh / network.total_gross_mwh
                          if network.total_gross_mwh else 0.0),
                "facts": network.edge_facts.get(tuple(sorted((e.a, e.b))), {}),
            }
            for e in network.edges
        ],
        "stats": {
            "n_bas": len(network.nodes), "n_ties": len(network.edges),
            "total_gross_mwh": network.total_gross_mwh,
            "algebraic_connectivity": network.algebraic_connectivity,
            "coupling": network.coupling, "n_bottlenecks": network.n_bottlenecks,
            "geo_coverage": network.geo_coverage,
        },
    }


def build_map_html(
    networks: Mapping[str, NetworkMap] | NetworkMap,
    title: str = "US Grid — Interactive Network Map",
    generated: date | None = None,
    default: str | None = None,
) -> str:
    """Render the self-contained page. `networks` is {year: NetworkMap}
    (a bare NetworkMap is accepted and treated as a single 'latest' year).
    """
    if isinstance(networks, NetworkMap):
        networks = {"latest": networks}
    generated = generated or date.today()
    years = sorted(networks)
    default = default or years[-1]
    shown = networks[default]
    data = json.dumps(
        {
            "years": {y: _map_payload(n) for y, n in networks.items()},
            "available": years,
            "default": default,
            "agent": map_agent_payload(),
        },
        separators=(",", ":"),
    )
    geo_note = (
        f"{shown.geo_coverage}/{len(shown.nodes)} BAs placed geographically"
        if shown.geo_coverage else "geographic placement unavailable (no eGRID)"
    )
    year_note = (
        f" Years {years[0]}–{years[-1]} selectable; showing {default}."
        if len(years) > 1 and "latest" not in networks else ""
    )
    daily_note = (
        f" Daily pulse through {shown.daily_date} on covered seams."
        if shown.daily_date else ""
    )
    return _TEMPLATE.format(
        title=escape(title), css=_CSS, js=_JS, data=data,
        n_bas=len(shown.nodes), n_ties=len(shown.edges),
        gross_twh=f"{shown.total_gross_mwh / 1e6:,.0f}",
        fiedler=f"{shown.algebraic_connectivity:.4f}",
        coupling=escape(shown.coupling),
        n_bottlenecks=shown.n_bottlenecks,
        geo_note=escape(geo_note),
        daily_note=escape(year_note + daily_note),
        generated=generated.isoformat(),
    )


def write_map(
    networks: Mapping[str, NetworkMap] | NetworkMap,
    path: str | Path = "docs/network_map.html",
    title: str = "US Grid — Interactive Network Map",
    default: str | None = None,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        build_map_html(networks, title=title, default=default), encoding="utf-8")
    return path


def _balance_siblings(interchange_csvs):
    return [str(p).replace("INTERCHANGE", "BALANCE") for p in interchange_csvs]


def build_from_interchange(
    interchange_csvs,
    path: str | Path = "docs/network_map.html",
    title: str = "US Grid — Interactive Network Map",
    egrid_workbook: str | Path | None = None,
    reports_dir: str | Path | None = "reports",
    balance_csvs=None,
) -> Path:
    """End-to-end single-year build (BALANCE defaults to INTERCHANGE siblings)."""
    if balance_csvs is None:
        balance_csvs = _balance_siblings(interchange_csvs)
    ties = load_interchange(interchange_csvs)
    network = build_network(
        ties, egrid_workbook=egrid_workbook, reports_dir=reports_dir,
        balance_csvs=balance_csvs)
    return write_map(network, path=path, title=title)


def build_multiyear(
    year_to_interchange: Mapping[str, list],
    path: str | Path = "docs/network_map.html",
    title: str = "US Grid — Interactive Network Map",
    egrid_workbook: str | Path | None = None,
    reports_dir: str | Path | None = "reports",
) -> Path:
    """Build one network per year and emit a single page with a year selector.

    Geographic placement and report/daily overlays are shared; flows,
    spectral layout, and per-BA demand/generation are recomputed per year.
    """
    networks: Dict[str, NetworkMap] = {}
    for year, interchange in year_to_interchange.items():
        ties = load_interchange(interchange)
        networks[year] = build_network(
            ties, egrid_workbook=egrid_workbook, reports_dir=reports_dir,
            balance_csvs=_balance_siblings(interchange))
    return write_map(networks, path=path, title=title)


_CSS = """
:root { color-scheme: light; --ink:#17202a; --muted:#5b6673; --line:#d8dee6;
  --surface:#fff; --page:#f5f7fa; --stage1:#ffffff; --stage2:#eef2f7;
  --blue:#1f6feb; --amber:#b7791f; --red:#d64545; --green:#1f8f5f; }
[data-theme="dark"] { color-scheme: dark; --ink:#e7edf3; --muted:#9aa7b4;
  --line:#2b333d; --surface:#1b2026; --page:#0f1318; --stage1:#1b2230;
  --stage2:#0f1318; --blue:#4a8bf5; --amber:#d6a24a;
  --red:#f06a6a; --green:#3fb27a; }
* { box-sizing:border-box; }
html,body { margin:0; height:100%; }
body { background:var(--page); color:var(--ink);
  font:14px/1.5 Arial, Helvetica, sans-serif; }
header { padding:12px 18px; border-bottom:1px solid var(--line);
  background:var(--surface); }
h1 { font-size:clamp(17px,2.6vw,22px); margin:0 0 4px; }
header p { margin:0; color:var(--muted); font-size:12.5px; }
.layout { display:grid; grid-template-columns:1fr 330px; height:calc(100vh - 60px); }
@media (max-width:760px){ .layout{ grid-template-columns:1fr; height:auto; }
  .stage{ height:68vh; } .panel{ border-left:0; border-top:1px solid var(--line); } }
.stage { position:relative; background:
  radial-gradient(circle at 50% 40%, var(--stage1) 0%, var(--stage2) 100%);
  overflow:hidden; }
.stage.whatif::after { content:"What-if mode — editing the network"; position:absolute;
  top:10px; left:50%; transform:translateX(-50%); background:var(--amber); color:#fff;
  padding:3px 12px; border-radius:999px; font-size:11.5px; pointer-events:none; z-index:5; }
.btnrow { display:flex; gap:6px; margin:2px 0 8px; }
.btnrow button { font:13px Arial; border:1px solid var(--line); background:var(--surface);
  color:var(--ink); border-radius:6px; padding:5px 10px; cursor:pointer; }
.btnrow button.active { background:var(--blue); color:#fff; border-color:var(--blue); }
.btnrow button:disabled { opacity:.45; cursor:default; }
svg { width:100%; height:100%; display:block; cursor:grab; touch-action:none; }
svg.panning { cursor:grabbing; }
.edge { stroke-linecap:round; }
.edge.off { stroke:#c2c9d2 !important; stroke-dasharray:3 5; stroke-opacity:.55 !important; }
.edge.added { stroke:var(--green) !important; stroke-dasharray:7 5; stroke-opacity:.95 !important; }
.edge.dim, .node.dim { opacity:.1; }
.node circle { stroke:var(--surface); cursor:pointer; }
.node.islanded circle { stroke:var(--red); stroke-width:2.5; }
.node text { fill:var(--ink); pointer-events:none; paint-order:stroke;
  stroke:var(--stage1); stroke-width:2.6px; }
.node text.hidden { display:none; }
.controls { position:absolute; top:12px; left:12px; display:flex; gap:6px;
  flex-wrap:wrap; align-items:center; max-width:calc(100% - 24px); }
.controls button, .controls input, .controls a { font:13px Arial; border:1px solid var(--line);
  background:var(--surface); border-radius:6px; padding:6px 10px; cursor:pointer; }
.controls button.active { background:var(--blue); color:#fff; border-color:var(--blue); }
.controls input { cursor:text; width:130px; }
.controls a { color:var(--ink); text-decoration:none; }
.controls .group { display:flex; border:1px solid var(--line); border-radius:6px;
  overflow:hidden; }
.controls .group button { border:0; border-radius:0; border-right:1px solid var(--line); }
.controls .group button:last-child { border-right:0; }
.legend { position:absolute; bottom:12px; left:12px; background:var(--surface);
  opacity:.95; border:1px solid var(--line); border-radius:8px; padding:9px 11px;
  font-size:11.5px; max-width:300px; }
.legend b { display:block; margin-bottom:4px; }
.legend-toggle { all:unset; cursor:pointer; display:block; color:var(--ink); }
.legend-toggle b::after { content:""; }
.legend.collapsed .legend-body { display:none; }
.legend.collapsed .legend-toggle b::after { content:"  ▸  tap to show key"; font-weight:400;
  color:var(--muted); font-size:11px; }
.legend span { display:inline-block; width:11px; height:11px; border-radius:50%;
  margin-right:5px; vertical-align:-1px; }
.panel { border-left:1px solid var(--line); background:var(--surface);
  padding:16px; overflow-y:auto; }
.panel h2 { font-size:16px; margin:0 0 4px; }
.panel .kind { color:var(--muted); font-size:12px; text-transform:uppercase;
  letter-spacing:.04em; margin-bottom:10px; }
.row { display:flex; justify-content:space-between; gap:12px; padding:6px 0;
  border-bottom:1px solid var(--line); }
.row span { color:var(--muted); } .row strong { text-align:right; }
.tag { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; }
.tag.bottleneck { background:#fde8e8; color:var(--red); }
.tag.meshed { background:#e6f5ec; color:var(--green); }
.tag.warn { background:#fdf0e0; color:var(--amber); }
.hint { color:var(--muted); font-size:13px; }
.metrics { display:flex; flex-wrap:wrap; gap:14px; margin-top:6px; }
.metrics div { font-size:12px; color:var(--muted); }
.metrics b { display:block; font-size:16px; color:var(--ink); }
.neighbors { margin-top:12px; } .neighbors h3 { font-size:13px; margin:0 0 6px; }
.neighbors a { display:block; padding:4px 0; color:var(--blue); cursor:pointer;
  text-decoration:none; font-size:13px; border-bottom:1px solid var(--line); }
.agentbox { margin-top:12px; border:1px solid var(--line); border-radius:8px;
  background:var(--page); padding:10px; }
.agentbox h3 { font-size:13px; margin:0 0 8px; }
.agentbox pre { margin:8px 0 0; max-height:240px; overflow:auto; white-space:pre-wrap;
  overflow-wrap:anywhere; font:12px/1.45 Consolas, "Liberation Mono", monospace; }
.agentcmd { display:grid; grid-template-columns:1fr auto; gap:8px; align-items:start;
  padding:7px 0; border-top:1px solid var(--line); }
.agentcmd:first-of-type { border-top:0; }
.agentcmd code { font:12px/1.4 Consolas, "Liberation Mono", monospace;
  overflow-wrap:anywhere; }
.copybtn { font:12px Arial; border:1px solid var(--line); border-radius:6px;
  background:var(--surface); color:var(--ink); padding:4px 8px; cursor:pointer; }
.chatlog { display:flex; flex-direction:column; gap:9px; margin-top:12px; }
.chatmsg { border:1px solid var(--line); border-radius:8px; padding:9px 10px;
  background:var(--page); font-size:13px; }
.chatmsg.user { align-self:flex-end; background:var(--blue); color:#fff;
  border-color:var(--blue); max-width:92%; }
.chatmsg.agent { align-self:stretch; }
.chatmsg.error { border-color:var(--red); }
.chatinput { display:grid; grid-template-columns:1fr auto; gap:8px; margin-top:12px; }
.chatinput textarea { min-height:54px; resize:vertical; font:13px Arial;
  border:1px solid var(--line); border-radius:8px; background:var(--surface);
  color:var(--ink); padding:8px; }
.chatinput button { font:13px Arial; border:1px solid var(--blue); border-radius:8px;
  background:var(--blue); color:#fff; padding:0 12px; cursor:pointer; }
.chips { display:flex; flex-wrap:wrap; gap:6px; margin-top:10px; }
.chips button { font:12px Arial; border:1px solid var(--line); border-radius:999px;
  background:var(--surface); color:var(--ink); padding:5px 9px; cursor:pointer; }
.artifact { border-top:1px solid var(--line); padding-top:8px; margin-top:8px; }
.artifact h3 { font-size:13px; margin:0 0 5px; }
.artifact p { margin:0 0 4px; }
.artifact .row { font-size:12px; }
footer { padding:7px 18px; color:var(--muted); font-size:11.5px;
  border-top:1px solid var(--line); background:var(--surface); }
"""

_JS = r"""
const PAYLOAD = JSON.parse(document.getElementById('map-data').textContent);
const YEARS = PAYLOAD.years;            // {year: {nodes, edges, stats}}
const AVAILABLE = PAYLOAD.available;    // sorted year strings
const AGENT = PAYLOAD.agent || {};
const NS = 'http://www.w3.org/2000/svg';
const W = 1000, H = 1000, PAD = 70;
const svg = document.getElementById('map');
svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
const vp = document.getElementById('viewport');

const SIDE_COLOR = ['#1f6feb', '#b7791f'];
const twh = mwh => (mwh/1e6).toLocaleString(undefined,{maximumFractionDigits:1}) + ' TWh';
const usd = v => v>=1e9 ? '$'+(v/1e9).toFixed(1)+'B' : v>=1e6 ? '$'+(v/1e6).toFixed(1)+'M'
  : '$'+Math.round(v).toLocaleString();
const baseR = n => 4 + 16 * Math.sqrt(n.gross_mwh / maxGross);

let year = PAYLOAD.default;
let mode = 'geo';
let tool = 'inspect';                 // 'inspect' | 'scenario' | 'agent'
let selectedContext = null;           // last selected BA/tie for local AI commands
let chatMessages = [];
let scale = 1, tx = 0, ty = 0;
const offEdges = new Set();           // disabled tie indices (what-if)
let linking = false, pendingAdd = null, nAdded = 0;  // add-a-link state
const history = [];                   // undo stack of closures
const COMP_PALETTE = ['#5b6673','#e8703a','#9b5de5','#0096c7','#d62246','#b7791f'];
const pos = {};                       // id -> {x,y} in [0,1] after layout

// these are (re)built per displayed year by buildGraph()
let DATA, nodeById, maxGross, maxEdge, adjacency, edgeEls, nodeEls;

function buildGraph(){
  DATA = YEARS[year];
  offEdges.clear(); history.length = 0; nAdded = 0; linking = false; pendingAdd = null;
  while (vp.firstChild) vp.removeChild(vp.firstChild);
  nodeById = {}; DATA.nodes.forEach(n => { nodeById[n.id] = n; });
  maxGross = Math.max(...DATA.nodes.map(n => n.gross_mwh), 1);
  maxEdge = Math.max(...DATA.edges.map(e => e.gross_mwh), 1);
  adjacency = {}; DATA.nodes.forEach(n => adjacency[n.id] = []);
  edgeEls = []; nodeEls = {};
  DATA.edges.forEach((e, i) => {
    if (!nodeById[e.a] || !nodeById[e.b]) return;
    adjacency[e.a].push({i, other: e.b});
    adjacency[e.b].push({i, other: e.a});
    const line = document.createElementNS(NS, 'line');
    line.setAttribute('class', 'edge'); line.style.cursor = 'pointer';
    line.addEventListener('click', ev => { ev.stopPropagation(); onEdge(e, i); });
    vp.appendChild(line); edgeEls.push({el: line, e, i});
  });
  DATA.nodes.forEach(n => {
    const g = document.createElementNS(NS, 'g');
    g.setAttribute('class', 'node');
    const c = document.createElementNS(NS, 'circle');
    c.setAttribute('fill', SIDE_COLOR[n.side] || '#1f6feb');
    c.setAttribute('fill-opacity', 0.85);
    const t = document.createElementNS(NS, 'text');
    t.setAttribute('text-anchor', 'middle'); t.textContent = n.id;
    g.appendChild(c); g.appendChild(t);
    g.addEventListener('click', ev => { ev.stopPropagation(); onNode(n); });
    vp.appendChild(g); nodeEls[n.id] = {g, c, t};
  });
  layout();
}

// per-year series for a node/tie metric, for the inspector trend rows
function nodeSeries(id, key){
  return AVAILABLE.map(y => {
    const n = YEARS[y].nodes.find(x => x.id === id);
    return {y, v: n ? (n.facts || {})[key] : null};
  });
}
function edgeSeries(a, b){
  return AVAILABLE.map(y => {
    const e = YEARS[y].edges.find(x => (x.a===a&&x.b===b)||(x.a===b&&x.b===a));
    return {y, v: e ? e.gross_mwh : null};
  });
}
function trendRow(label, series, fmt){
  const parts = series.filter(s => s.v != null).map(s => `${s.y} ${fmt(s.v)}`);
  return parts.length > 1 ? row(label, parts.join('  ·  ')) : '';
}

// ---- layout (mode) + non-overlap relaxation ----
const px = id => PAD + pos[id].x * (W - 2*PAD);
const py = id => PAD + pos[id].y * (H - 2*PAD);
function layout(){
  DATA.nodes.forEach(n => {
    pos[n.id] = mode === 'geo' ? {x:n.gx, y:n.gy} : {x:n.sx, y:n.sy};
  });
  relax();
  draw();
}
function relax(){              // Dorling-style: push overlapping circles apart
  const ids = DATA.nodes.map(n => n.id);
  const span = (W - 2*PAD);
  for (let it=0; it<80; it++){
    for (let a=0; a<ids.length; a++) for (let b=a+1; b<ids.length; b++){
      const A=ids[a], B=ids[b];
      let dx=(pos[B].x-pos[A].x)*span, dy=(pos[B].y-pos[A].y)*span;
      let d=Math.hypot(dx,dy)||0.01;
      const min=(baseR(nodeById[A])+baseR(nodeById[B]))*1.25;
      if (d<min){ const push=(min-d)/d*0.5;
        const ox=dx*push/span, oy=dy*push/span;
        pos[A].x-=ox; pos[A].y-=oy; pos[B].x+=ox; pos[B].y+=oy; }
    }
  }
  for (const id of ids){ pos[id].x=Math.min(1,Math.max(0,pos[id].x));
    pos[id].y=Math.min(1,Math.max(0,pos[id].y)); }
}

// ---- draw (positions, counter-scaled sizes, LOD labels) ----
function draw(){
  const cs = 1/scale;                              // counter-scale
  const labelCut = 11 * cs;                        // hide tiny labels
  edgeEls.forEach(({el, e, i}) => {
    el.setAttribute('x1', px(e.a)); el.setAttribute('y1', py(e.a));
    el.setAttribute('x2', px(e.b)); el.setAttribute('y2', py(e.b));
    const off = offEdges.has(i);
    el.classList.toggle('off', off);
    if (e.hypothetical){ el.setAttribute('stroke-width', 2.4*cs); return; }
    el.setAttribute('stroke', e.bottleneck ? '#d64545' : '#9aa7b4');
    el.setAttribute('stroke-width', (0.6 + 5*Math.sqrt(e.gross_mwh/maxEdge))*cs);
    el.setAttribute('stroke-opacity', off ? 0.5 : (e.bottleneck ? 0.85 : 0.45));
  });
  DATA.nodes.forEach(n => {
    const {g, c, t} = nodeEls[n.id]; const r = baseR(n);
    g.setAttribute('transform', `translate(${px(n.id)},${py(n.id)})`);
    c.setAttribute('r', r*cs); c.setAttribute('stroke-width', 1.2*cs);
    t.setAttribute('dy', (-r-3)*cs); t.setAttribute('font-size', 9*cs);
    const big = r >= 9 || n.gross_mwh/maxGross > 0.18;
    t.classList.toggle('hidden', !(big || r*scale > labelCut*scale));
  });
}
function apply(){ vp.setAttribute('transform', `translate(${tx},${ty}) scale(${scale})`); draw(); }

// ---- inspector / what-if ----
const panel = document.getElementById('panel');
const row = (l,v) => `<div class="row"><span>${l}</span><strong>${v}</strong></div>`;
const head = t => `<h3 style="font-size:13px;margin:14px 0 4px;color:var(--muted)">${t}</h3>`;
const pct = x => (x*100).toFixed(0)+'%';
const dailyRow = d => head(`Latest daily pulse · ${d.date}`)+
  row(d.label, d.value.toLocaleString(undefined,{maximumFractionDigits:2})+' '+d.unit);

function nodeFacts(f){
  if (!f || !Object.keys(f).length) return '';
  let h = '';
  if (f.demand_twh!=null || f.netgen_twh!=null || (f.fuel_mix||[]).length){
    h += head('Supply & demand (annual)');
    if (f.demand_twh!=null) h += row('Electricity demand', twh(f.demand_twh*1e6));
    if (f.netgen_twh!=null) h += row('Net generation', twh(f.netgen_twh*1e6));
    if (f.net_interchange_twh!=null) h += row('Net interchange',
      (f.net_interchange_twh>=0?'exports ':'imports ')+twh(Math.abs(f.net_interchange_twh)*1e6));
    if ((f.fuel_mix||[]).length) h += row('Top fuels',
      f.fuel_mix.map(x=>`${x.fuel} ${pct(x.share)}`).join(' · '));
  }
  if (f.curtailment_twh!=null || f.n_constraints!=null || f.reliability_value_usd!=null ||
      (f.waste_claims||[]).some(c=>c.value_usd>0)){
    h += head('Congestion & reliability');
    if (f.curtailment_twh!=null) h += row('Renewable curtailment', twh(f.curtailment_twh*1e6));
    if (f.n_constraints!=null) h += row('Congestion constraints',
      f.n_constraints.toLocaleString()+(f.top10_share!=null?` (top 10 carry ${pct(f.top10_share)})`:''));
    if (f.reliability_value_usd!=null) h += row('Reliability value at stake', usd(f.reliability_value_usd)+'/yr');
    (f.waste_claims||[]).filter(c=>c.value_usd>0).forEach(c =>
      h += row(c.title||'Waste claim', usd(c.value_usd)+` · ${c.evidence||''}`));
  }
  if (f.daily) h += dailyRow(f.daily);
  return h;
}

function edgeFacts(f){
  let study = '';
  if (f){
    if (f.congestion_value_usd != null)
      study += row('Congestion value', usd(f.congestion_value_usd)+'/yr'+
        (f.evidence_status ? ` · ${String(f.evidence_status).replace(/_/g,' ')}` : ''));
    if (f.congestion_spread_usd_mwh != null)
      study += row('Congestion spread', '$'+f.congestion_spread_usd_mwh.toFixed(2)+'/MWh');
    if (f.importing_side)
      study += row('Power flows toward', `${f.importing_side} (from ${f.exporting_side})`);
    if (f.queue_active_gw != null)
      study += row('Queue waiting on this seam',
        `${f.queue_active_gw} GW active · ${f.queue_withdrawn_gw} GW withdrawn`);
    if (f.solution_status)
      study += row('Solution status', f.solution_status+
        (f.solution_value_usd ? ` · ${usd(f.solution_value_usd)}/yr` : ''));
  }
  let h = study ? head('Corridor evidence')+study : '';
  if (f && (f.top_projects||[]).length)
    h += head('Largest queued projects')+
      f.top_projects.map(p=>`<div class="row"><span>${p}</span></div>`).join('');
  if (f && f.solution_trend)
    h += `<p class="hint" style="margin-top:8px">${f.solution_trend}</p>`;
  if (f && f.daily) h += dailyRow(f.daily);
  if (!h) h = `<p class="hint" style="margin-top:12px">No corridor study attached to this tie yet.</p>`;
  return h;
}

function onNode(n){
  selectedContext = {kind:'ba', id:n.id};
  if (tool === 'scenario'){
    if (linking){
      if (!pendingAdd){ pendingAdd = n.id; highlightNode(n.id); return; }
      if (n.id !== pendingAdd) addHypotheticalEdge(pendingAdd, n.id);
      pendingAdd = null; linking = false; recompute(); return;
    }
    baOutageAction(n.id); recompute(); return;
  }
  highlightNode(n.id);
  const neigh = adjacency[n.id]
    .map(({i, other}) => ({other, gross: DATA.edges[i].gross_mwh, off: offEdges.has(i)}))
    .sort((a,b) => b.gross-a.gross);
  const active = neigh.filter(x => !x.off);
  panel.innerHTML =
    `<div class="kind">Object · balancing authority</div><h2>${n.id}</h2>`+
    (n.geo ? '' : `<p><span class="tag warn">no geo footprint</span></p>`)+
    row('Total tie usage', twh(n.gross_mwh))+
    row('Connected ties', `${active.length}${active.length<n.degree?` of ${n.degree} active`:''}`)+
    row('Spectral seam side', n.side===0?'A (Fiedler −)':'B (Fiedler +)')+
    nodeFacts(n.facts)+
    trendRow('Demand by year', nodeSeries(n.id,'demand_twh'), v=>twh(v*1e6))+
    `<div class="neighbors"><h3>Ties from here (by flow)</h3>`+
    neigh.map(x=>`<a data-go="${x.other}">${n.id} — ${x.other} · ${twh(x.gross)}${x.off?' · off':''}</a>`).join('')+
    `</div>`;
  panel.querySelectorAll('[data-go]').forEach(a =>
    a.addEventListener('click', () => onNode(nodeById[a.dataset.go])));
}

function onEdge(e, i){
  selectedContext = e.hypothetical
    ? {kind:'hypothetical', a:e.a, b:e.b}
    : {kind:'tie', a:e.a, b:e.b};
  if (tool === 'scenario'){ toggleEdgeAction(i); recompute(); return; }
  highlightEdge(i);
  if (e.hypothetical){
    panel.innerHTML = `<div class="kind">Hypothetical · added link</div><h2>${e.a} — ${e.b}</h2>`+
      `<p class="hint">A what-if transmission link you added. It carries no measured flow — `+
      `it only changes connectivity (which regions stay joined). Use What-if mode to cut or Reset to remove it.</p>`;
    return;
  }
  const tag = e.bottleneck
    ? `<span class="tag bottleneck">structural bottleneck</span>`
    : `<span class="tag meshed">well-meshed</span>`;
  panel.innerHTML =
    `<div class="kind">Morphism · interchange tie</div><h2>${e.a} — ${e.b}</h2><p>${tag}</p>`+
    row('Gross flow (usage)', twh(e.gross_mwh))+
    row('Net flow', twh(e.net_mwh))+
    row('Net direction', `${e.source} → ${e.target}`)+
    row('Share of all interchange', (e.share*100).toFixed(2)+'%')+
    row('Ollivier–Ricci curvature', e.curvature.toFixed(3))+
    row('Reading', e.bottleneck
      ? 'Negative curvature: a thin passage where one tie links regions that are otherwise weakly connected — congestion concentrates here.'
      : 'Non-negative curvature: redundant, meshed neighbourhood — resilient.')+
    trendRow('Flow by year', edgeSeries(e.a, e.b), v=>twh(v))+
    edgeFacts(e.facts);
}

// ---- what-if actions (each records an inverse for Undo) ----
function pushUndo(fn){ history.push(fn); if (history.length>200) history.shift(); }
function setEdgeOff(i, off){ if (off) offEdges.add(i); else offEdges.delete(i); }

function toggleEdgeAction(i){
  const was = offEdges.has(i);
  setEdgeOff(i, !was);
  pushUndo(() => setEdgeOff(i, was));
}
function baOutageAction(id){
  const inc = adjacency[id].map(x => x.i);
  if (!inc.length) return;
  const anyOn = inc.some(i => !offEdges.has(i));   // any on -> cut all; else restore all
  const prev = inc.map(i => [i, offEdges.has(i)]);
  inc.forEach(i => setEdgeOff(i, anyOn));
  pushUndo(() => prev.forEach(([i, was]) => setEdgeOff(i, was)));
}
function addHypotheticalEdge(a, b){
  const idx = DATA.edges.length;
  const e = {a, b, source:a, target:b, gross_mwh:0, net_mwh:0, curvature:0,
             bottleneck:false, share:0, facts:{}, hypothetical:true};
  DATA.edges.push(e); nAdded++;
  const line = document.createElementNS(NS, 'line');
  line.setAttribute('class', 'edge added'); line.style.cursor = 'pointer';
  line.addEventListener('click', ev => { ev.stopPropagation(); onEdge(e, idx); });
  vp.insertBefore(line, nodeEls[DATA.nodes[0].id].g);  // keep edges beneath nodes
  edgeEls.push({el: line, e, i: idx});
  adjacency[a].push({i: idx, other: b}); adjacency[b].push({i: idx, other: a});
  pushUndo(() => removeLastAdded(idx));
}
function removeLastAdded(idx){
  const rec = edgeEls.pop(); if (!rec) return;
  rec.el.remove(); DATA.edges.pop(); nAdded--; offEdges.delete(idx);
  adjacency[rec.e.a] = adjacency[rec.e.a].filter(x => x.i !== idx);
  adjacency[rec.e.b] = adjacency[rec.e.b].filter(x => x.i !== idx);
}
function undo(){ const fn = history.pop(); if (fn){ fn(); recompute(); } }

function components(){
  const seen = new Set(), comps = [];
  for (const n of DATA.nodes){
    if (seen.has(n.id)) continue;
    const stack=[n.id], comp=[]; seen.add(n.id);
    while(stack.length){ const id=stack.pop(); comp.push(id);
      for (const {i, other} of adjacency[id])
        if (!offEdges.has(i) && !seen.has(other)){ seen.add(other); stack.push(other); } }
    comps.push(comp);
  }
  return comps.sort((a,b)=>b.length-a.length);
}
function paintComponents(comps){
  if (comps.length <= 1){ restoreNodeColors(); return; }
  comps.forEach((comp, k) => comp.forEach(id =>
    nodeEls[id].c.setAttribute('fill',
      k === 0 ? (SIDE_COLOR[nodeById[id].side] || '#1f6feb')
              : COMP_PALETTE[(k-1) % COMP_PALETTE.length])));
}
function restoreNodeColors(){
  DATA.nodes.forEach(n =>
    nodeEls[n.id].c.setAttribute('fill', SIDE_COLOR[n.side] || '#1f6feb'));
}
function balanceOf(comp){
  let d=0, g=0; comp.forEach(id => { const f = nodeById[id].facts || {};
    d += f.demand_twh || 0; g += f.netgen_twh || 0; });
  return {d, g, net: g - d};
}

// what-if: live recompute of the cheap, honest structural metrics
function recompute(){
  draw();
  const comps = components();
  paintComponents(comps);
  const mainSet = new Set(comps[0] || []);
  let carried=0, qgw=0, cval=0, offCount=0;
  const offList=[];
  DATA.edges.forEach((e,i) => {
    if (e.hypothetical || !offEdges.has(i)) return;
    offCount++; carried += e.gross_mwh;
    const f = e.facts || {}; qgw += f.queue_active_gw || 0; cval += f.congestion_value_usd || 0;
    offList.push({i, e});
  });
  const islanded = DATA.nodes.filter(n => !mainSet.has(n.id)).map(n => n.id);
  DATA.nodes.forEach(n => nodeEls[n.id].g.classList.toggle('islanded', !mainSet.has(n.id)));
  const lpct = DATA.stats.total_gross_mwh ? carried/DATA.stats.total_gross_mwh*100 : 0;

  let h = `<div class="kind">What-if · scenario</div><h2>Network under stress</h2>`+
    `<div class="btnrow">`+
    `<button id="undo"${history.length ? '' : ' disabled'}>↶ Undo</button>`+
    `<button id="addlink" class="${linking ? 'active' : ''}">＋ Add link</button></div>`+
    `<p class="hint">${linking
      ? 'Click two hubs to connect them with a hypothetical new line.'
      : 'Click a tie to cut it, a hub for a full BA outage, or <b>＋ Add link</b> to build a new line.'}</p>`+
    row('Ties cut', offCount)+
    (nAdded>0 ? row('Hypothetical links added', nAdded) : '')+
    row('Interchange on severed ties', `${twh(carried)} (${lpct.toFixed(1)}%)`)+
    row('Network pieces', comps.length)+
    row('BAs cut off from the main grid', islanded.length);
  if (comps.length > 1){
    h += head('Each piece — can it feed itself?');
    comps.slice(0,6).forEach((comp, k) => {
      const b = balanceOf(comp), short = b.net < 0;
      h += `<div class="row"><span>${k===0?'Main grid':'Island '+k} · ${comp.length} BAs</span>`+
        `<strong style="color:${short?'var(--red)':'var(--green)'}">`+
        `${short?'short ':'surplus '}${twh(Math.abs(b.net)*1e6)}</strong></div>`;
    });
  }
  if (qgw>0) h += row('Active queue behind cut ties', qgw.toFixed(1)+' GW');
  if (cval>0) h += row('Congestion value disrupted', usd(cval)+'/yr');
  if (offList.length) h += head('Cut ties (click to restore)')+
    `<div class="neighbors">`+
    offList.slice(0,30).map(o => `<a data-restore="${o.i}">${o.e.a} — ${o.e.b}</a>`).join('')+
    `</div>`;
  if (islanded.length) h += `<div class="neighbors"><h3>Cut off from main grid</h3>`+
    islanded.slice(0,40).map(id => `<a data-go="${id}">${id}</a>`).join('')+`</div>`;
  h += `<p class="hint" style="margin-top:12px">This is a <b>connectivity</b> view: it shows `+
    `which regions stay linked and the flow/queue/value exposed on cut ties — not how power `+
    `reroutes (that needs a load-flow model). Curvature &amp; the seam stay at the measured baseline.</p>`;
  panel.innerHTML = h;
  document.getElementById('undo').addEventListener('click', undo);
  document.getElementById('addlink').addEventListener('click', () => {
    linking = !linking; pendingAdd = null; recompute(); });
  panel.querySelectorAll('[data-go]').forEach(a =>
    a.addEventListener('click', () => { tool='inspect'; setTool(); onNode(nodeById[a.dataset.go]); }));
  panel.querySelectorAll('[data-restore]').forEach(a =>
    a.addEventListener('click', () => { toggleEdgeAction(+a.dataset.restore); recompute(); }));
}

// ---- highlight ----
function highlightNode(id){
  const near = new Set(adjacency[id].map(x=>x.other)); near.add(id);
  edgeEls.forEach(({el,e}) => el.classList.toggle('dim', !(e.a===id||e.b===id)));
  Object.entries(nodeEls).forEach(([nid,o]) => o.g.classList.toggle('dim', !near.has(nid)));
}
function highlightEdge(i){
  const e = DATA.edges[i];
  edgeEls.forEach(o => o.el.classList.toggle('dim', o.i!==i));
  Object.entries(nodeEls).forEach(([nid,o]) =>
    o.g.classList.toggle('dim', nid!==e.a && nid!==e.b));
}
function clearHighlight(){
  edgeEls.forEach(o => o.el.classList.remove('dim'));
  Object.values(nodeEls).forEach(o => o.g.classList.remove('dim'));
}

// ---- pan + zoom (pointer events: mouse, touch, pen; pinch on multitouch) ----
const toMap = (cx, cy) => {  // client px -> viewBox units
  const r = svg.getBoundingClientRect();
  return {x:(cx-r.left)/r.width*W, y:(cy-r.top)/r.height*H};
};
function zoomAt(cx, cy, factor){
  const m = toMap(cx, cy);
  const ns = Math.min(Math.max(scale*factor, 0.5), 14);
  tx = m.x-(m.x-tx)*(ns/scale); ty = m.y-(m.y-ty)*(ns/scale); scale = ns; apply();
}
svg.addEventListener('wheel', ev => {
  ev.preventDefault();
  zoomAt(ev.clientX, ev.clientY, ev.deltaY<0 ? 1.15 : 1/1.15);
}, {passive:false});

const ptrs = new Map();      // active pointers: id -> {x,y}
let panLast = null, pinchDist = 0, moved = false;
function ptrMid(){
  const v=[...ptrs.values()]; return {x:(v[0].x+v[1].x)/2, y:(v[0].y+v[1].y)/2}; }
function ptrSpan(){
  const v=[...ptrs.values()]; return Math.hypot(v[0].x-v[1].x, v[0].y-v[1].y); }
svg.addEventListener('pointerdown', ev => {
  ptrs.set(ev.pointerId, {x:ev.clientX, y:ev.clientY});
  moved = false;
  if (ptrs.size === 1){ panLast = {x:ev.clientX, y:ev.clientY}; svg.classList.add('panning'); }
  else if (ptrs.size === 2){ pinchDist = ptrSpan(); panLast = null; }
});
window.addEventListener('pointermove', ev => {
  if (!ptrs.has(ev.pointerId)) return;
  ptrs.set(ev.pointerId, {x:ev.clientX, y:ev.clientY});
  const r = svg.getBoundingClientRect();
  if (ptrs.size >= 2 && pinchDist > 0){          // pinch zoom about the midpoint
    const span = ptrSpan(), mid = ptrMid();
    if (span > 0){ moved = true; zoomAt(mid.x, mid.y, span/pinchDist); pinchDist = span; }
  } else if (ptrs.size === 1 && panLast){        // drag to pan
    const dx=ev.clientX-panLast.x, dy=ev.clientY-panLast.y;
    if (Math.abs(dx)+Math.abs(dy) > 2) moved = true;
    tx += dx/r.width*W; ty += dy/r.height*H;
    panLast = {x:ev.clientX, y:ev.clientY}; apply();
  }
});
function endPtr(ev){
  if (!ptrs.has(ev.pointerId)) return;
  ptrs.delete(ev.pointerId);
  if (ptrs.size < 2) pinchDist = 0;
  if (ptrs.size === 1){ const v=[...ptrs.values()][0]; panLast={x:v.x, y:v.y}; }
  if (ptrs.size === 0){ panLast = null; svg.classList.remove('panning'); }
}
window.addEventListener('pointerup', endPtr);
window.addEventListener('pointercancel', endPtr);
// a drag/pinch ends with a click; swallow it so it doesn't clear the selection
svg.addEventListener('click', () => {
  if (moved){ moved = false; return; }
  if (tool==='scenario'){ if (pendingAdd){ pendingAdd=null; clearHighlight(); } recompute(); }
  else if (tool==='agent'){ clearHighlight(); showAgentPanel(); }
  else { clearHighlight(); resetPanel(); }
});

// ---- local agent API chat ----
const esc = s => String(s).replace(/[&<>"']/g, ch =>
  ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const actionAttr = action => encodeURIComponent(JSON.stringify(action || {}));

function contextLabel(){
  if (selectedContext && selectedContext.kind === 'ba'){
    return `BA ${selectedContext.id}`;
  }
  if (selectedContext && selectedContext.kind === 'tie'){
    return `Tie ${selectedContext.a}-${selectedContext.b}`;
  }
  return 'Network';
}

function starterQuestions(){
  if (selectedContext && selectedContext.kind === 'ba'){
    const target = selectedContext.id === 'PJM' ? 'MISO' : 'PJM';
    return [`Explain ${selectedContext.id} in plain English`,
      `What areas act like ${selectedContext.id}?`,
      `Find paths from ${selectedContext.id} to ${target}`];
  }
  if (selectedContext && selectedContext.kind === 'tie'){
    const pair = `${selectedContext.a}-${selectedContext.b}`;
    return [`Why is ${pair} important?`, `What breaks if ${pair} fails?`,
      `What evidence supports ${pair}?`];
  }
  return ['Where is power getting stuck?', 'What should I look at next?',
    'Explain the weakest seam'];
}

function renderArtifact(card){
  const actions = (card.actions || []).map(a =>
    `<button class="copybtn agentaction" data-action="${actionAttr(a)}">${esc(a.label || 'Use')}</button>`
  ).join('');
  const rows = (card.rows || []).map(r =>
    `<div class="row"><span>${esc(r.label || '')}${r.meta ? `<br><small>${esc(r.meta)}</small>` : ''}</span>`+
    `<strong>${esc(r.value == null ? '' : r.value)}</strong></div>`).join('');
  return `<div class="artifact"><h3>${esc(card.title || 'Result')}</h3>`+
    `<p>${esc(card.body || '')}</p>${actions ? `<div class="btnrow">${actions}</div>` : ''}${rows}</div>`;
}

function renderChat(){
  const msgs = chatMessages.map(m =>
    `<div class="chatmsg ${m.role}${m.error ? ' error' : ''}">`+
    `<div>${esc(m.text)}</div>`+
    `${(m.cards || []).map(renderArtifact).join('')}`+
    `${(m.provenance || []).length ? `<p class="hint">${esc(m.provenance.join(' | '))}</p>` : ''}`+
    `</div>`).join('');
  const chips = starterQuestions().map(q => `<button data-ask="${esc(q)}">${esc(q)}</button>`).join('');
  panel.innerHTML = `<div class="kind">Local AI</div><h2>Ask the grid engine</h2>`+
    row('Context', contextLabel())+
    row('Backend', '/api/grid/chat')+
    `<p class="hint">This chat calls the local KOMPOSOS backend running from this repo. `+
    `It uses grounded tools for numbers and structural claims.</p>`+
    `<div class="chips">${chips}</div>`+
    `<div class="chatlog" id="chatlog">${msgs || `<div class="chatmsg agent">Ask about a BA, a tie, a path, similarity, bottlenecks, seams, or a what-if cut.</div>`}</div>`+
    `<div class="chatinput"><textarea id="agentq" placeholder="Ask: path CISO PJM, similar to PJM, what if cut PJM-NYIS..."></textarea>`+
    `<button id="agentsend">Send</button></div>`;
  panel.querySelectorAll('[data-ask]').forEach(btn =>
    btn.addEventListener('click', () => sendAgentMessage(btn.dataset.ask || '')));
  panel.querySelectorAll('[data-action]').forEach(btn =>
    btn.addEventListener('click', () => {
      try { runAgentAction(JSON.parse(decodeURIComponent(btn.dataset.action || '{}'))); }
      catch(e) {}
    }));
  document.getElementById('agentsend').addEventListener('click', () => {
    const box = document.getElementById('agentq');
    sendAgentMessage(box.value);
  });
  document.getElementById('agentq').addEventListener('keydown', ev => {
    if (ev.key === 'Enter' && !ev.shiftKey){ ev.preventDefault(); sendAgentMessage(ev.target.value); }
  });
  const log = document.getElementById('chatlog');
  if (log) log.scrollTop = log.scrollHeight;
}

function showAgentPanel(){
  renderChat();
}

function highlightAgentResult(resp){
  if (!resp || !resp.highlight) return;
  applyAgentHighlight(resp.highlight);
}

function applyAgentHighlight(highlight){
  clearHighlight();
  const nodes = new Set(highlight.nodes || []);
  const edgePairs = new Set((highlight.edges || []).map(p => p.split('-').sort().join('-')));
  if (!nodes.size && !edgePairs.size) return;
  edgeEls.forEach(({el,e}) => {
    const pair = [e.a, e.b].sort().join('-');
    el.classList.toggle('dim', !edgePairs.has(pair));
  });
  Object.entries(nodeEls).forEach(([nid,o]) => o.g.classList.toggle('dim', !nodes.has(nid)));
}

function edgeIndexForPair(pair){
  const want = String(pair || '').split('-').map(x=>x.trim()).sort().join('-');
  return DATA.edges.findIndex(e => [e.a, e.b].sort().join('-') === want);
}

function runAgentAction(action){
  if (!action || !action.type) return;
  if (action.type === 'highlight'){
    applyAgentHighlight({nodes:action.nodes || [], edges:action.edges || []});
  } else if (action.type === 'apply_cut'){
    const prev = [];
    (action.cut || []).forEach(pair => {
      const i = edgeIndexForPair(pair);
      if (i >= 0){ prev.push([i, offEdges.has(i)]); setEdgeOff(i, true); }
    });
    if (prev.length) pushUndo(() => prev.forEach(([i, was]) => setEdgeOff(i, was)));
    tool = 'scenario';
    setTool();
  }
}

async function sendAgentMessage(text){
  const message = (text || '').trim();
  if (!message) return;
  chatMessages.push({role:'user', text:message});
  chatMessages.push({role:'agent', text:'Thinking with local tools...'});
  renderChat();
  try {
    const resp = await fetch('/api/grid/chat', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message, year, context:selectedContext})
    });
    const data = await resp.json();
    chatMessages.pop();
    chatMessages.push({
      role:'agent',
      text:data.answer || 'No answer returned.',
      cards:data.cards || [],
      provenance:data.provenance || [],
      error:!data.ok
    });
    renderChat();
    highlightAgentResult(data);
  } catch (err) {
    chatMessages.pop();
    chatMessages.push({
      role:'agent',
      text:'The local agent API is not running. Start it with: python -m domains.grid.agent_server --port 8000, then reopen this page from that server.',
      error:true,
      cards:[{title:'Static fallback', body:'GitHub Pages/static file mode cannot call Python tools by itself. The local API bridge is required.'}]
    });
    renderChat();
  }
}

// ---- controls ----
function resetPanel(){
  panel.innerHTML = `<div class="kind">Inspector</div>`+
    `<p class="hint">Click any hub or tie-line to see its data. Scroll to zoom, drag to pan. `+
    `Switch to <b>What-if</b> to take ties or BAs offline and watch the grid respond.</p>`+
    `<div class="metrics">`+
    `<div><b>${DATA.stats.n_bas}</b>balancing authorities</div>`+
    `<div><b>${DATA.stats.n_ties}</b>tie-lines</div>`+
    `<div><b>${DATA.stats.n_bottlenecks}</b>bottleneck ties</div>`+
    `<div><b>${DATA.stats.coupling}</b>spectral coupling</div></div>`;
}
function setMode(m){ mode=m;
  document.getElementById('m-geo').classList.toggle('active', m==='geo');
  document.getElementById('m-spec').classList.toggle('active', m==='spectral');
  layout(); }
function setYear(y){
  year = y;
  document.querySelectorAll('#years button').forEach(b =>
    b.classList.toggle('active', b.dataset.year === y));
  buildGraph();                 // rebuilds the network for the chosen year
  apply(); clearHighlight();
  tool==='scenario' ? recompute() : tool==='agent' ? showAgentPanel() : resetPanel();
}
function buildYearControls(){
  const box = document.getElementById('years');
  if (AVAILABLE.length < 2){ box.style.display = 'none'; return; }
  box.innerHTML = AVAILABLE.map(y =>
    `<button data-year="${y}"${y===year?' class="active"':''}>${y}</button>`).join('');
  box.querySelectorAll('button').forEach(b =>
    b.addEventListener('click', () => setYear(b.dataset.year)));
}
function setTool(){
  document.getElementById('t-inspect').classList.toggle('active', tool==='inspect');
  document.getElementById('t-scenario').classList.toggle('active', tool==='scenario');
  document.getElementById('t-agent').classList.toggle('active', tool==='agent');
  document.querySelector('.stage').classList.toggle('whatif', tool==='scenario');
  clearHighlight();
  if (tool==='scenario'){ recompute(); }
  else if (tool==='agent'){
    linking=false; pendingAdd=null; restoreNodeColors();
    DATA.nodes.forEach(n => nodeEls[n.id].g.classList.remove('islanded'));
    showAgentPanel();
  }
  else {
    linking=false; pendingAdd=null; restoreNodeColors();
    DATA.nodes.forEach(n => nodeEls[n.id].g.classList.remove('islanded'));
    resetPanel();
  }
}
document.getElementById('m-geo').addEventListener('click', () => setMode('geo'));
document.getElementById('m-spec').addEventListener('click', () => setMode('spectral'));
document.getElementById('t-inspect').addEventListener('click', () => { tool='inspect'; setTool(); });
document.getElementById('t-scenario').addEventListener('click', () => { tool='scenario'; setTool(); });
document.getElementById('t-agent').addEventListener('click', () => { tool='agent'; setTool(); });
document.getElementById('reset').addEventListener('click', () => {
  scale=1; tx=0; ty=0; offEdges.clear(); history.length=0; linking=false; pendingAdd=null;
  while (nAdded>0) removeLastAdded(DATA.edges.length-1);
  restoreNodeColors();
  DATA.nodes.forEach(n => nodeEls[n.id].g.classList.remove('islanded'));
  apply(); clearHighlight();
  tool==='scenario' ? recompute() : tool==='agent' ? showAgentPanel() : resetPanel();
});
const themeBtn = document.getElementById('theme');
function applyTheme(dark){
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  themeBtn.textContent = dark ? '☀ Light' : '🌙 Dark';
  try { localStorage.setItem('gridmap-theme', dark ? 'dark' : 'light'); } catch(e){}
}
themeBtn.addEventListener('click', () =>
  applyTheme(document.documentElement.dataset.theme !== 'dark'));
let savedTheme = null;
try { savedTheme = localStorage.getItem('gridmap-theme'); } catch(e){}
applyTheme(savedTheme ? savedTheme === 'dark'
  : window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
const search = document.getElementById('search');
search.addEventListener('keydown', ev => {
  if(ev.key!=='Enter') return;
  const q = search.value.trim().toUpperCase();
  const n = nodeById[q] || DATA.nodes.find(x => x.id.toUpperCase().includes(q));
  if(n){ tool='inspect'; setTool(); onNode(n);
    scale=2.5; tx=W/2-px(n.id)*scale; ty=H/2-py(n.id)*scale; apply(); }
});
if (YEARS[year].stats.geo_coverage === 0){
  mode = 'spectral'; document.getElementById('m-geo').disabled = true;
}
document.getElementById('m-geo').classList.toggle('active', mode==='geo');
document.getElementById('m-spec').classList.toggle('active', mode==='spectral');
document.getElementById('t-inspect').classList.add('active');
const legend = document.getElementById('legend');
if (window.innerWidth <= 760) legend.classList.add('collapsed');  // default closed on phones
document.getElementById('legend-toggle').addEventListener('click',
  () => legend.classList.toggle('collapsed'));
buildYearControls();
buildGraph(); resetPanel();
"""

_TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style></head>
<body>
<header>
  <h1>{title}</h1>
  <p>Hubs are grid-operator areas; lines are tie-lines between them.
  {n_bas} areas · {n_ties} ties · {gross_twh} TWh/yr gross interchange ·
  {n_bottlenecks} bottleneck ties · coupling {coupling} (Fiedler {fiedler}).
  {geo_note}.{daily_note}</p>
</header>
<div class="layout">
  <div class="stage">
    <svg id="map"><g id="viewport"></g></svg>
    <div class="controls">
      <div class="group" id="years"></div>
      <div class="group">
        <button id="m-geo">Geographic</button>
        <button id="m-spec">Spectral</button>
      </div>
      <div class="group">
        <button id="t-inspect">Inspect</button>
        <button id="t-scenario">What-if</button>
        <button id="t-agent">AI</button>
      </div>
      <button id="reset">Reset</button>
      <a href="grid_map_manual.html" target="_blank" rel="noopener">Manual</a>
      <button id="theme" title="Toggle light / dark">🌙 Dark</button>
      <input id="search" placeholder="Find a BA (e.g. PJM)…">
    </div>
    <div class="legend" id="legend">
      <button class="legend-toggle" id="legend-toggle"><b>How to read this</b></button>
      <div class="legend-body">
      <span style="background:#1f6feb"></span>seam side A&nbsp;
      <span style="background:#b7791f"></span>seam side B&nbsp;
      <span style="background:#d64545"></span>bottleneck tie&nbsp;
      <span style="background:#1f8f5f"></span>added line<br>
      Circle size = total tie usage. Line thickness = flow on that tie.
      In What-if, each disconnected piece gets its own colour.
      Geographic = real territory centroids (representative points, not line routes).
      </div>
    </div>
  </div>
  <aside class="panel" id="panel"></aside>
</div>
<footer>Generated {generated}. Flows from EIA-930 INTERCHANGE (measured);
geographic placement from eGRID state footprints (approximate). Curvature and
the spectral seam are analytic screening lenses, not geographic claims.</footer>
<script type="application/json" id="map-data">{data}</script>
<script>{js}</script>
</body></html>
"""
