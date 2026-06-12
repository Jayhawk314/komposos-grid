# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the grid domain: ingestion + sheaf coherence check."""

import pytest

from core.category import Category

from domains.grid.coherence import (
    CONTRADICT,
    GLUE,
    GridCoherenceChecker,
    Section,
    ba_mapping_from_records,
    is_valid_ba_code,
    pushforward,
    relative_discrepancy,
    sections_from_sources,
)
from domains.grid.crosswalk import discover_crosswalk, write_to_category
from domains.grid.ingest import GridCategoryBuilder
from domains.grid.sources.base import PlantRecord
from domains.grid.sources.synthetic import make_fleet, make_synthetic_pair, SyntheticSource


# ---------------------------------------------------------------- coherence

def test_identical_sections_glue():
    values = {"1": 100.0, "2": 200.0, "3": 300.0}
    report = GridCoherenceChecker(tolerance=0.01).check(
        [Section("a", dict(values)), Section("b", dict(values))]
    )
    assert report.is_coherent
    (pair,) = report.pairs
    assert pair.overlap_size == 3
    assert pair.agreement_rate == 1.0
    assert all(v.verdict == GLUE for v in pair.verdicts)


def test_contradiction_detected_and_localized():
    sec_a = Section("a", {"1": 100.0, "2": 200.0})
    sec_b = Section("b", {"1": 100.5, "2": 600.0})  # plant 2 is 3x off
    report = GridCoherenceChecker(tolerance=0.01).check([sec_a, sec_b])
    assert not report.is_coherent
    contradictions = report.pairs[0].by_verdict(CONTRADICT)
    assert [v.plant_id for v in contradictions] == ["2"]


def test_disjoint_sections_are_vacuously_coherent():
    report = GridCoherenceChecker().check(
        [Section("a", {"1": 100.0}), Section("b", {"2": 50.0})]
    )
    assert report.is_coherent
    assert report.pairs[0].overlap_size == 0
    assert report.pairs[0].agreement_rate == 1.0


def test_synthetic_pair_recovers_planted_contradictions():
    src_a, src_b, planted = make_synthetic_pair(
        n_plants=40, noise=0.005, n_contradictions=4
    )
    report = GridCoherenceChecker(tolerance=0.02).check(
        sections_from_sources([src_a, src_b])
    )
    found = {
        v.plant_id for v in report.pairs[0].by_verdict(CONTRADICT)
    }
    assert found == set(planted)


def test_relative_discrepancy_edge_cases():
    assert relative_discrepancy(0.0, 0.0) == 0.0
    assert relative_discrepancy(100.0, 100.0) == 0.0
    assert relative_discrepancy(100.0, 0.0) == 1.0


def test_three_sections_pairwise():
    values = {"1": 100.0}
    report = GridCoherenceChecker().check(
        [Section(s, dict(values)) for s in ("a", "b", "c")]
    )
    assert len(report.pairs) == 3  # all pairs checked
    assert report.is_coherent


# ---------------------------------------------------------------- pushforward / BA level

def test_pushforward_sums_fibers_and_drops_unmapped():
    section = Section("x", {"1": 10.0, "2": 20.0, "3": 5.0, "4": 7.0})
    mapping = {"1": "ERCO", "2": "ERCO", "3": "CISO"}  # plant 4 unmapped
    pushed = pushforward(section, mapping, source="x@ba")
    assert pushed.source == "x@ba"
    assert pushed.values == {"ERCO": 30.0, "CISO": 5.0}


def test_ba_mapping_from_records_skips_missing():
    fleet = make_fleet(n_plants=5, seed=2)
    fleet[0].balancing_authority = ""
    fleet[1].balancing_authority = "State-Fuel Level Increment"
    mapping = ba_mapping_from_records(fleet)
    assert fleet[0].plant_id not in mapping
    assert fleet[1].plant_id not in mapping
    assert len(mapping) == 3


def test_is_valid_ba_code_rejects_aggregate_labels():
    assert is_valid_ba_code("BPAT")
    assert is_valid_ba_code("NA - PR")
    assert not is_valid_ba_code("State-Fuel Level Increment")
    assert not is_valid_ba_code("nan")


