# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the interactive network map: geo placement, overlays, build."""

import json
import re

from domains.grid.flow_geometry import TieLine
from domains.grid.geo import albers_usa, ba_centroids, ba_fuel_mix, projected_positions
from domains.grid.map_overlays import ba_balance_facts, daily_overlays, load_overlays
from domains.grid.network_map import (
    _top_fuels,
    build_map_html,
    compute_network,
)


class _Plant:
    def __init__(self, ba, state, gen):
        self.balancing_authority = ba
        self.state = state
        self.net_generation_mwh = gen


def simple_ties():
    """A small connected interchange graph: PJM-NYIS-ISNE plus a bridge."""
    return [
        TieLine("NYIS", "PJM", 4_000_000.0, 1_000_000.0),
        TieLine("ISNE", "NYIS", 2_000_000.0, -500_000.0),
        TieLine("MISO", "PJM", 3_000_000.0, 800_000.0),
    ]


def test_albers_west_is_left_of_east():
    # California (lon -119) projects to a smaller x than Virginia (lon -78).
    xw, _ = albers_usa(37.0, -119.0)
    xe, _ = albers_usa(37.0, -78.0)
    assert xw < xe


def test_ba_centroid_is_weighted_toward_heavier_state():
    plants = [
        _Plant("PJM", "PA", 9_000.0),
        _Plant("PJM", "NJ", 1_000.0),
    ]
    (lat, lon) = ba_centroids(plants)["PJM"]
    # Centroid sits much nearer Pennsylvania than New Jersey.
    assert 40.0 < lat < 41.0
    assert -78.5 < lon < -76.0


def test_projected_positions_normalised_to_unit_box():
    pos = projected_positions({"A": (47.0, -120.0), "B": (30.0, -81.0)})
    for x, y in pos.values():
        assert 0.0 <= x <= 1.0
        assert 0.0 <= y <= 1.0


def test_overlays_join_edges_and_nodes(tmp_path):
    reports = tmp_path
    (reports / "system_overview.json").write_text(json.dumps({
        "concentration": {"PJM": {"n_constraints": 857, "top10_share": 0.38}},
        "curtailment_twh": {"CAISO 2023": 2.66},
    }), encoding="utf-8")
    (reports / "congestion_evidence_report.json").write_text(json.dumps({
        "claims": [{"ba_a": "NYIS", "ba_b": "PJM",
                    "estimated_value_usd": 2.9e7, "evidence_status": "lmp_proxy",
                    "net_direction": "NYIS -> PJM"}],
    }), encoding="utf-8")
    (reports / "queue_match.json").write_text(json.dumps({
        "ties": [{"ba_a": "NYIS", "ba_b": "PJM",
                  "active": {"n": 10, "gw": 85.5},
                  "withdrawn": {"n": 40, "gw": 524.3},
                  "congestion_spread_usd_mwh": 1.53,
                  "importing_side": "PJM", "exporting_side": "NYIS",
                  "top_active": [{"q_id": "AG2-582", "mw": 2100.0, "fuel": "gas"}]}],
    }), encoding="utf-8")

    ba_states = {"PJM": ["PA", "NJ"], "CISO": ["CA"]}
    node_facts, edge_facts = load_overlays(
        reports, {"PJM", "NYIS", "CISO", "MISO"}, ba_states=ba_states)

    assert node_facts["PJM"]["n_constraints"] == 857
    assert node_facts["CISO"]["curtailment_twh"] == 2.66
    pjm_nyis = edge_facts[("NYIS", "PJM")]
    assert pjm_nyis["congestion_value_usd"] == 2.9e7
    assert pjm_nyis["queue_active_gw"] == 85.5
    assert pjm_nyis["top_projects"]  # top project rendered


def test_compute_network_attaches_facts_and_dual_layout():
    ties = simple_ties()
    centroids = {"PJM": (40.0, -77.0), "NYIS": (42.9, -75.5),
                 "ISNE": (44.0, -71.0), "MISO": (41.0, -90.0)}
    node_facts = {"PJM": {"n_constraints": 857}}
    edge_facts = {("NYIS", "PJM"): {"congestion_value_usd": 2.9e7}}
    net = compute_network(ties, centroids=centroids,
                          node_facts=node_facts, edge_facts=edge_facts)

    assert len(net.nodes) == 4
    assert net.geo_coverage == 4
    pjm = next(n for n in net.nodes if n.name == "PJM")
    assert pjm.geo_known and 0.0 <= pjm.gx <= 1.0 and 0.0 <= pjm.sx <= 1.0
    assert net.node_facts["PJM"]["n_constraints"] == 857


