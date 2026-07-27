# The Interconnection Agreement Is Not the Same Milestone in Every Region
### A reproducible cross-region benchmark from Berkeley Lab's *Queued Up* data — prepared for the i2X STITCH collaboration

*James Hawkins · jhawk314@gmail.com · July 2026 · Follow-up to the June 23 STITCH session on Regional Study Processes*

---

## Why this exists

Cross-region comparisons of interconnection performance are routinely contested because the regions do not share a unit of work — MISO studies cluster batches, ERCOT runs a serial process. This one-pager presents a **neutral, fully reproducible benchmark** built directly from the Berkeley Lab *Queued Up* data file (2026 Edition, data through year-end 2025).

**Two different provenance claims are made below, and they are deliberately kept apart.** Step 1 reconciles to LBNL's own published regional table to the integer — shared ground truth, nothing new to argue about. Step 2 applies LBNL's post-IA method *per region*, which LBNL publishes only at national level; those counts are my computation from the same data file, not an LBNL-published figure. Step 2 is where the finding is, and it is labelled as mine.

## Step 1 — The baseline reconciles exactly (LBNL Sheet 25)

Requests submitted 2000–2020 that reached a final decision:

| | Decided | Built | Withdrawn | LBNL completion rate* |
|---|---:|---:|---:|---:|
| **MISO** | 2,445 | 509 | 1,936 | **18.1%** (509 / 2,806 requests) |
| **ERCOT** | 1,254 | 459 | 795 | **29.6%** (459 / 1,553 requests) |

*\*LBNL definition: operational ÷ all 2000–2020 requests, including still-active.*

Every count in this table matches LBNL Sheet 25's published "Count by Status" columns exactly — including the denominators, which are that sheet's active + operational + withdrawn (+ suspended) totals.

## Step 2 — The finding: LBNL's post-IA method, applied per region (my computation)

LBNL publishes post-IA completion on Sheet 27 **at national level only** — there is no regional breakdown on that sheet, and its sample pools across LBNL's historical annual datasets rather than the current file alone. What follows applies the same method to each region using the current data file. **These are my counts, not LBNL's published figures.**

Isolating projects with an executed Interconnection Agreement date:

| | Executed IA | Built after signing | Withdrew after signing | **Post-IA completion** |
|---|---:|---:|---:|---:|
| **MISO** | 1,365 | 476 | 889 | **34.9%** |
| **ERCOT** | 610 | 486 | 124 | **79.7%** |

**An executed IA is an ~80% promise in ERCOT and roughly a coin-flip in MISO.** The same contract milestone carries fundamentally different completion information in the two regions — which means milestone-based comparisons (and developer capital decisions keyed to the IA) are not comparing like with like.

*Robustness: the gap does not depend on the definitional choice. Restricting to LBNL's own IA-year window (2000–2022) gives 34.8% vs 79.9%; restricting to fully mature cohorts (IAs 2000–2019) gives 32.9% vs 75.8%; counting suspended projects as not-built gives 34.9% vs 77.0%. Across every variant tested the spread stays between 42 and 45 points.*

## Step 3 — Where the time goes (median months, successful projects)

| | Request → IA | IA → COD | Request → COD |
|---|---:|---:|---:|
| **MISO** | 29.8 | 18.8 | 39.1 |
| **ERCOT** | 20.3 | 25.9 | 44.3 |

End-to-end, the regions are roughly tied (~3.5–4 years). ERCOT's edge is not total speed — it is **a faster path to a high-certainty contract**; MISO is slower to sign but builds faster after signing. Neither region "wins": they distribute certainty differently across the process.

## Implication for harmonization

Direct timeline and milestone comparisons between regions are structurally skewed until they are normalized for (1) the queue grouping asymmetry (cluster batch vs. serial request) and (2) the certainty content of each milestone. A harmonized reporting standard could publish **post-milestone completion rates** alongside timelines, so that "reached IA" means something comparable everywhere.

---

**Step 3 provenance.** Durations are my computation from the data file's `q_date` / `ia_date` / `on_date` fields, survivor-conditioned on projects that reached each milestone. LBNL publishes duration distributions on Sheets 29–40; I have not line-by-line reconciled against those, so treat Step 3 as mine rather than as a reconciliation.

**Independence.** Unfunded personal project. Not affiliated with, reviewed by, or endorsed by DOE, ESIG, or Berkeley Lab.

**Reproducibility.** Source: LBNL *Queued Up* data file, 2026 Edition (data through year-end 2025; public). Pipeline and interactive dashboard: `https://komposos-grid.streamlit.app` · code: `https://github.com/Jayhawk314/komposos-grid` (Apache-2.0; every figure above regenerates from the raw workbook with one command). I am glad to walk through any of it step by step — corrections especially welcome.
