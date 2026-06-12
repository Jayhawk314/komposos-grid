# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for D8 relief curves."""

import json

import pytest

from domains.grid.relief_curves import (
    CostBenchmark,
    build_relief_curve_report,
    build_relief_scm,
    evaluate_relief_point,
)


def _queue_match(path):
    payload = {
        "ties": [
            {
                "ba_a": "PJM",
                "ba_b": "NYIS",
                "evidence_status": "lmp_component_proxy",
                "congestion_spread_usd_mwh": 2.0,
                "tie_value_cap_usd": 20_000_000.0,
                "active": {"n": 4, "gw": 2.0, "capped_value_usd": 20_000_000.0},
                "withdrawn": {"n": 7, "gw": 3.0, "capped_value_usd": 20_000_000.0},
            },
            {
                "ba_a": "SOCO",
                "ba_b": "FPL",
                "evidence_status": "structural_only",
                "congestion_spread_usd_mwh": 0.0,
                "tie_value_cap_usd": 0.0,
                "active": {"n": 1, "gw": 1.0, "capped_value_usd": 0.0},
                "withdrawn": {"n": 1, "gw": 1.0, "capped_value_usd": 0.0},
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _congestion(path):
    payload = {
        "claims": [
            {
                "ba_a": "PJM",
                "ba_b": "NYIS",
                "gross_mwh": 10_000_000.0,
                "evidence_status": "lmp_component_proxy",
            }
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _constraints(path):
    payload = {
        "constraints": [
            {
                "constraint_name": "NOTTINGH230 KV  2-3",
                "binding_hours": 6000,
                "severity": 350_000,
            }
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_relief_scm_do_intervention_increases_relief():
    benchmark = CostBenchmark(
        "test_capacity",
        annualized_cost_usd_per_mw_year=100_000.0,
        effective_mwh_per_mw_year=1000.0,
        source="fixture",
    )
    scm = build_relief_scm(2.0, 10_000.0, benchmark)

    low = evaluate_relief_point("A", "B", scm, benchmark, 1.0)
    high = evaluate_relief_point("A", "B", scm, benchmark, 5.0)

    assert high.relief_mwh > low.relief_mwh
    assert high.residual_spread_usd_mwh < low.residual_spread_usd_mwh
    assert low.annual_cost_usd == pytest.approx(100_000.0)


def test_relief_curve_report_ranks_priced_ties_and_attaches_constraints(tmp_path):
    queue = tmp_path / "queue.json"
    congestion = tmp_path / "congestion.json"
    pjm = tmp_path / "pjm.json"
    _queue_match(queue)
    _congestion(congestion)
    _constraints(pjm)

    benchmark = CostBenchmark(
        "cheap_capacity",
        annualized_cost_usd_per_mw_year=1_000.0,
        effective_mwh_per_mw_year=8760.0,
        source="fixture",
    )
    report = build_relief_curve_report(
        queue,
        congestion_report_path=congestion,
        constraint_reports={"PJM": pjm},
        benchmarks=[benchmark],
        mw_steps=[10.0, 100.0],
    )

    assert len(report.opportunities) == 1
    opportunity = report.ranked()[0]
    assert opportunity.ba_a == "PJM"
    assert opportunity.ba_b == "NYIS"
    assert opportunity.constraints[0].constraint_name.startswith("NOTTINGH")
    assert opportunity.best_point.benchmark == "cheap_capacity"
    assert opportunity.best_point.benefit_cost_ratio > 0
    assert len(opportunity.points) == 2


def test_relief_curve_report_exports(tmp_path):
    queue = tmp_path / "queue.json"
    congestion = tmp_path / "congestion.json"
    pjm = tmp_path / "pjm.json"
    _queue_match(queue)
    _congestion(congestion)
    _constraints(pjm)
    report = build_relief_curve_report(queue, congestion, {"PJM": pjm}, mw_steps=[50.0])

    json_path = tmp_path / "relief.json"
    csv_path = tmp_path / "relief.csv"
    points_path = tmp_path / "points.csv"
    md_path = tmp_path / "relief.md"
    report.export_json(json_path)
    report.export_csv(csv_path)
    report.export_points_csv(points_path)
    report.export_markdown(md_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["opportunities"]
    assert "best_benchmark" in csv_path.read_text(encoding="utf-8")
    assert "intervention_mw" in points_path.read_text(encoding="utf-8")
    assert "Grid Relief Curves" in md_path.read_text(encoding="utf-8")
