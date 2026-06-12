# Energy Solution Cards

## Summary

- Cards: **6**

## Cards

| Status | Geography | Value | Spread | Queue | Generic B/C | Recommended Solution | Next Action | Caveat |
|---|---|---:|---:|---:|---:|---|---|---|
| priority_solution_study | NYIS-PJM | $142,391,661/yr | $7.38/MWh | 85.5 GW active / 524.3 GW withdrawn | 0.43 | Use 2025 congestion economics to scope NY import/export relief, storage, and queue-rescue packages. | Rebuild congestion evidence and relief curves on the 2025 NYISO component spread, then price named projects. | Generic costs still do not clear B/C > 1; the value is now high enough for project-specific costing. |
| priority_solution_study | MISO-SWPP | $25,176,168/yr | $6.31/MWh | 156.5 GW active / 344.7 GW withdrawn | 0.35 | Target wind-belt transfer relief: transmission upgrades, storage on the export side, and queue rescue on the import side. | Tie CHAWATCHAPAT/Charlie Creek-Watford constraints to candidate upgrades and rerun relief curves on 2024 spread. | Screening uses MISO-side settlement evidence; SPP-side evidence corroborates but should not be double-counted. |
| methodology_validated_screen | CISO-SRP | $14,038,274/yr | $1.39/MWh | 68.0 GW active / 389.8 GW withdrawn | 0.08 | Use OASIS-corrected spreads for Western storage/transmission siting screens, not old ICE hub levels. | Replace generic benchmark costs with project-specific storage, flexible-load, or transmission estimates. | OASIS correction made this defensible but much smaller than the old hub-proxy headline. |
| methodology_validated_screen | BPAT-CISO | $6,059,449/yr | $1.11/MWh | 85.6 GW active / 393.6 GW withdrawn | 0.06 | Use OASIS-corrected spreads for Western storage/transmission siting screens, not old ICE hub levels. | Replace generic benchmark costs with project-specific storage, flexible-load, or transmission estimates. | OASIS correction made this defensible but much smaller than the old hub-proxy headline. |
| bounded_solution_screen | MISO-SOCO | $8,194,348/yr | $1.53/MWh | 261.9 GW active / 467.9 GW withdrawn | 0.09 | Keep as a Southeast import-boundary screen; use targeted price/constraint evidence before spending design effort. | Attach SOCO/neighbor settlement or planning evidence and compare to Right Kan Southeast bounds. | Value is smaller than PJM-NYIS and MISO-SWPP, but it anchors Southeast bounds. |
| watchlist_for_solution_screen | ERCO West-North hubs | $0/yr | $5.78/MWh | 0.0 GW active / 0.0 GW withdrawn | 0.00 | Run ERCOT-specific queue/site matching before ranking storage or transmission interventions. | Attach ERCOT queue and constraint evidence to the West-North spread trend. | Hub spread trend is directional; no BA tie gross-flow value is attached. |

## Detail

### NYIS-PJM

- Status: **priority_solution_study**
- Evidence: NYISO DAM zonal LBMP 2023 (mis.nyiso.com; hourly NYCA internal-zone mean vs NYISO PJM proxy bus); NYISO DAM zonal LBMP 2023 settlement components (mis.nyiso.com; NYCA internal-zone mean vs PJM proxy bus)
- Trend: 2023 $1.53/MWh -> 2024 $2.02/MWh -> 2025 $7.38/MWh (4.8x over observed window).
- Constraints: PJM:NOTTINGH230 KV  2-3 (6,025 h, severity 353,557); PJM:LENOX-NMESHOPP NML 1090     B  115 KV (1,847 h, severity 227,804); PJM:GRACETON230 KV  GRA-SAF (3,339 h, severity 130,754); PJM:Chicago-Praxair3 138 kV l/o Wilton Center-Dumont 765 kV (661 h, severity 120,695); PJM:Turkey Hill-Hilgard 138 kV l/o Prairie State-Mt Vernon 345 kV (1,065 h, severity 118,169)
- Best generic intervention: transmission_capacity at 50 MW, B/C 0.43
- Recommended solution: Use 2025 congestion economics to scope NY import/export relief, storage, and queue-rescue packages.
- Next action: Rebuild congestion evidence and relief curves on the 2025 NYISO component spread, then price named projects.
- Caveat: Generic costs still do not clear B/C > 1; the value is now high enough for project-specific costing.

### MISO-SWPP

