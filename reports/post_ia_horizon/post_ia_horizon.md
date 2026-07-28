# Post-IA completion — minimum-follow-up sensitivity check

Source: **LBNL_Ix_Queue_Data_File_thru2026.xlsx** · vintage cutoff: **2025-12-31** · horizons: 24mo, 36mo, 60mo · min_cohort: **30**

For each region, the signed cohort is every project with an executed-IA date. At each horizon H (2, 3, 5 years), the MATURE subset is signed projects at least H months old as of the fixed vintage cutoff -- i.e. old enough to have had a fair chance to resolve by H, regardless of whether they actually did. Within that mature subset, the rate is operational / (operational + withdrawn) using CURRENT status, same definition as the raw post-IA rate, just restricted to older-than-H signings. Still-active and suspended projects within the mature cohort are reported as 'censored' -- old enough to expect resolution, not yet resolved -- and are never counted as failures or dropped from the report. This does not pin exactly WHEN within the horizon an outcome occurred (see module docstring on wd_date coverage). This is a minimum-follow-up sensitivity check, not age matching: it applies the same age floor to each region, but their remaining age distributions can still differ.

## Headline: does the MISO/ERCOT gap survive minimum-follow-up cutoffs?

| Cohort | MISO rate (n decided) | ERCOT rate (n decided) | Gap (ERCOT − MISO) |
|---|---:|---:|---:|
| raw (unadjusted) | 34.9% (1,365) | 79.7% (610) | +44.8 pp |
| 2-year | 34.9% (1,359) | 80.2% (581) | +45.3 pp |
| 3-year | 34.8% (1,346) | 79.9% (546) | +45.0 pp |
| 5-year | 34.0% (1,302) | 77.5% (418) | +43.5 pp |

## IA-cohort age — why this sensitivity check matters

Median months since IA execution (as of the vintage cutoff), among signed projects. A region whose signed cohort is younger has had less time for outcomes to resolve; this is the raw-rate bias the minimum-follow-up check above probes.

| Region | n signed | Median age (mo) | p25 | p75 |
|---|---:|---:|---:|---:|
| **CAISO** | 445 | 59.5 | 21.9 | 143.2 |
| **ERCOT** | 1,207 | 44.3 | 18.1 | 89.5 |
| **ISO_NE** | 170 | 66.6 | 35.2 | 116.6 |
| **MISO** | 1,760 | 164.4 | 69.9 | 209.0 |
| **NYISO** | 109 | 58.7 | 39.5 | 69.5 |
| **PJM** | 247 | 106.3 | 68.4 | 187.6 |
| **SOUTHEAST** | 167 | 95.9 | 81.9 | 129.5 |
| **SPP** | 0 | — | — | — |
| **WEST** | 728 | 121.0 | 69.3 | 186.9 |

## Full breakdown by region and horizon

`decided` = operational + withdrawn among the mature cohort; `censored` = still active/suspended despite being old enough to expect resolution -- reported, not dropped. `Δ raw` = horizon rate minus the unadjusted raw post-IA rate.

### CAISO — raw rate 90.7% (196/216)

| Horizon | Mature | Operational | Withdrawn | Censored | Decided | Rate | Δ raw | Classification |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2y | 327 | 186 | 20 | 121 | 206 | 90.3% | -0.4 pp | complete |
| 3y | 291 | 176 | 16 | 99 | 192 | 91.7% | +0.9 pp | complete |
| 5y | 221 | 152 | 15 | 54 | 167 | 91.0% | +0.3 pp | complete |

### ERCOT — raw rate 79.7% (486/610)

| Horizon | Mature | Operational | Withdrawn | Censored | Decided | Rate | Δ raw | Classification |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2y | 829 | 466 | 115 | 248 | 581 | 80.2% | +0.5 pp | complete |
| 3y | 681 | 436 | 110 | 135 | 546 | 79.9% | +0.2 pp | complete |
| 5y | 482 | 324 | 94 | 64 | 418 | 77.5% | -2.2 pp | complete |

### ISO_NE — raw rate 75.2% (97/129)

| Horizon | Mature | Operational | Withdrawn | Censored | Decided | Rate | Δ raw | Classification |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2y | 141 | 95 | 30 | 16 | 125 | 76.0% | +0.8 pp | complete |
| 3y | 122 | 84 | 30 | 8 | 114 | 73.7% | -1.5 pp | complete |
| 5y | 98 | 70 | 23 | 5 | 93 | 75.3% | +0.1 pp | complete |

### MISO — raw rate 34.9% (476/1,365)

| Horizon | Mature | Operational | Withdrawn | Censored | Decided | Rate | Δ raw | Classification |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2y | 1,592 | 474 | 885 | 233 | 1,359 | 34.9% | +0.0 pp | complete |
| 3y | 1,516 | 469 | 877 | 170 | 1,346 | 34.8% | -0.0 pp | complete |
| 5y | 1,368 | 443 | 859 | 66 | 1,302 | 34.0% | -0.8 pp | complete |

### NYISO — raw rate 70.0% (35/50)

| Horizon | Mature | Operational | Withdrawn | Censored | Decided | Rate | Δ raw | Classification |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2y | 109 | 35 | 15 | 59 | 50 | 70.0% | +0.0 pp | complete |
| 3y | 86 | 33 | 12 | 41 | 45 | 73.3% | +3.3 pp | complete |
| 5y | 43 | 24 | 8 | 11 | 32 | 75.0% | +5.0 pp | complete |

### PJM — raw rate 85.9% (195/227)

| Horizon | Mature | Operational | Withdrawn | Censored | Decided | Rate | Δ raw | Classification |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2y | 247 | 195 | 32 | 20 | 227 | 85.9% | +0.0 pp | complete |
| 3y | 247 | 195 | 32 | 20 | 227 | 85.9% | +0.0 pp | complete |
| 5y | 202 | 175 | 17 | 10 | 192 | 91.1% | +5.2 pp | complete |

### SOUTHEAST — raw rate 55.4% (92/166)

| Horizon | Mature | Operational | Withdrawn | Censored | Decided | Rate | Δ raw | Classification |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2y | 167 | 92 | 74 | 1 | 166 | 55.4% | +0.0 pp | complete |
| 3y | 166 | 91 | 74 | 1 | 165 | 55.2% | -0.3 pp | complete |
| 5y | 153 | 81 | 71 | 1 | 152 | 53.3% | -2.1 pp | complete |

### SPP — raw rate not computable (n=0) (0/0)

| Horizon | Mature | Operational | Withdrawn | Censored | Decided | Rate | Δ raw | Classification |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2y | 0 | 0 | 0 | 0 | 0 | — (n=0) | — | absent |
| 3y | 0 | 0 | 0 | 0 | 0 | — (n=0) | — | absent |
| 5y | 0 | 0 | 0 | 0 | 0 | — (n=0) | — | absent |

### WEST — raw rate 71.9% (440/612)

| Horizon | Mature | Operational | Withdrawn | Censored | Decided | Rate | Δ raw | Classification |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2y | 705 | 432 | 170 | 103 | 602 | 71.8% | -0.1 pp | complete |
| 3y | 645 | 423 | 166 | 56 | 589 | 71.8% | -0.1 pp | complete |
| 5y | 584 | 392 | 152 | 40 | 544 | 72.1% | +0.2 pp | complete |

_Scope: region level only, same 9 regions as the coverage audit. Not a survival/Kaplan-Meier estimate and not matched-age cohorts -- a minimum-follow-up filter on current status; see the method note above for what the check does and does not establish._
