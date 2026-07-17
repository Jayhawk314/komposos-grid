# Audit Working Copy — Scientific Accuracy & Communication Fixes

*Opened 2026-07-17 from the full scientific/accuracy audit + engineer/community review.
This is the living checklist: every finding, its fix, and its status. Update statuses as work lands.
Statuses: `OPEN` · `IN PROGRESS` · `FIXED` · `PARKED (deliberate)` · `VERIFY EXTERNALLY (needs human/source check)`*

---

## How to read this

The audit found the repo splits cleanly into three tiers:

1. **Verified core** — LBNL queue pipeline (recomputed from raw workbook 2026-07-17, exact match), congestion evidence chain with OASIS validation, provenance-badge system. *Protect this.*
2. **Defensible but oversold** — seam screening math (real computation, overclaimed language), large-load simulation (labeled in UI, overclaimed in report md).
3. **Unsourced or wrong** — harmonization matrix (hand-typed, uncited), nuclear page factual claims, session notes presented as minutes.

The strategy: quarantine tier 3, soften tier 2's language, never let either wear tier 1's styling.

---

## A. Scientific-accuracy findings

### F1 — Harmonization Matrix presented as measured deliverable — `FIXED (relabeled)` → full sourcing still `OPEN`
- **What:** `HARM_DATA` dict in `streamlit_app.py` is hand-typed ✅/⚠️/❌ with zero citations, yet the page called itself "the i2X STITCH core deliverable" and computed "alignment scores" and "priority gaps" from it.
- **Fix applied:** Warning banner declaring it an uncited working hypothesis; "core deliverable" language removed; session-finding blocks relabeled as author's notes.
- **Remaining:** Source every cell to a tariff / BPM / RTO presentation, or delete rows that can't be sourced. Until then the banner stays.

### F2 — Affiliation ambiguity with ESIG / Berkeley Lab / DOE — `FIXED`
- **What:** Sidebar "ESIG · Berkeley Lab · i2X STITCH", page title "Komposos Grid · i2X STITCH", badge on every page — reads as official affiliation. There is none.
- **Fix applied:** Page retitled "Komposos Grid — Independent Interconnection Analytics"; sidebar caption and info box now state independence explicitly ("Not affiliated with or endorsed by DOE, ESIG, or Berkeley Lab"); badge prefix now says "Independent analysis".

### F3 — Session notes presented as minutes of a real meeting — `FIXED (relabeled)` + `VERIFY EXTERNALLY`
- **What:** "Key Discussion Outputs" and topic checklist for the June 23 session are written as a record of what named professionals presented. If reconstructed rather than transcribed, this misattributes.
- **Fix applied:** Caption added: author's takeaways, not official minutes, verify against ESIG recording before quoting.
- **Human action required:** James — check each bullet against your own notes/recording of June 23. Delete any bullet you can't personally vouch for.

### F4 — Nuclear page factual errors — `FIXED (text)` · deeper rework `PARKED (deliberate)`
- **(a)** "zero commercial HALEU capacity" — false (Centrus Piketon producing since late 2023, ~900 kg/yr demo scale). → Fixed to "far below projected SMR fleet needs" with Centrus mention.
- **(b)** McClean Lake is a mill (Orano, Saskatchewan), not a mine; Metropolis is Honeywell's plant, ConverDyn is the marketing venture. → Comments fixed in `domains/nuclear/ingest.py`.
- **(c)** `comprehensive_nuclear_analysis.md` labels +0.25 curvature edges "BOTTLENECK" while its own legend says negative = bottleneck. → Check generator labeling logic in `run_comprehensive_analysis.py` / `flow_geometry.py`; regenerate report. Status: see F4c note at bottom of file after inspection.
- **(d)** "Claim Confidence 0.100" constant across all 5 scenarios — the claim check adds no information. → `OPEN` (needs either a claim check that responds to scenario changes, or removal of the column).
- **(e)** ACT-003 proposed running enrichment cascades on intermittent curtailment energy — physically dubious (centrifuges need continuous high-reliability power). → Fixed to firm-power framing with the physical caveat stated.
- **(f)** Page-level: whole page now carries a `simulated` provenance badge and "illustrative systems model" language. Deeper question — whether this page belongs in the STITCH-facing app at all — parked until the app is reorganized by audience (see C1).

