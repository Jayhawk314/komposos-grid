# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Run the daily grid-waste pulse (PLAN B4).

    python -m domains.grid.run_daily_update            # yesterday
    python -m domains.grid.run_daily_update --date 2026-06-10

Appends to reports/daily/grid_daily_metrics.csv (idempotent per
date+metric) and writes reports/daily/pulse_<date>.md. Designed to run
under a scheduler; every source is keyless.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import List

from domains.grid.daily_update import (
    METRICS_CSV,
    append_metrics,
    daily_pulse,
    miso_day_metrics,
    nyiso_day_spread,
    pjm_day_severity,
)

_INTERCHANGE_RE = re.compile(
    r"EIA930_INTERCHANGE_(\d{4})_(Jan_Jun|Jul_Dec)\.csv$"
)


def _interchange_halves(data_dir: str | Path) -> dict[int, dict[str, Path]]:
    halves: dict[int, dict[str, Path]] = {}
    for path in Path(data_dir).glob("EIA930_INTERCHANGE_*.csv"):
        m = _INTERCHANGE_RE.search(path.name)
        if m:
            halves.setdefault(int(m.group(1)), {})[m.group(2)] = path
    return halves


def latest_interchange_csvs(data_dir: str | Path) -> List[Path]:
    """The most recent year's INTERCHANGE half-files present, if complete."""
    halves = _interchange_halves(data_dir)
    for year in sorted(halves, reverse=True):
        if {"Jan_Jun", "Jul_Dec"} <= halves[year].keys():
            return [halves[year]["Jan_Jun"], halves[year]["Jul_Dec"]]
    return []


def all_interchange_years(data_dir: str | Path) -> dict[str, List[Path]]:
    """{year: [Jan_Jun, Jul_Dec]} for every complete INTERCHANGE year present."""
    halves = _interchange_halves(data_dir)
    return {
        str(year): [halves[year]["Jan_Jun"], halves[year]["Jul_Dec"]]
        for year in sorted(halves)
        if {"Jan_Jun", "Jul_Dec"} <= halves[year].keys()
    }


def publish_site(data_dir: str | Path = r"domains\grid\data",
                 reports_dir: str | Path = "reports") -> List[str]:
    """Regenerate the published dashboard and interactive map. Non-fatal."""
    from domains.grid.dashboard import build_dashboard_html, load_inputs
    from domains.grid.network_map import build_multiyear

    notes: List[str] = []
    try:
        inputs = load_inputs(reports_dir)
        html = build_dashboard_html(
            cards=inputs["cards"], studies=inputs["studies"],
            projects=inputs["projects"], chpe=inputs["chpe"],
        )
        out = Path("docs/index.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        notes.append(f"dashboard: {out}")
    except Exception as exc:
        notes.append(f"dashboard failed: {exc}")

    try:
        years = all_interchange_years(data_dir)
        if years:
            egrid = Path(data_dir) / "egrid2023_data_rev2.xlsx"
            path = build_multiyear(
                years, path="docs/network_map.html",
                egrid_workbook=egrid if egrid.exists() else None,
            )
            notes.append(f"network map ({'/'.join(years)}): {path}")
        else:
            notes.append("network map skipped: no complete INTERCHANGE year found")
    except Exception as exc:
        notes.append(f"network map failed: {exc}")
    return notes


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Daily grid waste pulse")
    parser.add_argument("--date", help="market date (default: yesterday)")
    parser.add_argument("--cache", default=r"domains\grid\data\daily")
    parser.add_argument("--data-dir", default=r"domains\grid\data",
                        help="where EIA-930 INTERCHANGE CSVs live (for the map)")
    parser.add_argument("--no-publish", action="store_true",
                        help="skip regenerating docs/ dashboard + network map")
    args = parser.parse_args(argv)

    day = (
        date.fromisoformat(args.date) if args.date
        else date.today() - timedelta(days=1)
    )

    metrics = []
    failures = []
    for name, fn in (
        ("nyiso", lambda: [m for m in [nyiso_day_spread(day, Path(args.cache) / "nyiso")] if m]),
        ("miso", lambda: miso_day_metrics(day, Path(args.cache) / "miso")),
        ("pjm", lambda: [m for m in [pjm_day_severity(day, Path(args.cache) / "pjm")] if m]),
    ):
        try:
            metrics.extend(fn())
        except Exception as exc:
            failures.append(f"{name}: {exc}")

    if metrics:
        append_metrics(day, metrics)
        pulse = daily_pulse(day, metrics)
        pulse_path = Path("reports/daily") / f"pulse_{day.isoformat()}.md"
        pulse_path.write_text(pulse, encoding="utf-8")
        print(pulse)
        print(f"metrics ledger: {METRICS_CSV}")
    else:
        print(f"no metrics for {day}; failures: {failures}")

    if not args.no_publish:
        for note in publish_site(args.data_dir):
            print(f"published {note}")

    if failures:
        print("partial failures:", "; ".join(failures))
    return 0 if metrics else 1


if __name__ == "__main__":
    sys.exit(main())
