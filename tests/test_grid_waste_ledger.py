# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the unified grid waste ledger."""

import json

from domains.grid.waste_ledger import (
    WasteClaim,
    WasteLedger,
    build_waste_ledger,
    claims_from_ba_footprint,
    claims_from_congestion_report,
    claims_from_outage_report,
)


def _write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_ba_footprint_claim_is_validated_hypothesis(tmp_path):
    path = _write_json(
        tmp_path / "ba.json",
        {
            "accepted_corrections": 2,
            "before": {
                "agreement_rate": 0.4,
                "contradictions": 5,
                "abs_error_mwh": 1000.0,
            },
            "after": {
                "agreement_rate": 0.6,
                "contradictions": 2,
                "abs_error_mwh": 650.0,
            },
        },
    )

    claim = claims_from_ba_footprint(path)[0]

    assert claim.evidence_level == "validated_hypothesis"
    assert claim.quantity == 350.0
    assert "human review pending" in claim.confidence


def test_congestion_claims_keep_proxy_and_structural_separate(tmp_path):
    path = _write_json(
        tmp_path / "congestion.json",
        {
            "claims": [
                {
                    "ba_a": "A",
                    "ba_b": "B",
                    "evidence_status": "price_spread_proxy",
                    "gross_mwh": 100.0,
                    "estimated_value_usd": 500.0,
                    "evidence_source": "test lmp",
                },
                {
                    "ba_a": "C",
                    "ba_b": "D",
                    "evidence_status": "structural_only",
                    "gross_mwh": 200.0,
                    "estimated_value_usd": 0.0,
                },
            ]
        },
    )

    claims = claims_from_congestion_report(path)

    assert claims[0].evidence_level == "measured_proxy"
    assert claims[0].value_usd == 500.0
    assert claims[1].evidence_level == "structural_only"
    assert claims[1].value_usd == 0.0


def test_outage_claims_include_total_and_top_states(tmp_path):
    path = _write_json(
        tmp_path / "outages.json",
        {
            "coverage_note": "test coverage",
            "rows_processed": 10,
            "first_timestamp": "2023-01-01 00:00:00",
            "last_timestamp": "2023-12-31 23:45:00",
            "total_customer_hours": 300.0,
            "states": [
                {
                    "state": "Texas",
                    "customer_hours": 200.0,
                    "hours_per_customer": 2.0,
                    "customer_hours_share": 0.666,
                }
            ],
        },
    )

    claims = claims_from_outage_report(path)

    assert claims[0].claim_id == "eaglei_total_customer_hours"
    assert claims[0].evidence_level == "measured"
    assert claims[1].geography == "Texas"
    assert claims[1].quantity == 2.0


def test_waste_ledger_exports(tmp_path):
    ledger = WasteLedger(
        claims=[
            WasteClaim(
                claim_id="measured",
                problem="curtailment",
                title="Measured claim",
                geography="CISO",
                evidence_level="measured",
                estimate_kind="energy",
                quantity=10.0,
                unit="MWh",
                value_usd=100.0,
            ),
            WasteClaim(
                claim_id="structural",
                problem="td_losses",
                title="Structural claim",
                geography="A-B",
                evidence_level="structural_only",
                estimate_kind="curvature",
                quantity=20.0,
                unit="MWh",
            ),
        ]
    )
    csv_path = tmp_path / "ledger.csv"
    json_path = tmp_path / "ledger.json"
    md_path = tmp_path / "ledger.md"
    html_path = tmp_path / "ledger.html"

    ledger.export_csv(csv_path)
    ledger.export_json(json_path)
    ledger.export_markdown(md_path)
    ledger.export_html(html_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["measured_value_usd"] == 100.0
    assert payload["counts_by_evidence"]["structural_only"] == 1
    assert "Grid Waste Ledger" in md_path.read_text(encoding="utf-8")
    assert "<!doctype html>" in html_path.read_text(encoding="utf-8")
    assert "measured" in csv_path.read_text(encoding="utf-8")


def test_build_waste_ledger_from_report_paths(tmp_path):
    ba = _write_json(
        tmp_path / "ba.json",
        {
            "accepted_corrections": 1,
            "before": {"abs_error_mwh": 10.0, "agreement_rate": 0.1},
            "after": {"abs_error_mwh": 4.0, "agreement_rate": 0.2},
        },
    )
    outage = _write_json(
        tmp_path / "outage.json",
        {
            "total_customer_hours": 100.0,
            "states": [],
        },
    )

    ledger = build_waste_ledger(
        ba_footprint_report=ba,
        outage_report=outage,
    )

    assert len(ledger.claims) == 2
    assert ledger.counts_by_evidence()["measured"] == 1
    assert ledger.counts_by_evidence()["validated_hypothesis"] == 1
