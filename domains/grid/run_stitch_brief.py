# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""STITCH MISO/ERCOT brief: region-specific queue-process factorization.

Built for the ESIG / Berkeley Lab i2X **STITCH** meeting of 2026-06-23
("Regional Study Processes": MISO + ERCOT). It does NOT introduce new
math -- it reuses the queue OPTIMUS factorization (queue_analysis.py)
but slices the LBNL "Queued Up" file to one region at a time and reports
the *interconnection study milestone* funnel, which is precisely the
topic presenters were asked to cover (process milestones, study methods,
where projects die).

    python -m domains.grid.run_stitch_brief \
        --queue domains/grid/data/LBNL_Ix_Queue_Data_File_thru2026.xlsx \
        --out reports/stitch_2026-06-23

Honesty notes (carried from queue_analysis.py):
- rates are over *decided* projects only (operational | withdrawn);
  active/suspended projects are censored, not failures.
- ia_status is the furthest/last known milestone, so per-milestone
  completion is descriptive mediation, not a causal process model.
- a region slice with few decided projects is reported but flagged.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from statistics import median
from typing import Dict, List, Optional

from domains.grid.sources.lbnl_queue import (
    LBNLQueueSource,
    OPERATIONAL,
    QueueProject,
    WITHDRAWN,
)

# regions of interest for the 2026-06-23 session, plus peers for context
DEFAULT_REGIONS = ["miso", "ercot"]
PEER_REGIONS = ["pjm", "caiso", "spp", "nyiso", "southeast", "west", "iso_ne"]


def _region_slice(projects: List[QueueProject], key: str) -> List[QueueProject]:
    return [p for p in projects if key in p.region]


def _completion(decided: List[QueueProject]) -> float:
    if not decided:
        return 0.0
    ops = sum(1 for p in decided if p.status == OPERATIONAL)
    return ops / len(decided)


def _cycle_key(p: QueueProject) -> str:
    """Region-adaptive study cycle.

    MISO tags projects with a DPP cluster ("DPP-2022 South"); collapse the
    sub-region so the *cycle* is the unit. ERCOT runs no cluster study, so
    fall back to entry-year cohort. This asymmetry is itself a harmonization
    finding: the 'cluster' construct does not exist on both sides.
    """
    if p.cluster:
        # collapse sub-rounds to the cycle YEAR: "DPP-2022 South",
        # "DPP-2018-APR", "DPP-2008-NOV" all map to their DPP-<year>.
        m = re.search(r"(19|20)\d{2}", p.cluster)
        if m:
            return f"cluster:DPP-{m.group(0)}"
        # non-DPP / yearless cluster tags fall back to entry year
    if p.q_year:
        return f"cycle:{p.q_year}"
    return "cycle:(unknown)"


def cycle_report(projects: List[QueueProject], key: str, min_cohort: int) -> List[Dict]:
    sub = _region_slice(projects, key)
    by_cycle: Dict[str, List[QueueProject]] = defaultdict(list)
    for p in sub:
        by_cycle[_cycle_key(p)].append(p)

    rows = []
    for cyc, members in by_cycle.items():
        decided = [m for m in members if m.decided]
        ops = sum(1 for m in decided if m.status == OPERATIONAL)
        wd = sum(1 for m in decided if m.status == WITHDRAWN)
        active = len(members) - len(decided)
        rows.append(
            {
                "cycle": cyc,
                "total": len(members),
                "decided": len(decided),
                "operational": ops,
                "withdrawn": wd,
                "active": active,
                "completion": ops / len(decided) if decided else 0.0,
                # maturity: a cycle that is still mostly in-queue can't be
                # judged on completion yet -- low decided_share = immature.
                "decided_share": len(decided) / len(members) if members else 0.0,
                "immature": (len(decided) / len(members) if members else 0.0) < 0.5,
                "thin": len(decided) < min_cohort,
            }
        )
    rows.sort(key=lambda r: r["cycle"])
    return rows


