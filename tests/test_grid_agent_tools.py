# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

import json

from domains.grid import agent_tools
from domains.grid.agent_contract import agent_manifest, agent_prompt
from domains.grid.flow_geometry import TieLine


def test_agent_manifest_is_vendor_neutral_and_grounded():
    manifest = agent_manifest()
    assert manifest["mode"] == "local_terminal_agent"
    assert manifest["requires_online_api"] is False
    assert manifest["entrypoint"] == "python -m domains.grid.agent_tools"
    assert "Do not invent flows, prices, topology, years, or BA facts." in manifest[
        "answer_contract"
    ]
    assert {tool["name"] for tool in manifest["tools"]} >= {
        "ba",
        "tie",
        "path",
        "similar",
        "bottlenecks",
        "seam",
        "whatif",
        "gaps",
    }


def test_agent_prompt_names_the_local_tool_entrypoint():
    prompt = agent_prompt()
    assert "Entrypoint: python -m domains.grid.agent_tools" in prompt
    assert "Answer grid questions by running the local JSON tools" in prompt


def test_agent_tools_manifest_and_prompt_cli(capsys):
    assert agent_tools.main(["manifest"]) == 0
    manifest = json.loads(capsys.readouterr().out)
    assert manifest["version"] == "grid-local-agent-v1"

    assert agent_tools.main(["prompt"]) == 0
    prompt = capsys.readouterr().out
    assert "Grounding rules:" in prompt
    assert "python -m domains.grid.agent_tools ba PJM" in prompt


def test_path_tool_reports_readable_route_strength(monkeypatch):
    ties = [
        TieLine("A", "B", 100_000_000.0, 100_000_000.0),
        TieLine("B", "C", 10_000_000.0, 10_000_000.0),
        TieLine("C", "D", 1_000_000.0, 1_000_000.0),
    ]
    monkeypatch.setattr(agent_tools, "_ties", lambda year=None: ties)

    result = agent_tools.tool_path("A", "D", k=1)
    route = result["result"]["routes"][0]

    assert route["hops"] == ["A", "B", "C", "D"]
    assert route["flow_weight"] > 0
    assert route["weakest_tie"] == "C-D"
    assert route["weakest_tie_twh"] == 1.0
    assert "weakest tie C-D" in result["summary"]
