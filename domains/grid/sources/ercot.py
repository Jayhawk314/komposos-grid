# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""ERCOT DAM hub/zone prices (PLAN A3).

Keyless yearly files: the MIS document list
(www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13060)
indexes DAMLZHBSPP_<year> zips; each holds one xlsx with monthly
sheets of hourly settlement point prices (hubs HB_*, load zones LZ_*).

ERCOT is a single BA (no seams in the tie list), so the deliverable is
*intra-ISO* congestion: the hourly spread between hubs. HB_WEST vs
HB_NORTH is the canonical West Texas wind-export signal -- the ERCOT
counterpart of the MISO/SPP wind-belt constraints.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

HUB_WEST = "HB_WEST"
HUB_NORTH = "HB_NORTH"


def load_dam_prices(zip_path: str | Path):
    """Yearly DAMLZHBSPP zip -> long DataFrame (date, hour, point, price)."""
    import pandas as pd

    with zipfile.ZipFile(zip_path) as zf:
        inner = [n for n in zf.namelist() if n.lower().endswith(".xlsx")][0]
        with zf.open(inner) as fh:
            xl = pd.ExcelFile(fh.read())
    frames = [xl.parse(sheet) for sheet in xl.sheet_names]
    df = pd.concat(frames, ignore_index=True)
    df.columns = [str(c).strip() for c in df.columns]
    df["Settlement Point Price"] = pd.to_numeric(
        df["Settlement Point Price"], errors="coerce"
    )
    return df.dropna(subset=["Settlement Point Price"])


@dataclass(frozen=True)
class HubSpread:
    hub_a: str
    hub_b: str
    year: int
    hours: int
    mean_a: float
    mean_b: float
    mean_abs_spread: float
    max_abs_spread: float
    share_a_above: float

    def summary(self) -> str:
        return (
            f"ERCOT {self.year} {self.hub_a} vs {self.hub_b}: "
            f"{self.hours} hours, mean ${self.mean_a:.2f} vs "
            f"${self.mean_b:.2f}, mean |spread| "
            f"${self.mean_abs_spread:.2f}/MWh "
            f"(max ${self.max_abs_spread:,.0f}), {self.hub_a} above "
            f"{self.share_a_above:.1%} of hours"
        )

    def to_dict(self) -> dict:
        return {
            "hub_a": self.hub_a, "hub_b": self.hub_b, "year": self.year,
            "hours": self.hours, "mean_a": self.mean_a, "mean_b": self.mean_b,
            "mean_abs_spread_usd_mwh": self.mean_abs_spread,
            "max_abs_spread_usd_mwh": self.max_abs_spread,
            "share_a_above": self.share_a_above,
        }


def hub_spread(
    df,
    hub_a: str = HUB_WEST,
    hub_b: str = HUB_NORTH,
    year: int = 0,
) -> HubSpread:
    pivot = df[df["Settlement Point"].isin([hub_a, hub_b])].pivot_table(
        index=["Delivery Date", "Hour Ending"],
        columns="Settlement Point",
        values="Settlement Point Price",
        aggfunc="first",
    ).dropna()
    spread = pivot[hub_a] - pivot[hub_b]
    return HubSpread(
        hub_a=hub_a,
        hub_b=hub_b,
        year=year,
        hours=int(len(pivot)),
        mean_a=float(pivot[hub_a].mean()),
        mean_b=float(pivot[hub_b].mean()),
        mean_abs_spread=float(spread.abs().mean()),
        max_abs_spread=float(spread.abs().max()),
        share_a_above=float((spread > 0).mean()),
    )
