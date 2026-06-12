# Grid Waste Project — Roadmap to a Lasting Instrument

Written 2026-06-12. Extends `PLAN.md` (whose A-D phases are complete)
from "working analysis" to "infrastructure other people rely on."
Companion reading: `reports/MASTER_GUIDE.md` (what the findings are),
`reports/agent_handoff.md` (current working state).

**The arc in one line:** screening instrument (done) → reproducible
evidence (Phase 0-1) → validated evidence (Phase 2) → paid evidence
(Phase 3) → public watchdog (Phase 4) → decision infrastructure
(Phase 5).

> **In plain English:** Right now this is a very good private
> analysis. The plan is to turn it into something with public
> standing — first by proving a stranger can check our math, then by
> letting an expert attack it, then by getting one customer to pay
> for it, then by publishing on a schedule until people cite it, and
> finally by becoming a tool that's part of how grid decisions get
> made. Each phase has a pass/fail test so we never fool ourselves.

---

## Decision points that belong to James (everything else can be agent work)

| # | Decision | Needed by |
|---|---|---|
| D1 | Make the `komposos-grid` repo public (or a cleaned mirror) | Phase 1 start |
| D2 | Check ISO/EIA data redistribution terms before selling anything (selling *analysis* of public data is normal practice; redistributing raw ISO files may not be — verify) | Phase 3 start |
| D3 | Who to approach for expert review and as design partners (warm intros beat cold email) | Phase 2-3 |
| D4 | Price for the first study (recommendation: low, $5-25k — the reference matters more than the revenue) | Phase 3 |

---

## Phase 0 — Stranger-proof the reproduction (prereq for M1)

*Goal: a person we've never met, on a machine we've never touched,
gets our headline number from a fresh clone in under one day.*

- [ ] **`REPRODUCE.md`** at repo root: one target number (recommend
      MISO-SWPP 2025: component spread **7.33 $/MWh** → corridor value
      **$31.1M/yr**), exact commands, expected runtime, expected output.
      Chosen because it is fully keyless and two-sided-corroborated.
- [ ] **Fetch script** (`domains/grid/fetch_data.py` or shell): downloads
      exactly the files the target number needs (MISO daily files via
      cache, EIA-930 2025 interchange), with sizes and resume handling.
      The gotchas are all documented in the handoff; encode them.
- [ ] **Clean-room test:** run the reproduction in a fresh clone +
      fresh venv on this machine (agent-runnable). Fix every friction
      point found. Pass = number matches to the cent without help.
- [ ] **Archive the perishable data** (OASIS has ~39-month retention;
      MISO/SPP files can move): zip the evidence-chain inputs for the
      headline numbers and store off-machine (user: pick a location —
      even a private GitHub release works). *Reproducibility dies
      silently when source data expires.*

**Exit test:** clean-room run passes twice in a row. ~Days of work.

## Phase 1 — M1: External reproduction (target: within ~1 month of D1)

*Goal: one outside person independently confirms a headline number.*

- [ ] D1: repo public, `MASTER_GUIDE.md` linked from README.
- [ ] Recruit 1-3 reproducers. Realistic pools: the gridstatus/energy
      data community, energy economics grad students, r/energy and
      energy-twitter data people, LBNL/NREL open-data circles.
      The ask is small and concrete: "clone, run, tell us if you get
      $31.1M." Offer named acknowledgment in the report.
- [ ] Treat every friction report as a bug; fix and tag a release
      (`v1.0-reproducible`).

**Exit test (M1, falsifiable):** a person with no prior contact with
the codebase posts/emails a matching number from their own run.

## Phase 2 — M2: Expert review (overlaps Phase 1)

*Goal: a domain expert tries to break the methodology and fails — or
breaks it, and we fix it (both outcomes are wins).*

- [ ] Package the review kit (mostly exists): MISO-SWPP memo,
      `grid_methodology_report.md` (the 8x proxy-correction story —
      lead with our own self-correction; it builds trust),
      two-sided seam corroboration, BA repair/review layer
      (`reports/ba_review_template.csv` — **the pending human review
      pass should happen before an external expert sees it**).
- [ ] Reviewer profiles, best-first: former RTO market-monitor staff
      (Potomac Economics alumni), RTO planning engineers, LBNL/NREL
      researchers (the queue data is theirs — natural contact point),
      energy economics faculty.
- [ ] Scope the ask: "find a methodological hole in the seam numbers
      or the corrections" — 2-4 hours of their time, not a referee job.

**Exit test (M2):** review completed; every hole found is either fixed
(with a test) or documented as a known limitation in MASTER_GUIDE §6.

## Phase 3 — M3: First paying design partner (target: 1-2 quarters)

*Goal: one organization pays for one corridor/siting study.*

- [ ] D2 (data licensing check) before any sale.
- [ ] **Productize what already exists:** the solution-study memo
      (`reports/solution_studies/*.md`) IS the product template —
      corridor value, trend, named constraints, project B/C gates,
      intake for the buyer's own cost quotes (`project_costs.csv`).
