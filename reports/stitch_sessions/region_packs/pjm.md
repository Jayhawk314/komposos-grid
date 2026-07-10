# PJM — STITCH Regional Study Process Engagement Pack

> 📏 **Measured** — every figure derives from the LBNL *Queued Up* data file (through 2026); headline counts reconcile to the published tables. Regenerate with `python -m domains.grid.run_region_packs`.

## Headline queue metrics

| Metric | Value |
|---|---:|
| Total interconnection requests (all-time) | 7,666 |
| Decided (built or withdrawn) | 6,418 |
| Operational (built) | 1,192 |
| Active in queue today | 1,248 |
| LBNL completion rate (2000-2020 requests, LBNL definition) | **20.5%** (1,145 of 5,589) |
| Post-IA completion (built after signing IA) | **85.9%** (195 of 227) |

## Where the region sits on the IA-certainty spectrum

The June 23 session's core finding: an executed IA is an ~80% completion promise in ERCOT but roughly a coin-flip (~35%) in MISO. This region's post-IA rate of **85.9%** places it on that spectrum — a talking point the presenters can react to directly.

## Pipeline durations (successful projects, medians)

| Stage | Duration |
|---|---|
| Request → IA (study phase) | 35.5 mo (IQR 22.0–49.4, n=247) |
| IA → COD (construction) | 22.8 mo (IQR 9.7–36.4, n=172) |
| Request → COD (end-to-end) | 37.9 mo (IQR 19.5–62.0, n=1,195) |

## Milestone funnel (decided 2000–2020 cohort)

| Milestone reached | Decided | Built | Completion |
|---|---:|---:|---:|
| ia_executed | 2,166 | 1,192 | 55.0% |
| feasibility_study | 2,499 | 0 | 0.0% |
| system_impact_study | 1,505 | 0 | 0.0% |
| in_progress_unknown_study | 193 | 0 | 0.0% |
| facility_study ⚠ thin cohort | 26 | 0 | 0.0% |
| ia_pending ⚠ thin cohort | 14 | 0 | 0.0% |
| withdrawn ⚠ thin cohort | 8 | 0 | 0.0% |
| (unlabeled) ⚠ thin cohort | 7 | 0 | 0.0% |

## Recent study cycles / entry cohorts

| Cycle | Total | Built | Withdrawn | Active | Completion |
|---|---:|---:|---:|---:|---:|
| 2014 | 187 | 60 | 126 | 1 | 32% |
| 2015 | 305 | 67 | 231 | 7 | 22% |
| 2016 | 389 | 108 | 250 | 31 | 30% |
| 2017 | 352 | 72 | 236 | 44 | 23% |
| 2018 | 435 | 56 | 311 | 68 | 15% |
| 2019 | 667 | 75 | 409 | 183 | 15% |
| 2020 | 926 | 29 | 719 | 178 | 4% |
| 2021 | 868 | 0 | 819 | 49 | 0% |
| 2022 *(immature)* | 483 | 0 | 182 | 301 | 0% |
| 2025 *(immature)* | 388 | 0 | 160 | 228 | 0% |

## Active queue by fuel (GW)

| Fuel | GW |
|---|---:|
| solar | 59.8 |
| battery | 29.6 |
| gas | 14.0 |
| solar + battery | 13.8 |
| offshore + wind | 13.5 |
| wind | 7.9 |

## Session prep notes *(fill in when presenters are confirmed)*

- **Presenters:** _TBD — check the ESIG events page for this session_
- **Their live question:** _what reform / process pain is this region actively debating?_
- **Claims to listen for:** _numbers stated on the panel → run each through `/verify-claim`_
- **Bridge phrase:** _one sentence connecting this pack's post-IA rate to their process design_
