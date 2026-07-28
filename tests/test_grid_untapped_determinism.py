# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins <jhawk314@gmail.com>

"""Determinism guards for the untapped-analytics pipeline.

`target_bas` was once a set literal and the neighbour union was unsorted. Python
randomizes set iteration order per process (PYTHONHASHSEED), so regenerating
`untapped_analytics.json` produced a different file each run: rows reordered, and
float sums accumulated in a different order could shift the 4th decimal.

Nothing failed and no test broke — the numbers were still right — but a reader
following REPRODUCE.md would get an artifact that did not match the committed
one, which is exactly the claim this project rests on.
"""

from __future__ import annotations

import inspect

from domains.grid import run_untapped_analytics as rua


def test_target_bas_is_ordered_not_a_set():
    """A set literal here reintroduces per-process row-order randomness."""
    src = inspect.getsource(rua.calculate_yoneda_similarities)
    assert "target_bas = (" in src, (
        "target_bas must be an ordered sequence (tuple/list). A set literal "
        "makes the emitted matrix row order depend on PYTHONHASHSEED."
    )


def test_neighbour_union_is_sorted_before_summation():
    """Float addition is not associative, so summation order must be fixed."""
    src = inspect.getsource(rua.calculate_yoneda_similarities)
    assert "neighbors = sorted(" in src, (
        "the neighbour union must be sorted before the min/max accumulation, "
        "otherwise the 4th decimal can move between runs"
    )


def test_sheaf_metrics_returns_none_without_its_input(tmp_path, monkeypatch):
    """No hardcoded fallbacks: a missing report must yield None, not constants.

    This previously returned six values copied from a past real run, which were
    indistinguishable from computed output on the dashboard.
    """
    monkeypatch.setattr(rua, "REPORTS_DIR", tmp_path)
    assert rua.load_sheaf_metrics() is None


def test_sheaf_metrics_returns_none_on_incomplete_input(tmp_path, monkeypatch):
    """Partial input must also fail closed rather than substitute defaults."""
    import json

    (tmp_path / "ba_footprint_report.json").write_text(
        json.dumps({"before": {"sheaf_energy_leak": 1.5}, "after": {}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(rua, "REPORTS_DIR", tmp_path)
    assert rua.load_sheaf_metrics() is None


def test_sheaf_metrics_reports_residual_not_just_improvement(tmp_path, monkeypatch):
    """The residual disagreement must ship alongside the improvement.

    Reporting only the delta let a 62.9% agreement rate read as success while
    ~37% of entities still disagreed.
    """
    import json

    (tmp_path / "ba_footprint_report.json").write_text(
        json.dumps({
            "before": {"sheaf_energy_leak": 2.0, "agreement_rate": 0.40,
                       "abs_error_mwh": 300_000_000.0},
            "after": {"sheaf_energy_leak": 1.0, "agreement_rate": 0.60,
                      "abs_error_mwh": 200_000_000.0},
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(rua, "REPORTS_DIR", tmp_path)
    m = rua.load_sheaf_metrics()

    assert m["residual_disagreement_rate"] == 0.4
    assert m["residual_abs_error_twh"] == 200.0
    assert m["error_reduction_twh"] == 100.0
