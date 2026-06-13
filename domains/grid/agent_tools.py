# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Grounded tool surface for a *local* coding agent (no online API/key).

Whoever clones the repo points their own coding agent (Claude Code,
etc.) at this CLI; the agent answers grid questions by calling these
tools and relaying what they return. Every command emits structured
JSON with a plain-English `summary` and a `provenance` note, so the
agent never has to invent a number — it reports computed results.

These expose the relational / categorical capabilities the static map
UI cannot: multi-hop power paths, shared-neighbor structural similarity,
Ricci/spectral structure, structural-gap (relief) candidates, and a
*full-geometry* what-if recompute (deeper than the UI's connectivity
view). See domains/grid/AGENTS.md for the agent playbook and contract.

    python -m domains.grid.agent_tools manifest
    python -m domains.grid.agent_tools prompt
    python -m domains.grid.agent_tools ba PJM
    python -m domains.grid.agent_tools tie PJM NYIS
    python -m domains.grid.agent_tools path CISO PJM --k 3
    python -m domains.grid.agent_tools similar PJM --top 5
    python -m domains.grid.agent_tools bottlenecks --top 10
    python -m domains.grid.agent_tools seam
    python -m domains.grid.agent_tools whatif --cut PJM-NYIS,MISO-SWPP
    python -m domains.grid.agent_tools gaps --top 5
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

from domains.grid.agent_contract import agent_manifest, agent_prompt

DATA_DIR = "domains/grid/data"
REPORTS_DIR = "reports"
EGRID = "domains/grid/data/egrid2023_data_rev2.xlsx"


# --- data loading (auto-discovers the latest complete INTERCHANGE year) ---

def _interchange(year: str | None):
    from domains.grid.run_daily_update import (
        all_interchange_years,
        latest_interchange_csvs,
    )

    if year:
        years = all_interchange_years(DATA_DIR)
        if year not in years:
            raise SystemExit(f"year {year} not available; have {sorted(years)}")
        return year, years[year]
    csvs = latest_interchange_csvs(DATA_DIR)
    if not csvs:
        raise SystemExit("no complete INTERCHANGE year found in " + DATA_DIR)
    import re
    y = re.search(r"_(\d{4})_", csvs[0].name)
    return (y.group(1) if y else "latest"), csvs


def _ties(year: str | None):
    from domains.grid.flow_geometry import load_interchange
    _, csvs = _interchange(year)
    return load_interchange(csvs)


def _flow_category(year: str | None):
    from domains.grid.flow_geometry import build_flow_category
    return build_flow_category(_ties(year))


def _undirected_flow_category(year: str | None):
    """Both-direction interchange graph for connectivity/similarity questions
    (the net-flow-directed graph dead-ends across the East/West seam)."""
    from core.category import Category
    ties = _ties(year)
    cat = Category(name="ba_flow_ud", db_path=":memory:")
    mx = max((t.gross_mwh for t in ties), default=1.0)
    for t in ties:
        w = max(t.gross_mwh / mx, 1e-3)
        cat.connect(f"ba:{t.ba_a}", f"ba:{t.ba_b}", name="ix", confidence=w)
        cat.connect(f"ba:{t.ba_b}", f"ba:{t.ba_a}", name="ix", confidence=w)
    return cat


def _neighbor_sets(year: str | None) -> Dict[str, set]:
    nb: Dict[str, set] = {}
    for t in _ties(year):
        nb.setdefault(t.ba_a, set()).add(t.ba_b)
        nb.setdefault(t.ba_b, set()).add(t.ba_a)
    return nb


def _route_strengths(year: str | None) -> Dict[frozenset, Dict[str, float]]:
    ties = _ties(year)
    mx = max((t.gross_mwh for t in ties), default=1.0)
    return {
        frozenset((t.ba_a, t.ba_b)): {
            "gross_twh": t.gross_mwh / 1e6,
            "normalized": t.gross_mwh / mx if mx else 0.0,
        }
        for t in ties
    }


def _sig_float(value: float) -> float:
    return float(f"{value:.6g}") if value else 0.0


