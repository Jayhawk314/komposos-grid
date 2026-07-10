---
name: webinar-prep
description: Prepare for an upcoming i2X STITCH webinar - regenerate the analytical pipelines, diff every report figure against the committed baseline, flag drifted numbers, and draft a pre-read brief. Use before a STITCH session or when the user asks "what changed since last session".
argument-hint: "[session date or topic, if known]"
---

# Webinar Prep — the "What Changed Since Last Session" Sweep

Produce a pre-read brief for the next i2X STITCH session: fresh numbers, an explicit
old → new diff against the last session's committed figures, and flags for anything that
drifted enough to change a talking point.

## Procedure

1. **Snapshot the baseline.** Note the git status of `reports/` first — the committed
   versions of the report JSONs *are* the last-session baseline. Don't lose them: work on
   a clean tree or record `git stash` / branch state before regenerating.

2. **Regenerate the pipelines** (order doesn't matter; each is independent):
   ```bash
   python -m domains.grid.run_stitch_brief --with-peers      # 9-region queue study
   python -m domains.grid.run_untapped_analytics             # seam opportunity analytics
   python -m domains.grid.experiments.large_load_coordination # ESIG large-load scenario
   python -m domains.grid.run_dashboard                       # static HTML dashboard
   ```
   Then run the test suite: `python -m pytest tests/test_grid_same_year_flows.py tests/test_grid_solution_cards.py -q`.

3. **Diff the figures.** `git diff reports/` and summarize *numerically*: for each changed
   JSON, list the headline metrics old → new (completion rates, post-IA rates, hub spreads,
   seam congestion $/MWh, cycle GW totals). Ignore formatting-only churn.

4. **Flag drift that changes talking points.** A change matters if it would alter a
   sentence someone says on the webinar — e.g., a completion rate crossing a round number,
   a spread changing sign of trend, a new DPP cycle appearing. List these under
   "⚠ Update your slide if you cite this."

5. **Draft the pre-read brief** at `reports/stitch_<session-date>/preread_brief.md`:
   - What changed since the last session (the diff from step 3–4)
   - 3–5 discussion hooks tied to the session topic (check the session list in
     `streamlit_app.py` sidebar and `docs/webinar_research_brief.md` for context)
   - Data vintages and provenance tier for every number cited
   - Anything time-sensitive on the large-load front (e.g., ERCOT Batch Zero milestones)

6. **Report to the user:** the numeric diff summary, the flagged talking-point changes,
   test results, and the path to the draft brief. Ask before committing anything.

## Guardrails

- Every number in the brief carries its provenance tier (📏 Measured / 🧮 Derived /
  🧪 Simulated) and data vintage. Mixed-provenance sentences are not allowed.
- Neutral framing across regions — the brief is arbitration infrastructure, not advocacy.
- If a pipeline fails, report the failure and use the committed baseline for that section,
  clearly marked as stale — never present half-regenerated numbers as fresh.
