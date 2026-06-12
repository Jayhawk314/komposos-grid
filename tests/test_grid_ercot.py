# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the ERCOT hub spread (no network)."""

import pandas as pd
import pytest

from domains.grid.sources.ercot import hub_spread


def _frame():
    rows = []
    for h, (west, north) in enumerate([(10.0, 20.0), (50.0, 30.0), (25.0, 25.0)]):
        for point, price in (("HB_WEST", west), ("HB_NORTH", north),
                             ("LZ_HOUSTON", 99.0)):
            rows.append({
                "Delivery Date": "01/01/2023",
                "Hour Ending": f"{h+1:02d}:00",
                "Settlement Point": point,
                "Settlement Point Price": price,
            })
    return pd.DataFrame(rows)


def test_hub_spread_math():
    result = hub_spread(_frame(), year=2023)
    assert result.hours == 3
    # spreads: -10, +20, 0 -> mean |.| = 10
    assert result.mean_abs_spread == pytest.approx(10.0)
    assert result.max_abs_spread == pytest.approx(20.0)
    assert result.share_a_above == pytest.approx(1.0 / 3.0)
    assert result.mean_a == pytest.approx((10 + 50 + 25) / 3)
    d = result.to_dict()
    assert d["mean_abs_spread_usd_mwh"] == pytest.approx(10.0)
