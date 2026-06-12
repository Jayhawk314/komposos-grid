# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Constraint-level congestion structure for MISO (PLAN A2, keyless half).

    python -m domains.grid.run_miso_constraints ^
        --report-json reports\\miso_constraints_2023.json ^
        --report-md reports\\miso_constraints_2023.md
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from domains.grid.sources.miso_constraints import fetch_constraint_report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="MISO binding constraint severity")
    parser.add_argument("--cache", default=r"domains\grid\data\miso\bc_cache")
    parser.add_argument("--start", default="2023-01-01")
    parser.add_argument("--end", default="2024-01-01")
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--report-json")
    parser.add_argument("--report-md")
    args = parser.parse_args(argv)

    report = fetch_constraint_report(
        date.fromisoformat(args.start), date.fromisoformat(args.end), args.cache
    )
    summary = report.summary(top=args.top)
    print(summary)

    if args.report_json:
        Path(args.report_json).write_text(
            json.dumps(report.to_dict(), indent=1), encoding="utf-8"
        )
        print(f"wrote constraint JSON: {args.report_json}")
    if args.report_md:
        Path(args.report_md).write_text(
            f"# MISO Binding Constraint Severity\n\n```\n{summary}\n```\n",
            encoding="utf-8",
        )
        print(f"wrote constraint report: {args.report_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