def test_ba_balance_facts_groups_demand_generation_by_ba(tmp_path):
    csv = tmp_path / "EIA930_BALANCE_test.csv"
    csv.write_text(
        "Balancing Authority,Demand (MW),Net Generation (MW),Total Interchange (MW)\n"
        "PJM,1000000,1100000,100000\n"
        "PJM,1000000,1100000,100000\n"
        "MISO,500000,400000,-100000\n",
        encoding="utf-8",
    )
    facts = ba_balance_facts([csv])
    assert facts["PJM"]["demand_twh"] == 2.0          # 2M MWh
    assert facts["PJM"]["net_interchange_twh"] > 0     # net exporter
    assert facts["MISO"]["net_interchange_twh"] < 0    # net importer


def test_top_fuels_ranks_and_normalises():
    class P:
        def __init__(s, ba, fuel, gen):
            s.balancing_authority, s.primary_fuel, s.net_generation_mwh = ba, fuel, gen
    mix = ba_fuel_mix([P("X", "gas", 60), P("X", "coal", 30), P("X", "wind", 10)])
    top = _top_fuels(mix["X"], top=2)
    assert top[0]["fuel"] == "gas" and abs(top[0]["share"] - 0.6) < 1e-9
    assert len(top) == 2


def test_daily_overlays_picks_latest_per_metric(tmp_path):
    daily = tmp_path / "daily"
    daily.mkdir()
    (daily / "grid_daily_metrics.csv").write_text(
        "date,metric,value,unit,detail\n"
        "2026-06-10,pjm_nyis_seam_spread,1.0,usd_per_mwh,h=24\n"
        "2026-06-11,pjm_nyis_seam_spread,2.5,usd_per_mwh,h=24\n"
        "2026-06-11,pjm_constraint_severity,184650.7,usd_per_mwh_hours,top=X\n",
        encoding="utf-8",
    )
    node_daily, edge_daily = daily_overlays(tmp_path, {"PJM", "NYIS", "MISO"})
    assert edge_daily[("NYIS", "PJM")]["value"] == 2.5   # latest, not 1.0
    assert edge_daily[("NYIS", "PJM")]["date"] == "2026-06-11"
    assert node_daily["PJM"]["label"] == "Constraint severity"


def test_build_map_html_is_self_contained_with_data_island():
    net = compute_network(simple_ties())
    html = build_map_html(net)
    assert html.startswith("<!doctype html>")
    # No leaked format placeholders.
    for tok in ("{css}", "{js}", "{data}", "{geo_note}"):
        assert tok not in html
    # The JSON data island parses: a years map keyed by year, with the
    # graph + facts slots under the default year.
    data = json.loads(re.search(r'id="map-data">(.*?)</script>', html, re.S).group(1))
    assert data["available"] == ["latest"] and data["default"] == "latest"
    assert data["agent"]["requires_online_api"] is False
    assert data["agent"]["entrypoint"] == "python -m domains.grid.agent_tools"
    assert "id=\"t-agent\"" in html
    assert "grid_map_manual.html" in html
    shown = data["years"]["latest"]
    assert len(shown["nodes"]) == 4
    assert all("facts" in n for n in shown["nodes"])
    assert all("facts" in e for e in shown["edges"])


def test_build_map_html_multiyear_embeds_each_year():
    ties = simple_ties()
    nets = {"2024": compute_network(ties), "2025": compute_network(ties)}
    html = build_map_html(nets)
    data = json.loads(re.search(r'id="map-data">(.*?)</script>', html, re.S).group(1))
    assert data["available"] == ["2024", "2025"]
    assert data["default"] == "2025"            # latest year is the default
    assert set(data["years"]) == {"2024", "2025"}
    assert len(data["years"]["2024"]["nodes"]) == 4
