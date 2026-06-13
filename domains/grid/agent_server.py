# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Local grid-map agent API.

Run this instead of a plain static server when you want the map's AI panel to
talk to KOMPOSOS in the background:

    python -m domains.grid.agent_server --port 8000

The server has no external dependencies. It serves docs/network_map.html and
handles POST /api/grid/chat by routing questions to grounded grid tools.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sys
from collections.abc import Mapping as ABCMapping
from dataclasses import dataclass
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence
from urllib.parse import unquote, urlparse

from domains.grid import agent_tools
from domains.grid.agent_contract import agent_manifest

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
BA_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,5}\b")
PAIR_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,5})\s*[-/]\s*([A-Z][A-Z0-9]{1,5})\b")

WHATIF_TERMS = (
    "what if", "what-if", "cut", "remove", "fail", "fails", "failure",
    "break", "breaks", "offline", "outage", "take out", "goes down",
)
BOTTLE_TERMS = (
    "bottleneck", "weak spot", "weak spots", "stuck", "pinch", "pinch point",
    "congestion", "trapped", "worst", "top tie", "fragile", "risk",
)
SEAM_TERMS = ("seam", "fiedler", "weakest split", "split", "partition", "divide")
SIMILAR_TERMS = (
    "similar", "like ", "act like", "acts like", "same shape", "same role",
    "resembles", "compare", "analog", "structural",
)
GAP_TERMS = (
    "gap", "missing link", "relieve", "relief", "candidate", "fix",
    "recommend", "build", "invest", "what should", "look at next",
)
PATH_TERMS = (
    "path", "route", "connect", "connected", "connection", "get from",
    "between", "how does power", "how is",
)
EXPLAIN_TERMS = ("explain", "why", "important", "matter", "evidence", "support",
                 "mean", "define", "definition", "what is", "what are",
                 "glossary", "methodology", "how do you know")


@dataclass
class AgentCard:
    title: str
    body: str
    kind: str = "tool"
    rows: List[Dict[str, object]] | None = None
    actions: List[Dict[str, object]] | None = None

    def as_dict(self) -> Dict[str, object]:
        out: Dict[str, object] = {
            "title": self.title,
            "body": self.body,
            "kind": self.kind,
        }
        if self.rows:
            out["rows"] = self.rows
        if self.actions:
            out["actions"] = self.actions
        return out


def _available_bas(year: str | None) -> set[str]:
    try:
        return set(agent_tools._neighbor_sets(year))  # local tool surface
    except Exception:
        return set()


def _codes(text: str, year: str | None) -> List[str]:
    known = _available_bas(year)
    out: List[str] = []
    for code in BA_RE.findall(text.upper()):
        if code in known and code not in out:
            out.append(code)
    return out


def _pairs(text: str, year: str | None) -> List[str]:
    known = _available_bas(year)
    pairs: List[str] = []
    for a, b in PAIR_RE.findall(text.upper()):
        if a in known and b in known:
            pair = f"{a}-{b}"
            if pair not in pairs:
                pairs.append(pair)
    return pairs


def _has_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _context_codes(context: Mapping | None) -> List[str]:
    if not context:
        return []
    if context.get("kind") == "ba" and context.get("id"):
        return [str(context["id"]).upper()]
    if context.get("kind") == "tie":
        return [
            str(context.get("a", "")).upper(),
            str(context.get("b", "")).upper(),
        ]
    return []


def _context_pair(context: Mapping | None) -> str | None:
    if context and context.get("kind") == "tie":
        a, b = context.get("a"), context.get("b")
        if a and b:
            return f"{str(a).upper()}-{str(b).upper()}"
    return None


def _call_tool(name: str, *args, year: str | None = None, **kwargs) -> Dict:
    tool = getattr(agent_tools, f"tool_{name}")
    return tool(*args, year=year, **kwargs)


