# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins <jhawk314@gmail.com>

"""Coverage for the queue figures the project is actually judged on.

Before this file, the only test touching `run_stitch_brief` was the cycle-label
one. `_completion`, `lbnl_completion`, `post_ia_completion` and
`duration_report` had none — and those produce every headline number: the
LBNL-reconciled completion rates and the post-IA finding.

A mutation check confirmed the gap. Changing the completion rate by 10%, and
widening the LBNL cohort window from 2000-2020 to 2000-2021, both left the full
suite green.

Two layers here:

* unit tests on synthetic projects, pinning the definitions (fast, no workbook);
* pinned-value tests against the committed artifact, so the figures that
  reconcile to LBNL *Queued Up* Sheet 25 cannot drift silently.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from domains.grid.run_stitch_brief import (
    _completion,
    duration_report,
    lbnl_completion,
    post_ia_completion,
)
from domains.grid.sources.lbnl_queue import OPERATIONAL, WITHDRAWN, QueueProject

REPO = Path(__file__).resolve().parents[1]
BRIEF = REPO / "reports" / "stitch_2026-06-23" / "queue_process_brief.json"


def _p(status=OPERATIONAL, q_year=2010, region="miso", ia_date="", q_date="", on_date=""):
    return QueueProject(
        q_id="Q", status=status, q_year=q_year, fuel="solar", region=region,
        state="MN", mw=100.0, ia_date=ia_date, q_date=q_date, on_date=on_date,
    )


# ── definitions ──────────────────────────────────────────────────────────────

def test_completion_is_operational_over_decided():
    projects = [_p(OPERATIONAL)] * 3 + [_p(WITHDRAWN)] * 7
    assert _completion(projects) == pytest.approx(0.3)


def test_completion_of_empty_cohort_is_zero_not_an_error():
    assert _completion([]) == 0.0


def test_lbnl_window_is_2000_to_2020_inclusive():
    """The window defines the published rate. Widening it silently was missed."""
    inside = [_p(OPERATIONAL, q_year=2000), _p(OPERATIONAL, q_year=2020)]
    outside = [_p(OPERATIONAL, q_year=1999), _p(OPERATIONAL, q_year=2021)]
    got = lbnl_completion(inside + outside, "miso")
    assert got["requests"] == 2, "only 2000-2020 requests belong in the denominator"
    assert got["built"] == 2


def test_lbnl_denominator_includes_still_active_projects():
    """LBNL's definition is operational / ALL requests, not / decided."""
    projects = [_p(OPERATIONAL, q_year=2010), _p("active", q_year=2010)]
    got = lbnl_completion(projects, "miso")
    assert got["requests"] == 2
    assert got["rate"] == pytest.approx(0.5)


def test_post_ia_counts_projects_that_signed_then_withdrew():
    """The whole point of the ia_date method versus the status-label shortcut."""
    projects = [
        _p(OPERATIONAL, ia_date="2015-01-01"),
        _p(WITHDRAWN, ia_date="2015-01-01"),
        _p(WITHDRAWN, ia_date=""),          # never signed -> excluded entirely
    ]
    got = post_ia_completion(projects, "miso")
    assert got["signed_decided"] == 2, "unsigned withdrawals must not enter the denominator"
    assert got["built_after_signing"] == 1
    assert got["rate"] == pytest.approx(0.5)


def test_post_ia_is_not_computable_when_no_signed_project_is_decided():
    """SPP's shape: IA dates exist but never on withdrawn projects.

    Must report zero decided rather than a confident rate. A denominator with
    no failures in it is not a success rate.
    """
    got = post_ia_completion([_p("active", ia_date="2015-01-01")], "miso")
    assert got["signed_decided"] == 0


def test_durations_are_survivor_conditioned():
    """Only projects that reached a milestone contribute to that stage."""
    projects = [
        _p(OPERATIONAL, q_date="2010-01-01", ia_date="2011-01-01", on_date="2012-01-01"),
        _p(WITHDRAWN, q_date="2010-01-01"),  # no IA, no COD -> contributes nothing
    ]
    dur = duration_report(projects, "miso")
    assert dur["ir_to_ia"]["n"] == 1
    assert dur["ia_to_cod"]["n"] == 1
    assert dur["ir_to_cod"]["median_months"] == pytest.approx(24.0, abs=0.5)


# ── pinned headline values ───────────────────────────────────────────────────

def _region(name: str) -> dict:
    if not BRIEF.exists():
        pytest.skip("brief artifact not generated in this checkout")
    data = json.loads(BRIEF.read_text(encoding="utf-8"))
    return {r["region"]: r for r in data["regions"]}[name]


@pytest.mark.parametrize(
    "region,requests,built",
    [("miso", 2806, 509), ("ercot", 1553, 459)],
)
def test_lbnl_completion_counts_match_queued_up_sheet_25(region, requests, built):
    """Verified against LBNL's published Sheet 25 on 2026-07-27.

    Sheet 25 prints MISO 509 operational / 1,936 withdrawn / 361 active and
    ERCOT 459 / 795 / 228 + 71 suspended. The denominators here are those
    columns summed. This is the project's central credibility claim, so it is
    pinned rather than left to inspection.
    """
    got = _region(region)["completion_lbnl"]
    assert got["requests"] == requests
    assert got["built"] == built


@pytest.mark.parametrize(
    "region,signed,built",
    [("miso", 1365, 476), ("ercot", 610, 486)],
)
def test_post_ia_headline_counts_are_pinned(region, signed, built):
    """The finding itself: ~35% MISO against ~80% ERCOT."""
    got = _region(region)["post_ia"]
    assert got["signed_decided"] == signed
    assert got["built_after_signing"] == built


def test_the_finding_holds_miso_far_below_ercot():
    """Guards the direction and rough size, not just the digits."""
    miso = _region("miso")["post_ia"]["rate"]
    ercot = _region("ercot")["post_ia"]["rate"]
    assert 0.30 < miso < 0.40
    assert 0.75 < ercot < 0.85
    assert ercot - miso > 0.40, "the 42-45 point gap is the finding"


def test_spp_post_ia_is_reported_as_not_computable():
    """SPP records no executed-IA date on withdrawn projects.

    It must stay at zero decided so the UI shows 'not tracked' rather than a
    fabricated rate.
    """
    assert (_region("spp")["post_ia"].get("signed_decided") or 0) == 0
