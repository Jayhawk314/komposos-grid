# California Energy Vision Audit

Generated: 2026-06-06

## What This Is

This report turns the WESyS audit into an energy alignment view: physical hotspots, human incentive bottlenecks, and candidate contract or constraint designs that could make repair practical.

This is a prototype report. The dollar values are planning estimates, not validated savings claims.

## Data Loaded

- Input workbook: `data/external/WESyS-Model-master/wesys/data/WESyS_Default_Inputs.xlsx`
- Sheets: Global-Inputs, CA-LF, CA-POTW, CA-CAFO, ROTUS-LF, ROTUS-POTW, ROTUS-CAFO, FU
- Snapshot year: 2026
- Resource nodes: 15
- Infrastructure pathways: 54

## System Health

- Algebraic connectivity: 0.0000
- Component count: 4
- Status: fragmented into 4 components

Interpretation: a fragmented or weakly coupled graph suggests the model has separated energy islands. That can indicate physical fragmentation, data partitioning, or missing cross-system links that should be checked.

## Coherence Findings

- Raw coherence gaps: 156
- Raw gap-weighted exposure: 4043 facility-equivalents
- Rolled-up conservative exposure: 1148 facility-equivalents
- Raw prototype savings estimate: $202.15M per year
- Conservative rolled-up estimate: $57.40M per year
- Savings assumption: $50.0K per facility-equivalent per year

The raw estimate counts every detected gap. The conservative estimate groups repeated findings by resource, technology, and gap type, then uses the largest facility exposure in each group. The conservative number is better for early conversations.

## Priority Hotspots

### 1. ROTUS LF -> Elec

- Gap type: `interchange_failure`
- Loss class: `grid_instability`
- Alignment tier: `high-priority prototype`
- Raw repeated gaps: 4
- Raw exposure: 1600 facility-equivalents
- Conservative exposure: 400 facility-equivalents
- Conservative prototype savings: $20.00M per year

Actors:

- facility operator: maintains the asset and executes repairs; interest: uptime, manageable maintenance, lower operating risk; constraint: capital budget, staffing, disruption risk
- city or public authority: sets public goals and may coordinate funding; interest: emissions reduction, resilience, public value; constraint: procurement rules, budget cycles, proof requirements
- community: receives local health, cost, and reliability effects; interest: lower pollution, fair rates, visible benefits; constraint: limited technical visibility and negotiating power
- utility: interconnects and values grid reliability; interest: stable generation, avoided congestion, reliability; constraint: tariff rules, interconnection queues, ratepayer protection

Activity diagnosis: landfill operators, utilities, city climate staff, and nearby communities may not share the same object of action. The operator sees maintenance and uptime; the city sees methane and emissions; the utility or fuel buyer sees system value.

Game diagnosis: high shared value suggests a coordination problem. Multiple actors can benefit, but no single actor may rationally carry the full cost.

Contract path: use a shared-savings or performance-based interconnection agreement between facility, city, and utility. Pay only against measured efficiency, reliability, or emissions improvements.

Constraints to design around: meter before and after repair; protect uptime; cap public exposure; record maintenance cost changes; require independent measurement and verification; verify process sequencing before capital spend.

Measurement needs: baseline throughput; energy input and useful output; downtime and maintenance events; before/after operating cost; methane capture or destruction rate; interconnection availability; exported kWh.

### 2. ROTUS CAFO -> Elec

- Gap type: `interchange_failure`
- Loss class: `grid_instability`
- Alignment tier: `high-priority prototype`
- Raw repeated gaps: 3
- Raw exposure: 396 facility-equivalents
- Conservative exposure: 132 facility-equivalents
- Conservative prototype savings: $6.60M per year

Actors:

- facility operator: maintains the asset and executes repairs; interest: uptime, manageable maintenance, lower operating risk; constraint: capital budget, staffing, disruption risk
- city or public authority: sets public goals and may coordinate funding; interest: emissions reduction, resilience, public value; constraint: procurement rules, budget cycles, proof requirements
- community: receives local health, cost, and reliability effects; interest: lower pollution, fair rates, visible benefits; constraint: limited technical visibility and negotiating power
- utility: interconnects and values grid reliability; interest: stable generation, avoided congestion, reliability; constraint: tariff rules, interconnection queues, ratepayer protection
- farm producer: hosts the waste stream and operational process; interest: margin protection, odor control, operational simplicity; constraint: thin margins, biological process risk, labor limits

