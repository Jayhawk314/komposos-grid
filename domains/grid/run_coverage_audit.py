# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""LBNL "Queued Up" milestone-field coverage audit, by region and status.

Turns the SPP "post-IA is not computable" observation (found by accident while
building run_stitch_brief.py) into a systematic, national result: for every
region this project tracks and every project status, how completely are the
fields a queue-process analysis depends on actually populated?

The central distinction this file exists to preserve: a missing field is a
statement about what the public data can OBSERVE, never a statement about what
happened. A withdrawn project with no ia_date is not known to have skipped
signing an interconnection agreement -- LBNL's data simply does not record
whether it did. See `POST_IA_OBSERVABILITY_NOTE` below; that wording is
load-bearing and must not be paraphrased into a stronger claim anywhere this
module's output is rendered.

Scope: this reports at the region level only (the 9 BA/RTO groupings
run_stitch_brief.py already uses). It does NOT attempt entity-level figures
(e.g. isolating PacifiCorp or BPA within the "west" region) -- that is a
separate, bounded audit for once the regional pipeline is trusted, not this
one.

    python -m domains.grid.run_coverage_audit \
        --queue domains/grid/data/LBNL_Ix_Queue_Data_File_thru2026.xlsx \
        --out reports/coverage_audit
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

from domains.grid.run_stitch_brief import DEFAULT_REGIONS, PEER_REGIONS, _region_slice
from domains.grid.sources.lbnl_queue import (
    ACTIVE,
    LBNLQueueSource,
    OPERATIONAL,
    QueueProject,
    SUSPENDED,
    WITHDRAWN,
)

# The 7 fields a queue-process analysis (funnels, durations, post-IA) depends
# on. "mw" here means mw_1 only -- see POPULATED_DEFINITIONS["mw"] for why
# mw_2/mw_3 are reported separately as hybrid_capacity instead of folded in.
FIELDS = ["q_date", "ia_date", "wd_date", "on_date", "cluster", "mw", "entity"]
STATUSES = [OPERATIONAL, WITHDRAWN, ACTIVE, SUSPENDED]
REGIONS = sorted(set(DEFAULT_REGIONS) | set(PEER_REGIONS))

POPULATED_DEFINITIONS = {
    "q_date": "non-empty interconnection-request (IR) date.",
    "ia_date": "non-empty executed interconnection-agreement date.",
    "wd_date": "non-empty withdrawal date. Only meaningful for withdrawn "
               "projects; operational/active/suspended projects are not "
               "expected to carry one.",
    "on_date": "non-empty commercial-operation (COD) date.",
    "cluster": "non-empty cluster/cycle tag. ERCOT runs no cluster study, so "
               "near-zero cluster coverage there reflects an absent process, "
               "not missing data -- see run_stitch_brief.py's _cycle_key.",
    "mw": "mw_1 (the primary reported capacity column) is non-null. This "
          "does NOT include mw_2 or mw_3, which are co-located/hybrid "
          "secondary capacity columns reported separately below as "
          "hybrid_capacity, because mw_1 is ~100% populated nationally while "
          "mw_2/mw_3 are populated only for the small share of projects that "
          "are hybrid -- collapsing them into one 'mw populated' percentage "
          "would misrepresent both.",
    "entity": "non-empty reporting utility/BA name. Distinct from the "
              "'region' field: region is LBNL's multi-entity grouping "
              "(e.g. 'west' spans dozens of utilities), entity is the "
              "individual reporting utility within it.",
}

POST_IA_OBSERVABILITY_NOTE = (
    "Post-IA completion (LBNL Sheet 27's method) requires knowing, for each "
    "withdrawn project, whether it withdrew before or after executing an "
    "interconnection agreement -- which this dataset can only tell from a "
    "populated ia_date on that withdrawn record. This audit reports, per "
    "region, how many withdrawn projects carry that date. A count of zero "
    "means the rate cannot be computed for that region; it does NOT mean no "
    "project in that region ever signed an IA and later withdrew. The public "
    "data does not record the date for those cases, so their IA history is "
    "unobservable, not absent. Classification: 'absent' = zero withdrawn "
    "projects carry an ia_date, so no post-IA rate can be computed at all. "
    "'partial' = at least one but fewer than min_cohort, so a rate could "
    "technically be computed but rests on very few cases. 'complete' = at "
    "least min_cohort withdrawn projects carry an ia_date -- enough decided, "
    "observed cases to support a stable rate. 'complete' describes whether "
    "the SAMPLE is large enough, not whether the field is 100% populated: "
    "MISO classifies 'complete' with only 27% of its withdrawn cohort dated, "
    "because 27% of a large region is still hundreds of cases."
)


def _is_populated(p: QueueProject, field: str) -> bool:
    if field == "mw":
        return p.mw is not None
    return bool(getattr(p, field))


