# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for EAGLE-I outage aggregation."""

import json

import pandas as pd
import pytest

from core.category import Category

from domains.grid.outages import (
    OutageReport,
    aggregate_outages,
    load_mcc,
    write_to_category,
)


def test_load_mcc_maps_fips_to_state(tmp_path):
    pd.DataFrame({
        "County_FIPS": [48001, 48003, 6001],
        "Customers": [1000, 2000, 5000],
    }).to_csv(tmp_path / "mcc.csv", index=False)
    mcc = load_mcc(tmp_path / "mcc.csv")
    assert mcc["Texas"] == pytest.approx(3000.0)
    assert mcc["California"] == pytest.approx(5000.0)


def test_aggregate_outages_chunked(tmp_path):
    # 8 intervals x 1000 customers in TX, 4 x 500 in CA
    df = pd.DataFrame({
        "fips_code": [48001] * 8 + [6001] * 4,
        "county": ["Anderson"] * 8 + ["Alameda"] * 4,
        "state": ["Texas"] * 8 + ["California"] * 4,
        "sum": [1000.0] * 8 + [500.0] * 4,
        "run_start_time": pd.date_range("2023-01-01", periods=12, freq="15min"),
    })
    path = tmp_path / "outages.csv"
    df.to_csv(path, index=False)

    mcc = {"Texas": 10_000.0, "California": 20_000.0}
    report = aggregate_outages(path, mcc, chunksize=5)

    assert report.state_customer_hours["Texas"] == pytest.approx(2000.0)
    assert report.state_customer_hours["California"] == pytest.approx(500.0)
    assert report.hours_per_customer("Texas") == pytest.approx(0.2)
    assert report.ranked()[0][0] == "Texas"
    assert report.rows_processed == 12
    assert report.first_timestamp == "2023-01-01 00:00:00"
    assert report.last_timestamp == "2023-01-01 02:45:00"


def test_write_to_category():
    report = OutageReport(
        year=2023,
        state_customer_hours={"Texas": 2000.0, "California": 500.0},
        state_customers={"Texas": 10_000.0, "California": 20_000.0},
    )
    cat = Category(name="outage-test", db_path=":memory:")
    write_to_category(cat, report)

    tx = next(m for m in cat.morphisms_from("state:Texas"))
    ca = next(m for m in cat.morphisms_from("state:California"))
    assert tx.name == "outage_burden"
    # Texas is the worst state -> lowest retention confidence
    assert tx.confidence < ca.confidence
    assert tx.metadata["hours_per_customer"] == pytest.approx(0.2)


def test_outage_report_exports(tmp_path):
    report = OutageReport(
        year=2023,
        state_customer_hours={"Texas": 2000.0, "California": 500.0},
        state_customers={"Texas": 10_000.0, "California": 20_000.0},
        rows_processed=12,
        first_timestamp="2023-01-01 00:00:00",
        last_timestamp="2023-12-31 23:45:00",
    )
    csv_path = tmp_path / "outages.csv"
    md_path = tmp_path / "outages.md"
    json_path = tmp_path / "outages.json"
    html_path = tmp_path / "outages.html"

    report.export_csv(csv_path)
    report.export_markdown(md_path)
    report.export_json(json_path)
    report.export_html(html_path)

    assert "EAGLE-I Reliability Waste Report 2023" in md_path.read_text(
        encoding="utf-8"
    )
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["total_customer_hours"] == pytest.approx(2500.0)
    assert payload["rows_processed"] == 12
    assert payload["states"][0]["state"] == "Texas"
    assert "<!doctype html>" in html_path.read_text(encoding="utf-8")
    rows = pd.read_csv(csv_path)
    assert rows.iloc[0]["state"] == "Texas"
