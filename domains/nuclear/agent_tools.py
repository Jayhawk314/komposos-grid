# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Grounded tool surface for a local coding agent query in the nuclear domain.

Exposes relational, curvature, spectral, and what-if capabilities for the
civilian nuclear enrichment fuel supply chain.

Commands:
    python -m domains.nuclear.agent_tools prompt
    python -m domains.nuclear.agent_tools stats
    python -m domains.nuclear.agent_tools path --source enrichment:urenco_eunice --target demand:hyperscaler_dc
    python -m domains.nuclear.agent_tools bottlenecks
    python -m domains.nuclear.agent_tools whatif --shutdown conversion:metropolis_converdyn
    python -m domains.nuclear.agent_tools whatif --upgrade enrichment:urenco_eunice-fabrication:westinghouse_columbia=0.85
"""

from __future__ import annotations

import argparse
import json
import sys
import os
from typing import Dict, List, Tuple

# Ensure local source imports are accessible
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_dirs = [
    os.path.join(repo_root, "src"),
    os.path.join(repo_root, "src", "komposos_core"),
    os.path.join(repo_root, "src", "komposos_wesys"),
]
for d in src_dirs:
    if os.path.exists(d) and d not in sys.path:
        sys.path.insert(0, d)

from core.category import Category
from cog.session import CogSession
from cog.engine import CogEngine
from cog.schema import CogClaim
from domains.nuclear.ingest import NuclearCategoryBuilder
from domains.nuclear.flow_geometry import analyze_enrichment_geometry


def _load_base_category() -> Category:
    cat = Category(name="nuclear_agent_tools", db_path=":memory:")
    builder = NuclearCategoryBuilder(cat)
    builder.ingest_synthetic_baseline()
    return cat


def tool_prompt() -> str:
    return """
=== NUCLEAR AGENT WORK CONTRACT ===
You are an expert energy systems AI agent. You verify nuclear fuel supply chain structures
using category theory and Ollivier-Ricci flow geometry.
Guidelines:
1. Always ground your claims. Call these tools first and report their JSON outputs verbatim.
2. Underline structural bottlenecks (represented by negative or low positive curvature).
3. Check SMR fuel availability by computing paths and temporal alignment.
"""


def tool_stats() -> Dict:
    cat = _load_base_category()
    objs = [o.name for o in cat.objects()]
    mors = [f"{m.source}->{m.target} (conf={m.confidence:.2f})" for m in cat.morphisms()]
    return {
        "tool": "stats",
        "summary": f"Category contains {len(objs)} facilities and {len(mors)} connections.",
        "result": {
            "facilities": objs,
            "flows": mors
        }
    }


def tool_path(source: str, target: str) -> Dict:
    cat = _load_base_category()
    opt = cat.optimal_path(source, target)
    if opt:
        path, weight = opt
        summary = f"Optimal path found: {' -> '.join(path)} (Multiplicative Yield: {weight:.4f})"
        res = {"path": path, "yield": weight}
    else:
        summary = f"No path found between '{source}' and '{target}'."
        res = {"path": [], "yield": 0.0}
    return {
        "tool": "path",
        "summary": summary,
        "result": res
    }


def tool_bottlenecks() -> Dict:
    cat = _load_base_category()
    report = analyze_enrichment_geometry(cat)
    items = []
    for u, v, kappa in report.edge_curvatures:
        items.append({
            "source": u,
            "target": v,
            "curvature": round(kappa, 4),
            "verdict": "BOTTLENECK" if kappa < 0.35 else "STABLE"
        })
    return {
        "tool": "bottlenecks",
        "summary": f"Ranked {len(items)} supply chain edges by geometric curvature.",
        "result": {"edges": items}
    }


def tool_whatif(shutdown: str | None = None, upgrade: str | None = None) -> Dict:
    cat = _load_base_category()
    mors = cat.morphisms()
    
    action_descr = ""
    if shutdown:
        # Cut or lower the flow confidence of a node/facility to 0.0
        target_mors = [m for m in mors if m.source == shutdown or m.target == shutdown]
        for m in target_mors:
            m.confidence = 0.0
            cat._hom_values[(m.source, m.target)] = 0.0
        action_descr = f"Shut down facility: '{shutdown}' (cut {len(target_mors)} connections)"
        
    elif upgrade:
        # Upgrade a specific connection edge (e.g. urenco-fabrication=0.85)
        try:
            edge_part, val_part = upgrade.split("=")
            src, tgt = edge_part.split("-")
            target_val = float(val_part)
            target_mors = [m for m in mors if m.source == src and m.target == tgt]
            for m in target_mors:
                m.confidence = target_val
                cat._hom_values[(m.source, m.target)] = target_val
            action_descr = f"Upgraded edge '{src} -> {tgt}' confidence to {target_val:.2f}"
        except Exception as exc:
            return {"tool": "whatif", "error": f"Failed parsing upgrade descriptor: {exc}"}

    # Recompute analytics
    geom = analyze_enrichment_geometry(cat)
    
    session = CogSession(category=cat)
    cog = CogEngine(session=session)
    claim = CogClaim(
        source="enrichment:urenco_eunice",
        target="demand:hyperscaler_dc",
        relation="powers",
        confidence=0.50
    )
    result = cog.check_claim(claim)
    
    opt = cat.optimal_path("enrichment:urenco_eunice", "demand:hyperscaler_dc")
    path_weight = opt[1] if opt else 0.0

    summary = (
        f"What-If: {action_descr}. "
        f"Fiedler connectivity: {geom.fiedler_value:.5f}. "
        f"Reactor powers claim: {result.status.value.upper()} (yield: {path_weight:.4f})."
    )

    return {
        "tool": "whatif",
        "summary": summary,
        "result": {
            "fiedler_connectivity": geom.fiedler_value,
            "claim_status": result.status.value,
            "path_yield": path_weight
        }
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Grounded nuclear supply tools for local coding agents (JSON output)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prompt")
    sub.add_parser("stats")
    
    p = sub.add_parser("path")
    p.add_argument("--source", required=True)
    p.add_argument("--target", required=True)
    
    sub.add_parser("bottlenecks")
    
    p = sub.add_parser("whatif")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--shutdown", help="Name of facility to shut down (e.g. conversion:metropolis_converdyn)")
    group.add_argument("--upgrade", help="Format: source-target=value (e.g. enrichment:urenco_eunice-fabrication:westinghouse_columbia=0.85)")
    
    args = parser.parse_args(argv)

    if args.cmd == "prompt":
        print(tool_prompt())
        return 0

    _TOOLS = {
        "stats": lambda a: tool_stats(),
        "path": lambda a: tool_path(a.source, a.target),
        "bottlenecks": lambda a: tool_bottlenecks(),
        "whatif": lambda a: tool_whatif(a.shutdown, a.upgrade)
    }

    result = _TOOLS[args.cmd](args)
    print(json.dumps(result, indent=2))
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
