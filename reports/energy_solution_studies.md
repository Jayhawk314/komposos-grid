# Energy Solution Studies

## Summary

| Corridor | Value | Current Spread | Active Queue | Best Cost Gate | Next Action |
|---|---:|---:|---:|---:|---|
| NYIS-PJM | $159,672,256/yr | $7.38/MWh | 85.5 GW | $161,622,000 | Price the top PJM-side active projects and a small transfer upgrade against the break-even capex envelope. |
| MISO-SWPP | $29,424,117/yr | $6.31/MWh | 156.5 GW | $138,189,000 | Map CHAWATCHAPAT and Charlie Creek-Watford to upgrade candidates and price a 50-100 MW relief package. |

## Flow Evidence Status

| Corridor | Price Year | Flow Year | Status | Gross Flow | Annual Value |
|---|---:|---:|---|---:|---:|
| NYIS-PJM | 2025 | 2025 | same_year_flow | 21,635,807 MWh | $159,672,256/yr |
| MISO-SWPP | 2024 | 2024 | same_year_flow | 4,663,093 MWh | $29,424,117/yr |

# PJM-NYIS 2025 Solution Memo

## Decision Frame

- Corridor: **NYIS-PJM**
- Current evidence year: **2025**
- Current congestion spread: **$7.38/MWh**
- Annual value at current spread: **$159,672,256/yr**
- Gross flow basis: **21,635,807 MWh** (2025; same_year_flow)
- Trend: 2023 $1.53/MWh -> 2024 $2.02/MWh -> 2025 $7.38/MWh (4.8x over observed window).
- Recommended path: Start with a 50-100 MW transfer-relief or queue-rescue package; storage clears only if it is paid for by more than seam congestion.
- Next action: Price the top PJM-side active projects and a small transfer upgrade against the break-even capex envelope.
- Caveat: Value uses same-year gross flow; remaining gap before a final investment case is project-specific costing, not flow evidence.

## Constraints

- PJM:NOTTINGH230 KV  2-3 (6,025 h, severity 353,557)
- PJM:LENOX-NMESHOPP NML 1090     B  115 KV (1,847 h, severity 227,804)
- PJM:GRACETON230 KV  GRA-SAF (3,339 h, severity 130,754)
- PJM:Chicago-Praxair3 138 kV l/o Wilton Center-Dumont 765 kV (661 h, severity 120,695)
- PJM:Turkey Hill-Hilgard 138 kV l/o Prairie State-Mt Vernon 345 kV (1,065 h, severity 118,169)

## Project-Cost Gates

A project clears on congestion value alone only if its real annual cost is below the break-even annual cost below. Capital envelopes use a 10% fixed-charge rate.

| Intervention | Capacity | Relief Value | Break-Even Annual Cost | Break-Even Capex | Capex $/kW |
|---|---:|---:|---:|---:|---:|
| 50 MW targeted transfer upgrade | 50 MW | $3,232,440/yr | $3,232,440/yr | $32,324,400 | $646/kW |
| 100 MW targeted transfer upgrade | 100 MW | $6,464,880/yr | $6,464,880/yr | $64,648,800 | $646/kW |
| 250 MW targeted transfer upgrade | 250 MW | $16,162,200/yr | $16,162,200/yr | $161,622,000 | $646/kW |
| 100 MW / 4-hour storage siting screen | 100 MW | $885,600/yr | $885,600/yr | $8,856,000 | $89/kW |
| 100 MW flexible-load program | 100 MW | $442,800/yr | $442,800/yr | $4,428,000 | $44/kW |

## Quoted Project Costs

- No quoted project costs supplied yet.

## Active Queue Candidates

| Queue ID | Fuel | MW | State | Role | Side | Relief Value |
|---|---|---:|---|---|---|---:|
| AG2-582 | gas | 2,100 | WV | generation | PJM | $74,669,364/yr |
| AI2-431 | offshore_wind | 2,139 | NJ | generation | PJM | $62,223,339/yr |
| AI1-001 | offshore_wind | 2,100 | NJ | generation | PJM | $61,093,116/yr |
| AH1-695 | nuclear | 859 | PA | generation | PJM | $49,979,987/yr |
| AH1-680 | gas | 1,300 | OH | generation | PJM | $46,223,892/yr |

## Withdrawn Opportunity

