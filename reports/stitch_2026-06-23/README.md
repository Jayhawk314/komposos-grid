# STITCH — Regional Study Processes (MISO + ERCOT), 2026-06-23

Self-contained packet for the ESIG / Berkeley Lab **i2X STITCH** session on
2026-06-23. Everything here is generated from data already in this repo; no
new modeling, no invented numbers.

- Event: i2X STITCH "Regional Study Processes" (MISO + ERCOT, developer
  perspective from Engie). Part of DOE i2X, facilitated by ESIG + Berkeley
  Lab + Elevate Energy Consulting.
- Theme presenters were asked to cover: interconnection process milestones,
  study methods/assumptions, pre-interconnection and study tools/automation.

## What's in this folder

| File | What it is |
|---|---|
| `queue_process_brief.md` / `.json` | MISO vs ERCOT completion, durations, study-milestone funnel, study-cycle trend, from LBNL Queued Up |
| `queue_process_brief.html` | the same brief as a single self-contained page (no JS/CDN) — the shareable artifact |
| `README.md` | this map: webinar topic → repo capability → number, + the outreach note |

The brief has four panels: (1) **headline** completion comparison, (2) **process
duration** — median IR→IA / IA→COD / IR→COD months per region, (3) **milestone
funnel** — where decided projects die, (4) **study-cycle trend** — completion by
MISO DPP cluster cycle vs ERCOT entry-year cohort, with immature/thin cycles flagged.

Regenerate the brief at any time:

```bash
python -m domains.grid.run_stitch_brief \
    --queue domains/grid/data/LBNL_Ix_Queue_Data_File_thru2026.xlsx \
    --out reports/stitch_2026-06-23 --with-peers
```

## The headline finding (Berkeley Lab's own definitions — counts verified against their published tables)

| | MISO | ERCOT |
|---|---:|---:|
| Requests (2000–2020) | 2,806 | 1,553 |
| Built | 509 | 459 |
| **Completion** (built ÷ requests, LBNL sheet 25) | **18.1%** | **29.6%** |
| **Built after signing IA** (LBNL sheet 27 method) | **34.9%** | **79.7%** |

Two regions, two study processes — and the sharper point:
**after an interconnection agreement is signed, ERCOT projects get built ~80% of
the time but MISO's only ~35%.** The same official milestone means very
different things in the two regions. That is a harmonization gap you can measure.

> These numbers use Berkeley Lab's published definitions and the project counts
> reproduce LBNL's own tables exactly (verified). They are intentionally *not*
> the more dramatic "decided-only, all-years" framing, so the comparison can't
> be dismissed as cherry-picked.

## Webinar topic → repo capability → evidence

| Presenter topic | Capability in this repo | Concrete artifact / number |
|---|---|---|
| Interconnection **process milestones** | queue outcome by milestone | reaching an executed IA is the gate to getting built |
| **Study methods / where projects die** | built-after-signing per region | ERCOT ~80% vs MISO ~35% — the IA milestone binds differently across regions |
| **Speed — how long, not just how many** | IR→IA / IA→COD / IR→COD durations (`run_stitch_brief.py`) | MISO study stage 29.8 mo vs ERCOT 20.3 mo, but **end-to-end IR→COD is a tie** (MISO 39.1 vs ERCOT 44.3 mo) — ERCOT's edge is the study gate + completion odds, not the total clock |
| **Are the reforms working?** | study-cycle subdivision (`run_stitch_brief.py`) | MISO DPP completion declines cycle-over-cycle (DPP-2008 56% → DPP-2016 28% → DPP-2018 8%); reform-era cycles (DPP-2021/22) show massive *early* withdrawal (DPP-2022: 522 of 911) before any build can register |
| Cross-region **harmonization** | `sheaf_audit.py` coherence (gluing = harmonization, H¹ = mismatch) | same operator the repo uses to glue eGRID/EIA datasets; **ERCOT has no cluster construct at all** — the subdivision itself doesn't align across regions |
| **Pre-interconnection tools / automation** | `agent_server.py` grounded local agent + `whatif` tool | `agent_tools whatif --cut MISO-SWPP` |
| Seam / deliverability context | MISO interface + ERCOT hub price evidence | MISO-SWPP $5.09/MWh (93% congestion), ERCOT hub spread $4.94→$5.78/MWh (2023→2025) |

## Outreach note (icebreaker after the session)

Low-key, cites *their* dataset, offers something for *their* technical report —
not a framework pitch:

> Thanks for the MISO/ERCOT session. I've been doing an independent analysis of
> the LBNL Queued Up data and one result lines up with the panel's framing:
> after an IA is executed, ERCOT projects get built ~80% of the time but MISO's
> only ~35% — so the IA milestone isn't equivalent across regions. (Using your
> published definitions; the counts match the Queued Up tables.) Happy to share
> the reproducible brief if it's a useful reference point for the STITCH report.

## Honesty / caveats (keep these attached to any number)

- Rates are over **decided** projects only (operational | withdrawn); active and
  suspended projects are censored, not counted as failures.
- `ia_status` is the **last-known** milestone, so per-milestone completion is
  descriptive mediation, not a causal process model.
- Durations are **survivor-conditioned**: IA→COD and IR→COD are computed only over
  projects that *reached* COD, so they describe completers, not the queue overall.
  Negative and >30-year spans are dropped as date errors. IR→IA covers any project
  that reached IA (1,760 MISO / 1,174 ERCOT), so it is the most representative stage.
- Thin cohorts (< 30 decided) are flagged `(thin)` in the brief.
- Seam dollar figures are screening proxies from price spreads, not
  production-cost simulations — same labeling discipline as the waste ledger.

## Sources

- ESIG i2X initiatives — https://www.esig.energy/i2x-initiatives/
- DOE i2X Transmission Interconnection Roadmap — https://www.energy.gov/sites/default/files/2024-04/i2X%20Transmission%20Interconnection%20Roadmap.pdf
- MISO Generator Interconnection Queue Improvements — https://www.misoenergy.org/engage/MISO-Dashboard/generator-interconnection-queue-improvements/
- ERCOT connect-and-manage context (Utility Dive) — https://www.utilitydive.com/news/connect-and-manage-grid-interconnection-ferc-ercot-transmission-planning/698949/
- LBNL Queued Up — https://emp.lbl.gov/queues
