# Commercial Guide & Manual: Seam Opportunity Screening
## Surfacing the Hidden Value of Grid Interconnections and Seam Optimizations

---

## Executive Overview

Every year, congestion across boundaries (seams) between Regional Transmission Organizations (RTOs) and Balancing Authorities (BAs) costs the US electric grid hundreds of millions of dollars. Traditional grid planning methods rely on simple historical data or static annual averages. These methods are blind to structural constraints, data inconsistencies, and the true economic value of unmarketed seams.

The **Komposos Seam Opportunity Screening Engine** utilizes advanced structural modeling to reveal hidden economic opportunities. By translating complex category-theoretic and topological formulas into clear, actionable business metrics, the engine provides developer portfolios, RTO planners, and investors with four proprietary screens:

1. **RTO Portability Score** (formerly Yoneda Similarity): Transferring proven congestion-relief solutions from one region to another without re-studying from scratch.
2. **Shadow Market Valuation** (formerly Right Kan limits): Uncovering hidden congestion costs on interfaces that do not publish transparent market prices.
3. **Optimal Investment Capacity Sweet Spot** (formerly Marginal BCR curves): Finding the exact upgrade capacity size that maximizes returns and avoids over-building.
4. **Data Integrity & Calibration Index** (formerly Sheaf Cohomological Audit): Reconciling conflicting reporting sources to ensure planning decisions are built on trusted numbers.

This manual explains what these metrics mean, how they generate value, and how to sell them to energy developers, regulators, and grid operators.

---

## 1. RTO Portability Score (Topological Similarity)

### The Business Problem
Interconnection queues are congested, and study timelines are measured in years. When a developer designs a successful congestion-relief project (like a battery storage facility or a transmission upgrade) in one region, they cannot easily copy-paste that project to another region. They are forced to restart the scoping and engineering studies from scratch, incurring massive regulatory costs and delays.

### The Opportunity Metric
The **RTO Portability Score** measures the *relational equivalence* of different grid regions. Instead of looking at geographic distance, it evaluates the structural role a Balancing Authority plays relative to all its trading neighbors. 

If region $A$ and region $B$ have a high Portability Score, it means they occupy identical topological positions in the national power grid. 

### Commercial Value & Selling Points
* **Reduce Development Cycles**: If a battery layout or dynamic line rating upgrade is approved in RTO $A$, and RTO $B$ has a high Portability Score, the developer has a ready-made business case to fast-track similar projects in RTO $B$.
* **Avoid redundant scoping**: Planners can group similar BAs into "equivalence classes," applying the same grid optimization templates across them.
* **Real-World Finding**: The system identifies that **MISO and NYISO** share a high structural similarity of **30.1%**. Methodologies proven in the highly-sophisticated NYISO seam can be ported into MISO with a high degree of confidence.

---

## 2. Shadow Market Valuation (Unpriced Seam Screening)

### The Business Problem
More than a third of the US grid (particularly in the Southeast and West) operates under bilateral agreements without transparent wholesale markets. Because these regions do not publish Locational Marginal Prices (LMPs), standard planning models treat them as having "zero congestion cost." This makes it impossible for developers to justify building transmission upgrades or storage projects in these areas.

### The Opportunity Metric
**Shadow Market Valuation** solves the pricing blindness. It looks at the unpriced boundary (such as SOCO or TVA) and maps it against its adjacent *priced* market neighbors. Using a mathematical limit, it computes the most conservative price spread that must exist across the seam to maintain physical flow consistency.

### Commercial Value & Selling Points
* **Unlocking Non-Market Territory**: It reveals the hidden congestion penalty that utilities and consumers are paying in non-market regions.
* **Finding Undervalued Grid Corridors**: Developers can identify highly lucrative transmission upgrade corridors that are completely hidden from competitors who only look at public LMP maps.
* **Real-World Finding**: The system exposes that the **AECI - SWPP** unpriced seam carries a lower-bound congestion value of **$14.25M/yr**. This is a massive, unmeasured investment opportunity that standard models miss.

---

## 3. Optimal Investment Capacity Sweet Spot (Marginal BCR)

### The Business Problem
Transmission upgrades are capital-intensive. When developers propose a seam upgrade, they often over-build (e.g., building a 500 MW line when a 200 MW line would suffice) or under-build. Diminishing returns set in rapidly as capacity increases—the first 100 MW of an upgrade relieves the most expensive congestion, whereas the next 100 MW relieves much less. Simple static checks fail to identify the sizing sweet spot.

### The Opportunity Metric
The **Optimal Investment Capacity Sweet Spot** continuously calculates the *Marginal Benefit-Cost Ratio* ($\text{Marginal BCR}$) across all possible upgrade sizes. It identifies the exact capacity (MW) where the incremental benefit of adding one more MW of capacity equals its incremental cost (the $1.0$ break-even point).

### Commercial Value & Selling Points
* **Optimize Capital Expenditure (CapEx)**: Prevents over-investment. Why build a 500 MW upgrade when the Marginal BCR falls below 1.0 at 250 MW?
* **Defensible Business Cases**: Provides developers and regulators with a clean, mathematically optimized sizing justification that maximizes economic efficiency.
* **Real-World Finding**: On the **MISO - SWPP** seam, upgrade capacity yields high returns initially, but the Marginal BCR drops sharply from $0.27$ to $0.03$ as capacity approaches 1000 MW, indicating that upgrades should be capped near 200 MW to maximize capital efficiency.

---

## 4. Data Integrity & Calibration Index (Sheaf Coherence)

### The Business Problem
Grid analysts must work with mismatched datasets. The physical telemetry reports (EIA-930) describe what flows across lines, but generator accounting reports (eGrid/EIA-923) describe what is produced at plants. Because of reporting errors, boundaries, and station-use deductions, these datasets frequently contradict each other. Building models on uncalibrated data leads to bad investment decisions and rejected regulatory filings.

### The Opportunity Metric
The **Data Integrity & Calibration Index** models the entire grid as a unified data sheaf. It calculates a single global **Data Leak** score. If the leak is $0$, all reporting sources agree. If the leak is high, the engine localizes exactly which BAs or plants are reporting contradictory numbers. It then applies a mathematical crosswalk correction to align the datasets.

### Commercial Value & Selling Points
* **Dual-Verified Models**: Ensures that planning decisions are based on data that is physically and mathematically coherent.
* **De-Risk Regulatory Filings**: Eliminates data contradiction errors that frequently cause regulators to reject grid interconnection cases.
* **Real-World Finding**: Applying the footprint crosswalk corrected the absolute reporting error by **59.4 TWh** and cut the data leak from **1.899** to **0.818** (a **56.9%** data quality improvement), validating that our calibrated data is the cleanest planning dataset available.

---

## How to Pitch These Screens to Stakeholders

When communicating with non-technical users, translate the formulas into these high-impact value statements:

| Technical Concept | What it is | How to Pitch it (The Value) |
| :--- | :--- | :--- |
| **Yoneda Similarity** | Enriched Category Morphisms | **"RTO Portability"**: Copy-paste your successful projects from one region to another with pre-calculated regulatory fit. |
| **Right Kan Extension** | Categorical Limits & Meets | **"Shadow Market Valuation"**: See the hidden congestion costs in non-market regions to find untapped project sites. |
| **SCM Relief Derivatives** | Exponential Saturation Model | **"Optimal Sizing"**: Find the exact capacity sweet spot to maximize your project's return-on-investment. |
| **Sheaf Coherence Audit** | Laplacian $H^1$ Cohomology | **"Data Integrity Index"**: Clean and calibrate conflicting public data to eliminate regulatory filing risks. |
