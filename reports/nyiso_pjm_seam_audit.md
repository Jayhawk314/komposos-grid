# NYISO PJM Seam Evidence Audit

## Summary

- Hours observed: **8,759**
- Mean absolute LBMP spread: **$2.01/MWh**
- Mean absolute congestion-component spread: **$1.53/MWh**
- Mean absolute loss-component spread: **$0.52/MWh**
- Congestion component / LBMP spread: **75.8%**
- NYCA LBMP above PJM proxy: **94.3%**

## Evidence Row

| BA Tie | Method | Mean LBMP Spread | Mean Congestion Component | Hours | Notes |
|---|---|---:|---:|---:|---|
| PJM - NYIS | lmp_component_proxy | $2.01/MWh | $1.53/MWh | 8,759 | Uses NYISO hourly settlement congestion component, not only annual hub price level. Congestion component is 75.8% of mean absolute LBMP spread; NYCA LBMP above PJM proxy 94.3% of hours. |