def test_ba_level_coherence_against_independent_section():
    fleet = make_fleet(n_plants=20, seed=3)
    plant_section = Section(
        "plants", {r.plant_id: r.net_generation_mwh for r in fleet}
    )
    mapping = ba_mapping_from_records(fleet)
    pushed = pushforward(plant_section, mapping, source="plants@ba")

    # Independent BA-level section agreeing within 2%, one BA off by 50%
    telemetry = {ba: v * 1.02 for ba, v in pushed.values.items()}
    bad_ba = next(iter(telemetry))
    telemetry[bad_ba] = pushed.values[bad_ba] * 1.5

    checker = GridCoherenceChecker(tolerance=0.05, key_namer=lambda c: f"ba:{c}")
    report = checker.check([pushed, Section("telemetry", telemetry)])
    contradictions = report.pairs[0].by_verdict(CONTRADICT)
    assert [v.plant_id for v in contradictions] == [bad_ba]


def test_ba_writeback_uses_ba_namer():
    pushed = Section("plants@ba", {"ERCO": 100.0})
    telemetry = Section("telemetry", {"ERCO": 200.0})
    cat = Category(name="grid-test", db_path=":memory:")
    checker = GridCoherenceChecker(
        category=cat, tolerance=0.05, key_namer=lambda c: f"ba:{c}"
    )
    checker.check([pushed, telemetry])
    disputes = [
        m for m in cat.morphisms_from("source:plants@ba") if m.name == "disputes"
    ]
    assert [m.target for m in disputes] == ["ba:ERCO"]


# ---------------------------------------------------------------- sheaf audit

def test_probe_single_ratio_edge_is_satisfiable():
    from komposos_wesys.validation.thermodynamic_probe import ThermodynamicSheaf

    sheaf = ThermodynamicSheaf()
    sheaf.add_flow("a", "b", efficiency=0.5)
    audit = sheaf.audit()
    assert audit.energy_leak == pytest.approx(0.0, abs=1e-10)
    assert audit.assignment == audit.asefficiencyment


def test_sheaf_audit_stable_under_global_calibration():
    from domains.grid.sheaf_audit import sheaf_audit

    # Source b reports exactly 0.97x source a everywhere: a pure gauge
    # difference, which must NOT count as an obstruction.
    values = {str(i): 1000.0 * (i + 1) for i in range(20)}
    sections = [
        Section("a", values),
        Section("b", {k: v * 0.97 for k, v in values.items()}),
    ]
    audit = sheaf_audit(sections)
    assert audit.stable
    assert audit.n_edges == 20
    assert audit.calibration["b"] == pytest.approx(1 / 0.97)
    assert audit.fused_values["3"].value == pytest.approx(values["3"])


def test_sheaf_audit_localizes_obstruction():
    from domains.grid.sheaf_audit import sheaf_audit

    values = {str(i): 1000.0 for i in range(20)}
    perturbed = dict(values)
    perturbed["7"] = 400.0  # one entity off by 2.5x
    audit = sheaf_audit([Section("a", values), Section("b", perturbed)])
    assert not audit.stable
    assert audit.offenders[0].entity == "7"


def test_sheaf_audit_skips_nonpositive_values():
    from domains.grid.sheaf_audit import sheaf_audit

    audit = sheaf_audit(
        [Section("a", {"1": 100.0, "2": -5.0}), Section("b", {"1": 100.0, "2": 50.0})]
    )
    assert audit.n_edges == 1
    assert audit.n_skipped == 1


# ---------------------------------------------------------------- crosswalk

def _rec(pid, gen, state="TX", source="x"):
    return PlantRecord(
        plant_id=pid, state=state, net_generation_mwh=gen, source=source
    )


def _split_facility_fixture():
    """Source A merges blocks under ID 100; source B reports them split."""
    a = [_rec("100", 300_000.0), _rec("5", 50_000.0)]
    b = [
        _rec("100", 100_000.0),   # block 1 under the shared ID
        _rec("101", 120_000.0),   # block 2, B-only
        _rec("102", 80_000.0),    # block 3, B-only
        _rec("5", 50_000.0),
    ]
    return SyntheticSource("a", a), SyntheticSource("b", b)


def _check(sources, tolerance=0.01, category=None):
    checker = GridCoherenceChecker(category=category, tolerance=tolerance)
    return checker, checker.check(sections_from_sources(sources))


