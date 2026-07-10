# ERCOT — STITCH Regional Study Process Engagement Pack

> 📏 **Measured** — every figure derives from the LBNL *Queued Up* data file (through 2026); headline counts reconcile to the published tables. Regenerate with `python -m domains.grid.run_region_packs`.

## Headline queue metrics

| Metric | Value |
|---|---:|
| Total interconnection requests (all-time) | 3,757 |
| Decided (built or withdrawn) | 1,771 |
| Operational (built) | 613 |
| Active in queue today | 1,986 |
| LBNL completion rate (2000-2020 requests, LBNL definition) | **29.6%** (459 of 1,553) |
| Post-IA completion (built after signing IA) | **79.7%** (486 of 610) |

## Where the region sits on the IA-certainty spectrum

The June 23 session's core finding: an executed IA is an ~80% completion promise in ERCOT but roughly a coin-flip (~35%) in MISO. This region's post-IA rate of **79.7%** places it on that spectrum — a talking point the presenters can react to directly.

## Pipeline durations (successful projects, medians)

| Stage | Duration |
|---|---|
| Request → IA (study phase) | 20.3 mo (IQR 12.9–29.4, n=1,174) |
| IA → COD (construction) | 25.9 mo (IQR 18.8–34.2, n=424) |
| Request → COD (end-to-end) | 44.3 mo (IQR 30.2–56.9, n=480) |

## Milestone funnel (decided 2000–2020 cohort)

| Milestone reached | Decided | Built | Completion |
|---|---:|---:|---:|
| ia_executed | 654 | 613 | 93.7% |
| facility_study | 1,008 | 0 | 0.0% |
| ia_pending | 83 | 0 | 0.0% |
| (unlabeled) ⚠ thin cohort | 17 | 0 | 0.0% |
| in_progress_unknown_study ⚠ thin cohort | 9 | 0 | 0.0% |

## Recent study cycles / entry cohorts

| Cycle | Total | Built | Withdrawn | Active | Completion |
|---|---:|---:|---:|---:|---:|
| 2015 | 59 | 18 | 28 | 13 | 39% |
| 2016 | 70 | 19 | 39 | 12 | 33% |
| 2017 | 131 | 40 | 55 | 36 | 42% |
| 2018 | 167 | 45 | 77 | 45 | 37% |
| 2019 | 245 | 64 | 109 | 72 | 37% |
| 2020 | 235 | 60 | 67 | 108 | 47% |
| 2021 *(immature)* | 329 | 45 | 77 | 207 | 37% |
| 2022 *(immature)* | 378 | 17 | 76 | 285 | 18% |
| 2023 *(immature)* | 470 | 29 | 85 | 356 | 25% |
| 2024 *(immature)* | 491 | 5 | 50 | 436 | 9% |

## Active queue by fuel (GW)

| Fuel | GW |
|---|---:|
| battery | 133.4 |
| solar + battery | 112.1 |
| solar | 96.8 |
| wind | 52.5 |
| gas | 45.7 |
| wind + battery | 3.6 |

## Session prep notes *(fill in when presenters are confirmed)*

- **Presenters:** _TBD — check the ESIG events page for this session_
- **Their live question:** _what reform / process pain is this region actively debating?_
- **Claims to listen for:** _numbers stated on the panel → run each through `/verify-claim`_
- **Bridge phrase:** _one sentence connecting this pack's post-IA rate to their process design_
