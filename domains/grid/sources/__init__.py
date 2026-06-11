# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Data source loaders for the grid domain.

Every loader normalizes its dataset into ``PlantRecord`` rows keyed by
the EIA plant ID (ORIS code), the shared spine that makes datasets
composable. See ``registry.py`` for the full catalog of sources and the
waste problem each one addresses.
"""

from domains.grid.sources.base import GridDataSource, PlantRecord
from domains.grid.sources.egrid import EGridSource
from domains.grid.sources.eia923 import EIA923Source
from domains.grid.sources.synthetic import SyntheticSource, make_synthetic_pair

__all__ = [
    "GridDataSource",
    "PlantRecord",
    "EGridSource",
    "EIA923Source",
    "SyntheticSource",
    "make_synthetic_pair",
]
