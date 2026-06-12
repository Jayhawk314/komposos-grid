# Grid Action Portfolio

## Summary

- Actions: **10**
- Status mix: **{'attach_evidence': 1, 'policy_design': 1, 'ready_for_scoping': 2, 'review_required': 1, 'validate_proxy': 5}**
- Measured value: **$0**
- Proxy value: **$52,421,825**
- Upper-bound value: **$172,470,248**
- Reported value: **$224,892,073**

## Actions

| Status | Action | Geography | Evidence | Quantity | Reported Value | Next Step | Caveat |
|---|---|---|---|---:|---:|---|---|
| ready_for_scoping | Scope CAISO curtailment reduction package | CISO | measured | 2,659,525.80 MWh curtailed renewable energy | $172,470,248 | Design storage, flexible-load, and transmission screens around CAISO curtailment windows. | Dollar value is an annual-average-price upper bound, not realized market value. |
| ready_for_scoping | Prioritize reliability hardening in highest-burden states | USVI, Maine, Puerto Rico, Michigan, Kentucky | measured | 1,059,209,999.25 customer-hours |  | Use EAGLE-I/MCC burden rankings to select outage-hardening and distribution-resilience targets. | Customer-hour burden is not monetized here. |
| policy_design | Target queue reform at IA-stage mediators | US interconnection queues | measured | 0.83 withdrawal share of decided projects |  | Study IA-executed completion structure and failure-path IA statuses before proposing process reform. | Mediators are descriptive, not causal proof. |
| validate_proxy | Validate proxy congestion value for PJM-NYIS | PJM-NYIS | measured_proxy | 19,294,263 MWh gross interchange | $29,461,244 | Replace component-spread proxy with direct congestion-cost or flow-attribution evidence. | Component spread is stronger than hub price evidence, but still not direct settlement cost. |
| validate_proxy | Validate proxy congestion value for CISO-SRP | CISO-SRP | measured_proxy | 10,099,478 MWh gross interchange | $14,038,274 | Replace component-spread proxy with direct congestion-cost or flow-attribution evidence. | Component spread is stronger than hub price evidence, but still not direct settlement cost. |
| validate_proxy | Validate proxy congestion value for BPAT-CISO | BPAT-CISO | measured_proxy | 5,458,963 MWh gross interchange | $6,059,449 | Replace component-spread proxy with direct congestion-cost or flow-attribution evidence. | Component spread is stronger than hub price evidence, but still not direct settlement cost. |
| validate_proxy | Validate proxy congestion value for BPAT-NEVP | BPAT-NEVP | measured_proxy | 569,040 MWh gross interchange | $2,156,662 | Replace hub/price-spread proxy with nodal LMP or direct congestion-cost evidence. | Proxy value depends on hub-to-BA mapping and should not be treated as direct settlement cost. |
| validate_proxy | Validate proxy congestion value for PACW-CISO | PACW-CISO | measured_proxy | 74,572 MWh gross interchange | $706,197 | Replace hub/price-spread proxy with nodal LMP or direct congestion-cost evidence. | Proxy value depends on hub-to-BA mapping and should not be treated as direct settlement cost. |
| review_required | Review BA footprint correction candidates | US balancing authorities | validated_hypothesis | 59,350,065 MWh BA absolute-error reduction |  | Have a domain reviewer approve, reject, or defer rows in ba_review_template.csv. | Not an official BA registration change until reviewed. |
| attach_evidence | Attach evidence to remaining structural bottlenecks | BPAT-NWMT, BPAT-LDWP, TVA-SOCO, MISO-SOCO | structural_only | 38,082,266 MWh gross interchange under review |  | Pull nodal LMP, congestion-cost, outage, or planning evidence for the remaining corridors. | Topology-only evidence is not counted as measured waste. |
