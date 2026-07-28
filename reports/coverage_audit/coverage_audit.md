# LBNL Queued Up — milestone-field coverage audit

Source: **LBNL_Ix_Queue_Data_File_thru2026.xlsx** · generator: `domains.grid.run_coverage_audit` · min_cohort: **30**

For every region and status this project tracks, how completely are the fields a queue-process analysis depends on actually populated? Built to turn the SPP "post-IA is not computable" observation from an anecdote into a national result.

## What "populated" means for each field

- **q_date** — non-empty interconnection-request (IR) date.
- **ia_date** — non-empty executed interconnection-agreement date.
- **wd_date** — non-empty withdrawal date. Only meaningful for withdrawn projects; operational/active/suspended projects are not expected to carry one.
- **on_date** — non-empty commercial-operation (COD) date.
- **cluster** — non-empty cluster/cycle tag. ERCOT runs no cluster study, so near-zero cluster coverage there reflects an absent process, not missing data -- see run_stitch_brief.py's _cycle_key.
- **mw** — mw_1 (the primary reported capacity column) is non-null. This does NOT include mw_2 or mw_3, which are co-located/hybrid secondary capacity columns reported separately below as hybrid_capacity, because mw_1 is ~100% populated nationally while mw_2/mw_3 are populated only for the small share of projects that are hybrid -- collapsing them into one 'mw populated' percentage would misrepresent both.
- **entity** — non-empty reporting utility/BA name. Distinct from the 'region' field: region is LBNL's multi-entity grouping (e.g. 'west' spans dozens of utilities), entity is the individual reporting utility within it.

## Post-IA observability test

