# Blueprint for Untapped Grid Analytics: Surfacing Novel Calculations from the KOMPOSOS Core

The current Komposos Grid dashboard is a highly effective briefing tool, but it is primarily presenting and organizing existing public data (e.g., LBNL *Queued Up* aggregates, hand-coded RTO/ISO alignment matrices, and basic meeting transcripts). 

However, the underlying **Komposos engine**—specifically the category theory core (`optimus_core.py`, `kan_extensions.py`, `two_categories.py`), the topological/geometric tools (`flow_geometry.py`, `sheaf_audit.py`), and the SCM models (`relief_curves.py`)—possesses vast, unused mathematical capabilities. 

This document outlines a series of **non-trivial, novel calculations** that can be immediately computed using the code already in this repository. surfeacing these analyses will provide STITCH presenters and grid analysts with figures and insights that are unavailable in any other industry tool.

---

## 1. Topological & Category-Theoretic Grid Analytics

These calculations leverage the mathematical structures in `optimus_core.py` and the `categorical` module, mapping them directly to the balancing authority (BA) and tie-line flow datasets.

### 1.1 Yoneda Similarity & Structural Equivalence of BAs
Currently, BAs are mapped geographically and spectrally, but we do not quantify their structural similarity. In category theory, the Yoneda lemma implies that an object is entirely determined by its relationships to all other objects. 
We can compute the **Yoneda Similarity** between any two BAs ($A$ and $B$) using their incoming and outgoing flow profiles.

#### Mathematical Form
Let $\text{in}_A(X)$ be the gross annual MWh flow from BA $X$ to $A$, and $\text{out}_A(X)$ be the gross flow from $A$ to $X$. The Yoneda Similarity $J(A, B)$ is defined as:

$$J(A, B) = \frac{\sum_{X} \min(\text{in}_A(X), \text{in}_B(X)) + \sum_{X} \min(\text{out}_A(X), \text{out}_B(X))}{\sum_{X} \max(\text{in}_A(X), \text{in}_B(X)) + \sum_{X} \max(\text{out}_A(X), \text{out}_B(X))}$$

#### What This Reveals
- Identifies "structural twins" in the grid (e.g., BAs that occupy identical topological niches, even if geographically separated).
- Enables **functorial property transfer** (`absorb` in `optimus_core.py`): if $A$ and $B$ are Yoneda-similar, we can project congestion mitigation strategies validated in $A$'s footprint onto $B$'s footprint with a mathematically computed confidence threshold.
- *Novel Figure:* A **Yoneda Similarity Matrix Heatmap** of all US Balancing Authorities.

---

### 1.2 Right Kan Extension for Congestion Estimation on Unpriced Seams
Analysts frequently face the problem of "unpriced ties"—interfaces between BAs (particularly in the Southeast US, such as SOCO, TVA, and DUK) that do not publish locational marginal prices (LMPs) or congestion spreads. The system has code for **Right Kan Extensions** (`methodology.py`) designed to solve this, but its output has not yet been surfaced as a visual figure.

#### Mathematical Form
Let $p$ be a priced tie, and $u$ be an unpriced tie. Let $N(u)$ be the set of priced ties that share at least one BA node endpoint with $u$. The Right Kan Extension $\text{Ran}_K(F)(u)$ computes the local limit (infimum/meet) over adjacent priced congestion spreads:

$$\text{Ran}_K(F)(u) = \min_{p \in N(u)} (\text{Spread}(p))$$

#### What This Reveals
- Establishes a mathematically rigorous **lower-bound congestion value** for interfaces that operate without transparent markets.
- Quantifies the "hidden congestion tax" in non-market regions.
- *Novel Figure:* A **Southeast Hidden Congestion Map** showing unpriced ties colored by their Right Kan-extended estimated dollar values.

---

### 1.3 Homotopy Path Classification of Alternative Power Flows
Under Homotopy Type Theory (HoTT) in `hott/homotopy.py` and `hott/geometric_homotopy.py`, paths in a category can be classified into equivalence classes based on continuous deformation or shared "spines" (critical bottlenecks).

#### Mathematical Form
Let $P_1, P_2, \dots, P_k$ be alternative topological paths between two major generation and load centers (e.g., wind generation in SPP to load centers in PJM). We construct the geometric signature of each path $P_i$ as a sequence of Ollivier-Ricci curvatures:

$$\Sigma(P_i) = \langle \kappa(e_1), \kappa(e_2), \dots, \kappa(e_n) \rangle$$

Paths are grouped into homotopy equivalence classes $[P]$ based on their signature similarity (using Levenshtein distance on curvature intervals).

#### What This Reveals
- Classifies routing paths not just by distance, but by **structural risk**. Paths in the same homotopy class will fail together when their shared structural spine (a negative-curvature bottleneck) binds.
- *Novel Figure:* An **Equivalence Class Flow Diagram** showing the primary "homotopical corridors" across grid seams, highlighting which alternative routes are independent vs. structurally redundant.