def _network(year: str | None):
    from domains.grid.network_map import build_network
    label, csvs = _interchange(year)
    balance = [str(p).replace("INTERCHANGE", "BALANCE") for p in csvs]
    from domains.grid.flow_geometry import load_interchange
    egrid = EGRID if Path(EGRID).exists() else None
    net = build_network(load_interchange(csvs), egrid_workbook=egrid,
                        reports_dir=REPORTS_DIR, balance_csvs=balance)
    return label, net


def _strip(name: str) -> str:
    return name.replace("ba:", "")


# ------------------------------- tools -------------------------------

def tool_ba(code: str, year: str | None = None) -> Dict:
    label, net = _network(year)
    node = next((n for n in net.nodes if n.name == code), None)
    if node is None:
        return {"error": f"BA '{code}' not found",
                "available": [n.name for n in net.nodes]}
    facts = net.node_facts.get(code, {})
    return {
        "tool": "ba", "year": label, "ba": code,
        "summary": f"{code}: {facts.get('demand_twh', 0):.0f} TWh demand, "
                   f"{node.degree} ties, "
                   f"{facts.get('reliability_value_usd', 0)/1e9:.0f}B reliability value.",
        "provenance": "flows EIA-930 (measured); placement eGRID; "
                      "curvature/seam are screening lenses; daily pulse is fresh.",
        "result": {"degree": node.degree, "total_tie_twh": node.gross_mwh / 1e6,
                    "seam_side": node.side, "facts": facts},
    }


def tool_tie(a: str, b: str, year: str | None = None) -> Dict:
    label, net = _network(year)
    key = tuple(sorted((a, b)))
    edge = next((e for e in net.edges
                 if tuple(sorted((e.a, e.b))) == key), None)
    if edge is None:
        return {"error": f"no tie between {a} and {b} in {label}"}
    return {
        "tool": "tie", "year": label, "tie": f"{edge.a}-{edge.b}",
        "summary": f"{edge.a}-{edge.b}: {edge.gross_mwh/1e6:.1f} TWh gross, "
                   f"net {edge.source}->{edge.target}, "
                   f"curvature {edge.curvature:+.3f}"
                   f"{' (bottleneck)' if edge.bottleneck else ''}.",
        "provenance": "flows measured (EIA-930); curvature is a screening "
                      "lens; corridor study facts tagged by evidence level.",
        "result": {"gross_twh": edge.gross_mwh / 1e6, "net_twh": edge.net_mwh / 1e6,
                    "net_direction": f"{edge.source}->{edge.target}",
                    "curvature": edge.curvature, "bottleneck": edge.bottleneck,
                    "facts": net.edge_facts.get(key, {})},
    }


def tool_path(a: str, b: str, k: int = 3, year: str | None = None) -> Dict:
    cat = _undirected_flow_category(year)  # physical connectivity (undirected)
    src, tgt = f"ba:{a}", f"ba:{b}"
    if cat.get(src) is None or cat.get(tgt) is None:
        return {"error": f"unknown BA(s): {a if cat.get(src) is None else ''} "
                         f"{b if cat.get(tgt) is None else ''}".strip()}
    paths = cat.top_k_paths(src, tgt, k=k, maximize=True)
    strengths = _route_strengths(year)
    routes = []
    for nodes, w in paths:
        hops = [_strip(n) for n in nodes]
        edge_strengths = []
        for left, right in zip(hops, hops[1:]):
            rec = strengths.get(frozenset((left, right)))
            if rec:
                edge_strengths.append((left, right, rec))
        weakest = min(edge_strengths, key=lambda item: item[2]["gross_twh"], default=None)
        route = {"hops": hops, "flow_weight": _sig_float(w)}
        if weakest:
            route.update({
                "weakest_tie": f"{weakest[0]}-{weakest[1]}",
                "weakest_tie_twh": round(weakest[2]["gross_twh"], 2),
                "min_normalized_tie_strength": round(weakest[2]["normalized"], 4),
            })
        routes.append(route)
    strength_note = (
        f" (weakest tie {routes[0]['weakest_tie']}, "
        f"{routes[0]['weakest_tie_twh']:.2f} TWh/yr)"
        if routes and "weakest_tie" in routes[0] else ""
    )
    return {
        "tool": "path", "from": a, "to": b,
        "summary": (f"{len(routes)} route(s) {a}->{b}; strongest: "
                    + " -> ".join(routes[0]["hops"]) + strength_note) if routes
                   else f"{a} and {b} are not connected on the interchange graph "
                        f"(likely different interconnections).",
        "provenance": "routes over the EIA-930 interchange graph (measured "
                      "ties), undirected = physical connectivity; weight = "
                      "categorical product of normalized gross flow; weakest_tie "
                      "is the route's lowest measured gross interchange. This is "
                      "a coupling proxy, not a power-flow solution. Net-flow "
                      "direction is reported by the 'tie' tool.",
        "result": {"routes": routes},
    }


