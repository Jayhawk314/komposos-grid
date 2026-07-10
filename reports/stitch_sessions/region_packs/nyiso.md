# NYISO — STITCH Regional Study Process Engagement Pack

> 📏 **Measured** — every figure derives from the LBNL *Queued Up* data file (through 2026); headline counts reconcile to the published tables. Regenerate with `python -m domains.grid.run_region_packs`.

## Headline queue metrics

| Metric | Value |
|---|---:|
| Total interconnection requests (all-time) | 1,936 |
| Decided (built or withdrawn) | 1,746 |
| Operational (built) | 215 |
| Active in queue today | 190 |
| LBNL completion rate (2000-2020 requests, LBNL definition) | **19.4%** (201 of 1,035) |
| Post-IA completion (built after signing IA) | **70.0%** (35 of 50) |

## Where the region sits on the IA-certainty spectrum

The June 23 session's core finding: an executed IA is an ~80% completion promise in ERCOT but roughly a coin-flip (~35%) in MISO. This region's post-IA rate of **70.0%** places it on that spectrum — a talking point the presenters can react to directly.

## Pipeline durations (successful projects, medians)

| Stage | Duration |
|---|---|
| Request → IA (study phase) | 41.2 mo (IQR 31.3–49.1, n=109) |
| IA → COD (construction) | 20.4 mo (IQR 10.7–31.0, n=26) |
| Request → COD (end-to-end) | 55.3 mo (IQR 40.8–75.3, n=83) |

## Milestone funnel (decided 2000–2020 cohort)

| Milestone reached | Decided | Built | Completion |
|---|---:|---:|---:|
| ia_executed | 215 | 215 | 100.0% |
| (unlabeled) | 1,531 | 0 | 0.0% |

## Recent study cycles / entry cohorts

| Cycle | Total | Built | Withdrawn | Active | Completion |
|---|---:|---:|---:|---:|---:|
| 2015 | 45 | 8 | 33 | 4 | 20% |
| 2016 | 48 | 10 | 25 | 13 | 29% |
| 2017 | 79 | 12 | 61 | 6 | 16% |
| 2018 | 117 | 28 | 74 | 15 | 27% |
| 2019 | 166 | 0 | 135 | 31 | 0% |
| 2020 | 148 | 0 | 129 | 19 | 0% |
| 2021 | 160 | 0 | 149 | 11 | 0% |
| 2022 | 166 | 0 | 165 | 1 | 0% |
| 2023 | 138 | 0 | 138 | 0 | 0% |
| 2024 | 383 | 0 | 294 | 89 | 0% |

## Active queue by fuel (GW)

| Fuel | GW |
|---|---:|
| battery | 11.1 |
| solar | 6.6 |
| offshore + wind | 4.4 |
| wind | 2.9 |
| solar + battery | 2.1 |

## Session prep notes *(fill in when presenters are confirmed)*

- **Presenters:** _TBD — check the ESIG events page for this session_
- **Their live question:** _what reform / process pain is this region actively debating?_
- **Claims to listen for:** _numbers stated on the panel → run each through `/verify-claim`_
- **Bridge phrase:** _one sentence connecting this pack's post-IA rate to their process design_