def field_coverage(members: List[QueueProject], field: str) -> Dict:
    n = len(members)
    populated = sum(1 for p in members if _is_populated(p, field))
    return {
        "populated": populated,
        "total": n,
        "pct": (populated / n) if n else None,
    }


def hybrid_capacity_coverage(members: List[QueueProject]) -> Dict:
    n = len(members)
    mw2 = sum(1 for p in members if p.mw2 is not None)
    mw3 = sum(1 for p in members if p.mw3 is not None)
    return {
        "mw2": {"populated": mw2, "total": n, "pct": (mw2 / n) if n else None},
        "mw3": {"populated": mw3, "total": n, "pct": (mw3 / n) if n else None},
    }


def _classify(count: int, min_cohort: int) -> str:
    if count == 0:
        return "absent"
    if count < min_cohort:
        return "partial"
    return "complete"


def post_ia_observability(withdrawn_members: List[QueueProject], min_cohort: int) -> Dict:
    """The generalized SPP test: can post-IA even be computed for this cohort?"""
    with_ia = sum(1 for p in withdrawn_members if p.ia_date)
    total = len(withdrawn_members)
    return {
        "with_ia_date": with_ia,
        "total_withdrawn": total,
        "pct": (with_ia / total) if total else None,
        "classification": _classify(with_ia, min_cohort),
    }


def status_report(region_members: List[QueueProject], status: str, min_cohort: int) -> Dict:
    members = [p for p in region_members if p.status == status]
    report = {
        "status": status,
        "n": len(members),
        "fields": {f: field_coverage(members, f) for f in FIELDS},
        "hybrid_capacity": hybrid_capacity_coverage(members),
    }
    if status == WITHDRAWN:
        report["post_ia_observability"] = post_ia_observability(members, min_cohort)
    return report


def region_report(projects: List[QueueProject], key: str, min_cohort: int) -> Dict:
    sub = _region_slice(projects, key)
    return {
        "region": key,
        "total": len(sub),
        "statuses": [status_report(sub, s, min_cohort) for s in STATUSES],
    }


def build(
    projects: List[QueueProject],
    regions: List[str],
    min_cohort: int,
    source_workbook: str,
) -> Dict:
    region_reports = [region_report(projects, r, min_cohort) for r in regions]

    def withdrawn_block(rr: Dict) -> Dict:
        return next(s for s in rr["statuses"] if s["status"] == WITHDRAWN)

    wd_date_by_region = []
    post_ia_by_region = []
    for rr in region_reports:
        wb = withdrawn_block(rr)
        cov = wb["fields"]["wd_date"]
        wd_date_by_region.append({"region": rr["region"], **cov})
        post_ia_by_region.append({"region": rr["region"], **wb["post_ia_observability"]})

    # Sorted ascending by pct so the worst-covered region leads -- that is
    # the direction a reader needs for "where does the data break down".
    wd_date_by_region.sort(key=lambda r: r["pct"] if r["pct"] is not None else -1.0)
    post_ia_by_region.sort(key=lambda r: r["pct"] if r["pct"] is not None else -1.0)

    return {
        # No runtime timestamp: this JSON must regenerate byte-identical from
        # the same workbook, which a timestamp would break.
        "provenance": {
            "source_workbook": Path(source_workbook).name,
            "generator": "domains.grid.run_coverage_audit",
            "audited_fields": FIELDS,
            "hybrid_capacity_fields": ["mw2", "mw3"],
            "populated_definitions": POPULATED_DEFINITIONS,
            "regions": regions,
            "region_definition": (
                "Each project's `region` field (an LBNL-assigned BA/RTO "
                "grouping) substring-matched against these 9 keys. 'west' "
                "and 'southeast' are LBNL's own multi-entity groupings, not "
                "single BAs -- see each status block's entity coverage for "
                "how many distinct reporting utilities that implies. Scope "
                "note: this audit reports at the region level only; it does "
                "not attempt entity-level breakdowns (e.g. isolating a "
                "single utility within 'west')."
            ),
            "statuses": STATUSES,
            "status_definition": (
                "operational | withdrawn | active | suspended, as classified "
                "from the raw q_status column by lbnl_queue._norm_status."
            ),
            "min_cohort": min_cohort,
            "post_ia_observability_note": POST_IA_OBSERVABILITY_NOTE,
        },
        "regions": region_reports,
        "national": {
            "wd_date_coverage_by_region_withdrawn": wd_date_by_region,
            "post_ia_observability_by_region": post_ia_by_region,
        },
    }


# --------------------------------------------------------------------------
# Markdown rendering
# --------------------------------------------------------------------------


def _pct(v: Optional[float]) -> str:
    return f"{v:.1%}" if v is not None else "— (n=0)"


