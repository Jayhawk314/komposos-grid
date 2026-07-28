# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Time-since-IA control for the post-IA completion finding.

run_stitch_brief.py's post_ia_completion() pools every signed project
regardless of how long ago it signed. That mixes mature and recent IA
cohorts: a region whose signed projects are on average younger has had less
time for either outcome (operational or withdrawn) to occur, which can bias
a raw pooled rate in either direction without saying anything about process
quality.

This module controls for that by restricting the post-IA cohort to projects
old enough, as of a fixed data vintage, to have had a fair chance to resolve
by 2, 3, and 5 years after IA execution -- then recomputing the same
operational / (operational + withdrawn) rate on that maturity-filtered
cohort. Still-active or suspended projects within the mature cohort are
reported explicitly as censored, never dropped silently.

Why status-based, not event-date-based: a stricter design would classify
each project's outcome AT exactly the horizon (operational by ia_date+H vs
withdrawn by ia_date+H) using on_date/wd_date. run_coverage_audit.py found
wd_date populated on only 12-35% of withdrawn projects in West and
Southeast, so that precision is not available nationally. This module uses
current (data-vintage) status among a maturity-filtered cohort instead --
answerable for every region, at the cost of not knowing exactly how long
after signing an eventual withdrawal happened.

    python -m domains.grid.run_post_ia_horizon \
        --queue domains/grid/data/LBNL_Ix_Queue_Data_File_thru2026.xlsx \
        --out reports/post_ia_horizon
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

from domains.grid.run_coverage_audit import _classify
from domains.grid.run_stitch_brief import (
    DEFAULT_REGIONS,
    PEER_REGIONS,
    _months_between,
    _region_slice,
    post_ia_completion,
)
from domains.grid.sources.lbnl_queue import (
    ACTIVE,
    LBNLQueueSource,
    OPERATIONAL,
    QueueProject,
    SUSPENDED,
    WITHDRAWN,
)

# 2, 3, and 5 years after IA execution, per the maturity-control design in
# WORKING_NOTES.md's "HIGHEST-VALUE RESEARCH UPGRADES" section.
HORIZONS_MONTHS = [24, 36, 60]

# Fixed data-vintage cutoff, matching run_stitch_brief.py's documented
# dataset string ("LBNL Queued Up, 2026 Edition (data through year-end
# 2025)"). Deliberately NOT datetime.now(): a live clock would make "months
# since IA" -- and therefore which cohort counts as mature -- change every
# time this regenerates, breaking byte-identical reproduction.
VINTAGE_CUTOFF = "2025-12-31"

REGIONS = sorted(set(DEFAULT_REGIONS) | set(PEER_REGIONS))

METHOD_NOTE = (
    "For each region, the signed cohort is every project with an executed-IA "
    "date. At each horizon H (2, 3, 5 years), the MATURE subset is signed "
    "projects at least H months old as of the fixed vintage cutoff -- i.e. "
    "old enough to have had a fair chance to resolve by H, regardless of "
    "whether they actually did. Within that mature subset, the rate is "
    "operational / (operational + withdrawn) using CURRENT status, same "
    "definition as the raw post-IA rate, just restricted to older-than-H "
    "signings. Still-active and suspended projects within the mature cohort "
    "are reported as 'censored' -- old enough to expect resolution, not yet "
    "resolved -- and are never counted as failures or dropped from the "
    "report. This does not pin exactly WHEN within the horizon an outcome "
    "occurred (see module docstring on wd_date coverage); it controls for "
    "cohort age, not for event timing precision."
)


def _age_months(p: QueueProject, cutoff: str = VINTAGE_CUTOFF) -> Optional[float]:
    return _months_between(p.ia_date, cutoff)


