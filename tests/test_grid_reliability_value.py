# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the reliability valuation."""

import pytest

from domains.grid.outages import OutageReport
from domains.grid.reliability_value import (
    CLASS_LOAD_KW,
    METER_MIX,
    USD_PER_KWH,
    usd_per_customer_hour,
    value_outages,
)


def _report():
    return OutageReport(
        year=2023,
        state_customer_hours={"Texas": 1_000_000.0, "Maine": 500_000.0},
        state_customers={"Texas": 1e7, "Maine": 1e6},
    )


def test_meter_mix_sums_to_one():
    assert sum(METER_MIX.values()) == pytest.approx(1.0)


def test_blended_rate_derivation():
    expected = sum(
        METER_MIX[c] * USD_PER_KWH[c] * CLASS_LOAD_KW[c] for c in METER_MIX
    )
    assert usd_per_customer_hour() == pytest.approx(expected)
    # residential floor must be far below the blended rate
    floor = USD_PER_KWH["residential"] * CLASS_LOAD_KW["residential"]
    assert floor < usd_per_customer_hour() / 10


def test_valuation_totals_and_ordering():
    v = value_outages(_report())
    assert v.total_customer_hours == pytest.approx(1_500_000.0)
    assert v.floor_usd < v.blended_usd < v.high_usd
    assert v.floor_usd == pytest.approx(1_500_000.0 * v.floor_rate)
    # state split preserved at blended rate
    assert v.state_values_blended["Texas"] == pytest.approx(
        1_000_000.0 * v.blended_rate
    )
    payload = v.to_dict()
    assert "Sullivan" in payload["source"]
    assert payload["totals_usd"]["blended"] == pytest.approx(v.blended_usd)
