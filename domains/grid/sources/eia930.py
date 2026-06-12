# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""EIA-930 Hourly Grid Monitor loader (BA-level sections).

EIA-930 is a genuinely independent measurement pathway from eGRID and
EIA-923: it comes from real-time operational telemetry reported hourly
by the 65 Lower-48 balancing authorities, not from annual plant
accounting forms. That makes the BA-level comparison a real coherence
test, not a derivation check.

Reads the bulk six-month BALANCE files
(https://www.eia.gov/electricity/gridmonitor/ -> "Six-Month Files"),
e.g. EIA930_BALANCE_2023_Jan_Jun.csv + ..._Jul_Dec.csv, and sums hourly
net generation to annual MWh per BA. The "(Adjusted)" series is used
when present -- EIA's published correction for missing/anomalous
telemetry -- falling back to the raw series.

Known systematic differences vs plant-accounting data (these are why
the BA-level tolerance is looser than the plant-level one):
- telemetry thresholds: small plants in EIA-923/eGRID may not be in
  BA metering
- station use and pumped-storage sign conventions differ
- behind-the-meter generation is excluded from both, but distributed
  utility-scale adjustments differ
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List

BA_COLUMN = "Balancing Authority"
NETGEN_ADJUSTED = "Net Generation (MW) (Adjusted)"
NETGEN_RAW = "Net Generation (MW)"


class EIA930Source:
    """BA-keyed section: annual net generation MWh per balancing authority.

    Not a GridDataSource (those are plant-keyed); the coherence checker
    only needs ``name`` and ``section()``.
    """

    name = "eia930"

    def __init__(self, csv_paths: Iterable[str | Path], year: int = 2023):
        self.csv_paths = [Path(p) for p in csv_paths]
        self.year = year

    def section(self) -> Dict[str, float]:
        import pandas as pd

        totals: Dict[str, float] = {}
        for path in self.csv_paths:
            header = pd.read_csv(path, nrows=0)
            value_col = (
                NETGEN_ADJUSTED if NETGEN_ADJUSTED in header.columns else NETGEN_RAW
            )
            df = pd.read_csv(
                path,
                usecols=[BA_COLUMN, value_col],
                thousands=",",
            )
            df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
            for ba, total in df.groupby(BA_COLUMN)[value_col].sum().items():
                totals[str(ba)] = totals.get(str(ba), 0.0) + float(total)
        return totals
