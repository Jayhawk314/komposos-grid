# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Catalog of grid datasets, keyed by the waste problem each addresses.

Three bottlenecks account for most recoverable grid waste:

- CURTAILMENT: renewable energy discarded because the grid cannot
  absorb or store it at the moment of production.
- TD_LOSSES: transmission & distribution losses -- heat dissipation,
  phase imbalance, congestion ("trapped" electricity).
- PEAKER_RELIANCE: inefficient fossil peakers covering demand spikes
  that flexible load or storage could absorb.
- DATA_COHERENCE: not a waste class but the precondition -- every
  analysis is only as good as the agreement between its sections.

Status meanings:
  implemented -- loader exists in this package
  planned     -- vetted, loader not yet written
  restricted  -- real data unavailable (CEII); synthetic stand-in noted
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


class WasteProblem(Enum):
    CURTAILMENT = "curtailment"
    TD_LOSSES = "td_losses"
    PEAKER_RELIANCE = "peaker_reliance"
    DATA_COHERENCE = "data_coherence"


@dataclass(frozen=True)
class DatasetEntry:
    key: str
    title: str
    problems: tuple
    granularity: str
    access: str
    status: str
    notes: str = ""


REGISTRY: List[DatasetEntry] = [
    DatasetEntry(
        key="egrid",
        title="EPA eGRID (plant-level generation, fuel mix, emissions)",
        problems=(WasteProblem.DATA_COHERENCE, WasteProblem.PEAKER_RELIANCE),
        granularity="annual, unit/plant/BA/region",
        access="free download, epa.gov/egrid",
        status="implemented",
        notes="sources/egrid.py; eGRID2024 due Jan 2026",
    ),
    DatasetEntry(
        key="eia923",
        title="EIA-923 (monthly plant generation & fuel consumption)",
        problems=(WasteProblem.DATA_COHERENCE, WasteProblem.PEAKER_RELIANCE),
        granularity="monthly, plant x fuel x prime mover",
        access="free download, eia.gov/electricity/data/eia923",
        status="implemented",
        notes="sources/eia923.py; eGRID is derived from this -- calibration overlap",
    ),
    DatasetEntry(
        key="pudl",
        title="PUDL (Catalyst Coop: cleaned EIA + FERC 1 + EPA CEMS, ID-crosswalked)",
        problems=(WasteProblem.DATA_COHERENCE,),
        granularity="plant/generator/boiler; hourly CEMS",
        access="free, catalystcoop-pudl (parquet / datasette)",
        status="planned",
        notes="the CAMD-EIA crosswalk is the functor that links EPA units to EIA plants",
    ),
    DatasetEntry(
        key="eia930",
        title="EIA-930 Hourly Grid Monitor (BA demand, generation, interchange)",
        problems=(WasteProblem.DATA_COHERENCE, WasteProblem.PEAKER_RELIANCE, WasteProblem.CURTAILMENT),
        granularity="hourly, 65 balancing authorities, REST API",
        access="free API",
        status="implemented",
        notes="sources/eia930.py; level-2 BA coherence and footprint repair proposals",
    ),
    DatasetEntry(
        key="lmp",
        title="ISO nodal LMPs via gridstatus (CAISO/PJM/MISO/ERCOT/SPP/NYISO/ISONE)",
        problems=(WasteProblem.TD_LOSSES,),
        granularity="5-min to hourly, nodal",
        access="free, gridstatus PyPI",
        status="planned",
        notes="congestion price signals locate trapped electricity geographically",
    ),
    DatasetEntry(
        key="lbnl_queue",
        title="LBNL Queued Up (project-level interconnection queue, ~98% of capacity)",
        problems=(WasteProblem.CURTAILMENT,),
        granularity="project-level with completion/withdrawal outcomes",
        access="free Excel, emp.lbl.gov/queues",
        status="planned",
        notes="OPTIMUS factorization target: what intermediates predict completion",
    ),
    DatasetEntry(
        key="eagle_i",
        title="ORNL EAGLE-I (county-level outages, 15-min, 2014-2025)",
        problems=(WasteProblem.TD_LOSSES,),
        granularity="county, 15-minute",
        access="free, doi.ccs.ornl.gov",
        status="planned",
    ),
    DatasetEntry(
        key="electricity_maps",
        title="Electricity Maps (real-time/historical carbon intensity & mix, global)",
        problems=(WasteProblem.PEAKER_RELIANCE, WasteProblem.CURTAILMENT),
        granularity="hourly, zone-level, API",
        access="API: free tier non-commercial; commercial use is licensed",
        status="planned",
        notes="marginal-intensity windows for demand shifting; check license before "
        "commercial wesys use -- EIA-930 covers the US for free",
    ),
    DatasetEntry(
        key="psml",
        title="PSML (TAMU: multi-scale T+D co-simulation time series)",
        problems=(WasteProblem.TD_LOSSES, WasteProblem.CURTAILMENT),
        granularity="millisecond-to-minute, synthetic buses, load/weather/PMU",
        access="free, open-source",
        status="planned",
        notes="synthetic but physics-faithful; where real voltage/current data is CEII",
    ),
    DatasetEntry(
        key="activsg",
        title="ACTIVSg / Texas2k synthetic grids (TAMU, 200-70k buses)",
        problems=(WasteProblem.TD_LOSSES,),
        granularity="full network topology with line parameters",
        access="free, synthetic",
        status="restricted",
        notes="real topology is FERC CEII; synthetic grids are the lawful stand-in. "
        "LMP-based topology recovery is the categorical alternative",
    ),
    DatasetEntry(
        key="storage_profiles",
        title="Storage optimization sets (Kaggle hybrid storage, Mendeley PV/EV/load)",
        problems=(WasteProblem.CURTAILMENT,),
        granularity="5-min interval SoC, round-trip losses, ramp rates",
        access="free download",
        status="planned",
        notes="charge/discharge scheduling against curtailment windows",
    ),
]


def for_problem(problem: WasteProblem) -> List[DatasetEntry]:
    return [e for e in REGISTRY if problem in e.problems]
