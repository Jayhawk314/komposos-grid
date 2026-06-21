# STITCH 2026-06-23 — MISO vs ERCOT Interconnection Study Process

Dataset: **LBNL Queued Up (thru 2026)** · method: LBNL-definition completion + built-after-signing, per region · national completion (decided): **16.5%**

## Headline comparison

Two headline numbers, both using Berkeley Lab's own definitions so they match the published *Queued Up* report (see Definitions at the bottom):

- **Completion** = share of all 2000–2020 requests now built (LBNL sheet 25).
- **Built after signing** = of projects that executed an interconnection agreement, the share built rather than withdrawn (LBNL sheet 27 method).

| Region | 2000–2020 requests | Built | Completion | Built after signing IA |
|---|---:|---:|---:|---:|
| **MISO** | 2,806 | 509 | **18.1%** | **34.9%** (476/1,365) |
| **ERCOT** | 1,553 | 459 | **29.6%** | **79.7%** (486/610) |

## Process duration — how long, not just how many (months)

Median elapsed months per stage, with [p25–p75] spread. **IR→IA** is the study/queue stage (the i2X speed bottleneck); **IA→COD** is construction; **IR→COD** is request-to-operation end to end. Computed only over projects that actually reached each milestone (so IA→COD is survivors), with negative and >30yr spans dropped as date errors.

| Region | IR→IA (study) | IA→COD (build) | IR→COD (total) |
|---|---|---|---|
| **MISO** | 29.8 mo [14.9–43.0], n=1760 | 18.8 mo [10.2–33.4], n=338 | 39.1 mo [22.3–57.0], n=539 |
| **ERCOT** | 20.3 mo [12.9–29.4], n=1174 | 25.9 mo [18.8–34.2], n=424 | 44.3 mo [30.2–56.9], n=480 |

## Study-milestone funnel (where decided projects ended up)

Completion rate among *decided* projects, grouped by their last-known interconnection-agreement milestone. A study phase with ~0% completion is where projects die; reaching **ia_executed** is the gate to service.

### MISO

| Milestone | Decided | Operational | Completion | |
|---|---:|---:|---:|---|
| ia_executed | 1,723 | 515 | 29.9% | |
| cluster_study | 696 | 0 | 0.0% | |
| in_progress_unknown_study | 417 | 0 | 0.0% | |
| (unlabeled) | 388 | 0 | 0.0% | |
| ia_pending | 286 | 0 | 0.0% | |
| feasibility_study | 166 | 0 | 0.0% | |
| system_impact_study | 81 | 0 | 0.0% | |
| facility_study | 9 | 0 | 0.0% | _(thin)_ |
| withdrawn | 8 | 0 | 0.0% | _(thin)_ |
| construction | 4 | 0 | 0.0% | _(thin)_ |

Active (still-in-queue) capacity by fuel — solar 133.2 GW, gas 65.3 GW, battery 54.9 GW, wind 42.7 GW, solar_battery 28.4 GW

### ERCOT

| Milestone | Decided | Operational | Completion | |
|---|---:|---:|---:|---|
| ia_executed | 654 | 613 | 93.7% | |
| facility_study | 1,008 | 0 | 0.0% | |
| ia_pending | 83 | 0 | 0.0% | |
| (unlabeled) | 17 | 0 | 0.0% | _(thin)_ |
| in_progress_unknown_study | 9 | 0 | 0.0% | _(thin)_ |

Active (still-in-queue) capacity by fuel — battery 133.4 GW, solar_battery 112.1 GW, solar 96.8 GW, wind 52.5 GW, gas 45.7 GW

## Study-cycle trend (are the reforms moving the needle?)

Completion by study cycle. MISO is sliced by DPP cluster cycle; ERCOT has no cluster study, so it is sliced by entry-year cohort — that asymmetry is itself a harmonization finding. Recent cycles are still mostly in study (**immature**: < 50% decided), so their completion rate is not yet meaningful — read the *active* and *decided-share* columns, not completion, for those.

### MISO