| Queue ID | Fuel | MW | State | Role | Side | Lost Relief Value |
|---|---|---:|---|---|---|---:|
| Q65 | nuclear | 1,594 | VA | generation | PJM | $92,745,168/yr |
| R67 | coal | 2,510 | PA | generation | PJM | $89,247,668/yr |
| AH1-675 | gas | 2,175 | PA | generation | PJM | $77,336,127/yr |
| R68 | coal | 1,940 | OH | generation | PJM | $68,980,270/yr |
| AE1-222 | gas | 2,563 | IL | generation | PJM | $67,728,699/yr |

# MISO-SWPP Wind-Belt Solution Memo

## Decision Frame

- Corridor: **MISO-SWPP**
- Current evidence year: **2024**
- Current congestion spread: **$6.31/MWh**
- Annual value at current spread: **$29,424,117/yr**
- Gross flow basis: **4,663,093 MWh** (2024; same_year_flow)
- Trend: 2023 $4.74/MWh -> 2024 $6.31/MWh (1.3x over observed window).
- Recommended path: Start with targeted transfer relief around the wind-belt constraints, then test storage only where it also captures local energy or capacity value.
- Next action: Map CHAWATCHAPAT and Charlie Creek-Watford to upgrade candidates and price a 50-100 MW relief package.
- Caveat: MISO-side and SPP-side seam evidence corroborate the problem; do not double-count them as separate benefits.

## Constraints

- MISO:CHAR_CK-WATFORD FLO PATINGATE-CHARLIE CK (5,138 h, severity 1,069,182)
- SPP:CHAWATCHAPAT (5,951 h, severity 895,951)
- MISO:MORRISOT-GRANTCO FLO HANK-WAP+WAP TR2 (2,453 h, severity 654,610)
- MISO:FORMAN TR12 FLO WAHPETON-HANKINSON (1,607 h, severity 389,783)
- SPP:OSAWEBCLESOO (2,078 h, severity 360,524)
- SPP:TMP499_26328 (2,074 h, severity 316,737)

## Project-Cost Gates

A project clears on congestion value alone only if its real annual cost is below the break-even annual cost below. Capital envelopes use a 10% fixed-charge rate.

| Intervention | Capacity | Relief Value | Break-Even Annual Cost | Break-Even Capex | Capex $/kW |
|---|---:|---:|---:|---:|---:|
| 50 MW targeted transfer upgrade | 50 MW | $2,763,780/yr | $2,763,780/yr | $27,637,800 | $553/kW |
| 100 MW targeted transfer upgrade | 100 MW | $5,527,560/yr | $5,527,560/yr | $55,275,600 | $553/kW |
| 250 MW targeted transfer upgrade | 250 MW | $13,818,900/yr | $13,818,900/yr | $138,189,000 | $553/kW |
| 100 MW / 4-hour storage siting screen | 100 MW | $757,200/yr | $757,200/yr | $7,572,000 | $76/kW |
| 100 MW flexible-load program | 100 MW | $378,600/yr | $378,600/yr | $3,786,000 | $38/kW |

## Quoted Project Costs

- No quoted project costs supplied yet.

## Active Queue Candidates

| Queue ID | Fuel | MW | State | Role | Side | Relief Value |
|---|---|---:|---|---|---|---:|
| GEN-2024-129 | gas | 910 | KS | generation | SWPP | $25,176,168/yr |
| GEN-2024-132 | gas | 1,300 | OK | generation | SWPP | $25,176,168/yr |
| GEN-2024-340 | gas | 1,400 | OK | generation | SWPP | $25,176,168/yr |
| GEN-2024-341 | gas | 1,045 | OK | generation | SWPP | $25,176,168/yr |
| ERAS-2025-011 | gas | 750 | ND | generation | SWPP | $22,801,185/yr |

## Withdrawn Opportunity

| Queue ID | Fuel | MW | State | Role | Side | Lost Relief Value |
|---|---|---:|---|---|---|---:|
| GEN-2000-014 | gas | 1,300 | OK | generation | SWPP | $25,176,168/yr |
| GEN-2004-013 | coal | 900 | KS | generation | SWPP | $25,176,168/yr |
| GEN-2007-007 | coal | 985 | OK | generation | SWPP | $25,176,168/yr |
| GEN-2009-021 | coal | 895 | KS | generation | SWPP | $25,176,168/yr |
| GEN-2011-030 | coal | 1,020 | KS | generation | SWPP | $25,176,168/yr |