def test_crosswalk_reconciles_split_facility():
    src_a, src_b = _split_facility_fixture()
    checker, report = _check([src_a, src_b])
    assert not report.is_coherent  # 300k vs 100k on ID 100

    crosswalk = discover_crosswalk(
        report,
        {s.source: s for s in sections_from_sources([src_a, src_b])},
        {"a": src_a.load(), "b": src_b.load()},
        tolerance=0.01,
    )
    (merge,) = crosswalk.merges
    assert merge.facility_id == "100"
    assert set(merge.members) == {"100", "101", "102"}
    assert merge.post_discrepancy <= 0.01

    facility_report = checker.check(
        crosswalk.apply_all(sections_from_sources([src_a, src_b]))
    )
    assert facility_report.is_coherent


def test_crosswalk_respects_state_boundaries():
    src_a, src_b = _split_facility_fixture()
    # Move the candidate blocks to another state: no merge may use them
    for rec in src_b.load():
        if rec.plant_id in ("101", "102"):
            rec.state = "CA"
    _, report = _check([src_a, src_b])
    crosswalk = discover_crosswalk(
        report,
        {s.source: s for s in sections_from_sources([src_a, src_b])},
        {"a": src_a.load(), "b": src_b.load()},
        tolerance=0.01,
    )
    assert crosswalk.merges == []


def test_crosswalk_rejects_unreconcilable_contradiction():
    # B misreports plant 7 threefold; there are no residuals to explain it
    src_a = SyntheticSource("a", [_rec("7", 100_000.0)])
    src_b = SyntheticSource("b", [_rec("7", 300_000.0)])
    _, report = _check([src_a, src_b])
    crosswalk = discover_crosswalk(
        report,
        {s.source: s for s in sections_from_sources([src_a, src_b])},
        {"a": src_a.load(), "b": src_b.load()},
        tolerance=0.01,
    )
    assert crosswalk.merges == []
    assert crosswalk.facility_of("7") == "7"


def test_crosswalk_writes_facility_structure():
    src_a, src_b = _split_facility_fixture()
    cat = Category(name="grid-test", db_path=":memory:")
    GridCategoryBuilder(cat).add_sources([src_a, src_b])
    _, report = _check([src_a, src_b])
    crosswalk = discover_crosswalk(
        report,
        {s.source: s for s in sections_from_sources([src_a, src_b])},
        {"a": src_a.load(), "b": src_b.load()},
        tolerance=0.01,
    )
    write_to_category(cat, crosswalk)

    assert cat.get("facility:100") is not None
    members = {
        m.source for m in cat.morphisms_to("facility:100") if m.name == "part_of"
    }
    assert members == {"plant:100", "plant:101", "plant:102"}


# ---------------------------------------------------------------- ingestion

def test_ingest_builds_expected_structure():
    fleet = make_fleet(n_plants=10, seed=1)
    cat = Category(name="grid-test", db_path=":memory:")
    counts = GridCategoryBuilder(cat).add_source(SyntheticSource("test_src", fleet))

    assert counts["plants_created"] == 10
    assert cat.get("source:test_src") is not None
    plant = f"plant:{fleet[0].plant_id}"
    assert cat.get(plant) is not None
    # structural morphisms exist: in_ba, in_state, uses_fuel + reports
    names = {m.name for m in cat.morphisms_from(plant)}
    assert {"in_ba", "in_state", "uses_fuel"} <= names
    reports = [m for m in cat.morphisms_from("source:test_src") if m.name == "reports"]
    assert len(reports) == 10


def test_coherence_writes_back_to_category():
    src_a, src_b, planted = make_synthetic_pair(n_plants=30, n_contradictions=2)
    cat = Category(name="grid-test", db_path=":memory:")
    builder = GridCategoryBuilder(cat)
    builder.add_sources([src_a, src_b])

    report = GridCoherenceChecker(category=cat, tolerance=0.02).check(
        sections_from_sources([src_a, src_b])
    )

    coheres = [
        m for m in cat.morphisms_from("source:synthetic_a")
        if m.name == "coheres_with"
    ]
    assert len(coheres) == 1
    assert coheres[0].confidence == pytest.approx(report.pairs[0].agreement_rate)

    disputes = {
        m.target for m in cat.morphisms_from("source:synthetic_a")
        if m.name == "disputes"
    }
    assert disputes == {f"plant:{pid}" for pid in planted}
