# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""PJM day-ahead constraint severity via Data Miner 2 (PLAN A2).

    $env:PJM_API_KEY = "<subscription key>"
    python -m domains.grid.run_pjm_constraints ^
        --report-json reports\\pjm_constraints_2023.json ^
        --report-md reports\\pjm_constraints_2023.md

The key comes from a free apiportal.pjm.com account and is never
written to the repo.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from domains.grid.sources.pjm_dataminer import (
    aggregate_pjm_constraints,
    fetch_da_constraints_year,
    resolve_api_key,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="PJM DA constraint severity")
    parser.add_argument("--api-key", help="or set PJM_API_KEY")
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--cache", default=r"domains\grid\data\pjm\cache")
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--report-json")
    parser.add_argument("--report-md")
    args = parser.parse_args(argv)

    key = resolve_api_key(args.api_key)
    rows = fetch_da_constraints_year(args.year, key, args.cache)
    table = aggregate_pjm_constraints(rows)

    total = sum(e["severity"] for e in table)
    lines = [
        f"PJM DA binding constraints {args.year}: {len(table)} constraints, "
        f"{len(rows):,} binding-hour rows, total severity {total:,.0f} "
        "$/MWh-hours (severity index; PJM congestion dollars by constraint "
        "come from Market Monitor reports)",
        "  top constraints:",
    ]
    for e in table[: args.top]:
        lines.append(
            f"    {e['constraint_name']}: {e['binding_hours']} binding hours, "
            f"severity {e['severity']:,.0f}, max |SP| ${e['max_abs_sp']:,.0f}/MWh"
        )
    summary = "\n".join(lines)
    print(summary)

    if args.report_json:
        Path(args.report_json).write_text(
            json.dumps({"year": args.year, "total_severity": total,
                        "constraints": table}, indent=1),
            encoding="utf-8",
        )
        print(f"wrote PJM constraint JSON: {args.report_json}")
    if args.report_md:
        Path(args.report_md).write_text(
            f"# PJM DA Constraint Severity {args.year}\n\n```\n{summary}\n```\n",
            encoding="utf-8",
        )
        print(f"wrote PJM constraint report: {args.report_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
