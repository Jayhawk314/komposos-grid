# Agent Working Handoff — Grid Domain

Living document. Update at the end of every working session. Plan
lives in `domains/grid/PLAN.md`; Codex's earlier handoff is in
`reports/codex_session_handoff.md` (still accurate for the BA
repair/review layers).

## State as of 2026-06-12 (commit 68aa2d8, pushed to `grid` remote)

- Repo: https://github.com/Jayhawk314/komposos-grid (remote `grid`);
  `origin` points at the older KOMPOSOS-IV repo, untouched.
- Tests: 262 passing (`pytest tests/`). All grid work in
  `domains/grid/`, data in gitignored `domains/grid/data/`.
- Phases 0-3 complete: coherence (plant/facility/BA levels), sheaf
  audit, flow geometry, BA repair+review, dual-engine verification,
  queue factorization, curtailment, EAGLE-I reliability, congestion
  evidence (NYISO + CAISO OASIS + MISO interface + ICE hubs),
  waste ledger ($251.0M, 28 claims), action portfolio (12 actions),
  queue-to-bottleneck matching.

## Key headline numbers (2023, all reproducible from public data)

- Congestion: $78.6M/yr over 7 measured ties; OASIS validation cut
  the ICE proxies 7-9x (CISO-SRP $142M -> $14M) — annual hub level
  differences are NOT seam spreads; never reintroduce that method.
- Curtailment: CAISO 2.66 TWh, 78% congestion-driven, <=$172.5M.
- Reliability: 1.059B customer-hours lost (EAGLE-I, full year).
- Queue: 16.5% completion of 29,010 decided; IA-execution cohort 4x.
- Matching: 4,205 withdrawn projects (524 GW) could have relieved
  PJM-NYIS alone.

## Active blockers / user actions

- PJM Data Miner API key (free signup) — unlocks constraint-level
  PJM congestion + CPLE-PJM seam (PLAN A2).
- Human review pass on reports/ba_review_template.csv still pending.

## Gotchas for future agents

- OASIS: version=12 for PRC_LMP, prices in column named "MW",
  ~39-month retention, resume curl on connection resets.
- figshare throttles first connections; curl -C - resume converges.
- LBNL queue file is Cloudflare-gated: manual browser download only.
- eGRID merges multi-block facilities; EIA-923 splits them — always
  go through the facility crosswalk before plant-level joins.
- MISO daily files: 4 preamble rows, wide HE 1..24 format,
  interfaces (SOCO/SWPP/TVA/AECI/SPA) are priced nodes.
- PowerShell: pipe to Select-Object can kill python exit codes
  (exit 255 = truncated pipe, not failure); $ in inline python -c
  gets mangled — use script files.
- Old import paths (core.*, oracle.*) work via compat loaders +
  sitecustomize; real code is under src/komposos_core etc.

## Completed this session

- PLAN A1 DONE: reliability monetization
  (domains/grid/reliability_value.py + run_reliability_value.py).
  2023 result: floor $4.4B / blended $142.1B / high $176.8B per year.
  The blended figure independently converges on DOE's ~$150B national
  number from the bottom up — strong method corroboration. Worst
  states at blended rate: MI $17.2B, CA $16.8B, TX $14.8B.
  Artifacts: reports/reliability_valuation_2023.{json,md}.
  Coefficients are screening-grade (Sullivan 2015 $/kWh x assumed
  class loads x EIA-861-ish meter mix), all overridable; swapping in
  exact ICE 2.0 calculator values is a clean upgrade path.

## Next up (task list order)

- A2 (#14): constraint-level congestion costs — partially blocked on
  user getting a free PJM Data Miner key; MISO MCC files keyless.
- A3 (#15): SPP/ERCOT/ISO-NE loaders + 2024/2025 reruns.
- B4 (#16): daily streaming ledger job (EIA-930 poll).
- C5-7 (#17): 2-cell evidence reconciliation, right Kan bounds for
  Southeast seams, axiom-mine the proxy-overstatement lesson.
- D8 (#18): natural-experiment relief curves via pronoia/scm.py.
- Product gates (PLAN E): M1 external reproduction, M2 expert review,
  M3 paying design partner.
