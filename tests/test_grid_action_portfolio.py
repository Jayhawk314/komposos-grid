# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the grid action portfolio."""

import json

from domains.grid.action_portfolio import build_action_portfolio, load_ledger_claims
from domains.grid.waste_ledger import WasteClaim, WasteLedger


def _claim(claim_id, problem, evidence, quantity=1.0, value=0.0, kind="energy"):
    return WasteClaim(
        claim_id=claim_id,
        problem=problem,
        title=claim_id.replace("_", " "),
        geography="A-B" if "congestion" in claim_id else "Test",
        evidence_level=evidence,
        estimate_kind=kind,
        quantity=quantity,
        unit="MWh",
        value_usd=value,
    )


def _ledger_path(tmp_path):
    ledger = WasteLedger(
        claims=[
            _claim(
                "caiso_total_curtailment",
                "curtailment",
                "measured",
                quantity=100.0,
                value=1000.0,
                kind="energy_upper_bound_value",
            ),
            _claim(
                "caiso_local_curtailment",
                "td_losses_congestion",
                "measured",
                quantity=40.0,
                kind="curtailment_reason_local",
            ),
            _claim(
                "caiso_system_curtailment",
                "curtailment",
                "measured",
                quantity=60.0,
                kind="curtailment_reason_system",
            ),
            _claim(
                "eaglei_total_customer_hours",
                "reliability",
                "measured",
                quantity=500.0,
                kind="customer_hours",
            ),
            _claim(
                "lbnl_queue_withdrawal_burden",
                "interconnection_queue",
                "measured",
                quantity=0.7,
                kind="withdrawal_rate_decided_projects",
            ),
            _claim(
                "congestion_a_b",
                "td_losses_congestion",
                "measured_proxy",
                quantity=25.0,
                value=250.0,
                kind="lmp_congestion_component_proxy",
            ),
            _claim(
                "ba_footprint_corrections",
                "data_coherence",
                "validated_hypothesis",
                quantity=12.0,
                kind="accounting_error_reduction",
            ),
            WasteClaim(
                claim_id="congestion_weak_hub",
                problem="td_losses_congestion",
                title="weak hub proxy",
                geography="Weak-Hub",
                evidence_level="measured_proxy",
                estimate_kind="lmp_spread_proxy",
                quantity=10.0,
                unit="MWh",
                value_usd=100.0,
                notes="flow/price alignment is weak",
            ),
            _claim(
                "congestion_c_d",
                "td_losses_congestion",
                "structural_only",
                quantity=30.0,
                kind="flow_weighted_negative_curvature",
            ),
        ]
    )
    path = tmp_path / "ledger.json"
    ledger.export_json(path)
    return path


def test_load_ledger_claims_round_trips_rows(tmp_path):
    path = _ledger_path(tmp_path)

    claims = load_ledger_claims(path)

    assert {claim.claim_id for claim in claims} >= {
        "caiso_total_curtailment",
        "congestion_a_b",
    }


def test_action_portfolio_groups_claims_by_decision_readiness(tmp_path):
    path = _ledger_path(tmp_path)

    portfolio = build_action_portfolio(path)
    statuses = {action.decision_status for action in portfolio.actions}
    ids = {action.action_id for action in portfolio.actions}

    assert statuses == {
        "ready_for_scoping",
        "policy_design",
        "validate_proxy",
        "review_required",
        "attach_evidence",
    }
    assert "caiso_curtailment_package" in ids
    assert "reliability_hardening_package" in ids
    assert "queue_ia_reform_package" in ids
    assert "validate_congestion_a_b" in ids
    assert "review_ba_footprint_corrections" in ids
    assert "attach_evidence_to_structural_bottlenecks" in ids


def test_action_portfolio_keeps_value_buckets_separate(tmp_path):
    path = _ledger_path(tmp_path)

    portfolio = build_action_portfolio(path)
    caiso = next(a for a in portfolio.actions if a.action_id == "caiso_curtailment_package")
    proxy = next(a for a in portfolio.actions if a.action_id == "validate_congestion_a_b")
    weak = next(a for a in portfolio.actions if a.action_id == "validate_congestion_weak_hub")
    totals = portfolio.totals()

    assert caiso.upper_bound_value_usd == 1000.0
    assert caiso.measured_value_usd == 0.0
    assert proxy.proxy_value_usd == 250.0
    assert "Component spread is stronger" in proxy.caveat
    assert "weak flow/price alignment" in weak.caveat
    assert totals["upper_bound_value_usd"] == 1000.0
    assert totals["proxy_value_usd"] == 350.0


def test_action_portfolio_exports(tmp_path):
    path = _ledger_path(tmp_path)
    portfolio = build_action_portfolio(path)
    csv_path = tmp_path / "portfolio.csv"
    json_path = tmp_path / "portfolio.json"
    md_path = tmp_path / "portfolio.md"
    html_path = tmp_path / "portfolio.html"

    portfolio.export_csv(csv_path)
    portfolio.export_json(json_path)
    portfolio.export_markdown(md_path)
    portfolio.export_html(html_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["n_actions"] == len(portfolio.actions)
    assert "Grid Action Portfolio" in md_path.read_text(encoding="utf-8")
    assert "<!doctype html>" in html_path.read_text(encoding="utf-8")
    assert "decision_status" in csv_path.read_text(encoding="utf-8")