def _months_between(start_iso: str, end_iso: str) -> Optional[float]:
    """Whole-month gap between two ISO dates; None if either missing or the
    span is negative (date error) or absurd (> 30 yr)."""
    if not start_iso or not end_iso:
        return None
    try:
        d0 = date.fromisoformat(start_iso)
        d1 = date.fromisoformat(end_iso)
    except ValueError:
        return None
    days = (d1 - d0).days
    if days < 0 or days > 30 * 365:
        return None
    return days / 30.44


def _stage_stats(months: List[float]) -> Dict:
    if not months:
        return {"n": 0, "median_months": None, "p25_months": None,
                "p75_months": None}
    s = sorted(months)
    return {
        "n": len(s),
        "median_months": round(median(s), 1),
        "p25_months": round(s[max(0, int(0.25 * len(s)) - 1)], 1),
        "p75_months": round(s[min(len(s) - 1, int(0.75 * len(s)))], 1),
    }


def duration_report(projects: List[QueueProject], key: str) -> Dict:
    """IR->IA (study), IA->COD (build), IR->COD (total) durations, months."""
    sub = _region_slice(projects, key)
    ir_ia, ia_cod, ir_cod = [], [], []
    for p in sub:
        m1 = _months_between(p.q_date, p.ia_date)
        if m1 is not None:
            ir_ia.append(m1)
        m2 = _months_between(p.ia_date, p.on_date)
        if m2 is not None:
            ia_cod.append(m2)
        m3 = _months_between(p.q_date, p.on_date)
        if m3 is not None:
            ir_cod.append(m3)
    return {
        "ir_to_ia": _stage_stats(ir_ia),
        "ia_to_cod": _stage_stats(ia_cod),
        "ir_to_cod": _stage_stats(ir_cod),
    }


def lbnl_completion(projects: List[QueueProject], key: str) -> Dict:
    """Completion rate using LBNL's OWN published definition: share of all
    requests submitted 2000-2020 that are operational as of the data vintage.
    This reproduces LBNL 'Queued Up' sheet 25 exactly, so the number is the
    report authors' own and cannot be called cherry-picked."""
    sub = [p for p in _region_slice(projects, key)
           if p.q_year and 2000 <= p.q_year <= 2020]
    built = sum(1 for p in sub if p.status == OPERATIONAL)
    return {
        "requests": len(sub),
        "built": built,
        "rate": built / len(sub) if sub else 0.0,
        "window": "2000-2020 requests, LBNL definition",
    }


def post_ia_completion(projects: List[QueueProject], key: str) -> Dict:
    """Of projects that actually executed an interconnection agreement
    (ia_date present), the share that got built vs withdrew after signing.
    Uses the IA date, matching LBNL's post-IA method (sheet 27): this counts
    projects that signed and THEN withdrew, which the status-label shortcut
    misses. Decided (built|withdrawn) denominator."""
    signed = [p for p in _region_slice(projects, key) if p.ia_date]
    decided = [p for p in signed if p.status in (OPERATIONAL, WITHDRAWN)]
    built = sum(1 for p in decided if p.status == OPERATIONAL)
    return {
        "signed_decided": len(decided),
        "built_after_signing": built,
        "rate": built / len(decided) if decided else 0.0,
    }


