# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""CHPE natural experiment on the PJM-NYIS seam.

Champlain Hudson Power Express (1,250 MW HVDC Quebec->Queens) reached
commercial operation 2026-05-13. If NYC supply scarcity drove the
exploding PJM-NYIS spread (2025 congestion component 7.38 $/MWh, NY
above PJM 97.9% of hours), the spread should compress after COD.

Difference-in-differences on NYISO DAM settlement components:

    DiD = (post2026 - pre2026) - (post2025 - pre2025)

with pre = Apr 13..May 12 and post = May 13..Jun 11 in both years.
The 2025 cells control for the seasonal spring->summer shift; a
negative DiD on the congestion component is spread compression beyond
seasonality. One month of post data is screening-grade only.
"""

from __future__ import annotations

import glob
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List, Sequence

from domains.grid.sources.nyiso import (
    NYCA_INTERNAL_ZONES,
    PROXY_PJM,
    CONGESTION_COL,
    LBMP_COL,
    _component_stats,
)

CHPE_COD = date(2026, 5, 13)
PRE_START_MD = (4, 13)
PRE_END_MD = (5, 12)
POST_START_MD = (5, 13)
POST_END_MD = (6, 11)

_DATE_RE = re.compile(r"(\d{8})damlbmp_zone\.csv$")


@dataclass(frozen=True)
class WindowSpread:
    label: str
    start: date
    end: date
    days: int
    hours: int
    mean_abs_lbmp_spread_usd_mwh: float
    mean_abs_congestion_spread_usd_mwh: float
    share_lbmp_internal_above: float

    def summary(self) -> str:
        return (
            f"{self.label} [{self.start}..{self.end}, {self.days} days]: "
            f"{self.hours} hours, mean |LBMP spread| "
            f"${self.mean_abs_lbmp_spread_usd_mwh:.2f}/MWh, congestion "
            f"component ${self.mean_abs_congestion_spread_usd_mwh:.2f}/MWh, "
            f"NY above {self.share_lbmp_internal_above:.1%} of hours"
        )


@dataclass(frozen=True)
class EventStudyResult:
    pre_2025: WindowSpread
    post_2025: WindowSpread
    pre_2026: WindowSpread
    post_2026: WindowSpread

    @property
    def did_congestion_usd_mwh(self) -> float:
        return (
            self.post_2026.mean_abs_congestion_spread_usd_mwh
            - self.pre_2026.mean_abs_congestion_spread_usd_mwh
        ) - (
            self.post_2025.mean_abs_congestion_spread_usd_mwh
            - self.pre_2025.mean_abs_congestion_spread_usd_mwh
        )

    @property
    def did_lbmp_usd_mwh(self) -> float:
        return (
            self.post_2026.mean_abs_lbmp_spread_usd_mwh
            - self.pre_2026.mean_abs_lbmp_spread_usd_mwh
        ) - (
            self.post_2025.mean_abs_lbmp_spread_usd_mwh
            - self.pre_2025.mean_abs_lbmp_spread_usd_mwh
        )

    def summary(self) -> str:
        lines = [w.summary() for w in
                 (self.pre_2025, self.post_2025, self.pre_2026, self.post_2026)]
        lines.append(
            f"DiD (post-pre, 2026 vs 2025): congestion component "
            f"{self.did_congestion_usd_mwh:+.2f} $/MWh, LBMP spread "
            f"{self.did_lbmp_usd_mwh:+.2f} $/MWh "
            f"(negative = compression beyond seasonality)"
        )
        return "\n".join(lines)


def _files_in_window(csv_dir: str | Path, start: date, end: date) -> List[str]:
    out = []
    for path in sorted(glob.glob(str(Path(csv_dir) / "*damlbmp_zone.csv"))):
        match = _DATE_RE.search(path)
        if not match:
            continue
        stamp = match.group(1)
        day = date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:8]))
        if start <= day <= end:
            out.append(path)
    return out


def windowed_component_spread(
    csv_dir: str | Path,
    start: date,
    end: date,
    label: str,
    proxy: str = PROXY_PJM,
    internal_zones: Sequence[str] = NYCA_INTERNAL_ZONES,
) -> WindowSpread:
    import pandas as pd

    files = _files_in_window(csv_dir, start, end)
    if not files:
        raise FileNotFoundError(
            f"no NYISO zone CSVs in {csv_dir} for {start}..{end}"
        )
    df = pd.concat(pd.read_csv(f) for f in files)
    lbmp = _component_stats(df, LBMP_COL, proxy, internal_zones)
    congestion = _component_stats(df, CONGESTION_COL, proxy, internal_zones)
    return WindowSpread(
        label=label,
        start=start,
        end=end,
        days=len(files),
        hours=lbmp["hours"],
        mean_abs_lbmp_spread_usd_mwh=lbmp["mean_abs_spread"],
        mean_abs_congestion_spread_usd_mwh=congestion["mean_abs_spread"],
        share_lbmp_internal_above=lbmp["share_internal_above"],
    )


def chpe_event_study(
    csv_dir_2025: str | Path,
    csv_dir_2026: str | Path,
    proxy: str = PROXY_PJM,
) -> EventStudyResult:
    def window(year: int, start_md, end_md):
        return (date(year, *start_md), date(year, *end_md))

    cells = {}
    for year, csv_dir in ((2025, csv_dir_2025), (2026, csv_dir_2026)):
        for phase, (s_md, e_md) in (
            ("pre", (PRE_START_MD, PRE_END_MD)),
            ("post", (POST_START_MD, POST_END_MD)),
        ):
            start, end = window(year, s_md, e_md)
            cells[(phase, year)] = windowed_component_spread(
                csv_dir, start, end, label=f"{phase}-{year}", proxy=proxy
            )
    return EventStudyResult(
        pre_2025=cells[("pre", 2025)],
        post_2025=cells[("post", 2025)],
        pre_2026=cells[("pre", 2026)],
        post_2026=cells[("post", 2026)],
    )
