# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""ERCOT West-North hub congestion spread, multi-year (PLAN A3).

    python -m domains.grid.run_ercot ^
        --zips domains\\grid\\data\\ercot_damlzhb_2023.zip ^
               domains\\grid\\data\\ercot_damlzhb_2024.zip ^
               domains\\grid\\data\\ercot_damlzhb_2025.zip ^
        --report-json reports\\ercot_hub_spreads.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from domains.grid.sources.ercot import hub_spread, load_dam_prices


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="ERCOT hub spread analysis")
    parser.add_argument("--zips", nargs="+", required=True)
    parser.add_argument("--hub-a", default="HB_WEST")
    parser.add_argument("--hub-b", default="HB_NORTH")
    parser.add_argument("--report-json")
    parser.add_argument("--report-md")
    args = parser.parse_args(argv)

    results = []
    for path in args.zips:
        match = re.search(r"(20\d\d)", Path(path).name)
        year = int(match.group(1)) if match else 0
        df = load_dam_prices(path)
        result = hub_spread(df, args.hub_a, args.hub_b, year=year)
        print(result.summary())
        results.append(result.to_dict())

    if args.report_json:
        Path(args.report_json).write_text(
            json.dumps(results, indent=1), encoding="utf-8"
        )
        print(f"wrote ERCOT JSON: {args.report_json}")
    if args.report_md:
        Path(args.report_md).write_text(
            "# ERCOT Hub Congestion Spreads\n\n```\n"
            + "\n".join(
                f"{r['year']}: mean |spread| ${r['mean_abs_spread_usd_mwh']:.2f}/MWh"
                for r in results
            )
            + "\n```\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
