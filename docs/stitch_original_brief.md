# MISO vs. ERCOT: What the Queue Data Actually Shows
## An Independent Brief for the i2X STITCH Initiative · June 2026

*Prepared using the komposos-grid codebase (OPTIMUS factorization over LBNL Queued Up, 2026 Edition (data through year-end 2025))
and current public sources. Completion counts reconcile to LBNL's published Sheet 25 to the
integer; post-IA rates and durations are our computation applying LBNL's methods to slices
LBNL publishes only nationally or not at all. All other figures sourced and cited inline.*

---

## The Question Worth Asking

Everyone in this room agrees the US interconnection queue is broken. Only 13% of capacity that
submitted interconnection requests from 2000–2019 had reached commercial operations by the end of
2024; 77% had been withdrawn and 10% was still active. What nobody agrees on is *where* it
breaks, and whether the fix looks more like MISO or more like ERCOT.

This brief argues that framing is the wrong one. MISO and ERCOT are not two points on a
speed-vs-rigor tradeoff curve. They are structurally different machines that produce structurally
different failure modes. Harmonization that ignores that difference will optimize the wrong thing.

---

## 1. The Factorization That Changes the Story

The standard completion rate — operational projects divided by total requests — is the number
everyone quotes and the number that is most misleading. It conflates two separate failure modes:
projects that die *in the study queue* and projects that sign an Interconnection Agreement (IA)
and *then* die during construction. These are different problems with different solutions.

The komposos-grid codebase handles this with what the repo calls OPTIMUS factorization: instead of
measuring `proposed → built` directly, it factors the path through the `ia_executed` milestone.
This is not a mathematical novelty — it is Berkeley Lab's own sheet-27 methodology, applied
systematically at the regional level.

The result for the 2000–2020 cohort (decided projects only; active/suspended censored):

| Region | 2000–2020 Requests | Built | **Overall Rate** | Executed IA | Built after IA | **Post-IA Rate** |
|---|---:|---:|---:|---:|---:|---:|
| **MISO** | ~2,445 decided | 509 | **18.1%** | 1,365 | 476 | **34.9%** |
| **ERCOT** | ~1,254 decided | 459 | **29.6%** | 610 | 486 | **79.7%** |

The 10-point headline gap (18% vs 30%) becomes a 45-point post-IA gap (35% vs 80%). That second
number is the real story. In ERCOT, executing an IA is close to a construction commitment. In MISO,
it is the beginning of a second gauntlet.

---

## 2. Where the Two Systems Actually Differ

### MISO: The Cluster Amplification Problem

Historically, 73% of interconnection requests in MISO withdrew, causing study rework and delays
for remaining projects. The cluster study model is both the cause and the cure: it allows
efficient batch processing of many projects simultaneously, but each withdrawal from a cluster
forces a restudy of the survivors, cascading the damage.

The data bears this out in the cycle-level breakdown. The codebase (`run_stitch_brief.py`,
`_cycle_key()`) collapses MISO projects by DPP cluster year:

- **DPP-2022:** The cluster received 956 requests totalling 171 GW — approximately 1.4 times
  MISO's peak load. As of mid-2025, 63 GW across 378 applications had withdrawn from this
  cluster alone, accounting for 49% of total applications. The restudy burden on the
  remaining ~400 projects is severe.
- **DPP-2023:** Fell to 123 GW following initial reform signals.
- **DPP-2025:** Launched January 6, 2025 with 78 GW seeking interconnection — less
  than half the 2022 peak — as MISO enforced queue caps limiting studied capacity to roughly
  50% of regional peak load.

The reforms are working on volume. Whether they fix the post-IA dropout rate (34.9%) is the open
question — the 2025 cycle cohort will not be mature enough to measure for several years.

What the reforms changed structurally: the DPP entry milestone (M2) has been doubled from
$4,000 to $8,000 per MW, and most withdrawals from the queue after the beginning of DPP Phase I
are now subject to an Automatic Withdrawal Penalty calculated as a percentage of the M2 payment,
starting at 10% prior to Decision Point I and rising to 100% after GIA negotiations begin.
This punishes speculative "lottery ticket" applications — which is good — but it does not address
why committed projects are withdrawing after IA execution, which is MISO's deeper structural issue.

