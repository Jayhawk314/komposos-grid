# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for energy solution cards."""

import csv
import json

import pytest

from domains.grid.solution_cards import (
    build_energy_solution_report,
    load_miso_trends,
    load_nyiso_trends,
)


def _write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _congestion(path):
    payload = {
        "claims": [
            {
                "ba_a": "MISO",
                "ba_b": "SWPP",
                "evidence_status": "lmp_component_proxy",
                "gross_mwh": 4_000_000,
                "evidence_source": "MISO DA ex-post LMP 2023",
                "mean_price_spread_usd_mwh": 5.09,
                "mean_congestion_component_spread_usd_mwh": 4.74,
                "hours_observed": 8760,
            },
            {
                "ba_a": "PJM",
                "ba_b": "NYIS",
                "evidence_status": "lmp_component_proxy",
                "gross_mwh": 10_000_000,
                "evidence_source": "NYISO 2023",
                "mean_price_spread_usd_mwh": 2.01,
                "mean_congestion_component_spread_usd_mwh": 1.53,
                "hours_observed": 8759,
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _queue(path):
    payload = {
        "ties": [
            {
                "ba_a": "MISO",
                "ba_b": "SWPP",
                "congestion_spread_usd_mwh": 4.74,
                "tie_value_cap_usd": 18_960_000,
                "active": {"gw": 10.0, "capped_value_usd": 18_960_000},
                "withdrawn": {"gw": 40.0, "capped_value_usd": 18_960_000},
            },
            {
                "ba_a": "PJM",
                "ba_b": "NYIS",
                "congestion_spread_usd_mwh": 1.53,
                "tie_value_cap_usd": 15_300_000,
                "active": {"gw": 20.0, "capped_value_usd": 15_300_000},
                "withdrawn": {"gw": 50.0, "capped_value_usd": 15_300_000},
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _relief(path):
    payload = {
        "opportunities": [
            {
                "ba_a": "MISO",
                "ba_b": "SWPP",
                "best_benchmark": "transmission_capacity",
                "best_intervention_mw": 50,
                "best_benefit_cost_ratio": 0.25,
                "constraints": "MISO:CHAR_CK-WATFORD; SPP:CHAWATCHAPAT",
            },
            {
                "ba_a": "PJM",
                "ba_b": "NYIS",
                "best_benchmark": "transmission_capacity",
                "best_intervention_mw": 50,
                "best_benefit_cost_ratio": 0.09,
                "constraints": "PJM:NOTTINGH230 KV",
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _miso_2024(path):
    _write_csv(
        path,
        [
            {
                "ba_a": "MISO",
                "ba_b": "SWPP",
                "evidence_source": "MISO DA ex-post LMP (2024-01-01..2024-12-31)",
                "evidence_method": "interface_settlement_spread",
                "mean_price_spread_usd_mwh": 6.63,
                "mean_congestion_component_spread_usd_mwh": 6.31,
                "hours_observed": 8736,
                "notes": "fixture",
            }
        ],
    )


def _nyiso(path):
    path.write_text(
        "2024 | NYISO seam component audit vs PJM: 8783 hours, "
        "mean |LBMP spread| $2.78/MWh, mean |congestion-component spread| "
        "$2.02/MWh (72.7% of LBMP spread), mean |loss spread| $0.84/MWh\n"
        "2025 | NYISO seam component audit vs PJM: 8759 hours, "
        "mean |LBMP spread| $9.03/MWh, mean |congestion-component spread| "
        "$7.38/MWh (81.7% of LBMP spread), mean |loss spread| $1.74/MWh\n",
        encoding="utf-8",
    )


def test_trend_loaders_parse_miso_and_nyiso(tmp_path):
    miso = tmp_path / "miso.csv"
    nyiso = tmp_path / "nyiso.txt"
    _miso_2024(miso)
    _nyiso(nyiso)

    miso_trends = load_miso_trends(miso)
    nyiso_trends = load_nyiso_trends(nyiso)

    assert miso_trends[0].year == 2024
    assert miso_trends[0].component_spread_usd_mwh == pytest.approx(6.31)
    assert [trend.year for trend in nyiso_trends] == [2024, 2025]
    assert nyiso_trends[-1].component_spread_usd_mwh == pytest.approx(7.38)


def test_solution_cards_learn_latest_trends_and_scale_bcr(tmp_path):
    congestion = tmp_path / "congestion.json"
    queue = tmp_path / "queue.json"
    relief = tmp_path / "relief.json"
    miso = tmp_path / "miso.csv"
    nyiso = tmp_path / "nyiso.txt"
    _congestion(congestion)
    _queue(queue)
    _relief(relief)
    _miso_2024(miso)
    _nyiso(nyiso)

    report = build_energy_solution_report(
        congestion,
        queue,
        relief,
        miso_evidence=miso,
        nyiso_2024_2025=nyiso,
    )
    cards = {card.geography: card for card in report.cards}

    miso_card = cards["MISO-SWPP"]
    assert miso_card.current_year == 2024
    assert miso_card.spread_usd_mwh == pytest.approx(6.31)
    assert miso_card.annual_value_usd == pytest.approx(25_240_000)
    assert miso_card.updated_generic_benefit_cost_ratio == pytest.approx(0.25 * 6.31 / 4.74)
    assert miso_card.active_queue_can_reach_cap

    pjm_card = cards["NYIS-PJM"]
    assert pjm_card.current_year == 2025
    assert pjm_card.spread_usd_mwh == pytest.approx(7.38)
    assert pjm_card.solution_status == "priority_solution_study"
    assert "2025" in pjm_card.next_action


def test_solution_report_exports(tmp_path):
    congestion = tmp_path / "congestion.json"
    queue = tmp_path / "queue.json"
    relief = tmp_path / "relief.json"
    miso = tmp_path / "miso.csv"
    _congestion(congestion)
    _queue(queue)
    _relief(relief)
    _miso_2024(miso)
    report = build_energy_solution_report(congestion, queue, relief, miso_evidence=miso)

    csv_path = tmp_path / "cards.csv"
    json_path = tmp_path / "cards.json"
    md_path = tmp_path / "cards.md"
    report.export_csv(csv_path)
    report.export_json(json_path)
    report.export_markdown(md_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["n_cards"] == len(report.cards)
    assert "Energy Solution Cards" in md_path.read_text(encoding="utf-8")
    assert "solution_status" in csv_path.read_text(encoding="utf-8")