def tool_similar(code: str, top: int = 5, year: str | None = None) -> Dict:
    """Shared-neighbour (Jaccard) similarity: which BAs interconnect with the
    same set of neighbours. (The categorical Yoneda metric degenerates to 0 on
    this sparse graph, so we report the transparent structural overlap instead.)
    """
    nb = _neighbor_sets(year)
    if code not in nb:
        return {"error": f"BA '{code}' not found", "available": sorted(nb)}
    base = nb[code]
    scored = []
    for other, ns in nb.items():
        if other == code:
            continue
        union = base | ns
        j = len(base & ns) / len(union) if union else 0.0
        scored.append((other, round(j, 3), sorted(base & ns)))
    scored.sort(key=lambda kv: kv[1], reverse=True)
    scored = scored[:top]
    return {
        "tool": "similar", "ba": code,
        "summary": f"BAs that interconnect like {code} (shared-neighbour "
                   f"overlap): " + ", ".join(f"{n} ({s:.2f})" for n, s, _ in scored),
        "provenance": "shared-neighbour Jaccard on the measured interchange "
                      "graph: |common neighbours| / |union|. A structural screen "
                      "(who connects to the same BAs), not an operational claim.",
        "result": {"similar": [{"ba": n, "similarity": s, "shared_neighbours": sh}
                               for n, s, sh in scored]},
    }


def tool_bottlenecks(top: int = 10, year: str | None = None) -> Dict:
    from domains.grid.flow_report import build_flow_bottleneck_report
    report = build_flow_bottleneck_report(_ties(year))
    rows = [{"tie": f"{b.ba_a}-{b.ba_b}", "curvature": round(b.curvature, 4),
             "gross_twh": round(b.gross_mwh / 1e6, 2),
             "net_direction": b.net_direction} for b in report.bottlenecks[:top]]
    return {
        "tool": "bottlenecks",
        "summary": f"{report.hyperbolic_edges} hyperbolic ties; top {len(rows)} "
                   f"carry {report.bottleneck_gross_share(len(rows)):.0%} of gross "
                   f"interchange. Worst: {rows[0]['tie'] if rows else 'none'}.",
        "provenance": "Ollivier-Ricci curvature on the measured interchange "
                      "graph; negative + high-flow = structural bottleneck "
                      "(a screening signal, not a congestion price).",
        "result": {"bottlenecks": rows},
    }


def tool_seam(year: str | None = None) -> Dict:
    from domains.grid.flow_geometry import analyze_flow_geometry
    geo = analyze_flow_geometry(_ties(year))
    small, large = geo.fiedler_partition
    return {
        "tool": "seam",
        "summary": f"Weakest spectral seam splits {len(small)} BAs from "
                   f"{len(large)}; coupling {geo.coupling} "
                   f"(Fiedler {geo.algebraic_connectivity:.4f}).",
        "provenance": "Fiedler vector of the interchange Laplacian (measured "
                      "graph); recovers the structurally weakest cut.",
        "result": {"smaller_side": sorted(small), "other_side_count": len(large),
                   "algebraic_connectivity": geo.algebraic_connectivity,
                   "coupling": geo.coupling},
    }


