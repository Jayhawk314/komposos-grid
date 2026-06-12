# Energy Solution Studies

## Summary

| Corridor | Value | Current Spread | Active Queue | Best Cost Gate | Next Action |
|---|---:|---:|---:|---:|---|
| NYIS-PJM | $159,672,256/yr | $7.38/MWh | 85.5 GW | $161,622,000 | Price the top PJM-side active projects and a small transfer upgrade against the break-even capex envelope. |
| MISO-SWPP | $31,147,626/yr | $7.33/MWh | 156.5 GW | $160,527,000 | Map CHAWATCHAPAT and Charlie Creek-Watford to upgrade candidates and price a 50-100 MW relief package. |

## Flow Evidence Status

| Corridor | Price Year | Flow Year | Status | Gross Flow | Annual Value |
|---|---:|---:|---|---:|---:|
| NYIS-PJM | 2025 | 2025 | same_year_flow | 21,635,807 MWh | $159,672,256/yr |
| MISO-SWPP | 2025 | 2025 | same_year_flow | 4,249,335 MWh | $31,147,626/yr |

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
- Caveat: Value uses same-year gross flow. CHPE (1,250 MW HVDC into NYC) entered commercial operation 2026-05-13 and should compress this seam's spread going forward, so the 2025 spread-based value is an upper bound for post-2026 cases; rerun seam evidence on post-CHPE months before committing.

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

| Project | Type | Capacity | Annual Cost | Relief Value | B/C | Net Value |
|---|---|---:|---:|---:|---:|---:|
| Champlain Hudson Power Express 1250 MW HVDC (context screen) | transmission_or_grid_enhancing_transfer | 1,250 MW | $690,000,000/yr | $80,811,000/yr | 0.12 | $-609,189,000/yr |

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
- Current evidence year: **2025**
- Current congestion spread: **$7.33/MWh**
- Annual value at current spread: **$31,147,626/yr**
- Gross flow basis: **4,249,335 MWh** (2025; same_year_flow)
- Trend: 2023 $4.74/MWh -> 2024 $6.31/MWh -> 2025 $7.33/MWh (1.5x over observed window).
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
| 50 MW targeted transfer upgrade | 50 MW | $3,210,540/yr | $3,210,540/yr | $32,105,400 | $642/kW |
| 100 MW targeted transfer upgrade | 100 MW | $6,421,080/yr | $6,421,080/yr | $64,210,800 | $642/kW |
| 250 MW targeted transfer upgrade | 250 MW | $16,052,700/yr | $16,052,700/yr | $160,527,000 | $642/kW |
| 100 MW / 4-hour storage siting screen | 100 MW | $879,600/yr | $879,600/yr | $8,796,000 | $88/kW |
| 100 MW flexible-load program | 100 MW | $439,800/yr | $439,800/yr | $4,398,000 | $44/kW |

## Quoted Project Costs

| Project | Type | Capacity | Annual Cost | Relief Value | B/C | Net Value |
|---|---|---:|---:|---:|---:|---:|
| Patent Gate - Pioneer 345 kV Ckt 1 New Line (full-relief cap case) | transmission_or_grid_enhancing_transfer | 1,000 MW | $18,827,114/yr | $31,147,626/yr | 1.65 | $12,320,511/yr |
| Patent Gate - Pioneer 345 kV Ckt 1 New Line (250 MW seam-relief sensitivity) | transmission_or_grid_enhancing_transfer | 250 MW | $18,827,114/yr | $16,052,700/yr | 0.85 | $-2,774,414/yr |

## Active Queue Candidates

| Queue ID | Fuel | MW | State | Role | Side | Relief Value |
|---|---|---:|---|---|---|---:|
| GEN-2024-129 | gas | 910 | KS | generation | SWPP | $29,245,850/yr |
| GEN-2024-132 | gas | 1,300 | OK | generation | SWPP | $29,245,850/yr |
| GEN-2024-340 | gas | 1,400 | OK | generation | SWPP | $29,245,850/yr |
| GEN-2024-341 | gas | 1,045 | OK | generation | SWPP | $29,245,850/yr |
| ERAS-2025-011 | gas | 750 | ND | generation | SWPP | $26,486,955/yr |

## Withdrawn Opportunity

| Queue ID | Fuel | MW | State | Role | Side | Lost Relief Value |
|---|---|---:|---|---|---|---:|
| GEN-2000-014 | gas | 1,300 | OK | generation | SWPP | $29,245,850/yr |
| GEN-2004-013 | coal | 900 | KS | generation | SWPP | $29,245,850/yr |
| GEN-2007-007 | coal | 985 | OK | generation | SWPP | $29,245,850/yr |
| GEN-2009-021 | coal | 895 | KS | generation | SWPP | $29,245,850/yr |
| GEN-2011-030 | coal | 1,020 | KS | generation | SWPP | $29,245,850/yr |
