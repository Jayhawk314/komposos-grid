# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Run the CHPE natural experiment on the PJM-NYIS seam.

    python -m domains.grid.run_chpe_event_study

Needs NYISO DAM zone CSVs for Apr 13..Jun 11 in both years:
- 2025: domains/grid/data/nyiso/csv2025 (full-year dir already used by A3)
- 2026: domains/grid/data/nyiso/csv2026 (monthly zips:
  mis.nyiso.com/public/csv/damlbmp/<yyyymm01>damlbmp_zone_csv.zip)
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
import sys

from domains.grid.chpe_event_study import chpe_event_study


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="CHPE COD difference-in-differences on the PJM-NYIS seam"
    )
    parser.add_argument("--csv-dir-2025", default="domains/grid/data/nyiso/csv2025")
    parser.add_argument("--csv-dir-2026", default="domains/grid/data/nyiso/csv2026")
    parser.add_argument("--report-json", default="reports/chpe_event_study.json")
    parser.add_argument("--report-md", default="reports/chpe_event_study.md")
    args = parser.parse_args(argv)

    result = chpe_event_study(args.csv_dir_2025, args.csv_dir_2026)
    print(result.summary())

    payload = {
        "pre_2025": asdict(result.pre_2025),
        "post_2025": asdict(result.post_2025),
        "pre_2026": asdict(result.pre_2026),
        "post_2026": asdict(result.post_2026),
        "did_congestion_usd_mwh": result.did_congestion_usd_mwh,
        "did_lbmp_usd_mwh": result.did_lbmp_usd_mwh,
    }
    Path(args.report_json).write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    Path(args.report_md).write_text(_markdown(result), encoding="utf-8")
    print(f"wrote {args.report_json}")
    print(f"wrote {args.report_md}")
    return 0


def _markdown(result) -> str:
    rows = []
    for w in (result.pre_2025, result.post_2025, result.pre_2026, result.post_2026):
        rows.append(
            f"| {w.label} | {w.start}..{w.end} | {w.days} | {w.hours:,} | "
            f"${w.mean_abs_lbmp_spread_usd_mwh:.2f} | "
            f"${w.mean_abs_congestion_spread_usd_mwh:.2f} | "
            f"{w.share_lbmp_internal_above:.1%} |"
        )
    direction = (
        "COMPRESSION beyond seasonality"
        if result.did_congestion_usd_mwh < 0
        else "NO compression beyond seasonality"
    )
    return "\n".join([
        "# CHPE Event Study - PJM-NYIS Seam",
        "",
        "CHPE (1,250 MW HVDC Quebec->Queens) reached commercial operation",
        "2026-05-13. Difference-in-differences on the NYISO DAM seam spread",
        "vs the PJM proxy bus, 2025 as the seasonal control.",
        "",
        "| Window | Dates | Days | Hours | Mean \\|LBMP spread\\| | Congestion component | NY above |",
        "|---|---|---:|---:|---:|---:|---:|",
        *rows,
        "",
        f"**DiD congestion component: {result.did_congestion_usd_mwh:+.2f} $/MWh**",
        f"(LBMP spread DiD {result.did_lbmp_usd_mwh:+.2f} $/MWh) - {direction}.",
        "",
        "One month of post-COD data: screening-grade. Rerun with more post",
        "months before adjusting the corridor's annual value.",
        "",
    ])


if __name__ == "__main__":
    sys.exit(main())
