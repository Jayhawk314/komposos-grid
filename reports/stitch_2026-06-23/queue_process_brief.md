# STITCH 2026-06-23 — MISO vs ERCOT Interconnection Study Process

Dataset: **LBNL Queued Up, 2026 Edition (data through year-end 2025)** · method: LBNL-definition completion + built-after-signing, per region · national completion (decided): **16.5%**

## Headline comparison

Two headline numbers, both using Berkeley Lab's own definitions. **Completion** reconciles to LBNL's published Sheet 25 regional table to the integer. **Built after signing** applies LBNL's Sheet 27 method, which LBNL publishes at national level only — the per-region split is this project's own computation, not an LBNL-published figure (see Definitions at the bottom):

- **Completion** = share of all 2000–2020 requests now built (LBNL sheet 25).
- **Built after signing** = of projects that executed an interconnection agreement, the share built rather than withdrawn (LBNL sheet 27 method).

| Region | 2000–2020 requests | Built | Completion | Built after signing IA |
|---|---:|---:|---:|---:|
| **MISO** | 2,806 | 509 | **18.1%** | **34.9%** (476/1,365) |
| **ERCOT** | 1,553 | 459 | **29.6%** | **79.7%** (486/610) |
| **PJM** | 5,589 | 1,145 | **20.5%** | **85.9%** (195/227) |
| **CAISO** | 1,910 | 232 | **12.1%** | **90.7%** (196/216) |
| **SPP** | 1,682 | 277 | **16.5%** | **0.0%** (0/0) |
| **NYISO** | 1,035 | 201 | **19.4%** | **70.0%** (35/50) |
| **SOUTHEAST** | 2,072 | 328 | **15.8%** | **55.4%** (92/166) |
| **WEST** | 4,874 | 823 | **16.9%** | **71.9%** (440/612) |
| **ISO_NE** | 827 | 222 | **26.8%** | **75.2%** (97/129) |

## Process duration — how long, not just how many (months)

Median elapsed months per stage, with [p25–p75] spread. **IR→IA** is the study/queue stage (the i2X speed bottleneck); **IA→COD** is construction; **IR→COD** is request-to-operation end to end. Computed only over projects that actually reached each milestone (so IA→COD is survivors), with negative and >30yr spans dropped as date errors.

| Region | IR→IA (study) | IA→COD (build) | IR→COD (total) |
|---|---|---|---|
| **MISO** | 29.8 mo [14.9–43.0], n=1760 | 18.8 mo [10.2–33.4], n=338 | 39.1 mo [22.3–57.0], n=539 |
| **ERCOT** | 20.3 mo [12.9–29.4], n=1174 | 25.9 mo [18.8–34.2], n=424 | 44.3 mo [30.2–56.9], n=480 |
| **PJM** | 35.5 mo [22.0–49.4], n=247 | 22.8 mo [9.7–36.4], n=172 | 37.9 mo [19.5–62.0], n=1195 |
| **CAISO** | 44.4 mo [31.1–58.6], n=445 | 28.6 mo [16.5–48.6], n=193 | 70.5 mo [51.5–95.7], n=248 |
| **SPP** | — (n=0) | — (n=0) | 47.7 mo [29.8–71.3], n=554 |
| **NYISO** | 41.2 mo [31.3–49.1], n=109 | 20.4 mo [10.7–31.0], n=26 | 55.3 mo [40.8–75.3], n=83 |
| **SOUTHEAST** | 21.2 mo [16.6–27.6], n=89 | 23.2 mo [15.2–33.1], n=84 | 45.5 mo [32.1–59.8], n=234 |
| **WEST** | 17.5 mo [11.0–32.4], n=724 | 5.8 mo [0.0–29.6], n=32 | 25.4 mo [13.5–52.5], n=183 |
| **ISO_NE** | 33.7 mo [23.1–46.3], n=170 | — (n=0) | — (n=0) |

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

### PJM

| Milestone | Decided | Operational | Completion | |
|---|---:|---:|---:|---|
| ia_executed | 2,166 | 1,192 | 55.0% | |
| feasibility_study | 2,499 | 0 | 0.0% | |
| system_impact_study | 1,505 | 0 | 0.0% | |
| in_progress_unknown_study | 193 | 0 | 0.0% | |
| facility_study | 26 | 0 | 0.0% | _(thin)_ |
| ia_pending | 14 | 0 | 0.0% | _(thin)_ |
| withdrawn | 8 | 0 | 0.0% | _(thin)_ |
| (unlabeled) | 7 | 0 | 0.0% | _(thin)_ |

Active (still-in-queue) capacity by fuel — solar 59.8 GW, battery 29.6 GW, gas 14.0 GW, solar_battery 13.8 GW, offshore_wind 13.5 GW

### CAISO

| Milestone | Decided | Operational | Completion | |
|---|---:|---:|---:|---|
| ia_executed | 289 | 235 | 81.3% | |
| system_impact_study | 1,354 | 0 | 0.0% | |
| in_progress_unknown_study | 328 | 0 | 0.0% | |
| feasibility_study | 269 | 0 | 0.0% | |
| not_started | 179 | 0 | 0.0% | |
| (unlabeled) | 10 | 0 | 0.0% | _(thin)_ |
| withdrawn | 6 | 0 | 0.0% | _(thin)_ |

