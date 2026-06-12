# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for static BA footprint dashboard exports."""

from domains.grid.ba_dashboard import (
    export_footprint_report_html,
    export_review_html,
    footprint_report_to_html,
    review_to_html,
)
from domains.grid.ba_footprint_crosswalk import build_ba_footprint_crosswalk
from domains.grid.ba_footprint_report import build_ba_footprint_report
from domains.grid.ba_repair import propose_ba_footprint_repair
from domains.grid.ba_review import ReviewDecision, apply_review_decisions
from domains.grid.coherence import Section


def _fixtures():
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
    decision = ReviewDecision(
        entity="p2",
        from_ba="ERCO",
        to_ba="CISO",
        status="accepted",
        reviewer="operator",
    )
    review = apply_review_decisions(
        crosswalk,
        {decision.key: decision},
        telemetry,
        accounting,
        mapping,
        tolerance=0.03,
    )
    reviewed_report = build_ba_footprint_report(
        telemetry,
        accounting,
        mapping,
        review.curated_crosswalk,
        tolerance=0.03,
    )
    return report, review, reviewed_report


def test_footprint_report_dashboard_contains_key_metrics():
    report, _, _ = _fixtures()

    html = footprint_report_to_html(report)

    assert "<!doctype html>" in html
    assert "BA Footprint Correction Dashboard" in html
    assert "BA agreement" in html
    assert "Absolute BA error" in html
    assert "Accepted Corrections" in html
    assert "p2" in html
    assert "ERCO" in html
    assert "CISO" in html


def test_review_dashboard_contains_approval_state():
    _, review, reviewed_report = _fixtures()

    html = review_to_html(review, reviewed_report=reviewed_report)

    assert "BA Footprint Review Dashboard" in html
    assert "Approved corrections" in html
    assert "operator" in html
    assert "approved-only report" in html


def test_dashboard_exports_html_files(tmp_path):
    report, review, reviewed_report = _fixtures()
    report_path = tmp_path / "footprint.html"
    review_path = tmp_path / "review.html"

    export_footprint_report_html(report, report_path)
    export_review_html(review, review_path, reviewed_report=reviewed_report)

    assert "Correction Dashboard" in report_path.read_text(encoding="utf-8")
    assert "Review Dashboard" in review_path.read_text(encoding="utf-8")
