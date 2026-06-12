# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for congestion evidence joined to flow bottlenecks."""

import csv
import json

import pytest

from domains.grid.congestion_evidence import (
    build_congestion_evidence_report,
    export_evidence_template_csv,
    load_congestion_evidence_csv,
)


def _flow_report_json(tmp_path):
    path = tmp_path / "flow.json"
    payload = {
        "bottlenecks": [
            {
                "ba_a": "PJM",
                "ba_b": "NYIS",
                "curvature": -0.10,
                "gross_mwh": 1000.0,
                "net_mwh": -900.0,
                "net_direction": "NYIS -> PJM",
                "gross_share": 0.1,
                "priority_score": 100.0,
            },
            {
                "ba_a": "BPAT",
                "ba_b": "NWMT",
                "curvature": -0.20,
                "gross_mwh": 500.0,
                "net_mwh": -300.0,
                "net_direction": "NWMT -> BPAT",
                "gross_share": 0.05,
                "priority_score": 80.0,
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_template_csv_contains_structural_fields(tmp_path):
    flow_path = _flow_report_json(tmp_path)
    template_path = tmp_path / "template.csv"

    export_evidence_template_csv(flow_path, template_path)

    with template_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["ba_a"] == "PJM"
    assert rows[0]["ba_b"] == "NYIS"
    assert "mean_price_spread_usd_mwh" in rows[0]
    assert "congestion_cost_usd" in rows[0]


def test_evidence_join_matches_ties_without_direction(tmp_path):
    flow_path = _flow_report_json(tmp_path)
    evidence_path = tmp_path / "evidence.csv"
    evidence_path.write_text(
        "ba_a,ba_b,evidence_source,congestion_cost_usd,hours_observed,notes\n"
        "NYIS,PJM,market-report,12345,100,verified cost\n",
        encoding="utf-8",
    )

    evidence = load_congestion_evidence_csv([evidence_path])
    report = build_congestion_evidence_report(flow_path, evidence)

    assert len(report.matched_claims) == 1
    assert len(report.measured_claims) == 1
    claim = report.ranked_claims()[0]
    assert claim.evidence_status == "measured_cost"
    assert claim.estimated_value_usd == pytest.approx(12345.0)
    assert claim.evidence.evidence_source == "market-report"


def test_price_spread_proxy_estimates_value_from_gross_flow(tmp_path):
    flow_path = _flow_report_json(tmp_path)
    evidence_path = tmp_path / "evidence.csv"
    evidence_path.write_text(
        "from_ba,to_ba,mean_price_spread_usd_mwh,max_price_spread_usd_mwh\n"
        "BPAT,NWMT,20,80\n",
        encoding="utf-8",
    )

    evidence = load_congestion_evidence_csv([evidence_path])
    report = build_congestion_evidence_report(flow_path, evidence)
    claim = report.ranked_claims()[0]

    assert claim.evidence_status == "price_spread_proxy"
    assert claim.estimated_value_usd == pytest.approx(10_000.0)
    assert report.total_estimated_value_usd == pytest.approx(10_000.0)


def test_congestion_evidence_exports_reports(tmp_path):
    flow_path = _flow_report_json(tmp_path)
    evidence_path = tmp_path / "evidence.csv"
    evidence_path.write_text(
        "ba_a,ba_b,evidence_source,congestion_cost_usd\n"
        "PJM,NYIS,cost-model,5000\n",
        encoding="utf-8",
    )
    report = build_congestion_evidence_report(
        flow_path,
        load_congestion_evidence_csv([evidence_path]),
    )
    csv_path = tmp_path / "report.csv"
    md_path = tmp_path / "report.md"
    json_path = tmp_path / "report.json"
    html_path = tmp_path / "report.html"

    report.export_csv(csv_path)
    report.export_markdown(md_path)
    report.export_json(json_path)
    report.export_html(html_path)

    assert "Congestion Evidence Report" in md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["measured_or_proxy_claims"] == 1
    assert payload["claims"][0]["estimated_value_usd"] == pytest.approx(5000.0)
    assert "<!doctype html>" in html_path.read_text(encoding="utf-8")
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["evidence_status"] == "measured_cost"


def test_structural_only_report_is_explicit(tmp_path):
    flow_path = _flow_report_json(tmp_path)

    report = build_congestion_evidence_report(flow_path)

    assert report.matched_claims == []
    assert report.measured_claims == []
    assert "no measured LMP/congestion evidence attached yet" in report.summary()
