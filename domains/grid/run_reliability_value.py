# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Run the reliability waste valuation (PLAN A1).

    python -m domains.grid.run_reliability_value ^
        --outages domains\\grid\\data\\eaglei_outages_2023.csv ^
        --mcc domains\\grid\\data\\eaglei_mcc.csv ^
        --report-json reports\\reliability_valuation_2023.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from domains.grid.outages import aggregate_outages, load_mcc
from domains.grid.reliability_value import value_outages


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Reliability waste valuation")
    parser.add_argument("--outages", required=True)
    parser.add_argument("--mcc", required=True)
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--report-json")
    parser.add_argument("--report-md")
    args = parser.parse_args(argv)

    outage_report = aggregate_outages(
        args.outages, load_mcc(args.mcc), year=args.year
    )
    valuation = value_outages(outage_report)
    summary = valuation.summary()
    print(summary)

    if args.report_json:
        valuation.export_json(args.report_json)
        print(f"wrote valuation JSON: {args.report_json}")
    if args.report_md:
        Path(args.report_md).write_text(
            f"# Reliability Waste Valuation {args.year}\n\n```\n{summary}\n```\n",
            encoding="utf-8",
        )
        print(f"wrote valuation report: {args.report_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
