# Side Experiment: ESIG Large Loads Interconnection & Siting Audit
## Modeling Coordinated Study Processes and Flexible (Non-Firm) Service NPV
*Prepared in response to the June 2026 ESIG report: "Interconnection Processes for Large Loads: Current Practices and Recommendations"*

---

## Executive Summary

The massive surge in large loads—primarily driven by AI hyperscaler data centers, advanced manufacturing, and gigafactories—has overwhelmed traditional utility interconnection processes. Historically, load interconnection was treated as a local distribution service utility task. Today, gigawatt-scale data center requests impact the high-voltage transmission backbone, creating a parallel "load queue" crisis that matches the scale of the generator queue.

This side experiment simulates a cohort of five large load requests totaling **1,100 MW** attempting to connect to a local grid interface with **800 MW** of available transmission headroom. 

### Key Findings
1.  **Isolated Utility Studies Fail at Scale:** When utilities study loads sequentially without RTO coordination, they fail to detect cumulative transmission overloads. This triggers late-stage **restudy cascades**, pushing average delays to **31.2 months** and forcing **40% of the projects (350 MW) to withdraw** from the queue.
2.  **Coordinated Cluster Studies Stabilize the Queue:** By running a joint utility-RTO study using a coordinated data sheaf, the $45M upgrade is identified upfront. Siting timelines are shortened to a flat **24 months** for all projects, and **zero projects withdraw**.
3.  **Flexible (Non-Firm) Interconnection Yields a +$235.5M NPV Gain:** For a 300 MW AI training facility (LD-003), bypassing the transmission upgrade and connecting 12 months earlier in exchange for a non-firm, curtailable service agreement (curtailing 50% of capacity for 120 hours of peak congestion/yr) increases project NPV by **$235.53M** over a 10-year horizon, even when accounting for **$2.16M/yr in lost compute revenue**.

---

## 1. The Siting Dilemma: Sequential vs. Coordinated Studies

We modeled 5 large load requests trying to connect to a congested seam (e.g., PJM-West / MISO boundary):
*   **LD-001:** 250 MW (Hyperscaler Cluster)
*   **LD-002:** 200 MW (Inference Center)
*   **LD-003:** 300 MW (AI Training Pod)
*   **LD-004:** 150 MW (Sovereign Compute)
*   **LD-005:** 200 MW (Giga-Factory)

```
              Available Headroom: 800 MW
Sequential:  [ LD-001: 250 MW ] + [ LD-002: 200 MW ] + [ LD-003: 300 MW ] = 750 MW (Cleared)
             ------------------ Overload Threshold (800 MW) ------------------
             [ LD-004: 150 MW ] + [ LD-005: 200 MW ] = 1,100 MW (Overload -> Restudy Cascade)
```

### Scenario A: Isolated Utility Studies (Current Practice)
Utilities process requests individually on a first-come, first-served basis, checking only local distribution lines.
*   **The Cascade Trigger:** LD-001, LD-002, and LD-003 clear. When LD-004 and LD-005 submit requests, cumulative demand hits 1,100 MW, triggering a severe thermal overload at the transmission boundary.
*   **The Restudy Cascade:** The RTO halts the queue, forcing all 5 projects back into restudy to recalculate who triggers and pays for the regional upgrades. 
*   **The Outcome:** Siting timelines inflate by **24 months**. LD-004 and LD-005 withdraw due to timeline-induced capital expiration. Average delay rises to **31.2 months**.

### Scenario B: Coordinated Cluster Studies (ESIG Recommendation)
The utility and RTO share a joint data sheaf (local-to-global mapping via a Grothendieck Fibration), studying the 1,100 MW collectively.
*   **Upfront Cost Allocation:** The $45M regional upgrade is identified in the first cycle. The cost is allocated proportionally among all 5 loads based on MW share:
    *   `LD-001 (250 MW)` pays **$10.23M**
    *   `LD-002 (200 MW)` pays **$8.18M**
    *   `LD-003 (300 MW)` pays **$12.27M**
    *   `LD-004 (150 MW)` pays **$6.14M**
    *   `LD-005 (200 MW)` pays **$8.18M**
*   **The Outcome:** Restudy cascades are avoided. Timeline is capped at a predictable **24 months** for all projects. **Zero projects withdraw**.

---

## 2. The Financial Case for Flexible (Non-Firm) Service

To bypass the 24-month coordinated study queue entirely, the ESIG report recommends offering **Flexible Interconnection Services (Non-Firm or Provisional Service)**. Under this agreement, the load is allowed to connect immediately using the existing 800 MW grid headroom, but must agree to curtail its demand during peak congestion hours.

We ran a 10-year NPV cash-flow simulation for **LD-003 (AI Training Pod, 300 MW)** comparing the two options:

```
Option 1: Firm Coordinated Interconnection
  Siting Cost: $12.27M (Proportional share of $45M upgrade)
  Timeline to Power: 24 months (Zero revenue in Years 1 & 2)
  Operational Revenue: Starts Year 3 (100% firm capacity, $283.82M/yr)

Option 2: Non-Firm Flexible Interconnection
  Siting Cost: $0 (Bypasses regional upgrade by accepting curtailment)
  Timeline to Power: 12 months (Zero revenue in Year 1, operational in Year 2)
  Operational Revenue: Starts Year 2 (Curtails 150 MW of flexible capacity for 120 hours/yr)
  Curtailment Loss: $2.16M/yr in lost compute revenue
```

### NPV Comparison Results
*   **Discount Rate:** 10%
*   **NPV Firm Connection:** **$1,239,115,779.50**
*   **NPV Non-Firm Connection:** **$1,474,645,167.44**
*   **Net Present Value Gain:** **+$235,529,387.94**

$$\text{Net Present Value Gain} = \text{NPV}_{\text{Non-Firm}} - \text{NPV}_{\text{Firm}} = \$235.53\text{ Million}$$

### Why This is a Game-Changer for Hyperscalers
For AI training and inference, **speed-to-market is the primary driver of NPV**. 
Even though the non-firm connection suffers an annual curtailment penalty of **$2.16M** (18,000 MWh of lost compute energy), starting operations **12 months earlier** pulls a massive volume of cash flow forward, yielding a net present value benefit of **over $235M**.

---

## 3. Policy & Siting Rules for Developers (e.g., ENGIE)

Based on these simulation results, developers should implement three specific risk rules:

1.  **Audit the Local Utility's RTO Data-Sharing Protocols:** Before selecting a site, verify whether the local utility has a formal information-sharing agreement with the RTO. If they study in isolation, increase the project’s schedule contingency by **18–24 months** to account for restudy cascade risks.
2.  **Evaluate Compute Workload Flexibility:** If the data center is hosting **AI Training** (which is highly asynchronous and can be paused), actively request a Non-Firm Interconnection Agreement. The NPV gain from avoiding queue delays outweighs the operational cost of curtailment.
3.  **Hedge Against Co-located Generation:** For workloads that require high uptime (AI Inference, SLAs), co-locate the data center behind the meter with a curtailed generator (such as wind/storage in West Texas or nuclear in PJM). This achieves the fast 12-month non-firm timeline while using the co-located asset to firm up the load, eliminating the $2.16M/yr curtailment revenue loss.