### F5 — Seam Opportunity Screen oversells its math — `FIXED (language + dynamic values)`
- **(a)** "Right Kan Extension… mathematically rigorous lower-bound" — implementation is neighbor-spread transfer (often n=1 neighbor); an adjacent tie's spread does not bound a different interface. → Reframed as screening proxy / analogy; `structural_only` status now stated on the page (matches the README, which was already honest).
- **(b)** Yoneda 0.3011 called "high structural similarity… prime candidates for transfer". → Now computed dynamically from the JSON and framed as moderate-similarity screening candidates.
- **(c)** "dual-verified verification that accounting adjustments improve macroscopic flow physics" — corrections improve dataset consistency, not physics. → Reworded.
- **(d)** Headline numbers were hardcoded in `st.info` strings and would drift on regeneration. → Now read from `untapped_analytics.json`.
- **(e)** "actionable investment indicators" → "screening indicators… not investment advice".

### F6 — UI display bugs — `FIXED`
- **(a)** SPP detail view showed "Built after Signing IA: 0.0%" when the milestone isn't tracked (`signed_decided=0`). → Shows "— not tracked".
- **(b)** "Active Stalled in Queue" mislabeled all active projects as stalled. → "Active in Queue".

### F7 — Large-load report blurs simulation and finding — `FIXED (framing)` + `VERIFY EXTERNALLY`
- **What:** `reports/experiments/esig_large_loads_audit.md` reported "Key Findings" (31.2 mo, 40% withdrawal) that are baked-in assumptions, with NPV quoted to the cent.
- **Fix applied:** Reframed as illustrative, assumption-driven results; NPV rounded to $M with a precision note. UI already carried the `simulated` badge (kept).
- **Human/external action:** Verify the exact ESIG report title and date cited ("Interconnection Processes for Large Loads…", June 2026) against ESIG's publication page before any external use.

### F8 — No single canonical "current totals" — `OPEN`
- **What:** README narrates $398.2M → $224.9M → $251.0M across phases; `docs/index.html` carries corridor figures; ledger/portfolio have their own totals. A quoter will pick the wrong number.
- **Fix plan:** One dated "Current headline totals" block (likely generated into `reports/` and included by README + index.html + app), everything else linking to it. Do together with C1 reorganization.

### F9 — `science_informatics_audit.py` is a demo, not an audit — `FIXED (relabeled)`
- **What:** Audits 1–3 construct fixtures and assert the detector detects them (can only pass); audit 4 is chem-domain. "ALL AUDITS PASSED" = false assurance.
- **Fix applied:** Docstring and output banners relabeled as demonstration suite. Real verification lives in `/webinar-prep` (regeneration diff) and `/verify-claim` (recompute from raw).

---

## B. Verification log

| Claim | Method | Result |
|---|---|---|
| MISO post-IA completion 34.9% (476/1,365) | Recomputed from raw `LBNL_Ix_Queue_Data_File_thru2026.xlsx` via repo loader, 2026-07-17 | ✅ exact match |
| MISO LBNL completion 18.1% (509/2,806, 2000–2020) | same | ✅ exact match |
| Committed `queue_process_brief.json` vs fresh recompute | same | ✅ match |
| Grid unit tests | `pytest tests/test_grid_same_year_flows.py tests/test_grid_solution_cards.py` | ✅ 6/6 pass |
| One-pager full number set (MISO+ERCOT decided/built/withdrawn, post-IA, durations) | `/verify-claim` runs | see §B2 below (fill in after runs) |
| "13% of 2000–2019 capacity operational by end 2024; 77% withdrawn" (stitch_original_brief.md) | Should be checked against `Queued Up 2025 Edition` PDF in `domains/grid/data/` | `OPEN` |
| ESIG large-loads report citation (title/date) | Web check | `OPEN` |

### B2 — /verify-claim results for the outreach one-pager

**Run 2026-07-17.** Method: full recompute from the raw workbook
(`domains/grid/data/LBNL_Ix_Queue_Data_File_thru2026.xlsx`) via the repo loader
(`LBNLQueueSource`) and the brief's own functions (`lbnl_completion`, `post_ia_completion`,
`duration_report`), cross-checked against the committed
`reports/stitch_2026-06-23/queue_process_brief.json`. Provenance tier: 📏 Measured.
Definitions: LBNL 2000–2020 request window; completion = operational ÷ all 2000–2020 requests
(including still-active); post-IA = built ÷ (built + withdrawn) among IA-executed decided projects
(LBNL Sheet 25/27 methodology). Data vintage: LBNL *Queued Up* thru-2026 workbook.

