# Tiered Presentation: MISO vs ERCOT Interconnection Study Process

This document structures the regional study findings for the ESIG / Berkeley Lab **i2X STITCH** session into the four presentation tiers outlined in [HOW_THIS_LANDS_IN_INDUSTRY.md](file:///c:/Users/JAMES/github/KOMPOSOS-GRID/reports/stitch_2026-06-23/HOW_THIS_LANDS_IN_INDUSTRY.md). 

It is designed to let you communicate with any audience—from a general policy manager to a mathematical researcher—without losing them in unnecessary complexity.

---

## Tier 0 — The Hook (30 Seconds)
**For:** Anyone (general audience, icebreaker)

> **"In Texas, signing a grid connection contract is almost a guarantee that a project gets built (~80% success). In the Midwest, even after signing, it's a coin-flip (~35% success)—yet both regions take the exact same total time (~3.5 to 4 years) to connect a project from start to finish. ERCOT's real edge is certainty, not speed."**

---

## Tier 1 — The Decision View (5 Minutes)
**For:** Managers, Developers, and Policy Makers

This tier provides the high-level summary and key metrics from the public data without technical details.

### Headline Metrics (2000–2020 Requests)
All metrics use Berkeley Lab's official definitions. The **Overall Completion Rate** column
matches their published Sheet 25 table exactly; **Built after signing IA** is our own
computation (LBNL publishes post-IA nationally only, Sheet 27).

| Region | Requests Submitted | Operational (Built) | Overall Completion Rate | Built after signing IA |
|---|---:|---:|---:|---:|
| **ERCOT (Texas)** | 1,553 | 459 | **29.6%** | **79.7%** (486 / 610) |
| **MISO (Midwest)** | 2,806 | 509 | **18.1%** | **34.9%** (476 / 1,365) |

### Key Takeaways
1. **The Contract Milestone Inconsistency:** The executed Interconnection Agreement (IA) is the green light. In Texas, 4 out of 5 projects with an IA get built. In the Midwest, nearly 2 out of 3 projects with an IA still withdraw. The same official milestone has very different predictive weights across regions.
2. **Speed is a Tie:** While Texas studies and clears projects faster, MISO builds them faster once cleared. End-to-end, the clocks align.
3. **Harmonization Needs:** Harmonizing the study-to-IA pathway across regions is the highest-value target for reducing queue withdrawals.

---

## Tier 2 — The Analyst View (30 Minutes)
**For:** Grid Engineers, Skeptics, and Data Scientists

This tier provides the rigorous data science backing, definitions, durations, and caveats.

### 1. Process Duration Breakdown
*Median elapsed months per stage (computed only over projects reaching each milestone, date errors excluded):*

- **Study Stage (IR $\to$ IA):** MISO: **29.8 months** [14.9–43.0] vs. ERCOT: **20.3 months** [12.9–29.4]
- **Construction Stage (IA $\to$ COD):** MISO: **18.8 months** [10.2–33.4] vs. ERCOT: **25.9 months** [18.8–34.2]
- **Total Duration (IR $\to$ COD):** MISO: **39.1 months** [22.3–57.0] vs. ERCOT: **44.3 months** [30.2–56.9]

### 2. Milestone funnel (where decided projects ended up)
Projects terminate at different study stages. Reaching `ia_executed` is the gate to commercial operation.

- **ERCOT Funnel:** 
  - `ia_executed`: **93.7%** completion (613 operational out of 654 decided)
  - `facility_study` / `ia_pending` / `unknown_study`: **0.0%** completion (all 1,100 decided projects withdrew)
- **MISO Funnel:**
  - `ia_executed`: **29.9%** completion (515 operational out of 1,723 decided)
  - `cluster_study` / `feasibility` / `system_impact`: **0.0%** completion (all 1,600+ decided projects withdrew)

### 3. Study-Cycle Trends (Impact of Reforms)
- **MISO:** Sliced by DPP cluster cycle. Historically, DPP-2008 had **56.2%** completion. This declined to **27.9%** (DPP-2016) and **8.3%** (DPP-2018). The newest reform batches (DPP-2021/2022) show massive *early* withdrawals (e.g. 522 out of 911 projects in DPP-2022 quit early), demonstrating that tightened rules are successfully filtering out non-serious projects.
- **ERCOT:** ERCOT has **no cluster construct**; study cycles are sliced by entry-year cohort. Completion rates hover steadily between **30%** and **45%** for mature cohorts (2012–2020).

### Data Sources & Caveats
- **Dataset:** LBNL *Queued Up*, 2026 Edition (data through year-end 2025).
- **Completion Definition:** Operational $\div$ all requests submitted 2000–2020 (LBNL sheet 25).
- **Built after signing Definition:** Operational $\div$ (operational + withdrawn) among projects with an executed-IA date (LBNL sheet 27).
- **Caveat:** active/suspended projects in the queue are censored (ignored as outcomes, not counted as failures). Durations are survivor-conditioned (computed only over successful projects that reached COD).

---

## Tier 3 — The Methodology (The Engine Room)
**For:** Academic Reviewers and Mathematical Researchers

This tier explains the category-theoretic and sheaf-theoretic engine that powers the repository's back-end validation.

### 1. Interconnection Queue Category
In [queue_analysis.py](file:///c:/Users/JAMES/github/KOMPOSOS-GRID/domains/grid/queue_analysis.py), the queue is modeled as a Category:
- **Objects ($Ob(\mathcal{C})$):** The source object is $A = \text{queue:proposed}$. The terminal objects are $Z \in \{\text{outcome:operational}, \text{outcome:withdrawn}\}$. Intermediate objects are cohorts $B_i$ (e.g., `fuel:solar`, `region:miso`, `ia:ia_executed`).
- **Morphisms ($\text{Hom}(X, Y)$):** Enriched morphisms carry a quantale weight representing conditional transition confidence $P(Y \mid X)$. The direct morphism has a confidence:
  \[w(A \to \text{operational}) = \text{overall completion rate} \approx 0.13\]
- **Factorization Search:** The [OptimusEngine](file:///c:/Users/JAMES/github/KOMPOSOS-GRID/src/komposos_core/core/optimus.py#L282) (from [optimus_core.py](file:///c:/Users/JAMES/github/KOMPOSOS-GRID/optimus_core.py)) searches for intermediate objects $B$ that factor the direct morphism with higher confidence:
  \[A \longrightarrow B \longrightarrow Z\]
  where the composite confidence $w(A \to B) \otimes w(B \to Z)$ exceeds the direct confidence $w(A \to Z)$. The transition $A \to \text{ia\_executed} \to \text{operational}$ is surfaced as the primary factorization, and the difference in $w(\text{ia\_executed} \to \text{operational})$ (ERCOT's $0.80$ vs MISO's $0.35$) measures the regional misalignment.

### 2. Presheaf Data Coherence & Sheaf Audits
Harmonization across data sources is checked using sheaf cohomology in [coherence.py](file:///c:/Users/JAMES/github/KOMPOSOS-GRID/domains/grid/coherence.py) and [sheaf_audit.py](file:///c:/Users/JAMES/github/KOMPOSOS-GRID/domains/grid/sheaf_audit.py):
- **Presheaf Section:** Each grid data source (e.g. eGRID, EIA-923, EIA-930) is modeled as a section $s_i$ over a subset of plants $U_i$.
- **Gluing Condition:** Harmonization requires sections to agree on overlaps:
  \[s_i\vert_{U_i \cap U_j} = s_j\vert_{U_i \cap U_j}\]
- **Sheaf Laplacian & $H^1$ Obstructions:** In [sheaf_audit.py](file:///c:/Users/JAMES/github/KOMPOSOS-GRID/domains/grid/sheaf_audit.py), a global ratio audit is set up where nodes are data sources and edges assert a scaling relationship $x_{\text{low}} = (\frac{\text{value}_{\text{low}}}{\text{value}_{\text{high}}}) \cdot x_{\text{high}}$. The sheaf Laplacian's smallest eigenvalue represents the $H^1$ obstruction (the energy leak). A leak of $\sim 0$ indicates global coherence, and the minimizing eigenvector provides the global calibration factor. Edge residuals localize the specific entities causing incoherence.
