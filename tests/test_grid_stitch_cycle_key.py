# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins <jhawk314@gmail.com>

"""Study-cycle labelling in the STITCH brief.

The cluster family name must come from the operator's own tag. MISO's "DPP"
is MISO vocabulary; labelling SPP's DISIS cycles (or the non-ISO West and
Southeast) as "DPP-<year>" misattributes one region's process to another and
is exactly the kind of error a regional planner spots immediately.
"""

from __future__ import annotations

import pytest

from domains.grid.run_stitch_brief import _cycle_key
from domains.grid.sources.lbnl_queue import QueueProject


def _proj(cluster: str = "", q_year=None) -> QueueProject:
    return QueueProject(
        q_id="Q1",
        status="active",
        q_year=q_year,
        fuel="solar",
        region="miso",
        state="MN",
        mw=100.0,
        cluster=cluster,
    )


@pytest.mark.parametrize(
    "cluster,expected",
    [
        # MISO keeps DPP, and sub-rounds collapse to the cycle year.
        ("DPP-2022 South", "cluster:DPP-2022"),
        ("DPP-2018-APR", "cluster:DPP-2018"),
        ("DPP-2008-NOV", "cluster:DPP-2008"),
        # SPP runs DISIS, not DPP -- the regression this test exists for.
        ("DISIS-2024-001", "cluster:DISIS-2024"),
        ("DISIS 2025", "cluster:DISIS-2025"),
        # Lowercase and mixed-case tags normalize to the same family.
        ("disis-2024", "cluster:DISIS-2024"),
    ],
)
def test_cluster_family_comes_from_the_operators_own_tag(cluster, expected):
    assert _cycle_key(_proj(cluster)) == expected


def test_spp_disis_is_never_labelled_dpp():
    """Direct regression guard: no non-MISO tag may acquire a DPP- prefix."""
    assert "DPP" not in _cycle_key(_proj("DISIS-2024-001"))


def test_yearless_cluster_tag_falls_back_to_entry_year():
    assert _cycle_key(_proj("Cluster A", q_year=2021)) == "cycle:2021"


def test_no_cluster_falls_back_to_entry_year():
    assert _cycle_key(_proj(q_year=2019)) == "cycle:2019"


def test_no_cluster_and_no_year_is_unknown():
    assert _cycle_key(_proj()) == "cycle:(unknown)"


def test_year_first_tag_does_not_invent_a_family_name():
    """A tag with no alphabetic token must not be given one."""
    assert _cycle_key(_proj("2024-001")) == "cluster:CLUSTER-2024"
