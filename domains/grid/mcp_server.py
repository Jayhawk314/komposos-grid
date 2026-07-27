# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""MCP (Model Context Protocol) server over the grounded grid tool surface.

Thin stdio adapter around `domains.grid.agent_tools` so any MCP client
(Claude Code, Gemini CLI, etc.) can call the same grounded tools the in-app
chat uses. Every response carries the underlying tool's `summary` and
`provenance` fields — the agent relays computed results, it never invents
numbers. All tools are read-only; what-if simulations run on copies.

Run (stdio):
    python -m domains.grid.mcp_server

Requires the MCP Python SDK:
    pip install "mcp[cli]"

Claude Code project config (`.mcp.json` at the repo root):
    {"mcpServers": {"komposos-grid": {"command": "python",
                                      "args": ["-m", "domains.grid.mcp_server"]}}}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - depends on optional package
    raise SystemExit(
        "The MCP Python SDK is not installed. Install it with:\n"
        '    pip install "mcp[cli]"'
    ) from exc

from domains.grid import agent_tools

ROOT_DIR = Path(__file__).parent.parent.parent
REPORTS_DIR = ROOT_DIR / "reports"

mcp = FastMCP(
    "komposos-grid",
    instructions=(
        "Grounded analytics for the STITCH grid interconnection platform "
        "(EIA-930 tie flows, LBNL Queued Up cohorts, seam congestion evidence). "
        "Prefer these tools over recalling numbers: each response includes a "
        "plain-English `summary` and a `provenance` note describing method and "
        "limits. Relay provenance caveats when reporting results."
    ),
)


@mcp.tool()
def ba(code: str, year: str | None = None) -> Dict:
    """Profile one balancing authority: interchange totals, neighbors, role."""
    return agent_tools.tool_ba(code, year=year)


@mcp.tool()
def tie(a: str, b: str, year: str | None = None) -> Dict:
    """Facts about one tie (interface) between two balancing authorities."""
    return agent_tools.tool_tie(a, b, year=year)


@mcp.tool()
def path(a: str, b: str, k: int = 3, year: str | None = None) -> Dict:
    """Top-k multi-hop power transfer paths between two balancing authorities."""
    return agent_tools.tool_path(a, b, k=k, year=year)


@mcp.tool()
def similar(code: str, top: int = 5, year: str | None = None) -> Dict:
    """Structural twins of a BA via Yoneda-profile (relationship) similarity."""
    return agent_tools.tool_similar(code, top=top, year=year)


@mcp.tool()
def bottlenecks(top: int = 10, year: str | None = None) -> Dict:
    """Most negatively curved (bottleneck) ties by Ollivier-Ricci curvature."""
    return agent_tools.tool_bottlenecks(top=top, year=year)


@mcp.tool()
def seam(year: str | None = None) -> Dict:
    """Seam-level congestion and coupling overview across the interchange graph."""
    return agent_tools.tool_seam(year=year)


@mcp.tool()
def whatif(cut: List[str], year: str | None = None) -> Dict:
    """Full-geometry what-if: drop ties (e.g. ["PJM-NYIS"]) and recompute
    Ricci curvature + spectral connectivity. Read-only; runs on a copy."""
    return agent_tools.tool_whatif(cut, year=year)


@mcp.tool()
def gaps(top: int = 5, year: str | None = None) -> Dict:
    """Structural-gap (relief-candidate) suggestions from OPTIMUS factorization."""
    return agent_tools.tool_gaps(top=top, year=year)


@mcp.tool()
def explain(query: str, top: int = 3) -> Dict:
    """Retrieve verbatim methodology passages from the repo's committed docs
    (lexical TF-IDF, with citations) for 'why / how do you know' questions."""
    return agent_tools.tool_explain(query, top=top)


@mcp.tool()
def manifest() -> Dict:
    """List the grounded tool surface and its contract (self-description)."""
    return agent_tools.tool_manifest()


def _report_json(relative: str) -> str:
    path = REPORTS_DIR / relative
    if not path.exists():
        return json.dumps({
            "error": f"{relative} not found",
            "hint": "run the generator pipeline — see CLAUDE.md commands",
        })
    return path.read_text(encoding="utf-8")


@mcp.resource("komposos://reports/queue-process-brief")
def queue_process_brief() -> str:
    """9-region interconnection queue study. The LBNL-completion figures are
    measured (reconcile to Queued Up Sheet 25 to the integer); post-IA
    completion, durations and cohort panels are our computation applying LBNL's
    methods to slices LBNL publishes only nationally or not at all.
    Source: run_stitch_brief pipeline."""
    return _report_json("stitch_2026-06-23/queue_process_brief.json")


@mcp.resource("komposos://reports/large-load-experiment")
def large_load_experiment() -> str:
    """Large load (data center) coordination simulation (simulated —
    stylized ESIG-report scenario, not observations)."""
    return _report_json("experiments/large_load_coordination_experiment.json")


def main() -> None:
    mcp.run()  # stdio transport


if __name__ == "__main__":
    main()