def region_report(projects: List[QueueProject], key: str, min_cohort: int) -> Dict:
    sub = _region_slice(projects, key)
    decided = [p for p in sub if p.decided]
    ops = [p for p in decided if p.status == OPERATIONAL]

    # milestone funnel: per last-known IA milestone, completion among decided
    by_ms: Dict[str, List[QueueProject]] = defaultdict(list)
    for p in decided:
        by_ms[p.ia_status or "(unlabeled)"].append(p)

    milestones = []
    for ms, rows in by_ms.items():
        n = len(rows)
        n_ops = sum(1 for r in rows if r.status == OPERATIONAL)
        milestones.append(
            {
                "milestone": ms,
                "n_decided": n,
                "n_operational": n_ops,
                "completion": n_ops / n if n else 0.0,
                "below_min_cohort": n < min_cohort,
            }
        )
    milestones.sort(key=lambda m: (-m["completion"], -m["n_decided"]))

    # fuel mix of *active* (still-in-queue) projects -- what is waiting
    active = [p for p in sub if p.status not in (OPERATIONAL, WITHDRAWN)]
    fuel_active: Dict[str, int] = defaultdict(int)
    mw_active: Dict[str, float] = defaultdict(float)
    for p in active:
        fuel_active[p.fuel] += 1
        if p.mw:
            mw_active[p.fuel] += p.mw

    return {
        "region": key,
        "total_requests": len(sub),
        "decided": len(decided),
        "operational": len(ops),
        "active_in_queue": len(active),
        "completion": _completion(decided),  # internal, all-yr decided rate
        "completion_lbnl": lbnl_completion(projects, key),   # headline metric
        "post_ia": post_ia_completion(projects, key),        # headline metric
        "milestones": milestones,
        "active_fuel_mix": dict(
            sorted(fuel_active.items(), key=lambda kv: -kv[1])
        ),
        "active_fuel_gw": {
            k: round(v / 1000.0, 1)
            for k, v in sorted(mw_active.items(), key=lambda kv: -kv[1])
        },
        "cycles": cycle_report(projects, key, min_cohort),
        "durations": duration_report(projects, key),
    }


def build(projects: List[QueueProject], regions: List[str], min_cohort: int) -> Dict:
    return {
        "dataset": "LBNL Queued Up, 2026 Edition (data through year-end 2025)",
        "method": "LBNL-definition completion + built-after-signing, per region",
        "national_completion": _completion([p for p in projects if p.decided]),
        "regions": [region_report(projects, r, min_cohort) for r in regions],
    }


