# AI-Energy Matching Audit (KOMPOSOS-WESyS)

Generated: 2026-06-06

## What This Is

A reframing of WESyS around the 2026 AI energy dilemma. The bottleneck is not generation — it is interconnection and allocation. Stranded generation runs at partial utilization while AI load waits years to connect. This audit treats that as a categorical matching and contract problem: which stranded generator can energize which flexible AI load, and what agreement would make the match rational.

The facilities below are calibrated to real 2026 figures and announced deals (see Provenance), but they are not a live queue export. Replace the data file with an ISO/RTO queue + EIA-860 utilization export for a real audit. Every value figure is an explicit hypothesis, not a validated claim.

## Real-World Context

- U.S. interconnection queue (end 2025): 2060 GW
- ERCOT large-load queue: 226 GW (up from 63 GW a year prior)
- ERCOT solar+storage share of queue: 77%

## Data Loaded

- Stranded generators: 6  (total available headroom: 3509 MW)
- AI data-center loads: 6  (total demand: 2530 MW)
- Feasible couplings found (score >= 0.45): 8

## System Health (coupling graph)

- Algebraic connectivity (Fiedler): 0.0000
- Connected components: 5

Interpretation: a high component count means loads and generators sit on separate islands with no feasible coupling between them — the structural signature of the allocation failure.

## Finding

- Demand that can be served from stranded headroom: **1855 of 2530 MW** (73%)
- Matches proposed: 5
- Loads left stranded (no feasible in-region match): 1

## Value Hypothesis

The value here is *time-to-power*, not a fabricated savings number. Each match lets a load energize on an existing interconnection — months instead of a multi-year queue — while turning an underused asset into revenue. The unit to validate is **MW energized x queue-years avoided**, confirmed only after a real agreement and meter.

## Proposed Matches

### 1. Aging Coal Unit (low capacity factor)  ->  AI Campus (Susquehanna-style)

- Region: PJM-West
- Match score (coupling confidence): 0.95
- MW served from stranded headroom: 480 of 480 needed
- Load flexibility (interruptible share): 35%
- Queue-years potentially avoided: ~5
- Alignment tier: `high-priority prototype`

Actors:

- AI operator / hyperscaler: needs power in months not years; will trade flexibility for speed; constraint: uptime SLA, capex, board timeline
- stranded-generator owner (coal): holds an underused interconnection and asset; wants revenue; constraint: existing PPA terms, ramp limits, fuel/weather availability
- utility / ISO-RTO: owns the interconnection queue and reliability; constraint: queue rules, ratepayer protection, deliverability
- regulator / PUC: protects ratepayers and equity; constraint: cost-allocation rules, who pays for upgrades
- local community / ratepayers: bears rate and reliability effects; constraint: limited visibility and negotiating power

Activity diagnosis: the actor who can energize the load fast (the stranded generator) is not the actor who captures the AI revenue, and the utility that controls the queue captures neither — so the match that is obviously good for the system is nobody's job by default.

Game diagnosis: high shared value, classic coordination failure: the generator, the AI operator, and grid reliability all gain, but first-come-first-served queue rules and split cost-allocation mean no single actor will assemble the deal. Queue-stuffing by speculative projects makes it worse.

Contract path: co-locate behind the existing interconnection: a curtailable-load service agreement where the AI operator firms up to the generator's reliable output and curtails the flexible portion on the operator's signal, in exchange for energizing on the generator's existing queue position. Share the queue-skip value via a capacity payment to the generator.

Constraints to design around: firm only the non-flexible MW; price the interruptible MW separately; no net reliability reduction for existing ratepayers; meter delivered MWh and curtailment events before any value claim; cap ratepayer-funded upgrades; allocate deliverability cost to the beneficiary; respect the generator's existing PPA and ramp limits.

Measurement needs: delivered MWh and time-to-power (months saved vs. queue baseline); curtailment hours actually called and honored; generator utilization before/after; deliverability headroom on the shared interconnection.

### 2. Underused Gas Peaker Fleet  ->  Inference Cluster (24/7)

- Region: ERCOT
- Match score (coupling confidence): 0.98
- MW served from stranded headroom: 400 of 400 needed
- Load flexibility (interruptible share): 15%
- Queue-years potentially avoided: ~4
- Alignment tier: `high-priority prototype`

Actors:

- AI operator / hyperscaler: needs power in months not years; will trade flexibility for speed; constraint: uptime SLA, capex, board timeline
- stranded-generator owner (gas): holds an underused interconnection and asset; wants revenue; constraint: existing PPA terms, ramp limits, fuel/weather availability
- utility / ISO-RTO: owns the interconnection queue and reliability; constraint: queue rules, ratepayer protection, deliverability
- regulator / PUC: protects ratepayers and equity; constraint: cost-allocation rules, who pays for upgrades
- local community / ratepayers: bears rate and reliability effects; constraint: limited visibility and negotiating power