- [ ] Candidate buyers, in order of fit:
      1. **Storage developers** — siting against congestion is their
         core problem; our spread/constraint maps are direct input.
      2. **Large-load siting teams** (data centers) — the Atlas Power
         story is the cautionary tale; "don't be the next CHAWATCHAPAT"
         is a pitch that writes itself.
      3. **Transmission developers / GET vendors** (DLR, advanced
         conductors) — Patent Gate-Pioneer-style B/C evidence supports
         their project cases.
      4. **State energy offices** — FERC Order 1920 obliges benefit
         analysis they often can't produce in-house.
      5. (Adjacent, different product: FTR/congestion traders value
         the seam trends — only if comfortable with that market.)
- [ ] First study at reference pricing (D4); deliver in <4 weeks;
      get a quotable outcome.

**Exit test (M3):** money received, study delivered, partner agrees
to be referenced (even anonymously: "a storage developer").

## Phase 4 — The watchdog: recurring publication (after M1)

*Goal: published on a schedule until someone cites it.*

- [ ] **Monthly Grid Waste Pulse** (public): seam-trend table, CHPE
      tracker, constraint leaderboard. The daily job (B4) plus the
      date-parameterized loaders make this mostly invocation work —
      candidate for a scheduled agent once stable.
- [ ] **Quarterly evidence-graded ledger release:** versioned, citable
      (DOI via Zenodo is free), each number tagged measured /
      screening / bounded exactly as MASTER_GUIDE §6 does.
- [ ] **Evidence maintenance cadence** (the instrument must stay warm
      to stay credible):
      - **Sep 2026:** CHPE summer verdict — the single most important
        scheduled measurement on the books. Decides whether the
        $159.7M/yr NYIS-PJM value survives. If CHPE kills the
        headline, *publish that prominently* — the watchdog's asset
        is credibility, not any particular number.
      - Monthly: NYISO/MISO monthly zips, daily pulse health check.
      - Jan-Feb each year: full-year reruns (2026 evidence) across
        NYISO/MISO/SPP/ERCOT + EIA-930 flows; refresh all corridor
        values same-year.
- [ ] Submit the ledger where it can be used: FERC docket comments
      accept public evidence; reporters covering grid congestion
      need exactly these tables.

**Exit test:** one citation in a docket filing, regulatory comment,
or published article we didn't write.

## Phase 5 — Decision infrastructure (12+ months, after M1-M3)

*Goal: part of how decisions get made, not commentary on them.*

- Coverage: all seven US ISOs measured two-sided where possible;
  Southeast non-market seams bounded (the Right Kan machinery exists);
  constraint-level *dollars* (not severity indexes) via market-monitor
  reports — this is where the honest national congestion number
  ($8-20B/yr scale) becomes computable.
- **FERC 1920 benefit-check tooling:** planners must now file 20-year
  benefit analyses; an independent tool that re-computes their claimed
  benefits from public data has obvious standing. This is the
  "independent transmission monitor" role — a recognized policy
  proposal with no incumbent. It is the natural end-state identity
  for this system.
- Self-serve product: corridor dashboard + intake (the CSVs become a
  web form; the memos become generated reports per subscriber).
- The categorical engine's differentiator at this scale: every number
  carries its evidence chain (morphisms), every methodology correction
  is structural (2-cells), every bound is principled (Kan extensions) —
  i.e., **auditability is native**, which is exactly what a watchdog
  must have and dashboards-built-on-spreadsheets don't.

---

## Risks, stated plainly

| Risk | Reality check | Mitigation |
|---|---|---|
| CHPE erases the NY headline | Possible — first month shows mild relief only | Report it loudly either way; the wind-belt corridor is CHPE-immune |
| Expert finds a real hole (M2) | That's the gate working | Fix publicly; the 8x self-correction story proves we do this |
| Data expires (OASIS 39-month window) | Certain, on a clock | Phase 0 archive task — do not defer |
| One-person bus factor | Current state | Reproducibility (Phase 0-1) *is* the mitigation |
| ISO data terms vs paid product | Unverified | D2 before any sale; sell analysis, never raw redistribution |
| Nobody bites (M1/M3) | Possible | Gates are cheap to attempt; failure information is also valuable — it falsifies the product shape, per PLAN E's own logic |

## Sequencing and the next physical actions

```
Phase 0 (days)  ──>  M1 (≤1 mo after D1) ──> Phase 4 watchdog (monthly)
                └──> M2 (parallel)        ──> M3 (1-2 quarters) ──> Phase 5
```

Next three concrete actions, in order:
1. Write `REPRODUCE.md` + fetch script + clean-room test (agent work,
   can start immediately).
2. James: D1 decision (public repo) + human pass on
   `ba_review_template.csv` (blocks M2 packaging).
3. Calendar anchor: CHPE summer rerun in September 2026 — the one
   dated obligation in the portfolio.
