# BA Footprint Correction Report

## Result

- Accepted corrections: **10**
- Rejected candidates: **3**
- BA agreement: **45.2% -> 62.9%**
- BA contradictions: **11 -> 7**
- Absolute BA error: **290.5 TWh -> 231.2 TWh**
- Sheaf H^1 leak: **1.899e+00 -> 8.185e-01**

## Accepted Corrections

| Entity | State | From BA | To BA | MWh | Improvement MWh | Confidence |
|---|---:|---:|---:|---:|---:|---:|
| 3082 | OR | BPAT | GRID | 6,793,297 | 13,586,594 | 1.00 |
| 3895 | OR | BPAT | GRID | 5,406,985 | 10,813,970 | 1.00 |
| 2721 | NC | DUK | CPLW | 5,244,807 | 8,325,182 | 0.79 |
| 55306 | AZ | SRP | AZPS | 7,390,743 | 7,810,272 | 0.53 |
| 55821 | FL | FPC | FMPP | 3,546,362 | 7,092,724 | 1.00 |
| 55482 | WA | PSEI | GCPD | 2,172,002 | 4,344,004 | 1.00 |
| 55700 | WA | PSEI | GCPD | 1,989,583 | 3,401,670 | 0.85 |
| 117 | AZ | AZPS | TEPC | 3,053,387 | 2,075,763 | 0.34 |
| 10202 | FL | JEA | SEC | 557,724 | 1,115,448 | 1.00 |
| 447 | CA | WALC | IID | 392,219 | 784,438 | 1.00 |

## Rejected Candidates

| Entity | From BA | To BA | Reason |
|---|---:|---:|---|
| 55112 | WALC | BANC | source and target BAs lack observed interchange tie |
| 65577 | PSEI | NWMT | source and target BAs lack observed interchange tie |
| 50188 | CPLE | SEPA | source and target BAs lack observed interchange tie |

## Remaining Largest BA Deltas

| BA | Delta MWh | Interpretation |
|---|---:|---|
| MISO | -39,569,125 | accounting higher |
| ERCO | -31,761,206 | accounting higher |
| NA - PR | -17,501,153 | accounting higher |
| SOCO | -11,333,276 | accounting higher |
| TVA | -10,059,476 | accounting higher |
| CPLE | -9,370,872 | accounting higher |
| WALC | -7,842,254 | accounting higher |
| PSCO | 7,761,660 | telemetry higher |
| PGE | -6,903,039 | accounting higher |
| FPL | 6,665,650 | telemetry higher |