| Cycle | Total | Decided | Operational | Withdrawn | Active | Completion | Decided-share | |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| cluster:DPP-2008 | 32 | 32 | 18 | 14 | 0 | 56.2% | 100% |  |
| cluster:DPP-2009 | 52 | 52 | 19 | 33 | 0 | 36.5% | 100% |  |
| cluster:DPP-2010 | 31 | 31 | 7 | 24 | 0 | 22.6% | 100% |  |
| cluster:DPP-2011 | 8 | 8 | 0 | 8 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:DPP-2012 | 52 | 51 | 34 | 17 | 1 | 66.7% | 98% |  |
| cluster:DPP-2013 | 27 | 27 | 12 | 15 | 0 | 44.4% | 100% | _(thin)_ |
| cluster:DPP-2014 | 76 | 76 | 22 | 54 | 0 | 28.9% | 100% |  |
| cluster:DPP-2015 | 93 | 91 | 32 | 59 | 2 | 35.2% | 98% |  |
| cluster:DPP-2016 | 196 | 179 | 50 | 129 | 17 | 27.9% | 91% |  |
| cluster:DPP-2017 | 252 | 216 | 45 | 171 | 36 | 20.8% | 86% |  |
| cluster:DPP-2018 | 239 | 180 | 15 | 165 | 59 | 8.3% | 75% |  |
| cluster:DPP-2019 | 299 | 173 | 22 | 151 | 126 | 12.7% | 58% |  |
| cluster:DPP-2020 | 339 | 207 | 2 | 205 | 132 | 1.0% | 61% |  |
| cluster:DPP-2021 | 465 | 290 | 0 | 290 | 175 | 0.0% | 62% |  |
| cluster:DPP-2022 | 911 | 522 | 0 | 522 | 389 | 0.0% | 57% |  |
| cluster:DPP-2023 | 592 | 386 | 0 | 386 | 206 | 0.0% | 65% |  |
| cycle:(unknown) | 6 | 2 | 0 | 2 | 4 | 0.0% | 33% | _(immature, thin)_ |
| cycle:1995 | 1 | 1 | 0 | 1 | 0 | 0.0% | 100% | _(thin)_ |
| cycle:1998 | 4 | 2 | 0 | 2 | 2 | 0.0% | 50% | _(thin)_ |
| cycle:1999 | 16 | 11 | 6 | 5 | 5 | 54.5% | 69% | _(thin)_ |
| cycle:2000 | 50 | 49 | 21 | 28 | 1 | 42.9% | 98% |  |
| cycle:2001 | 99 | 95 | 21 | 74 | 4 | 22.1% | 96% |  |
| cycle:2002 | 82 | 81 | 27 | 54 | 1 | 33.3% | 99% |  |
| cycle:2003 | 104 | 104 | 49 | 55 | 0 | 47.1% | 100% |  |
| cycle:2004 | 77 | 72 | 25 | 47 | 5 | 34.7% | 94% |  |
| cycle:2005 | 91 | 89 | 36 | 53 | 2 | 40.4% | 98% |  |
| cycle:2006 | 109 | 108 | 21 | 87 | 1 | 19.4% | 99% |  |
| cycle:2007 | 140 | 140 | 17 | 123 | 0 | 12.1% | 100% |  |
| cycle:2008 | 120 | 119 | 6 | 113 | 1 | 5.0% | 99% |  |
| cycle:2009 | 79 | 79 | 1 | 78 | 0 | 1.3% | 100% |  |
| cycle:2010 | 67 | 67 | 4 | 63 | 0 | 6.0% | 100% |  |
| cycle:2011 | 44 | 44 | 1 | 43 | 0 | 2.3% | 100% |  |
| cycle:2012 | 18 | 16 | 0 | 16 | 2 | 0.0% | 89% | _(thin)_ |
| cycle:2013 | 17 | 17 | 1 | 16 | 0 | 5.9% | 100% | _(thin)_ |
| cycle:2014 | 12 | 12 | 0 | 12 | 0 | 0.0% | 100% | _(thin)_ |
| cycle:2015 | 1 | 1 | 0 | 1 | 0 | 0.0% | 100% | _(thin)_ |
| cycle:2016 | 38 | 37 | 1 | 36 | 1 | 2.7% | 97% |  |
| cycle:2017 | 1 | 0 | 0 | 0 | 1 | 0.0% | 0% | _(immature, thin)_ |
| cycle:2018 | 2 | 0 | 0 | 0 | 2 | 0.0% | 0% | _(immature, thin)_ |
| cycle:2019 | 6 | 2 | 0 | 2 | 4 | 0.0% | 33% | _(immature, thin)_ |
| cycle:2020 | 11 | 5 | 0 | 5 | 6 | 0.0% | 45% | _(immature, thin)_ |
| cycle:2021 | 14 | 11 | 0 | 11 | 3 | 0.0% | 79% | _(thin)_ |
| cycle:2022 | 36 | 7 | 0 | 7 | 29 | 0.0% | 19% | _(immature, thin)_ |
| cycle:2023 | 14 | 3 | 0 | 3 | 11 | 0.0% | 21% | _(immature, thin)_ |
| cycle:2024 | 95 | 23 | 0 | 23 | 72 | 0.0% | 24% | _(immature, thin)_ |
| cycle:2025 | 406 | 60 | 0 | 60 | 346 | 0.0% | 15% | _(immature)_ |

