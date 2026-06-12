# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the daily pulse (no network)."""

import csv
from datetime import date

from domains.grid.daily_update import append_metrics, daily_pulse


def _metric(name, value=1.0):
    return {"metric": name, "value": value, "unit": "u", "detail": "d"}


def test_append_metrics_idempotent(tmp_path):
    path = tmp_path / "metrics.csv"
    day = date(2026, 6, 10)
    append_metrics(day, [_metric("a", 1.0), _metric("b", 2.0)], path)
    # rerun same day with updated value for a: replaces, keeps b
    append_metrics(day, [_metric("a", 9.0)], path)
    # different day appends
    append_metrics(date(2026, 6, 11), [_metric("a", 3.0)], path)

    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 3
    a_10 = next(r for r in rows
                if r["date"] == "2026-06-10" and r["metric"] == "a")
    assert float(a_10["value"]) == 9.0
    assert any(r["metric"] == "b" for r in rows)


def test_daily_pulse_renders():
    text = daily_pulse(date(2026, 6, 10), [_metric("pjm_nyis_seam_spread", 2.5)])
    assert "2026-06-10" in text
    assert "pjm_nyis_seam_spread" in text
    assert "2.5" in text
