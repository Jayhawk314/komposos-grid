# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Generate per-region STITCH engagement packs from the queue process brief.

The i2X STITCH series continues with "Regional Study Processes Cont." sessions
(2026-07-28, 2026-08-18, 2026-09-22). Each session brings new regions to the
panel. This module gives every region in the 9-region brief the same
deep-dive treatment the June 23 MISO/ERCOT session material received, so the
per-session tailoring left to do when presenters are confirmed is narrative,
not analysis.

Outputs (all derived from reports/stitch_2026-06-23/queue_process_brief.json,
which reconciles to LBNL Queued Up):
    reports/stitch_sessions/region_packs/<region>.md   one pack per region
    reports/stitch_sessions/region_packs/INDEX.md      cross-region comparison

Run:
    python -m domains.grid.run_region_packs
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
BRIEF_PATH = ROOT_DIR / "reports" / "stitch_2026-06-23" / "queue_process_brief.json"
OUT_DIR = ROOT_DIR / "reports" / "stitch_sessions" / "region_packs"

DISPLAY = {
    "miso": "MISO",
    "ercot": "ERCOT",
    "pjm": "PJM",
    "caiso": "CAISO",
    "spp": "SPP",
    "nyiso": "NYISO",
    "iso_ne": "ISO-NE",
    "southeast": "Southeast (non-market)",
    "west": "West (non-ISO)",
}

PROVENANCE = (
    "> 📏 **Measured** — every figure derives from the LBNL *Queued Up* data file "
    "(2026 Edition, data through year-end 2025); headline counts reconcile to the published tables. "
    "Regenerate with `python -m domains.grid.run_region_packs`.\n"
)


def _fmt_months(entry: dict | None) -> str:
    if not entry or entry.get("median_months") is None:
        return "—"
    return (f"{entry['median_months']:.1f} mo "
            f"(IQR {entry.get('p25_months', 0):.1f}–{entry.get('p75_months', 0):.1f}, "
            f"n={entry.get('n', 0):,})")


