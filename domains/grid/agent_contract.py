# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Shared local-agent contract for the grid map.

This module is intentionally model/vendor neutral. The "AI" is the user's
terminal coding agent; this repo supplies grounded JSON tools and a prompt
contract the agent can follow without an online API key.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Dict, List


ENTRYPOINT = "python -m domains.grid.agent_tools"
CONTRACT_VERSION = "grid-local-agent-v1"


TOOL_SPECS: List[Dict] = [
    {
        "name": "ba",
        "command": f"{ENTRYPOINT} --year YEAR ba CODE",
        "use_when": "Inspect one balancing authority.",
        "returns": ["summary", "provenance", "degree", "facts"],
        "example": f"{ENTRYPOINT} ba PJM",
    },
    {
        "name": "tie",
        "command": f"{ENTRYPOINT} --year YEAR tie BA_A BA_B",
        "use_when": "Inspect one interchange tie and its net-flow direction.",
        "returns": ["summary", "provenance", "gross_twh", "net_direction"],
        "example": f"{ENTRYPOINT} tie PJM NYIS",
    },
    {
        "name": "path",
        "command": f"{ENTRYPOINT} --year YEAR path BA_A BA_B --k N",
        "use_when": "Find physical connectivity routes between two BAs.",
        "returns": ["summary", "provenance", "routes"],
        "example": f"{ENTRYPOINT} path CISO PJM --k 3",
    },
    {
        "name": "similar",
        "command": f"{ENTRYPOINT} --year YEAR similar CODE --top N",
        "use_when": "Find BAs with similar measured-neighbor structure.",
        "returns": ["summary", "provenance", "similar"],
        "example": f"{ENTRYPOINT} similar PJM --top 5",
    },
    {
        "name": "bottlenecks",
        "command": f"{ENTRYPOINT} --year YEAR bottlenecks --top N",
        "use_when": "Rank structural bottleneck ties.",
        "returns": ["summary", "provenance", "bottlenecks"],
        "example": f"{ENTRYPOINT} bottlenecks --top 10",
    },
    {
        "name": "seam",
        "command": f"{ENTRYPOINT} --year YEAR seam",
        "use_when": "Explain the weakest spectral seam.",
        "returns": ["summary", "provenance", "smaller_side"],
        "example": f"{ENTRYPOINT} seam",
    },
    {
        "name": "whatif",
        "command": f"{ENTRYPOINT} --year YEAR whatif --cut A-B,C-D",
        "use_when": "Run a full Ricci/spectral recompute after cutting ties.",
        "returns": ["summary", "provenance", "baseline", "after"],
        "example": f"{ENTRYPOINT} whatif --cut PJM-NYIS,MISO-SWPP",
    },
    {
        "name": "gaps",
        "command": f"{ENTRYPOINT} --year YEAR gaps --top N",
        "use_when": "Ask OPTIMUS for structural-gap relief candidates.",
        "returns": ["summary", "provenance", "gaps"],
        "example": f"{ENTRYPOINT} gaps --top 5",
    },
]


def agent_manifest() -> Dict:
    """Machine-readable contract for terminal agents and the static map."""
    return {
        "version": CONTRACT_VERSION,
        "entrypoint": ENTRYPOINT,
        "mode": "local_terminal_agent",
        "requires_online_api": False,
        "answer_contract": [
            "Use tool JSON for quantitative or structural grid claims.",
            "Include the tool summary and provenance in user-facing answers.",
            "Label screening results as screening results.",
            "Say when a requested claim is not grounded by the available tools.",
            "Do not invent flows, prices, topology, years, or BA facts.",
        ],
        "tools": deepcopy(TOOL_SPECS),
        "output_shape": {
            "success": ["tool", "summary", "provenance", "result"],
            "error": ["error"],
        },
    }


def agent_prompt() -> str:
    """Plain prompt a user can paste into any terminal coding agent."""
    tools = "\n".join(
        f"- {spec['name']}: {spec['example']} ({spec['use_when']})"
        for spec in TOOL_SPECS
    )
    return (
        "You are the local KOMPOSOS grid-map agent for this repository.\n"
        "\n"
        "Grounding rules:\n"
        "- Answer grid questions by running the local JSON tools, not from memory.\n"
        "- Quote or paraphrase the returned summary and provenance.\n"
        "- Keep measured values, proxies, and screening signals separate.\n"
        "- If the tools cannot ground a claim, say that directly.\n"
        "- Never invent BA facts, flows, costs, topology, years, or evidence.\n"
        "\n"
        f"Entrypoint: {ENTRYPOINT}\n"
        "\n"
        "Available tools:\n"
        f"{tools}\n"
        "\n"
        "Recommended answer shape:\n"
        "1. One-sentence result.\n"
        "2. Computed evidence from tool JSON.\n"
        "3. Provenance and limits.\n"
        "4. Suggested next tool call only when it would deepen the answer.\n"
    )


def map_agent_payload() -> Dict:
    """Small payload embedded in the static map."""
    manifest = agent_manifest()
    return {
        "version": manifest["version"],
        "entrypoint": manifest["entrypoint"],
        "requires_online_api": manifest["requires_online_api"],
        "prompt": agent_prompt(),
        "tools": manifest["tools"],
    }
