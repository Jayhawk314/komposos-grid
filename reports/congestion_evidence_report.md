# Congestion Evidence Report

## Result

- Structural bottlenecks: **25**
- Evidence matched: **6**
- Measured/proxy claims: **6**
- Estimated measured/proxy value: **$223,830,377**

## Ranked Claims

| Tie | Evidence | Curvature | Gross MWh | Estimated Value | Source | Notes |
|---|---|---:|---:|---:|---|---|
| PJM - NYIS | lmp_component_proxy | -0.107 | 21,635,807 | $159,584,663 | NYISO DAM zonal LBMP 2025 settlement components (mis.nyiso.com; NYCA internal-zone mean vs PJM proxy bus) | Uses NYISO hourly settlement congestion component, not only annual hub price level. Congestion component is 81.7% of mean absolute LBMP spread; NYCA LBMP above PJM proxy 97.9% of hours. |
| MISO - SWPP | lmp_component_proxy | -0.037 | 4,249,335 | $31,062,639 | MISO DA ex-post LMP (docs.misoenergy.org; ARKANSAS.HUB vs SWPP interface, 2025-01-01..2025-12-31) | Hourly DA settlement spread, MISO side of the seam; congestion component 93.4% of mean |LMP spread|; ARKANSAS.HUB above 50.1% of hours; 0 report days missing. |
| CISO - SRP | lmp_component_proxy | -0.036 | 9,041,327 | $12,567,445 | CAISO OASIS PRC_LMP DAM v12 (TH_SP15_GEN-APND vs PALOVRDE_ASR-APND, 2023-04-01..2024-01-01); EIA ICE daily wholesale prices 2023 + EIA-930 interchange | Hourly DAM settlement spread; congestion component is 89.4% of mean |LMP spread|; TH_SP15_GEN-APND above 63.8% of hours. Window limited by OASIS ~39-month retention.; SP15 EZ Gen DA LMP Peak $64.85 vs Palo Verde Peak $78.87; daily overlap mean |spread| $15.58/MWh; flow-weighted alignment 39.0%; flow/price alignment is weak. |
| MISO - SOCO | lmp_component_proxy | -0.160 | 5,909,762 | $12,292,305 | MISO DA ex-post LMP (docs.misoenergy.org; MS.HUB vs SOCO interface, 2025-01-01..2025-12-31) | Hourly DA settlement spread, MISO side of the seam; congestion component 85.5% of mean |LMP spread|; MS.HUB above 19.2% of hours; 0 report days missing. |
| BPAT - CISO | lmp_component_proxy | -0.085 | 6,076,992 | $6,745,461 | CAISO OASIS PRC_LMP DAM v12 (TH_NP15_GEN-APND vs MALIN_5_N101, 2023-04-01..2024-01-01); EIA ICE daily wholesale prices 2023 + EIA-930 interchange | Hourly DAM settlement spread; congestion component is 81.4% of mean |LMP spread|; TH_NP15_GEN-APND above 63.1% of hours. Window limited by OASIS ~39-month retention.; Mid C Peak $82.66 vs NP15 EZ Gen DA LMP Peak $73.19; daily overlap mean |spread| $32.90/MWh; flow-weighted alignment 58.9%; flow/price alignment is mixed. NP15 volume is thin, so keep this as a hub-screening proxy. |
| BPAT - NEVP | price_spread_proxy | -0.034 | 416,580 | $1,577,864 | EIA ICE daily wholesale prices 2023 + EIA-930 interchange | Mid C Peak $82.66 vs Palo Verde Peak $78.87; daily overlap mean |spread| $24.02/MWh; flow-weighted alignment 45.3%; flow/price alignment is mixed. NEVP is approximated by Palo Verde. |
| BPAT - GRID | structural_only | -0.228 | 5,729,835 | $0 |  |  |
| BPAT - NWMT | structural_only | -0.122 | 7,588,975 | $0 |  |  |
| BPAT - LDWP | structural_only | -0.098 | 7,952,644 | $0 |  |  |
| SOCO - FPL | structural_only | -0.208 | 3,392,644 | $0 |  |  |
| BPAT - BANC | structural_only | -0.127 | 4,587,718 | $0 |  |  |
| CPLE - PJM | structural_only | -0.086 | 6,175,589 | $0 |  |  |
| TVA - SOCO | structural_only | -0.079 | 5,254,930 | $0 |  |  |
| BPAT - PSEI | structural_only | -0.018 | 15,655,223 | $0 |  |  |
| BPAT - SCL | structural_only | -0.044 | 5,418,456 | $0 |  |  |
| BPAT - DOPD | structural_only | -0.074 | 2,240,220 | $0 |  |  |
| AECI - TVA | structural_only | -0.086 | 1,598,393 | $0 |  |  |
| BPAT - TPWR | structural_only | -0.044 | 2,997,868 | $0 |  |  |
| WACM - WALC | structural_only | -0.048 | 2,551,141 | $0 |  |  |
| SOCO - FPC | structural_only | -0.095 | 635,810 | $0 |  |  |
| NWMT - WAUW | structural_only | -0.119 | 419,600 | $0 |  |  |
| PNM - GRID | structural_only | -0.018 | 2,005,411 | $0 |  |  |
| SWPP - WAUW | structural_only | -0.033 | 407,026 | $0 |  |  |
| SWPP - WACM | structural_only | -0.007 | 1,198,564 | $0 |  |  |
| SWPP - EPE | structural_only | -0.033 | 195,217 | $0 |  |  |
