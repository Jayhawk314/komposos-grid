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

from domains.grid.coherence import (
    GridCoherenceChecker,
    Section,
    ba_mapping_from_records,
    pushforward,
    sections_from_records,
)
from domains.grid.ba_repair import (
    consensus_accounting,
    consensus_entity_states,
    propose_ba_footprint_repair,
    write_repair_to_category,
)
from domains.grid.ba_footprint_crosswalk import (
    build_ba_footprint_crosswalk,
    interchange_neighbors_from_ties,
    write_crosswalk_to_category,
)
from domains.grid.ba_footprint_report import build_ba_footprint_report
from domains.grid.ba_review import (
    apply_review_decisions,
    export_review_template_csv,
    export_review_template_json,
    load_review_decisions,
    write_review_to_category,
)
from domains.grid.ba_dashboard import (
    export_footprint_report_html,
    export_review_html,
)
from domains.grid.crosswalk import discover_crosswalk, write_to_category
from domains.grid.ingest import GridCategoryBuilder
from domains.grid.sources.base import InMemorySource
from domains.grid.sources.egrid import EGridSource
from domains.grid.sources.eia923 import EIA923Source
from domains.grid.sheaf_audit import sheaf_audit
from domains.grid.sources.eia930 import EIA930Source
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
    parser.add_argument("--eia930", nargs="+", metavar="CSV",
                        help="EIA-930 BALANCE six-month CSVs (enables the "
                             "BA-level coherence check)")
    parser.add_argument("--eia930-interchange", nargs="+", metavar="CSV",
                        help="optional EIA-930 INTERCHANGE CSVs; when provided, "
                             "BA footprint corrections must follow observed ties")
    parser.add_argument("--ba-tolerance", type=float, default=0.05,
                        help="relative discrepancy treated as agreement at BA "
                             "level (default 5%%; telemetry vs accounting)")
    parser.add_argument("--ba-repair-csv",
                        help="write validated BA footprint candidates to CSV")
    parser.add_argument("--ba-repair-json",
                        help="write validated BA footprint candidates to JSON")
    parser.add_argument("--ba-footprint-report-md",
                        help="write before/after BA footprint report to Markdown")
    parser.add_argument("--ba-footprint-report-json",
                        help="write before/after BA footprint report to JSON")
    parser.add_argument("--ba-footprint-report-html",
                        help="write before/after BA footprint dashboard to HTML")
    parser.add_argument("--ba-review-template-csv",
                        help="write editable BA correction review template to CSV")
    parser.add_argument("--ba-review-template-json",
                        help="write editable BA correction review template to JSON")
    parser.add_argument("--ba-review-decisions",
                        help="CSV/JSON review decisions to apply as curated BA corrections")
    parser.add_argument("--ba-review-allow-overrides", action="store_true",
                        help="allow reviewers to accept machine-rejected candidates")
    parser.add_argument("--ba-reviewed-csv",
                        help="write curated BA correction review result to CSV")
    parser.add_argument("--ba-reviewed-json",
                        help="write curated BA correction review result to JSON")
    parser.add_argument("--ba-reviewed-report-md",
                        help="write curated before/after BA report to Markdown")
    parser.add_argument("--ba-reviewed-report-json",
                        help="write curated before/after BA report to JSON")
    parser.add_argument("--ba-reviewed-report-html",
                        help="write curated before/after BA dashboard to HTML")
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

        if crosswalk.merges:
            print()
            print("=== Level 1: facility gluing (pushforward along plant->facility) ===")
            facility_sections = crosswalk.apply_all(sections)
            facility_report = checker.check(facility_sections)
            print(facility_report.summary())
            sections = facility_sections  # downstream audits use reconciled sections

    print()
    print(sheaf_audit(sections).summary())

    if args.eia930:
        print()
        print("=== Level 2: BA gluing (plant sections pushed along plant->BA, "
              "vs EIA-930 telemetry) ===")
        eia930 = EIA930Source(args.eia930, year=args.year)
        ba_sections = [
            Section(source="eia930", values=eia930.section())
        ]
        for section in sections:
            mapping = ba_mapping_from_records(records[section.source])
            if not mapping:
                continue
            ba_sections.append(
                pushforward(section, mapping, source=f"{section.source}@ba")
            )

        if category.get("source:eia930") is None:
            category.add("source:eia930", type_name="data_source")
        for s in ba_sections[1:]:
            if category.get(f"source:{s.source}") is None:
                category.add(f"source:{s.source}", type_name="data_source")

        ba_checker = GridCoherenceChecker(
            category=category,
            tolerance=args.ba_tolerance,
            key_namer=lambda code: f"ba:{code}",
        )
        print(ba_checker.check(ba_sections).summary())
        print()
        print(sheaf_audit(ba_sections).summary())
        accounting, entity_to_ba, mapping_conflicts = consensus_accounting(
            sections,
            records,
        )
        entity_state, ba_states = consensus_entity_states(
            sections,
            records,
            entity_to_ba,
        )
        repair = propose_ba_footprint_repair(
            telemetry=ba_sections[0],
            accounting=accounting,
            entity_to_ba=entity_to_ba,
            entity_state=entity_state,
            ba_states=ba_states,
            tolerance=args.ba_tolerance,
        )
        write_repair_to_category(category, repair)
        print()
        print(repair.summary())
        interchange_neighbors = None
        if args.eia930_interchange:
            from domains.grid.flow_geometry import load_interchange

            interchange_neighbors = interchange_neighbors_from_ties(
                load_interchange(args.eia930_interchange)
            )
        footprint_crosswalk = build_ba_footprint_crosswalk(
            report=repair,
            telemetry=ba_sections[0],
            accounting=accounting,
            entity_to_ba=entity_to_ba,
            entity_state=entity_state,
            ba_states=ba_states,
            interchange_neighbors=interchange_neighbors,
            tolerance=args.ba_tolerance,
        )
        write_crosswalk_to_category(category, footprint_crosswalk)
        print()
        print(footprint_crosswalk.summary())
        footprint_report = build_ba_footprint_report(
            telemetry=ba_sections[0],
            accounting=accounting,
            base_mapping=entity_to_ba,
            crosswalk=footprint_crosswalk,
            tolerance=args.ba_tolerance,
        )
        print()
        print(footprint_report.summary())
        if args.ba_repair_csv:
            footprint_crosswalk.export_csv(args.ba_repair_csv, records, sections)
            print(f"  wrote BA repair CSV: {args.ba_repair_csv}")
        if args.ba_repair_json:
            footprint_crosswalk.export_json(args.ba_repair_json, records, sections)
            print(f"  wrote BA repair JSON: {args.ba_repair_json}")
        if args.ba_footprint_report_md:
            footprint_report.export_markdown(args.ba_footprint_report_md)
            print(f"  wrote BA footprint report: {args.ba_footprint_report_md}")
        if args.ba_footprint_report_json:
            footprint_report.export_json(args.ba_footprint_report_json)
            print(f"  wrote BA footprint report JSON: {args.ba_footprint_report_json}")
        if args.ba_footprint_report_html:
            export_footprint_report_html(
                footprint_report,
                args.ba_footprint_report_html,
            )
            print(f"  wrote BA footprint dashboard: {args.ba_footprint_report_html}")
        if args.ba_review_template_csv:
            export_review_template_csv(
                footprint_crosswalk,
                args.ba_review_template_csv,
                records,
                sections,
            )
            print(f"  wrote BA review template CSV: {args.ba_review_template_csv}")
        if args.ba_review_template_json:
            export_review_template_json(
                footprint_crosswalk,
                args.ba_review_template_json,
                records,
                sections,
            )
            print(f"  wrote BA review template JSON: {args.ba_review_template_json}")
        if args.ba_review_decisions:
            decisions = load_review_decisions(args.ba_review_decisions)
            reviewed = apply_review_decisions(
                crosswalk=footprint_crosswalk,
                decisions=decisions,
                telemetry=ba_sections[0],
                accounting=accounting,
                entity_to_ba=entity_to_ba,
                tolerance=args.ba_tolerance,
                allow_machine_rejected=args.ba_review_allow_overrides,
            )
            write_review_to_category(category, reviewed)
            print()
            print(reviewed.summary())
            reviewed_report = build_ba_footprint_report(
                telemetry=ba_sections[0],
                accounting=accounting,
                base_mapping=entity_to_ba,
                crosswalk=reviewed.curated_crosswalk,
                tolerance=args.ba_tolerance,
            )
            print()
            print(reviewed_report.summary())
            if args.ba_reviewed_csv:
                reviewed.export_csv(args.ba_reviewed_csv, records, sections)
                print(f"  wrote curated BA review CSV: {args.ba_reviewed_csv}")
            if args.ba_reviewed_json:
                reviewed.export_json(args.ba_reviewed_json, records, sections)
                print(f"  wrote curated BA review JSON: {args.ba_reviewed_json}")
            if args.ba_reviewed_report_md:
                reviewed_report.export_markdown(args.ba_reviewed_report_md)
                print(f"  wrote curated BA report: {args.ba_reviewed_report_md}")
            if args.ba_reviewed_report_json:
                reviewed_report.export_json(args.ba_reviewed_report_json)
                print(
                    "  wrote curated BA report JSON: "
                    f"{args.ba_reviewed_report_json}"
                )
            if args.ba_reviewed_report_html:
                export_review_html(
                    reviewed,
                    args.ba_reviewed_report_html,
                    reviewed_report=reviewed_report,
                )
                print(
                    "  wrote curated BA dashboard: "
                    f"{args.ba_reviewed_report_html}"
                )
        if mapping_conflicts:
            print(
                f"  note: {len(mapping_conflicts)} entities had conflicting BA "
                "registrations across accounting sources; majority vote used"
            )

    print()
    stats = category.statistics()
    print(f"Category: {stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
