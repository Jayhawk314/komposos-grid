# CAISO — STITCH Regional Study Process Engagement Pack

> 📏 **LBNL Completion — measured.** Reconciles to *Queued Up* 2026 Edition (data through year-end 2025) Sheet 25 to the integer, denominators included.
>
> 🧮 **Everything else — derived (our computation).** Post-IA completion, durations and cohort panels apply LBNL's methods to slices LBNL does not publish: Sheet 27 gives post-IA at national level only, and there is no published regional duration split. Accurate, but ours to defend — not LBNL-published figures.
>
> Regenerate with `python -m domains.grid.run_region_packs`.

## Headline queue metrics

| Metric | Value |
|---|---:|
| Total interconnection requests (all-time) | 2,868 |
| Decided (built or withdrawn) | 2,435 |
| Operational (built) | 235 |
| Active in queue today | 433 |
| LBNL completion rate (2000-2020 requests, LBNL definition) | **12.1%** (232 of 1,910) |
| Post-IA completion (built after signing IA) | **90.7%** (196 of 216) |

## Where the region sits on the IA-certainty spectrum

The June 23 session's core finding: an executed IA is an ~80% completion promise in ERCOT but roughly a coin-flip (~35%) in MISO. This region's post-IA rate of **90.7%** places it on that spectrum — a talking point the presenters can react to directly.

## Pipeline durations (successful projects, medians)

| Stage | Duration |
|---|---|
| Request → IA (study phase) | 44.4 mo (IQR 31.1–58.6, n=445) |
| IA → COD (construction) | 28.6 mo (IQR 16.5–48.6, n=193) |
| Request → COD (end-to-end) | 70.5 mo (IQR 51.5–95.7, n=248) |

## Milestone funnel (decided 2000–2020 cohort)

| Milestone reached | Decided | Built | Completion |
|---|---:|---:|---:|
| ia_executed | 289 | 235 | 81.3% |
| system_impact_study | 1,354 | 0 | 0.0% |
| in_progress_unknown_study | 328 | 0 | 0.0% |
| feasibility_study | 269 | 0 | 0.0% |
| not_started | 179 | 0 | 0.0% |
| (unlabeled) ⚠ thin cohort | 10 | 0 | 0.0% |
| withdrawn ⚠ thin cohort | 6 | 0 | 0.0% |

## Recent study cycles / entry cohorts

| Cycle | Total | Built | Withdrawn | Active | Completion |
|---|---:|---:|---:|---:|---:|
| 2013 | 61 | 10 | 48 | 3 | 17% |
| 2014 | 89 | 10 | 70 | 9 | 12% |
| 2015 | 126 | 20 | 91 | 15 | 18% |
| 2016 | 126 | 17 | 96 | 13 | 15% |
| 2017 | 91 | 9 | 65 | 17 | 12% |
| 2018 | 98 | 8 | 67 | 23 | 11% |
| 2019 | 139 | 5 | 97 | 37 | 5% |
| 2020 | 153 | 4 | 107 | 42 | 4% |
| 2021 | 361 | 2 | 220 | 139 | 1% |
| 2023 | 594 | 0 | 486 | 108 | 0% |

## Active queue by fuel (GW)

| Fuel | GW |
|---|---:|
| solar + battery | 62.1 |
| battery | 47.6 |
| solar | 6.4 |
| wind + battery | 3.0 |
| wind | 2.9 |
| gas + battery | 1.6 |

## Session prep notes *(fill in when presenters are confirmed)*

- **Presenters:** _TBD — check the ESIG events page for this session_
- **Their live question:** _what reform / process pain is this region actively debating?_
- **Claims to listen for:** _numbers stated on the panel → run each through `/verify-claim`_
- **Bridge phrase:** _one sentence connecting this pack's post-IA rate to their process design_
