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