- Status: **priority_solution_study**
- Evidence: MISO DA ex-post LMP (docs.misoenergy.org; ARKANSAS.HUB vs SWPP interface, 2023-01-01..2023-12-31)
- Trend: 2023 $4.74/MWh -> 2024 $6.31/MWh (1.3x over observed window).
- Constraints: MISO:CHAR_CK-WATFORD FLO PATINGATE-CHARLIE CK (5,138 h, severity 1,069,182); SPP:CHAWATCHAPAT (5,951 h, severity 895,951); MISO:MORRISOT-GRANTCO FLO HANK-WAP+WAP TR2 (2,453 h, severity 654,610); MISO:FORMAN TR12 FLO WAHPETON-HANKINSON (1,607 h, severity 389,783); SPP:OSAWEBCLESOO (2,078 h, severity 360,524); SPP:TMP499_26328 (2,074 h, severity 316,737)
- Best generic intervention: transmission_capacity at 50 MW, B/C 0.35
- Recommended solution: Target wind-belt transfer relief: transmission upgrades, storage on the export side, and queue rescue on the import side.
- Next action: Tie CHAWATCHAPAT/Charlie Creek-Watford constraints to candidate upgrades and rerun relief curves on 2024 spread.
- Caveat: Screening uses MISO-side settlement evidence; SPP-side evidence corroborates but should not be double-counted.

### CISO-SRP

- Status: **methodology_validated_screen**
- Evidence: CAISO OASIS PRC_LMP DAM v12 (TH_SP15_GEN-APND vs PALOVRDE_ASR-APND, 2023-04-01..2024-01-01)
- Trend: 2023 $1.39/MWh.
- Constraints: not attached
- Best generic intervention: transmission_capacity at 50 MW, B/C 0.08
- Recommended solution: Use OASIS-corrected spreads for Western storage/transmission siting screens, not old ICE hub levels.
- Next action: Replace generic benchmark costs with project-specific storage, flexible-load, or transmission estimates.
- Caveat: OASIS correction made this defensible but much smaller than the old hub-proxy headline.

### BPAT-CISO

- Status: **methodology_validated_screen**
- Evidence: CAISO OASIS PRC_LMP DAM v12 (TH_NP15_GEN-APND vs MALIN_5_N101, 2023-04-01..2024-01-01)
- Trend: 2023 $1.11/MWh.
- Constraints: not attached
- Best generic intervention: transmission_capacity at 50 MW, B/C 0.06
- Recommended solution: Use OASIS-corrected spreads for Western storage/transmission siting screens, not old ICE hub levels.
- Next action: Replace generic benchmark costs with project-specific storage, flexible-load, or transmission estimates.
- Caveat: OASIS correction made this defensible but much smaller than the old hub-proxy headline.

### MISO-SOCO

- Status: **bounded_solution_screen**
- Evidence: MISO DA ex-post LMP (docs.misoenergy.org; MS.HUB vs SOCO interface, 2023-01-01..2023-12-31)
- Trend: 2023 $1.35/MWh -> 2024 $1.53/MWh (1.1x over observed window).
- Constraints: MISO:CHAR_CK-WATFORD FLO PATINGATE-CHARLIE CK (5,138 h, severity 1,069,182); MISO:MORRISOT-GRANTCO FLO HANK-WAP+WAP TR2 (2,453 h, severity 654,610); MISO:FORMAN TR12 FLO WAHPETON-HANKINSON (1,607 h, severity 389,783); MISO:SWAN LK-WILMARTH FLO HELENAMN-SHEASLK (1,924 h, severity 218,268); MISO:CREE-CRES2 FLO CRESTON-SUMMITLK N (829 h, severity 207,932)
- Best generic intervention: transmission_capacity at 50 MW, B/C 0.09
- Recommended solution: Keep as a Southeast import-boundary screen; use targeted price/constraint evidence before spending design effort.
- Next action: Attach SOCO/neighbor settlement or planning evidence and compare to Right Kan Southeast bounds.
- Caveat: Value is smaller than PJM-NYIS and MISO-SWPP, but it anchors Southeast bounds.

### ERCO West-North hubs

- Status: **watchlist_for_solution_screen**
- Evidence: ERCOT DAM hub spread series
- Trend: 2023 $4.94/MWh -> 2025 $5.78/MWh.
- Constraints: not attached
- Best generic intervention: not_evaluated at 0 MW, B/C 0.00
- Recommended solution: Run ERCOT-specific queue/site matching before ranking storage or transmission interventions.
- Next action: Attach ERCOT queue and constraint evidence to the West-North spread trend.
- Caveat: Hub spread trend is directional; no BA tie gross-flow value is attached.

