# MISO — STITCH Regional Study Process Engagement Pack

> 📏 **Measured** — every figure derives from the LBNL *Queued Up* data file (2026 Edition, data through year-end 2025); headline counts reconcile to the published tables. Regenerate with `python -m domains.grid.run_region_packs`.

## Headline queue metrics

| Metric | Value |
|---|---:|
| Total interconnection requests (all-time) | 5,424 |
| Decided (built or withdrawn) | 3,778 |
| Operational (built) | 515 |
| Active in queue today | 1,646 |
| LBNL completion rate (2000-2020 requests, LBNL definition) | **18.1%** (509 of 2,806) |
| Post-IA completion (built after signing IA) | **34.9%** (476 of 1,365) |

## Where the region sits on the IA-certainty spectrum

The June 23 session's core finding: an executed IA is an ~80% completion promise in ERCOT but roughly a coin-flip (~35%) in MISO. This region's post-IA rate of **34.9%** places it on that spectrum — a talking point the presenters can react to directly.

## Pipeline durations (successful projects, medians)

| Stage | Duration |
|---|---|
| Request → IA (study phase) | 29.8 mo (IQR 14.9–43.0, n=1,760) |
| IA → COD (construction) | 18.8 mo (IQR 10.2–33.4, n=338) |
| Request → COD (end-to-end) | 39.1 mo (IQR 22.3–57.0, n=539) |

## Milestone funnel (decided 2000–2020 cohort)

| Milestone reached | Decided | Built | Completion |
|---|---:|---:|---:|
| ia_executed | 1,723 | 515 | 29.9% |
| cluster_study | 696 | 0 | 0.0% |
| in_progress_unknown_study | 417 | 0 | 0.0% |
| (unlabeled) | 388 | 0 | 0.0% |
| ia_pending | 286 | 0 | 0.0% |
| feasibility_study | 166 | 0 | 0.0% |
| system_impact_study | 81 | 0 | 0.0% |
| facility_study ⚠ thin cohort | 9 | 0 | 0.0% |
| withdrawn ⚠ thin cohort | 8 | 0 | 0.0% |
| construction ⚠ thin cohort | 4 | 0 | 0.0% |

## Recent study cycles / entry cohorts

| Cycle | Total | Built | Withdrawn | Active | Completion |
|---|---:|---:|---:|---:|---:|
| 2004 | 77 | 25 | 47 | 5 | 35% |
| 2005 | 91 | 36 | 53 | 2 | 40% |
| 2006 | 109 | 21 | 87 | 1 | 19% |
| 2007 | 140 | 17 | 123 | 0 | 12% |
| 2008 | 120 | 6 | 113 | 1 | 5% |
| 2009 | 79 | 1 | 78 | 0 | 1% |
| 2010 | 67 | 4 | 63 | 0 | 6% |
| 2011 | 44 | 1 | 43 | 0 | 2% |
| 2016 | 38 | 1 | 36 | 1 | 3% |
| 2025 *(immature)* | 406 | 0 | 60 | 346 | 0% |

## Active queue by fuel (GW)

| Fuel | GW |
|---|---:|
| solar | 133.2 |
| gas | 65.3 |
| battery | 54.9 |
| wind | 42.7 |
| solar + battery | 28.4 |
| other + battery | 6.1 |

## Session prep notes *(fill in when presenters are confirmed)*

- **Presenters:** _TBD — check the ESIG events page for this session_
- **Their live question:** _what reform / process pain is this region actively debating?_
- **Claims to listen for:** _numbers stated on the panel → run each through `/verify-claim`_
- **Bridge phrase:** _one sentence connecting this pack's post-IA rate to their process design_