Active (still-in-queue) capacity by fuel — solar_battery 62.1 GW, battery 47.6 GW, solar 6.4 GW, wind_battery 3.0 GW, wind 2.9 GW

### SPP

| Milestone | Decided | Operational | Completion | |
|---|---:|---:|---:|---|
| ia_executed | 299 | 299 | 100.0% | |
| withdrawn | 1,846 | 0 | 0.0% | |

Active (still-in-queue) capacity by fuel — solar 37.7 GW, gas 33.1 GW, battery 31.4 GW, wind 26.7 GW, solar_battery 17.7 GW

### NYISO

| Milestone | Decided | Operational | Completion | |
|---|---:|---:|---:|---|
| ia_executed | 215 | 215 | 100.0% | |
| (unlabeled) | 1,531 | 0 | 0.0% | |

Active (still-in-queue) capacity by fuel — battery 11.1 GW, solar 6.6 GW, offshore_wind 4.4 GW, wind 2.9 GW, solar_battery 2.1 GW

### SOUTHEAST

| Milestone | Decided | Operational | Completion | |
|---|---:|---:|---:|---|
| ia_executed | 535 | 529 | 98.9% | |
| withdrawn | 1,629 | 0 | 0.0% | |
| (unlabeled) | 975 | 0 | 0.0% | |
| in_progress_unknown_study | 49 | 0 | 0.0% | |
| feasibility_study | 34 | 0 | 0.0% | |
| facility_study | 22 | 0 | 0.0% | _(thin)_ |
| system_impact_study | 22 | 0 | 0.0% | _(thin)_ |
| ia_pending | 1 | 0 | 0.0% | _(thin)_ |

Active (still-in-queue) capacity by fuel — gas 64.1 GW, solar 51.6 GW, battery 19.4 GW, solar_battery 15.0 GW, nuclear 3.7 GW

### WEST

| Milestone | Decided | Operational | Completion | |
|---|---:|---:|---:|---|
| ia_executed | 1,168 | 963 | 82.4% | |
| (unlabeled) | 2,487 | 0 | 0.0% | |
| withdrawn | 1,800 | 0 | 0.0% | |
| in_progress_unknown_study | 328 | 0 | 0.0% | |
| facility_study | 173 | 0 | 0.0% | |
| system_impact_study | 139 | 0 | 0.0% | |
| feasibility_study | 102 | 0 | 0.0% | |
| cluster_study | 29 | 0 | 0.0% | _(thin)_ |
| suspended | 13 | 0 | 0.0% | _(thin)_ |
| not_started | 1 | 0 | 0.0% | _(thin)_ |

Active (still-in-queue) capacity by fuel — solar_battery 185.6 GW, battery 76.0 GW, wind 63.5 GW, solar 34.1 GW, gas 25.3 GW

### ISO_NE

| Milestone | Decided | Operational | Completion | |
|---|---:|---:|---:|---|
| ia_executed | 259 | 228 | 88.0% | |
| (unlabeled) | 633 | 0 | 0.0% | |
| system_impact_study | 147 | 0 | 0.0% | |
| feasibility_study | 100 | 0 | 0.0% | |
| in_progress_unknown_study | 49 | 0 | 0.0% | |
| not_started | 17 | 0 | 0.0% | _(thin)_ |
| facility_study | 3 | 0 | 0.0% | _(thin)_ |
| ia_pending | 1 | 0 | 0.0% | _(thin)_ |
| suspended | 1 | 0 | 0.0% | _(thin)_ |

Active (still-in-queue) capacity by fuel — battery 6.8 GW, offshore_wind 6.0 GW, solar 1.4 GW, solar_battery 0.2 GW, gas_oil 0.1 GW

## Study-cycle trend (are the reforms moving the needle?)

Completion by study cycle. MISO is sliced by DPP cluster cycle; ERCOT has no cluster study, so it is sliced by entry-year cohort — that asymmetry is itself a harmonization finding. Recent cycles are still mostly in study (**immature**: < 50% decided), so their completion rate is not yet meaningful — read the *active* and *decided-share* columns, not completion, for those.

### MISO

