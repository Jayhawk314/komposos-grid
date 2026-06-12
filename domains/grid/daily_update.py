# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Daily grid-waste metrics: yesterday's seams and constraints (PLAN B4).

Fully keyless daily pulse using the per-day files every source already
publishes:

- NYISO: daily DAM zonal CSV
  (mis.nyiso.com/public/csv/damlbmp/<yyyymmdd>damlbmp_zone.csv)
  -> PJM-NYIS seam spread for the day.
- MISO: daily DA ex-post LMP (sources/miso.py fetch_day)
  -> MISO-SWPP and MISO-SOCO seam spreads for the day.
- MISO: daily binding constraints (sources/miso_constraints.fetch_bc_day)
  -> daily constraint severity total + top constraint.
- PJM: da_marginal_value for the day (public key, sources/pjm_dataminer)
  -> daily PJM severity.

Each run appends one row per metric to a long-format CSV ledger
(reports/daily/grid_daily_metrics.csv) keyed by (date, metric), and
rewrites a small Markdown pulse. Append is idempotent per (date,
metric): rerunning a day replaces its rows.

EIA-930 demand/interchange can join later via an EIA API key; omitted
to keep the daily job zero-credential.
"""

from __future__ import annotations

import csv
import io
import urllib.request
import zipfile
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

NYISO_DAY_URL = "http://mis.nyiso.com/public/csv/damlbmp/{day:%Y%m%d}damlbmp_zone.csv"

METRICS_CSV = Path("reports/daily/grid_daily_metrics.csv")
FIELDS = ["date", "metric", "value", "unit", "detail"]


def nyiso_day_spread(day: date, cache_dir: str | Path) -> Optional[dict]:
    """One day's PJM-NYIS seam spread from the daily zonal CSV."""
    import pandas as pd

    from domains.grid.sources.nyiso import (
        LBMP_COL,
        NYCA_INTERNAL_ZONES,
        PROXY_PJM,
    )

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"{day:%Y%m%d}damlbmp_zone.csv"
    if not cached.exists():
        req = urllib.request.Request(
            NYISO_DAY_URL.format(day=day),
            headers={"User-Agent": "Mozilla/5.0 (komposos-grid)"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            cached.write_bytes(resp.read())

    df = pd.read_csv(cached)
    pivot = df.pivot_table(index="Time Stamp", columns="Name", values=LBMP_COL)
    zones = [z for z in NYCA_INTERNAL_ZONES if z in pivot.columns]
    if PROXY_PJM not in pivot.columns or not zones:
        return None
    spread = (pivot[zones].mean(axis=1) - pivot[PROXY_PJM]).dropna()
    return {
        "metric": "pjm_nyis_seam_spread",
        "value": round(float(spread.abs().mean()), 3),
        "unit": "usd_per_mwh",
        "detail": f"hours={len(spread)}",
    }


def miso_day_metrics(day: date, cache_dir: str | Path) -> List[dict]:
    """Seam spreads + constraint severity for one MISO market day."""
    from domains.grid.sources.miso import fetch_day
    from domains.grid.sources.miso_constraints import fetch_bc_day

    out: List[dict] = []
    df = fetch_day(day, Path(cache_dir) / "lmp")
    df = df[df["Value"].isin(["LMP"])]
    he_cols = [c for c in df.columns if c.startswith("HE ")]
    for seam, iface, hub in (
        ("miso_swpp_seam_spread", "SWPP", "ARKANSAS.HUB"),
        ("miso_soco_seam_spread", "SOCO", "MS.HUB"),
    ):
        sub = df[df["Node"].isin([iface, hub])]
        if sub.empty:
            continue
        wide = sub.set_index("Node")[he_cols].T.astype(float)
        if iface not in wide.columns or hub not in wide.columns:
            continue
        spread = (wide[hub] - wide[iface]).dropna()
        out.append({
            "metric": seam,
            "value": round(float(spread.abs().mean()), 3),
            "unit": "usd_per_mwh",
            "detail": f"hours={len(spread)}",
        })

    # da_bc file published on `day` covers market day+1; fetch the file
    # whose market date IS this day (publish day-1)
    bc = fetch_bc_day(day - timedelta(days=1), Path(cache_dir) / "bc")
    severity = float(bc["shadow_price"].abs().sum())
    top = (
        bc.assign(sp=bc["shadow_price"].abs())
        .groupby("constraint_name")["sp"].sum().sort_values(ascending=False)
    )
    out.append({
        "metric": "miso_constraint_severity",
        "value": round(severity, 1),
        "unit": "usd_per_mwh_hours",
        "detail": f"top={top.index[0] if len(top) else 'none'}",
    })
    return out


def pjm_day_severity(day: date, cache_dir: str | Path) -> Optional[dict]:
    from domains.grid.sources.pjm_dataminer import (
        aggregate_pjm_constraints,
        fetch_feed,
        resolve_api_key,
    )

    key = resolve_api_key()
    nxt = day + timedelta(days=1)
    rows = fetch_feed(
        "da_marginal_value",
        {"datetime_beginning_ept":
         f"{day.month}/{day.day}/{day.year} 00:00to"
         f"{nxt.month}/{nxt.day}/{nxt.year} 00:00"},
        key,
        cache_dir,
    )
    if not rows:
        return None
    table = aggregate_pjm_constraints(rows)
    return {
        "metric": "pjm_constraint_severity",
        "value": round(sum(e["severity"] for e in table), 1),
        "unit": "usd_per_mwh_hours",
        "detail": f"top={table[0]['constraint_name'] if table else 'none'}",
    }


def append_metrics(day: date, metrics: List[dict],
                   csv_path: Path = METRICS_CSV) -> None:
    """Idempotent per (date, metric): old rows for the day are replaced."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    existing: List[Dict[str, str]] = []
    if csv_path.exists():
        with open(csv_path, newline="", encoding="utf-8") as fh:
            existing = [
                row for row in csv.DictReader(fh)
                if not (row["date"] == day.isoformat()
                        and any(m["metric"] == row["metric"] for m in metrics))
            ]
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(existing)
        for m in metrics:
            writer.writerow({"date": day.isoformat(), **m})


def daily_pulse(day: date, metrics: List[dict]) -> str:
    lines = [f"# Grid Daily Pulse — {day.isoformat()}", ""]
    for m in metrics:
        lines.append(
            f"- **{m['metric']}**: {m['value']} {m['unit']} ({m['detail']})"
        )
    lines.append("")
    lines.append("Sources: NYISO/MISO/PJM daily public files; see "
                 "domains/grid/daily_update.py for methods.")
    return "\n".join(lines)
