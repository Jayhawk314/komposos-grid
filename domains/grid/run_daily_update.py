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
import sys
from datetime import date, timedelta
from pathlib import Path

from domains.grid.daily_update import (
    METRICS_CSV,
    append_metrics,
    daily_pulse,
    miso_day_metrics,
    nyiso_day_spread,
    pjm_day_severity,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Daily grid waste pulse")
    parser.add_argument("--date", help="market date (default: yesterday)")
    parser.add_argument("--cache", default=r"domains\grid\data\daily")
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

    if not metrics:
        print(f"no metrics for {day}; failures: {failures}")
        return 1

    append_metrics(day, metrics)
    pulse = daily_pulse(day, metrics)
    pulse_path = Path("reports/daily") / f"pulse_{day.isoformat()}.md"
    pulse_path.write_text(pulse, encoding="utf-8")

    print(pulse)
    if failures:
        print("partial failures:", "; ".join(failures))
    print(f"metrics ledger: {METRICS_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
