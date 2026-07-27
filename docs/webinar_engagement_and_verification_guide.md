# i2X STITCH Webinar: Engagement, Concept-Bridging, and Verification Guide

This document is a strategic guide for presenting the findings of the **komposos-grid** repository to the organizers and presenters of the **i2X STITCH** session. It details the professional backgrounds of each presenter, outlines how to translate the codebase's mathematical language into industry-standard terms, and provides a step-by-step numerical walkthrough to build instant trust with the panelists.

---

## 1. Presenter Profiles & Communication Strategies

To earn the trust of grid professionals, you must communicate in their language and address their active priorities. Here is a breakdown of the presenters for the June 23, 2026 session:

### Alyssa Hickey · Midcontinent ISO (MISO)
* **Role:** Engineer, Resource Utilization Department (focused on the Definitive Planning Phase / DPP cluster studies for the South subregion).
* **Her World:** Managing the massive influx of generation requests, enforcing strict milestone deadlines, re-running cluster studies when developers withdraw, and preventing grid instability.
* **How to Talk to Her:** Focus on **winnowing and queue hygiene**. MISO's live question is whether their recent cluster reforms are successfully filtering out speculative "lottery ticket" projects without harming viable ones.
* **Bridge Phrase:** *"MISO's recent DPP cluster rules are visibly accelerating early-stage filtering. The data shows a massive volume of projects withdrawing before reaching the facility study stage, which keeps the restudy burden lower for the survivors."*

### Jenifer Fernandes · ERCOT
* **Role:** Manager of Resource Integration & Chair of the Resource Integration Working Group (RIWG).
* **Her World:** Managing ERCOT's serial (individual) study process, coordinating Planning Guide Revision Requests (PGRRs), and ensuring high-speed interconnection under Texas's "connect-and-manage" framework.
* **How to Talk to Her:** Focus on **certainty and timeline predictability**. ERCOT's process is fast but shifting more construction risk to developers. 
* **Bridge Phrase:** *"ERCOT’s individual serial process is highly predictive: once a project executes its Interconnection Agreement (IA), the probability of completion is outstanding (~80%). Your process trades cluster overhead for developer certainty."*

### Vish Sankaran · ENGIE North America
* **Role:** Head of Transmission & Interconnection for North America (formerly U.S. HHS Program Director for Federal Health Architecture).
* **His World:** Managing developer risk, allocating capital, and seeking predictability across multiple regional transmission operators (RTOs). Because of his federal technology background, he understands complex data architectures but values bottom-line developer predictability.
* **How to Talk to Him:** Focus on the **contract-certainty gap**. A developer needs to know if their milestone expenditures represent a safe bet.
* **Bridge Phrase:** *"From a developer's perspective, the executed IA milestone is not equivalent across regions. An IA is a solid bet in ERCOT (~80% build rate) but a coin-flip in MISO (~35% build rate). This gap is a major risk factor in portfolio capital allocation."*

### Julia Matevosyan · Energy Systems Integration Group (ESIG)
* **Role:** Associate Director and Chief Engineer at ESIG, host/facilitator of the i2X STITCH initiative.
* **Her World:** Researching how to integrate inverter-based resources (IBRs) safely and trying to find common, automated practices that all U.S. regions can adopt (harmonization).
* **How to Talk to Her:** Focus on the **structural mismatches** preventing automation. 
* **Bridge Phrase:** *"Direct timeline comparisons between MISO and ERCOT are structurally skewed because they do not share a common unit of work. MISO runs on cluster batches, while ERCOT has no cluster concept. True harmonization must normalize for this queue grouping asymmetry first."*

---

## 2. Bridging the Concepts: Math to Power Systems

The underlying engine of the repository runs on **applied category theory** (sheaves, categories, and OPTIMUS factorization). Presenting these terms directly to grid engineers will trigger skepticism. Use this translation guide:

| Category Theory Concept | Power System Translation | Why the Presenter Cares |
|:---|:---|:---|
| **Objects & Morphisms** | Queue States & Transitions | Maps the project lifecycle from Interconnection Request (IR) $\to$ Interconnection Agreement (IA) $\to$ Commercial Operation Date (COD). |
| **OPTIMUS Refinement** | Queue Factorization | Instead of looking at direct completion rates (`proposed` $\to$ `built`), we factor the path through `ia_executed`. This isolates whether failures are driven by the *study queue* or *post-agreement construction*. |
| **Sheaf Coherence & Gluing** | Regional Harmonization | Checks if data fields and process steps align across MISO and ERCOT. A coherence failure ($H^1$ mismatch) is simply an inconsistency in regional definitions. |
| **Yoneda-Profile Distance** | Contextual Performance Profile | Compares grid nodes or study processes by how they behave under active grid constraints (e.g., congestion, dynamic stability) rather than just looking at their raw capacities. |

---

