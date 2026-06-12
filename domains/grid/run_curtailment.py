# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Run the CAISO curtailment waste quantification.

    python -m domains.grid.run_curtailment ^
        --caiso domains\\grid\\data\\caiso_production_curtailments_2023.xlsx ^
        --avg-price 64.85

Data: https://www.caiso.com/documents/productionandcurtailmentsdata_<year>.xlsx
(keyless). --avg-price is the annual hub average used only for the
labeled upper-bound valuation (SP15 2023 = 64.85 from EIA ICE data).
"""

from __future__ import annotations

import argparse
import sys

from domains.grid.curtailment import load_caiso_report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="CAISO curtailment waste")
    parser.add_argument("--caiso", required=True,
                        help="CAISO production and curtailments workbook")
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--avg-price", type=float, default=None,
                        help="annual avg hub price for upper-bound valuation")
    args = parser.parse_args(argv)

    report = load_caiso_report(
        args.caiso, year=args.year, avg_price_usd_mwh=args.avg_price
    )
    print(report.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
