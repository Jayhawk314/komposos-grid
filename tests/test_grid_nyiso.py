# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the NYISO seam-spread computation."""

import pandas as pd
import pytest

from domains.grid.sources.nyiso import (
    CONGESTION_COL,
    LBMP_COL,
    LOSS_COL,
    seam_component_spread,
    seam_spread,
)


def test_seam_spread_on_synthetic_zones(tmp_path):
    # 3 hours, two internal zones and a proxy; internal mean is
    # (30+50)/2 = 40 each hour; proxy alternates 35 / 45 / 40.
    rows = []
    for h, proxy_price in enumerate((35.0, 45.0, 40.0)):
        ts = f"01/0{h+1}/2023 00:00"
        rows += [
            {"Time Stamp": ts, "Name": "WEST", LBMP_COL: 30.0},
            {"Time Stamp": ts, "Name": "N.Y.C.", LBMP_COL: 50.0},
            {"Time Stamp": ts, "Name": "PJM", LBMP_COL: proxy_price},
        ]
    pd.DataFrame(rows).to_csv(tmp_path / "zones.csv", index=False)

    result = seam_spread(
        tmp_path, proxy="PJM", internal_zones=["WEST", "N.Y.C."]
    )
    assert result.hours == 3
    assert result.internal_mean_usd_mwh == pytest.approx(40.0)
    # |40-35|, |40-45|, |40-40| -> mean 10/3
    assert result.mean_abs_spread_usd_mwh == pytest.approx(10.0 / 3.0)
    assert result.max_abs_spread_usd_mwh == pytest.approx(5.0)
    assert result.share_internal_above == pytest.approx(1.0 / 3.0)


def test_missing_zone_raises(tmp_path):
    pd.DataFrame(
        [{"Time Stamp": "01/01/2023 00:00", "Name": "WEST", LBMP_COL: 30.0}]
    ).to_csv(tmp_path / "zones.csv", index=False)
    with pytest.raises(ValueError, match="missing"):
        seam_spread(tmp_path, proxy="PJM", internal_zones=["WEST"])


def test_seam_component_spread_exports_congestion_evidence_row(tmp_path):
    rows = []
    for ts, pjm_lbmp, pjm_congestion in [
        ("01/01/2023 00:00", 35.0, 1.0),
        ("01/01/2023 01:00", 45.0, 7.0),
    ]:
        rows += [
            {
                "Time Stamp": ts,
                "Name": "WEST",
                LBMP_COL: 30.0,
                CONGESTION_COL: 1.0,
                LOSS_COL: 0.5,
            },
            {
                "Time Stamp": ts,
                "Name": "N.Y.C.",
                LBMP_COL: 50.0,
                CONGESTION_COL: 3.0,
                LOSS_COL: 1.5,
            },
            {
                "Time Stamp": ts,
                "Name": "PJM",
                LBMP_COL: pjm_lbmp,
                CONGESTION_COL: pjm_congestion,
                LOSS_COL: 0.25,
            },
        ]
    pd.DataFrame(rows).to_csv(tmp_path / "zones.csv", index=False)

    audit = seam_component_spread(
        tmp_path,
        proxy="PJM",
        internal_zones=["WEST", "N.Y.C."],
    )
    row = audit.to_evidence_row()

    assert audit.hours == 2
    assert audit.mean_abs_lbmp_spread_usd_mwh == pytest.approx(5.0)
    # Internal congestion mean is 2.0 each hour; PJM is 1.0 then 7.0.
    assert audit.mean_abs_congestion_spread_usd_mwh == pytest.approx(3.0)
    assert audit.congestion_to_lbmp_ratio == pytest.approx(0.6)
    assert row["evidence_method"] == "lmp_component_proxy"
    assert row["mean_congestion_component_spread_usd_mwh"] == pytest.approx(3.0)
