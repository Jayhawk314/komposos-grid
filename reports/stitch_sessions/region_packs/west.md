# West (non-ISO) — STITCH Regional Study Process Engagement Pack

> 📏 **LBNL Completion — measured.** Reconciles to *Queued Up* 2026 Edition (data through year-end 2025) Sheet 25 to the integer, denominators included.
>
> 🧮 **Everything else — derived (our computation).** Post-IA completion, durations and cohort panels apply LBNL's methods to slices LBNL does not publish: Sheet 27 gives post-IA at national level only, and there is no published regional duration split. Accurate, but ours to defend — not LBNL-published figures.
>
> Regenerate with `python -m domains.grid.run_region_packs`.

## Headline queue metrics

| Metric | Value |
|---|---:|
| Total interconnection requests (all-time) | 8,097 |
| Decided (built or withdrawn) | 6,240 |
| Operational (built) | 963 |
| Active in queue today | 1,857 |
| LBNL completion rate (2000-2020 requests, LBNL definition) | **16.9%** (823 of 4,874) |
| Post-IA completion (built after signing IA) | **71.9%** (440 of 612) |

## Where the region sits on the IA-certainty spectrum

The June 23 session's core finding: an executed IA is an ~80% completion promise in ERCOT but roughly a coin-flip (~35%) in MISO. This region's post-IA rate of **71.9%** places it on that spectrum — a talking point the presenters can react to directly.

## Pipeline durations (successful projects, medians)

| Stage | Duration |
|---|---|
| Request → IA (study phase) | 17.5 mo (IQR 11.0–32.4, n=724) |
| IA → COD (construction) | 5.8 mo (IQR 0.0–29.6, n=32) |
| Request → COD (end-to-end) | 25.4 mo (IQR 13.5–52.5, n=183) |

## Milestone funnel (decided 2000–2020 cohort)

| Milestone reached | Decided | Built | Completion |
|---|---:|---:|---:|
| ia_executed | 1,168 | 963 | 82.4% |
| (unlabeled) | 2,487 | 0 | 0.0% |
| withdrawn | 1,800 | 0 | 0.0% |
| in_progress_unknown_study | 328 | 0 | 0.0% |
| facility_study | 173 | 0 | 0.0% |
| system_impact_study | 139 | 0 | 0.0% |
| feasibility_study | 102 | 0 | 0.0% |
| cluster_study ⚠ thin cohort | 29 | 0 | 0.0% |
| suspended ⚠ thin cohort | 13 | 0 | 0.0% |
| not_started ⚠ thin cohort | 1 | 0 | 0.0% |

## Recent study cycles / entry cohorts

| Cycle | Total | Built | Withdrawn | Active | Completion |
|---|---:|---:|---:|---:|---:|
| 2016 | 345 | 48 | 255 | 42 | 16% |
| 2017 | 408 | 46 | 302 | 60 | 13% |
| 2018 | 420 | 51 | 302 | 67 | 14% |
| 2019 | 353 | 39 | 242 | 72 | 14% |
| 2020 | 287 | 23 | 170 | 94 | 12% |
| 2021 | 568 | 31 | 314 | 223 | 9% |
| 2022 | 807 | 10 | 482 | 315 | 2% |
| 2023 | 817 | 9 | 516 | 292 | 2% |
| 2024 | 356 | 0 | 224 | 132 | 0% |
| 2025 *(immature)* | 319 | 4 | 53 | 262 | 7% |

## Active queue by fuel (GW)

| Fuel | GW |
|---|---:|
| solar + battery | 185.6 |
| battery | 76.0 |
| wind | 63.5 |
| solar | 34.1 |
| gas | 25.3 |
| other | 23.5 |

## Session prep notes *(fill in when presenters are confirmed)*

- **Presenters:** _TBD — check the ESIG events page for this session_
- **Their live question:** _what reform / process pain is this region actively debating?_
- **Claims to listen for:** _numbers stated on the panel → run each through `/verify-claim`_
- **Bridge phrase:** _one sentence connecting this pack's post-IA rate to their process design_
