# CHPE Event Study - PJM-NYIS Seam

CHPE (1,250 MW HVDC Quebec->Queens) reached commercial operation
2026-05-13. Difference-in-differences on the NYISO DAM seam spread
vs the PJM proxy bus, 2025 as the seasonal control.

| Window | Dates | Days | Hours | Mean \|LBMP spread\| | Congestion component | NY above |
|---|---|---:|---:|---:|---:|---:|
| pre-2025 | 2025-04-13..2025-05-12 | 30 | 720 | $1.11 | $0.41 | 95.7% |
| post-2025 | 2025-05-13..2025-06-11 | 30 | 720 | $2.10 | $1.35 | 98.8% |
| pre-2026 | 2026-04-13..2026-05-12 | 30 | 720 | $2.64 | $1.42 | 97.4% |
| post-2026 | 2026-05-13..2026-06-11 | 30 | 720 | $3.24 | $2.05 | 97.8% |

**DiD congestion component: -0.31 $/MWh**
(LBMP spread DiD -0.39 $/MWh) - COMPRESSION beyond seasonality.

One month of post-COD data: screening-grade. Rerun with more post
months before adjusting the corridor's annual value.
