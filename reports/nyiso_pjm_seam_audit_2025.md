# NYISO PJM Seam Evidence Audit

## Summary

- Hours observed: **8,759**
- Mean absolute LBMP spread: **$9.03/MWh**
- Mean absolute congestion-component spread: **$7.38/MWh**
- Mean absolute loss-component spread: **$1.74/MWh**
- Congestion component / LBMP spread: **81.7%**
- NYCA LBMP above PJM proxy: **97.9%**

## Evidence Row

| BA Tie | Method | Mean LBMP Spread | Mean Congestion Component | Hours | Notes |
|---|---|---:|---:|---:|---|
| PJM - NYIS | lmp_component_proxy | $9.03/MWh | $7.38/MWh | 8,759 | Uses NYISO hourly settlement congestion component, not only annual hub price level. Congestion component is 81.7% of mean absolute LBMP spread; NYCA LBMP above PJM proxy 97.9% of hours. |