Activity diagnosis: farm operators may face thin margins and operational risk, while public value comes from methane reduction and local resilience.

Game diagnosis: high shared value suggests a coordination problem. Multiple actors can benefit, but no single actor may rationally carry the full cost.

Contract path: use a shared-savings or performance-based interconnection agreement between facility, city, and utility. Pay only against measured efficiency, reliability, or emissions improvements.

Constraints to design around: meter before and after repair; protect uptime; cap public exposure; record maintenance cost changes; require independent measurement and verification; verify process sequencing before capital spend.

Measurement needs: baseline throughput; energy input and useful output; downtime and maintenance events; before/after operating cost; methane capture or destruction rate; interconnection availability; exported kWh.

### 3. ROTUS LF -> CNG

- Gap type: `interchange_failure`
- Loss class: `grid_instability`
- Alignment tier: `high-priority prototype`
- Raw repeated gaps: 4
- Raw exposure: 472 facility-equivalents
- Conservative exposure: 118 facility-equivalents
- Conservative prototype savings: $5.90M per year

Actors:

- facility operator: maintains the asset and executes repairs; interest: uptime, manageable maintenance, lower operating risk; constraint: capital budget, staffing, disruption risk
- city or public authority: sets public goals and may coordinate funding; interest: emissions reduction, resilience, public value; constraint: procurement rules, budget cycles, proof requirements
- community: receives local health, cost, and reliability effects; interest: lower pollution, fair rates, visible benefits; constraint: limited technical visibility and negotiating power
- fuel offtaker: buys or credits recovered gas/fuel; interest: reliable volume, quality, low-carbon attributes; constraint: quality specs, delivery risk, credit verification

Activity diagnosis: landfill operators, utilities, city climate staff, and nearby communities may not share the same object of action. The operator sees maintenance and uptime; the city sees methane and emissions; the utility or fuel buyer sees system value.

Game diagnosis: high shared value suggests a coordination problem. Multiple actors can benefit, but no single actor may rationally carry the full cost.

Contract path: use an offtake or fuel-credit sharing contract that splits measured gas-quality and throughput gains between the facility and buyer.

Constraints to design around: meter before and after repair; protect uptime; cap public exposure; record maintenance cost changes; require independent measurement and verification; verify process sequencing before capital spend.

Measurement needs: baseline throughput; energy input and useful output; downtime and maintenance events; before/after operating cost; methane capture or destruction rate; fuel quality; delivered fuel volume.

### 4. ROTUS CAFO -> PNG

- Gap type: `interchange_failure`
- Loss class: `grid_instability`
- Alignment tier: `high-priority prototype`
- Raw repeated gaps: 3
- Raw exposure: 330 facility-equivalents
- Conservative exposure: 110 facility-equivalents
- Conservative prototype savings: $5.50M per year

Actors:

- facility operator: maintains the asset and executes repairs; interest: uptime, manageable maintenance, lower operating risk; constraint: capital budget, staffing, disruption risk
- city or public authority: sets public goals and may coordinate funding; interest: emissions reduction, resilience, public value; constraint: procurement rules, budget cycles, proof requirements
- community: receives local health, cost, and reliability effects; interest: lower pollution, fair rates, visible benefits; constraint: limited technical visibility and negotiating power
- fuel offtaker: buys or credits recovered gas/fuel; interest: reliable volume, quality, low-carbon attributes; constraint: quality specs, delivery risk, credit verification
- farm producer: hosts the waste stream and operational process; interest: margin protection, odor control, operational simplicity; constraint: thin margins, biological process risk, labor limits

Activity diagnosis: farm operators may face thin margins and operational risk, while public value comes from methane reduction and local resilience.

Game diagnosis: high shared value suggests a coordination problem. Multiple actors can benefit, but no single actor may rationally carry the full cost.

Contract path: use a staged energy service contract: small measurement phase, independent verification, then shared verified savings after repair.

