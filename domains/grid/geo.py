# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Honest geographic placement for balancing authorities.

The grid data carries no coordinates, so a geographic map needs a
defensible source of position. This module derives one from data the
repo already has: eGRID assigns every power plant a state and a
balancing-authority code (sources/egrid.py). We aggregate that into a
BA -> states footprint and place each BA at the generation-weighted
centroid of the states it operates in.

Placement is therefore a *representative point*, not a survey
coordinate, and tie-lines drawn between two such points are schematic
connectors, not physical transmission routes. State centroids are the
standard approximate internal points (Census-style); they are constants
here, labelled approximate. Projection is Albers Equal-Area Conic for
the contiguous US (the usual choice for national thematic maps).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, Iterable, Mapping, Tuple

# Approximate internal state centroids (lat, lon), degrees. Representative
# points for placement only; not authoritative survey coordinates.
STATE_CENTROIDS: Dict[str, Tuple[float, float]] = {
    "AL": (32.8, -86.8), "AZ": (34.2, -111.7), "AR": (34.9, -92.4),
    "CA": (37.2, -119.4), "CO": (39.0, -105.5), "CT": (41.6, -72.7),
    "DE": (39.0, -75.5), "DC": (38.9, -77.0), "FL": (28.6, -82.4),
    "GA": (32.6, -83.4), "ID": (44.4, -114.6), "IL": (40.0, -89.2),
    "IN": (39.9, -86.3), "IA": (42.0, -93.5), "KS": (38.5, -98.4),
    "KY": (37.5, -85.3), "LA": (31.0, -92.0), "ME": (45.4, -69.2),
    "MD": (39.0, -76.8), "MA": (42.3, -71.8), "MI": (44.3, -85.4),
    "MN": (46.3, -94.3), "MS": (32.7, -89.7), "MO": (38.4, -92.5),
    "MT": (47.0, -109.6), "NE": (41.5, -99.8), "NV": (39.3, -116.6),
    "NH": (43.7, -71.6), "NJ": (40.2, -74.7), "NM": (34.4, -106.1),
    "NY": (42.9, -75.5), "NC": (35.5, -79.4), "ND": (47.4, -100.5),
    "OH": (40.3, -82.8), "OK": (35.6, -97.5), "OR": (43.9, -120.6),
    "PA": (40.9, -77.8), "RI": (41.7, -71.5), "SC": (33.9, -80.9),
    "SD": (44.4, -100.2), "TN": (35.9, -86.4), "TX": (31.5, -99.3),
    "UT": (39.3, -111.7), "VT": (44.1, -72.7), "VA": (37.5, -78.9),
    "WA": (47.4, -120.5), "WV": (38.6, -80.6), "WI": (44.6, -89.9),
    "WY": (43.0, -107.6), "AK": (64.0, -152.0), "HI": (20.3, -156.4),
}

# Albers Equal-Area Conic parameters for the contiguous US.
_ALBERS = dict(lat0=23.0, lon0=-96.0, lat1=29.5, lat2=45.5)


def albers_usa(lat: float, lon: float) -> Tuple[float, float]:
    """Project (lat, lon) degrees to Albers conic (x, y) map units."""
    lat0, lon0 = math.radians(_ALBERS["lat0"]), math.radians(_ALBERS["lon0"])
    lat1, lat2 = math.radians(_ALBERS["lat1"]), math.radians(_ALBERS["lat2"])
    phi, lam = math.radians(lat), math.radians(lon)
    n = 0.5 * (math.sin(lat1) + math.sin(lat2))
    c = math.cos(lat1) ** 2 + 2 * n * math.sin(lat1)
    rho = math.sqrt(c - 2 * n * math.sin(phi)) / n
    rho0 = math.sqrt(c - 2 * n * math.sin(lat0)) / n
    theta = n * (lam - lon0)
    return rho * math.sin(theta), rho0 - rho * math.cos(theta)


def ba_state_weights(plants: Iterable) -> Dict[str, Dict[str, float]]:
    """BA -> {state: net generation MWh} from eGRID plant records."""
    out: Dict[str, Dict[str, float]] = {}
    for rec in plants:
        ba = (getattr(rec, "balancing_authority", "") or "").strip()
        state = (getattr(rec, "state", "") or "").strip().upper()
        if not ba or state not in STATE_CENTROIDS:
            continue
        gen = getattr(rec, "net_generation_mwh", None)
        weight = abs(float(gen)) if gen else 0.0
        bucket = out.setdefault(ba, {})
        bucket[state] = bucket.get(state, 0.0) + max(weight, 1.0)
    return out


