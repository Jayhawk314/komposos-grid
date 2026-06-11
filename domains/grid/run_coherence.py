# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Run the grid data coherence check.

Demo on synthetic data (no downloads needed):
    python -m domains.grid.run_coherence --synthetic

Real data (download the workbooks first):
    python -m domains.grid.run_coherence ^
        --egrid path\\to\\egrid2023_data_rev2.xlsx ^
        --eia923 path\\to\\EIA923_Schedules_2_3_4_5_M_12_2023_Final.xlsx ^
        --year 2023

eGRID:   https://www.epa.gov/egrid/detailed-data
EIA-923: https://www.eia.gov/electricity/data/eia923/
"""

from __future__ import annotations

import argparse
import sys

from core.category import Category

from domains.grid.coherence import GridCoherenceChecker, sections_from_records
from domains.grid.crosswalk import discover_crosswalk, write_to_category
from domains.grid.ingest import GridCategoryBuilder
from domains.grid.sources.base import InMemorySource
from domains.grid.sources.egrid import EGridSource
from domains.grid.sources.eia923 import EIA923Source
from domains.grid.sources.synthetic import make_synthetic_pair


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Grid data sheaf coherence check")
    parser.add_argument("--egrid", help="path to eGRID data workbook (.xlsx)")
    parser.add_argument("--eia923", help="path to EIA-923 Schedules 2_3_4_5 workbook")
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--tolerance", type=float, default=0.01,
                        help="relative discrepancy treated as agreement (default 1%%)")
    parser.add_argument("--db", default=":memory:",
                        help="Category SQLite path (default in-memory)")
    parser.add_argument("--synthetic", action="store_true",
                        help="run on synthetic data with injected contradictions")
    parser.add_argument("--no-crosswalk", action="store_true",
                        help="skip facility crosswalk discovery on contradictions")
    args = parser.parse_args(argv)

    if args.synthetic:
        src_a, src_b, planted = make_synthetic_pair()
        sources = [src_a, src_b]
        print(f"[synthetic] planted contradictions at plants: {sorted(planted)}\n")
    else:
        sources = []
        if args.egrid:
            sources.append(EGridSource(args.egrid, year=args.year))
        if args.eia923:
            sources.append(EIA923Source(args.eia923, year=args.year))
        if len(sources) < 2:
            parser.error(
                "need at least two sources (--egrid and --eia923), or --synthetic"
            )

    # Parse each workbook exactly once
    records = {s.name: s.load() for s in sources}
    preloaded = [InMemorySource(name, recs) for name, recs in records.items()]

    category = Category(name="grid", db_path=args.db)
    builder = GridCategoryBuilder(category)
    for name, counts in builder.add_sources(preloaded).items():
        print(f"ingested {name}: {counts}")

    checker = GridCoherenceChecker(category=category, tolerance=args.tolerance)
    sections = sections_from_records(records)
    report = checker.check(sections)

    print()
    print("=== Level 0: plant-ID gluing ===")
    print(report.summary())

    if not report.is_coherent and not args.no_crosswalk:
        crosswalk = discover_crosswalk(
            report,
            {s.source: s for s in sections},
            records,
            tolerance=args.tolerance,
        )
        print()
        print(f"=== Facility crosswalk: {len(crosswalk.merges)} merges discovered ===")
        for m in crosswalk.merges:
            print(
                f"  facility {m.facility_id} <= {' + '.join(m.members)} "
                f"[{m.low_source} split / {m.high_source} merged] "
                f"discrepancy {m.pre_discrepancy:.1%} -> {m.post_discrepancy:.2%}"
            )
        write_to_category(category, crosswalk)

        print()
        print("=== Level 1: facility gluing (pushforward along plant->facility) ===")
        facility_report = checker.check(crosswalk.apply_all(sections))
        print(facility_report.summary())

    print()
    stats = category.statistics()
    print(f"Category: {stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
