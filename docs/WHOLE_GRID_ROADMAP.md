# Whole-Grid Roadmap

*Written 2026-07-10. This is a roadmap for extending the existing system, not a plan to narrow it into a STITCH-only tool or a commercial product.*

## Purpose

Build a public system-of-systems tool that helps people see how the real grid fits together: what is flowing, what is blocked, who is affected, what is known, and which repairs are plausible.

The central question is:

> How do we get reliable, affordable, fair power to real demand when fuel, generation, wires, queues, markets, money, policy, and communities all constrain each other?

STITCH is an early expert audience and feedback channel. It is not the boundary of the tool.

## The shared story

```text
Demand
  homes · industry · EVs · electrification · data centers
        ↓
Connection
  load requests · generator queue · studies · agreements · upgrades
        ↓
Physical grid
  generation · storage · transmission · substations · seams · constraints
        ↓
Operations
  congestion · curtailment · balancing · outages · reliability
        ↓
Economics and people
  prices · upgrade costs · investment risk · ratepayers · communities
        ↓
Actions
  transmission · storage · flexible load · queue reform · generation · nuclear/fuel
```

The arrows are the point. A data center is not only demand: it changes forecasts, study requirements, upgrade costs, queue outcomes, congestion, ratepayer exposure, supply investment, and sometimes the case for storage or nuclear. Likewise, a fuel constraint is not only a nuclear problem if it changes the feasibility of firm power for a load.

## Preserve and connect existing work

| Existing capability | Whole-system role |
|---|---|
| `reports/SYSTEM_OVERVIEW.md` and grid-waste reports | National causal backbone |
| BA map, seams, flow geometry, constraints | Where power can and cannot move |
| Curtailment, queues, and outage work | Symptoms of system failure |
| Solution cards, relief curves, and B/C studies | Candidate repairs |
| Large-load work | Demand-side pressure and flexibility choices |
| Nuclear enrichment work | Firm-supply and fuel-chain constraints |
| Energy-alignment/community work | Who pays, benefits, governs, and bears risk |
| STITCH queue comparison | One concrete process/interconnection thread |

Do not remove these domains. Add common structure so each finding has a place in the same reality.

## First-class demand-side layer

Create a **Load Queue** parallel to the generator queue. Track, where public data permits:

- requested, studied, contracted, and energized MW;
- location, ramp schedule, and customer/load type;
- firm versus flexible service;
- on-site generation, storage, and backup;
- expected transmission upgrades; and
- uncertainty, including duplicate or speculative requests.

Then build a **Generation–Load–Transmission Collision Map**:

```text
Queued generation + new load + available transmission
→ co-located and mutually helpful?
→ separated and transmission-dependent?
→ competing for constrained upgrades?
→ creating reliability or ratepayer risk?
```

This should connect data-center demand, industrial growth, existing generation, generator queues, transmission constraints, and community consequences. Nuclear should enter as a possible firm-supply path with its fuel, timing, cost, and transmission dependencies visible.

## One evidence contract everywhere

Every claim, scenario, chart, and intervention should carry:

1. The question it answers.
2. Scope: geography, time period, and population/cohort.
3. Source and data vintage.
4. Status: **measured**, **derived**, **screening**, **simulated**, or **unknown**.
5. Assumptions and caveats.
6. What would improve or disprove the claim.
7. Related constraints, impacts, and possible actions.

The backend math earns its place by answering useful questions: whether two processes genuinely map, where datasets conflict, how much can safely be inferred from missing data, and whether a proposed repair is physically and economically coherent.

## One system, multiple entry questions

Do not create separate products. Give people different doors into the same map:

| Starting question | First thread to show |
|---|---|
| Why is power costly or unreliable here? | flows, constraints, outages, curtailment, rates |
| Can I connect a generator, storage project, or load? | queue risk, studies, upgrades, delivery constraints |
| Can a data center get power? | load queue, time-to-power, firm/flexible service, supply, transmission |
| Is an asset or corridor worth pursuing? | constraint, relief potential, cost, risk, evidence strength |
| Can nuclear help? | demand timing, fuel, construction, transmission, offtake |
| Who pays and who benefits? | cost allocation, ratepayer/reliability/community impacts |

