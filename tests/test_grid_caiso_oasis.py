# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the CAISO OASIS loader (no network)."""

import pandas as pd
import pytest

from domains.grid.sources.caiso_oasis import (
    OASISSeamSpread,
    _cache_path,
    _window_url,
    pivot_components,
    seam_spread,
)


def _oasis_frame(node, prices):
    """OASIS long format: one row per (interval, LMP_TYPE)."""
    rows = []
    for hour, (lmp, mcc) in enumerate(prices):
        ts = f"2023-06-01T{hour:02d}:00:00-00:00"
        for lmp_type, value in (("LMP", lmp), ("MCC", mcc), ("MCL", 0.5)):
            rows.append({
                "INTERVALSTARTTIME_GMT": ts,
                "NODE": node,
                "MARKET_RUN_ID": "DAM",
                "LMP_TYPE": lmp_type,
                "MW": value,
            })
    return pd.DataFrame(rows)


def test_window_url_has_required_params():
    from datetime import date

    url = _window_url("TH_SP15_GEN-APND", date(2023, 6, 1), date(2023, 6, 2), "DAM")
    assert "version=12" in url
    assert "resultformat=6" in url
    assert "node=TH_SP15_GEN-APND" in url
    assert "startdatetime=20230601T08:00-0000" in url


def test_pivot_components():
    df = _oasis_frame("A", [(30.0, 1.0), (40.0, 2.0)])
    pivot = pivot_components(df)
    assert list(pivot["LMP"]) == [30.0, 40.0]
    assert list(pivot["MCC"]) == [1.0, 2.0]


def test_seam_spread_math():
    df_a = _oasis_frame("A", [(30.0, 1.0), (40.0, 2.0), (50.0, 3.0)])
    df_b = _oasis_frame("B", [(35.0, 0.0), (38.0, 0.0), (44.0, 0.0)])
    result = seam_spread(df_a, df_b, "A", "B")
    assert result.hours == 3
    # |30-35|, |40-38|, |50-44| -> mean 13/3
    assert result.mean_abs_lmp_spread == pytest.approx(13.0 / 3.0)
    assert result.max_abs_lmp_spread == pytest.approx(6.0)
    assert result.share_a_above == pytest.approx(2.0 / 3.0)
    assert result.mean_abs_congestion_spread == pytest.approx(2.0)
    row = result.to_evidence_row("CISO", "SRP")
    assert row["evidence_method"] == "oasis_settlement_spread"
    assert row["hours_observed"] == 3


def test_cache_path_is_param_keyed(tmp_path):
    from datetime import date

    p1 = _cache_path(tmp_path, "TH_SP15_GEN-APND", date(2023, 6, 1),
                     date(2023, 6, 26), "DAM")
    p2 = _cache_path(tmp_path, "PALOVRDE_ASR-APND", date(2023, 6, 1),
                     date(2023, 6, 26), "DAM")
    assert p1 != p2
    assert "20230601" in p1.name
