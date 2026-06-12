# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for human review of BA footprint correction candidates."""

import csv
import json

import pytest

from core.category import Category

from domains.grid.ba_footprint_crosswalk import build_ba_footprint_crosswalk
from domains.grid.ba_repair import (
    BARepairReport,
    EntityMove,
    propose_ba_footprint_repair,
)
from domains.grid.ba_review import (
    ReviewDecision,
    apply_review_decisions,
    export_review_template_csv,
    export_review_template_json,
    load_review_decisions,
    review_key,
    write_review_to_category,
)
from domains.grid.coherence import Section
from domains.grid.sources.base import PlantRecord


def _fixture():
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
    return telemetry, accounting, mapping, crosswalk


def test_review_template_defaults_machine_accepts_to_needs_review(tmp_path):
    telemetry, accounting, _, crosswalk = _fixture()
    csv_path = tmp_path / "review.csv"
    json_path = tmp_path / "review.json"
    records = {"accounting": [PlantRecord("p2", name="Plant Two")]}

    export_review_template_csv(crosswalk, csv_path, records, [accounting])
    export_review_template_json(crosswalk, json_path, records, [accounting])

    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["review_status"] == "needs_review"
    assert rows[0]["machine_status"] == "accepted"
    assert rows[0]["name"] == "Plant Two"
    assert rows[0]["accounting_mwh"] == "50.0"

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["candidates"][0]["review_status"] == "needs_review"
    assert payload["candidates"][0]["entity"] == "p2"
    assert telemetry.source == "eia930"


def test_review_decisions_apply_only_explicit_acceptances(tmp_path):
    telemetry, accounting, mapping, crosswalk = _fixture()
    csv_path = tmp_path / "review.csv"
    export_review_template_csv(crosswalk, csv_path)

    # No explicit approval means a machine-accepted candidate is still withheld.
    empty_review = apply_review_decisions(
        crosswalk,
        load_review_decisions(csv_path),
        telemetry,
        accounting,
        mapping,
    )
    assert empty_review.approved == []
    assert empty_review.curated_crosswalk.after_score.abs_error_mwh == pytest.approx(
        100.0
    )

    rows = list(csv.DictReader(csv_path.open(newline="", encoding="utf-8")))
    rows[0]["review_status"] = "accepted"
    rows[0]["reviewer"] = "grid-review"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    reviewed = apply_review_decisions(
        crosswalk,
        load_review_decisions(csv_path),
        telemetry,
        accounting,
        mapping,
    )

    assert len(reviewed.approved) == 1
    assert reviewed.approved[0].decision.reviewer == "grid-review"
    assert reviewed.curated_crosswalk.apply_mapping(mapping)["p2"] == "CISO"
    assert reviewed.curated_crosswalk.after_score.abs_error_mwh == pytest.approx(0.0)
    assert "approved 1 of 1 candidates" in reviewed.summary()


def test_review_cannot_apply_machine_rejected_candidate_without_override():
    telemetry, accounting, mapping, _ = _fixture()
    move = EntityMove(
        entity="p2",
        from_ba="ERCO",
        to_ba="CISO",
        value_mwh=50.0,
        improvement_mwh=100.0,
        confidence=1.0,
        state="TX",
    )
    report = BARepairReport(
        reference_source="accounting",
        n_entities=3,
        initial_abs_error_mwh=100.0,
        repaired_abs_error_mwh=0.0,
        remaining_delta_mwh={},
        moves=[move],
    )
    crosswalk = build_ba_footprint_crosswalk(
        report,
        telemetry,
        accounting,
        mapping,
        entity_state={"p2": "TX"},
        ba_states={"ERCO": {"TX"}, "CISO": {"CA"}},
    )
    decisions = {
        review_key("p2", "ERCO", "CISO"): ReviewDecision(
            entity="p2",
            from_ba="ERCO",
            to_ba="CISO",
            status="accepted",
            note="external footprint document supplied",
        )
    }

    blocked = apply_review_decisions(
        crosswalk,
        decisions,
        telemetry,
        accounting,
        mapping,
    )
    overridden = apply_review_decisions(
        crosswalk,
        decisions,
        telemetry,
        accounting,
        mapping,
        allow_machine_rejected=True,
    )

    assert blocked.approved == []
    assert "machine-rejected candidate needs override evidence" in (
        blocked.needs_review[0].review_reasons
    )
    assert len(overridden.approved) == 1
    assert overridden.curated_crosswalk.after_score.abs_error_mwh == pytest.approx(0.0)


def test_review_exports_and_writes_category_evidence(tmp_path):
    telemetry, accounting, mapping, crosswalk = _fixture()
    decision = ReviewDecision(
        entity="p2",
        from_ba="ERCO",
        to_ba="CISO",
        status="accepted",
        reviewer="operator",
        evidence="footprint-doc-1",
    )
    reviewed = apply_review_decisions(
        crosswalk,
        {decision.key: decision},
        telemetry,
        accounting,
        mapping,
    )
    category = Category(name="ba-review-test", db_path=":memory:")
    csv_path = tmp_path / "reviewed.csv"
    json_path = tmp_path / "reviewed.json"

    reviewed.export_csv(csv_path)
    reviewed.export_json(json_path)
    write_review_to_category(category, reviewed)

    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["applied"] == "true"
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["approved"] == 1
    assert payload["reviewed_after"]["abs_error_mwh"] == pytest.approx(0.0)

    morphisms = [
        m for m in category.morphisms_from("plant:p2")
        if m.name == "reviewed_footprint_correction"
    ]
    assert len(morphisms) == 1
    assert morphisms[0].target == "ba:CISO"
    assert morphisms[0].metadata["reviewer"] == "operator"