Each thread should let a user travel outward to the full system and inward to sources and methodology.

## Phased roadmap

### Phase 1 — Establish the canonical whole-grid story

Use current work to produce one evidence-backed narrative:

`demand → queue → constrained movement → curtailment/reliability/cost → repair options`

Deliverables:

- a canonical system map and plain-language guide;
- an inventory mapping current reports and modules to system nodes;
- visible evidence labels and refresh dates; and
- links from every headline to its report, source, and reproduction path.

This phase primarily connects existing work; it does not require new grand models.

### Phase 2 — Build the common constraint graph

Represent the whole system with shared types:

- **entities:** loads, generators, storage, fuel assets, lines, queue projects, communities, regulators, investors;
- **constraints:** capacity, time, fuel, cost, policy, reliability, data quality;
- **relationships:** depends on, blocks, relieves, pays for, benefits, contradicts; and
- **evidence:** source, date, method, confidence, limitation.

Suggested future artifacts:

- `reports/evidence_registry.json` — an index of existing and future findings;
- `domains/grid/evidence_registry.py` — generator/validator for that index; and
- a small common schema for finding IDs and graph links.

The graph should preserve real differences between domains rather than flattening them into a generic score.

### Phase 3 — Make demand growth and data centers real

Add the Load Queue and collision map. Prioritize real public facts over a polished simulated cohort. Build from the smallest defensible regional data sources first, mark gaps honestly, and distinguish requested from committed and energized load.

Outputs:

- load-status funnel;
- regional demand-ramp timeline;
- firm-versus-flexible service scenarios grounded in observed constraints where possible; and
- generation/load/transmission collision findings.

### Phase 4 — Connect repairs to consequences

For every candidate repair—line, storage, flexible load, queue reform, generation, or nuclear/fuel intervention—show:

```text
constraint relieved
→ affected people and projects
→ cost and dependencies
→ evidence strength
→ remaining unsolved constraints
```

This turns existing solution cards and B/C work into a system-level repair conversation rather than isolated project rankings.

### Phase 5 — Surface the mathematical audit layer

Use the advanced backend to make claims that ordinary dashboards cannot safely make:

- identify incompatible regional milestones and definitions;
- detect data mismatches and weak joins;
- find genuinely comparable systems before transferring lessons;
- bound uncertainty for unobserved conditions; and
- check whether an action is coherent across physical, timing, and economic constraints.

Present the result in plain language first, then provide evidence and method depth for people who need it.

### Phase 6 — Share relevant threads, not the entire repository

Use the broad system as the source of focused external packets:

- **STITCH:** interconnection-process and queue thread, with the larger map as context.
- **Data-center teams:** demand, time-to-power, transmission, flexibility, and supply thread.
- **Nuclear/fuel people:** firm-supply, fuel timing, transmission, and offtake thread.
- **Investors/developers:** constraint-to-intervention evidence packet.
- **Regulators/advocates:** cost allocation, reliability, and community-impact thread.

Every packet should say it is one thread in a larger public system map, not ask anyone to adopt a platform.

## Non-goals and guardrails

- Do not turn this into a login, messaging, or social platform.
- Do not claim public data replaces an RTO planning study.
- Do not make simulations look like observations.
- Do not turn every finding into investment advice.
- Do not hide uncertainty to make the story cleaner.
- Do not flatten regional differences merely to create a national score.
- Do not shrink the system to fit one audience.

## Definition of success

The system works when someone can start with a real question—"Can this data center get power?", "Why did this project fail?", "Would this line help?", or "Can nuclear solve this here?"—and reach:

1. the relevant constraint;
2. the connected causes and consequences;
3. the evidence and uncertainty;
4. plausible repair paths; and
5. the next fact that must be checked.

That is the intended whole-picture tool: a living map of how grid reality composes, and where it fails.