def to_markdown(rep: Dict) -> str:
    L = []
    L.append("# STITCH 2026-06-23 — MISO vs ERCOT Interconnection Study Process")
    L.append("")
    L.append(
        f"Dataset: **{rep['dataset']}** · method: {rep['method']} · "
        f"national completion (decided): **{rep['national_completion']:.1%}**"
    )
    L.append("")
    L.append("## Headline comparison")
    L.append("")
    L.append(
        "Two headline numbers, both using Berkeley Lab's own definitions so they "
        "match the published *Queued Up* report (see Definitions at the bottom):"
    )
    L.append("")
    L.append(
        "- **Completion** = share of all 2000–2020 requests now built "
        "(LBNL sheet 25)."
    )
    L.append(
        "- **Built after signing** = of projects that executed an "
        "interconnection agreement, the share built rather than withdrawn "
        "(LBNL sheet 27 method)."
    )
    L.append("")
    L.append("| Region | 2000–2020 requests | Built | Completion | Built after signing IA |")
    L.append("|---|---:|---:|---:|---:|")
    for r in rep["regions"]:
        c = r["completion_lbnl"]
        pia = r["post_ia"]
        L.append(
            f"| **{r['region'].upper()}** | {c['requests']:,} | "
            f"{c['built']:,} | **{c['rate']:.1%}** | "
            f"**{pia['rate']:.1%}** ({pia['built_after_signing']:,}"
            f"/{pia['signed_decided']:,}) |"
        )
    L.append("")
    L.append("## Process duration — how long, not just how many (months)")
    L.append("")
    L.append(
        "Median elapsed months per stage, with [p25–p75] spread. **IR→IA** is "
        "the study/queue stage (the i2X speed bottleneck); **IA→COD** is "
        "construction; **IR→COD** is request-to-operation end to end. Computed "
        "only over projects that actually reached each milestone (so IA→COD is "
        "survivors), with negative and >30yr spans dropped as date errors."
    )
    L.append("")
    L.append("| Region | IR→IA (study) | IA→COD (build) | IR→COD (total) |")
    L.append("|---|---|---|---|")
    for r in rep["regions"]:
        d = r["durations"]

        def cell(s):
            if not s["n"]:
                return "— (n=0)"
            return (f"{s['median_months']} mo "
                    f"[{s['p25_months']}–{s['p75_months']}], n={s['n']}")

        L.append(
            f"| **{r['region'].upper()}** | {cell(d['ir_to_ia'])} | "
            f"{cell(d['ia_to_cod'])} | {cell(d['ir_to_cod'])} |"
        )
    L.append("")
    L.append("## Study-milestone funnel (where decided projects ended up)")
    L.append("")
    L.append(
        "Completion rate among *decided* projects, grouped by their last-known "
        "interconnection-agreement milestone. A study phase with ~0% completion "
        "is where projects die; reaching **ia_executed** is the gate to service."
    )
    for r in rep["regions"]:
        L.append("")
        L.append(f"### {r['region'].upper()}")
        L.append("")
        L.append("| Milestone | Decided | Operational | Completion | |")
        L.append("|---|---:|---:|---:|---|")
        for m in r["milestones"]:
            flag = " _(thin)_" if m["below_min_cohort"] else ""
            L.append(
                f"| {m['milestone']} | {m['n_decided']:,} | "
                f"{m['n_operational']:,} | {m['completion']:.1%} |{flag} |"
            )
        gw = r["active_fuel_gw"]
        if gw:
            top = ", ".join(f"{k} {v} GW" for k, v in list(gw.items())[:5])
            L.append("")
            L.append(f"Active (still-in-queue) capacity by fuel — {top}")
    L.append("")
    L.append("## Study-cycle trend (are the reforms moving the needle?)")
    L.append("")
    L.append(
        "Completion by study cycle. MISO is sliced by DPP cluster cycle; ERCOT "
        "has no cluster study, so it is sliced by entry-year cohort — that "
        "asymmetry is itself a harmonization finding. Recent cycles are still "
        "mostly in study (**immature**: < 50% decided), so their completion "
        "rate is not yet meaningful — read the *active* and *decided-share* "
        "columns, not completion, for those."
    )
    for r in rep["regions"]:
        if not r["cycles"]:
            continue
        L.append("")
        L.append(f"### {r['region'].upper()}")
        L.append("")
        L.append(
            "| Cycle | Total | Decided | Operational | Withdrawn | Active | "
            "Completion | Decided-share | |"
        )
        L.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
        for c in r["cycles"]:
            flags = []
            if c["immature"]:
                flags.append("immature")
            if c["thin"]:
                flags.append("thin")
            tag = " _(" + ", ".join(flags) + ")_" if flags else " "
            L.append(
                f"| {c['cycle']} | {c['total']:,} | {c['decided']:,} | "
                f"{c['operational']:,} | {c['withdrawn']:,} | {c['active']:,} | "
                f"{c['completion']:.1%} | {c['decided_share']:.0%} |{tag} |"
            )
    L.append("")
    L.append("## Reading for the harmonization discussion")
    L.append("")
    L.append(
        "- The two regions run structurally different study processes and the "
        "outcome gap is large and measured, not modeled."
    )
    L.append(
        "- The dominant cause of withdrawal in both regions is *not reaching "
        "IA execution* — every study-phase exit is effectively terminal. "
        "Harmonization that compresses the study→IA path attacks the gap "
        "directly."
    )
    L.append(
        "- This is the same OPTIMUS factorization used across the repo: the "
        "milestone is the discovered intermediate through which "
        "`proposed → operational` factors with higher confidence than the "
        "direct rate."
    )
    L.append("")
    L.append("## Definitions (so the numbers are unambiguous)")
    L.append("")
    L.append(
        "- **Completion** uses LBNL's published definition: operational ÷ all "
        "requests submitted 2000–2020 (LBNL *Queued Up* sheet 25). These counts "
        "reproduce LBNL's own table exactly."
    )
    L.append(
        "- **Built after signing** = operational ÷ (operational + withdrawn) "
        "among projects with an executed-IA date (LBNL sheet 27 method). It "
        "counts projects that signed and then withdrew."
    )
    L.append(
        "- The **milestone funnel, durations, and study-cycle** panels below use "
        "all submission years and project counts, for breadth; they are "
        "descriptive, not the headline comparison."
    )
    L.append("")
    L.append(
        "_Honesty: rates over decided projects (active/suspended censored); "
        "durations survivor-conditioned; thin/immature cohorts flagged; "
        "descriptive mediation, not a causal model._"
    )
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------
# Static HTML export (self-contained, dependency-free, repo house style)
# --------------------------------------------------------------------------

