# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""NYISO day-ahead zonal LBMP loader and seam-spread computation.

NYISO publishes day-ahead zonal prices keylessly as monthly zips of
daily CSVs (http://mis.nyiso.com/public/csv/damlbmp/
<yyyymm01>damlbmp_zone_csv.zip). Crucially the zone table includes
*proxy buses* for the neighboring systems (PJM, NPX/New England,
O H/Ontario, H Q/Quebec), so a true bidirectional hourly seam spread
is computable from one ISO's own settlement data:

    spread(t) = mean(LBMP internal zones, t) - LBMP(proxy, t)

The mean absolute hourly spread is the evidence figure used by the
congestion join (mean annual *level* differences understate congestion
because the sign flips by hour).
"""

from __future__ import annotations

import glob
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

LBMP_COL = "LBMP ($/MWHr)"
CONGESTION_COL = "Marginal Cost Congestion ($/MWHr)"
LOSS_COL = "Marginal Cost Losses ($/MWHr)"

NYCA_INTERNAL_ZONES = [
    "WEST", "GENESE", "CENTRL", "MHK VL", "NORTH", "CAPITL",
    "HUD VL", "MILLWD", "DUNWOD", "N.Y.C.", "LONGIL",
]
PROXY_PJM = "PJM"
PROXY_NEW_ENGLAND = "NPX"


@dataclass
class SeamSpread:
    proxy: str
    hours: int
    internal_mean_usd_mwh: float
    proxy_mean_usd_mwh: float
    mean_abs_spread_usd_mwh: float
    max_abs_spread_usd_mwh: float
    share_internal_above: float

    def summary(self) -> str:
        return (
            f"NYISO seam vs {self.proxy}: {self.hours} hours, "
            f"internal ${self.internal_mean_usd_mwh:.2f} vs proxy "
            f"${self.proxy_mean_usd_mwh:.2f}, mean |spread| "
            f"${self.mean_abs_spread_usd_mwh:.2f}/MWh "
            f"(max ${self.max_abs_spread_usd_mwh:.2f}), internal above "
            f"{self.share_internal_above:.1%} of hours"
        )


@dataclass(frozen=True)
class SeamComponentSpread:
    """Hourly seam spread split into LBMP, congestion, and loss components."""

    proxy: str
    hours: int
    internal_lbmp_mean_usd_mwh: float
    proxy_lbmp_mean_usd_mwh: float
    mean_abs_lbmp_spread_usd_mwh: float
    max_abs_lbmp_spread_usd_mwh: float
    share_lbmp_internal_above: float
    internal_congestion_mean_usd_mwh: float
    proxy_congestion_mean_usd_mwh: float
    mean_abs_congestion_spread_usd_mwh: float
    max_abs_congestion_spread_usd_mwh: float
    share_congestion_internal_above: float
    internal_loss_mean_usd_mwh: float
    proxy_loss_mean_usd_mwh: float
    mean_abs_loss_spread_usd_mwh: float
    max_abs_loss_spread_usd_mwh: float
    share_loss_internal_above: float

    @property
    def congestion_to_lbmp_ratio(self) -> float:
        if self.mean_abs_lbmp_spread_usd_mwh <= 0:
            return 0.0
        return (
            self.mean_abs_congestion_spread_usd_mwh
            / self.mean_abs_lbmp_spread_usd_mwh
        )

    def summary(self) -> str:
        return (
            f"NYISO seam component audit vs {self.proxy}: {self.hours} hours, "
            f"mean |LBMP spread| ${self.mean_abs_lbmp_spread_usd_mwh:.2f}/MWh, "
            f"mean |congestion-component spread| "
            f"${self.mean_abs_congestion_spread_usd_mwh:.2f}/MWh "
            f"({self.congestion_to_lbmp_ratio:.1%} of LBMP spread), "
            f"mean |loss spread| ${self.mean_abs_loss_spread_usd_mwh:.2f}/MWh"
        )

    def to_evidence_row(self, ba_a: str = "PJM", ba_b: str = "NYIS") -> dict:
        return {
            "ba_a": ba_a,
            "ba_b": ba_b,
            "evidence_source": (
                "NYISO DAM zonal LBMP 2023 settlement components "
                "(mis.nyiso.com; NYCA internal-zone mean vs PJM proxy bus)"
            ),
            "evidence_method": "lmp_component_proxy",
            "mean_price_spread_usd_mwh": self.mean_abs_lbmp_spread_usd_mwh,
            "max_price_spread_usd_mwh": self.max_abs_lbmp_spread_usd_mwh,
            "mean_congestion_component_spread_usd_mwh": (
                self.mean_abs_congestion_spread_usd_mwh
            ),
            "max_congestion_component_spread_usd_mwh": (
                self.max_abs_congestion_spread_usd_mwh
            ),
            "mean_loss_component_spread_usd_mwh": (
                self.mean_abs_loss_spread_usd_mwh
            ),
            "hours_observed": self.hours,
            "notes": (
                "Uses NYISO hourly settlement congestion component, not only "
                "annual hub price level. Congestion component is "
                f"{self.congestion_to_lbmp_ratio:.1%} of mean absolute LBMP "
                f"spread; NYCA LBMP above PJM proxy "
                f"{self.share_lbmp_internal_above:.1%} of hours."
            ),
        }


def load_zone_frames(csv_dir: str | Path):
    import pandas as pd

    files = sorted(glob.glob(str(Path(csv_dir) / "*.csv")))
    if not files:
        raise FileNotFoundError(f"no NYISO zone CSVs under {csv_dir}")
    return pd.concat(pd.read_csv(f) for f in files)


def seam_spread(
    csv_dir: str | Path,
    proxy: str = PROXY_PJM,
    internal_zones: Sequence[str] = NYCA_INTERNAL_ZONES,
) -> SeamSpread:
    df = load_zone_frames(csv_dir)
    pivot = df.pivot_table(index="Time Stamp", columns="Name", values=LBMP_COL)
    missing = [z for z in (*internal_zones, proxy) if z not in pivot.columns]
    if missing:
        raise ValueError(f"zones missing from NYISO data: {missing}")
    internal = pivot[list(internal_zones)].mean(axis=1)
    spread = (internal - pivot[proxy]).dropna()
    return SeamSpread(
        proxy=proxy,
        hours=int(len(spread)),
        internal_mean_usd_mwh=float(internal.mean()),
        proxy_mean_usd_mwh=float(pivot[proxy].mean()),
        mean_abs_spread_usd_mwh=float(spread.abs().mean()),
        max_abs_spread_usd_mwh=float(spread.abs().max()),
        share_internal_above=float((spread > 0).mean()),
    )


def seam_component_spread(
    csv_dir: str | Path,
    proxy: str = PROXY_PJM,
    internal_zones: Sequence[str] = NYCA_INTERNAL_ZONES,
) -> SeamComponentSpread:
    df = load_zone_frames(csv_dir)
    lbmp = _component_stats(df, LBMP_COL, proxy, internal_zones)
    congestion = _component_stats(df, CONGESTION_COL, proxy, internal_zones)
    losses = _component_stats(df, LOSS_COL, proxy, internal_zones)
    return SeamComponentSpread(
        proxy=proxy,
        hours=lbmp["hours"],
        internal_lbmp_mean_usd_mwh=lbmp["internal_mean"],
        proxy_lbmp_mean_usd_mwh=lbmp["proxy_mean"],
        mean_abs_lbmp_spread_usd_mwh=lbmp["mean_abs_spread"],
        max_abs_lbmp_spread_usd_mwh=lbmp["max_abs_spread"],
        share_lbmp_internal_above=lbmp["share_internal_above"],
        internal_congestion_mean_usd_mwh=congestion["internal_mean"],
        proxy_congestion_mean_usd_mwh=congestion["proxy_mean"],
        mean_abs_congestion_spread_usd_mwh=congestion["mean_abs_spread"],
        max_abs_congestion_spread_usd_mwh=congestion["max_abs_spread"],
        share_congestion_internal_above=congestion["share_internal_above"],
        internal_loss_mean_usd_mwh=losses["internal_mean"],
        proxy_loss_mean_usd_mwh=losses["proxy_mean"],
        mean_abs_loss_spread_usd_mwh=losses["mean_abs_spread"],
        max_abs_loss_spread_usd_mwh=losses["max_abs_spread"],
        share_loss_internal_above=losses["share_internal_above"],
    )


def _component_stats(df, column: str, proxy: str, internal_zones: Sequence[str]) -> dict:
    pivot = df.pivot_table(index="Time Stamp", columns="Name", values=column)
    missing = [z for z in (*internal_zones, proxy) if z not in pivot.columns]
    if missing:
        raise ValueError(f"zones missing from NYISO data: {missing}")
    internal = pivot[list(internal_zones)].mean(axis=1)
    spread = (internal - pivot[proxy]).dropna()
    return {
        "hours": int(len(spread)),
        "internal_mean": float(internal.mean()),
        "proxy_mean": float(pivot[proxy].mean()),
        "mean_abs_spread": float(spread.abs().mean()),
        "max_abs_spread": float(spread.abs().max()),
        "share_internal_above": float((spread > 0).mean()),
    }
