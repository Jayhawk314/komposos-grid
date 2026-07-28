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

import json
import subprocess
import sys
from pathlib import Path

from domains.grid import run_untapped_analytics as rua

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "reports" / "untapped_analytics.json"


def _emitted_matrix_keys() -> list[str]:
    if not ARTIFACT.exists():
        return []
    return list(json.loads(ARTIFACT.read_text(encoding="utf-8")).get("yoneda_matrix", {}))


def test_emitted_matrix_rows_are_in_deterministic_order():
    """Output property, not a source string.

    The row order must not depend on PYTHONHASHSEED. Sorted order is the
    observable consequence of iterating deterministically, so assert on that
    rather than on how the code happens to be written today.
    """
    keys = _emitted_matrix_keys()
    if not keys:
        return  # artifact not generated in this checkout
    assert keys == sorted(keys), (
        f"yoneda_matrix rows are not in a stable order: {keys}. "
        "Iterate sorted(target_bas), not the raw set."
    )


def test_regeneration_is_byte_identical_under_a_different_hash_seed():
    """The real guarantee: same inputs, same bytes, regardless of hash seed.

    This is what REPRODUCE.md promises a reader. Catches any future
    set-iteration or dict-ordering regression anywhere in this pipeline, not
    just the two spots fixed today.
    """
    if not ARTIFACT.exists():
        return

    def regen(seed: str) -> str:
        subprocess.run(
            [sys.executable, "-m", "domains.grid.run_untapped_analytics"],
            cwd=REPO, capture_output=True,
            env={**__import__("os").environ, "PYTHONHASHSEED": seed},
        )
        return ARTIFACT.read_text(encoding="utf-8")

    assert regen("1") == regen("98765"), (
        "untapped_analytics.json differs between hash seeds — output is "
        "nondeterministic and the reproducibility claim does not hold"
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
