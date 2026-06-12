# Grid Methodology Report

## Summary

- Correction 2-cells: **2**
- Mean proxy overstatement: **8.0x**
- Right Kan ties reviewed: **6**
- Mined methodology axioms: **1**
- Proxy warnings: **4**

## Evidence Correction 2-Cells

| Tie | Source Method | Target Method | Source $/MWh | Target $/MWh | Ratio | Avoided Overclaim |
|---|---|---|---:|---:|---:|---:|
| CISO-SRP | hub_daily_overlap_proxy | oasis_settlement_spread | 14.03 | 1.55 | 9.0x | $126,006,082 |
| BPAT-CISO | hub_daily_overlap_proxy | oasis_settlement_spread | 9.47 | 1.37 | 6.9x | $44,230,597 |

## Right Kan Bounds

Bounds use the minimum adjacent priced spread as the limit/meet. They are upper-screening bounds for unpriced structural ties, not measured cost.

| Tie | Status | Bound $/MWh | Bound Value | Adjacent Measurements |
|---|---|---:|---:|---|
| AECI-SWPP | bounded | 4.74 | $13,274,526 | MISO-SWPP $4.74/MWh |
| SOCO-TVA | bounded | 1.35 | $7,641,653 | MISO-SOCO $1.35/MWh |
| CPLE-PJM | bounded | 1.53 | $6,477,501 | NYIS-PJM $1.53/MWh |
| FPL-SOCO | bounded | 1.35 | $4,762,010 | MISO-SOCO $1.35/MWh |
| FPC-SOCO | bounded | 1.35 | $566,426 | MISO-SOCO $1.35/MWh |
| AECI-TVA | unbounded_no_priced_neighbor | 0.00 | $0 |  |

## Mined Axioms

### hub_level_proxy_overstates_hourly_seam_spread

- Template: `hub_level_proxy(tie) and no_settlement_2cell(tie) -> screening_only(tie)`
- Support: **2** correction episodes
- Agreement rate: **100%**
- Average confidence: **0.80**
- Description: Annual or daily hub-level price proxies repeatedly overstated hourly settlement seam spreads. Future hub proxies require a settlement or nodal evidence 2-cell before being treated as actionable congestion value.

## Proxy Warnings

| Tie | Method | Status | Warning |
|---|---|---|---|
| CISO-SRP | hub_daily_overlap_proxy | resolved_by_2cell | Hub-level proxy has a settlement correction 2-cell; keep the settlement row as the actionable value. |
| BPAT-CISO | hub_daily_overlap_proxy | resolved_by_2cell | Hub-level proxy has a settlement correction 2-cell; keep the settlement row as the actionable value. |
| BPAT-NEVP | hub_daily_overlap_proxy | screening_only | Hub-level proxy has no settlement correction in this report; keep it as screening evidence only. |
| CISO-PACW | hub_daily_overlap_proxy | screening_only | Hub-level proxy has no settlement correction in this report; keep it as screening evidence only. |