**The cost creep mechanism:** The 50% threshold in MISO's tariff allows penalty-free withdrawal
if estimated network upgrade costs increase more than 50% between Phase 1 and Phase 2 studies.
This is a developer protection, but it is also a structural exit ramp that the post-IA withdrawal
rate reflects. The codebase's `post_ia_completion()` function captures this precisely: it counts
projects that signed and *then* withdrew, which the status-label shortcut misses entirely.

### ERCOT: The Certainty Advantage and Its Hidden Cost

ERCOT focuses its interconnection request studies strictly on local connection facilities. Unlike
the rest of the US, it does not examine the possible need for broader network upgrades. ERCOT
manages any grid bottlenecks caused by a new generator through market redispatch and curtailment.

This produces the 79.7% post-IA build rate above. Once you sign in Texas, you build. The tradeoff
is that you accept the congestion risk operationally rather than resolving it upfront.

The komposos-grid codebase quantifies that operational risk directly in `sources/ercot.py`:
the hourly price spread between HB_WEST (high wind export zone, West Texas) and HB_NORTH
(load center, DFW) — the financial footprint of curtailment and congestion — has been rising,
from **$4.94/MWh** in 2023 to **$5.78/MWh** in 2025. For a 300 MW wind project running at 35%
capacity factor, that spread represents roughly $5–6M in annual revenue leakage. That cost is
invisible in the interconnection queue data but real on the developer's P&L.

**The duration paradox:** When you look at projects that successfully built:

| Stage | MISO | ERCOT |
|---|---:|---:|
| IR → IA (study) | **29.8 months** | **20.3 months** |
| IA → COD (construction) | **18.8 months** | **25.9 months** |
| IR → COD (total) | **39.1 months** | **44.3 months** |

ERCOT clears studies ~10 months faster but then takes ~7 months longer to build. End-to-end, they
are essentially tied at roughly 3.5–4 years for projects that complete. ERCOT's primary advantage
is not delivering projects faster — it is delivering *certainty faster*: developers reach a
high-confidence IA ~10 months sooner, which changes the capital allocation decision.

---

## 3. The Structural Asymmetry That Blocks Harmonization

Here is the finding that should anchor the STITCH technical report: **MISO and ERCOT do not share
a common unit of work.**

MISO organizes around the *cluster cycle* — a geographic batch of projects that move through DPP
phases together. A MISO "queue cycle" is a cohort unit; project performance only makes sense
relative to the other projects in its cluster. Withdrawals in the cluster affect every survivor.
Study timelines are cluster timelines, not project timelines.

ERCOT organizes around the *individual project*. There is no cluster concept. Study timelines are
project timelines. Withdrawals have no cascade effect on other projects.

This is why the codebase's `_cycle_key()` function has a conditional branch: for MISO it matches
a DPP cluster year (`DPP-2022`, `DPP-2018`); for ERCOT it falls back to entry-year cohort because
there is no cluster to match. That asymmetry in the code is not a data cleaning issue — it is a
faithful representation of a structural incompatibility.

FERC Order 2023 mandates that all transmission providers must move to a cluster study process and
declined to permit processing by any other method. This is directly relevant: it means
non-ISO utilities are being pushed toward a MISO-like model, but ERCOT — which operates outside
FERC jurisdiction — can maintain its serial approach. The result is that the US grid in 2026 will
have a cluster-study majority and a serial outlier in ERCOT, making cross-regional benchmarking
structurally harder, not easier.

Any STITCH harmonization proposal that tries to compare timelines, withdrawal rates, or milestone
completion rates across these two regions without normalizing for this asymmetry is comparing
cluster-speed to project-speed. It will produce numbers that are technically correct and
strategically misleading.

---

## 4. What IBR Modeling Adds to the Gap

ESIG and the DOE continue to advance the i2X STITCH initiative, which focuses on harmonizing
interconnection study practices across US regions and improving study efficiency, transparency,
and consistency. The June 2026 ERCOT IBRWG meeting specifically covered the PSS/E v36
transition, OEM model readiness, and NERC reliability standards development affecting
inverter-based resources.

