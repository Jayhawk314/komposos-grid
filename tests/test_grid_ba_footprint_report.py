# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for before/after BA footprint proof reports."""

import json

import pytest

from domains.grid.ba_footprint_crosswalk import build_ba_footprint_crosswalk
from domains.grid.ba_footprint_report import build_ba_footprint_report
from domains.grid.ba_repair import propose_ba_footprint_repair
from domains.grid.coherence import Section


def _report_fixture():
    accounting = Section("accounting", {"p1": 100.0, "p2": 50.0, "p3": 200.0})
    telemetry = Section("eia930", {"ERCO": 100.0, "CISO": 250.0})
    mapping = {"p1": "ERCO", "p2": "ERCO", "p3": "CISO"}
    repair = propose_ba_footprint_repair(
        telemetry,
        accounting,
        mapping,
        min_entity_mwh=1.0,
    )
    crosswalk = build_ba_footprint_crosswalk(repair, telemetry, accounting, mapping)
    report = build_ba_footprint_report(
        telemetry,
        accounting,
        mapping,
        crosswalk,
        tolerance=0.03,
    )
    return report


def test_report_computes_before_after_coherence_and_error():
    report = _report_fixture()

    assert report.before_contradictions == 2
    assert report.after_contradictions == 0
    assert report.contradiction_reduction == 2
    assert report.before_agreement_rate == pytest.approx(0.0)
    assert report.after_agreement_rate == pytest.approx(1.0)
    assert report.crosswalk.before_score.abs_error_mwh == pytest.approx(100.0)
    assert report.crosswalk.after_score.abs_error_mwh == pytest.approx(0.0)
    assert "contradictions: 2 -> 0" in report.summary()


def test_report_markdown_contains_accepted_rejected_and_unresolved_sections():
    report = _report_fixture()

    markdown = report.to_markdown()

    assert "# BA Footprint Correction Report" in markdown
    assert "## Accepted Corrections" in markdown
    assert "| p2 |" in markdown
    assert "## Rejected Candidates" in markdown
    assert "## Remaining Largest BA Deltas" in markdown


def test_report_exports_markdown_and_json(tmp_path):
    report = _report_fixture()
    md_path = tmp_path / "report.md"
    json_path = tmp_path / "report.json"

    report.export_markdown(md_path)
    report.export_json(json_path)

    assert "BA Footprint Correction Report" in md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["before"]["contradictions"] == 2
    assert payload["after"]["contradictions"] == 0
    assert payload["accepted"][0]["entity"] == "p2"
