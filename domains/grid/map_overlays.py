# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Per-BA and per-tie facts for the interactive map's click-through.

The map's nodes (balancing authorities) and edges (interchange ties) are
the same keys the committed report artifacts use, so we can attach the
deeper evidence to each one for the inspector panel:

Edges (exact ba_a/ba_b join):
  - congestion_evidence_report.json : estimated congestion value, evidence
  - queue_match.json                : interconnection-queue GW behind the
                                      tie (active vs withdrawn), spread,
                                      import/export side, top projects
  - energy_solution_cards.json      : headline corridor solution status

Nodes (region alias / state footprint):
  - system_overview.json            : constraint concentration, curtailment
  - grid_waste_ledger.json          : single-BA waste claims
  - reliability_valuation_2023.json : reliability $ summed over the BA's
                                      states (footprint from geo.py)

Every fact carries the same measured-vs-screening honesty as its source;
nothing new is computed here beyond joining and summing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Mapping, Set, Tuple

# BA code -> the key the ISO-level reports use.
BA_TO_REGION: Dict[str, str] = {
    "MISO": "MISO", "PJM": "PJM", "SWPP": "SPP",
    "CISO": "CAISO", "NYIS": "NYISO", "ISNE": "ISONE", "ERCO": "ERCOT",
}

# State full name -> 2-letter (reliability_valuation uses full names).
_STATE_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN",
    "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}


# Daily-pulse metric -> where it lands on the map (live-ish data).
_DAILY_EDGE = {
    "pjm_nyis_seam_spread": (("NYIS", "PJM"), "Seam spread", "$/MWh"),
    "miso_swpp_seam_spread": (("MISO", "SWPP"), "Seam spread", "$/MWh"),
    "miso_soco_seam_spread": (("MISO", "SOCO"), "Seam spread", "$/MWh"),
}
_DAILY_NODE = {
    "miso_constraint_severity": ("MISO", "Constraint severity"),
    "pjm_constraint_severity": ("PJM", "Constraint severity"),
}


def _load(reports_dir: Path, name: str):
    path = reports_dir / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def ba_balance_facts(balance_csvs) -> Dict[str, Dict]:
    """Per-BA annual demand, net generation, and net interchange (TWh).

    From EIA-930 BALANCE - the same hourly files the national overview
    sums, here grouped by balancing authority so every node (not just the
    big ISOs) shows what it consumes, produces, and net imports/exports.
    Net interchange follows EIA's sign: positive = net exporter.
    """
    import pandas as pd

    cols = ["Balancing Authority", "Demand (MW)",
            "Net Generation (MW)", "Total Interchange (MW)"]
    demand: Dict[str, float] = {}
    netgen: Dict[str, float] = {}
    interchange: Dict[str, float] = {}
    for path in balance_csvs:
        if not Path(path).exists():
            continue
        df = pd.read_csv(path, usecols=cols, thousands=",")
        for col in cols[1:]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        grouped = df.groupby("Balancing Authority")
        for ba, v in grouped["Demand (MW)"].sum().items():
            demand[ba] = demand.get(ba, 0.0) + float(v)
        for ba, v in grouped["Net Generation (MW)"].sum().items():
            netgen[ba] = netgen.get(ba, 0.0) + float(v)
        for ba, v in grouped["Total Interchange (MW)"].sum().items():
            interchange[ba] = interchange.get(ba, 0.0) + float(v)

    out: Dict[str, Dict] = {}
    for ba in set(demand) | set(netgen) | set(interchange):
        out[ba] = {
            "demand_twh": demand.get(ba, 0.0) / 1e6,
            "netgen_twh": netgen.get(ba, 0.0) / 1e6,
            "net_interchange_twh": interchange.get(ba, 0.0) / 1e6,
        }
    return out


def daily_overlays(
    reports_dir: Path, node_ids: Set[str]
) -> Tuple[Dict[str, Dict], Dict[Tuple[str, str], Dict]]:
    """Latest daily-pulse reading per seam/region (the live-ish layer)."""
    import csv

    path = reports_dir / "daily" / "grid_daily_metrics.csv"
    if not path.exists():
        return {}, {}
    latest: Dict[str, Dict] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            m = r["metric"]
            if m not in latest or r["date"] > latest[m]["date"]:
                latest[m] = r

    node_daily: Dict[str, Dict] = {}
    edge_daily: Dict[Tuple[str, str], Dict] = {}
    for metric, r in latest.items():
        rec = {"label": None, "value": float(r["value"]),
               "unit": r["unit"], "date": r["date"]}
        if metric in _DAILY_EDGE:
            pair, label, unit = _DAILY_EDGE[metric]
            edge_daily[pair] = {**rec, "label": label, "unit": unit}
        elif metric in _DAILY_NODE:
            ba, label = _DAILY_NODE[metric]
            if ba in node_ids:
                node_daily[ba] = {**rec, "label": label}
    return node_daily, edge_daily


def _pair(a: str, b: str) -> Tuple[str, str]:
    return tuple(sorted((a, b)))  # type: ignore[return-value]