def ba_centroids(plants: Iterable) -> Dict[str, Tuple[float, float]]:
    """BA -> (lat, lon), generation-weighted centroid of its states."""
    centroids: Dict[str, Tuple[float, float]] = {}
    for ba, weights in ba_state_weights(plants).items():
        total = sum(weights.values())
        if total <= 0:
            continue
        lat = sum(STATE_CENTROIDS[s][0] * w for s, w in weights.items()) / total
        lon = sum(STATE_CENTROIDS[s][1] * w for s, w in weights.items()) / total
        centroids[ba] = (lat, lon)
    return centroids


def ba_centroids_from_egrid(
    workbook: str | Path, year: int = 2023
) -> Dict[str, Tuple[float, float]]:
    from domains.grid.sources.egrid import EGridSource

    return ba_centroids(EGridSource(workbook, year=year).load())


def ba_fuel_mix(plants: Iterable) -> Dict[str, Dict[str, float]]:
    """BA -> {primary fuel: net generation MWh} from eGRID plant records."""
    out: Dict[str, Dict[str, float]] = {}
    for rec in plants:
        ba = (getattr(rec, "balancing_authority", "") or "").strip()
        fuel = (getattr(rec, "primary_fuel", "") or "").strip().lower() or "other"
        gen = getattr(rec, "net_generation_mwh", None)
        if not ba or not gen:
            continue
        bucket = out.setdefault(ba, {})
        bucket[fuel] = bucket.get(fuel, 0.0) + float(gen)
    return out


def projected_positions(
    centroids: Mapping[str, Tuple[float, float]]
) -> Dict[str, Tuple[float, float]]:
    """Albers-project BA centroids and normalise to [0,1] (y flipped for SVG)."""
    projected = {ba: albers_usa(lat, lon) for ba, (lat, lon) in centroids.items()}
    if not projected:
        return {}
    xs = [p[0] for p in projected.values()]
    ys = [p[1] for p in projected.values()]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    sx = (maxx - minx) or 1.0
    sy = (maxy - miny) or 1.0
    s = max(sx, sy)  # uniform scale preserves the country's aspect ratio
    return {
        ba: ((x - minx) / s, 1.0 - (y - miny) / s)
        for ba, (x, y) in projected.items()
    }


def load_or_build_centroids(
    workbook: str | Path,
    cache: str | Path = "reports/ba_centroids.json",
    year: int = 2023,
) -> Dict[str, Tuple[float, float]]:
    """Cached BA centroids; build from eGRID once, reuse the JSON after."""
    cache = Path(cache)
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        return {k: (v[0], v[1]) for k, v in data.items()}
    centroids = ba_centroids_from_egrid(workbook, year=year)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(
        json.dumps({k: [round(a, 4), round(b, 4)] for k, (a, b) in centroids.items()},
                   indent=2),
        encoding="utf-8",
    )
    return centroids


def load_or_build_footprints(
    workbook: str | Path,
    cache: str | Path = "reports/ba_footprints.json",
    year: int = 2023,
) -> Tuple[Dict[str, Tuple[float, float]], Dict[str, list], Dict[str, Dict[str, float]]]:
    """Cached BA centroids + state footprints + fuel mix from one eGRID read.

    Returns (centroids, ba_states, fuel_mix). A single pass over the plant
    table feeds geographic placement, the reliability-by-state join, and
    the per-BA generation mix shown in the inspector.
    """
    from domains.grid.sources.egrid import EGridSource

    cache = Path(cache)
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        centroids = {k: (v["centroid"][0], v["centroid"][1]) for k, v in data.items()}
        ba_states = {k: list(v["states"]) for k, v in data.items()}
        fuel_mix = {k: dict(v.get("fuel_mix", {})) for k, v in data.items()}
        return centroids, ba_states, fuel_mix

    plants = EGridSource(workbook, year=year).load()
    weights = ba_state_weights(plants)
    centroids = ba_centroids(plants)
    fuel_mix = ba_fuel_mix(plants)
    ba_states = {ba: sorted(w) for ba, w in weights.items()}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(
        json.dumps(
            {
                ba: {"centroid": [round(centroids[ba][0], 4), round(centroids[ba][1], 4)],
                     "states": ba_states.get(ba, []),
                     "fuel_mix": {f: round(m, 1) for f, m in fuel_mix.get(ba, {}).items()}}
                for ba in centroids
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return centroids, ba_states, fuel_mix