| Cycle | Total | Decided | Operational | Withdrawn | Active | Completion | Decided-share | |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| cluster:DPP-2008 | 32 | 32 | 18 | 14 | 0 | 56.2% | 100% |  |
| cluster:DPP-2009 | 52 | 52 | 19 | 33 | 0 | 36.5% | 100% |  |
| cluster:DPP-2010 | 31 | 31 | 7 | 24 | 0 | 22.6% | 100% |  |
| cluster:DPP-2011 | 2 | 2 | 0 | 2 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:DPP-2012 | 46 | 45 | 34 | 11 | 1 | 75.6% | 98% |  |
| cluster:DPP-2013 | 17 | 17 | 12 | 5 | 0 | 70.6% | 100% | _(thin)_ |
| cluster:DPP-2014 | 33 | 33 | 22 | 11 | 0 | 66.7% | 100% |  |
| cluster:DPP-2015 | 58 | 56 | 32 | 24 | 2 | 57.1% | 97% |  |
| cluster:DPP-2016 | 121 | 104 | 48 | 56 | 17 | 46.2% | 86% |  |
| cluster:DPP-2017 | 252 | 216 | 45 | 171 | 36 | 20.8% | 86% |  |
| cluster:DPP-2018 | 239 | 180 | 15 | 165 | 59 | 8.3% | 75% |  |
| cluster:DPP-2019 | 299 | 173 | 22 | 151 | 126 | 12.7% | 58% |  |
| cluster:DPP-2020 | 339 | 207 | 2 | 205 | 132 | 1.0% | 61% |  |
| cluster:DPP-2021 | 465 | 290 | 0 | 290 | 175 | 0.0% | 62% |  |
| cluster:DPP-2022 | 911 | 522 | 0 | 522 | 389 | 0.0% | 57% |  |
| cluster:DPP-2023 | 592 | 386 | 0 | 386 | 206 | 0.0% | 65% |  |
| cluster:FES-2011 | 6 | 6 | 0 | 6 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:FES-2012 | 2 | 2 | 0 | 2 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:FES-2013 | 7 | 7 | 0 | 7 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:FES-2014 | 38 | 38 | 0 | 38 | 0 | 0.0% | 100% |  |
| cluster:FES-2015 | 26 | 26 | 0 | 26 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:FES-2016 | 62 | 62 | 0 | 62 | 0 | 0.0% | 100% |  |
| cluster:MM-2016 | 2 | 2 | 2 | 0 | 0 | 100.0% | 100% | _(thin)_ |
| cluster:SPA-2012 | 4 | 4 | 0 | 4 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:SPA-2013 | 3 | 3 | 0 | 3 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:SPA-2014 | 5 | 5 | 0 | 5 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:SPA-2015 | 9 | 9 | 0 | 9 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:SPA-2016 | 11 | 11 | 0 | 11 | 0 | 0.0% | 100% | _(thin)_ |
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

### PJM

| Cycle | Total | Decided | Operational | Withdrawn | Active | Completion | Decided-share | |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| cycle:(unknown) | 48 | 48 | 0 | 48 | 0 | 0.0% | 100% |  |
| cycle:1997 | 13 | 13 | 10 | 3 | 0 | 76.9% | 100% | _(thin)_ |
| cycle:1998 | 18 | 18 | 9 | 9 | 0 | 50.0% | 100% | _(thin)_ |
| cycle:1999 | 90 | 90 | 28 | 62 | 0 | 31.1% | 100% |  |
| cycle:2000 | 83 | 83 | 24 | 59 | 0 | 28.9% | 100% |  |
| cycle:2001 | 91 | 91 | 26 | 65 | 0 | 28.6% | 100% |  |
| cycle:2002 | 51 | 51 | 16 | 35 | 0 | 31.4% | 100% |  |
| cycle:2003 | 50 | 50 | 18 | 32 | 0 | 36.0% | 100% |  |
| cycle:2004 | 53 | 53 | 21 | 32 | 0 | 39.6% | 100% |  |
| cycle:2005 | 133 | 133 | 51 | 82 | 0 | 38.3% | 100% |  |
| cycle:2006 | 157 | 157 | 52 | 105 | 0 | 33.1% | 100% |  |
| cycle:2007 | 220 | 220 | 115 | 105 | 0 | 52.3% | 100% |  |
| cycle:2008 | 219 | 219 | 47 | 172 | 0 | 21.5% | 100% |  |
| cycle:2009 | 179 | 179 | 57 | 122 | 0 | 31.8% | 100% |  |
| cycle:2010 | 442 | 442 | 81 | 361 | 0 | 18.3% | 100% |  |
| cycle:2011 | 348 | 348 | 59 | 289 | 0 | 17.0% | 100% |  |
| cycle:2012 | 159 | 159 | 48 | 111 | 0 | 30.2% | 100% |  |
| cycle:2013 | 143 | 143 | 63 | 80 | 0 | 44.1% | 100% |  |
| cycle:2014 | 187 | 186 | 60 | 126 | 1 | 32.3% | 99% |  |
| cycle:2015 | 305 | 298 | 67 | 231 | 7 | 22.5% | 98% |  |
| cycle:2016 | 389 | 358 | 108 | 250 | 31 | 30.2% | 92% |  |
| cycle:2017 | 352 | 308 | 72 | 236 | 44 | 23.4% | 88% |  |
| cycle:2018 | 435 | 367 | 56 | 311 | 68 | 15.3% | 84% |  |
| cycle:2019 | 667 | 484 | 75 | 409 | 183 | 15.5% | 73% |  |
| cycle:2020 | 926 | 748 | 29 | 719 | 178 | 3.9% | 81% |  |
| cycle:2021 | 868 | 819 | 0 | 819 | 49 | 0.0% | 94% |  |
| cycle:2022 | 483 | 182 | 0 | 182 | 301 | 0.0% | 38% | _(immature)_ |
| cycle:2023 | 167 | 11 | 0 | 11 | 156 | 0.0% | 7% | _(immature, thin)_ |
| cycle:2024 | 2 | 0 | 0 | 0 | 2 | 0.0% | 0% | _(immature, thin)_ |
| cycle:2025 | 388 | 160 | 0 | 160 | 228 | 0.0% | 41% | _(immature)_ |

### CAISO