def _tool_card(result: Mapping) -> AgentCard:
    title = {
        "whatif": "What-if",
    }.get(str(result.get("tool")), str(result.get("tool", "tool")).replace("_", " ").title())
    if result.get("ba"):
        title += f" {result['ba']}"
    elif result.get("tie"):
        title += f" {result['tie']}"
    elif result.get("from") and result.get("to"):
        title += f" {result['from']} -> {result['to']}"
    return AgentCard(
        title=title,
        body=str(result.get("summary") or result.get("error") or ""),
        rows=_rows_for(result),
        actions=_actions_for(result),
    )


def _actions_for(result: Mapping) -> List[Dict[str, object]]:
    highlight = _highlight_for([result])
    actions: List[Dict[str, object]] = []
    if highlight["nodes"] or highlight["edges"]:
        actions.append({
            "type": "highlight",
            "label": "Highlight on map",
            "nodes": highlight["nodes"],
            "edges": highlight["edges"],
        })
    if result.get("tool") == "whatif":
        cuts = [str(pair) for pair in result.get("cut", []) if "-" in str(pair)]
        if cuts:
            actions.append({
                "type": "apply_cut",
                "label": "Apply cut to map",
                "cut": cuts,
            })
    return actions


def _rows_for(result: Mapping) -> List[Dict[str, object]]:
    data = result.get("result") or {}
    if not isinstance(data, ABCMapping):
        return []
    if result.get("tool") == "path":
        return [
            {
                "label": "Route",
                "value": " -> ".join(route.get("hops", [])),
                "meta": (
                    f"weakest {route.get('weakest_tie')} "
                    f"{route.get('weakest_tie_twh')} TWh/yr"
                    if route.get("weakest_tie") else ""
                ),
            }
            for route in data.get("routes", [])[:4]
        ]
    if result.get("tool") == "similar":
        return [
            {
                "label": item.get("ba"),
                "value": item.get("similarity"),
                "meta": "shared: " + ", ".join(item.get("shared_neighbours", [])),
            }
            for item in data.get("similar", [])[:6]
        ]
    if result.get("tool") == "bottlenecks":
        return [
            {
                "label": row.get("tie"),
                "value": f"{row.get('gross_twh')} TWh",
                "meta": f"curvature {row.get('curvature')}",
            }
            for row in data.get("bottlenecks", [])[:8]
        ]
    if result.get("tool") == "whatif":
        after = data.get("after") or {}
        base = data.get("baseline") or {}
        return [
            {"label": "Ties cut", "value": data.get("ties_cut")},
            {
                "label": "Fiedler",
                "value": f"{base.get('algebraic_connectivity'):.4f}"
                if isinstance(base.get("algebraic_connectivity"), float)
                else base.get("algebraic_connectivity"),
                "meta": (
                    f"after {after.get('algebraic_connectivity'):.4f}"
                    if isinstance(after.get("algebraic_connectivity"), float)
                    else ""
                ),
            },
        ]
    if result.get("tool") == "explain":
        return [
            {
                "label": f"{p.get('source')} § {p.get('section')}",
                "value": p.get("excerpt"),
                "meta": f"score {p.get('score')}",
            }
            for p in data.get("passages", [])[:3]
        ]
    return []


def _highlight_for(results: Sequence[Mapping]) -> Dict[str, List[str]]:
    nodes: set[str] = set()
    edges: set[str] = set()
    for result in results:
        tool = result.get("tool")
        data = result.get("result") or {}
        if tool == "ba" and result.get("ba"):
            nodes.add(str(result["ba"]))
        elif tool == "tie" and result.get("tie"):
            pair = str(result["tie"])
            edges.add(pair)
            nodes.update(pair.split("-"))
        elif tool == "path":
            routes = data.get("routes", []) if isinstance(data, ABCMapping) else []
            if routes:
                hops = routes[0].get("hops", [])
                nodes.update(hops)
                edges.update(f"{a}-{b}" for a, b in zip(hops, hops[1:]))
        elif tool == "bottlenecks":
            rows = data.get("bottlenecks", []) if isinstance(data, ABCMapping) else []
            for row in rows[:5]:
                pair = str(row.get("tie", ""))
                if "-" in pair:
                    edges.add(pair)
                    nodes.update(pair.split("-"))
        elif tool == "similar" and result.get("ba"):
            nodes.add(str(result["ba"]))
            rows = data.get("similar", []) if isinstance(data, ABCMapping) else []
            nodes.update(str(row.get("ba")) for row in rows[:5] if row.get("ba"))
        elif tool == "whatif":
            for pair in result.get("cut", []):
                pair_text = str(pair)
                if "-" in pair_text:
                    edges.add(pair_text)
                    nodes.update(pair_text.split("-"))
    return {"nodes": sorted(nodes), "edges": sorted(edges)}


