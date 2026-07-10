# Plain English Guide: Modeling the Nuclear Fuel Bottleneck

This guide explains how we model the civilian nuclear fuel supply chain, how the software analyzes it, and what our findings mean for securing power for next-generation AI data centers.

---

## 1. The Core Problem: The SMR Fuel Trap

Hyperscalers (Google, Microsoft, Amazon, Meta) want to build next-generation nuclear reactors (Small Modular Reactors, or SMRs) directly behind the meter to power their massive AI data centers. However, these advanced reactors require a special fuel called **HALEU** (High-Assay Low-Enriched Uranium). 

Currently, the Western supply chain has a critical bottleneck: we have virtually zero domestic HALEU enrichment capacity. If a tech company builds a reactor but cannot secure the fuel, they are left with an empty concrete dome. We need to model the steps of the fuel cycle to identify where the bottlenecks are and when expansions will realistically yield fuel.

---

## 2. How the Software Models the Supply Chain

This system (`komposos-grid`) acts like a smart graphing library. We represent the supply chain as a map of **Nodes** and **Connections**:

```
[Uranium Mine] ──(feed flow)──> [Conversion Plant] ──(SWU capacity)──> [Enrichment Centrifuges] ──(fuel rods)──> [SMR Reactor] ──(electricity)──> [Data Center]
```

*   **Nodes (Objects):** The physical locations in the supply chain (e.g., Urenco Eunice enrichment facility, Metropolis ConverDyn conversion facility, SMR reactors, and data center loads).
*   **Connections (Morphisms):** The flow of material and capacity between facilities. Each connection has a **Confidence Score** from `0.0` (will fail/long delay) to `1.0` (completely reliable). High-risk steps, like construction delays or single-source facilities, are assigned lower confidence.
*   **Timeline Scenarios:** We can connect planned expansions to reactor start dates. If a centrifuge expansion isn't ready until 2032, a 2028 reactor checking its fuel connection will get a low confidence score, flagging a timeline mismatch.

---

## 3. The Math Explained Simply

The software uses three mathematical tools to analyze the supply chain:

### A. Path Composition (Cognitive Claims Check)
If we want to know if Urenco's centrifuges can power the data center, the engine checks every connection along the path:
\[
\text{Enrichment} \xrightarrow{\text{processes}} \text{Fabrication} \xrightarrow{\text{powers}} \text{Reactor} \xrightarrow{\text{powers}} \text{Data Center}
\]
It multiplies the confidences of each step together to calculate the **System-Wide Confidence**. If any single hop is blocked or delayed, the overall confidence drops to near zero.

### B. Curvature Analysis (Finding Pinch Points)
Curvature measures how "meshed" a network is:
*   **Bottlenecks (Negative Curvature):** A single road where all traffic is forced to squeeze through, with no detour options. If that road closes, the entire network fails. In our model, **Metropolis ConverDyn** is a bottleneck because it is the sole domestic conversion facility.
*   **Stable Zones (Positive Curvature):** A grid of city streets where you have multiple detours. If one street is blocked, traffic flows around it.

### C. Fiedler Seam Partitioning (Regulatory & Supply Boundaries)
Fiedler analysis divides the map into weakly-coupled regions:
*   **Upstream Region:** Raw mining, chemical conversion, and enrichment.
*   **Downstream Region:** Fuel fabrication, reactor operations, and power delivery.
*   The boundary between these regions marks the weakest link in the supply chain, which is the transition from raw materials to fabricated fuel rods.

---

## 4. Key Findings from the 5 Scenarios

We simulated 5 scenarios to test different business decisions and interventions:

1.  **Baseline (Current Status):** The supply chain is choked by two bottlenecks: conversion limits (ConverDyn) and centrifuge queue delays (Urenco). Fuel delivery confidence is very low (**0.100**).
2.  **Scenario A (Faster Centrifuges):** We simulate accelerating the installation of Urenco's centrifuges. This solves the queue bottleneck, but overall fuel confidence remains low (**0.160**) because the conversion bottleneck still chokes the flow upstream.
3.  **Scenario B (More Conversion):** We simulate co-funding conversion upgrades. This secures the upstream raw material flow, but fuel confidence remains low (**0.120**) because the centrifuge queue delays downstream still block deliveries.
4.  **Scenario C (Dual Intervention):** We simulate resolving **both** bottlenecks at the same time. This results in a **3x increase** in fuel cycle confidence (**0.300**). **Key takeaway:** Hyperscalers and policymakers must fund both upgrades jointly; fixing only one bottleneck yields virtually no benefit.
5.  **Scenario D (Supply Disruption):** We simulate a shutdown at the conversion plant. The entire system immediately disconnects, and confidence drops to **0.010** (near total system failure).

---

## 5. How to Edit the Data Yourself

You don't need to write code to test different scenarios. We created two simple spreadsheets in the [domains/nuclear/data/](file:///c:/Users/JAMES/github/KOMPOSOS-ENRICH/domains/nuclear/data) folder:

1.  **[nuclear_facilities_template.csv](file:///c:/Users/JAMES/github/KOMPOSOS-ENRICH/domains/nuclear/data/nuclear_facilities_template.csv)**: You can open this in Excel or notepad and edit the names, capacities, and locations of your facilities.
2.  **[nuclear_flows_template.csv](file:///c:/Users/JAMES/github/KOMPOSOS-ENRICH/domains/nuclear/data/nuclear_flows_template.csv)**: You can edit the connections, rename relationships, or change the confidence scores.

To run the software with your custom numbers, enter this command in your terminal:
```bash
python -m domains.nuclear.run_enrichment_flow --nodes-csv domains/nuclear/data/nuclear_facilities_template.csv --edges-csv domains/nuclear/data/nuclear_flows_template.csv
```