def _parse_pair(geography: str, node_ids: Set[str]) -> Tuple[str, str] | None:
    """Turn a 'X-Y' corridor label into a known BA pair, if it is one."""
    parts = [p.strip() for p in str(geography).split("-")]
    if len(parts) == 2 and parts[0] in node_ids and parts[1] in node_ids:
        return _pair(parts[0], parts[1])
    return None


def edge_overlays(
    reports_dir: Path, node_ids: Set[str]
) -> Dict[Tuple[str, str], Dict]:
    facts: Dict[Tuple[str, str], Dict] = {}

    def slot(a: str, b: str) -> Dict:
        return facts.setdefault(_pair(a, b), {})

    ce = _load(reports_dir, "congestion_evidence_report.json") or {}
    for c in ce.get("claims", []):
        value = float(c.get("estimated_value_usd", 0) or 0)
        if value <= 0:
            continue
        s = slot(c["ba_a"], c["ba_b"])
        s["congestion_value_usd"] = value
        s["evidence_status"] = c.get("evidence_status")
        s["net_direction"] = c.get("net_direction")

    qm = _load(reports_dir, "queue_match.json") or {}
    for t in qm.get("ties", []):
        s = slot(t["ba_a"], t["ba_b"])
        active = t.get("active") or {}
        withdrawn = t.get("withdrawn") or {}
        s["queue_active_gw"] = round(float(active.get("gw", 0) or 0), 1)
        s["queue_active_n"] = int(active.get("n", 0) or 0)
        s["queue_withdrawn_gw"] = round(float(withdrawn.get("gw", 0) or 0), 1)
        s["queue_withdrawn_n"] = int(withdrawn.get("n", 0) or 0)
        s["congestion_spread_usd_mwh"] = round(
            float(t.get("congestion_spread_usd_mwh", 0) or 0), 3)
        s["importing_side"] = t.get("importing_side")
        s["exporting_side"] = t.get("exporting_side")
        top = t.get("top_active") or []
        s["top_projects"] = [
            f"{p.get('q_id', '?')} · {p.get('mw', 0):,.0f} MW {p.get('fuel', '')}"
            for p in top[:3]
        ]

    cards = _load(reports_dir, "energy_solution_cards.json") or {}
    for card in cards.get("cards", []):
        pair = _parse_pair(card.get("geography", ""), node_ids)
        if pair is None:
            continue
        s = facts.setdefault(pair, {})
        s["solution_status"] = str(card.get("solution_status", "")).replace("_", " ")
        s["solution_value_usd"] = float(card.get("annual_value_usd", 0) or 0)
        s["solution_trend"] = card.get("trend_summary")

    return facts


def node_overlays(
    reports_dir: Path,
    node_ids: Set[str],
    ba_states: Mapping[str, Iterable[str]] | None = None,
) -> Dict[str, Dict]:
    facts: Dict[str, Dict] = {ba: {} for ba in node_ids}

    overview = _load(reports_dir, "system_overview.json") or {}
    concentration = overview.get("concentration", {})
    curtailment = overview.get("curtailment_twh", {})
    for ba in node_ids:
        region = BA_TO_REGION.get(ba)
        if region and region in concentration:
            facts[ba]["n_constraints"] = concentration[region].get("n_constraints")
            facts[ba]["top10_share"] = concentration[region].get("top10_share")
        # curtailment keys look like "CAISO 2023" / "SPP 2023"
        if region:
            for key, val in curtailment.items():
                if str(key).split()[0] == region:
                    facts[ba]["curtailment_twh"] = float(val)
                    break

    ledger = _load(reports_dir, "grid_waste_ledger.json") or {}
    for claim in ledger.get("claims", []):
        geo = str(claim.get("geography", ""))
        if geo in node_ids:
            bucket = facts[geo].setdefault("waste_claims", [])
            bucket.append({
                "title": claim.get("title"),
                "value_usd": float(claim.get("value_usd", 0) or 0),
                "evidence": claim.get("evidence_level"),
            })

    reliability = _load(reports_dir, "reliability_valuation_2023.json") or {}
    state_values = reliability.get("state_values_blended_usd", {})
    if ba_states and state_values:
        abbr_value = {
            _STATE_ABBR.get(name, name): float(v)
            for name, v in state_values.items()
        }
        for ba, states in ba_states.items():
            if ba not in facts:
                continue
            total = sum(abbr_value.get(s, 0.0) for s in set(states))
            if total > 0:
                facts[ba]["reliability_value_usd"] = total

    return facts


def load_overlays(
    reports_dir: str | Path,
    node_ids: Iterable[str],
    ba_states: Mapping[str, Iterable[str]] | None = None,
) -> Tuple[Dict[str, Dict], Dict[Tuple[str, str], Dict]]:
    reports_dir = Path(reports_dir)
    ids = set(node_ids)
    return (
        node_overlays(reports_dir, ids, ba_states=ba_states),
        edge_overlays(reports_dir, ids),
    )