def _answer_from(results: Sequence[Mapping]) -> str:
    summaries = [str(r.get("summary")) for r in results if r.get("summary")]
    if not summaries:
        return "I could not ground that with the available grid tools."
    if len(summaries) == 1:
        return summaries[0]
    return " I also checked: ".join(summaries)


def _suggestions(
    context: Mapping | None,
    codes: Sequence[str],
    pairs: Sequence[str] | None = None,
) -> List[str]:
    pair = _context_pair(context) or (pairs[0] if pairs else None)
    if pair:
        return [
            f"Why is {pair} important?",
            f"What breaks if {pair} fails?",
            f"What evidence supports {pair}?",
        ]
    code = codes[0] if codes else (_context_codes(context) or [None])[0]
    if code:
        path_target = "PJM" if code != "PJM" else "MISO"
        return [
            f"Explain {code} in plain English",
            f"What areas act like {code}?",
            f"Find paths from {code} to {path_target}",
        ]
    return [
        "Where is power getting stuck?",
        "What should I look at next?",
        "Explain the weakest seam",
    ]


def answer_question(
    message: str,
    year: str | None = None,
    context: Mapping | None = None,
) -> Dict[str, object]:
    """Route one chat message to grounded tools and return UI-friendly JSON."""
    text = (message or "").strip()
    lower = text.lower()
    codes = _codes(text, year)
    for code in _context_codes(context):
        if code and code not in codes:
            codes.append(code)
    pairs = _pairs(text, year)
    ctx_pair = _context_pair(context)
    if ctx_pair and ctx_pair not in pairs:
        pairs.append(ctx_pair)

    results: List[Dict] = []
    try:
        if not text or any(w in lower for w in ("help", "what can you", "commands")):
            manifest = agent_manifest()
            return {
                "ok": True,
                "answer": (
                    "I can call grounded grid tools for BA facts, tie facts, "
                    "paths, structural similarity, bottlenecks, seams, full "
                    "geometry what-if cuts, and OPTIMUS gap screens."
                ),
                "cards": [
                    AgentCard(
                        "Available grounded tools",
                        ", ".join(t["name"] for t in manifest["tools"]),
                        kind="manifest",
                    ).as_dict()
                ],
                "provenance": ["local manifest; no online API key required"],
                "suggestions": _suggestions(context, codes, pairs),
                "highlight": {"nodes": [], "edges": []},
                "tools": [],
            }

        wants_whatif = _has_any(lower, WHATIF_TERMS)
        wants_bottlenecks = _has_any(lower, BOTTLE_TERMS)
        wants_seam = _has_any(lower, SEAM_TERMS)
        wants_similar = _has_any(lower, SIMILAR_TERMS)
        wants_gaps = _has_any(lower, GAP_TERMS)
        wants_path = _has_any(lower, PATH_TERMS)
        wants_explain = _has_any(lower, EXPLAIN_TERMS)

        if wants_whatif:
            cut = pairs[:]
            if not cut and len(codes) >= 2:
                cut = [f"{codes[0]}-{codes[1]}"]
            if cut:
                results.append(_call_tool("whatif", cut, year=year))
            elif codes:
                results.append(_call_tool("ba", codes[0], year=year))
        elif pairs and (wants_explain or not (wants_path or wants_similar or wants_bottlenecks)):
            a, b = pairs[0].split("-")
            results.append(_call_tool("tie", a, b, year=year))
        elif wants_bottlenecks:
            results.append(_call_tool("bottlenecks", top=8, year=year))
        elif wants_seam:
            results.append(_call_tool("seam", year=year))
        elif wants_similar:
            if codes:
                results.append(_call_tool("similar", codes[0], top=6, year=year))
            else:
                results.append(_call_tool("bottlenecks", top=5, year=year))
        elif wants_gaps:
            if not codes and not pairs:
                results.append(_call_tool("bottlenecks", top=5, year=year))
            results.append(_call_tool("gaps", top=5, year=year))
        elif wants_path:
            if len(codes) >= 2:
                results.append(_call_tool("path", codes[0], codes[1], k=3, year=year))
            elif pairs:
                a, b = pairs[0].split("-")
                results.append(_call_tool("path", a, b, k=3, year=year))
        elif pairs:
            a, b = pairs[0].split("-")
            results.append(_call_tool("tie", a, b, year=year))
        elif codes:
            results.append(_call_tool("ba", codes[0], year=year))

        # RAG: "why / how do you know / what does this mean" -> cited docs.
        if wants_explain:
            explain = _call_tool("explain", text, year=year)
            if explain.get("result", {}).get("passages") or not results:
                results.append(explain)

        if not results:
            return {
                "ok": True,
                "answer": (
                    "I need a BA code, tie, or analysis type to ground that. "
                    "Try 'explain PJM', 'path CISO PJM', 'similar to PJM', "
                    "'top bottlenecks', or 'what if cut PJM-NYIS'."
                ),
                "cards": [],
                "provenance": ["no tool selected"],
                "suggestions": _suggestions(context, codes, pairs),
                "highlight": {"nodes": [], "edges": []},
                "tools": [],
            }

        return {
            "ok": not any("error" in r for r in results),
            "answer": _answer_from(results),
            "cards": [_tool_card(r).as_dict() for r in results],
            "provenance": [str(r.get("provenance", "")) for r in results if r.get("provenance")],
            "suggestions": _suggestions(context, codes, pairs),
            "highlight": _highlight_for(results),
            "tools": results,
        }
    except Exception as exc:
        return {
            "ok": False,
            "answer": "The local agent API hit an error before it could answer.",
            "error": str(exc),
            "cards": [],
            "provenance": ["local API exception"],
            "suggestions": _suggestions(context, codes, pairs),
            "highlight": {"nodes": [], "edges": []},
            "tools": [],
        }


