# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""MISO day-ahead ex-post LMP loader and eastern-seam spreads.

MISO publishes daily DA ex-post LMP CSVs keylessly at
https://docs.misoenergy.org/marketreports/<yyyymmdd>_da_expost_lmp.csv
(wide format: one row per Node x Value with HE 1..24 columns; Value in
{LMP, MCC, MLC}; 4 preamble rows). Crucially the node table prices
MISO's *external interfaces* (SOCO, SWPP, TVA, AECI, SPA, ...), so the
same proxy-bus method used for NYISO applies to the eastern seams:

    spread(t) = LMP(adjacent internal hub, t) - LMP(interface, t)

Seam -> reference hub choices (geographic adjacency):
- SOCO interface vs MS.HUB        (MISO South / Southern Company seam)
- SWPP interface vs ARKANSAS.HUB  (MISO South / SPP seam)

Ties with no market on either side (TVA-SOCO, SOCO-FPL/FPC) and seams
where MISO is not an endpoint (AECI-SWPP, SPA-SWPP, CPLE-PJM) cannot
be priced this way and stay structural_only.
"""

from __future__ import annotations

import time
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import List, Sequence

BASE_URL = "https://docs.misoenergy.org/marketreports/{day:%Y%m%d}_da_expost_lmp.csv"
PREAMBLE_ROWS = 4
POLITE_DELAY_S = 0.4

HOUR_COLS = [f"HE {h}" for h in range(1, 25)]


def fetch_day(day: date, cache_dir: str | Path):
    """One daily wide-format report, cached raw."""
    import pandas as pd

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"{day:%Y%m%d}_da_expost_lmp.csv"
    if not cached.exists():
        req = urllib.request.Request(
            BASE_URL.format(day=day),
            headers={"User-Agent": "Mozilla/5.0 (komposos-grid-domain)"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            cached.write_bytes(resp.read())
        time.sleep(POLITE_DELAY_S)
    return pd.read_csv(cached, skiprows=PREAMBLE_ROWS)


def fetch_nodes_range(
    nodes: Sequence[str],
    start: date,
    end: date,
    cache_dir: str | Path,
):
    """Long-format (day, hour, node, value_type, price) for the nodes,
    over [start, end). Missing days are skipped and counted."""
    import pandas as pd

    frames: List = []
    missing = 0
    cursor = start
    while cursor < end:
        try:
            df = fetch_day(cursor, cache_dir)
        except Exception:
            missing += 1
            cursor += timedelta(days=1)
            continue
        sub = df[df["Node"].isin(nodes) & df["Value"].isin(["LMP", "MCC"])]
        melted = sub.melt(
            id_vars=["Node", "Value"],
            value_vars=[c for c in HOUR_COLS if c in sub.columns],
            var_name="he",
            value_name="price",
        )
        melted["day"] = cursor.isoformat()
        frames.append(melted)
        cursor += timedelta(days=1)

    out = pd.concat(frames, ignore_index=True)
    out["price"] = pd.to_numeric(out["price"], errors="coerce")
    out.attrs["missing_days"] = missing
    return out


@dataclass(frozen=True)
class MISOSeamSpread:
    interface: str
    hub: str
    start: str
    end: str
    hours: int
    missing_days: int
    mean_hub: float
    mean_interface: float
    mean_abs_lmp_spread: float
    max_abs_lmp_spread: float
    share_hub_above: float
    mean_abs_congestion_spread: float

    @property
    def congestion_share(self) -> float:
        if self.mean_abs_lmp_spread <= 0:
            return 0.0
        return self.mean_abs_congestion_spread / self.mean_abs_lmp_spread

    def summary(self) -> str:
        return (
            f"MISO seam {self.hub} vs {self.interface} "
            f"[{self.start}..{self.end}, {self.missing_days} days missing]: "
            f"{self.hours} hours, mean LMP ${self.mean_hub:.2f} vs "
            f"${self.mean_interface:.2f}, mean |spread| "
            f"${self.mean_abs_lmp_spread:.2f}/MWh "
            f"(max ${self.max_abs_lmp_spread:.2f}), congestion component "
            f"{self.congestion_share:.1%}, hub above "
            f"{self.share_hub_above:.1%} of hours"
        )

    def to_evidence_row(self, ba_a: str, ba_b: str) -> dict:
        return {
            "ba_a": ba_a,
            "ba_b": ba_b,
            "evidence_source": (
                f"MISO DA ex-post LMP (docs.misoenergy.org; {self.hub} vs "
                f"{self.interface} interface, {self.start}..{self.end})"
            ),
            "evidence_method": "interface_settlement_spread",
            "mean_price_spread_usd_mwh": round(self.mean_abs_lmp_spread, 2),
            "max_price_spread_usd_mwh": round(self.max_abs_lmp_spread, 2),
            "mean_congestion_component_spread_usd_mwh": round(
                self.mean_abs_congestion_spread, 2
            ),
            "hours_observed": self.hours,
            "notes": (
                f"Hourly DA settlement spread, MISO side of the seam; "
                f"congestion component {self.congestion_share:.1%} of mean "
                f"|LMP spread|; {self.hub} above {self.share_hub_above:.1%} "
                f"of hours; {self.missing_days} report days missing."
            ),
        }


def seam_spread(long_df, interface: str, hub: str) -> MISOSeamSpread:
    pivot = long_df.pivot_table(
        index=["day", "he"],
        columns=["Node", "Value"],
        values="price",
        aggfunc="first",
    )
    lmp = (pivot[(hub, "LMP")] - pivot[(interface, "LMP")]).dropna()
    try:
        mcc = (pivot[(hub, "MCC")] - pivot[(interface, "MCC")]).abs().mean()
    except KeyError:
        mcc = 0.0
    days = sorted({d for d, _ in lmp.index})
    return MISOSeamSpread(
        interface=interface,
        hub=hub,
        start=days[0],
        end=days[-1],
        hours=int(len(lmp)),
        missing_days=int(long_df.attrs.get("missing_days", 0)),
        mean_hub=float(pivot[(hub, "LMP")].mean()),
        mean_interface=float(pivot[(interface, "LMP")].mean()),
        mean_abs_lmp_spread=float(lmp.abs().mean()),
        max_abs_lmp_spread=float(lmp.abs().max()),
        share_hub_above=float((lmp > 0).mean()),
        mean_abs_congestion_spread=float(mcc),
    )