Post-IA completion (LBNL Sheet 27's method) requires knowing, for each withdrawn project, whether it withdrew before or after executing an interconnection agreement -- which this dataset can only tell from a populated ia_date on that withdrawn record. This audit reports, per region, how many withdrawn projects carry that date. A count of zero means the rate cannot be computed for that region; it does NOT mean no project in that region ever signed an IA and later withdrew. The public data does not record the date for those cases, so their IA history is unobservable, not absent. Classification: 'absent' = zero withdrawn projects carry an ia_date, so no post-IA rate can be computed at all. 'partial' = at least one but fewer than min_cohort, so a rate could technically be computed but rests on very few cases. 'complete' = at least min_cohort withdrawn projects carry an ia_date -- enough decided, observed cases to support a stable rate. 'complete' describes whether the SAMPLE is large enough, not whether the field is 100% populated: MISO classifies 'complete' with only 27% of its withdrawn cohort dated, because 27% of a large region is still hundreds of cases.

| Region | Withdrawn w/ ia_date | Total withdrawn | % | Classification |
|---|---:|---:|---:|---|
| **SPP** | 0 | 1,846 | absent — not computable | absent |
| **PJM** | 32 | 5,226 | 0.6% | complete |
| **CAISO** | 20 | 2,200 | 0.9% | partial |
| **NYISO** | 15 | 1,531 | 1.0% | partial |
| **SOUTHEAST** | 74 | 2,738 | 2.7% | complete |
| **ISO_NE** | 32 | 982 | 3.3% | complete |
| **WEST** | 172 | 5,277 | 3.3% | complete |
| **ERCOT** | 124 | 1,158 | 10.7% | complete |
| **MISO** | 889 | 3,263 | 27.2% | complete |

## Notable finding — wd_date coverage varies sharply by region

wd_date (withdrawal date) is currently unused by any pipeline in this repo, but it is required to know *when* a withdrawn project's clock stopped -- the input any survival/censoring analysis (planned next) needs. Coverage within each region's withdrawn cohort, worst first:

| Region | wd_date populated | Total withdrawn | % |
|---|---:|---:|---:|
| **WEST** | 641 | 5,277 | 12.1% |
| **SOUTHEAST** | 957 | 2,738 | 35.0% |
| **NYISO** | 745 | 1,531 | 48.7% |
| **ERCOT** | 564 | 1,158 | 48.7% |
| **SPP** | 1,343 | 1,846 | 72.8% |
| **MISO** | 3,061 | 3,263 | 93.8% |
| **CAISO** | 2,161 | 2,200 | 98.2% |
| **PJM** | 5,140 | 5,226 | 98.4% |
| **ISO_NE** | 970 | 982 | 98.8% |

## Field coverage by region and status

Cells read populated/total (%). `mw` is mw_1 only; hybrid_capacity (mw_2/mw_3) is reported separately beneath each region's table.

### CAISO (n=2,868)

| Field | operational | withdrawn | active | suspended |
|---|---:|---:|---:|---:|
| q_date | 235/235 (100.0%) | 2,200/2,200 (100.0%) | 432/432 (100.0%) | 1/1 (100.0%) |
| ia_date | 196/235 (83.4%) | 20/2,200 (0.9%) | 228/432 (52.8%) | 1/1 (100.0%) |
| wd_date | 0/235 (0.0%) | 2,161/2,200 (98.2%) | 0/432 (0.0%) | 0/1 (0.0%) |
| on_date | 227/235 (96.6%) | 0/2,200 (0.0%) | 23/432 (5.3%) | 0/1 (0.0%) |
| cluster | 150/235 (63.8%) | 1,746/2,200 (79.4%) | 416/432 (96.3%) | 1/1 (100.0%) |
| mw | 235/235 (100.0%) | 2,200/2,200 (100.0%) | 432/432 (100.0%) | 1/1 (100.0%) |
| entity | 235/235 (100.0%) | 2,200/2,200 (100.0%) | 432/432 (100.0%) | 1/1 (100.0%) |

Hybrid capacity (co-located projects, not part of the mw row above): operational: mw2 39/235 (16.6%), mw3 0/235 (0.0%); withdrawn: mw2 483/2,200 (22.0%), mw3 15/2,200 (0.7%); active: mw2 214/432 (49.5%), mw3 2/432 (0.5%); suspended: mw2 0/1 (0.0%), mw3 0/1 (0.0%)

### ERCOT (n=3,757)

| Field | operational | withdrawn | active | suspended |
|---|---:|---:|---:|---:|
| q_date | 564/613 (92.0%) | 1,100/1,158 (95.0%) | 1,764/1,796 (98.2%) | 180/190 (94.7%) |
| ia_date | 486/613 (79.3%) | 124/1,158 (10.7%) | 576/1,796 (32.1%) | 21/190 (11.1%) |
| wd_date | 0/613 (0.0%) | 564/1,158 (48.7%) | 1/1,796 (0.1%) | 6/190 (3.2%) |
| on_date | 519/613 (84.7%) | 0/1,158 (0.0%) | 6/1,796 (0.3%) | 4/190 (2.1%) |
| cluster | 0/613 (0.0%) | 0/1,158 (0.0%) | 0/1,796 (0.0%) | 0/190 (0.0%) |
| mw | 613/613 (100.0%) | 1,158/1,158 (100.0%) | 1,796/1,796 (100.0%) | 190/190 (100.0%) |
| entity | 613/613 (100.0%) | 1,158/1,158 (100.0%) | 1,796/1,796 (100.0%) | 190/190 (100.0%) |

Hybrid capacity (co-located projects, not part of the mw row above): operational: mw2 0/613 (0.0%), mw3 0/613 (0.0%); withdrawn: mw2 0/1,158 (0.0%), mw3 0/1,158 (0.0%); active: mw2 0/1,796 (0.0%), mw3 0/1,796 (0.0%); suspended: mw2 0/190 (0.0%), mw3 0/190 (0.0%)

### ISO_NE (n=1,282)

| Field | operational | withdrawn | active | suspended |
|---|---:|---:|---:|---:|
| q_date | 228/228 (100.0%) | 982/982 (100.0%) | 72/72 (100.0%) | 0/0 (— (n=0)) |
| ia_date | 97/228 (42.5%) | 32/982 (3.3%) | 41/72 (56.9%) | 0/0 (— (n=0)) |
| wd_date | 4/228 (1.8%) | 970/982 (98.8%) | 0/72 (0.0%) | 0/0 (— (n=0)) |
| on_date | 0/228 (0.0%) | 0/982 (0.0%) | 0/72 (0.0%) | 0/0 (— (n=0)) |
| cluster | 12/228 (5.3%) | 34/982 (3.5%) | 0/72 (0.0%) | 0/0 (— (n=0)) |
| mw | 228/228 (100.0%) | 982/982 (100.0%) | 72/72 (100.0%) | 0/0 (— (n=0)) |
| entity | 228/228 (100.0%) | 982/982 (100.0%) | 72/72 (100.0%) | 0/0 (— (n=0)) |

Hybrid capacity (co-located projects, not part of the mw row above): operational: mw2 0/228 (0.0%), mw3 0/228 (0.0%); withdrawn: mw2 0/982 (0.0%), mw3 0/982 (0.0%); active: mw2 0/72 (0.0%), mw3 0/72 (0.0%); suspended: mw2 0/0 (— (n=0)), mw3 0/0 (— (n=0))

### MISO (n=5,424)

| Field | operational | withdrawn | active | suspended |
|---|---:|---:|---:|---:|
| q_date | 515/515 (100.0%) | 3,261/3,263 (99.9%) | 1,642/1,646 (99.8%) | 0/0 (— (n=0)) |
| ia_date | 476/515 (92.4%) | 889/3,263 (27.2%) | 395/1,646 (24.0%) | 0/0 (— (n=0)) |
| wd_date | 3/515 (0.6%) | 3,061/3,263 (93.8%) | 18/1,646 (1.1%) | 0/0 (— (n=0)) |
| on_date | 497/515 (96.5%) | 3/3,263 (0.1%) | 60/1,646 (3.6%) | 0/0 (— (n=0)) |
| cluster | 389/515 (75.5%) | 2,414/3,263 (74.0%) | 1,458/1,646 (88.6%) | 0/0 (— (n=0)) |
| mw | 515/515 (100.0%) | 3,263/3,263 (100.0%) | 1,646/1,646 (100.0%) | 0/0 (— (n=0)) |
| entity | 515/515 (100.0%) | 3,263/3,263 (100.0%) | 1,646/1,646 (100.0%) | 0/0 (— (n=0)) |

Hybrid capacity (co-located projects, not part of the mw row above): operational: mw2 0/515 (0.0%), mw3 0/515 (0.0%); withdrawn: mw2 0/3,263 (0.0%), mw3 0/3,263 (0.0%); active: mw2 0/1,646 (0.0%), mw3 0/1,646 (0.0%); suspended: mw2 0/0 (— (n=0)), mw3 0/0 (— (n=0))

### NYISO (n=1,936)

| Field | operational | withdrawn | active | suspended |
|---|---:|---:|---:|---:|
| q_date | 215/215 (100.0%) | 1,531/1,531 (100.0%) | 190/190 (100.0%) | 0/0 (— (n=0)) |
| ia_date | 35/215 (16.3%) | 15/1,531 (1.0%) | 59/190 (31.1%) | 0/0 (— (n=0)) |
| wd_date | 2/215 (0.9%) | 745/1,531 (48.7%) | 0/190 (0.0%) | 0/0 (— (n=0)) |
| on_date | 83/215 (38.6%) | 0/1,531 (0.0%) | 0/190 (0.0%) | 0/0 (— (n=0)) |
| cluster | 0/215 (0.0%) | 282/1,531 (18.4%) | 89/190 (46.8%) | 0/0 (— (n=0)) |
| mw | 215/215 (100.0%) | 1,531/1,531 (100.0%) | 190/190 (100.0%) | 0/0 (— (n=0)) |
| entity | 215/215 (100.0%) | 1,531/1,531 (100.0%) | 190/190 (100.0%) | 0/0 (— (n=0)) |

Hybrid capacity (co-located projects, not part of the mw row above): operational: mw2 0/215 (0.0%), mw3 0/215 (0.0%); withdrawn: mw2 0/1,531 (0.0%), mw3 0/1,531 (0.0%); active: mw2 0/190 (0.0%), mw3 0/190 (0.0%); suspended: mw2 0/0 (— (n=0)), mw3 0/0 (— (n=0))

### PJM (n=7,666)

| Field | operational | withdrawn | active | suspended |
|---|---:|---:|---:|---:|
| q_date | 1,192/1,192 (100.0%) | 5,178/5,226 (99.1%) | 1,134/1,134 (100.0%) | 114/114 (100.0%) |
| ia_date | 195/1,192 (16.4%) | 32/5,226 (0.6%) | 15/1,134 (1.3%) | 5/114 (4.4%) |
| wd_date | 5/1,192 (0.4%) | 5,140/5,226 (98.4%) | 1/1,134 (0.1%) | 0/114 (0.0%) |
| on_date | 1,185/1,192 (99.4%) | 8/5,226 (0.2%) | 5/1,134 (0.4%) | 1/114 (0.9%) |
| cluster | 0/1,192 (0.0%) | 580/5,226 (11.1%) | 313/1,134 (27.6%) | 0/114 (0.0%) |
| mw | 1,192/1,192 (100.0%) | 5,226/5,226 (100.0%) | 1,134/1,134 (100.0%) | 114/114 (100.0%) |
| entity | 1,192/1,192 (100.0%) | 5,226/5,226 (100.0%) | 1,134/1,134 (100.0%) | 114/114 (100.0%) |

Hybrid capacity (co-located projects, not part of the mw row above): operational: mw2 0/1,192 (0.0%), mw3 0/1,192 (0.0%); withdrawn: mw2 0/5,226 (0.0%), mw3 0/5,226 (0.0%); active: mw2 0/1,134 (0.0%), mw3 0/1,134 (0.0%); suspended: mw2 0/114 (0.0%), mw3 0/114 (0.0%)

### SOUTHEAST (n=4,334)

| Field | operational | withdrawn | active | suspended |
|---|---:|---:|---:|---:|
| q_date | 446/529 (84.3%) | 2,526/2,738 (92.3%) | 922/957 (96.3%) | 110/110 (100.0%) |
| ia_date | 92/529 (17.4%) | 74/2,738 (2.7%) | 1/957 (0.1%) | 0/110 (0.0%) |
| wd_date | 0/529 (0.0%) | 957/2,738 (35.0%) | 0/957 (0.0%) | 0/110 (0.0%) |
| on_date | 313/529 (59.2%) | 5/2,738 (0.2%) | 14/957 (1.5%) | 0/110 (0.0%) |
| cluster | 10/529 (1.9%) | 444/2,738 (16.2%) | 345/957 (36.1%) | 0/110 (0.0%) |
| mw | 529/529 (100.0%) | 2,738/2,738 (100.0%) | 957/957 (100.0%) | 110/110 (100.0%) |
| entity | 529/529 (100.0%) | 2,738/2,738 (100.0%) | 957/957 (100.0%) | 110/110 (100.0%) |

Hybrid capacity (co-located projects, not part of the mw row above): operational: mw2 0/529 (0.0%), mw3 0/529 (0.0%); withdrawn: mw2 0/2,738 (0.0%), mw3 0/2,738 (0.0%); active: mw2 0/957 (0.0%), mw3 0/957 (0.0%); suspended: mw2 0/110 (0.0%), mw3 0/110 (0.0%)

### SPP (n=2,837)

| Field | operational | withdrawn | active | suspended |
|---|---:|---:|---:|---:|
| q_date | 281/299 (94.0%) | 1,838/1,846 (99.6%) | 683/683 (100.0%) | 9/9 (100.0%) |
| ia_date | 0/299 (0.0%) | 0/1,846 (0.0%) | 0/683 (0.0%) | 0/9 (0.0%) |
| wd_date | 0/299 (0.0%) | 1,343/1,846 (72.8%) | 0/683 (0.0%) | 0/9 (0.0%) |
| on_date | 288/299 (96.3%) | 241/1,846 (13.1%) | 43/683 (6.3%) | 0/9 (0.0%) |
| cluster | 254/299 (84.9%) | 1,062/1,846 (57.5%) | 683/683 (100.0%) | 9/9 (100.0%) |
| mw | 299/299 (100.0%) | 1,846/1,846 (100.0%) | 683/683 (100.0%) | 9/9 (100.0%) |
| entity | 299/299 (100.0%) | 1,846/1,846 (100.0%) | 683/683 (100.0%) | 9/9 (100.0%) |

Hybrid capacity (co-located projects, not part of the mw row above): operational: mw2 0/299 (0.0%), mw3 0/299 (0.0%); withdrawn: mw2 0/1,846 (0.0%), mw3 0/1,846 (0.0%); active: mw2 0/683 (0.0%), mw3 0/683 (0.0%); suspended: mw2 0/9 (0.0%), mw3 0/9 (0.0%)

### WEST (n=8,097)

| Field | operational | withdrawn | active | suspended |
|---|---:|---:|---:|---:|
| q_date | 877/963 (91.1%) | 5,267/5,277 (99.8%) | 1,608/1,613 (99.7%) | 239/244 (98.0%) |
| ia_date | 440/963 (45.7%) | 172/5,277 (3.3%) | 76/1,613 (4.7%) | 40/244 (16.4%) |
| wd_date | 0/963 (0.0%) | 641/5,277 (12.1%) | 0/1,613 (0.0%) | 1/244 (0.4%) |
| on_date | 177/963 (18.4%) | 0/5,277 (0.0%) | 7/1,613 (0.4%) | 0/244 (0.0%) |
| cluster | 55/963 (5.7%) | 966/5,277 (18.3%) | 654/1,613 (40.5%) | 29/244 (11.9%) |
| mw | 963/963 (100.0%) | 5,277/5,277 (100.0%) | 1,613/1,613 (100.0%) | 244/244 (100.0%) |
| entity | 963/963 (100.0%) | 5,277/5,277 (100.0%) | 1,613/1,613 (100.0%) | 244/244 (100.0%) |

Hybrid capacity (co-located projects, not part of the mw row above): operational: mw2 9/963 (0.9%), mw3 0/963 (0.0%); withdrawn: mw2 173/5,277 (3.3%), mw3 15/5,277 (0.3%); active: mw2 170/1,613 (10.5%), mw3 13/1,613 (0.8%); suspended: mw2 8/244 (3.3%), mw3 0/244 (0.0%)

_Scope: region level only. Entity-level figures (e.g. isolating a single utility within a multi-entity region) are a separate, bounded audit for later, not covered here._
