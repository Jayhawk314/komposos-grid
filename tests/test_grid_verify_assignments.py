# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for Dual-Engine verification of plant->BA assignments."""

from domains.grid.flow_geometry import TieLine
from domains.grid.sources.base import PlantRecord
from domains.grid.verify_assignments import (
    build_verification_category,
    verify_assignments,
)


def _fleet():
    recs = []
    for i in range(6):
        recs.append(
            PlantRecord(plant_id=f"a{i}", balancing_authority="AAA",
                        net_generation_mwh=1000.0)
        )
        recs.append(
            PlantRecord(plant_id=f"b{i}", balancing_authority="BBB",
                        net_generation_mwh=1000.0)
        )
    return recs


def test_build_verification_category_samples_and_ties():
    cat = build_verification_category(
        _fleet(), ["AAA", "BBB"],
        ties=[TieLine("AAA", "BBB", 1e6, 1e5)],
        max_plants_per_ba=4,
    )
    in_ba = [m for m in cat.morphisms() if m.name == "in_ba"]
    assert len(in_ba) == 8  # 4 sampled per BA
    ties = [m for m in cat.morphisms() if m.name == "interchange"]
    assert len(ties) == 2  # both directions


def test_registered_assignments_agree():
    cat = build_verification_category(_fleet(), ["AAA", "BBB"])
    report = verify_assignments(cat, ["AAA"], ["BBB"], queries_per_ba=3)
    for row in report.results:
        # every recorded assignment is logically + structurally supported
        assert row.registered_deltas.get("AGREE", 0) == sum(
            row.registered_deltas.values()
        )


def test_counterfactual_leakiness_requires_ties():
    # Without ties: no path from plant to the other BA -> no counterfactuals
    cat = build_verification_category(_fleet(), ["AAA", "BBB"])
    report = verify_assignments(cat, ["AAA"], ["BBB"], queries_per_ba=3)
    assert all(r.counterfactual_total == 0 for r in report.results)

    # With ties: counterfactual queries run, and CAT finds the 2-hop path
    cat2 = build_verification_category(
        _fleet(), ["AAA", "BBB"], ties=[TieLine("AAA", "BBB", 1e6, 1e5)]
    )
    report2 = verify_assignments(cat2, ["AAA"], ["BBB"], queries_per_ba=3)
    leaky = [r for r in report2.results if r.counterfactual_total > 0]
    assert leaky
    assert report2.group_leakiness("disputed") > 0


def test_leakiness_scales_with_tie_vs_generation():
    # AAA: tiny fleet (6 MWh), BBB: huge fleet (6M MWh), same physical tie.
    recs = []
    for i in range(6):
        recs.append(PlantRecord(plant_id=f"a{i}", balancing_authority="AAA",
                                net_generation_mwh=1.0))
        recs.append(PlantRecord(plant_id=f"b{i}", balancing_authority="BBB",
                                net_generation_mwh=1_000_000.0))
    tie = TieLine("AAA", "BBB", gross_mwh=600.0, net_mwh=100.0)
    cat = build_verification_category(recs, ["AAA", "BBB"], ties=[tie])
    report = verify_assignments(cat, ["AAA"], ["BBB"], queries_per_ba=3)

    # AAA's tie dwarfs its generation -> leaky; BBB's tie is negligible.
    assert report.group_leakiness("disputed") > 0.9
    assert report.group_leakiness("control") < 0.01


def test_system3_records_episodes():
    cat = build_verification_category(
        _fleet(), ["AAA", "BBB"], ties=[TieLine("AAA", "BBB", 1e6, 1e5)]
    )
    report = verify_assignments(cat, ["AAA"], ["BBB"], queries_per_ba=2)
    assert report.n_episodes > 0
    assert isinstance(report.system3_report, str)
