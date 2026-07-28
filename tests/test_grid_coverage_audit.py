# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins <jhawk314@gmail.com>

"""Coverage for the milestone-field coverage audit (run_coverage_audit.py).

Two layers, matching test_grid_stitch_headline_numbers.py's pattern:

* unit tests on synthetic projects, pinning the definitions (fast, no workbook);
* pinned-value tests against the committed artifact, so the SPP-generalizing
  result cannot drift silently.

The critical thing under test isn't the arithmetic -- it's that a zero count
is reported as "absent" (data cannot observe this) and never rendered in a way
that could be read as "this did not happen".
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from domains.grid.run_coverage_audit import (
    FIELDS,
    _classify,
    field_coverage,
    hybrid_capacity_coverage,
    post_ia_observability,
)
from domains.grid.sources.lbnl_queue import ACTIVE, OPERATIONAL, WITHDRAWN, QueueProject

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "reports" / "coverage_audit" / "coverage_audit.json"


def _p(status=OPERATIONAL, region="miso", ia_date="", wd_date="", q_date="",
       on_date="", cluster="", mw=100.0, entity="", mw2=None, mw3=None):
    return QueueProject(
        q_id="Q", status=status, q_year=2010, fuel="solar", region=region,
        state="MN", mw=mw, ia_date=ia_date, wd_date=wd_date, q_date=q_date,
        on_date=on_date, cluster=cluster, entity=entity, mw2=mw2, mw3=mw3,
    )


# ── definitions ──────────────────────────────────────────────────────────────


def test_field_coverage_counts_populated_over_total():
    members = [_p(ia_date="2015-01-01")] * 3 + [_p(ia_date="")] * 7
    got = field_coverage(members, "ia_date")
    assert got == {"populated": 3, "total": 10, "pct": pytest.approx(0.3)}


def test_field_coverage_of_empty_cohort_is_none_not_an_error():
    got = field_coverage([], "ia_date")
    assert got["total"] == 0
    assert got["pct"] is None


def test_mw_coverage_checks_mw1_only_not_mw2_or_mw3():
    """mw2/mw3 are near-empty hybrid columns; folding them into 'mw populated'
    would misrepresent both. mw field coverage must ignore them entirely."""
    members = [_p(mw=100.0, mw2=None), _p(mw=None, mw2=50.0)]
    got = field_coverage(members, "mw")
    assert got == {"populated": 1, "total": 2, "pct": pytest.approx(0.5)}


def test_hybrid_capacity_is_reported_separately_from_mw():
    members = [_p(mw=100.0, mw2=20.0, mw3=None), _p(mw=100.0, mw2=None, mw3=None)]
    got = hybrid_capacity_coverage(members)
    assert got["mw2"] == {"populated": 1, "total": 2, "pct": pytest.approx(0.5)}
    assert got["mw3"] == {"populated": 0, "total": 2, "pct": pytest.approx(0.0)}


def test_all_seven_audited_fields_are_the_documented_set():
    assert FIELDS == ["q_date", "ia_date", "wd_date", "on_date", "cluster", "mw", "entity"]


# ── classification: the honesty-critical part ──────────────────────────────


def test_zero_ia_dated_withdrawals_classifies_absent_not_zero_percent():
    """The SPP shape: withdrawn projects exist, none carry an ia_date.

    Must be labelled 'absent' (data cannot observe this), not merely a 0.0%
    that a reader could misparse as 'no project ever signed and withdrew'.
    """
    withdrawn = [_p(WITHDRAWN, ia_date="") for _ in range(50)]
    got = post_ia_observability(withdrawn, min_cohort=30)
    assert got["with_ia_date"] == 0
    assert got["total_withdrawn"] == 50
    assert got["classification"] == "absent"


def test_thin_but_nonzero_ia_dated_withdrawals_classifies_partial():
    withdrawn = [_p(WITHDRAWN, ia_date="2015-01-01")] * 5 + [_p(WITHDRAWN, ia_date="")] * 45
    got = post_ia_observability(withdrawn, min_cohort=30)
    assert got["with_ia_date"] == 5
    assert got["classification"] == "partial"


def test_min_cohort_or_more_ia_dated_withdrawals_classifies_complete():
    withdrawn = [_p(WITHDRAWN, ia_date="2015-01-01")] * 30 + [_p(WITHDRAWN, ia_date="")] * 5
    got = post_ia_observability(withdrawn, min_cohort=30)
    assert got["with_ia_date"] == 30
    assert got["classification"] == "complete"


def test_classify_boundary_is_inclusive_at_min_cohort():
    assert _classify(29, min_cohort=30) == "partial"
    assert _classify(30, min_cohort=30) == "complete"
    assert _classify(0, min_cohort=30) == "absent"


def test_post_ia_observability_of_empty_withdrawn_cohort_is_absent():
    """A region with zero withdrawn projects at all -- distinct from the SPP
    case (withdrawn projects exist, none dated), but must not divide by zero
    or report a misleadingly confident rate."""
    got = post_ia_observability([], min_cohort=30)
    assert got["total_withdrawn"] == 0
    assert got["pct"] is None
    assert got["classification"] == "absent"


def test_active_projects_never_enter_the_post_ia_observability_denominator():
    """Only withdrawn-status members belong in this test -- an active project
    with an ia_date has not withdrawn at all and says nothing about the
    post-IA question."""
    members = [_p(ACTIVE, ia_date="2015-01-01")] * 40
    got = post_ia_observability([m for m in members if m.status == WITHDRAWN], 30)
    assert got["total_withdrawn"] == 0


# ── pinned values against the generated artifact ────────────────────────────


def _region(name: str) -> dict:
    if not AUDIT.exists():
        pytest.skip("coverage_audit artifact not generated in this checkout")
    data = json.loads(AUDIT.read_text(encoding="utf-8"))
    return {r["region"]: r for r in data["regions"]}[name]


def _withdrawn_block(region_rep: dict) -> dict:
    return next(s for s in region_rep["statuses"] if s["status"] == WITHDRAWN)


def test_spp_post_ia_is_pinned_absent():
    """The finding this whole audit was built to generalize."""
    wb = _withdrawn_block(_region("spp"))
    assert wb["post_ia_observability"]["with_ia_date"] == 0
    assert wb["post_ia_observability"]["total_withdrawn"] == 1846
    assert wb["post_ia_observability"]["classification"] == "absent"


def test_miso_post_ia_is_pinned_complete_despite_low_raw_percentage():
    """MISO: only 27% of withdrawn projects carry an ia_date, yet the absolute
    count (889) is large enough to classify 'complete'. Pins that the
    classification is count-based, not percentage-based."""
    wb = _withdrawn_block(_region("miso"))
    obs = wb["post_ia_observability"]
    assert obs["with_ia_date"] == 889
    assert obs["total_withdrawn"] == 3263
    assert obs["classification"] == "complete"
    assert obs["pct"] < 0.30, "the raw percentage stays low even though the count is usable"


def test_wd_date_coverage_is_pinned_worst_in_west():
    """The unexpected finding: wd_date coverage ranges from 12% (west) to 98%
    (caiso) within withdrawn cohorts. West must sort first (worst)."""
    if not AUDIT.exists():
        pytest.skip("coverage_audit artifact not generated in this checkout")
    data = json.loads(AUDIT.read_text(encoding="utf-8"))
    ranked = data["national"]["wd_date_coverage_by_region_withdrawn"]
    assert ranked[0]["region"] == "west"
    assert ranked[0]["pct"] < 0.15
    assert ranked[-1]["pct"] > 0.90


def test_national_summary_is_sorted_ascending_by_percent():
    if not AUDIT.exists():
        pytest.skip("coverage_audit artifact not generated in this checkout")
    data = json.loads(AUDIT.read_text(encoding="utf-8"))
    pcts = [r["pct"] for r in data["national"]["wd_date_coverage_by_region_withdrawn"]]
    assert pcts == sorted(pcts)


def test_provenance_has_no_runtime_timestamp():
    """Byte-identical regeneration is required; a timestamp field would break it."""
    if not AUDIT.exists():
        pytest.skip("coverage_audit artifact not generated in this checkout")
    data = json.loads(AUDIT.read_text(encoding="utf-8"))
    prov_text = json.dumps(data["provenance"])
    for forbidden in ("generated_at", "timestamp", "date_run"):
        assert forbidden not in prov_text


def test_artifact_never_names_bpa_or_pacificorp():
    """Scope discipline: this is a region-level audit. BPA and PacifiCorp are
    entities inside the 'west' region, not one of the 9 audited regions, and
    must not appear anywhere in this artifact."""
    if not AUDIT.exists():
        pytest.skip("coverage_audit artifact not generated in this checkout")
    text = AUDIT.read_text(encoding="utf-8").lower()
    assert "bpa" not in text
    assert "pacificorp" not in text
