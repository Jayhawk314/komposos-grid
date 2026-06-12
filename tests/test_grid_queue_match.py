# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for queue-to-bottleneck matching."""

import pytest

from domains.grid.queue_match import (
    build_ba_state_footprint,
    match_queue_to_bottlenecks,
    project_role_and_potential,
    region_compatible,
    state_ba_weight,
)
from domains.grid.sources.base import PlantRecord
from domains.grid.sources.lbnl_queue import QueueProject


def _plant(ba, state, gen):
    return PlantRecord(plant_id=f"{ba}{state}", balancing_authority=ba,
                       state=state, net_generation_mwh=gen)


def _footprint():
    # AR generation: 70% MISO, 30% SWPP; MS: 100% MISO; OK: 100% SWPP
    return build_ba_state_footprint([
        _plant("MISO", "AR", 7_000_000.0),
        _plant("SWPP", "AR", 3_000_000.0),
        _plant("MISO", "MS", 5_000_000.0),
        _plant("SWPP", "OK", 8_000_000.0),
    ])


def _claim(**over):
    base = {
        "ba_a": "MISO", "ba_b": "SWPP",
        "evidence_status": "lmp_component_proxy",
        "gross_mwh": 4_000_000.0,
        "net_direction": "SWPP -> MISO",  # MISO imports
        "mean_congestion_component_spread_usd_mwh": 5.0,
    }
    base.update(over)
    return base


def _project(q_id, fuel, state, region, mw, status="active"):
    return QueueProject(q_id=q_id, status=status, q_year=2020, fuel=fuel,
                        region=region, state=state, mw=mw)


def test_footprint_and_weights():
    fp = _footprint()
    assert fp["MISO"]["AR"] == pytest.approx(7_000_000.0)
    assert state_ba_weight(fp, "AR", "MISO") == pytest.approx(0.7)
    assert state_ba_weight(fp, "AR", "SWPP") == pytest.approx(0.3)
    assert state_ba_weight(fp, "OK", "MISO") == 0.0


def test_roles_and_potential():
    role, mwh = project_role_and_potential(_project("1", "battery", "AR", "miso", 100))
    assert role == "storage" and mwh == pytest.approx(120_000)
    role, mwh = project_role_and_potential(_project("2", "solar", "AR", "miso", 100))
    assert role == "generation" and mwh == pytest.approx(100 * 0.25 * 8760)


def test_region_compatibility():
    assert region_compatible("miso", "MISO")
    assert not region_compatible("miso", "SWPP")
    assert region_compatible("west", "BPAT")
    assert not region_compatible("west", "CISO")


def test_matching_sides_and_value():
    projects = [
        # generation in MISO-side AR -> matches importing side (MISO)
        _project("gen1", "solar", "AR", "miso", 200),
        # storage in SPP-side OK -> matches exporting side (SWPP)
        _project("st1", "battery", "OK", "spp", 100),
        # generation in OK/spp: wrong side (gen goes to importer MISO) -> no match
        _project("gen2", "solar", "OK", "spp", 200),
        # withdrawn project still recorded under withdrawn totals
        _project("gone", "wind", "MS", "miso", 300, status="withdrawn"),
    ]
    report = match_queue_to_bottlenecks([_claim()], projects, _footprint())
    (tie,) = report.ties
    ids = {m.q_id for m in tie.matches}
    assert ids == {"gen1", "st1", "gone"}

    gen1 = next(m for m in tie.matches if m.q_id == "gen1")
    expected_mwh = 200 * 0.25 * 8760 * 0.7  # CF x state weight
    assert gen1.relief_mwh == pytest.approx(expected_mwh)
    assert gen1.relief_value_usd == pytest.approx(expected_mwh * 5.0)
    assert gen1.side == "MISO"

    st1 = next(m for m in tie.matches if m.q_id == "st1")
    assert st1.side == "SWPP" and st1.role == "storage"

    n_act, gw_act, _ = tie.total("active")
    n_wd, _, _ = tie.total("withdrawn")
    assert (n_act, n_wd) == (2, 1)
    assert gw_act == pytest.approx(0.3)


def test_relief_capped_at_tie_gross():
    huge = _project("big", "nuclear", "MS", "miso", 5000)  # 39.4 TWh potential
    report = match_queue_to_bottlenecks([_claim()], [huge], _footprint())
    (tie,) = report.ties
    assert tie.matches[0].relief_mwh == pytest.approx(4_000_000.0)
    _, _, val = tie.total("active")
    assert val == pytest.approx(4_000_000.0 * 5.0)  # also <= tie cap


def test_unmeasured_tie_carries_no_dollars():
    claim = _claim(mean_congestion_component_spread_usd_mwh=None,
                   evidence_status="structural_only")
    report = match_queue_to_bottlenecks(
        [claim], [_project("g", "solar", "AR", "miso", 100)], _footprint()
    )
    (tie,) = report.ties
    assert tie.matches and tie.matches[0].relief_value_usd == 0.0
    assert tie.tie_value_cap_usd == 0.0
