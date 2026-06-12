# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the LBNL queue OPTIMUS factorization."""

import pytest

from domains.grid.queue_analysis import (
    OP,
    PROPOSED,
    WD,
    analyze_queue,
    build_queue_category,
)
from domains.grid.sources.lbnl_queue import (
    ACTIVE,
    OPERATIONAL,
    WITHDRAWN,
    QueueProject,
    _norm_status,
)


def _project(i, fuel, status, year=2015, mw=100.0, region="pjm"):
    return QueueProject(
        q_id=str(i), status=status, q_year=year, fuel=fuel,
        region=region, state="TX", mw=mw,
    )


def _engineered_queue():
    """gas completes 60%, solar completes 10%; 100 decided each."""
    projects = []
    i = 0
    for fuel, rate in (("gas", 0.6), ("solar", 0.1)):
        for k in range(100):
            status = OPERATIONAL if k < rate * 100 else WITHDRAWN
            projects.append(_project(i, fuel, status))
            i += 1
    return projects


def test_status_normalization():
    assert _norm_status("Operational") == OPERATIONAL
    assert _norm_status("IA Executed - Withdrawn") == WITHDRAWN
    assert _norm_status("Active") == ACTIVE


def test_build_queue_category_rates():
    cat = build_queue_category(_engineered_queue(), min_cohort=30)
    gas_completes = next(
        m for m in cat.morphisms_to(OP)
        if m.source == "fuel:gas" and m.name == "completes"
    )
    assert gas_completes.confidence == pytest.approx(0.6)
    direct = next(
        m for m in cat.morphisms_to(OP)
        if m.source == PROPOSED and m.name == "completes"
    )
    assert direct.confidence == pytest.approx(0.35)  # 70/200


def test_small_cohorts_carry_no_morphism():
    projects = _engineered_queue()
    projects.append(_project(999, "geothermal", OPERATIONAL))
    cat = build_queue_category(projects, min_cohort=30)
    assert not any(
        m.source == "fuel:geothermal" for m in cat.morphisms_to(OP)
    )


def test_censored_projects_excluded():
    projects = _engineered_queue()
    projects += [_project(1000 + k, "gas", ACTIVE) for k in range(50)]
    cat = build_queue_category(projects, min_cohort=30)
    gas = next(
        m for m in cat.morphisms_to(OP)
        if m.source == "fuel:gas" and m.name == "completes"
    )
    assert gas.confidence == pytest.approx(0.6)  # active projects don't dilute


def test_optimus_discovers_high_completion_cohort():
    report = analyze_queue(_engineered_queue(), min_cohort=30)
    assert report.overall_completion == pytest.approx(0.35)
    # the best mediator of completion is the gas cohort...
    top_cohort, top_rate, _ = report.operational_intermediates[0]
    assert top_cohort == "fuel:gas"
    assert top_rate == pytest.approx(0.6)
    # ...and the best mediator of withdrawal is solar
    top_wd, wd_rate, _ = report.withdrawal_intermediates[0]
    assert top_wd == "fuel:solar"
    assert wd_rate == pytest.approx(0.9)
    # OPTIMUS factorization surfaces an improving intermediate
    assert "fuel:gas" in report.optimus_discovered_op
