# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the static dashboard generator (no network)."""

from domains.grid.dashboard import build_dashboard_html, fmt_money

STUDY = {
    "geography": "MISO-SWPP",
    "annual_value_usd": 31_147_626.0,
    "current_year": 2025,
    "flow_year": 2025,
    "same_year_flow_status": "same_year_flow",
}
CARD = {
    "geography": "MISO-SWPP",
    "solution_status": "priority_solution_study",
    "current_year": 2025,
    "spread_usd_mwh": 7.33,
    "annual_value_usd": 31_147_626.0,
    "trend_summary": "2023 $4.74/MWh -> 2025 $7.33/MWh",
}
PROJECT = {
    "project_name": "Patent Gate - Pioneer 345 kV",
    "geography": "MISO-SWPP",
    "capex_usd": "163714033",
    "annual_cost_usd": "18827114",
    "relief_value_usd": "31147626",
    "benefit_cost_ratio": "1.65",
    "clears_congestion_value": "True",
}
CHPE = {
    "pre_2025": {"label": "pre-2025", "start": "2025-04-13", "end": "2025-05-12",
                 "mean_abs_lbmp_spread_usd_mwh": 1.11,
                 "mean_abs_congestion_spread_usd_mwh": 0.41,
                 "share_lbmp_internal_above": 0.957},
    "post_2025": {"label": "post-2025", "start": "2025-05-13", "end": "2025-06-11",
                  "mean_abs_lbmp_spread_usd_mwh": 2.10,
                  "mean_abs_congestion_spread_usd_mwh": 1.35,
                  "share_lbmp_internal_above": 0.988},
    "pre_2026": {"label": "pre-2026", "start": "2026-04-13", "end": "2026-05-12",
                 "mean_abs_lbmp_spread_usd_mwh": 2.64,
                 "mean_abs_congestion_spread_usd_mwh": 1.42,
                 "share_lbmp_internal_above": 0.974},
    "post_2026": {"label": "post-2026", "start": "2026-05-13", "end": "2026-06-11",
                  "mean_abs_lbmp_spread_usd_mwh": 3.24,
                  "mean_abs_congestion_spread_usd_mwh": 2.05,
                  "share_lbmp_internal_above": 0.978},
    "did_congestion_usd_mwh": -0.31,
    "did_lbmp_usd_mwh": -0.39,
}


def test_fmt_money_scales():
    assert fmt_money(31_147_626) == "$31.1M"
    assert fmt_money(6_000_000_000) == "$6.0B"
    assert fmt_money(950) == "$950"


def test_dashboard_contains_headline_figures():
    html = build_dashboard_html([CARD], [STUDY], [PROJECT], CHPE)
    assert "$31.1M/yr" in html
    assert "Patent Gate - Pioneer 345 kV" in html
    assert "1.65" in html and "clears" in html
    assert "-0.31 $/MWh" in html
    assert "REPRODUCE.md" in html
    assert "<script" not in html  # static page, no JS


def test_dashboard_handles_missing_inputs():
    html = build_dashboard_html([], [], [], None)
    assert "No corridor cards available" in html
    assert "No costed projects yet" in html
    assert "CHPE" not in html.split("</header>")[1].split("Read this")[0]
