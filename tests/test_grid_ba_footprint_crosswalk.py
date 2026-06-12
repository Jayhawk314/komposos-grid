# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for validated BA footprint crosswalks."""

import csv
import json

import pytest

from core.category import Category

from domains.grid.ba_footprint_crosswalk import (
    build_ba_footprint_crosswalk,
    interchange_neighbors_from_ties,
    score_ba_mapping,
    write_crosswalk_to_category,
)
from domains.grid.ba_repair import BARepairReport, EntityMove, propose_ba_footprint_repair
from domains.grid.coherence import Section
from domains.grid.sources.base import PlantRecord


def _fixture():
    accounting = Section("accounting", {"p1": 100.0, "p2": 50.0, "p3": 200.0})
    telemetry = Section("eia930", {"ERCO": 100.0, "CISO": 250.0})
    mapping = {"p1": "ERCO", "p2": "ERCO", "p3": "CISO"}
    return telemetry, accounting, mapping


def test_score_ba_mapping_reports_total_error_and_tolerance_count():
    telemetry, accounting, mapping = _fixture()

    score = score_ba_mapping(telemetry, accounting, mapping, tolerance=0.05)

    assert score.abs_error_mwh == pytest.approx(100.0)
    assert score.max_abs_delta_mwh == pytest.approx(50.0)
    assert score.outside_tolerance == 2


def test_crosswalk_promotes_validated_moves_and_applies_mapping():
    telemetry, accounting, mapping = _fixture()
    report = propose_ba_footprint_repair(
        telemetry,
        accounting,
        mapping,
        min_entity_mwh=1.0,
    )

    crosswalk = build_ba_footprint_crosswalk(report, telemetry, accounting, mapping)

    assert len(crosswalk.accepted) == 1
    assert crosswalk.after_score.abs_error_mwh == pytest.approx(0.0)
    assert crosswalk.apply_mapping(mapping)["p2"] == "CISO"
    pushed = crosswalk.apply(accounting, mapping)
    assert pushed.values == {"ERCO": 100.0, "CISO": 250.0}


def test_crosswalk_rejects_candidate_outside_target_state_footprint():
    telemetry, accounting, mapping = _fixture()
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

    assert crosswalk.accepted == []
    assert len(crosswalk.rejected) == 1
    assert "target BA has no observed TX footprint" in crosswalk.rejected[0].reasons


def test_crosswalk_can_require_observed_interchange_tie():
    telemetry, accounting, mapping = _fixture()
    report = propose_ba_footprint_repair(
        telemetry,
        accounting,
        mapping,
        min_entity_mwh=1.0,
    )

    rejected = build_ba_footprint_crosswalk(
        report,
        telemetry,
        accounting,
        mapping,
        interchange_neighbors={"ERCO": {"PJM"}, "PJM": {"ERCO"}},
    )
    accepted = build_ba_footprint_crosswalk(
        report,
        telemetry,
        accounting,
        mapping,
        interchange_neighbors={"ERCO": {"CISO"}, "CISO": {"ERCO"}},
    )

    assert rejected.accepted == []
    assert "source and target BAs lack observed interchange tie" in rejected.rejected[0].reasons
    assert len(accepted.accepted) == 1


def test_interchange_neighbors_from_ties_builds_undirected_adjacency():
    class Tie:
        def __init__(self, a, b):
            self.ba_a = a
            self.ba_b = b

    neighbors = interchange_neighbors_from_ties([Tie("A", "B"), Tie("B", "C")])

    assert neighbors == {"A": {"B"}, "B": {"A", "C"}, "C": {"B"}}


def test_crosswalk_writeback_materializes_accepted_corrections():
    telemetry, accounting, mapping = _fixture()
    report = propose_ba_footprint_repair(
        telemetry,
        accounting,
        mapping,
        min_entity_mwh=1.0,
    )
    crosswalk = build_ba_footprint_crosswalk(report, telemetry, accounting, mapping)
    category = Category(name="ba-footprint-test", db_path=":memory:")

    write_crosswalk_to_category(category, crosswalk)

    corrections = [
        m for m in category.morphisms_from("plant:p2")
        if m.name == "footprint_correction"
    ]
    assert len(corrections) == 1
    assert corrections[0].target == "ba:CISO"
    assert corrections[0].metadata["validated_improvement_mwh"] == pytest.approx(100.0)


def test_crosswalk_exports_review_files(tmp_path):
    telemetry, accounting, mapping = _fixture()
    report = propose_ba_footprint_repair(
        telemetry,
        accounting,
        mapping,
        min_entity_mwh=1.0,
    )
    crosswalk = build_ba_footprint_crosswalk(report, telemetry, accounting, mapping)
    records = {"accounting": [PlantRecord("p2", name="Plant Two")]}
    sections = [accounting]
    csv_path = tmp_path / "ba_repair.csv"
    json_path = tmp_path / "ba_repair.json"

    crosswalk.export_csv(csv_path, records, sections)
    crosswalk.export_json(json_path, records, sections)

    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["status"] == "accepted"
    assert rows[0]["name"] == "Plant Two"
    assert rows[0]["accounting_mwh"] == "50.0"

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["after"]["abs_error_mwh"] == pytest.approx(0.0)
    assert payload["candidates"][0]["entity"] == "p2"