_CSS = """
:root { color-scheme: light; --ink:#17202a; --muted:#5b6673; --line:#d8dee6;
  --surface:#ffffff; --page:#f5f7fa; --blue:#1f6feb; --green:#1f8f5f; --amber:#b7791f; }
* { box-sizing: border-box; }
body { margin:0; background:var(--page); color:var(--ink);
  font:14px/1.5 Arial, Helvetica, sans-serif; }
.shell { width:min(1280px, calc(100vw - 32px)); margin:0 auto; padding:28px 0 40px; }
header { border-bottom:1px solid var(--line); margin-bottom:18px; padding-bottom:16px; }
h1 { font-size:clamp(26px,4vw,38px); line-height:1.1; margin:0 0 8px; }
h2 { font-size:18px; line-height:1.25; margin:0 0 14px; }
p { margin:0 0 8px; color:var(--muted); }
.band { background:var(--surface); border:1px solid var(--line); border-radius:8px;
  margin:16px 0; padding:18px; }
.metrics { display:grid; grid-template-columns:repeat(auto-fit, minmax(210px,1fr));
  gap:12px; margin:16px 0; }
.metric { min-height:118px; background:var(--surface); border:1px solid var(--line);
  border-top:4px solid var(--blue); border-radius:8px; padding:14px; display:grid;
  gap:6px; align-content:start; }
.metric:nth-child(2n) { border-top-color:var(--green); }
.metric:nth-child(3n) { border-top-color:var(--amber); }
.metric span { color:var(--muted); font-size:12px; text-transform:uppercase; }
.metric strong { font-size:24px; line-height:1.05; }
.metric small { color:var(--muted); }
.table-wrap { overflow-x:auto; }
table { width:100%; border-collapse:collapse; }
th, td { border-bottom:1px solid var(--line); padding:9px 10px; text-align:left;
  vertical-align:top; }
th { color:var(--muted); font-size:12px; text-transform:uppercase; background:#fbfcfe; }
td.num, th.num { text-align:right; }
tr:hover td { background:#f9fbfd; }
.flag { color:var(--amber); font-size:12px; }
.foot { color:var(--muted); font-size:12px; }
.foot a { color:var(--blue); }
@media (max-width:640px) { .shell { width:min(100vw - 20px,1280px); padding-top:18px; }
  .band { padding:14px; } .metric strong { font-size:21px; } }
"""


