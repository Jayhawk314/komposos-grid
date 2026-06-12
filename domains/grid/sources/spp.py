# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""SPP Marketplace loaders (PLAN A3): curtailments, constraints, LMPs.

All keyless via the portal file-browser API
(https://portal.spp.org/file-browser-api/download/<endpoint>?path=...).
Recent months keep daily files; older years are consolidated into
yearly zips (e.g. path=/2023/2023.zip). Endpoints used:

- ``ver-curtailments``: 5-minute wind/solar curtailment MW with SPP's
  own cause split -- Redispatch (congestion), Manual (reliability),
  CurtailedForEnergy (economic/oversupply). The annual rollup CSV maps
  directly onto the CAISO Local/System decomposition.
- ``da-binding-constraints``: hourly DA binding constraints with
  shadow prices (DA-BC-<yyyymmdd>0100.csv inside the yearly zip) --
  the third ISO in the constraint severity series.
- ``da-lmp-by-settlement-location``: hourly DA LMP/MLC/MCC per
  settlement location, for seam spreads from the SPP side.

Production denominators for curtailment shares come from the EIA-930
BALANCE files (SWPP wind/solar columns) already used elsewhere.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from domains.grid.curtailment import CurtailmentReport

MWH_PER_5MIN = 1.0 / 12.0

VER_COLUMNS = {
    "wind": {
        "Redispatch": "WindRedispatchCurtailments",
        "Manual": "WindManualCurtailments",
        "Energy": "WindCurtailedForEnergy",
    },
    "solar": {
        "Redispatch": "SolarRedispatchCurtailments",
        "Manual": "SolarManualCurtailments",
        "Energy": "SolarCurtailedForEnergy",
    },
}


def load_ver_curtailments(
    rollup_csv: str | Path,
    produced_mwh: Optional[Dict[str, float]] = None,
    year: int = 2023,
    avg_price_usd_mwh: Optional[float] = None,
) -> CurtailmentReport:
    """SPP annual VER rollup -> CurtailmentReport (CAISO-compatible).

    Reason mapping: Redispatch = congestion-driven (CAISO 'Local'),
    Energy = oversupply (CAISO 'System'), Manual = operator action.
    """
    import pandas as pd

    df = pd.read_csv(rollup_csv)
    curtailed: Dict[str, Dict[str, float]] = {}
    for fuel, cols in VER_COLUMNS.items():
        reasons = {}
        for reason, col in cols.items():
            if col not in df.columns:
                continue
            mwh = float(
                pd.to_numeric(df[col], errors="coerce").sum() * MWH_PER_5MIN
            )
            if mwh > 0:
                reasons[reason] = mwh
        if reasons:
            curtailed[fuel] = reasons

    return CurtailmentReport(
        year=year,
        ba="SWPP",
        curtailed_mwh=curtailed,
        produced_mwh=produced_mwh or {},
        avg_price_usd_mwh=avg_price_usd_mwh,
    )


def swpp_production_from_eia930(
    balance_csvs: Iterable[str | Path],
) -> Dict[str, float]:
    """SWPP annual wind/solar MWh from EIA-930 BALANCE files."""
    import pandas as pd

    cols = {
        "wind": "Net Generation (MW) from Wind (Adjusted)",
        "solar": "Net Generation (MW) from Solar (Adjusted)",
    }
    totals = {"wind": 0.0, "solar": 0.0}
    for path in balance_csvs:
        df = pd.read_csv(
            path,
            usecols=["Balancing Authority", *cols.values()],
            thousands=",",
        )
        swpp = df[df["Balancing Authority"] == "SWPP"]
        for fuel, col in cols.items():
            totals[fuel] += float(
                pd.to_numeric(swpp[col], errors="coerce").sum()
            )
    return totals


def constraint_frames_from_zip(zip_path: str | Path) -> List:
    """DA-BC CSVs from the yearly archive -> list of DataFrames.

    SPP nests archives: the yearly zip holds DA-BC-YEARLY-<yyyy>.csv.zip
    plus monthly/daily variants. The YEARLY rollup is preferred; if
    absent, all plain CSVs (recursing one level into .csv.zip) load."""
    import pandas as pd

    def _read_entry(zf: zipfile.ZipFile, name: str):
        data = zf.read(name)
        if name.lower().endswith(".csv.zip") or name.lower().endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as inner:
                return [
                    pd.read_csv(io.BytesIO(inner.read(n)))
                    for n in inner.namelist()
                    if n.lower().endswith(".csv")
                ]
        return [pd.read_csv(io.BytesIO(data))]

    with zipfile.ZipFile(zip_path) as zf:
        names = [n for n in zf.namelist() if not n.endswith("/")]
        yearly = [n for n in names if "YEARLY" in n.upper()]
        targets = yearly or [
            n for n in names
            if n.lower().endswith(".csv") or n.lower().endswith(".csv.zip")
        ]
        frames = []
        for name in targets:
            frames.extend(_read_entry(zf, name))
    return frames


def aggregate_spp_constraints(frames: List) -> List[dict]:
    """Severity table matching the MISO/PJM semantics."""
    import pandas as pd

    df = pd.concat(frames, ignore_index=True)
    cols = {c.strip().lower(): c for c in df.columns}
    name_col = next(
        (cols[k] for k in cols if "constraint name" in k or k == "constraint"),
        None,
    )
    sp_col = next((cols[k] for k in cols if "shadow price" in k), None)
    if name_col is None or sp_col is None:
        raise ValueError(f"unrecognized SPP DA-BC columns: {list(df.columns)[:12]}")

    df["_sp"] = pd.to_numeric(df[sp_col], errors="coerce").abs()
    df = df.dropna(subset=["_sp"])
    grouped = df.groupby(df[name_col].astype(str).str.strip()).agg(
        binding_hours=("_sp", "size"),
        severity=("_sp", "sum"),
        max_abs_sp=("_sp", "max"),
    )
    table = [
        {"constraint_name": name, "binding_hours": int(r["binding_hours"]),
         "severity": float(r["severity"]), "max_abs_sp": float(r["max_abs_sp"])}
        for name, r in grouped.iterrows()
    ]
    return sorted(table, key=lambda e: -e["severity"])
