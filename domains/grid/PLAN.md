# Grid Domain — Phase 4 Plan: Scale the Ledger, Earn the Product

Written 2026-06-12. Tracks the four weaknesses identified after Phase 3
and the path to a product. Work items are mirrored in the session task
list; status updates live in `reports/agent_handoff.md`.

**Status 2026-06-12: A-D are complete.** The E milestones are now
expanded into a full phased roadmap: `domains/grid/ROADMAP.md`.

## A. Coverage: from $251M to national scale

1. **Reliability monetization** (largest single jump, in progress).
   Value EAGLE-I customer-hours with LBNL interruption-cost
   coefficients (Sullivan et al. 2015, $/unserved kWh by customer
   class; ICE 2.0 update 2025). Output a low/mid/high range:
   residential-only floor vs class-blended estimates. Expected scale:
   $4B-$140B/yr nationally — consistent with DOE's ~$150B figure.
2. **Constraint-level congestion costs.** Replace tie-spread proxies
   with the congestion dollars ISOs actually publish (PJM State of the
   Market by constraint, MISO MCC reports). Needs a free PJM Data
   Miner key (user action) for the PJM API; MISO/SPP files are
   keyless. This is where the $8-20B/yr national congestion number
   becomes reachable honestly.
3. **Breadth**: SPP / ERCOT / ISO-NE seam loaders (same pattern as
   sources/miso.py); rerun everything for 2024 and 2025 (retention
   favors recent years; OASIS only has Apr 2023+).

## B. Static -> streaming

4. **Daily ledger job.** Poll EIA-930 API + ISO daily files,
   incrementally update the Category (hooks exist), re-emit ledger
   and dashboards. "Yesterday's waste every morning." Candidate for a
   scheduled agent once stable. True 5-min streaming via gridstatus
   real-time feeds is a later step.

## C. Categorical layer: earn its keep

5. **2-cells for evidence reconciliation.** The ICE-vs-OASIS
   correction (annual level proxy vs settlement truth) is a 2-cell
   between parallel evidence morphisms. Formalize so methodology
   corrections are tracked structurally, not just in git history.
6. **Right Kan extension for unpriceable seams.** Southeast ties have
   priced neighbors; Rightt Kan along the adjacency functor = the most
   conservative estimate consistent with measurements. Turns "no
   market exists" into a bounded claim.
7. **Axiom mining on evidence episodes.** Teach System 3 the learned
   lesson "annual hub-level proxies overstate hourly seam spreads
   7-9x" via zfc/axiom_miner.py; auto-flag future proxies of that
   shape.

## D. Toward causality

8. **Natural-experiment relief curves.** ISO binding-constraint and
   outage event data = capacity-change experiments per seam. Fit
   empirical spread-vs-capacity curves (home: pronoia/scm.py), add
   public transmission/storage cost benchmarks, rank interventions by
   cost-per-relieved-dollar. Upgrades queue-matching from screening to
   recommendation.

## E. Product shape (decision made: open-core + report product)

- Publish referent layer (crosswalks) + ledger methodology openly.
- Sell the recurring evidence-graded waste ledger and bespoke
  seam/siting studies.
- **Gate scaling on three falsifiable milestones:**
  M1: an outside person reproduces the ledger from a fresh clone.
  M2: a domain expert reviews BA corrections + seam numbers without
      finding a methodological hole.
  M3: one design partner pays for one study.

## Sequencing

A1 (now) -> A2/PJM key (user) -> B4 daily job -> C5-7 alongside ->
A3 breadth -> D8 -> E milestones. Each item lands as: module + tests +
real-data run + report artifact + handoff update + commit/push.
