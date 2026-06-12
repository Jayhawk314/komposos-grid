# Congestion Evidence Report

## Result

- Structural bottlenecks: **25**
- Evidence matched: **5**
- Measured/proxy claims: **5**
- Estimated measured/proxy value: **$225,692,599**

## Ranked Claims

| Tie | Evidence | Curvature | Gross MWh | Estimated Value | Source | Notes |
|---|---|---:|---:|---:|---|---|
| CISO - SRP | price_spread_proxy | -0.036 | 10,099,478 | $141,660,273 | EIA ICE daily wholesale prices 2023 + EIA-930 interchange | SP15 EZ Gen DA LMP Peak $64.85 vs Palo Verde Peak $78.87; daily overlap mean |spread| $15.58/MWh; flow-weighted alignment 39.0%; flow/price alignment is weak. |
| BPAT - CISO | price_spread_proxy | -0.085 | 5,458,963 | $51,709,377 | EIA ICE daily wholesale prices 2023 + EIA-930 interchange | Mid C Peak $82.66 vs NP15 EZ Gen DA LMP Peak $73.19; daily overlap mean |spread| $32.90/MWh; flow-weighted alignment 58.9%; flow/price alignment is mixed. NP15 volume is thin, so keep this as a hub-screening proxy. |
| PJM - NYIS | lmp_component_proxy | -0.107 | 19,294,263 | $29,461,244 | NYISO DAM zonal LBMP 2023 settlement components (mis.nyiso.com; NYCA internal-zone mean vs PJM proxy bus) | Uses NYISO hourly settlement congestion component, not only annual hub price level. Congestion component is 75.8% of mean absolute LBMP spread; NYCA LBMP above PJM proxy 94.3% of hours. |
| BPAT - NEVP | price_spread_proxy | -0.034 | 569,040 | $2,155,331 | EIA ICE daily wholesale prices 2023 + EIA-930 interchange | Mid C Peak $82.66 vs Palo Verde Peak $78.87; daily overlap mean |spread| $24.02/MWh; flow-weighted alignment 45.3%; flow/price alignment is mixed. NEVP is approximated by Palo Verde. |
| PACW - CISO | price_spread_proxy | -0.157 | 74,572 | $706,374 | EIA ICE daily wholesale prices 2023 + EIA-930 interchange | Mid C Peak $82.66 vs NP15 EZ Gen DA LMP Peak $73.19; daily overlap mean |spread| $32.90/MWh; flow-weighted alignment 82.5%; flow/price alignment is directionally supportive. PACW and CISO are approximated by Mid C and NP15. |
| BPAT - NWMT | structural_only | -0.122 | 7,221,314 | $0 |  |  |
| MISO - SOCO | structural_only | -0.151 | 5,355,783 | $0 |  |  |
| SOCO - FPL | structural_only | -0.208 | 3,527,415 | $0 |  |  |
| BPAT - LDWP | structural_only | -0.098 | 6,773,556 | $0 |  |  |
| BPAT - BANC | structural_only | -0.127 | 3,927,078 | $0 |  |  |
| TVA - SOCO | structural_only | -0.079 | 5,660,484 | $0 |  |  |
| MISO - SWPP | structural_only | -0.095 | 3,989,884 | $0 |  |  |
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