Activity diagnosis: the actor who can energize the load fast (the stranded generator) is not the actor who captures the AI revenue, and the utility that controls the queue captures neither — so the match that is obviously good for the system is nobody's job by default.

Game diagnosis: high shared value, classic coordination failure: the generator, the AI operator, and grid reliability all gain, but first-come-first-served queue rules and split cost-allocation mean no single actor will assemble the deal. Queue-stuffing by speculative projects makes it worse.

Contract path: co-locate behind the existing interconnection: a curtailable-load service agreement where the AI operator firms up to the generator's reliable output and curtails the flexible portion on the operator's signal, in exchange for energizing on the generator's existing queue position. Share the queue-skip value via a capacity payment to the generator.

Constraints to design around: firm only the non-flexible MW; price the interruptible MW separately; no net reliability reduction for existing ratepayers; meter delivered MWh and curtailment events before any value claim; cap ratepayer-funded upgrades; allocate deliverability cost to the beneficiary; respect the generator's existing PPA and ramp limits.

Measurement needs: delivered MWh and time-to-power (months saved vs. queue baseline); curtailment hours actually called and honored; generator utilization before/after; deliverability headroom on the shared interconnection.

### 3. Curtailed Solar+Storage (West TX)  ->  Hyperscaler Training Campus

- Region: ERCOT
- Match score (coupling confidence): 0.87
- MW served from stranded headroom: 375 of 750 needed
- Load flexibility (interruptible share): 65%
- Queue-years potentially avoided: ~4
- Alignment tier: `medium-priority prototype`

Actors:

- AI operator / hyperscaler: needs power in months not years; will trade flexibility for speed; constraint: uptime SLA, capex, board timeline
- stranded-generator owner (solar+storage): holds an underused interconnection and asset; wants revenue; constraint: existing PPA terms, ramp limits, fuel/weather availability
- utility / ISO-RTO: owns the interconnection queue and reliability; constraint: queue rules, ratepayer protection, deliverability
- regulator / PUC: protects ratepayers and equity; constraint: cost-allocation rules, who pays for upgrades
- local community / ratepayers: bears rate and reliability effects; constraint: limited visibility and negotiating power

Activity diagnosis: the actor who can energize the load fast (the stranded generator) is not the actor who captures the AI revenue, and the utility that controls the queue captures neither — so the match that is obviously good for the system is nobody's job by default.

Game diagnosis: moderate shared value, a bargaining problem: the deal needs a flexibility commitment and a clear split of who funds any deliverability upgrade before either side moves.

Contract path: co-locate behind the existing interconnection: a curtailable-load service agreement where the AI operator firms up to the generator's reliable output and curtails the flexible portion on the operator's signal, in exchange for energizing on the generator's existing queue position. Share the queue-skip value via a capacity payment to the generator.

Constraints to design around: firm only the non-flexible MW; price the interruptible MW separately; no net reliability reduction for existing ratepayers; meter delivered MWh and curtailment events before any value claim; cap ratepayer-funded upgrades; allocate deliverability cost to the beneficiary; respect the generator's existing PPA and ramp limits.

Measurement needs: delivered MWh and time-to-power (months saved vs. queue baseline); curtailment hours actually called and honored; generator utilization before/after; deliverability headroom on the shared interconnection.

### 4. Curtailed Solar+Storage (West TX)  ->  Burst Training Pod

- Region: ERCOT
- Match score (coupling confidence): 0.95
- MW served from stranded headroom: 300 of 300 needed
- Load flexibility (interruptible share): 80%
- Queue-years potentially avoided: ~3
- Alignment tier: `medium-priority prototype`

Actors:

- AI operator / hyperscaler: needs power in months not years; will trade flexibility for speed; constraint: uptime SLA, capex, board timeline
- stranded-generator owner (solar+storage): holds an underused interconnection and asset; wants revenue; constraint: existing PPA terms, ramp limits, fuel/weather availability
- utility / ISO-RTO: owns the interconnection queue and reliability; constraint: queue rules, ratepayer protection, deliverability
- regulator / PUC: protects ratepayers and equity; constraint: cost-allocation rules, who pays for upgrades
- local community / ratepayers: bears rate and reliability effects; constraint: limited visibility and negotiating power

Activity diagnosis: the actor who can energize the load fast (the stranded generator) is not the actor who captures the AI revenue, and the utility that controls the queue captures neither — so the match that is obviously good for the system is nobody's job by default.

