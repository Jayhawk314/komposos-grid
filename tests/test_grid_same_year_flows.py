# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for same-year flow extraction (no network)."""

import pytest

from domains.grid.same_year_flows import (
    extract_same_year_flows,
    write_same_year_flow_csv,
)
from domains.grid.solution_studies import load_same_year_flow_csv

HEADER = ('"Balancing Authority",'
          '"Directly Interconnected Balancing Authority",'
          '"Interchange (MW)"\n')


def _write_interchange(path, rows):
    path.write_text(HEADER + "".join(rows), encoding="utf-8")


def test_extract_pair_gross_and_net(tmp_path):
    csv_path = tmp_path / "interchange.csv"
    # Both reporters present with opposite signs; only the
    # alphabetically-first reporter (NYIS) should be counted.
    _write_interchange(csv_path, [
        'NYIS,PJM,"1,000"\n',
        "NYIS,PJM,-400\n",
        "PJM,NYIS,-1000\n",
        "PJM,NYIS,400\n",
        "MISO,SWPP,250\n",
    ])
    flows = extract_same_year_flows([csv_path], ["NYIS-PJM"], 2025)
    assert len(flows) == 1
    flow = flows[0]
    assert flow.geography == "NYIS-PJM"
    assert flow.year == 2025
    assert flow.gross_mwh == 1400.0   # |1000| + |-400|
    assert flow.net_mwh == 600.0      # 1000 - 400


def test_missing_pair_raises(tmp_path):
    csv_path = tmp_path / "interchange.csv"
    _write_interchange(csv_path, ["NYIS,PJM,100\n"])
    with pytest.raises(ValueError, match="MISO-SWPP"):
        extract_same_year_flows([csv_path], ["MISO-SWPP"], 2024)


def test_roundtrip_into_solution_study_intake(tmp_path):
    csv_path = tmp_path / "interchange.csv"
    _write_interchange(csv_path, ["MISO,SWPP,300\n", "MISO,SWPP,-100\n"])
    flows = extract_same_year_flows([csv_path], ["SWPP-MISO"], 2024)
    out = tmp_path / "same_year_flows.csv"
    write_same_year_flow_csv(flows, out)
    write_same_year_flow_csv(flows, out, append=True)  # idempotent header
    loaded = load_same_year_flow_csv(out)
    assert len(loaded) == 2
    assert loaded[0].ba_a == "MISO"
    assert loaded[0].gross_mwh == 400.0
    assert loaded[0].net_mwh == 200.0