def cohort_age_report(signed: List[QueueProject]) -> Dict:
    ages = sorted(a for a in (_age_months(p) for p in signed) if a is not None)
    if not ages:
        return {"n": 0, "median_months": None, "p25_months": None, "p75_months": None}
    n = len(ages)
    return {
        "n": n,
        "median_months": round(ages[n // 2], 1),
        "p25_months": round(ages[max(0, int(0.25 * n) - 1)], 1),
        "p75_months": round(ages[min(n - 1, int(0.75 * n))], 1),
    }


def horizon_report(signed: List[QueueProject], months_h: int, min_cohort: int) -> Dict:
    mature = [p for p in signed if (_age_months(p) or -1.0) >= months_h]
    ops = [p for p in mature if p.status == OPERATIONAL]
    wd = [p for p in mature if p.status == WITHDRAWN]
    censored = [p for p in mature if p.status in (ACTIVE, SUSPENDED)]
    decided = len(ops) + len(wd)
    return {
        "horizon_months": months_h,
        "n_signed": len(signed),
        "n_mature": len(mature),
        "operational": len(ops),
        "withdrawn": len(wd),
        "censored_active_or_suspended": len(censored),
        "decided": decided,
        "rate": (len(ops) / decided) if decided else None,
        "classification": _classify(decided, min_cohort),
    }


def region_report(projects: List[QueueProject], key: str, min_cohort: int) -> Dict:
    signed = [p for p in _region_slice(projects, key) if p.ia_date]
    raw = post_ia_completion(projects, key)
    horizons = [horizon_report(signed, h, min_cohort) for h in HORIZONS_MONTHS]
    for h in horizons:
        h["delta_from_raw_rate"] = (
            (h["rate"] - raw["rate"])
            if (h["rate"] is not None and raw["signed_decided"])
            else None
        )
    return {
        "region": key,
        "raw_post_ia": raw,
        "cohort_age_months": cohort_age_report(signed),
        "horizons": horizons,
    }


def _gap_row(horizon_months: int, label: str, region_reports: Dict[str, Dict]) -> Optional[Dict]:
    if "miso" not in region_reports or "ercot" not in region_reports:
        return None
    if horizon_months == 0:
        miso_rate = region_reports["miso"]["raw_post_ia"]["rate"]
        ercot_rate = region_reports["ercot"]["raw_post_ia"]["rate"]
        miso_n = region_reports["miso"]["raw_post_ia"]["signed_decided"]
        ercot_n = region_reports["ercot"]["raw_post_ia"]["signed_decided"]
    else:
        mh = next(h for h in region_reports["miso"]["horizons"] if h["horizon_months"] == horizon_months)
        eh = next(h for h in region_reports["ercot"]["horizons"] if h["horizon_months"] == horizon_months)
        miso_rate, miso_n = mh["rate"], mh["decided"]
        ercot_rate, ercot_n = eh["rate"], eh["decided"]
    gap = (ercot_rate - miso_rate) if (miso_rate is not None and ercot_rate is not None) else None
    return {
        "horizon_months": horizon_months,
        "label": label,
        "miso_rate": miso_rate,
        "miso_n_decided": miso_n,
        "ercot_rate": ercot_rate,
        "ercot_n_decided": ercot_n,
        "gap": gap,
    }


def build(projects: List[QueueProject], regions: List[str], min_cohort: int, source_workbook: str) -> Dict:
    region_reports = [region_report(projects, r, min_cohort) for r in regions]
    by_region = {r["region"]: r for r in region_reports}

    gap_by_horizon = [_gap_row(0, "raw (unadjusted)", by_region)]
    for h in HORIZONS_MONTHS:
        gap_by_horizon.append(_gap_row(h, f"{h // 12}-year", by_region))
    gap_by_horizon = [g for g in gap_by_horizon if g is not None]

    return {
        # No runtime timestamp -- see VINTAGE_CUTOFF comment; this JSON must
        # regenerate byte-identical from the same workbook.
        "provenance": {
            "source_workbook": Path(source_workbook).name,
            "generator": "domains.grid.run_post_ia_horizon",
            "vintage_cutoff": VINTAGE_CUTOFF,
            "vintage_cutoff_note": (
                "Fixed to match the dataset's documented vintage "
                "(run_stitch_brief.py: 'data through year-end 2025'), not "
                "computed from the current date."
            ),
            "horizons_months": HORIZONS_MONTHS,
            "min_cohort": min_cohort,
            "regions": regions,
            "method_note": METHOD_NOTE,
        },
        "miso_ercot_gap_by_horizon": gap_by_horizon,
        "regions": region_reports,
    }


# --------------------------------------------------------------------------
# Markdown rendering
# --------------------------------------------------------------------------


def _pct(v: Optional[float]) -> str:
    return f"{v:.1%}" if v is not None else "— (n=0)"


def _pp(v: Optional[float]) -> str:
    if v is None:
        return "—"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v * 100:.1f} pp"


def _raw_rate_label(raw: Dict) -> str:
    """A signed_decided of 0 means not computable (e.g. SPP), not a 0% rate --
    same distinction run_coverage_audit.py's 'absent' classification exists
    to preserve. Never render that case as a bare percentage."""
    if not raw["signed_decided"]:
        return "not computable (n=0)"
    return _pct(raw["rate"])


def to_markdown(rep: Dict) -> str:
    prov = rep["provenance"]
    L: List[str] = []
    L.append("# Post-IA completion — time-since-IA (maturity) control")
    L.append("")
    L.append(
        f"Source: **{prov['source_workbook']}** · vintage cutoff: "
        f"**{prov['vintage_cutoff']}** · horizons: "
        f"{', '.join(f'{h}mo' for h in prov['horizons_months'])} · "
        f"min_cohort: **{prov['min_cohort']}**"
    )
    L.append("")
    L.append(prov["method_note"])
    L.append("")

    if rep["miso_ercot_gap_by_horizon"]:
        L.append("## Headline: does the MISO/ERCOT gap survive maturity control?")
        L.append("")
        L.append("| Cohort | MISO rate (n decided) | ERCOT rate (n decided) | Gap (ERCOT − MISO) |")
        L.append("|---|---:|---:|---:|")
        for g in rep["miso_ercot_gap_by_horizon"]:
            L.append(
                f"| {g['label']} | {_pct(g['miso_rate'])} ({g['miso_n_decided']:,}) | "
                f"{_pct(g['ercot_rate'])} ({g['ercot_n_decided']:,}) | "
                f"{_pp(g['gap'])} |"
            )
        L.append("")

    L.append("## IA-cohort age — why maturity control matters here")
    L.append("")
    L.append(
        "Median months since IA execution (as of the vintage cutoff), among "
        "signed projects. A region whose signed cohort is younger has had "
        "less time for outcomes to resolve; this is the raw-rate bias the "
        "horizon control above tests for."
    )
    L.append("")
    L.append("| Region | n signed | Median age (mo) | p25 | p75 |")
    L.append("|---|---:|---:|---:|---:|")
    for rr in rep["regions"]:
        ca = rr["cohort_age_months"]
        if not ca["n"]:
            L.append(f"| **{rr['region'].upper()}** | 0 | — | — | — |")
            continue
        L.append(
            f"| **{rr['region'].upper()}** | {ca['n']:,} | {ca['median_months']} | "
            f"{ca['p25_months']} | {ca['p75_months']} |"
        )
    L.append("")

    L.append("## Full breakdown by region and horizon")
    L.append("")
    L.append(
        "`decided` = operational + withdrawn among the mature cohort; "
        "`censored` = still active/suspended despite being old enough to "
        "expect resolution -- reported, not dropped. `Δ raw` = horizon rate "
        "minus the unadjusted raw post-IA rate."
    )
    for rr in rep["regions"]:
        raw = rr["raw_post_ia"]
        L.append("")
        L.append(
            f"### {rr['region'].upper()} — raw rate {_raw_rate_label(raw)} "
            f"({raw['built_after_signing']:,}/{raw['signed_decided']:,})"
        )
        L.append("")
        L.append(
            "| Horizon | Mature | Operational | Withdrawn | Censored | "
            "Decided | Rate | Δ raw | Classification |"
        )
        L.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
        for h in rr["horizons"]:
            L.append(
                f"| {h['horizon_months'] // 12}y | {h['n_mature']:,} | "
                f"{h['operational']:,} | {h['withdrawn']:,} | "
                f"{h['censored_active_or_suspended']:,} | {h['decided']:,} | "
                f"{_pct(h['rate'])} | {_pp(h['delta_from_raw_rate'])} | "
                f"{h['classification']} |"
            )
    L.append("")
    L.append(
        "_Scope: region level only, same 9 regions as the coverage audit. "
        "Not a survival/Kaplan-Meier estimate -- a fixed-horizon maturity "
        "filter on current status; see method note above for what that "
        "does and does not control for._"
    )
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Time-since-IA control for post-IA completion")
    ap.add_argument("--queue", required=True, help="LBNL queue workbook (.xlsx)")
    ap.add_argument("--out", default="reports/post_ia_horizon")
    ap.add_argument("--min-cohort", type=int, default=30)
    args = ap.parse_args(argv)

    projects = LBNLQueueSource(args.queue).load()
    rep = build(projects, REGIONS, args.min_cohort, args.queue)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "post_ia_horizon.json").write_text(
        json.dumps(rep, indent=2, sort_keys=False), encoding="utf-8"
    )
    md = to_markdown(rep)
    (out / "post_ia_horizon.md").write_text(md, encoding="utf-8")

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(md)
    print(f"\nWrote {out/'post_ia_horizon.md'} and .json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
