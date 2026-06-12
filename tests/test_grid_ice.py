# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for Western ICE hub evidence audits."""

import pandas as pd
import pytest

from domains.grid.sources.ice import (
    BA_COLUMN,
    DAILY_VOLUME,
    DATE_COLUMN,
    DELIVERY_DATE,
    DIBA_COLUMN,
    FLOW_COLUMN,
    HubPairSpec,
    PRICE_HUB,
    WEIGHTED_PRICE,
    audit_hub_pair,
)


def test_hub_pair_audit_keeps_conservative_spread_and_alignment():
    prices = pd.DataFrame([
        {
            PRICE_HUB: "A Hub",
            DELIVERY_DATE: pd.Timestamp("2023-01-01"),
            WEIGHTED_PRICE: 20.0,
            DAILY_VOLUME: 100.0,
        },
        {
            PRICE_HUB: "B Hub",
            DELIVERY_DATE: pd.Timestamp("2023-01-01"),
            WEIGHTED_PRICE: 30.0,
            DAILY_VOLUME: 80.0,
        },
        {
            PRICE_HUB: "A Hub",
            DELIVERY_DATE: pd.Timestamp("2023-01-02"),
            WEIGHTED_PRICE: 50.0,
            DAILY_VOLUME: 100.0,
        },
        {
            PRICE_HUB: "B Hub",
            DELIVERY_DATE: pd.Timestamp("2023-01-02"),
            WEIGHTED_PRICE: 40.0,
            DAILY_VOLUME: 80.0,
        },
    ])
    flows = pd.DataFrame([
        {
            BA_COLUMN: "A",
            DIBA_COLUMN: "B",
            DATE_COLUMN: pd.Timestamp("2023-01-01"),
            FLOW_COLUMN: 100.0,
        },
        {
            BA_COLUMN: "A",
            DIBA_COLUMN: "B",
            DATE_COLUMN: pd.Timestamp("2023-01-02"),
            FLOW_COLUMN: -50.0,
        },
    ])

    audit = audit_hub_pair(
        prices,
        flows,
        HubPairSpec("A", "B", "A Hub", "B Hub", "test"),
    )
    row = audit.to_evidence_row()

    assert audit.conservative_spread_usd_mwh == pytest.approx(0.0)
    assert audit.daily_mean_abs_spread_usd_mwh == pytest.approx(10.0)
    assert audit.flow_alignment_day_share == pytest.approx(1.0)
    assert audit.flow_alignment_weighted_share == pytest.approx(1.0)
    assert row["evidence_method"] == "hub_daily_overlap_proxy"
    assert row["mean_price_spread_usd_mwh"] == pytest.approx(0.0)


def test_hub_pair_audit_handles_reversed_alphabetical_flow():
    prices = pd.DataFrame([
        {
            PRICE_HUB: "Z Hub",
            DELIVERY_DATE: pd.Timestamp("2023-01-01"),
            WEIGHTED_PRICE: 20.0,
            DAILY_VOLUME: 100.0,
        },
        {
            PRICE_HUB: "A Hub",
            DELIVERY_DATE: pd.Timestamp("2023-01-01"),
            WEIGHTED_PRICE: 40.0,
            DAILY_VOLUME: 100.0,
        },
    ])
    # EIA rows are kept from alphabetically first BA, A -> Z. The requested
    # audit direction is Z -> A, so the sign must flip.
    flows = pd.DataFrame([
        {
            BA_COLUMN: "A",
            DIBA_COLUMN: "Z",
            DATE_COLUMN: pd.Timestamp("2023-01-01"),
            FLOW_COLUMN: -10.0,
        },
    ])

    audit = audit_hub_pair(
        prices,
        flows,
        HubPairSpec("Z", "A", "Z Hub", "A Hub", "test"),
    )

    assert audit.net_flow_mwh_a_to_b == pytest.approx(10.0)
    assert audit.flow_alignment_weighted_share == pytest.approx(1.0)