| One-pager claim | Recomputed | Verdict |
|---|---|---|
| MISO decided 2,445 = 509 built + 1,936 withdrawn | 2,445 = 509 + 1,936 | ✅ CONFIRMED |
| MISO completion 18.1% (509/2,806) | 509/2,806 = 18.1397% | ✅ CONFIRMED |
| MISO executed IA 1,365 · built 476 · withdrew 889 · 34.9% | 1,365 · 476 · 889 · 34.8718% | ✅ CONFIRMED |
| MISO medians 29.8 / 18.8 / 39.1 mo | 29.8 (n=1,760) / 18.8 (n=338) / 39.1 (n=539) | ✅ CONFIRMED |
| ERCOT decided 1,254 = 459 built + 795 withdrawn | 1,254 = 459 + 795 | ✅ CONFIRMED |
| ERCOT completion 29.6% (459/1,553) | 459/1,553 = 29.5557% | ✅ CONFIRMED |
| ERCOT executed IA 610 · built 486 · withdrew 124 · 79.7% | 610 · 486 · 124 · 79.6721% | ✅ CONFIRMED |
| ERCOT medians 20.3 / 25.9 / 44.3 mo | 20.3 (n=1,174) / 25.9 (n=424) / 44.3 (n=480) | ✅ CONFIRMED |

**All 22 numbers CONFIRMED to the integer / within rounding.** Committed artifact and fresh
recompute agree exactly (no drift).

Structural caveat to carry when quoting: MISO cluster batches and ERCOT's serial process do not
share a unit of work — direct timeline comparisons need normalization. Neutrality note: ERCOT
wins study speed and IA certainty; MISO wins post-IA build speed; end-to-end is roughly a tie
(~3.5–4 years).

Side finding fixed during the run: `docs/webinar_engagement_and_verification_guide.md` Step 2
stated the completion formula as `Operational / (Operational + Withdrawn)` while showing the
all-requests-denominator number (18.1% = 509/2,806). Formula text corrected to the actual
LBNL definition. The one-pager itself was already correct.

Still `OPEN` (external checks a human should do before sending): (1) spot-check the sheet-25/27
anchors against the *Queued Up 2025* PDF tables; (2) confirm the ESIG large-loads report
citation; (3) confirm the Streamlit URL is live.

---

## C. Communication / engineering findings (the "engineer hat" list)

### C1 — Navigation is a flat list of 9 pages in 3 vocabularies — `OPEN`
Reorganize by audience question per `docs/WHOLE_GRID_ROADMAP.md`: Queues & Milestones / Seams & Congestion / Large Loads / Fuel & Firm Supply / Methods & Data. IA-certainty spectrum on the landing page. Decide fate of nuclear page placement here (see F4f).

### C2 — Category-theory vocabulary front-of-house — `PARTIALLY FIXED`
Worst instances softened (Kan tab, fibration phrasing, quantale references in body text). Full pass: keep every mathematical term one click down in a methods layer; plain-English claim first. Remaining instances: nuclear page tab internals, grid_map_manual, agent pages.

### C3 — Two apps exist (`streamlit_app.py`, `grid_app.py`) — `OPEN`
Pick one; archive the other. Also: uncommitted dev hack (module-reload loop on nuclear page) should not ship; forced dark CSS ignores viewer theme.

### C4 — Outreach sequencing — `IN PROGRESS`
1. ✅ Disclaimer + quarantine + bug fixes (this pass)
2. `/verify-claim` on one-pager numbers (this pass, §B2)
3. Export one-pager to PDF; confirm Streamlit URL live and current
4. Send the prepared ESIG outreach email (draft kept locally, not in the public repo) — natural hook: "ahead of the July 28 session" (registry: 2026-07-28, 08-18, 09-22)
5. Optional parallel: public one-pager on GitHub/LinkedIn

### C5 — Repo/folder hygiene — `OPEN (low priority)`
Many `" - Copy"` duplicates and .zip snapshots in the parent folder; canonical version of each repo should be unambiguous. Root repo also carries unrelated artifacts (`scratch.pdf`, kids' math book, story md) that dilute the professional impression if the repo is shared — decide what stays in a public grid-facing repo.

---

## Guardrails (carry into every future change)

- Never let hand-typed or simulated content carry `measured` styling or "deliverable"/"finding" framing.
- Every number shown in the UI must be read from a generated artifact, never retyped into a string.
- Any claim naming a real person or organization must be verifiable from a primary source James actually possesses.
- Validation is allowed to shrink our numbers — that is the system working (Phase-3 precedent). Say so out loud.
- Screening ≠ measurement ≠ bound. Use the exact word.
