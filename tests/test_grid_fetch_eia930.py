# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the EIA-930 fetcher (no network)."""

from domains.grid import fetch_eia930


def test_complete_file_is_not_redownloaded(tmp_path, monkeypatch):
    dest = tmp_path / "EIA930_INTERCHANGE_2025_Jan_Jun.csv"
    dest.write_bytes(b"x" * 100)
    monkeypatch.setattr(fetch_eia930, "_remote_size", lambda url: 100)

    def boom(req, timeout=0):
        raise AssertionError("should not download a complete file")

    monkeypatch.setattr(fetch_eia930.urllib.request, "urlopen", boom)
    out = fetch_eia930._fetch_file("https://example.invalid/f.csv", dest)
    assert out == dest
    assert dest.stat().st_size == 100


def test_fetch_year_names_both_halves(tmp_path, monkeypatch):
    fetched = []
    monkeypatch.setattr(
        fetch_eia930, "_fetch_file",
        lambda url, dest: fetched.append((url, dest)) or dest,
    )
    paths = fetch_eia930.fetch_year(2025, data_dir=tmp_path)
    assert [p.name for p in paths] == [
        "EIA930_INTERCHANGE_2025_Jan_Jun.csv",
        "EIA930_INTERCHANGE_2025_Jul_Dec.csv",
    ]
    assert all(url.startswith(fetch_eia930.BASE_URL) for url, _ in fetched)
