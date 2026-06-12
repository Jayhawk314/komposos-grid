# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for BA interchange bottleneck reports."""

import json

from domains.grid.flow_geometry import TieLine, analyze_flow_geometry
from domains.grid.flow_report import build_flow_bottleneck_report


def _barbell_ties():
    west = ["W1", "W2", "W3", "W4"]
    east = ["E1", "E2", "E3", "E4"]
    ties = []
    for cluster in (west, east):
        for i in range(len(cluster)):
            for j in range(i + 1, len(cluster)):
                ties.append(TieLine(cluster[i], cluster[j], 1_000_000.0, 100_000.0))
    ties.append(TieLine("W1", "E1", 2_000_000.0, 500_000.0))
    return ties


def test_flow_bottleneck_report_prioritizes_bridge():
    ties = _barbell_ties()
    geometry = analyze_flow_geometry(ties)

    report = build_flow_bottleneck_report(ties, geometry=geometry)

    assert report.total_gross_mwh == 14_000_000.0
    assert report.hyperbolic_edges > 0
    assert report.bottlenecks
    top = report.bottlenecks[0]
    assert {top.ba_a, top.ba_b} == {"W1", "E1"}
    assert top.priority_score > 0
    assert "BA interchange bottleneck proof report" in report.summary()


def test_flow_report_exports_markdown_json_and_html(tmp_path):
    report = build_flow_bottleneck_report(_barbell_ties())
    md_path = tmp_path / "flow.md"
    json_path = tmp_path / "flow.json"
    html_path = tmp_path / "flow.html"

    report.export_markdown(md_path)
    report.export_json(json_path)
    report.export_html(html_path)

    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")

    assert "# BA Interchange Bottleneck Report" in markdown
    assert payload["n_bas"] == 8
    assert payload["bottlenecks"][0]["priority_score"] > 0
    assert "<!doctype html>" in html
    assert "BA Interchange Bottleneck Dashboard" in html
    assert "Priority Bottlenecks" in html


def test_flow_report_dict_includes_spectral_partition():
    report = build_flow_bottleneck_report(_barbell_ties())

    payload = report.to_dict()

    assert payload["spectral"]["coupling"] in {
        "very weak",
        "weak",
        "moderate",
        "strong",
    }
    assert len(payload["spectral"]["fiedler_partition"]["small"]) == 4
    assert len(payload["spectral"]["fiedler_partition"]["large"]) == 4