### ERCOT

| Cycle | Total | Decided | Operational | Withdrawn | Active | Completion | Decided-share | |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| cycle:(unknown) | 149 | 107 | 49 | 58 | 42 | 45.8% | 72% |  |
| cycle:2001 | 1 | 1 | 0 | 1 | 0 | 0.0% | 100% | _(thin)_ |
| cycle:2002 | 8 | 8 | 3 | 5 | 0 | 37.5% | 100% | _(thin)_ |
| cycle:2003 | 7 | 7 | 5 | 2 | 0 | 71.4% | 100% | _(thin)_ |
| cycle:2004 | 22 | 22 | 13 | 9 | 0 | 59.1% | 100% | _(thin)_ |
| cycle:2005 | 36 | 36 | 19 | 17 | 0 | 52.8% | 100% |  |
| cycle:2006 | 70 | 69 | 26 | 43 | 1 | 37.7% | 99% |  |
| cycle:2007 | 99 | 99 | 26 | 73 | 0 | 26.3% | 100% |  |
| cycle:2008 | 66 | 66 | 8 | 58 | 0 | 12.1% | 100% |  |
| cycle:2009 | 45 | 44 | 14 | 30 | 1 | 31.8% | 98% |  |
| cycle:2010 | 38 | 37 | 9 | 28 | 1 | 24.3% | 97% |  |
| cycle:2011 | 39 | 39 | 13 | 26 | 0 | 33.3% | 100% |  |
| cycle:2012 | 47 | 47 | 23 | 24 | 0 | 48.9% | 100% |  |
| cycle:2013 | 90 | 85 | 33 | 52 | 5 | 38.8% | 94% |  |
| cycle:2014 | 78 | 73 | 21 | 52 | 5 | 28.8% | 94% |  |
| cycle:2015 | 59 | 46 | 18 | 28 | 13 | 39.1% | 78% |  |
| cycle:2016 | 70 | 58 | 19 | 39 | 12 | 32.8% | 83% |  |
| cycle:2017 | 131 | 95 | 40 | 55 | 36 | 42.1% | 73% |  |
| cycle:2018 | 167 | 122 | 45 | 77 | 45 | 36.9% | 73% |  |
| cycle:2019 | 245 | 173 | 64 | 109 | 72 | 37.0% | 71% |  |
| cycle:2020 | 235 | 127 | 60 | 67 | 108 | 47.2% | 54% |  |
| cycle:2021 | 329 | 122 | 45 | 77 | 207 | 36.9% | 37% | _(immature)_ |
| cycle:2022 | 378 | 93 | 17 | 76 | 285 | 18.3% | 25% | _(immature)_ |
| cycle:2023 | 470 | 114 | 29 | 85 | 356 | 25.4% | 24% | _(immature)_ |
| cycle:2024 | 491 | 55 | 5 | 50 | 436 | 9.1% | 11% | _(immature)_ |
| cycle:2025 | 387 | 26 | 9 | 17 | 361 | 34.6% | 7% | _(immature, thin)_ |

## Reading for the harmonization discussion

- The two regions run structurally different study processes and the outcome gap is large and measured, not modeled.
- The dominant cause of withdrawal in both regions is *not reaching IA execution* — every study-phase exit is effectively terminal. Harmonization that compresses the study→IA path attacks the gap directly.
- This is the same OPTIMUS factorization used across the repo: the milestone is the discovered intermediate through which `proposed → operational` factors with higher confidence than the direct rate.

## Definitions (so the numbers are unambiguous)

- **Completion** uses LBNL's published definition: operational ÷ all requests submitted 2000–2020 (LBNL *Queued Up* sheet 25). These counts reproduce LBNL's own table exactly.
- **Built after signing** = operational ÷ (operational + withdrawn) among projects with an executed-IA date (LBNL sheet 27 method). It counts projects that signed and then withdrew.
- The **milestone funnel, durations, and study-cycle** panels below use all submission years and project counts, for breadth; they are descriptive, not the headline comparison.

_Honesty: rates over decided projects (active/suspended censored); durations survivor-conditioned; thin/immature cohorts flagged; descriptive mediation, not a causal model._
