# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for corridor solution studies."""

import json

import pytest

from domains.grid.solution_studies import (
    InterventionTemplate,
    build_solution_study_report,
)


def _cards(path):
    payload = {
        "cards": [
            {
                "geography": "NYIS-PJM",
                "title": "NYISO-PJM 2025 congestion relief",
                "current_year": 2025,
                "annual_value_usd": 73_800_000.0,
                "spread_usd_mwh": 7.38,
                "trend_summary": "2023 $1.53/MWh -> 2025 $7.38/MWh.",
                "evidence_basis": "fixture",
                "constraints": "PJM:NOTTINGH; PJM:GRACETON",
                "active_queue_gw": 10.0,
                "withdrawn_queue_gw": 20.0,
            },
            {
                "geography": "MISO-SWPP",
                "title": "MISO-SPP wind-belt transfer relief",
                "current_year": 2024,
                "annual_value_usd": 25_240_000.0,
                "spread_usd_mwh": 6.31,
                "trend_summary": "2023 $4.74/MWh -> 2024 $6.31/MWh.",
                "evidence_basis": "fixture",
                "constraints": "MISO:CHAR_CK-WATFORD; SPP:CHAWATCHAPAT",
                "active_queue_gw": 11.0,
                "withdrawn_queue_gw": 21.0,
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _queue(path):
    payload = {
        "ties": [
            {
                "ba_a": "PJM",
                "ba_b": "NYIS",
                "top_active": [
                    {
                        "q_id": "A1",
                        "fuel": "wind",
                        "state": "NJ",
                        "region": "pjm",
                        "mw": 100,
                        "status": "active",
                        "role": "generation",
                        "side": "PJM",
                        "relief_mwh": 1000,
                    }
                ],
                "top_withdrawn": [
                    {
                        "q_id": "W1",
                        "fuel": "gas",
                        "state": "PA",
                        "region": "pjm",
                        "mw": 200,
                        "status": "withdrawn",
                        "role": "generation",
                        "side": "PJM",
                        "relief_mwh": 2000,
                    }
                ],
            },
            {
                "ba_a": "MISO",
                "ba_b": "SWPP",
                "top_active": [],
                "top_withdrawn": [],
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_solution_study_revalues_queue_projects_and_cost_gates(tmp_path):
    cards = tmp_path / "cards.json"
    queue = tmp_path / "queue.json"
    _cards(cards)
    _queue(queue)
    intervention = InterventionTemplate(
        intervention_id="test_10mw",
        label="10 MW transfer",
        capacity_mw=10,
        effective_mwh_per_mw_year=100,
        solution_type="transfer",
        source="fixture",
    )

    report = build_solution_study_report(
        cards,
        queue,
        interventions=[intervention],
        fixed_charge_rate=0.10,
    )
    studies = {study.geography: study for study in report.studies}

    pjm = studies["NYIS-PJM"]
    assert pjm.top_active[0].relief_value_usd == pytest.approx(7_380.0)
    assert pjm.top_withdrawn[0].relief_value_usd == pytest.approx(14_760.0)
    case = pjm.interventions[0]
    assert case.relief_mwh == pytest.approx(1000.0)
    assert case.relief_value_usd == pytest.approx(7_380.0)
    assert case.break_even_capex_usd == pytest.approx(73_800.0)
    assert case.break_even_capex_usd_per_kw == pytest.approx(7.38)


def test_solution_study_exports_combined_and_individual_memos(tmp_path):
    cards = tmp_path / "cards.json"
    queue = tmp_path / "queue.json"
    _cards(cards)
    _queue(queue)
    report = build_solution_study_report(cards, queue)

    json_path = tmp_path / "studies.json"
    csv_path = tmp_path / "studies.csv"
    intervention_path = tmp_path / "interventions.csv"
    md_path = tmp_path / "studies.md"
    memo_dir = tmp_path / "memos"
    report.export_json(json_path)
    report.export_csv(csv_path)
    report.export_interventions_csv(intervention_path)
    report.export_markdown(md_path)
    memos = report.export_individual_memos(memo_dir)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["n_studies"] == 2
    assert "best_break_even_capex_usd" in csv_path.read_text(encoding="utf-8")
    assert "break_even_capex_usd_per_kw" in intervention_path.read_text(encoding="utf-8")
    assert "Energy Solution Studies" in md_path.read_text(encoding="utf-8")
    assert len(memos) == 2
    assert all(path.exists() for path in memos)