---

### 1.4 Grothendieck Fibrations for Multi-Scale Grid Modeling
Grid data is usually analyzed either at the macroscopic BA-level (EIA-930) or the microscopic plant-level (eGRID/EIA-923). The system implements Grothendieck fibrations (`fibrations.py`), which formally unify these scales.

#### Mathematical Form
We define a fibration $p: \mathcal{E} \to \mathcal{B}$ where:
- The base category $\mathcal{B}$ represents the BA-level interchange graph.
- The fiber category $\mathcal{E}_X$ over BA $X$ contains the internal plant-to-plant transmission and generator assets within $X$.
- Cartesian lifts represent the mapping of individual plant generation adjustments up to the boundary interchange tie-line flows.

#### What This Reveals
- Tracks how sub-BA plant outages (from `outages.py`) cartesian-lift to restrict boundary tie-line capacities.
- Computes **cross-fiber Dijkstra routes** to identify the true microscopic paths that power takes when flowing across seams.
- *Novel Figure:* A **Multi-Scale Grid Fibration Tree**, showing how local plant-level adjustments aggregate dynamically into macroscopic seam flows.

---

## 2. Quantitative SCM & Queue Analytics

These calculations utilize the structural causal models (SCMs) in `relief_curves.py` and the queue matching heuristics in `queue_match.py`.

### 2.1 Marginal BCR and Saturation Curves ($\partial\text{BCR}/\partial\text{MW}$)
The current relief curves evaluate benefit-cost ratios (BCR) at discrete steps (50, 100, 250, 500, 1000 MW). We can calculate the continuous **Marginal BCR** to show the exact point of diminishing returns for transmission and storage interventions.

#### Mathematical Form
The exponential saturation model for relief energy is:

$$R(c) = G \cdot \left(1 - e^{-\frac{\eta \cdot c}{G}}\right)$$

where $c$ is the intervened capacity (MW), $\eta$ is the effective MWh throughput per MW-year, and $G$ is the annual gross MWh flow. The marginal relief value with respect to capacity is the derivative:

$$\frac{\partial V}{\partial c} = \text{Spread} \cdot \eta \cdot e^{-\frac{\eta \cdot c}{G}}$$

The Marginal BCR represents the incremental dollar of congestion relieved per incremental dollar of annualized cost:

$$\text{Marginal BCR}(c) = \frac{\text{Spread} \cdot \eta \cdot e^{-\frac{\eta \cdot c}{G}}}{\text{Annual Cost per MW}}$$

#### What This Reveals
- The exact **optimal sizing** for an upgrade. Surfacing the point where $\text{Marginal BCR} = 1.0$ prevents over-building.
- *Novel Figure:* A **Marginal Benefit-Cost Curve** plotting Capacity (MW) on the X-axis against Marginal BCR on the Y-axis for transmission vs. storage vs. flexible load.

```
Marginal BCR
  ▲
3 │  \   ◄─── Transmission Upgrade
2 │   \__
1 │      \─────── (BCR = 1.0 Break-even)
0 └──────────────► Capacity (MW)
```

---

### 2.2 The "Queue Rescue" Scorecard (Queue $\to$ Seam Congestion Integration)
Currently, queue completion probability (`queue_analysis.py`) and seam congestion matching (`queue_match.py`) exist as separate steps. We can combine them into a single metric: the **Stalled Relief Potential (SRP)**.

#### Mathematical Form
For each project $j$ currently stalled in the queue:
- Let $P(\text{Complete}_j)$ be its baseline completion probability based on its OPTIMUS cohort factorization (fuel, size, region, era).
- Let $V(\text{Relief}_j)$ be its potential congestion relief value matching adjacent ties.
- Let $C(\text{Seam}_j)$ be the constraint pressure of the target tie (binding hours $\times$ shadow price).

We compute the **Stalled Relief Potential**:

$$\text{SRP}_j = (1 - P(\text{Complete}_j)) \times V(\text{Relief}_j) \times \log(C(\text{Seam}_j) + 1)$$

#### What This Reveals
- Identifies projects that have a **high probability of withdrawal** but would provide **massive congestion relief** if they crossed the finish line.
- Pinpoints the exact projects where policy interventions (e.g., MISO cluster restudy reforms) would yield the highest economic return.
- *Novel Figure:* A **Queue Intervention Priority Scatter Plot** (X-axis: Completion Probability, Y-axis: Congestion Relief Value, bubble size: Constraint Pressure).

---

### 2.3 Seam Value Volatility & Drift Detection (Daily $\to$ Annual Integration)
The system collects daily LMP spreads and constraint shadow prices via `daily_update.py` and stores them in a long-format CSV. We can calculate the **drift and volatility of seam values** in real-time, showing which corridors are deteriorating or stabilizing relative to their 2023/2024 baselines.

