# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins <jhawk314@gmail.com>

"""Coverage for the minimum-follow-up check (run_post_ia_horizon.py).

The question this module exists to answer: does the MISO/ERCOT post-IA gap
survive when the youngest signings are removed at common age thresholds,
instead of pooling everything regardless of how recently it signed? The tests
pin the mechanics (who counts as mature, who is censored, who is excluded)
and then pin that the answer -- on the committed artifact -- is "yes, it
survives", without assuming that has to remain true if the data changes.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from domains.grid.run_post_ia_horizon import (
    HORIZONS_MONTHS,
    METHOD_NOTE,
    VINTAGE_CUTOFF,
    _age_months,
    cohort_age_report,
    horizon_report,
)
from domains.grid.sources.lbnl_queue import ACTIVE, OPERATIONAL, SUSPENDED, WITHDRAWN, QueueProject

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "reports" / "post_ia_horizon" / "post_ia_horizon.json"


def _p(status=OPERATIONAL, ia_date="2015-01-01"):
    return QueueProject(
        q_id="Q", status=status, q_year=2010, fuel="solar", region="miso",
        state="MN", mw=100.0, ia_date=ia_date,
    )


# ── definitions ──────────────────────────────────────────────────────────────


def test_horizon_excludes_signings_younger_than_the_horizon():
    """A project signed 12 months before the cutoff is not mature at 24mo."""
    recent = _p(OPERATIONAL, ia_date="2025-01-01")  # ~12mo before cutoff
    old = _p(OPERATIONAL, ia_date="2020-01-01")      # ~72mo before cutoff
    got = horizon_report([recent, old], months_h=24, min_cohort=30)
    assert got["n_mature"] == 1
    assert got["operational"] == 1


def test_maturity_boundary_is_inclusive_not_exclusive():
    """A project exactly as old as the horizon must count as mature (>=),
    not require being strictly older (>)."""
    p = _p(OPERATIONAL, ia_date="2020-06-15")
    exact_age = _age_months(p)
    got = horizon_report([p], months_h=exact_age, min_cohort=30)
    assert got["n_mature"] == 1


def test_mature_active_projects_are_censored_not_dropped_and_not_failures():
    """The whole point of the follow-up check: an old-enough project that
    still hasn't resolved must be visible and must not lower the rate."""
    old_active = _p(ACTIVE, ia_date="2015-01-01")
    old_ops = _p(OPERATIONAL, ia_date="2015-01-01")
    got = horizon_report([old_active, old_ops], months_h=24, min_cohort=30)
    assert got["n_mature"] == 2
    assert got["censored_active_or_suspended"] == 1
    assert got["decided"] == 1, "the censored project must not enter the decided denominator"
    assert got["rate"] == pytest.approx(1.0)


def test_mature_suspended_projects_are_also_censored():
    old_suspended = _p(SUSPENDED, ia_date="2015-01-01")
    got = horizon_report([old_suspended], months_h=24, min_cohort=30)
    assert got["censored_active_or_suspended"] == 1
    assert got["decided"] == 0


def test_rate_is_none_not_zero_when_nothing_decided():
    """A mature cohort of pure censored projects must report rate=None, not a
    fabricated 0.0 or 1.0 -- same 'absent, not a false rate' rule as the
    coverage audit's post-IA observability classification."""
    got = horizon_report([_p(ACTIVE, ia_date="2015-01-01")], months_h=24, min_cohort=30)
    assert got["decided"] == 0
    assert got["rate"] is None
    assert got["classification"] == "absent"


def test_classification_reuses_the_coverage_audit_thresholds():
    thin = [_p(OPERATIONAL, ia_date="2015-01-01")] * 5
    adequate = [_p(OPERATIONAL, ia_date="2015-01-01")] * 30
    assert horizon_report(thin, 24, min_cohort=30)["classification"] == "partial"
    assert horizon_report(adequate, 24, min_cohort=30)["classification"] == "complete"


def test_cohort_age_report_of_empty_list_has_no_median():
    got = cohort_age_report([])
    assert got["n"] == 0
    assert got["median_months"] is None


def test_cohort_age_report_median_of_multiple_ages():
    """A direct, artifact-independent check of the median math -- the pinned
    MISO-vs-ERCOT comparison only catches a broken median after the artifact
    is regenerated, so this covers the same logic without that dependency."""
    projects = [_p(ia_date=d) for d in ("2024-12-31", "2023-12-31", "2020-12-31")]
    got = cohort_age_report(projects)
    assert got["n"] == 3
    assert got["median_months"] == pytest.approx(24.0, abs=1.0)


def test_cohort_age_is_measured_from_the_fixed_vintage_cutoff():
    """Age must come from VINTAGE_CUTOFF, not from today's date -- a project
    signed exactly 24 months before the fixed cutoff must report age ~24,
    regardless of when the test suite actually runs."""
    p = _p(ia_date="2023-12-31")  # 24 months before 2025-12-31
    got = cohort_age_report([p])
    assert got["median_months"] == pytest.approx(24.0, abs=1.0)


def test_horizons_are_two_three_and_five_years():
    assert HORIZONS_MONTHS == [24, 36, 60]


def test_method_note_calls_this_a_sensitivity_check_not_age_matching():
    note = METHOD_NOTE.lower()
    assert "minimum-follow-up sensitivity check" in note
    assert "not age matching" in note
    assert "controls for cohort age" not in note


def test_vintage_cutoff_is_a_fixed_date_string_not_derived_at_import():
    """Regression guard against someone 'helpfully' swapping this for
    datetime.date.today() -- which would break byte-identical regeneration."""
    assert VINTAGE_CUTOFF == "2025-12-31"
    assert isinstance(VINTAGE_CUTOFF, str)


# ── pinned values against the generated artifact ────────────────────────────


def _region(name: str) -> dict:
    if not ARTIFACT.exists():
        pytest.skip("post_ia_horizon artifact not generated in this checkout")
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    return {r["region"]: r for r in data["regions"]}[name]


def test_the_miso_ercot_gap_survives_every_horizon():
    """The headline result: common minimum-age cutoffs do not close the gap.
    Guards direction and rough size at all three horizons, not just the raw
    pooled rate; it does not claim that remaining ages are matched."""
    if not ARTIFACT.exists():
        pytest.skip("post_ia_horizon artifact not generated in this checkout")
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    rows = {g["horizon_months"]: g for g in data["miso_ercot_gap_by_horizon"]}
    for h in [0, 24, 36, 60]:
        row = rows[h]
        assert row["gap"] > 0.35, f"gap at horizon {h} narrowed below 35pp: {row}"


def test_miso_cohort_is_far_older_than_ercot_cohort():
    """The mechanism that could have produced a spurious gap, and didn't:
    MISO's signed cohort is much older on average than ERCOT's."""
    miso_age = _region("miso")["cohort_age_months"]["median_months"]
    ercot_age = _region("ercot")["cohort_age_months"]["median_months"]
    assert miso_age > ercot_age + 60, "MISO's cohort should be over 5 years older, median-to-median"


def test_spp_horizons_are_pinned_absent_not_zero_percent():
    wb = _region("spp")
    for h in wb["horizons"]:
        assert h["decided"] == 0
        assert h["rate"] is None
        assert h["classification"] == "absent"


def test_artifact_has_no_runtime_timestamp():
    if not ARTIFACT.exists():
        pytest.skip("post_ia_horizon artifact not generated in this checkout")
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    prov_text = json.dumps(data["provenance"])
    for forbidden in ("generated_at", "timestamp", "date_run"):
        assert forbidden not in prov_text
    assert data["provenance"]["vintage_cutoff"] == "2025-12-31"
