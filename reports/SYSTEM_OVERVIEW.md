# US Grid System Overview

This page answers one plain question: **what is the nation's grid problem?** The answer is not just "we need more power plants." Demand is rising. Power already has to move between regions. A small number of bottlenecks limit that movement. Useful clean energy gets shut off when it cannot be delivered. Many new projects never make it through the queue. The result shows up as recurring congestion and reliability costs.

That is why the lead figure is a **system graph**, not a bar chart. The graph shows how the pieces relate. The bar charts that follow are the evidence behind each box.

## The System Graph

![system_problem_map.svg](figures/system_problem_map.svg)

Read the system from left to right:

1. **Need grows:** electricity demand is rising again.
2. **Movement matters:** the grid already depends on regional power transfers.
3. **The blockage is specific:** congestion is concentrated in a small set of constraints.
4. **Energy gets stranded:** renewable output is curtailed when the system cannot use or deliver it.
5. **The replacement pipeline is weak:** most queued projects do not become operating plants.
6. **Customers pay:** the same physical limits show up as dollar waste and reliability exposure.

The point is the relationship among the parts. Demand growth matters because power has to be delivered through a network. Cross-region flows matter because the network is already used that way. Bottlenecks matter because they decide where cheap or clean energy can actually go. Curtailment and queue attrition matter because they show energy and new supply getting stuck. The dollar figures matter because they show the consequence is not theoretical.

## Key Numbers

- Demand reached **4,294 TWh** in 2025, up **215 TWh** from 2023.
- Gross electricity crossing grid-operator borders was **494 TWh** in 2025.
- In **PJM**, the top 10 constraints carry **38%** of severity across **857** constraints.
- CAISO + SPP renewable curtailment shown here totals **13.03 TWh**.
- Decided interconnection queue projects completed at **16.5%**; signed-IA projects reach **65.5%**.
- The measured/proxy waste ledger is **$251M**; the reliability valuation floor is **$4,369M/yr**.

## Supporting Evidence Charts

These charts are not the story by themselves. Each one backs up one box or arrow in the system graph above.

### 1. Demand Pressure Is Rising

This is the starting point. A grid that was already hard to run has to serve more electricity. More demand is not automatically bad, but every added terawatt-hour has to be generated, moved, and delivered at the right hour and place.

![system_demand.svg](figures/system_demand.svg)

### 2. Moving Power Between Regions Is Not Optional

This shows gross energy crossing balancing-authority borders. The point is not that bigger is always better. The point is that regional transfers are already a normal operating feature of the US grid, so weak borders become national problems.

![system_interchange.svg](figures/system_interchange.svg)

### 3. The Problem Is Not Spread Evenly Everywhere

Congestion severity is concentrated. When the worst 10 constraints carry roughly a third of total severity, the system is telling us that a small set of physical limits can drive a large share of the pain.

![system_concentration.svg](figures/system_concentration.svg)

### 4. Stranded Energy Turns Into Curtailment

Curtailment means usable generation was ordered down. That is the simplest physical symptom of the grid problem: energy exists, but the system cannot absorb it locally or move it somewhere more useful.

![system_curtailment.svg](figures/system_curtailment.svg)

### 5. The Queue Does Not Reliably Refill The System

The interconnection queue is the path new plants use to reach the grid. If most decided projects do not finish, then "more projects are waiting" is not the same thing as "more power is coming."

![system_queue.svg](figures/system_queue.svg)

### 6. The Same Limits Become A Bill

The dollar chart is not one single grand total. It puts different layers of evidence side by side: measured/proxy congestion and curtailment claims, plus a conservative reliability floor. The reason to care is that these are recurring costs, not one-time annoyances.

![system_waste.svg](figures/system_waste.svg)

## What The Six Figures Prove Together

The national grid problem is a chain: rising demand increases the need to move power; regional transfers already carry a large amount of energy; a few constraints block a disproportionate share of that movement; blocked movement strands clean generation and slows new supply; the consequences appear as annual congestion, curtailment, and reliability costs. That points toward targeted transmission, interconnection reform, storage, and flexible demand at the binding places, not a vague call for "more grid" everywhere.

## Terms

- **Balancing authority (BA):** a grid operator area that balances supply and demand.
- **Interchange:** electricity crossing from one BA area to another.
- **Constraint:** a grid limit that prevents cheaper or cleaner power from flowing freely.
- **Curtailment:** usable generation ordered to reduce output.
- **Interconnection queue:** the approval pipeline for new generators to connect to the grid.

## Machine-Readable Stats

```json
{
  "demand_twh": {
    "2023": 4078.972669,
    "2024": 4198.102877,
    "2025": 4294.309865
  },
  "interchange_twh": {
    "2023": 499.719924,
    "2024": 501.844792,
    "2025": 493.662162
  },
  "concentration": {
    "MISO": {
      "n_constraints": 2463,
      "top10_share": 0.33238071236994515
    },
    "PJM": {
      "n_constraints": 857,
      "top10_share": 0.3818580692361303
    },
    "SPP": {
      "n_constraints": 1532,
      "top10_share": 0.3592630630920616
    }
  },
  "curtailment_twh": {
    "CAISO 2023": 2.66,
    "SPP 2023": 10.367625992499997
  },
  "queue_completion": {
    "overall": 0.16508100654946567,
    "ia_executed": 0.6553092501368363
  },
  "waste_usd_m": {
    "Seam congestion (measured ties)": 78.6,
    "Waste ledger, all claims": 251.03443050390814,
    "Reliability floor": 4369.24124690625
  }
}
```
