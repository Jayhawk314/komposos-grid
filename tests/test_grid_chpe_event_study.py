# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the CHPE event study (no network, synthetic NYISO files)."""

from datetime import date, timedelta

import pytest

from domains.grid.chpe_event_study import (
    chpe_event_study,
    windowed_component_spread,
)
from domains.grid.sources.nyiso import NYCA_INTERNAL_ZONES

HEADER = ('"Time Stamp","Name","PTID","LBMP ($/MWHr)",'
          '"Marginal Cost Losses ($/MWHr)",'
          '"Marginal Cost Congestion ($/MWHr)"\n')


def _write_day(directory, day: date, internal_lbmp: float, proxy_lbmp: float):
    rows = []
    stamp = f"{day.month:02d}/{day.day:02d}/{day.year} 00:00"
    for zone in NYCA_INTERNAL_ZONES:
        rows.append(f'"{stamp}","{zone}",1,{internal_lbmp},0.0,'
                    f'{internal_lbmp / 2}\n')
    rows.append(f'"{stamp}","PJM",2,{proxy_lbmp},0.0,{proxy_lbmp / 2}\n')
    path = directory / f"{day:%Y%m%d}damlbmp_zone.csv"
    path.write_text(HEADER + "".join(rows), encoding="utf-8")


def _fill_year(directory, year: int, pre_spread: float, post_spread: float):
    directory.mkdir(parents=True, exist_ok=True)
    day = date(year, 4, 13)
    while day <= date(year, 6, 11):
        spread = pre_spread if day < date(year, 5, 13) else post_spread
        _write_day(directory, day, internal_lbmp=20.0 + spread, proxy_lbmp=20.0)
        day += timedelta(days=1)


def test_window_filters_by_filename_date(tmp_path):
    _fill_year(tmp_path, 2026, pre_spread=10.0, post_spread=2.0)
    window = windowed_component_spread(
        tmp_path, date(2026, 5, 13), date(2026, 6, 11), label="post-2026"
    )
    assert window.days == 30
    assert window.mean_abs_lbmp_spread_usd_mwh == pytest.approx(2.0)


def test_did_detects_compression_beyond_seasonality(tmp_path):
    # 2025: spread rises 4 -> 6 seasonally; 2026: 10 -> 4 after CHPE.
    _fill_year(tmp_path / "csv2025", 2025, pre_spread=4.0, post_spread=6.0)
    _fill_year(tmp_path / "csv2026", 2026, pre_spread=10.0, post_spread=4.0)
    result = chpe_event_study(tmp_path / "csv2025", tmp_path / "csv2026")
    # DiD = (4 - 10) - (6 - 4) = -8
    assert result.did_lbmp_usd_mwh == pytest.approx(-8.0)
    assert result.did_congestion_usd_mwh == pytest.approx(-4.0)


def test_missing_window_raises(tmp_path):
    (tmp_path / "csv2026").mkdir()
    with pytest.raises(FileNotFoundError):
        windowed_component_spread(
            tmp_path / "csv2026", date(2026, 5, 13), date(2026, 6, 11),
            label="post-2026",
        )
