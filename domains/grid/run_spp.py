# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""SPP curtailment + constraint severity (PLAN A3).

    python -m domains.grid.run_spp ^
        --ver-rollup domains\\grid\\data\\spp_ver_2023\\rollup\\2023-VER-Curtailments-ANNUAL-ROLLUP.csv ^
        --bc-zip domains\\grid\\data\\spp_da_bc_2023.zip ^
        --eia930 domains\\grid\\data\\EIA930_BALANCE_2023_Jan_Jun.csv domains\\grid\\data\\EIA930_BALANCE_2023_Jul_Dec.csv

Data: portal.spp.org file-browser-api (keyless); yearly archives under
path=/2023/2023.zip for ver-curtailments and da-binding-constraints.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from domains.grid.sources.spp import (
    aggregate_spp_constraints,
    constraint_frames_from_zip,
    load_ver_curtailments,
    swpp_production_from_eia930,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="SPP curtailment + constraints")
    parser.add_argument("--ver-rollup", help="VER curtailments annual rollup CSV")
    parser.add_argument("--bc-zip", help="da-binding-constraints yearly zip")
    parser.add_argument("--eia930", nargs="*", default=[],
                        help="EIA-930 BALANCE CSVs for production denominators")
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--report-json")
    parser.add_argument("--report-md")
    args = parser.parse_args(argv)

    sections = []
    payload = {"year": args.year}

    if args.ver_rollup:
        produced = (
            swpp_production_from_eia930(args.eia930) if args.eia930 else None
        )
        report = load_ver_curtailments(
            args.ver_rollup, produced_mwh=produced, year=args.year
        )
        sections.append(report.summary())
        payload["curtailment"] = {
            "curtailed_mwh": report.curtailed_mwh,
            "produced_mwh": report.produced_mwh,
        }

    if args.bc_zip:
        table = aggregate_spp_constraints(constraint_frames_from_zip(args.bc_zip))
        total = sum(e["severity"] for e in table)
        lines = [
            f"SPP DA binding constraints {args.year}: {len(table)} constraints, "
            f"total severity {total:,.0f} $/MWh-hours (severity index)",
            "  top constraints:",
        ]
        for e in table[: args.top]:
            lines.append(
                f"    {e['constraint_name']}: {e['binding_hours']} binding "
                f"hours, severity {e['severity']:,.0f}, "
                f"max |SP| ${e['max_abs_sp']:,.0f}/MWh"
            )
        sections.append("\n".join(lines))
        payload["constraints"] = {"total_severity": total, "table": table}

    summary = "\n\n".join(sections)
    print(summary)

    if args.report_json:
        Path(args.report_json).write_text(
            json.dumps(payload, indent=1), encoding="utf-8"
        )
        print(f"wrote SPP JSON: {args.report_json}")
    if args.report_md:
        Path(args.report_md).write_text(
            f"# SPP Curtailment + Constraint Severity {args.year}\n\n"
            f"```\n{summary}\n```\n",
            encoding="utf-8",
        )
        print(f"wrote SPP report: {args.report_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