def tool_whatif(cut: List[str], year: str | None = None) -> Dict:
    """Full-geometry what-if: drop ties, recompute Ricci + spectral (deeper
    than the UI's connectivity-only view)."""
    from domains.grid.flow_geometry import analyze_flow_geometry
    ties = _ties(year)
    cut_keys = {frozenset(p.replace(" ", "").split("-")) for p in cut}
    kept = [t for t in ties if frozenset((t.ba_a, t.ba_b)) not in cut_keys]
    removed = len(ties) - len(kept)
    base = analyze_flow_geometry(ties)
    after = analyze_flow_geometry(kept) if kept else None
    res = {
        "ties_cut": removed,
        "baseline": {"coupling": base.coupling,
                     "algebraic_connectivity": base.algebraic_connectivity,
                     "n_bottlenecks": len(base.bottlenecks)},
    }
    if after is not None:
        res["after"] = {"coupling": after.coupling,
                        "algebraic_connectivity": after.algebraic_connectivity,
                        "n_bottlenecks": len(after.bottlenecks)}
        delta = after.algebraic_connectivity - base.algebraic_connectivity
        summary = (f"Cut {removed} tie(s): algebraic connectivity "
                   f"{base.algebraic_connectivity:.4f} -> "
                   f"{after.algebraic_connectivity:.4f} ({delta:+.4f}); "
                   f"coupling {base.coupling} -> {after.coupling}.")
    else:
        summary = f"Cut {removed} tie(s): no ties remain."
    return {
        "tool": "whatif", "cut": cut, "summary": summary,
        "provenance": "FULL geometry recompute (Ricci + spectral) on the "
                      "measured graph minus the cut ties — connectivity and "
                      "structure, still not an AC/DC power-flow solution.",
        "result": res,
    }


def tool_gaps(top: int = 5, year: str | None = None) -> Dict:
    from core.optimus import OptimusEngine
    engine = OptimusEngine(_flow_category(year))
    try:
        gaps = engine.find_structural_gaps()
    except Exception as exc:  # defensive: surface rather than fabricate
        return {"tool": "gaps", "error": f"structural-gap search failed: {exc}"}
    items = []
    for g in list(gaps)[:top]:
        items.append(json.loads(json.dumps(g, default=str)))
    return {
        "tool": "gaps",
        "summary": f"{len(items)} structural-gap (relief-candidate) suggestion(s) "
                   f"from OPTIMUS factorization.",
        "provenance": "OPTIMUS categorical gradient: intermediate objects whose "
                      "addition would shorten/strengthen composition — a "
                      "screening hypothesis for where new links could help.",
        "result": {"gaps": items},
    }


# --- explain: lexical RAG over this repo's own committed docs ---------------
# Honest scope: this is *lexical* (TF-IDF) retrieval, not semantic/embedding
# RAG. It grounds the "why / how do you know / what does this mean" questions
# the computed tools can't, by returning verbatim passages + citations from
# the repo's own methodology docs. (The data/ embeddings engine could swap in
# for semantic retrieval later; lexical keeps it dependency-free and offline.)
import math
import re as _re

_DOC_GLOBS = ("reports/*.md", "domains/grid/*.md")
_DOC_EXTRA = ("REPRODUCE.md", "README.md")
_STOP = {"the", "and", "for", "are", "but", "not", "you", "with", "that", "this",
         "from", "have", "has", "was", "what", "why", "how", "does", "explain",
         "where", "which", "into", "over", "per", "its", "their", "our"}


def _doc_sections():
    """Committed docs split into (source, heading, text) sections by heading."""
    paths: List[Path] = []
    for pattern in _DOC_GLOBS:
        paths.extend(sorted(Path().glob(pattern)))
    paths.extend(Path(p) for p in _DOC_EXTRA if Path(p).exists())
    sections = []
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        heading, buf = "(intro)", []
        for line in lines:
            if _re.match(r"^#{1,6}\s", line):
                if buf:
                    sections.append((str(path).replace("\\", "/"), heading,
                                     "\n".join(buf).strip()))
                heading, buf = _re.sub(r"^#{1,6}\s*", "", line).strip(), []
            else:
                buf.append(line)
        if buf:
            sections.append((str(path).replace("\\", "/"), heading,
                             "\n".join(buf).strip()))
    return [s for s in sections if s[2]]


def _terms(text: str) -> List[str]:
    return [t for t in _re.findall(r"[a-z0-9]+", text.lower())
            if len(t) >= 3 and t not in _STOP]