| Cycle | Total | Decided | Operational | Withdrawn | Active | Completion | Decided-share | |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| cycle:1999 | 1 | 1 | 1 | 0 | 0 | 100.0% | 100% | _(thin)_ |
| cycle:2000 | 8 | 8 | 4 | 4 | 0 | 50.0% | 100% | _(thin)_ |
| cycle:2001 | 1 | 1 | 0 | 1 | 0 | 0.0% | 100% | _(thin)_ |
| cycle:2002 | 3 | 3 | 2 | 1 | 0 | 66.7% | 100% | _(thin)_ |
| cycle:2003 | 11 | 10 | 6 | 4 | 1 | 60.0% | 91% | _(thin)_ |
| cycle:2004 | 29 | 28 | 8 | 20 | 1 | 28.6% | 97% | _(thin)_ |
| cycle:2005 | 30 | 26 | 9 | 17 | 4 | 34.6% | 87% | _(thin)_ |
| cycle:2006 | 79 | 75 | 14 | 61 | 4 | 18.7% | 95% |  |
| cycle:2007 | 134 | 131 | 15 | 116 | 3 | 11.5% | 98% |  |
| cycle:2008 | 181 | 179 | 18 | 161 | 2 | 10.1% | 99% |  |
| cycle:2009 | 66 | 63 | 15 | 48 | 3 | 23.8% | 95% |  |
| cycle:2010 | 212 | 209 | 39 | 170 | 3 | 18.7% | 99% |  |
| cycle:2011 | 207 | 202 | 14 | 188 | 5 | 6.9% | 98% |  |
| cycle:2012 | 66 | 65 | 5 | 60 | 1 | 7.7% | 98% |  |
| cycle:2013 | 61 | 58 | 10 | 48 | 3 | 17.2% | 95% |  |
| cycle:2014 | 89 | 80 | 10 | 70 | 9 | 12.5% | 90% |  |
| cycle:2015 | 126 | 111 | 20 | 91 | 15 | 18.0% | 88% |  |
| cycle:2016 | 126 | 113 | 17 | 96 | 13 | 15.0% | 90% |  |
| cycle:2017 | 91 | 74 | 9 | 65 | 17 | 12.2% | 81% |  |
| cycle:2018 | 98 | 75 | 8 | 67 | 23 | 10.7% | 77% |  |
| cycle:2019 | 139 | 102 | 5 | 97 | 37 | 4.9% | 73% |  |
| cycle:2020 | 153 | 111 | 4 | 107 | 42 | 3.6% | 73% |  |
| cycle:2021 | 361 | 222 | 2 | 220 | 139 | 0.9% | 61% |  |
| cycle:2022 | 2 | 2 | 0 | 2 | 0 | 0.0% | 100% | _(thin)_ |
| cycle:2023 | 594 | 486 | 0 | 486 | 108 | 0.0% | 82% |  |

### SPP