Game diagnosis: moderate shared value, a bargaining problem: the deal needs a flexibility commitment and a clear split of who funds any deliverability upgrade before either side moves.

Contract path: co-locate behind the existing interconnection: a curtailable-load service agreement where the AI operator firms up to the generator's reliable output and curtails the flexible portion on the operator's signal, in exchange for energizing on the generator's existing queue position. Share the queue-skip value via a capacity payment to the generator.

Constraints to design around: firm only the non-flexible MW; price the interruptible MW separately; no net reliability reduction for existing ratepayers; meter delivered MWh and curtailment events before any value claim; cap ratepayer-funded upgrades; allocate deliverability cost to the beneficiary; respect the generator's existing PPA and ramp limits.

Measurement needs: delivered MWh and time-to-power (months saved vs. queue baseline); curtailment hours actually called and honored; generator utilization before/after; deliverability headroom on the shared interconnection.

### 5. Seasonal Spilled Hydro  ->  Sovereign AI Build

- Region: MISO
- Match score (coupling confidence): 0.76
- MW served from stranded headroom: 300 of 350 needed
- Load flexibility (interruptible share): 30%
- Queue-years potentially avoided: ~6
- Alignment tier: `medium-priority prototype`

Actors:

- AI operator / hyperscaler: needs power in months not years; will trade flexibility for speed; constraint: uptime SLA, capex, board timeline
- stranded-generator owner (hydro): holds an underused interconnection and asset; wants revenue; constraint: existing PPA terms, ramp limits, fuel/weather availability
- utility / ISO-RTO: owns the interconnection queue and reliability; constraint: queue rules, ratepayer protection, deliverability
- regulator / PUC: protects ratepayers and equity; constraint: cost-allocation rules, who pays for upgrades
- local community / ratepayers: bears rate and reliability effects; constraint: limited visibility and negotiating power

Activity diagnosis: the actor who can energize the load fast (the stranded generator) is not the actor who captures the AI revenue, and the utility that controls the queue captures neither — so the match that is obviously good for the system is nobody's job by default.

Game diagnosis: moderate shared value, a bargaining problem: the deal needs a flexibility commitment and a clear split of who funds any deliverability upgrade before either side moves.

Contract path: co-locate behind the existing interconnection: a curtailable-load service agreement where the AI operator firms up to the generator's reliable output and curtails the flexible portion on the operator's signal, in exchange for energizing on the generator's existing queue position. Share the queue-skip value via a capacity payment to the generator.

Constraints to design around: firm only the non-flexible MW; price the interruptible MW separately; no net reliability reduction for existing ratepayers; meter delivered MWh and curtailment events before any value claim; cap ratepayer-funded upgrades; allocate deliverability cost to the beneficiary; respect the generator's existing PPA and ramp limits.

Measurement needs: delivered MWh and time-to-power (months saved vs. queue baseline); curtailment hours actually called and honored; generator utilization before/after; deliverability headroom on the shared interconnection.

## Stranded Loads (the unsolved part)

- **Research Supercompute (24/7)** (SPP, 250 MW, 4-yr queue): firm 24/7 load; only variable capacity in-region — needs storage/firming or transmission, not pure co-location.

These are honest negatives: the engine should say where no match exists, not invent one. They are the queue-reform, firming, and transmission cases — not co-location cases.

## Limits

- This is a decision/coordination layer. It does not generate power or shorten a literal queue; it finds feasible matches and the agreement that unlocks them.
- Cross-region couplings are scored as infeasible here — real transmission and deliverability modeling is required before claiming an inter-region match.
- Facility data is calibrated but not a live export. Real use needs ISO/RTO queues, EIA-860 utilization, and the generator's actual PPA and ramp terms.
- Dollar and queue-year values are hypotheses until one match is struck and measured.

## Next Implementation Targets

- Ingest a real ISO/RTO interconnection queue (PJM, ERCOT, MISO, SPP are public; LBNL 'Queued Up' is a clean aggregate).
- Add EIA-860 / EIA-923 generator utilization to find true stranded headroom.
- Model deliverability/transmission so cross-region matches become scoreable.
- Store struck-deal outcomes and compare predicted vs. realized time-to-power.

## Provenance

- LBNL 'Queued Up' (emp.lbl.gov/queues), data through end of 2025, updated May 2026
- Latitude Media: ERCOT large-load queue quadrupled to 226 GW (2025)
- IEEE Spectrum / Introl: Amazon-Susquehanna 300 MW behind-the-meter (+180 MW requested); Microsoft-Three Mile Island 835 MW restart
- CNBC (2025-10-17): data-center energy mix ~gas 40% / renewables 24% / coal 15%
- Chevron + GE Vernova: up to 4 GW behind-the-meter gas for data centers (18-24 month timelines)
