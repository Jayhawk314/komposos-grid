# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

from domains.grid.agent_server import answer_question


def test_agent_chat_routes_help_to_manifest():
    resp = answer_question("what can you answer?", year="2025")

    assert resp["ok"] is True
    assert "grounded grid tools" in resp["answer"]
    assert resp["cards"][0]["kind"] == "manifest"


def test_agent_chat_routes_ba_context_to_ba_tool():
    resp = answer_question("explain this", year="2025", context={"kind": "ba", "id": "PJM"})

    assert resp["ok"] is True
    assert "PJM" in resp["answer"]
    assert resp["tools"][0]["tool"] == "ba"
    assert "PJM" in resp["highlight"]["nodes"]


def test_agent_chat_routes_path_question_to_path_tool():
    resp = answer_question("how is CISO connected to PJM?", year="2025")

    assert resp["ok"] is True
    assert resp["tools"][0]["tool"] == "path"
    assert resp["cards"][0]["rows"]
    assert "CISO" in resp["highlight"]["nodes"]
    assert "PJM" in resp["highlight"]["nodes"]


def test_agent_chat_routes_tie_context_to_whatif():
    resp = answer_question(
        "what if we cut this?",
        year="2025",
        context={"kind": "tie", "a": "PJM", "b": "NYIS"},
    )

    assert resp["ok"] is True
    assert resp["tools"][0]["tool"] == "whatif"
    assert resp["tools"][0]["result"]["ties_cut"] == 1
    assert resp["cards"][0]["title"] == "What-if"
    assert "PJM-NYIS" in resp["highlight"]["edges"]


def test_agent_suggestions_do_not_suggest_same_source_and_target():
    resp = answer_question("similar to PJM", year="2025")

    assert "Find paths from PJM to PJM" not in resp["suggestions"]
    assert "Find paths from PJM to MISO" in resp["suggestions"]


def test_agent_understands_plain_language_weak_spots():
    resp = answer_question("where is power getting stuck?", year="2025")

    assert resp["ok"] is True
    assert resp["tools"][0]["tool"] == "bottlenecks"
    assert resp["cards"][0]["actions"][0]["type"] == "highlight"


def test_agent_understands_plain_language_similarity():
    resp = answer_question("what areas act like PJM?", year="2025")

    assert resp["ok"] is True
    assert resp["tools"][0]["tool"] == "similar"


def test_typed_tie_questions_get_tie_followups_and_actions():
    resp = answer_question("why is PJM-NYIS important?", year="2025")

    assert resp["ok"] is True
    assert resp["tools"][0]["tool"] == "tie"
    assert "What breaks if PJM-NYIS fails?" in resp["suggestions"]
    assert resp["cards"][0]["actions"][0]["type"] == "highlight"


def test_whatif_card_can_apply_cut():
    resp = answer_question("what breaks if PJM-NYIS fails?", year="2025")

    actions = resp["cards"][0]["actions"]
    assert resp["tools"][0]["tool"] == "whatif"
    assert any(a["type"] == "apply_cut" and a["cut"] == ["PJM-NYIS"] for a in actions)
