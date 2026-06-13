# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the SVG chart generator and its dashboard wiring."""

from domains.grid.charts import bar_chart, line_chart, nice_max
from domains.grid.dashboard import (
    parse_trend_summary,
    project_bc_chart,
    seam_trend_chart,
)


def test_nice_max_rounds_to_clean_ceilings():
    assert nice_max(7.38) == 10.0
    assert nice_max(1.8) == 2.0
    assert nice_max(42) == 50.0
    assert nice_max(0) == 1.0


def test_line_chart_renders_series_and_gaps():
    svg = line_chart(
        [2023, 2024, 2025],
        {"NYIS-PJM": [1.53, 2.02, 7.38], "CISO-SRP": [1.39, None, None]},
        title="Seam spread", y_label="$/MWh",
    )
    assert svg.startswith("<svg")
    assert "7.38" in svg and "NYIS-PJM" in svg
    # single-point series draws no polyline but still shows its dot
    assert svg.count("<polyline") == 1
    assert "1.39" in svg


def test_bar_chart_ref_line_and_values():
    svg = bar_chart(
        ["Patent Gate", "CHPE"],
        {"B/C": [1.65, 0.12]},
        title="Does it pay?", y_label="b/c",
        ref_line=1.0, ref_label="break-even",
    )
    assert "1.65" in svg and "0.12" in svg
    assert "break-even" in svg
    assert "stroke-dasharray" in svg


def test_parse_trend_summary():
    points = parse_trend_summary(
        "2023 $1.53/MWh -> 2024 $2.02/MWh -> 2025 $7.38/MWh (4.8x)")
    assert points == [(2023, 1.53), (2024, 2.02), (2025, 7.38)]
    assert parse_trend_summary("corrected to $1.39") == []


def test_dashboard_chart_builders_skip_empty_inputs():
    assert seam_trend_chart([{"trend_summary": "no years here"}]) == ""
    assert project_bc_chart([{"benefit_cost_ratio": "0"}]) == ""
    svg = seam_trend_chart([
        {"geography": "A-B", "trend_summary": "2024 $2.00/MWh -> 2025 $3.00/MWh"},
    ])
    assert "A-B" in svg and "3.00" in svg
