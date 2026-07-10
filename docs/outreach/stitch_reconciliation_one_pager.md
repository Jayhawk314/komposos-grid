# The Interconnection Agreement Is Not the Same Milestone in Every Region
### A reproducible cross-region benchmark from Berkeley Lab's *Queued Up* data — prepared for the i2X STITCH collaboration

*James Hawkins · jhawk314@gmail.com · July 2026 · Follow-up to the June 23 STITCH session on Regional Study Processes*

---

## Why this exists

Cross-region comparisons of interconnection performance are routinely contested because the regions do not share a unit of work — MISO studies cluster batches, ERCOT runs a serial process. This one-pager presents a **neutral, fully reproducible benchmark** built directly from the Berkeley Lab *Queued Up* data file (through 2026). Every count below reconciles with LBNL's published tables **to the integer**, so the starting point is shared ground truth, not a new methodology to argue about.

## Step 1 — The baseline reconciles exactly (LBNL Sheet 25)

Requests submitted 2000–2020 that reached a final decision:

| | Decided | Built | Withdrawn | LBNL completion rate* |
|---|---:|---:|---:|---:|
| **MISO** | 2,445 | 509 | 1,936 | **18.1%** (509 / 2,806 requests) |
| **ERCOT** | 1,254 | 459 | 795 | **29.6%** (459 / 1,553 requests) |

*\*LBNL definition: operational ÷ all 2000–2020 requests, including still-active.*

## Step 2 — The finding: factor the funnel through the executed IA (Sheet 27)

Isolating projects that reached the executed Interconnection Agreement milestone:

| | Executed IA | Built after signing | Withdrew after signing | **Post-IA completion** |
|---|---:|---:|---:|---:|
| **MISO** | 1,365 | 476 | 889 | **34.9%** |
| **ERCOT** | 610 | 486 | 124 | **79.7%** |

**An executed IA is an ~80% promise in ERCOT and roughly a coin-flip in MISO.** The same contract milestone carries fundamentally different completion information in the two regions — which means milestone-based comparisons (and developer capital decisions keyed to the IA) are not comparing like with like.

## Step 3 — Where the time goes (median months, successful projects)

| | Request → IA | IA → COD | Request → COD |
|---|---:|---:|---:|
| **MISO** | 29.8 | 18.8 | 39.1 |
| **ERCOT** | 20.3 | 25.9 | 44.3 |

End-to-end, the regions are roughly tied (~3.5–4 years). ERCOT's edge is not total speed — it is **a faster path to a high-certainty contract**; MISO is slower to sign but builds faster after signing. Neither region "wins": they distribute certainty differently across the process.

## Implication for harmonization

Direct timeline and milestone comparisons between regions are structurally skewed until they are normalized for (1) the queue grouping asymmetry (cluster batch vs. serial request) and (2) the certainty content of each milestone. A harmonized reporting standard could publish **post-milestone completion rates** alongside timelines, so that "reached IA" means something comparable everywhere.

---

**Reproducibility.** Source: LBNL *Queued Up* data file through 2026 (public). Pipeline and interactive dashboard: `https://komposos-grid.streamlit.app` (open-source; every figure above is regenerable from the raw workbook with one command). I am glad to walk through the reconciliation step by step.
