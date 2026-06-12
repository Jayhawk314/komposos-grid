# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for MISO binding-constraint aggregation (no network)."""

import pandas as pd
import pytest

from domains.grid.sources.miso_constraints import (
    ConstraintReport,
    _frame_below_header,
    aggregate_constraints,
)


def _bc_frame(rows):
    return pd.DataFrame(
        rows,
        columns=["market_date", "constraint_id", "constraint_name",
                 "hour", "shadow_price"],
    )


def test_frame_below_header_finds_real_columns():
    raw = pd.DataFrame([
        ["Binding Constraints Report", None, None],
        ["Market Date: 06/02/2023", None, None],
        ["Constraint_ID", "Constraint Name", "Shadow Price"],
        [123, "TEST FLO", -4.5],
    ])
    df = _frame_below_header(raw, "Constraint_ID")
    assert list(df.columns) == ["Constraint_ID", "Constraint Name", "Shadow Price"]
    assert df.iloc[0]["Constraint_ID"] == 123


def test_aggregate_constraints_severity():
    frames = [
        _bc_frame([
            ["2023-06-01", 1, "SEAM FLO", 1, -10.0],
            ["2023-06-01", 1, "SEAM FLO", 2, -30.0],
            ["2023-06-01", 2, "LOCAL XF", 5, 5.0],
        ]),
        _bc_frame([["2023-06-02", 1, "SEAM FLO", 7, -20.0]]),
    ]
    catalog = {1: ("EAI", "SWPP"), 2: ("CONS", "CONS")}
    out = {c.constraint_id: c for c in aggregate_constraints(frames, catalog)}

    seam = out[1]
    assert seam.binding_hours == 3
    assert seam.severity == pytest.approx(60.0)   # |−10|+|−30|+|−20|
    assert seam.max_abs_sp == pytest.approx(30.0)
    assert (seam.from_area, seam.to_area) == ("EAI", "SWPP")
    assert out[2].severity == pytest.approx(5.0)


def test_report_area_pairs_and_totals():
    constraints = aggregate_constraints(
        [_bc_frame([
            ["2023-06-01", 1, "A", 1, -10.0],
            ["2023-06-01", 2, "B", 1, -40.0],
        ])],
        {1: ("EAI", "SWPP"), 2: ("EAI", "SWPP")},
    )
    report = ConstraintReport(
        start="2023-06-01", end="2023-06-01",
        days_fetched=1, days_missing=0, constraints=constraints,
    )
    assert report.total_severity == pytest.approx(50.0)
    assert report.area_pairs()[0] == ("EAI->SWPP", 50.0)
    assert "severity index" in report.summary()