def tool_explain(query: str, top: int = 3, year: str | None = None) -> Dict:
    q_terms = set(_terms(query))
    if not q_terms:
        return {"tool": "explain", "error": "give a concept to explain, "
                "e.g. 'explain curtailment' or 'why cap relief at observed congestion'"}
    sections = _doc_sections()
    if not sections:
        return {"tool": "explain", "error": "no committed docs found to retrieve from"}
    # TF-IDF: rare query terms weigh more; score each section.
    n = len(sections)
    df = {t: 0 for t in q_terms}
    toks = []
    for _, _, text in sections:
        tt = _terms(text)
        toks.append(tt)
        present = set(tt)
        for t in q_terms:
            if t in present:
                df[t] += 1
    idf = {t: math.log(n / (1 + df[t])) + 1.0 for t in q_terms}
    scored = []
    for (src, heading, text), tt in zip(sections, toks):
        counts = {t: tt.count(t) for t in q_terms}
        score = sum(counts[t] * idf[t] for t in q_terms)
        if score <= 0:
            continue
        # excerpt: window around the first hit of the highest-idf matched term
        hit_term = max((t for t in q_terms if counts[t]),
                       key=lambda t: idf[t], default=None)
        low = text.lower()
        i = low.find(hit_term) if hit_term else 0
        start = max(0, i - 120)
        excerpt = text[start:start + 320].strip().replace("\n", " ")
        if start > 0:
            excerpt = "…" + excerpt
        scored.append({"source": src, "section": heading,
                       "score": round(score, 2), "excerpt": excerpt})
    scored.sort(key=lambda d: d["score"], reverse=True)
    scored = scored[:top]
    if not scored:
        return {"tool": "explain", "query": query,
                "summary": f"No committed doc passage matches '{query}'.",
                "provenance": "lexical retrieval over repo docs; nothing matched.",
                "result": {"passages": []}}
    top_cite = f"{scored[0]['source']} § {scored[0]['section']}"
    return {
        "tool": "explain", "query": query,
        "summary": f"{len(scored)} passage(s); best: {top_cite}.",
        "provenance": "lexical (TF-IDF) retrieval over this repo's committed "
                      "docs; excerpts are quoted verbatim with file + section "
                      "citations. Synthesis is the agent's; the words are the "
                      "doc's. Not semantic search — phrase queries by keyword.",
        "result": {"passages": scored},
    }


def tool_manifest() -> Dict:
    return agent_manifest()


_TOOLS = {
    "ba": lambda a: tool_ba(a.code, a.year),
    "tie": lambda a: tool_tie(a.a, a.b, a.year),
    "path": lambda a: tool_path(a.a, a.b, a.k, a.year),
    "similar": lambda a: tool_similar(a.code, a.top, a.year),
    "bottlenecks": lambda a: tool_bottlenecks(a.top, a.year),
    "seam": lambda a: tool_seam(a.year),
    "whatif": lambda a: tool_whatif(
        [c for c in (a.cut or "").split(",") if c], a.year),
    "gaps": lambda a: tool_gaps(a.top, a.year),
    "explain": lambda a: tool_explain(" ".join(a.query), a.top, a.year),
    "manifest": lambda a: tool_manifest(),
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Grounded grid tools for a local coding agent (JSON out)")
    parser.add_argument("--year", help="INTERCHANGE year (default: latest)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("manifest")
    sub.add_parser("prompt")
    sub.add_parser("ba").add_argument("code")
    p = sub.add_parser("tie"); p.add_argument("a"); p.add_argument("b")
    p = sub.add_parser("path"); p.add_argument("a"); p.add_argument("b")
    p.add_argument("--k", type=int, default=3)
    p = sub.add_parser("similar"); p.add_argument("code")
    p.add_argument("--top", type=int, default=5)
    sub.add_parser("bottlenecks").add_argument("--top", type=int, default=10)
    sub.add_parser("seam")
    sub.add_parser("whatif").add_argument("--cut", required=True,
                                          help="comma-separated A-B pairs")
    sub.add_parser("gaps").add_argument("--top", type=int, default=5)
    p = sub.add_parser("explain"); p.add_argument("query", nargs="+")
    p.add_argument("--top", type=int, default=3)
    args = parser.parse_args(argv)

    if args.cmd == "prompt":
        print(agent_prompt())
        return 0

    result = _TOOLS[args.cmd](args)
    print(json.dumps(result, indent=2))
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