| Cycle | Total | Decided | Operational | Withdrawn | Active | Completion | Decided-share | |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| cluster:DISIS-2009 | 11 | 11 | 11 | 0 | 0 | 100.0% | 100% | _(thin)_ |
| cluster:DISIS-2010 | 21 | 21 | 19 | 2 | 0 | 90.5% | 100% | _(thin)_ |
| cluster:DISIS-2011 | 25 | 23 | 21 | 2 | 2 | 91.3% | 92% | _(thin)_ |
| cluster:DISIS-2012 | 14 | 14 | 14 | 0 | 0 | 100.0% | 100% | _(thin)_ |
| cluster:DISIS-2013 | 13 | 11 | 10 | 1 | 2 | 90.9% | 85% | _(thin)_ |
| cluster:DISIS-2014 | 21 | 21 | 19 | 2 | 0 | 90.5% | 100% | _(thin)_ |
| cluster:DISIS-2015 | 43 | 42 | 28 | 14 | 1 | 66.7% | 98% |  |
| cluster:DISIS-2016 | 110 | 87 | 47 | 40 | 23 | 54.0% | 79% |  |
| cluster:DISIS-2017 | 247 | 181 | 12 | 169 | 66 | 6.6% | 73% |  |
| cluster:DISIS-2018 | 128 | 88 | 0 | 88 | 40 | 0.0% | 69% |  |
| cluster:DISIS-2019 | 74 | 51 | 1 | 50 | 23 | 2.0% | 69% |  |
| cluster:DISIS-2020 | 94 | 61 | 7 | 54 | 33 | 11.5% | 65% |  |
| cluster:DISIS-2021 | 108 | 64 | 0 | 64 | 44 | 0.0% | 59% |  |
| cluster:DISIS-2022 | 247 | 207 | 0 | 207 | 40 | 0.0% | 84% |  |
| cluster:DISIS-2023 | 241 | 194 | 0 | 194 | 47 | 0.0% | 80% |  |
| cluster:DISIS-2024 | 381 | 130 | 0 | 130 | 251 | 0.0% | 34% | _(immature)_ |
| cluster:ERAS-2025 | 36 | 0 | 0 | 0 | 36 | 0.0% | 0% | _(immature, thin)_ |
| cluster:FCS-2018 | 3 | 3 | 0 | 3 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:FCS-2019 | 6 | 6 | 0 | 6 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:ICS-2008 | 54 | 54 | 53 | 1 | 0 | 98.1% | 100% |  |
| cycle:(unknown) | 26 | 26 | 18 | 8 | 0 | 69.2% | 100% | _(thin)_ |
| cycle:2000 | 7 | 7 | 0 | 7 | 0 | 0.0% | 100% | _(thin)_ |
| cycle:2001 | 38 | 38 | 5 | 33 | 0 | 13.2% | 100% |  |
| cycle:2002 | 24 | 24 | 2 | 22 | 0 | 8.3% | 100% | _(thin)_ |
| cycle:2003 | 22 | 22 | 2 | 20 | 0 | 9.1% | 100% | _(thin)_ |
| cycle:2004 | 28 | 28 | 8 | 20 | 0 | 28.6% | 100% | _(thin)_ |
| cycle:2005 | 22 | 22 | 2 | 20 | 0 | 9.1% | 100% | _(thin)_ |
| cycle:2006 | 65 | 65 | 7 | 58 | 0 | 10.8% | 100% |  |
| cycle:2007 | 75 | 75 | 0 | 75 | 0 | 0.0% | 100% |  |
| cycle:2008 | 128 | 128 | 4 | 124 | 0 | 3.1% | 100% |  |
| cycle:2009 | 71 | 71 | 0 | 71 | 0 | 0.0% | 100% |  |
| cycle:2010 | 49 | 49 | 1 | 48 | 0 | 2.0% | 100% |  |
| cycle:2011 | 41 | 41 | 0 | 41 | 0 | 0.0% | 100% |  |
| cycle:2012 | 31 | 31 | 1 | 30 | 0 | 3.2% | 100% |  |
| cycle:2013 | 29 | 29 | 0 | 29 | 0 | 0.0% | 100% | _(thin)_ |
| cycle:2014 | 54 | 54 | 0 | 54 | 0 | 0.0% | 100% |  |
| cycle:2015 | 56 | 56 | 0 | 56 | 0 | 0.0% | 100% |  |
| cycle:2016 | 51 | 51 | 1 | 50 | 0 | 2.0% | 100% |  |
| cycle:2017 | 18 | 18 | 1 | 17 | 0 | 5.6% | 100% | _(thin)_ |
| cycle:2018 | 2 | 2 | 1 | 1 | 0 | 50.0% | 100% | _(thin)_ |
| cycle:2020 | 4 | 3 | 0 | 3 | 1 | 0.0% | 75% | _(thin)_ |
| cycle:2021 | 9 | 8 | 1 | 7 | 1 | 12.5% | 89% | _(thin)_ |
| cycle:2022 | 18 | 13 | 0 | 13 | 5 | 0.0% | 72% | _(thin)_ |
| cycle:2023 | 29 | 14 | 3 | 11 | 15 | 21.4% | 48% | _(immature, thin)_ |
| cycle:2024 | 22 | 1 | 0 | 1 | 21 | 0.0% | 5% | _(immature, thin)_ |
| cycle:2025 | 41 | 0 | 0 | 0 | 41 | 0.0% | 0% | _(immature, thin)_ |

### NYISO

| Cycle | Total | Decided | Operational | Withdrawn | Active | Completion | Decided-share | |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| cycle:1998 | 4 | 4 | 4 | 0 | 0 | 100.0% | 100% | _(thin)_ |
| cycle:1999 | 34 | 34 | 10 | 24 | 0 | 29.4% | 100% |  |
| cycle:2000 | 59 | 59 | 18 | 41 | 0 | 30.5% | 100% |  |
| cycle:2001 | 23 | 23 | 4 | 19 | 0 | 17.4% | 100% | _(thin)_ |
| cycle:2002 | 20 | 20 | 7 | 13 | 0 | 35.0% | 100% | _(thin)_ |
| cycle:2003 | 17 | 17 | 10 | 7 | 0 | 58.8% | 100% | _(thin)_ |
| cycle:2004 | 23 | 23 | 13 | 10 | 0 | 56.5% | 100% | _(thin)_ |
| cycle:2005 | 53 | 53 | 20 | 33 | 0 | 37.7% | 100% |  |
| cycle:2006 | 41 | 41 | 16 | 25 | 0 | 39.0% | 100% |  |
| cycle:2007 | 41 | 41 | 11 | 30 | 0 | 26.8% | 100% |  |
| cycle:2008 | 40 | 39 | 6 | 33 | 1 | 15.4% | 98% |  |
| cycle:2009 | 25 | 25 | 6 | 19 | 0 | 24.0% | 100% | _(thin)_ |
| cycle:2010 | 9 | 9 | 4 | 5 | 0 | 44.4% | 100% | _(thin)_ |
| cycle:2011 | 9 | 9 | 0 | 9 | 0 | 0.0% | 100% | _(thin)_ |
| cycle:2012 | 22 | 22 | 12 | 10 | 0 | 54.5% | 100% | _(thin)_ |
| cycle:2013 | 10 | 10 | 6 | 4 | 0 | 60.0% | 100% | _(thin)_ |
| cycle:2014 | 40 | 40 | 10 | 30 | 0 | 25.0% | 100% |  |
| cycle:2015 | 45 | 41 | 8 | 33 | 4 | 19.5% | 91% |  |
| cycle:2016 | 48 | 35 | 10 | 25 | 13 | 28.6% | 73% |  |
| cycle:2017 | 79 | 73 | 12 | 61 | 6 | 16.4% | 92% |  |
| cycle:2018 | 117 | 102 | 28 | 74 | 15 | 27.5% | 87% |  |
| cycle:2019 | 166 | 135 | 0 | 135 | 31 | 0.0% | 81% |  |
| cycle:2020 | 148 | 129 | 0 | 129 | 19 | 0.0% | 87% |  |
| cycle:2021 | 160 | 149 | 0 | 149 | 11 | 0.0% | 93% |  |
| cycle:2022 | 166 | 165 | 0 | 165 | 1 | 0.0% | 99% |  |
| cycle:2023 | 138 | 138 | 0 | 138 | 0 | 0.0% | 100% |  |
| cycle:2024 | 383 | 294 | 0 | 294 | 89 | 0.0% | 77% |  |
| cycle:2025 | 16 | 16 | 0 | 16 | 0 | 0.0% | 100% | _(thin)_ |