def _region_pack(r: dict) -> str:
    name = DISPLAY.get(r["region"], r["region"].upper())
    lbnl = r.get("completion_lbnl", {})
    pia = r.get("post_ia", {})
    dur = r.get("durations", {})

    lines = [
        f"# {name} — STITCH Regional Study Process Engagement Pack",
        "",
        PROVENANCE,
        "## Headline queue metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Total interconnection requests (all-time) | {r.get('total_requests', 0):,} |",
        f"| Decided (built or withdrawn) | {r.get('decided', 0):,} |",
        f"| Operational (built) | {r.get('operational', 0):,} |",
        f"| Active in queue today | {r.get('active_in_queue', 0):,} |",
    ]
    if lbnl:
        lines.append(
            f"| LBNL completion rate ({lbnl.get('window', '2000-2020')}) | "
            f"**{lbnl.get('rate', 0):.1%}** ({lbnl.get('built', 0):,} of {lbnl.get('requests', 0):,}) |")
    has_post_ia = bool(pia and pia.get("signed_decided"))
    if has_post_ia:
        lines.append(
            f"| Post-IA completion (built after signing IA) | "
            f"**{pia.get('rate', 0):.1%}** ({pia.get('built_after_signing', 0):,} of {pia.get('signed_decided', 0):,}) |")
    lines += [
        "",
        "## Where the region sits on the IA-certainty spectrum",
        "",
    ]
    if has_post_ia:
        lines += [
            "The June 23 session's core finding: an executed IA is an ~80% completion promise "
            "in ERCOT but roughly a coin-flip (~35%) in MISO. This region's post-IA rate of "
            f"**{pia.get('rate', 0):.1%}** places it on that spectrum — a talking point the "
            "presenters can react to directly.",
        ]
    else:
        lines += [
            "**Not computable for this region** — its LBNL records do not track IA execution "
            "for withdrawn projects, so post-IA completion is undefined here. This is itself "
            "a harmonization finding: milestone *data coverage* differs across regions, which "
            "is a question worth putting to this region's presenters.",
        ]
    lines += [
        "",
        "## Pipeline durations (successful projects, medians)",
        "",
        "| Stage | Duration |",
        "|---|---|",
        f"| Request → IA (study phase) | {_fmt_months(dur.get('ir_to_ia'))} |",
        f"| IA → COD (construction) | {_fmt_months(dur.get('ia_to_cod'))} |",
        f"| Request → COD (end-to-end) | {_fmt_months(dur.get('ir_to_cod'))} |",
        "",
        "## Milestone funnel (decided 2000–2020 cohort)",
        "",
        "| Milestone reached | Decided | Built | Completion |",
        "|---|---:|---:|---:|",
    ]
    for m in r.get("milestones", []):
        flag = " ⚠ thin cohort" if m.get("below_min_cohort") else ""
        lines.append(
            f"| {m['milestone']}{flag} | {m.get('n_decided', 0):,} | "
            f"{m.get('n_operational', 0):,} | {m.get('completion', 0):.1%} |")

    cycles = [c for c in r.get("cycles", []) if not c.get("thin")]
    if cycles:
        lines += [
            "",
            "## Recent study cycles / entry cohorts",
            "",
            "| Cycle | Total | Built | Withdrawn | Active | Completion |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for c in cycles[-10:]:
            label = c["cycle"].replace("cycle:", "")
            note = " *(immature)*" if c.get("immature") else ""
            lines.append(
                f"| {label}{note} | {c.get('total', 0):,} | {c.get('operational', 0):,} | "
                f"{c.get('withdrawn', 0):,} | {c.get('active', 0):,} | {c.get('completion', 0):.0%} |")

    fuel = r.get("active_fuel_gw", {})
    if fuel:
        top = sorted(fuel.items(), key=lambda kv: -kv[1])[:6]
        lines += [
            "",
            "## Active queue by fuel (GW)",
            "",
            "| Fuel | GW |",
            "|---|---:|",
        ]
        lines += [f"| {k.replace('_', ' + ')} | {v:,.1f} |" for k, v in top if v > 0]

    lines += [
        "",
        "## Session prep notes *(fill in when presenters are confirmed)*",
        "",
        "- **Presenters:** _TBD — check the ESIG events page for this session_",
        "- **Their live question:** _what reform / process pain is this region actively debating?_",
        "- **Claims to listen for:** _numbers stated on the panel → run each through `/verify-claim`_",
        "- **Bridge phrase:** _one sentence connecting this pack's post-IA rate to their process design_",
        "",
    ]
    return "\n".join(lines)


def _index(regions: list[dict]) -> str:
    lines = [
        "# Cross-Region Comparison — the IA-Certainty Spectrum",
        "",
        PROVENANCE,
        "One table the STITCH panel has likely never seen: **what an executed IA is worth, "
        "by region.** The same contract milestone carries very different completion "
        "information depending on where it is signed.",
        "",
        "| Region | Requests | LBNL completion | Post-IA completion | Study (Req→IA) | Build (IA→COD) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    # Regions whose LBNL records don't track IA execution (signed_decided == 0)
    # get "—", not a false 0%, and sort to the bottom.
    def _rank_key(r: dict):
        pia = r.get("post_ia", {})
        return -(pia.get("rate") or 0) if pia.get("signed_decided") else 1.0

    ranked = sorted(regions, key=_rank_key)
    def _mo(entry: dict) -> str:
        med = entry.get("median_months")
        return f"{med:.1f} mo" if med is not None else "—"

    for r in ranked:
        name = DISPLAY.get(r["region"], r["region"].upper())
        lbnl = r.get("completion_lbnl", {})
        pia = r.get("post_ia", {})
        dur = r.get("durations", {})
        post_ia_cell = (f"**{pia.get('rate') or 0:.1%}**"
                        if pia.get("signed_decided") else "— *(not tracked)*")
        lines.append(
            f"| [{name}]({r['region']}.md) | {r.get('total_requests') or 0:,} | "
            f"{lbnl.get('rate') or 0:.1%} | {post_ia_cell} | "
            f"{_mo(dur.get('ir_to_ia') or {})} | "
            f"{_mo(dur.get('ia_to_cod') or {})} |")
    lines += [
        "",
        "*\"Not tracked\" is a finding, not a gap in our pipeline: those regions' LBNL "
        "records do not record IA execution for withdrawn projects, so the milestone's "
        "certainty content cannot be computed there — direct evidence that milestone data "
        "coverage itself needs harmonizing.*",
        "",
        "Sessions this feeds: *Regional Study Processes Cont.* — 2026-07-28, 2026-08-18, "
        "2026-09-22 (ESIG i2X STITCH). When a session's presenters are announced, start "
        "from that region's pack and fill in the Session prep notes.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    with open(BRIEF_PATH, encoding="utf-8") as f:
        brief = json.load(f)
    regions = brief["regions"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for r in regions:
        out = OUT_DIR / f"{r['region']}.md"
        out.write_text(_region_pack(r), encoding="utf-8")
        print(f"wrote {out}")
    idx = OUT_DIR / "INDEX.md"
    idx.write_text(_index(regions), encoding="utf-8")
    print(f"wrote {idx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
