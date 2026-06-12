# MISO-SWPP Wind-Belt Solution Memo

## Decision Frame

- Corridor: **MISO-SWPP**
- Current evidence year: **2024**
- Current congestion spread: **$6.31/MWh**
- Annual value at current spread: **$25,176,168/yr**
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
