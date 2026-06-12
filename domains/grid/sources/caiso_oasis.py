# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""CAISO OASIS PRC_LMP loader with local cache.

OASIS (https://oasis.caiso.com/oasisapi/SingleZip) serves zipped CSVs,
keyless. Empirically established (June 2026):

- ``version=12`` is required for PRC_LMP; v1 returns "no data".
- ``resultformat=6`` yields CSV with one row per (interval, LMP_TYPE):
  LMP (total), MCE (energy), MCC (congestion), MCL (loss); the price is
  in the ``MW`` column.
- Retention is ~39 months: as of June 2026, April 2023 onward exists,
  January-March 2023 is purged. Any evidence produced from partial
  windows must say so.
- Windows are limited to 31 days per request; we chunk to 25 and sleep
  between live fetches (cache hits don't sleep).

Key nodes for the Western seams:

- ``TH_SP15_GEN-APND`` / ``TH_NP15_GEN-APND``: trading hubs.
- ``PALOVRDE_ASR-APND``: Palo Verde scheduling point -- CAISO's own
  hourly price at the Arizona border, the seam node for the CISO-SRP
  corridor.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

BASE_URL = "https://oasis.caiso.com/oasisapi/SingleZip"
PRC_LMP_VERSION = 12
MAX_WINDOW_DAYS = 25
POLITE_DELAY_S = 5.0

NODE_SP15 = "TH_SP15_GEN-APND"
NODE_NP15 = "TH_NP15_GEN-APND"
NODE_PALO_VERDE = "PALOVRDE_ASR-APND"

PRICE_COL = "MW"  # OASIS quirk: the $/MWh value lives in a column named MW


def _window_url(node: str, start: date, end: date, market_run_id: str) -> str:
    return (
        f"{BASE_URL}?queryname=PRC_LMP"
        f"&startdatetime={start:%Y%m%d}T08:00-0000"
        f"&enddatetime={end:%Y%m%d}T08:00-0000"
        f"&version={PRC_LMP_VERSION}&market_run_id={market_run_id}"
        f"&resultformat=6&node={node}"
    )


def _cache_path(cache_dir: Path, node: str, start: date, end: date,
                market_run_id: str) -> Path:
    safe_node = node.replace("/", "_")
    return cache_dir / f"{safe_node}_{market_run_id}_{start:%Y%m%d}_{end:%Y%m%d}.csv"


class OASISError(RuntimeError):
    pass


def fetch_window(
    node: str,
    start: date,
    end: date,
    cache_dir: str | Path,
    market_run_id: str = "DAM",
):
    """One <=31-day PRC_LMP window as a DataFrame, cached as CSV."""
    import io
    import zipfile

    import pandas as pd
    import urllib.request

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = _cache_path(cache_dir, node, start, end, market_run_id)
    if cached.exists():
        return pd.read_csv(cached)

    req = urllib.request.Request(
        _window_url(node, start, end, market_run_id),
        headers={"User-Agent": "Mozilla/5.0 (komposos-grid-domain)"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = resp.read()
    time.sleep(POLITE_DELAY_S)

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        name = zf.namelist()[0]
        if name.endswith(".xml"):
            body = zf.read(name).decode("utf-8", "replace")
            if "No data returned" in body:
                raise OASISError(
                    f"OASIS has no data for {node} {start}..{end} "
                    "(retention is ~39 months)"
                )
            raise OASISError(f"OASIS error for {node} {start}..{end}: {body[-300:]}")
        df = pd.read_csv(io.BytesIO(zf.read(name)))

    df.to_csv(cached, index=False)
    return df


def fetch_range(
    node: str,
    start: date,
    end: date,
    cache_dir: str | Path,
    market_run_id: str = "DAM",
):
    """Inclusive [start, end) chunked into polite windows."""
    import pandas as pd

    frames = []
    cursor = start
    while cursor < end:
        stop = min(cursor + timedelta(days=MAX_WINDOW_DAYS), end)
        frames.append(fetch_window(node, cursor, stop, cache_dir, market_run_id))
        cursor = stop
    return pd.concat(frames, ignore_index=True)


def pivot_components(df):
    """OASIS long format -> one row per interval with LMP/MCC/MCL columns."""
    pivot = df.pivot_table(
        index="INTERVALSTARTTIME_GMT",
        columns="LMP_TYPE",
        values=PRICE_COL,
        aggfunc="first",
    )
    return pivot


@dataclass(frozen=True)
class OASISSeamSpread:
    node_a: str
    node_b: str
    start: str
    end: str
    hours: int
    mean_lmp_a: float
    mean_lmp_b: float
    mean_abs_lmp_spread: float
    max_abs_lmp_spread: float
    share_a_above: float
    mean_abs_congestion_spread: float

    @property
    def congestion_share(self) -> float:
        if self.mean_abs_lmp_spread <= 0:
            return 0.0
        return self.mean_abs_congestion_spread / self.mean_abs_lmp_spread

    def summary(self) -> str:
        return (
            f"OASIS seam {self.node_a} vs {self.node_b} "
            f"[{self.start}..{self.end}]: {self.hours} hours, "
            f"mean LMP ${self.mean_lmp_a:.2f} vs ${self.mean_lmp_b:.2f}, "
            f"mean |spread| ${self.mean_abs_lmp_spread:.2f}/MWh "
            f"(max ${self.max_abs_lmp_spread:.2f}), "
            f"congestion component {self.congestion_share:.1%} of spread, "
            f"{self.node_a} above {self.share_a_above:.1%} of hours"
        )

    def to_evidence_row(self, ba_a: str, ba_b: str) -> dict:
        return {
            "ba_a": ba_a,
            "ba_b": ba_b,
            "evidence_source": (
                f"CAISO OASIS PRC_LMP DAM v{PRC_LMP_VERSION} "
                f"({self.node_a} vs {self.node_b}, {self.start}..{self.end})"
            ),
            "evidence_method": "oasis_settlement_spread",
            "mean_price_spread_usd_mwh": round(self.mean_abs_lmp_spread, 2),
            "max_price_spread_usd_mwh": round(self.max_abs_lmp_spread, 2),
            "mean_congestion_component_spread_usd_mwh": round(
                self.mean_abs_congestion_spread, 2
            ),
            "hours_observed": self.hours,
            "notes": (
                f"Hourly DAM settlement spread; congestion component is "
                f"{self.congestion_share:.1%} of mean |LMP spread|; "
                f"{self.node_a} above {self.share_a_above:.1%} of hours. "
                "Window limited by OASIS ~39-month retention."
            ),
        }


def seam_spread(
    df_a,
    df_b,
    node_a: str,
    node_b: str,
) -> OASISSeamSpread:
    """Hourly settlement spread between two OASIS nodes."""
    a = pivot_components(df_a)
    b = pivot_components(df_b)
    joined = a.join(b, how="inner", lsuffix="_a", rsuffix="_b").dropna(
        subset=["LMP_a", "LMP_b"]
    )
    lmp_spread = joined["LMP_a"] - joined["LMP_b"]
    if "MCC_a" in joined.columns and "MCC_b" in joined.columns:
        mcc_spread = (joined["MCC_a"] - joined["MCC_b"]).abs().mean()
    else:
        mcc_spread = 0.0
    idx = joined.index.sort_values()
    return OASISSeamSpread(
        node_a=node_a,
        node_b=node_b,
        start=str(idx[0])[:10],
        end=str(idx[-1])[:10],
        hours=int(len(joined)),
        mean_lmp_a=float(joined["LMP_a"].mean()),
        mean_lmp_b=float(joined["LMP_b"].mean()),
        mean_abs_lmp_spread=float(lmp_spread.abs().mean()),
        max_abs_lmp_spread=float(lmp_spread.abs().max()),
        share_a_above=float((lmp_spread > 0).mean()),
        mean_abs_congestion_spread=float(mcc_spread),
    )


def ciso_srp_seam(
    cache_dir: str | Path,
    start: date = date(2023, 4, 1),
    end: date = date(2024, 1, 1),
) -> OASISSeamSpread:
    """SP15 hub vs Palo Verde scheduling point: the CISO-SRP corridor
    as priced by CAISO's own settlement system."""
    df_sp15 = fetch_range(NODE_SP15, start, end, cache_dir)
    df_pv = fetch_range(NODE_PALO_VERDE, start, end, cache_dir)
    return seam_spread(df_sp15, df_pv, NODE_SP15, NODE_PALO_VERDE)