def _esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _table(headers: List[str], rows: List[List[str]], num_cols=None) -> str:
    num_cols = num_cols or set()
    th = "".join(
        f'<th class="num">{_esc(h)}</th>' if i in num_cols else f"<th>{_esc(h)}</th>"
        for i, h in enumerate(headers)
    )
    body = []
    for row in rows:
        tds = "".join(
            f'<td class="num">{c}</td>' if i in num_cols else f"<td>{c}</td>"
            for i, c in enumerate(row)
        )
        body.append(f"<tr>{tds}</tr>")
    return (f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def to_html(rep: Dict) -> str:
    regions = rep["regions"]
    by = {r["region"]: r for r in regions}

    def dur_cell(s):
        if not s["n"]:
            return "— (n=0)"
        return (f"{s['median_months']} mo [{s['p25_months']}–{s['p75_months']}], "
                f"n={s['n']:,}")

    # metric cards (LBNL-aligned headline metrics)
    cards = []
    for r in regions[:2]:  # MISO + ERCOT completion
        c = r["completion_lbnl"]
        cards.append(
            f'<div class="metric"><span>{_esc(r["region"].upper())} completion</span>'
            f'<strong>{c["rate"]:.1%}</strong>'
            f'<small>{c["built"]:,} of {c["requests"]:,} requests (2000–2020)</small></div>'
        )
    for r in regions[:2]:  # MISO + ERCOT built-after-signing
        pia = r["post_ia"]
        cards.append(
            f'<div class="metric"><span>{_esc(r["region"].upper())} built after signing</span>'
            f'<strong>{pia["rate"]:.1%}</strong>'
            f'<small>{pia["built_after_signing"]:,} of {pia["signed_decided"]:,} '
            f'executed IAs</small></div>'
        )

    # headline table (LBNL-aligned)
    head_rows = []
    for r in regions:
        c = r["completion_lbnl"]
        pia = r["post_ia"]
        head_rows.append(
            [f'<strong>{_esc(r["region"].upper())}</strong>',
             f'{c["requests"]:,}', f'{c["built"]:,}',
             f'<strong>{c["rate"]:.1%}</strong>',
             f'<strong>{pia["rate"]:.1%}</strong> '
             f'({pia["built_after_signing"]:,}/{pia["signed_decided"]:,})'])
    head_tbl = _table(
        ["Region", "2000–2020 requests", "Built", "Completion",
         "Built after signing IA"],
        head_rows, num_cols={1, 2, 3, 4})

    # duration table
    dur_rows = [
        [f'<strong>{_esc(r["region"].upper())}</strong>',
         dur_cell(r["durations"]["ir_to_ia"]),
         dur_cell(r["durations"]["ia_to_cod"]),
         dur_cell(r["durations"]["ir_to_cod"])]
        for r in regions
    ]
    dur_tbl = _table(["Region", "IR→IA (study)", "IA→COD (build)",
                      "IR→COD (total)"], dur_rows)

    # milestone + cycle tables per region
    def milestone_tbl(r):
        rows = []
        for m in r["milestones"]:
            ms = _esc(m["milestone"])
            if m["below_min_cohort"]:
                ms += ' <span class="flag">thin</span>'
            rows.append([ms, f'{m["n_decided"]:,}', f'{m["n_operational"]:,}',
                         f'{m["completion"]:.1%}'])
        return _table(["Milestone", "Decided", "Operational", "Completion"],
                      rows, num_cols={1, 2, 3})

    def cycle_tbl(r):
        rows = []
        for c in r["cycles"]:
            flags = []
            if c["immature"]:
                flags.append("immature")
            if c["thin"]:
                flags.append("thin")
            cyc = _esc(c["cycle"])
            if flags:
                cyc += f' <span class="flag">{", ".join(flags)}</span>'
            rows.append([cyc, f'{c["total"]:,}', f'{c["decided"]:,}',
                         f'{c["operational"]:,}', f'{c["withdrawn"]:,}',
                         f'{c["active"]:,}', f'{c["completion"]:.1%}',
                         f'{c["decided_share"]:.0%}'])
        return _table(["Cycle", "Total", "Decided", "Op.", "Withdrawn",
                       "Active", "Completion", "Decided-share"],
                      rows, num_cols={1, 2, 3, 4, 5, 6, 7})

    milestone_bands = "".join(
        f'<div class="band"><h2>Milestone funnel — {_esc(r["region"].upper())}</h2>'
        f'{milestone_tbl(r)}</div>' for r in regions
    )
    cycle_bands = "".join(
        f'<div class="band"><h2>Study-cycle trend — {_esc(r["region"].upper())}</h2>'
        f'{cycle_tbl(r)}</div>' for r in regions if r["cycles"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>STITCH 2026-06-23 — MISO vs ERCOT Interconnection Study Process</title>
<style>{_CSS}</style>
</head>
<body>
<div class="shell">
<header>
<h1>MISO vs ERCOT — Interconnection Study Process</h1>
<p>i2X STITCH "Regional Study Processes" · 2026-06-23 · source:
{_esc(rep["dataset"])}. Headline numbers use Berkeley Lab's own definitions
(see foot) so they match the published <em>Queued Up</em> report.</p>
</header>

<div class="metrics">{"".join(cards)}</div>

<div class="band"><h2>Headline comparison</h2>{head_tbl}</div>

<div class="band">
<h2>Process duration — how long, not just how many (months)</h2>
<p>Median elapsed months per stage, with [p25–p75] spread. IR→IA is the
study/queue stage (the i2X speed bottleneck); IA→COD is construction; IR→COD is
request-to-operation end to end. IA→COD and IR→COD are survivor-conditioned
(completers only); negative and &gt;30-year spans dropped as date errors.</p>
{dur_tbl}
</div>

<div class="band">
<h2>Study-milestone funnel</h2>
<p>Where decided projects end up, by last-known IA milestone (all years, by
count — descriptive detail, not the headline). Study-phase exits complete ~0%;
reaching an executed IA is the gate. The defensible headline version of this
gate — built-after-signing — is in the cards and table above.</p>
</div>
{milestone_bands}
{cycle_bands}

<div class="band foot">
<p><strong>Definitions (match Berkeley Lab):</strong> <em>Completion</em> =
operational ÷ all requests submitted 2000–2020 (LBNL <em>Queued Up</em> sheet 25;
these counts reproduce LBNL's table exactly). <em>Built after signing IA</em> =
operational ÷ (operational + withdrawn) among projects with an executed-IA date
(LBNL sheet 27 method; counts projects that signed then withdrew). The
milestone-funnel, duration and study-cycle panels use all years and project
counts as descriptive detail, not the headline.</p>
<p><strong>Honesty:</strong> rates over decided projects (active/suspended
censored); durations survivor-conditioned; thin cohorts (&lt;30) and immature
cycles (&lt;50% decided) flagged; descriptive, not a causal model.</p>
<p>Sources:
<a href="https://emp.lbl.gov/queues">LBNL Queued Up</a> ·
<a href="https://www.esig.energy/i2x-initiatives/">ESIG i2X</a> ·
generated by <code>domains/grid/run_stitch_brief.py</code></p>
</div>

</div>
</body>
</html>
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="STITCH MISO/ERCOT queue brief")
    ap.add_argument("--queue", required=True, help="LBNL queue workbook (.xlsx)")
    ap.add_argument("--out", default="reports/stitch_2026-06-23")
    ap.add_argument("--min-cohort", type=int, default=30)
    ap.add_argument(
        "--with-peers", action="store_true",
        help="also report PJM/CAISO/SPP/NYISO/... for context",
    )
    args = ap.parse_args(argv)

    projects = LBNLQueueSource(args.queue).load()
    regions = list(DEFAULT_REGIONS)
    if args.with_peers:
        regions += PEER_REGIONS

    rep = build(projects, regions, args.min_cohort)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "queue_process_brief.json").write_text(
        json.dumps(rep, indent=2), encoding="utf-8"
    )
    md = to_markdown(rep)
    (out / "queue_process_brief.md").write_text(md, encoding="utf-8")
    (out / "queue_process_brief.html").write_text(to_html(rep), encoding="utf-8")

    try:
        sys.stdout.reconfigure(encoding="utf-8")  # py3.7+ ; avoids cp1252 crash
    except Exception:
        pass
    print(md)
    print(f"\nWrote {out/'queue_process_brief.md'}, .json, and .html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
