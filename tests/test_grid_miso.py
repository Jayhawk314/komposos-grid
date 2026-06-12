# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the MISO seam loader (no network)."""

import pandas as pd
import pytest

from domains.grid.sources.miso import HOUR_COLS, seam_spread


def _long_frame():
    """Two days x 2 hours for hub and interface, LMP + MCC."""
    rows = []
    data = {
        # (day, he) -> (hub_lmp, iface_lmp, hub_mcc, iface_mcc)
        ("2023-06-01", "HE 1"): (30.0, 25.0, 2.0, 0.0),
        ("2023-06-01", "HE 2"): (40.0, 44.0, 3.0, 0.0),
        ("2023-06-02", "HE 1"): (35.0, 35.0, 1.0, 1.0),
        ("2023-06-02", "HE 2"): (50.0, 41.0, 6.0, 1.0),
    }
    for (day, he), (hl, il, hm, im) in data.items():
        rows += [
            {"Node": "MS.HUB", "Value": "LMP", "he": he, "price": hl, "day": day},
            {"Node": "SOCO", "Value": "LMP", "he": he, "price": il, "day": day},
            {"Node": "MS.HUB", "Value": "MCC", "he": he, "price": hm, "day": day},
            {"Node": "SOCO", "Value": "MCC", "he": he, "price": im, "day": day},
        ]
    df = pd.DataFrame(rows)
    df.attrs["missing_days"] = 1
    return df


def test_seam_spread_math():
    result = seam_spread(_long_frame(), interface="SOCO", hub="MS.HUB")
    assert result.hours == 4
    # spreads: +5, -4, 0, +9 -> mean |.| = 4.5, max 9
    assert result.mean_abs_lmp_spread == pytest.approx(4.5)
    assert result.max_abs_lmp_spread == pytest.approx(9.0)
    assert result.share_hub_above == pytest.approx(0.5)
    # MCC spreads: 2, 3, 0, 5 -> mean 2.5
    assert result.mean_abs_congestion_spread == pytest.approx(2.5)
    assert result.missing_days == 1
    assert result.start == "2023-06-01" and result.end == "2023-06-02"


def test_evidence_row_fields():
    row = seam_spread(_long_frame(), "SOCO", "MS.HUB").to_evidence_row(
        "MISO", "SOCO"
    )
    assert row["ba_a"] == "MISO" and row["ba_b"] == "SOCO"
    assert row["evidence_method"] == "interface_settlement_spread"
    assert row["mean_price_spread_usd_mwh"] == pytest.approx(4.5)
    assert row["hours_observed"] == 4


def test_hour_cols_cover_24():
    assert len(HOUR_COLS) == 24
    assert HOUR_COLS[0] == "HE 1" and HOUR_COLS[-1] == "HE 24"
