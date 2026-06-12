# Grid Relief Curves

## Method

Each curve evaluates a deterministic structural causal model under `do(capacity_mw = x)`. Relief is capped by the priced annual tie value and should be read as screening-grade, not a production-cost simulation.

## Benchmarks

| Benchmark | Annualized Cost $/MW-yr | Effective MWh/MW-yr | Source |
|---|---:|---:|---|
| transmission_capacity | $150,000 | 8,760 | screening default; replace with project-specific transmission estimate |
| grid_storage_4h | $187,500 | 1,200 | NREL ATB utility-scale battery methodology, annualized screening default |
| flexible_load | $70,000 | 600 | screening default; replace with customer/program bid data |

## Ranked Opportunities

| Tie | Spread $/MWh | Value Cap | Active Queue | Best Benchmark | Relief | Annual Cost | B/C | Constraints |
|---|---:|---:|---:|---|---:|---:|---:|---|
| MISO-SWPP | 4.74 | $18,912,050 | 156.5 GW | transmission_capacity | $1,966,222 | $7,500,000 | 0.26 | MISO:CHAR_CK-WATFORD FLO PATINGATE-CHARLIE CK (5,138 h, severity 1,069,182); SPP:CHAWATCHAPAT (5,951 h, severity 895,951); MISO:MORRISOT-GRANTCO FLO HANK-WAP+WAP TR2 (2,453 h, severity 654,610) |
| PJM-NYIS | 1.53 | $29,461,244 | 85.5 GW | transmission_capacity | $661,267 | $7,500,000 | 0.09 | PJM:NOTTINGH230 KV  2-3 (6,025 h, severity 353,557); PJM:LENOX-NMESHOPP NML 1090     B  115 KV (1,847 h, severity 227,804); PJM:GRACETON230 KV  GRA-SAF (3,339 h, severity 130,754) |
| MISO-SOCO | 1.35 | $7,230,307 | 261.9 GW | transmission_capacity | $567,767 | $7,500,000 | 0.08 | MISO:CHAR_CK-WATFORD FLO PATINGATE-CHARLIE CK (5,138 h, severity 1,069,182); MISO:MORRISOT-GRANTCO FLO HANK-WAP+WAP TR2 (2,453 h, severity 654,610); MISO:FORMAN TR12 FLO WAHPETON-HANKINSON (1,607 h, severity 389,783) |
| CISO-SRP | 1.39 | $14,038,274 | 68.0 GW | transmission_capacity | $595,807 | $7,500,000 | 0.08 |  |
| BPAT-CISO | 1.11 | $6,059,449 | 85.6 GW | transmission_capacity | $467,187 | $7,500,000 | 0.06 |  |