### SOUTHEAST

| Cycle | Total | Decided | Operational | Withdrawn | Active | Completion | Decided-share | |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| cluster:CLUSTER-2023 | 19 | 0 | 0 | 0 | 19 | 0.0% | 0% | _(immature, thin)_ |
| cluster:CLUSTER-2024 | 26 | 7 | 0 | 7 | 19 | 0.0% | 27% | _(immature, thin)_ |
| cluster:CLUSTER-2025 | 46 | 0 | 0 | 0 | 46 | 0.0% | 0% | _(immature, thin)_ |
| cluster:CS-2025 | 12 | 0 | 0 | 0 | 12 | 0.0% | 0% | _(immature, thin)_ |
| cluster:DEC-2022 | 7 | 6 | 0 | 6 | 1 | 0.0% | 86% | _(thin)_ |
| cluster:DISIS-2022 | 92 | 66 | 0 | 66 | 26 | 0.0% | 72% |  |
| cluster:DISIS-2023 | 51 | 31 | 0 | 31 | 20 | 0.0% | 61% |  |
| cluster:DISIS-2024 | 93 | 36 | 0 | 36 | 57 | 0.0% | 39% | _(immature)_ |
| cluster:DISIS-2025 | 64 | 9 | 0 | 9 | 55 | 0.0% | 14% | _(immature, thin)_ |
| cluster:SOLAR-2023 | 77 | 65 | 0 | 65 | 12 | 0.0% | 84% |  |
| cluster:SOLAR-2024 | 47 | 36 | 0 | 36 | 11 | 0.0% | 77% |  |
| cluster:TCS-2024 | 7 | 0 | 0 | 0 | 7 | 0.0% | 0% | _(immature, thin)_ |
| cluster:TRANS-2022 | 1 | 0 | 0 | 0 | 1 | 0.0% | 0% | _(immature, thin)_ |
| cycle:(unknown) | 330 | 295 | 83 | 212 | 35 | 28.1% | 89% |  |
| cycle:1997 | 6 | 6 | 6 | 0 | 0 | 100.0% | 100% | _(thin)_ |
| cycle:1998 | 42 | 42 | 28 | 14 | 0 | 66.7% | 100% |  |
| cycle:1999 | 63 | 62 | 24 | 38 | 1 | 38.7% | 98% |  |
| cycle:2000 | 71 | 71 | 6 | 65 | 0 | 8.5% | 100% |  |
| cycle:2001 | 69 | 69 | 21 | 48 | 0 | 30.4% | 100% |  |
| cycle:2002 | 17 | 17 | 3 | 14 | 0 | 17.6% | 100% | _(thin)_ |
| cycle:2003 | 19 | 19 | 3 | 16 | 0 | 15.8% | 100% | _(thin)_ |
| cycle:2004 | 8 | 8 | 1 | 7 | 0 | 12.5% | 100% | _(thin)_ |
| cycle:2005 | 17 | 17 | 8 | 9 | 0 | 47.1% | 100% | _(thin)_ |
| cycle:2006 | 15 | 15 | 6 | 9 | 0 | 40.0% | 100% | _(thin)_ |
| cycle:2007 | 47 | 45 | 9 | 36 | 2 | 20.0% | 96% |  |
| cycle:2008 | 35 | 35 | 1 | 34 | 0 | 2.9% | 100% |  |
| cycle:2009 | 24 | 18 | 4 | 14 | 6 | 22.2% | 75% | _(thin)_ |
| cycle:2010 | 23 | 22 | 4 | 18 | 1 | 18.2% | 96% | _(thin)_ |
| cycle:2011 | 38 | 36 | 4 | 32 | 2 | 11.1% | 95% |  |
| cycle:2012 | 44 | 43 | 7 | 36 | 1 | 16.3% | 98% |  |
| cycle:2013 | 70 | 69 | 7 | 62 | 1 | 10.1% | 99% |  |
| cycle:2014 | 91 | 86 | 10 | 76 | 5 | 11.6% | 95% |  |
| cycle:2015 | 59 | 56 | 7 | 49 | 3 | 12.5% | 95% |  |
| cycle:2016 | 256 | 245 | 33 | 212 | 11 | 13.5% | 96% |  |
| cycle:2017 | 318 | 290 | 82 | 208 | 28 | 28.3% | 91% |  |
| cycle:2018 | 309 | 288 | 40 | 248 | 21 | 13.9% | 93% |  |
| cycle:2019 | 270 | 234 | 35 | 199 | 36 | 15.0% | 87% |  |
| cycle:2020 | 270 | 215 | 37 | 178 | 55 | 17.2% | 80% |  |
| cycle:2021 | 191 | 128 | 5 | 123 | 63 | 3.9% | 67% |  |
| cycle:2022 | 260 | 146 | 7 | 139 | 114 | 4.8% | 56% |  |
| cycle:2023 | 438 | 281 | 46 | 235 | 157 | 16.4% | 64% |  |
| cycle:2024 | 206 | 118 | 2 | 116 | 88 | 1.7% | 57% |  |
| cycle:2025 | 186 | 35 | 0 | 35 | 151 | 0.0% | 19% | _(immature)_ |