Constraints to design around: meter before and after repair; protect uptime; cap public exposure; record maintenance cost changes; require independent measurement and verification; verify process sequencing before capital spend.

Measurement needs: baseline throughput; energy input and useful output; downtime and maintenance events; before/after operating cost; methane capture or destruction rate; fuel quality; delivered fuel volume.

### 5. ROTUS LF -> PNG

- Gap type: `interchange_failure`
- Loss class: `grid_instability`
- Alignment tier: `medium-priority prototype`
- Raw repeated gaps: 4
- Raw exposure: 284 facility-equivalents
- Conservative exposure: 71 facility-equivalents
- Conservative prototype savings: $3.55M per year

Actors:

- facility operator: maintains the asset and executes repairs; interest: uptime, manageable maintenance, lower operating risk; constraint: capital budget, staffing, disruption risk
- city or public authority: sets public goals and may coordinate funding; interest: emissions reduction, resilience, public value; constraint: procurement rules, budget cycles, proof requirements
- community: receives local health, cost, and reliability effects; interest: lower pollution, fair rates, visible benefits; constraint: limited technical visibility and negotiating power
- fuel offtaker: buys or credits recovered gas/fuel; interest: reliable volume, quality, low-carbon attributes; constraint: quality specs, delivery risk, credit verification

Activity diagnosis: landfill operators, utilities, city climate staff, and nearby communities may not share the same object of action. The operator sees maintenance and uptime; the city sees methane and emissions; the utility or fuel buyer sees system value.

Game diagnosis: moderate value suggests a bargaining problem. The repair may need bundling, a low-friction maintenance window, or a cost-share trigger.

Contract path: use a measured-efficiency service contract with a small discovery phase, then share verified savings after repair.

Constraints to design around: meter before and after repair; protect uptime; cap public exposure; record maintenance cost changes; verify process sequencing before capital spend.

Measurement needs: baseline throughput; energy input and useful output; downtime and maintenance events; before/after operating cost; methane capture or destruction rate; fuel quality; delivered fuel volume.

### 6. CA LF -> Elec

- Gap type: `interchange_failure`
- Loss class: `grid_instability`
- Alignment tier: `medium-priority prototype`
- Raw repeated gaps: 3
- Raw exposure: 177 facility-equivalents
- Conservative exposure: 59 facility-equivalents
- Conservative prototype savings: $2.95M per year

Actors:

- facility operator: maintains the asset and executes repairs; interest: uptime, manageable maintenance, lower operating risk; constraint: capital budget, staffing, disruption risk
- city or public authority: sets public goals and may coordinate funding; interest: emissions reduction, resilience, public value; constraint: procurement rules, budget cycles, proof requirements
- community: receives local health, cost, and reliability effects; interest: lower pollution, fair rates, visible benefits; constraint: limited technical visibility and negotiating power
- utility: interconnects and values grid reliability; interest: stable generation, avoided congestion, reliability; constraint: tariff rules, interconnection queues, ratepayer protection

Activity diagnosis: landfill operators, utilities, city climate staff, and nearby communities may not share the same object of action. The operator sees maintenance and uptime; the city sees methane and emissions; the utility or fuel buyer sees system value.

Game diagnosis: moderate value suggests a bargaining problem. The repair may need bundling, a low-friction maintenance window, or a cost-share trigger.

Contract path: use a shared-savings or performance-based interconnection agreement between facility, city, and utility. Pay only against measured efficiency, reliability, or emissions improvements.

Constraints to design around: meter before and after repair; protect uptime; cap public exposure; record maintenance cost changes; verify process sequencing before capital spend.

Measurement needs: baseline throughput; energy input and useful output; downtime and maintenance events; before/after operating cost; methane capture or destruction rate; interconnection availability; exported kWh.

### 7. ROTUS CAFO -> CNG

- Gap type: `interchange_failure`
- Loss class: `grid_instability`
- Alignment tier: `medium-priority prototype`
- Raw repeated gaps: 3
- Raw exposure: 162 facility-equivalents
- Conservative exposure: 54 facility-equivalents
- Conservative prototype savings: $2.70M per year

