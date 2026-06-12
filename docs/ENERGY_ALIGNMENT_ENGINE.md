# Energy Alignment Engine

## Purpose

KOMPOSOS-WESyS should help people see energy as a system they can repair.

The project is not only an audit that says where energy may be wasted. It is an
alignment engine that connects four layers:

1. Physical flows: WESyS resource pathways, conversion routes, and grid coupling.
2. Human activity: who uses, maintains, pays for, and benefits from energy.
3. Strategic incentives: where actors would cooperate, defect, delay, or shift cost.
4. Constraint and contract design: the rules that make repair practical.

The core product question is:

> Where is energy being lost, why does that loss persist, and what agreement or
> constraint would make repair rational?

## Operating Thesis

Energy waste is often not just a technical leak. It can also be a misdesigned
agreement.

A facility may know a pathway is inefficient but lack budget authority. A city
may benefit from lower emissions while the facility bears upgrade cost. A utility
may gain resilience from a repair without sharing the value created. WESyS can
surface the physical tension; alignment analysis explains the social and
economic tension around the repair.

## Layer Model

### 1. WESyS Physical Audit

This layer answers:

- What data was loaded?
- Which resources, technologies, and pathways exist?
- Where are pathways fragmented, weakly coupled, duplicated, or contradictory?
- What raw savings hypothesis follows from the model?

Current prototype signals:

- Resource graph nodes and pathways.
- Spectral connectivity and component count.
- Gray-category coherence gaps.
- Thermodynamic sheaf grounding checks.

### 2. Activity Theory

This layer answers:

- Who is the subject trying to act?
- What object are they trying to transform?
- What tools, rules, community, and division of labor shape the action?
- Which contradictions keep the energy loss in place?

Example mapping:

- Subject: landfill operator, utility, city, household, waste authority.
- Object: lower waste, produce RNG, reduce bills, stabilize grid.
- Tools: WESyS, meters, digesters, compressors, turbines, incentives.
- Rules: tariffs, permits, contracts, maintenance windows, procurement.
- Community: residents, regulators, operators, utilities, taxpayers.
- Division of labor: who pays, who maintains, who captures savings.

### 3. Game Theory

This layer answers:

- Are actors incentivized to cooperate?
- Who can free ride?
- Who bears cost while another actor receives the benefit?
- Which repair is unstable without coordination?

Use this layer to identify incentive failure, not to inflate savings claims.

### 4. Contract Theory and Constraint Design

This layer answers:

- What agreement would unlock the repair?
- What must be measured before payment?
- What constraints prevent bad incentives?
- How can savings, risk, emissions value, and reliability value be shared?

Example designs:

- Shared-savings contract.
- Performance-based maintenance agreement.
- Utility-city-facility cost share.
- Pay-for-measured-efficiency tariff.
- Grant or green-bank loan with verified savings.
- Community benefit agreement tied to measured emissions reduction.

Constraints can include:

- No reliability reduction.
- Payback under a target window.
- Verified metering before savings claims.
- Maintenance capacity and operator training.
- Permitting and interconnection feasibility.
- Equity guardrails for ratepayer or community impact.

## Report Shape

Every energy vision report should separate five claims:

1. Data: what WESyS data was loaded and what year was used.
2. Finding: what the model found physically.
3. Value hypothesis: what savings assumption turns the finding into dollars.
4. Alignment diagnosis: why actors may not repair it today.
5. Contract path: what agreement or constraint could make repair happen.

This keeps the work honest. The model can say "prototype savings estimate" while
still giving a useful next action.

## Near-Term Implementation Plan

### Phase 1: Runnable Vision Report

- Generate a Markdown report from the California WESyS audit.
- Roll repeated raw gaps into hotspot groups.
- Show both raw exposure and conservative rolled-up exposure.
- Add activity/game/contract analysis templates for each hotspot.
- Name the assumptions and caveats clearly.

### Phase 2: Better Hotspot Rollups

- Deduplicate repeated coherence gaps by resource, technology, and gap type.
- Track raw gap count separately from facility exposure.
- Add confidence tiers: prototype, plausible, validated.
- Attach physical grounding when thermodynamic sheaf evidence exists.

### Phase 3: Actor and Contract Model

- Add simple actor templates for landfill, POTW, CAFO, utility, city, and
  community.
- Map each hotspot to likely payer, beneficiary, regulator, and maintainer.
- Generate candidate contract designs with constraints.
- Record what data would validate or reject each design.

### Phase 4: Measured Feedback

- Store actual repair outcomes and measured savings.
- Compare predicted value against realized value.
- Update savings assumptions by pathway and region.
- Make the engine more humble where it is wrong and more specific where it is
  repeatedly right.

## Success Criteria

The engine creates value when a non-specialist can read a report and understand:

- Where energy is likely being wasted.
- Why the waste is not just a technical issue.
- Who needs to cooperate.
- What agreement could make repair rational.
- What measurement is needed before making a strong money claim.

The long-term goal is to change energy vision: people should see waste, water,
electricity, fuel, infrastructure, and incentives as one repairable system.