class GridAgentHandler(SimpleHTTPRequestHandler):
    server_version = "KOMPOSOSGridAgent/0.1"

    def translate_path(self, path: str) -> str:
        parsed = urlparse(path)
        clean = unquote(parsed.path)
        if clean in ("", "/"):
            clean = "/network_map.html"
        rel = clean.lstrip("/")
        target = (DOCS / rel).resolve()
        docs = DOCS.resolve()
        if not str(target).startswith(str(docs)):
            return str(docs / "network_map.html")
        return str(target)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _json(self, status: int, payload: Mapping):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/api/grid/health"):
            self._json(200, {"ok": True, "service": "grid-agent", "manifest": agent_manifest()})
            return
        return super().do_GET()

    def do_POST(self):
        if not self.path.startswith("/api/grid/chat"):
            self._json(404, {"ok": False, "error": "unknown endpoint"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            req = json.loads(body or "{}")
        except Exception as exc:
            self._json(400, {"ok": False, "error": f"bad JSON: {exc}"})
            return
        payload = answer_question(
            str(req.get("message", "")),
            year=req.get("year"),
            context=req.get("context") if isinstance(req.get("context"), ABCMapping) else None,
        )
        self._json(200 if payload.get("ok", True) else 500, payload)

    def log_message(self, fmt: str, *args):
        sys.stderr.write("[grid-agent] " + fmt % args + "\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Serve grid map + local agent API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    mimetypes.add_type("text/html; charset=utf-8", ".html")
    server = ThreadingHTTPServer((args.host, args.port), GridAgentHandler)
    url = f"http://{args.host}:{args.port}/network_map.html"
    print(f"serving grid map + local agent API at {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping grid agent server")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