def _post_ia_pct(row: Dict) -> str:
    """Render zero observed IA dates as unavailable, never as a rate."""
    if row["with_ia_date"] == 0:
        return "absent — not computable"
    return _pct(row["pct"])


def _cell(cov: Dict) -> str:
    return f"{cov['populated']:,}/{cov['total']:,} ({_pct(cov['pct'])})"


def to_markdown(rep: Dict) -> str:
    prov = rep["provenance"]
    L: List[str] = []
    L.append("# LBNL Queued Up — milestone-field coverage audit")
    L.append("")
    L.append(
        f"Source: **{prov['source_workbook']}** · generator: "
        f"`{prov['generator']}` · min_cohort: **{prov['min_cohort']}**"
    )
    L.append("")
    L.append(
        "For every region and status this project tracks, how completely are "
        "the fields a queue-process analysis depends on actually populated? "
        "Built to turn the SPP \"post-IA is not computable\" observation from "
        "an anecdote into a national result."
    )
    L.append("")
    L.append("## What \"populated\" means for each field")
    L.append("")
    for f in FIELDS:
        L.append(f"- **{f}** — {prov['populated_definitions'][f]}")
    L.append("")
    L.append("## Post-IA observability test")
    L.append("")
    L.append(prov["post_ia_observability_note"])
    L.append("")
    L.append(
        "| Region | Withdrawn w/ ia_date | Total withdrawn | % | Classification |"
    )
    L.append("|---|---:|---:|---:|---|")
    for row in rep["national"]["post_ia_observability_by_region"]:
        L.append(
            f"| **{row['region'].upper()}** | {row['with_ia_date']:,} | "
            f"{row['total_withdrawn']:,} | {_post_ia_pct(row)} | "
            f"{row['classification']} |"
        )
    L.append("")
    L.append("## Notable finding — wd_date coverage varies sharply by region")
    L.append("")
    L.append(
        "wd_date (withdrawal date) is currently unused by any pipeline in "
        "this repo, but it is required to know *when* a withdrawn project's "
        "clock stopped -- the input any survival/censoring analysis (planned "
        "next) needs. Coverage within each region's withdrawn cohort, worst "
        "first:"
    )
    L.append("")
    L.append("| Region | wd_date populated | Total withdrawn | % |")
    L.append("|---|---:|---:|---:|")
    for row in rep["national"]["wd_date_coverage_by_region_withdrawn"]:
        L.append(
            f"| **{row['region'].upper()}** | {row['populated']:,} | "
            f"{row['total']:,} | {_pct(row['pct'])} |"
        )
    L.append("")
    L.append(
        "## Field coverage by region and status"
    )
    L.append("")
    L.append(
        "Cells read populated/total (%). `mw` is mw_1 only; hybrid_capacity "
        "(mw_2/mw_3) is reported separately beneath each region's table."
    )
    for rr in rep["regions"]:
        L.append("")
        L.append(f"### {rr['region'].upper()} (n={rr['total']:,})")
        L.append("")
        header = "| Field | " + " | ".join(s["status"] for s in rr["statuses"]) + " |"
        sep = "|---|" + "---:|" * len(rr["statuses"])
        L.append(header)
        L.append(sep)
        for f in FIELDS:
            cells = " | ".join(_cell(s["fields"][f]) for s in rr["statuses"])
            L.append(f"| {f} | {cells} |")
        L.append("")
        hyb_cells = []
        for s in rr["statuses"]:
            h = s["hybrid_capacity"]
            hyb_cells.append(
                f"{s['status']}: mw2 {_cell(h['mw2'])}, mw3 {_cell(h['mw3'])}"
            )
        L.append("Hybrid capacity (co-located projects, not part of the mw row above): " + "; ".join(hyb_cells))
    L.append("")
    L.append(
        "_Scope: region level only. Entity-level figures (e.g. isolating a "
        "single utility within a multi-entity region) are a separate, "
        "bounded audit for later, not covered here._"
    )
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="LBNL queue milestone-field coverage audit")
    ap.add_argument("--queue", required=True, help="LBNL queue workbook (.xlsx)")
    ap.add_argument("--out", default="reports/coverage_audit")
    ap.add_argument("--min-cohort", type=int, default=30)
    args = ap.parse_args(argv)

    projects = LBNLQueueSource(args.queue).load()
    rep = build(projects, REGIONS, args.min_cohort, args.queue)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "coverage_audit.json").write_text(
        json.dumps(rep, indent=2, sort_keys=False), encoding="utf-8"
    )
    md = to_markdown(rep)
    (out / "coverage_audit.md").write_text(md, encoding="utf-8")

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(md)
    print(f"\nWrote {out/'coverage_audit.md'} and .json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
