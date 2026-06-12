# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the PJM Data Miner client (no network, no real keys)."""

import pytest

from domains.grid.sources.pjm_dataminer import (
    PJMError,
    aggregate_pjm_constraints,
    month_windows,
    resolve_api_key,
)


def test_resolve_api_key_explicit_and_env(monkeypatch):
    assert resolve_api_key("abc123") == "abc123"
    monkeypatch.setenv("PJM_API_KEY", "envkey")
    assert resolve_api_key() == "envkey"
    monkeypatch.delenv("PJM_API_KEY")
    with pytest.raises(PJMError, match="apiportal"):
        resolve_api_key()


def test_month_windows_cover_year():
    windows = list(month_windows(2023))
    assert len(windows) == 12
    assert windows[0][0].startswith("1/1/2023")
    assert windows[-1][1].startswith("1/1/2024")


def test_aggregate_pjm_constraints():
    rows = [
        {"monitored_facility": "SEAM LINE", "shadow_price": -50.0},
        {"monitored_facility": "SEAM LINE", "shadow_price": -150.0},
        {"monitored_facility": "LOCAL XFMR", "shadow_price": 25.0},
        {"constraint_name": "FALLBACK NAME", "shadow_price": -10.0},
    ]
    table = aggregate_pjm_constraints(rows)
    assert table[0]["constraint_name"] == "SEAM LINE"
    assert table[0]["binding_hours"] == 2
    assert table[0]["severity"] == pytest.approx(200.0)
    assert table[0]["max_abs_sp"] == pytest.approx(150.0)
    names = {e["constraint_name"] for e in table}
    assert "FALLBACK NAME" in names
