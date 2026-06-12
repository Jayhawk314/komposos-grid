# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for grid methodology C5-C7 artifacts."""

import csv
import json

import pytest

from domains.grid.methodology import (
    build_evidence_two_category,
    build_methodology_report,
)


def _write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _legacy(path):
    _write_csv(
        path,
        [
            {
                "ba_a": "CISO",
                "ba_b": "SRP",
                "evidence_source": "EIA ICE daily wholesale prices",
                "evidence_method": "hub_daily_overlap_proxy",
                "mean_price_spread_usd_mwh": 14.0,
            },
            {
                "ba_a": "BPAT",
                "ba_b": "CISO",
                "evidence_source": "EIA ICE daily wholesale prices",
                "evidence_method": "hub_daily_overlap_proxy",
                "mean_price_spread_usd_mwh": 9.5,
            },
            {
                "ba_a": "BPAT",
                "ba_b": "NEVP",
                "evidence_source": "EIA ICE daily wholesale prices",
                "evidence_method": "hub_daily_overlap_proxy",
                "mean_price_spread_usd_mwh": 3.8,
            },
        ],
    )


def _congestion(path):
    payload = {
        "claims": [
            {
                "ba_a": "CISO",
                "ba_b": "SRP",
                "evidence_status": "lmp_component_proxy",
                "gross_mwh": 10_000_000,
                "evidence_source": "CAISO OASIS",
                "evidence_method": "oasis_settlement_spread",
                "mean_price_spread_usd_mwh": 1.55,
                "mean_congestion_component_spread_usd_mwh": 1.39,
            },
            {
                "ba_a": "BPAT",
                "ba_b": "CISO",
                "evidence_status": "lmp_component_proxy",
                "gross_mwh": 5_000_000,
                "evidence_source": "CAISO OASIS",
                "evidence_method": "oasis_settlement_spread",
                "mean_price_spread_usd_mwh": 1.37,
                "mean_congestion_component_spread_usd_mwh": 1.11,
            },
            {
                "ba_a": "MISO",
                "ba_b": "SOCO",
                "evidence_status": "lmp_component_proxy",
                "gross_mwh": 4_000_000,
                "evidence_source": "MISO DA ex-post LMP",
                "evidence_method": "interface_settlement_spread",
                "mean_price_spread_usd_mwh": 1.58,
                "mean_congestion_component_spread_usd_mwh": 1.35,
            },
            {
                "ba_a": "SOCO",
                "ba_b": "FPL",
                "evidence_status": "structural_only",
                "gross_mwh": 3_000_000,
                "net_direction": "FPL -> SOCO",
                "curvature": -0.2,
            },
            {
                "ba_a": "AECI",
                "ba_b": "TVA",
                "evidence_status": "structural_only",
                "gross_mwh": 1_000_000,
                "net_direction": "AECI -> TVA",
                "curvature": -0.03,
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_methodology_report_builds_corrections_bounds_and_axioms(tmp_path):
    legacy = tmp_path / "legacy.csv"
    congestion = tmp_path / "congestion.json"
    _legacy(legacy)
    _congestion(congestion)

    report = build_methodology_report([legacy], [congestion], congestion)

    assert len(report.corrections) == 2
    assert report.mean_overstatement_ratio == pytest.approx((14.0 / 1.55 + 9.5 / 1.37) / 2)
    assert report.axioms[0].name == "hub_level_proxy_overstates_hourly_seam_spread"
    assert any(w.status == "screening_only" and w.ba_b == "NEVP" for w in report.warnings)

    soco_fpl = next(b for b in report.right_kan_bounds if b.ba_a == "FPL" and b.ba_b == "SOCO")
    assert soco_fpl.status == "bounded"
    assert soco_fpl.bound_spread_usd_mwh == pytest.approx(1.35)
    assert soco_fpl.bound_value_usd == pytest.approx(4_050_000.0)


def test_evidence_two_category_has_correction_cells(tmp_path):
    legacy = tmp_path / "legacy.csv"
    congestion = tmp_path / "congestion.json"
    _legacy(legacy)
    _congestion(congestion)
    report = build_methodology_report([legacy], [congestion], congestion)

    two_cat = build_evidence_two_category(report.corrections)

    assert len(two_cat.two_cells) == 2
    for cell in two_cat.two_cells.values():
        assert cell.source_object.startswith("tie:")
        assert cell.target_object.startswith("spread_claim:")
        assert cell.data["overstatement_ratio"] > 2.0


def test_methodology_report_exports(tmp_path):
    legacy = tmp_path / "legacy.csv"
    congestion = tmp_path / "congestion.json"
    _legacy(legacy)
    _congestion(congestion)
    report = build_methodology_report([legacy], [congestion], congestion)

    json_path = tmp_path / "methodology.json"
    md_path = tmp_path / "methodology.md"
    corrections_path = tmp_path / "corrections.csv"
    bounds_path = tmp_path / "bounds.csv"
    warnings_path = tmp_path / "warnings.csv"
    report.export_json(json_path)
    report.export_markdown(md_path)
    report.export_corrections_csv(corrections_path)
    report.export_bounds_csv(bounds_path)
    report.export_warnings_csv(warnings_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["correction_2cells"]
    assert "Right Kan Bounds" in md_path.read_text(encoding="utf-8")
    assert "overstatement_ratio" in corrections_path.read_text(encoding="utf-8")
    assert "bound_spread_usd_mwh" in bounds_path.read_text(encoding="utf-8")
    assert "screening_only" in warnings_path.read_text(encoding="utf-8")
