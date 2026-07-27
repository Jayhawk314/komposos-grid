---
name: verify-claim
description: Verify a quantitative interconnection-queue claim (e.g. "MISO post-IA completion is 35%") against this repo's LBNL-reconciled artifacts, recomputing from raw data if needed. Use for fact-checking webinar/panelist claims or the dashboard's own numbers.
argument-hint: "<the claim to verify, with region and metric>"
---

# Verify Claim — the Trust Walkthrough as a Procedure

Turn a quantitative claim into a CONFIRMED / CLOSE / MISMATCH / UNVERIFIABLE verdict with
the exact numbers and definitions shown. This is the repo's core credibility move: every
headline number must be traceable to Berkeley Lab's *Queued Up* file — reconciling to
their published tables to the integer where such a table exists, and labelled as our own
computation where it does not.

**Provenance boundary:** LBNL publishes the regional *completion* table (Sheet 25) — those counts reconcile to the integer. LBNL publishes post-IA completion **nationally only** (Sheet 27) and no regional duration split, so post-IA rates and durations here are our computation applying LBNL's methods. Do not present them as LBNL-published figures.

## Procedure

1. **Parse the claim** into (region, metric, value, cohort window if stated). Common metric
   vocabulary: "completion rate" (LBNL definition), "post-IA / after signing IA build rate",
   "withdrawal rate", "months to IA / to COD", "GW in queue", "requests in cycle X".

2. **Check the committed artifacts first** (cheap, already reconciled):
   - `reports/stitch_2026-06-23/queue_process_brief.json` — per region:
     `total_requests`, `decided`, `operational`, `active_in_queue`, `completion`,
     `completion_lbnl` (LBNL 2000–2020 definition), `post_ia`, `milestones`, `cycles`
     (DPP/entry-year cohorts), `durations` (request→IA, IA→COD medians).
   - `docs/webinar_engagement_and_verification_guide.md` §3 — the ground-truth reconciliation
     anchors (LBNL Sheets 25/27): MISO 2,445 decided = 509 built + 1,936 withdrawn; ERCOT
     1,254 = 459 + 795; post-IA MISO 476/1,365 ≈ 34.9%, ERCOT 486/610 ≈ 79.7%.

3. **Recompute from raw data if** the artifact doesn't cover the claim, the cohort window
   differs, or the user asks for a from-scratch check:
   ```bash
   python -m domains.grid.run_stitch_brief --with-peers
   ```
   Raw workbook: `domains/grid/data/LBNL_Ix_Queue_Data_File_thru2026.xlsx` (loader:
   `domains/grid/sources/lbnl_queue.py`). For ad-hoc slices, load the workbook with the
   loader and filter — do not hand-count rows in the xlsx.

4. **Compare and issue a verdict:**
   - **CONFIRMED** — matches to the integer (counts) or within rounding (rates). Show the
     arithmetic, e.g. `476 / 1,365 = 34.87% ≈ "35%"`.
   - **CLOSE** — right magnitude, small gap. Show both numbers and the most likely cause
     (different cohort window, vintage, or rounding).
   - **MISMATCH** — show both numbers and diagnose: different *definition* (LBNL completion
     = operational / (operational + withdrawn), decided 2000–2020 cohorts vs. all-time),
     different *milestone* (IA-executed vs. GIA vs. COD), or different *data vintage*.
   - **UNVERIFIABLE** — the repo has no data for it. Say so plainly. **Never estimate a
     verdict from memory or general knowledge.**

5. **Always state, in every verdict:** the definition used, the cohort window, the data
   vintage (LBNL thru-2026 workbook), and the provenance tier (these checks are
   📏 Measured). If the claim mixes regions, note the structural caveat: MISO cluster
   batches and ERCOT's serial process do not share a unit of work, so direct timeline
   comparisons need normalization.

## Guardrails

- Neutrality: when a verdict favors one region, also state the other region's offsetting
  strength (e.g., ERCOT wins on study speed and IA certainty; MISO wins on post-IA build
  speed; end-to-end is roughly a tie at ~3.5–4 years).
- If recomputation and the committed artifact disagree, that is itself the finding —
  report the drift, don't silently prefer one.
