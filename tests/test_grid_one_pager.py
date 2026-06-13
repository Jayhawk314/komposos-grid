# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the emailable one-pager."""

from domains.grid.run_one_pager import SECTIONS, _ascii, build_html


def test_ascii_sanitizer_handles_typographic_punctuation():
    assert _ascii("waste — it’s “real”") == 'waste - it\'s "real"'


def test_one_pager_html_is_self_contained():
    charts = [f"<svg data-chart='{i}'></svg>" for i in range(4)]
    html = build_html(charts)
    assert html.count("<svg") == 4
    for heading, _ in SECTIONS:
        assert heading in html
    assert "traffic jams quietly charge" in html
    assert "src=" not in html  # no external references; safe to email
    assert "<script" not in html
