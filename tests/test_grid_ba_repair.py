# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for BA footprint repair proposals."""

import pytest

from core.category import Category

from domains.grid.ba_repair import (
    consensus_accounting,
    propose_ba_footprint_repair,
    write_repair_to_category,
)
from domains.grid.coherence import Section
from domains.grid.sources.base import PlantRecord


def test_consensus_accounting_averages_values_and_votes_ba():
    sections = [
        Section("a", {"p1": 100.0, "p2": 50.0}),
        Section("b", {"p1": 102.0, "p2": 50.0}),
    ]
    records = {
        "a": [
            PlantRecord("p1", balancing_authority="ERCO"),
            PlantRecord("p2", balancing_authority="CISO"),
        ],
        "b": [
            PlantRecord("p1", balancing_authority="ERCO"),
            PlantRecord("p2", balancing_authority="PJM"),
        ],
    }

    accounting, mapping, conflicts = consensus_accounting(sections, records)

    assert accounting.values["p1"] == pytest.approx(101.0)
    assert mapping["p1"] == "ERCO"
    assert mapping["p2"] in {"CISO", "PJM"}
    assert conflicts == ["p2"]


def test_repair_proposes_move_that_conserves_and_reduces_error():
    accounting = Section("accounting", {"p1": 100.0, "p2": 50.0, "p3": 200.0})
    entity_to_ba = {"p1": "ERCO", "p2": "ERCO", "p3": "CISO"}
    telemetry = Section("eia930", {"ERCO": 100.0, "CISO": 250.0})

    report = propose_ba_footprint_repair(
        telemetry,
        accounting,
        entity_to_ba,
        min_entity_mwh=1.0,
    )

    assert report.initial_abs_error_mwh == pytest.approx(100.0)
    assert report.repaired_abs_error_mwh == pytest.approx(0.0)
    assert len(report.moves) == 1
    move = report.moves[0]
    assert move.entity == "p2"
    assert (move.from_ba, move.to_ba) == ("ERCO", "CISO")
    assert move.confidence == pytest.approx(1.0)


def test_repair_respects_target_state_footprint_when_provided():
    accounting = Section("accounting", {"p1": 100.0, "p2": 50.0, "p3": 200.0})
    entity_to_ba = {"p1": "ERCO", "p2": "ERCO", "p3": "CISO"}
    telemetry = Section("eia930", {"ERCO": 100.0, "CISO": 250.0})

    report = propose_ba_footprint_repair(
        telemetry,
        accounting,
        entity_to_ba,
        entity_state={"p1": "TX", "p2": "TX", "p3": "CA"},
        ba_states={"ERCO": {"TX"}, "CISO": {"CA"}},
        min_entity_mwh=1.0,
    )

    assert report.moves == []
    assert report.repaired_abs_error_mwh == pytest.approx(report.initial_abs_error_mwh)


def test_repair_writeback_materializes_reviewable_candidates():
    report = propose_ba_footprint_repair(
        telemetry=Section("eia930", {"ERCO": 100.0, "CISO": 250.0}),
        accounting=Section("accounting", {"p1": 100.0, "p2": 50.0, "p3": 200.0}),
        entity_to_ba={"p1": "ERCO", "p2": "ERCO", "p3": "CISO"},
        min_entity_mwh=1.0,
    )
    category = Category(name="grid-repair-test", db_path=":memory:")

    write_repair_to_category(category, report)

    candidates = [
        m for m in category.morphisms_from("plant:p2")
        if m.name == "footprint_candidate"
    ]
    assert len(candidates) == 1
    assert candidates[0].target == "ba:CISO"
    assert candidates[0].metadata["from_ba"] == "ERCO"