#### Mathematical Form
For a given tie, let $S_t$ be the daily spread. We compute:
- **Rolling Volatility**: $\sigma = \text{std}(S_t)$ over a 30-day window.
- **Methodology Drift**: $\text{Drift} = \frac{\mu_{30} - \mu_{\text{baseline}}}{\sigma_{\text{baseline}}}$, where $\mu_{30}$ is the 30-day moving average and $\mu_{\text{baseline}}$ is the annual baseline mean.

#### What This Reveals
- Flags when a corridor's economics have structurally shifted (drift $> 2.0$), rendering historical annual briefs obsolete.
- *Novel Figure:* **Real-time Seam Volatility and Drift Sparklines** next to the static annual numbers on the dashboard.

---

## 3. Data Coherence & Reliability Analytics

These calculations utilize the sheaf-theoretic consistency checks in `sheaf_audit.py` and `coherence.py`, and the Sullivan reliability models in `reliability_value.py`.

### 3.1 Dempster-Shafer Sensor Fusion for Conflicting Telemetry
When evaluating grid waste, analysts often deal with conflicting telemetry data (e.g., EIA-930 reporting different interchange values than eGRID or ISO-specific state reports). We can use Dempster-Shafer evidence theory (`dempster_shafer.py`) to fuse these sources and report explicit belief intervals.

#### Mathematical Form
Let $\Theta = \{\text{Congested}, \text{Uncongested}\}$. A data source $i$ assigns belief mass $m_i$ to subsets of $\Theta$.
We fuse two independent sources $1$ and $2$ using Dempster's combination rule:

$$m_{1 \oplus 2}(A) = \frac{\sum_{B \cap C = A} m_1(B) m_2(C)}{1 - K}$$

where $K = \sum_{B \cap C = \emptyset} m_1(B) m_2(C)$ is the measure of conflict.

#### What This Reveals
- Provides a **Belief-Plausibility Interval** $[\text{Bel}(A), \text{Pl}(A)]$ for whether a specific seam bottleneck exists.
- Quantifies data conflict ($K$). High $K$ values alert analysts to sensor/reporting failures rather than grid physical congestion.
- *Novel Figure:* A **Telemetry Conflict Heatmap** overlaying the network map, coloring ties by their conflict factor $K$.

---

### 3.2 thermodynamic Sheaf Coherence $H^1$ Obstructions
`sheaf_audit.py` contains a complete thermodynamic sheaf representation of the grid. By building the sheaf Laplacian, we can compute the cohomology group $H^1$, which represents the global obstruction to data gluing.

#### Mathematical Form
Let $L_\mathcal{F}$ be the Sheaf Laplacian. We compute its smallest non-zero eigenvalue $\lambda_2$.
- If $\lambda_2 = 0$, the grid datasets are globally consistent (gluable).
- If $\lambda_2 > 0$, $\lambda_2$ represents the **coherence obstruction**. The corresponding eigenvector localizes the exact nodes and ties contributing most to the inconsistency.

#### What This Reveals
- A single, national **Grid Data Quality Index** ($\lambda_2$).
- The exact nodes where reporting agencies are out of sync (e.g., one BA reporting exports that the importing BA does not register).
- *Novel Figure:* A **Data Incoherence Hotspot Map** highlighting BAs where the sheaf residual error is concentrated.

---

## 4. Implementation Matrix: Surfacing These Figures

The table below outlines how these calculations map to the existing codebase and how they can be surfaced in the Streamlit application.

| Analytical Figure | Backend Script | Primary Math Module | Proposed UI Component |
| :--- | :--- | :--- | :--- |
| **BA Yoneda Similarity Heatmap** | `domains.grid.run_yoneda` (New) | `optimus_core.py` | Add to "🗺️ Harmonization Matrix" page as an "Equivalent RTO Structures" tab. |
| **Southeast Hidden Congestion Map** | `domains.grid.run_kan_estimation` | `categorical.kan_extensions` / `methodology.py` | Add to "📈 Seam Congestion Findings" page. |
| **Homotopy Corridor Trees** | `domains.grid.run_homotopy` (New) | `hott.homotopy` / `hott.geometric_homotopy` | Add to "📖 Grid Map Manual" as a structural classification. |
| **Marginal BCR Sizing Curves** | Update `relief_curves.py` | `relief_curves.py` | Add to "📈 Seam Congestion Findings" as interactive plots. |
| **Queue Rescue Scorecard** | `domains.grid.run_queue_rescue` (New) | `queue_analysis.py` + `queue_match.py` | Add to "📊 MISO vs ERCOT Queue Study" page. |
| **Seam Value Drift Sparklines** | Update `daily_update.py` | `daily_update.py` | Add to "⚡ Grid Network Map" node/edge inspector panels. |
| **Telemetry Conflict Map ($K$)** | Update `coherence.py` | `dempster_shafer.py` / `coherence.py` | Add to "⚡ Grid Network Map" as a "Data Confidence" overlay toggle. |
| **Grid Data Quality Index ($\lambda_2$)** | Update `sheaf_audit.py` | `sheaf_audit.py` | Add to "📖 Grid Map Manual" as a global status card. |
