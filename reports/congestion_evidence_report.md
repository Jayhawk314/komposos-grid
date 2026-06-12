# Congestion Evidence Report

## Result

- Structural bottlenecks: **25**
- Evidence matched: **7**
- Measured/proxy claims: **7**
- Estimated measured/proxy value: **$78,564,183**

## Ranked Claims

| Tie | Evidence | Curvature | Gross MWh | Estimated Value | Source | Notes |
|---|---|---:|---:|---:|---|---|
| PJM - NYIS | lmp_component_proxy | -0.107 | 19,294,263 | $29,461,244 | NYISO DAM zonal LBMP 2023 (mis.nyiso.com; hourly NYCA internal-zone mean vs NYISO PJM proxy bus); NYISO DAM zonal LBMP 2023 settlement components (mis.nyiso.com; NYCA internal-zone mean vs PJM proxy bus) | Mean absolute hourly spread; NYCA above PJM proxy 94.3% of hours (persistent west-to-east direction); Uses NYISO hourly settlement congestion component, not only annual hub price level. Congestion component is 75.8% of mean absolute LBMP spread; NYCA LBMP above PJM proxy 94.3% of hours. |
| MISO - SWPP | lmp_component_proxy | -0.095 | 3,989,884 | $18,912,050 | MISO DA ex-post LMP (docs.misoenergy.org; ARKANSAS.HUB vs SWPP interface, 2023-01-01..2023-12-31) | Hourly DA settlement spread, MISO side of the seam; congestion component 93.2% of mean |LMP spread|; ARKANSAS.HUB above 49.5% of hours; 0 report days missing. |
| CISO - SRP | lmp_component_proxy | -0.036 | 10,099,478 | $14,038,274 | CAISO OASIS PRC_LMP DAM v12 (TH_SP15_GEN-APND vs PALOVRDE_ASR-APND, 2023-04-01..2024-01-01) | Hourly DAM settlement spread; congestion component is 89.4% of mean |LMP spread|; TH_SP15_GEN-APND above 63.8% of hours. Window limited by OASIS ~39-month retention. |
| MISO - SOCO | lmp_component_proxy | -0.151 | 5,355,783 | $7,230,307 | MISO DA ex-post LMP (docs.misoenergy.org; MS.HUB vs SOCO interface, 2023-01-01..2023-12-31) | Hourly DA settlement spread, MISO side of the seam; congestion component 85.6% of mean |LMP spread|; MS.HUB above 28.6% of hours; 0 report days missing. |
| BPAT - CISO | lmp_component_proxy | -0.085 | 5,458,963 | $6,059,449 | CAISO OASIS PRC_LMP DAM v12 (TH_NP15_GEN-APND vs MALIN_5_N101, 2023-04-01..2024-01-01) | Hourly DAM settlement spread; congestion component is 81.4% of mean |LMP spread|; TH_NP15_GEN-APND above 63.1% of hours. Window limited by OASIS ~39-month retention. |
| BPAT - NEVP | price_spread_proxy | -0.034 | 569,040 | $2,156,662 | EIA ICE daily wholesale prices 2023 (volume-weighted peak) | Mid C Peak $82.66 vs Palo Verde Peak $78.87; NEVP approximated by Palo Verde; mapping approximate |
| PACW - CISO | price_spread_proxy | -0.157 | 74,572 | $706,197 | EIA ICE daily wholesale prices 2023 (volume-weighted peak) | PACW approximated by Mid C Peak $82.66 vs NP15 $73.19; hub-to-BA mapping approximate |
| BPAT - NWMT | structural_only | -0.122 | 7,221,314 | $0 |  |  |
| SOCO - FPL | structural_only | -0.208 | 3,527,415 | $0 |  |  |
| BPAT - LDWP | structural_only | -0.098 | 6,773,556 | $0 |  |  |
| BPAT - BANC | structural_only | -0.127 | 3,927,078 | $0 |  |  |
| TVA - SOCO | structural_only | -0.079 | 5,660,484 | $0 |  |  |
| BPAT - GRID | structural_only | -0.228 | 1,626,752 | $0 |  |  |
| CPLE - PJM | structural_only | -0.086 | 4,242,136 | $0 |  |  |
| BPAT - SCL | structural_only | -0.044 | 7,798,197 | $0 |  |  |
| BPAT - PSEI | structural_only | -0.018 | 16,049,993 | $0 |  |  |
| BPAT - DOPD | structural_only | -0.074 | 2,370,212 | $0 |  |  |
| BPAT - TPWR | structural_only | -0.044 | 3,599,272 | $0 |  |  |
| WACM - WALC | structural_only | -0.064 | 2,222,314 | $0 |  |  |
| AECI - SWPP | structural_only | -0.042 | 2,800,533 | $0 |  |  |
| NWMT - WAUW | structural_only | -0.119 | 494,475 | $0 |  |  |
| AECI - TVA | structural_only | -0.036 | 1,198,856 | $0 |  |  |
| SOCO - FPC | structural_only | -0.095 | 419,575 | $0 |  |  |
| PNM - GRID | structural_only | -0.018 | 2,078,483 | $0 |  |  |
| SPA - SWPP | structural_only | -0.000 | 1,512,521 | $0 |  |  |