## 3. The Trust Walkthrough: Numerical Proof of Accuracy

To prove the system is accurate, show the presenters numbers that reconcile **exactly** to the integer with the published tables in **Berkeley Lab's "Queued Up" 2026 Edition (data through year-end 2025)**.

If they see your system reproduces their trusted ground truth, they will trust the rest. Walk them through these 4 steps.

> ⚠️ **Steps 1–2 are reconciliations. Steps 3–4 are our own computation.** Sheet 25 publishes the regional completion table, so Steps 1–2 can be checked against LBNL's document. Sheet 27 publishes post-IA **nationally only**, and LBNL does not publish regional duration splits — so Steps 3–4 apply their methods to slices they never printed. Keep the two claims separate when you present. Overstating the second is the fastest way to lose this audience, because they are the people who can check.

### Step 1: Count the Raw Decided Cohorts (2000–2020)
Ask the presenters to verify the baseline project counts for requests submitted between 2000 and 2020 that have reached a final decision (either built or withdrawn):

* **MISO:** **2,445 decided projects**
  * *Operational (Built):* **509**
  * *Withdrawn (Quit):* **1,936**
* **ERCOT:** **1,254 decided projects**
  * *Operational (Built):* **459**
  * *Withdrawn (Quit):* **795**

> **Reconciliation Check:** These numbers match the published tables on **LBNL Queued Up Sheet 25** to the integer. They prove the data pipeline in the repository is not corrupt or buggy.

### Step 2: Establish the Overall Completion Rate
Using the standard Berkeley Lab definition (`Operational ÷ all 2000–2020 requests`, i.e. the denominator **includes still-active/censored projects**, not just decided ones):

* **MISO Overall Completion:** **18.1%** ($509 \div 2,806$ requests, including active/censored)
* **ERCOT Overall Completion:** **29.6%** ($459 \div 1,553$ requests, including active/censored)

> **Reconciliation Check:** This confirms that ERCOT builds roughly 1 in 3 projects it proposes, while MISO builds fewer than 1 in 5.

### Step 3: Introduce the "Green Light" Factorization (The Core Hook)
Now, isolate the projects that reached the final executed contract milestone (**Executed IA**). This is where the two regions diverge dramatically:

* **MISO:** **1,365 projects executed an IA**
  * *Became Operational:* **476**
  * *Withdrawn after signing:* **889**
  * *Post-Signing Completion Rate:* **34.9%** ($476 \div 1,365$)
* **ERCOT:** **610 projects executed an IA**
  * *Became Operational:* **486**
  * *Withdrawn after signing:* **124**
  * *Post-Signing Completion Rate:* **79.7%** ($486 \div 610$)

> **Provenance — say this out loud, do not skip it.** LBNL publishes post-IA completion on **Sheet 27 at national level only**; there is no regional breakdown on that sheet, and its sample pools LBNL's historical annual datasets rather than this file alone. **These per-region counts are our computation applying LBNL's method, not an LBNL-published figure.** Claiming otherwise is checkable in thirty seconds by anyone who opens the workbook — and this audience will. Framed correctly it is a *stronger* pitch: you read the method closely enough to see where LBNL stopped, and carried it one step further.
>
> **What it shows:** in ERCOT, executing an IA is a strong indicator of completion (~80% promise); in MISO it is close to a coin-flip (~35%).
>
> **If challenged on definitions**, the gap is not an artifact of the cutoff: LBNL's own IA-year window (2000–2022) gives 34.8% vs 79.9%; mature cohorts only (2000–2019) gives 32.9% vs 75.8%; counting suspended as not-built gives 34.9% vs 77.0%. The spread stays between 42 and 45 points in every variant.

### Step 4: The Duration Split (Certainty vs. Speed)
Finally, compare the median durations in months for projects that successfully built. This exposes that ERCOT's edge is not raw speed, but stage-specific certainty:

| Region | Study Stage (Request $\to$ IA) | Construction (IA $\to$ COD) | Total Clock (Request $\to$ COD) |
|:---|:---:|:---:|:---:|
| **MISO** | **29.8 months** | **18.8 months** | **39.1 months** |
| **ERCOT** | **20.3 months** | **25.9 months** | **44.3 months** |

* **The Insight:** MISO takes longer in the study phase, but once they sign, they build faster. ERCOT clears the studies faster, but takes longer to build. End-to-end, it is essentially a tie (~3.5 to 4 years). ERCOT's primary advantage is providing developers a faster path to a high-certainty contract (IA).

---

## 4. Key Takeaway for the i2X STITCH Panel
By presenting this walkthrough, you offer the panel a rare asset: a **neutral, reproducible cross-region benchmark** that uses their own data, validates to the single integer, and explains *where* and *why* the process breaks down. 

It moves the conversation away from general complaints about "slow queues" toward targeted process alignment—which is the exact mission of the i2X STITCH project.
