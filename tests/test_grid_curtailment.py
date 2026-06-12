# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for curtailment aggregation."""

import pandas as pd
import pytest

from core.category import Category

from domains.grid.curtailment import aggregate_curtailments, write_to_category


def _frames():
    # 24 intervals of 12 MW solar curtailment = 24 MWh, split by reason
    curtailments = pd.DataFrame({
        "Date": ["2023-06-01"] * 24,
        "Hour": [10] * 24,
        "Interval": list(range(1, 13)) * 2,
        "Wind Curtailment": [6.0] * 24,    # 12 MWh wind
        "Solar Curtailment": [12.0] * 24,  # 24 MWh solar
        "Reason": ["Local"] * 12 + ["System"] * 12,
    })
    production = pd.DataFrame({
        "Solar": [120.0] * 24,  # 240 MWh produced
        "Wind": [60.0] * 24,    # 120 MWh produced
    })
    return curtailments, production


def test_aggregation_energy_and_reasons():
    report = aggregate_curtailments(*_frames(), avg_price_usd_mwh=50.0)
    assert report.total("solar") == pytest.approx(24.0)
    assert report.total("wind") == pytest.approx(12.0)
    assert report.by_reason("Local") == pytest.approx(18.0)   # 12 solar + 6 wind
    assert report.by_reason("System") == pytest.approx(18.0)
    assert report.share("solar") == pytest.approx(24.0 / 264.0)
    assert "upper bound" in report.summary()


def test_write_to_category():
    report = aggregate_curtailments(*_frames())
    cat = Category(name="curtail-test", db_path=":memory:")
    write_to_category(cat, report)
    mor = next(
        m for m in cat.morphisms_from("fuel:solar") if m.name == "curtailed_in"
    )
    assert mor.target == "ba:CISO"
    assert mor.confidence == pytest.approx(1 - 24.0 / 264.0)
    assert mor.metadata["reason_local_mwh"] == pytest.approx(12.0)