Actors:

- facility operator: maintains the asset and executes repairs; interest: uptime, manageable maintenance, lower operating risk; constraint: capital budget, staffing, disruption risk
- city or public authority: sets public goals and may coordinate funding; interest: emissions reduction, resilience, public value; constraint: procurement rules, budget cycles, proof requirements
- community: receives local health, cost, and reliability effects; interest: lower pollution, fair rates, visible benefits; constraint: limited technical visibility and negotiating power
- fuel offtaker: buys or credits recovered gas/fuel; interest: reliable volume, quality, low-carbon attributes; constraint: quality specs, delivery risk, credit verification
- farm producer: hosts the waste stream and operational process; interest: margin protection, odor control, operational simplicity; constraint: thin margins, biological process risk, labor limits

Activity diagnosis: farm operators may face thin margins and operational risk, while public value comes from methane reduction and local resilience.

Game diagnosis: moderate value suggests a bargaining problem. The repair may need bundling, a low-friction maintenance window, or a cost-share trigger.

Contract path: use an offtake or fuel-credit sharing contract that splits measured gas-quality and throughput gains between the facility and buyer.

Constraints to design around: meter before and after repair; protect uptime; cap public exposure; record maintenance cost changes; verify process sequencing before capital spend.

Measurement needs: baseline throughput; energy input and useful output; downtime and maintenance events; before/after operating cost; methane capture or destruction rate; fuel quality; delivered fuel volume.

### 8. CA CAFO -> Elec

- Gap type: `interchange_failure`
- Loss class: `grid_instability`
- Alignment tier: `medium-priority prototype`
- Raw repeated gaps: 3
- Raw exposure: 129 facility-equivalents
- Conservative exposure: 43 facility-equivalents
- Conservative prototype savings: $2.15M per year

Actors:

- facility operator: maintains the asset and executes repairs; interest: uptime, manageable maintenance, lower operating risk; constraint: capital budget, staffing, disruption risk
- city or public authority: sets public goals and may coordinate funding; interest: emissions reduction, resilience, public value; constraint: procurement rules, budget cycles, proof requirements
- community: receives local health, cost, and reliability effects; interest: lower pollution, fair rates, visible benefits; constraint: limited technical visibility and negotiating power
- utility: interconnects and values grid reliability; interest: stable generation, avoided congestion, reliability; constraint: tariff rules, interconnection queues, ratepayer protection
- farm producer: hosts the waste stream and operational process; interest: margin protection, odor control, operational simplicity; constraint: thin margins, biological process risk, labor limits

Activity diagnosis: farm operators may face thin margins and operational risk, while public value comes from methane reduction and local resilience.

Game diagnosis: moderate value suggests a bargaining problem. The repair may need bundling, a low-friction maintenance window, or a cost-share trigger.

Contract path: use a shared-savings or performance-based interconnection agreement between facility, city, and utility. Pay only against measured efficiency, reliability, or emissions improvements.

Constraints to design around: meter before and after repair; protect uptime; cap public exposure; record maintenance cost changes; verify process sequencing before capital spend.

Measurement needs: baseline throughput; energy input and useful output; downtime and maintenance events; before/after operating cost; methane capture or destruction rate; interconnection availability; exported kWh.

## Alignment Roadmap

1. Validate whether each top hotspot is a physical issue, a model partition, or a missing data link.
2. Identify payer, beneficiary, maintainer, regulator, and community for each hotspot.
3. Choose the smallest contract design that aligns those actors.
4. Add measurement before making strong savings claims.
5. Feed measured outcomes back into WESyS assumptions.

## Limits

- Facility counts are used as prototype exposure weights.
- The current coherence scan can emit repeated raw gaps for the same resource pathway.
- Contract recommendations are templates, not legal advice.
- Savings estimates need measured energy, maintenance, emissions, and reliability data before becoming audit-grade claims.

## Next Implementation Targets

- Add actor templates for LF, POTW, CAFO, utility, city, and community.
- Attach actual WESyS energy units where available instead of facility count proxies.
- Store measured repair outcomes and compare them with predicted value.
- Produce a community-facing version that explains energy flows in plain language.