### WEST

| Cycle | Total | Decided | Operational | Withdrawn | Active | Completion | Decided-share | |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| cluster:CLUSTER-2023 | 13 | 9 | 0 | 9 | 4 | 0.0% | 69% | _(thin)_ |
| cluster:CLUSTER-2024 | 15 | 10 | 0 | 10 | 5 | 0.0% | 67% | _(thin)_ |
| cluster:CLUSTER-2025 | 35 | 13 | 0 | 13 | 22 | 0.0% | 37% | _(immature, thin)_ |
| cluster:DISIS-2020 | 12 | 8 | 0 | 8 | 4 | 0.0% | 67% | _(thin)_ |
| cluster:DISIS-2021 | 26 | 22 | 0 | 22 | 4 | 0.0% | 85% | _(thin)_ |
| cluster:DISIS-2022 | 13 | 12 | 0 | 12 | 1 | 0.0% | 92% | _(thin)_ |
| cluster:DISIS-2023 | 18 | 17 | 0 | 17 | 1 | 0.0% | 94% | _(thin)_ |
| cluster:DISIS-2024 | 20 | 0 | 0 | 0 | 20 | 0.0% | 0% | _(immature, thin)_ |
| cluster:DISIS-2025 | 12 | 1 | 0 | 1 | 11 | 0.0% | 8% | _(immature, thin)_ |
| cluster:GI-2011 | 1 | 0 | 0 | 0 | 1 | 0.0% | 0% | _(immature, thin)_ |
| cluster:GI-2014 | 1 | 1 | 0 | 1 | 0 | 0.0% | 100% | _(thin)_ |
| cluster:GI-2025 | 29 | 5 | 0 | 5 | 24 | 0.0% | 17% | _(immature, thin)_ |
| cluster:RSC-2020 | 5 | 3 | 0 | 3 | 2 | 0.0% | 60% | _(thin)_ |
| cluster:RSC-2023 | 3 | 0 | 0 | 0 | 3 | 0.0% | 0% | _(immature, thin)_ |
| cluster:RSC-2024 | 21 | 1 | 0 | 1 | 20 | 0.0% | 5% | _(immature, thin)_ |
| cluster:RSC-2025 | 3 | 1 | 0 | 1 | 2 | 0.0% | 33% | _(immature, thin)_ |
| cluster:SURPLUS-2025 | 6 | 2 | 0 | 2 | 4 | 0.0% | 33% | _(immature, thin)_ |
| cluster:TC-2024 | 26 | 6 | 0 | 6 | 20 | 0.0% | 23% | _(immature, thin)_ |
| cluster:TRANSITION-2022 | 17 | 15 | 0 | 15 | 2 | 0.0% | 88% | _(thin)_ |
| cluster:TRANSITIONAL-2024 | 4 | 0 | 0 | 0 | 4 | 0.0% | 0% | _(immature, thin)_ |
| cycle:(unknown) | 106 | 96 | 86 | 10 | 10 | 89.6% | 91% |  |
| cycle:2000 | 22 | 22 | 7 | 15 | 0 | 31.8% | 100% | _(thin)_ |
| cycle:2001 | 196 | 194 | 27 | 167 | 2 | 13.9% | 99% |  |
| cycle:2002 | 63 | 63 | 17 | 46 | 0 | 27.0% | 100% |  |
| cycle:2003 | 77 | 75 | 15 | 60 | 2 | 20.0% | 97% |  |
| cycle:2004 | 69 | 67 | 13 | 54 | 2 | 19.4% | 97% |  |
| cycle:2005 | 116 | 114 | 38 | 76 | 2 | 33.3% | 98% |  |
| cycle:2006 | 157 | 150 | 37 | 113 | 7 | 24.7% | 96% |  |
| cycle:2007 | 273 | 252 | 62 | 190 | 21 | 24.6% | 92% |  |
| cycle:2008 | 335 | 328 | 28 | 300 | 7 | 8.5% | 98% |  |
| cycle:2009 | 283 | 268 | 46 | 222 | 15 | 17.2% | 95% |  |
| cycle:2010 | 365 | 357 | 55 | 302 | 8 | 15.4% | 98% |  |
| cycle:2011 | 211 | 200 | 43 | 157 | 11 | 21.5% | 95% |  |
| cycle:2012 | 158 | 144 | 49 | 95 | 14 | 34.0% | 91% |  |
| cycle:2013 | 195 | 189 | 53 | 136 | 6 | 28.0% | 97% |  |
| cycle:2014 | 232 | 216 | 65 | 151 | 16 | 30.1% | 93% |  |
| cycle:2015 | 279 | 258 | 61 | 197 | 21 | 23.6% | 92% |  |
| cycle:2016 | 345 | 303 | 48 | 255 | 42 | 15.8% | 88% |  |
| cycle:2017 | 408 | 348 | 46 | 302 | 60 | 13.2% | 85% |  |
| cycle:2018 | 420 | 353 | 51 | 302 | 67 | 14.4% | 84% |  |
| cycle:2019 | 353 | 281 | 39 | 242 | 72 | 13.9% | 80% |  |
| cycle:2020 | 287 | 193 | 23 | 170 | 94 | 11.9% | 67% |  |
| cycle:2021 | 568 | 345 | 31 | 314 | 223 | 9.0% | 61% |  |
| cycle:2022 | 807 | 492 | 10 | 482 | 315 | 2.0% | 61% |  |
| cycle:2023 | 817 | 525 | 9 | 516 | 292 | 1.7% | 64% |  |
| cycle:2024 | 356 | 224 | 0 | 224 | 132 | 0.0% | 63% |  |
| cycle:2025 | 319 | 57 | 4 | 53 | 262 | 7.0% | 18% | _(immature)_ |

