# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the explain (lexical RAG) tool and its registration."""

from domains.grid import agent_tools
from domains.grid.agent_contract import agent_manifest


def test_explain_returns_cited_passages_from_repo_docs():
    out = agent_tools.tool_explain("curtailment", top=3)
    assert out["tool"] == "explain"
    passages = out["result"]["passages"]
    assert passages, "expected at least one passage about curtailment"
    p = passages[0]
    assert p["source"].endswith(".md")          # cites a real doc
    assert p["section"] and p["excerpt"]          # heading + verbatim excerpt
    assert "verbatim" in out["provenance"] and "TF-IDF" in out["provenance"]


def test_explain_empty_query_is_an_honest_error():
    out = agent_tools.tool_explain("   ", top=3)
    assert "error" in out and "passages" not in out.get("result", {})


def test_explain_registered_in_cli_and_manifest():
    assert "explain" in agent_tools._TOOLS
    names = [t["name"] for t in agent_manifest()["tools"]]
    assert names[-1] == "explain" or "explain" in names
