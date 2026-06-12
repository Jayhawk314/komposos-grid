# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for SPP loaders (no network)."""

import pandas as pd
import pytest

from domains.grid.sources.spp import (
    aggregate_spp_constraints,
    load_ver_curtailments,
)


def test_load_ver_curtailments(tmp_path):
    # 12 intervals of 12 MW wind redispatch = 12 MWh; 24 MW energy = 24 MWh
    df = pd.DataFrame({
        "LocalIntervalEnding": ["x"] * 12,
        "WindRedispatchCurtailments": [12.0] * 12,
        "WindManualCurtailments": [0.0] * 12,
        "WindCurtailedForEnergy": [24.0] * 12,
        "SolarRedispatchCurtailments": [6.0] * 12,
        "SolarManualCurtailments": [0.0] * 12,
        "SolarCurtailedForEnergy": [0.0] * 12,
    })
    path = tmp_path / "rollup.csv"
    df.to_csv(path, index=False)

    report = load_ver_curtailments(
        path, produced_mwh={"wind": 964.0, "solar": 100.0}
    )
    assert report.ba == "SWPP"
    assert report.total("wind") == pytest.approx(36.0)
    assert report.by_reason("Redispatch") == pytest.approx(18.0)
    assert report.by_reason("Energy") == pytest.approx(24.0)
    # share: 36 / (36 + 964) = 3.6%
    assert report.share("wind") == pytest.approx(0.036)
    # zero-valued reasons are dropped
    assert "Manual" not in report.curtailed_mwh["wind"]


def test_aggregate_spp_constraints():
    frames = [
        pd.DataFrame({
            "Constraint Name": ["SEAM_FG", "SEAM_FG", "LOCAL"],
            "Shadow Price": [-100.0, -50.0, 10.0],
        }),
        pd.DataFrame({
            "Constraint Name": ["SEAM_FG"],
            "Shadow Price": [-25.0],
        }),
    ]
    table = aggregate_spp_constraints(frames)
    assert table[0]["constraint_name"] == "SEAM_FG"
    assert table[0]["binding_hours"] == 3
    assert table[0]["severity"] == pytest.approx(175.0)
    assert table[0]["max_abs_sp"] == pytest.approx(100.0)


def test_aggregate_spp_constraints_bad_columns():
    with pytest.raises(ValueError, match="unrecognized"):
        aggregate_spp_constraints([pd.DataFrame({"foo": [1]})])


def test_seam_from_lmp_zip(tmp_path):
    import zipfile

    from domains.grid.sources.spp import seam_from_lmp_zip

    rows = []
    for loc, ptype, he1, he2 in [
        ("SPPSOUTH_HUB", "LMP", 30.0, 50.0),
        ("MISO", "LMP", 35.0, 44.0),
        ("SPPSOUTH_HUB", "MCC", 1.0, 5.0),
        ("MISO", "MCC", 0.0, 0.0),
        ("OTHER_LOC", "LMP", 99.0, 99.0),
    ]:
        rows.append({
            "Date": "06/01/2023",
            " Settlement Location Name": f" {loc}",  # stray spaces, as real files
            " PNODE Name": loc,
            " Price Type": f" {ptype}",
            " HE01": he1,
            "HE02": he2,
        })
    csv_path = tmp_path / "DA-LMP-MONTHLY-SL-202306.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    zip_path = tmp_path / "2023.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(csv_path, "2023/06/DA-LMP-MONTHLY-SL-202306.csv")

    seam = seam_from_lmp_zip(zip_path)
    assert seam["hours"] == 2
    # spreads: 30-35=-5, 50-44=+6 -> mean 5.5
    assert seam["mean_abs_lmp_spread"] == pytest.approx(5.5)
    assert seam["mean_abs_congestion_spread"] == pytest.approx(3.0)
    assert seam["share_hub_above"] == pytest.approx(0.5)