### ISO_NE

| Cycle | Total | Decided | Operational | Withdrawn | Active | Completion | Decided-share | |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| cycle:2000 | 3 | 3 | 1 | 2 | 0 | 33.3% | 100% | _(thin)_ |
| cycle:2001 | 3 | 3 | 2 | 1 | 0 | 66.7% | 100% | _(thin)_ |
| cycle:2002 | 2 | 2 | 2 | 0 | 0 | 100.0% | 100% | _(thin)_ |
| cycle:2003 | 12 | 12 | 7 | 5 | 0 | 58.3% | 100% | _(thin)_ |
| cycle:2004 | 5 | 5 | 4 | 1 | 0 | 80.0% | 100% | _(thin)_ |
| cycle:2005 | 14 | 14 | 3 | 11 | 0 | 21.4% | 100% | _(thin)_ |
| cycle:2006 | 46 | 46 | 15 | 31 | 0 | 32.6% | 100% |  |
| cycle:2007 | 47 | 47 | 14 | 33 | 0 | 29.8% | 100% |  |
| cycle:2008 | 42 | 42 | 12 | 30 | 0 | 28.6% | 100% |  |
| cycle:2009 | 31 | 31 | 12 | 19 | 0 | 38.7% | 100% |  |
| cycle:2010 | 27 | 27 | 15 | 12 | 0 | 55.6% | 100% | _(thin)_ |
| cycle:2011 | 22 | 22 | 8 | 14 | 0 | 36.4% | 100% | _(thin)_ |
| cycle:2012 | 19 | 18 | 8 | 10 | 1 | 44.4% | 95% | _(thin)_ |
| cycle:2013 | 16 | 16 | 7 | 9 | 0 | 43.8% | 100% | _(thin)_ |
| cycle:2014 | 39 | 39 | 11 | 28 | 0 | 28.2% | 100% |  |
| cycle:2015 | 63 | 62 | 16 | 46 | 1 | 25.8% | 98% |  |
| cycle:2016 | 31 | 29 | 7 | 22 | 2 | 24.1% | 94% | _(thin)_ |
| cycle:2017 | 54 | 51 | 9 | 42 | 3 | 17.6% | 94% |  |
| cycle:2018 | 117 | 112 | 28 | 84 | 5 | 25.0% | 96% |  |
| cycle:2019 | 99 | 92 | 23 | 69 | 7 | 25.0% | 93% |  |
| cycle:2020 | 135 | 131 | 18 | 113 | 4 | 13.7% | 97% |  |
| cycle:2021 | 110 | 90 | 5 | 85 | 20 | 5.6% | 82% |  |
| cycle:2022 | 107 | 99 | 1 | 98 | 8 | 1.0% | 93% |  |
| cycle:2023 | 125 | 119 | 0 | 119 | 6 | 0.0% | 95% |  |
| cycle:2024 | 112 | 97 | 0 | 97 | 15 | 0.0% | 87% |  |
| cycle:2025 | 1 | 1 | 0 | 1 | 0 | 0.0% | 100% | _(thin)_ |

## Reading for the harmonization discussion

- The two regions run structurally different study processes and the outcome gap is large and measured, not modeled.
- The dominant cause of withdrawal in both regions is *not reaching IA execution* — every study-phase exit is effectively terminal. Harmonization that compresses the study→IA path attacks the gap directly.
- This is the same OPTIMUS factorization used across the repo: the milestone is the discovered intermediate through which `proposed → operational` factors with higher confidence than the direct rate.

## Definitions (so the numbers are unambiguous)

- **Completion** uses LBNL's published definition: operational ÷ all requests submitted 2000–2020 (LBNL *Queued Up* sheet 25). These counts reproduce LBNL's own table exactly.
- **Built after signing** = operational ÷ (operational + withdrawn) among projects with an executed-IA date (LBNL sheet 27 method). It counts projects that signed and then withdrew.
- The **milestone funnel, durations, and study-cycle** panels below use all submission years and project counts, for breadth; they are descriptive, not the headline comparison.

_Honesty: rates over decided projects (active/suspended censored); durations survivor-conditioned; thin/immature cohorts flagged; descriptive mediation, not a causal model._
