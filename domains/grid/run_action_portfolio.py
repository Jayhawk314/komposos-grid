# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Build a decision action portfolio from the grid waste ledger."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from domains.grid.action_portfolio import build_action_portfolio


DEFAULT_LEDGER = Path("reports/grid_waste_ledger.json")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Grid action portfolio")
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    parser.add_argument("--report-csv", default="reports/grid_action_portfolio.csv")
    parser.add_argument("--report-json", default="reports/grid_action_portfolio.json")
    parser.add_argument("--report-md", default="reports/grid_action_portfolio.md")
    parser.add_argument("--report-html", default="reports/grid_action_dashboard.html")
    args = parser.parse_args(argv)

    ledger = Path(args.ledger)
    if not ledger.exists():
        parser.error(
            f"ledger does not exist: {ledger}. Run domains.grid.run_waste_ledger first."
        )

    portfolio = build_action_portfolio(ledger)
    print(portfolio.summary())
    portfolio.export_csv(args.report_csv)
    portfolio.export_json(args.report_json)
    portfolio.export_markdown(args.report_md)
    portfolio.export_html(args.report_html)
    print(f"wrote grid action portfolio CSV: {args.report_csv}")
    print(f"wrote grid action portfolio JSON: {args.report_json}")
    print(f"wrote grid action portfolio report: {args.report_md}")
    print(f"wrote grid action dashboard: {args.report_html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