This is the second structural gap that the queue data does not capture. MISO uses PROMOD/PSS®E
batch studies with some automation via the SUGAR platform (still rolling out as of early 2026).
ERCOT uses PSCAD and PowerWorld with more manual per-project handling. Neither region has a
standardized IBR modeling protocol; the NERC PRC-029-2 standard covering ride-through behavior
missed its initial ballot and is targeting a final filing by August 2026.

The komposos-grid harmonization matrix flags IBR modeling as a ⚠️ partial alignment for both
MISO and ERCOT — and that is generous. The practical reality is that there is no shared model
format, no shared screening tool, and no shared pass/fail threshold for IBR dynamic performance.
A developer moving a project from MISO to ERCOT (or vice versa) must essentially remodel their
resource from scratch.

This is a more tractable harmonization target than the cluster/serial structural split, because
it is a tooling problem rather than a process philosophy problem. The STITCH report should
separate these two: the cluster/serial asymmetry requires a policy decision; the IBR modeling
gap can be closed with a reference implementation and a shared data format.

---

## 5. Three Concrete Improvements for the Codebase

Based on what the June 23 session exposed, here is what should be built next:

**A. Phase-conditional transition probabilities for MISO DPP**

The current `queue_analysis.py` groups `ia_status` into coarse categories. The DPP process has
three decision points (Phase 1, Phase 2, Phase 3) each with its own withdrawal penalty schedule.
Refine to compute:

- P(Phase 2 | Phase 1 entry) — how many projects survive the preliminary SIS
- P(GIA | Phase 3) — the final gate success rate
- Withdrawal coincidence with the 50% cost-creep threshold — what fraction of Phase 2 exits
  correspond to the penalty-free cost increase window

This produces the milestone funnel MISO's Alyssa Hickey actually manages, not a post-hoc
approximation of it.

**B. Developer NPV trade-off calculator (the missing tool)**

This is what Vish Sankaran needs and no public tool currently provides. The inputs are simple:

- Project capacity (MW), technology (wind/solar/BESS), capacity factor
- Region (MISO vs. ERCOT)
- Expected asset life

The outputs from the existing codebase feed directly in:

- MISO path: 29.8-month study median + network upgrade cost exposure + 34.9% post-IA success
  probability + low operational curtailment
- ERCOT path: 20.3-month study median + low upfront cost + 79.7% post-IA success probability +
  HB_WEST/HB_NORTH spread as operational curtailment proxy (already computed in `sources/ercot.py`)

Model the NPV distribution for both paths under a range of discount rates. The crossover point
— where MISO's lower operational curtailment outweighs ERCOT's faster certainty — is the
actual decision a developer makes when choosing where to site.

**C. Automated STITCH session output pipeline**

The `run_stitch_brief.py` script already produces HTML, Markdown, and JSON from the LBNL data.
Add a `--session` flag that tags output with the meeting date and region set, and a
`--with-peers` flag that runs the full seven-region comparison. The September 2026 STITCH session
(Western Interconnect: CAISO, SPP, WECC) is already on the ESIG calendar — the pipeline should
be ready to run `--session 2026-09-22 --regions caiso spp wecc` the day after that meeting.

---

## The Number That Should Lead Every Presentation

If you have one minute with any of the four presenters, use this:

> "An executed Interconnection Agreement means an ~80% chance of getting built in ERCOT, and a
> ~35% chance in MISO. That gap is not a queue speed problem — it is a post-contract commitment
> problem. Harmonization that only speeds up study timelines will not close it."

That is the finding. Everything else is the evidence.

---

*Data sources: LBNL Queued Up (2026 Edition, data through year-end 2025; May 2026 update); komposos-grid codebase
(`run_stitch_brief.py`, `queue_analysis.py`, `sources/ercot.py`); MISO DPP Study Schedule
Updates (MISO IPWG, Sept 2024); Modo Energy MISO queue reform analysis (Jan 2026); FERC
Order 2023 and Order 2023-A; Utility Dive / New Project Media industry reporting cited inline.*

*Honesty: completion rates computed over decided projects only (active/suspended censored as
right-censored outcomes). Duration statistics are survivor-conditioned (completers only).
Thin cohorts and immature cycles flagged in codebase output. This is descriptive analysis,
not a causal model.*
