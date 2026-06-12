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

- PLAN A2 keyless half DONE: MISO binding-constraint severity
  (sources/miso_constraints.py + run_miso_constraints.py; needs xlrd,
  now in requirements.txt). Full-year 2023, 365/365 days: 2,463
  constraints, 10.07M $/MWh-hours severity. Headline: the top
  constraints are the Upper-Midwest wind belt (Charlie Creek-Watford
  ND bound 5,138 h = 59% of the year; WAUE/OTP/NSP/ALTW dominate) —
  MISO's deepest congestion is wind export, not the southern seams.
  Severity is an index, NOT dollars (flow MW not public); dollars
  arrive via PJM key or market-monitor data.
  Artifacts: reports/miso_constraints_2023.{json,md}.
  da_bc.xls gotcha: file named by publish date, market date inside is
  +1 day; header is row 2 under banners; xls needs xlrd.

- PLAN A2 DONE (no user key needed): pjm_dataminer.py uses PJM's
  public subscription key (dataminer2 settings.json) + DoH fallback
  (Google 8.8.8.8) for flaky resolvers. Feed is da_marginal_value
  (da_transconstraints has no shadow prices). 2023: 857 constraints,
  3.81M severity; Nottingham 230kV binds 69% of the year. M2M
  flowgates (Chicago-Praxair3, Turkey Hill-Hilgard) rank high in BOTH
  MISO and PJM tables — cross-ISO corroboration.
- PLAN A3 underway: SPP loaders done (sources/spp.py, run_spp.py;
  portal.spp.org file-browser-api, keyless; older years live in
  yearly zips path=/2023/2023.zip with NESTED .csv.zip rollups).
  2023 results: SPP curtailed 10.37 TWh (4x CAISO!), 82% Redispatch
  (congestion-driven) — the wires-problem finding replicates. 1,532
  DA constraints, 7.78M severity; top constraint CHAWATCHAPAT (5,951
  binding h) matches MISO's Charlie Creek-Watford corridor profile
  (likely same M2M iron — verify before claiming as fact).
  Outstanding in A3: SPP-side seam LMP (yearly zip download was in
  flight), ERCOT/ISO-NE loaders, 2024/2025 reruns.

## Next up (task list order)

- A3 (#15) remainder, then B4 daily job, C5-7, D8 (see PLAN.md).
- A3 (#15): SPP/ERCOT/ISO-NE loaders + 2024/2025 reruns.
- B4 (#16): daily streaming ledger job (EIA-930 poll).
- C5-7 (#17): 2-cell evidence reconciliation, right Kan bounds for
  Southeast seams, axiom-mine the proxy-overstatement lesson.
- D8 (#18): natural-experiment relief curves via pronoia/scm.py.
- Product gates (PLAN E): M1 external reproduction, M2 expert review,
  M3 paying design partner.
