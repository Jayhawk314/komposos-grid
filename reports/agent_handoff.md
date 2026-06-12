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
- A3 continued: SPP-side MISO seam from the yearly LMP archive
  (seam_from_lmp_zip; monthly rollups inside, wide HE01-24 format
  with stray leading spaces in headers): $6.12/MWh mean |spread|,
  91% congestion component — corroborates MISO-side $5.09 within
  ~20%. FIRST TWO-SIDED SEAM MEASUREMENT. Kept MISO-side as the
  ledger evidence row (one row per tie; SPP side is corroboration in
  reports/spp_2023.json, do NOT double-count).
- A3 continued: ERCOT loader (sources/ercot.py; keyless yearly
  DAMLZHBSPP zips via IceDocListJsonWS reportTypeId=13060).
  West-North wind congestion grows: $4.94 (2023) -> $5.40 (2024) ->
  $5.78/MWh (2025), West above North ~2/3 of hours.
  reports/ercot_hub_spreads.{json,md}.

- A3 reruns, NYISO 2024+2025 (reports/nyiso_seam_2024_2025.txt):
  PJM-NYIS seam spread is EXPLODING year-over-year —
  2023 $2.01 -> 2024 $2.78 -> 2025 $9.03/MWh mean |spread|
  (congestion component $1.53 -> $2.02 -> $7.38; NY above PJM 97.9%
  of hours in 2025). The 2025 component implies ~$142M/yr on this tie
  alone, 5x the 2023 ledger figure. Pattern matches ERCOT's rising
  West-North trend: load growth vs stalled queue, visible in prices.

## A3 remainder / Next up

- A3: ISO-NE loader (iso-ne.com static CSVs, keyless) — low seam
  relevance, breadth only; 2024/2025 reruns of NYISO/MISO/OASIS
  evidence chains (loaders are date-parameterized; just invocations
  + new evidence files).
- Then B4 daily job, C5-7 categorical upgrades, D8 relief curves
  (see PLAN.md).
- A3 (#15): SPP/ERCOT/ISO-NE loaders + 2024/2025 reruns.
- B4 (#16): daily streaming ledger job (EIA-930 poll).
- C5-7 (#17): 2-cell evidence reconciliation, right Kan bounds for
  Southeast seams, axiom-mine the proxy-overstatement lesson.
- D8 (#18): natural-experiment relief curves via pronoia/scm.py.
- Product gates (PLAN E): M1 external reproduction, M2 expert review,
  M3 paying design partner.

## State as of 2026-06-12 (Codex continuation after commit eb9f8e9)

- PLAN B4 daily pulse was already committed at `eb9f8e9` before this
  continuation. I did not change it.
- PLAN C5-C7 DONE:
  - Added `domains/grid/methodology.py` and
    `domains/grid/run_methodology.py`.
  - C5: formalized proxy-to-settlement methodology corrections as
    2-cells using `categorical.two_categories.TwoCategory`.
  - C6: added conservative Right Kan bounds for unpriced Southeast
    structural ties. These are explicitly bounded screening claims,
    not measured congestion costs.
  - C7: mined the repeated hub-proxy correction into a methodology
    axiom: hub-level proxies without a settlement/nodal correction
    2-cell stay screening-only.
  - Generated `reports/grid_methodology_report.{md,json}`,
    `reports/grid_methodology_corrections.csv`,
    `reports/grid_right_kan_bounds.csv`, and
    `reports/grid_proxy_warnings.csv`.
  - Result: 2 correction 2-cells, mean proxy overstatement 8.0x.
    CISO-SRP corrected 14.03 -> 1.55 $/MWh (9.0x);
    BPAT-CISO corrected 9.47 -> 1.37 $/MWh (6.9x).
    Five Right Kan bounds were emitted; AECI-TVA remains unbounded
    because no adjacent priced measurement exists in the current report.
- PLAN D8 FIRST PASS DONE:
  - Added `domains/grid/relief_curves.py` and
    `domains/grid/run_relief_curves.py`.
  - Uses `pronoia.scm.SCM` for deterministic `do(capacity_mw=x)`
    relief curves over priced queue-match ties.
  - Attaches MISO/PJM/SPP named constraint context where available.
  - Adds annualized screening benchmarks for transmission capacity,
    4-hour grid storage, and flexible load. These are overrideable
    defaults; project-specific cost estimates should replace them for
    any decision-grade study.
  - Generated `reports/grid_relief_curves.{md,json,csv}` and
    `reports/grid_relief_curve_points.csv`.
  - Result: five priced ties evaluated. None of the generic benchmark
    interventions clears B/C > 1 at the default annualized costs.
    MISO-SWPP ranks first, with 50 MW transmission-capacity relief at
    about $2.0M/yr benefit vs $7.5M/yr annualized cost.
- Validation:
  - Focused new tests: `6 passed`.
  - Nearby grid tests: `27 passed` across methodology, relief curves,
    congestion evidence, waste ledger, action portfolio, and queue matching.
  - Full local suite: `285 passed`.
- A3 caution:
  - Two MISO rerun artifacts appeared in the worktree during this
    continuation and were not authored here:
    `reports/miso_seam_2024.txt` modified and
    `reports/miso_seam_evidence_2024.csv` untracked.
  - I intentionally left them out of the C5-C7/D8 commit so the A3
    rerun can be reviewed/closed separately.

## State as of 2026-06-12 (solution-card continuation)

- User explicitly pointed at the MISO 2024 rerun artifacts and asked to
  learn them:
  - `reports/miso_seam_2024.txt`
  - `reports/miso_seam_evidence_2024.csv`
- Learned A3 update:
  - MISO-SOCO 2024: 8,736 hours, 2 missing report days, mean |spread|
    1.77 $/MWh, congestion component 1.53 $/MWh, congestion is 86.8%
    of mean spread.
  - MISO-SWPP 2024: 8,736 hours, 2 missing report days, mean |spread|
    6.63 $/MWh, congestion component 6.31 $/MWh, congestion is 95.2%
    of mean spread.
  - MISO-SWPP worsened versus 2023 component evidence
    (4.74 -> 6.31 $/MWh); MISO-SOCO also rose
    (1.35 -> 1.53 $/MWh).
- Added solution cards:
  - `domains/grid/solution_cards.py`
  - `domains/grid/run_solution_cards.py`
  - `tests/test_grid_solution_cards.py`
  - Generated `reports/energy_solution_cards.{md,json,csv}`.
- Current solution-card ranking:
  - PJM-NYIS: priority solution study. Uses the 2025 NYISO component
    trend, 7.38 $/MWh, about $142.4M/yr on the current gross-flow
    baseline, generic B/C 0.43.
  - MISO-SWPP: priority solution study. Uses the learned 2024 MISO
    component, 6.31 $/MWh, about $25.2M/yr, generic B/C 0.35.
  - CISO-SRP and BPAT-CISO: methodology-validated Western screens
    using OASIS-corrected values, not old ICE hub proxies.
  - MISO-SOCO: bounded Southeast solution screen, useful mostly as an
    anchor for Southeast pricing/bounds unless better evidence arrives.
  - ERCOT West-North: watchlist only until ERCOT-specific queue and
    constraint evidence are attached.
- Important interpretation:
  - Generic benchmark interventions still do not clear B/C > 1.
    The next useful move is project-specific costing for PJM-NYIS 2025
    and MISO-SWPP 2024, not another generic cost curve.
- Validation:
  - Solution-card focused tests: `3 passed`.
  - Nearby grid tests: `15 passed`.
  - Full local suite: `288 passed`.

## State as of 2026-06-12 (project-specific solution studies)

- User asked to do all four next steps: PJM-NYIS 2025 study,
  MISO-SWPP wind-belt study, replacement of generic costs, and
  audience-ready memos.
- Added:
  - `domains/grid/solution_studies.py`
  - `domains/grid/run_solution_studies.py`
  - `tests/test_grid_solution_studies.py`
- Generated:
  - `reports/energy_solution_studies.md`
  - `reports/energy_solution_studies.json`
  - `reports/energy_solution_studies.csv`
  - `reports/energy_solution_interventions.csv`
  - `reports/energy_solution_cost_assumptions.csv`
  - `reports/solution_studies/nyis_pjm.md`
  - `reports/solution_studies/miso_swpp.md`
- What changed methodologically:
  - Replaced generic B/C framing with project-cost break-even gates.
    The reports now answer: "what real annual cost / capex can this
    corridor support before congestion value alone stops clearing?"
  - Uses a 10% fixed-charge-rate default for break-even capex envelopes.
  - Storage assumption is tied to the NREL ATB utility-scale battery
    storage methodology URL in the assumptions CSV, but the memo does
    not claim storage clears on seam value alone.
- PJM-NYIS 2025 memo:
  - Current spread: 7.38 $/MWh.
  - Annual value: about $142.4M/yr.
  - 50 MW targeted transfer gate: $3.23M/yr annual cost,
    $32.3M capex at 10% FCR, $646/kW.
  - 250 MW targeted transfer gate: $16.2M/yr annual cost,
    $161.6M capex, $646/kW.
  - 100 MW 4-hour storage gate: only $8.9M capex, $89/kW, so storage
    does not clear from seam congestion value alone unless stacked with
    other value streams.
  - Next action: price top PJM-side active projects and a small
    transfer upgrade; rerun gross-flow/evidence on 2025 before final
    investment case.
- MISO-SWPP wind-belt memo:
  - Current spread: 6.31 $/MWh.
  - Annual value: about $25.2M/yr.
  - 50 MW targeted transfer gate: $2.76M/yr annual cost,
    $27.6M capex at 10% FCR, $553/kW.
  - 250 MW targeted transfer gate: $13.8M/yr annual cost,
    $138.2M capex, $553/kW.
  - 100 MW 4-hour storage gate: only $7.6M capex, $76/kW, so storage
    needs local energy/capacity stacking.
  - Next action: map CHAWATCHAPAT and Charlie Creek-Watford to specific
    upgrade candidates and price a 50-100 MW relief package.
- Validation:
  - Solution-study focused tests: `2 passed`.
  - Focused nearby tests: `8 passed`.
  - Full local suite: `290 passed`.

## State as of 2026-06-12 (solution-study intake gates, commit 54c38f2)

- Latest commit: `54c38f2 Add solution study intake gates`.
- Worktree was clean immediately after the commit.
- Added same-year flow and quoted project-cost intake to the solution-study
  path:
  - `domains/grid/solution_studies.py`
  - `domains/grid/run_solution_studies.py`
  - `tests/test_grid_solution_studies.py`
- New CLI inputs:
  - `--same-year-flow <csv>`: replaces the older gross-flow baseline for a
    corridor/year when a same-year EIA-930/ISO flow row is available.
  - `--project-costs <csv>`: evaluates actual quoted capex/O&M or explicit
    annual cost against the corridor's congestion-relief value.
- New generated artifacts:
  - `reports/energy_solution_flow_status.csv`
  - `reports/same_year_flow_template.csv`
  - `reports/project_cost_template.csv`
  - `reports/project_cost_results.csv`
- Current evidence status:
  - Only 2023 bulk EIA-930 BALANCE/INTERCHANGE files were found locally.
  - NYIS-PJM 2025 is therefore flagged `needs_same_year_flow`; current value
    remains `$142.4M/yr` from 7.38 $/MWh applied to the 2023 gross-flow
    baseline of 19,294,263 MWh.
  - MISO-SWPP 2024 is also flagged `needs_same_year_flow`; current value
    remains `$25.2M/yr` from 6.31 $/MWh applied to the 2023 gross-flow
    baseline of 3,989,884 MWh.
  - This is intentional: the reports now show when price year and flow year
    do not match, rather than silently treating the baseline as final.
- Project-cost intake behavior:
  - Blank template rows are ignored.
  - If `annual_cost_usd` is provided, B/C uses that explicit annual cost.
  - Otherwise annual cost is `capex_usd * fixed_charge_rate + annual_om_usd`.
  - Relief MWh is capped by corridor gross flow, so a project cannot claim
    more relieved congestion than the tie's observed gross-flow envelope.
  - `reports/project_cost_results.csv` currently has only headers because no
    real quoted costs were supplied yet.
- To rerun after filling templates:

```powershell
python -m domains.grid.run_solution_studies `
  --same-year-flow reports\same_year_flow_template.csv `
  --project-costs reports\project_cost_template.csv
```

- Validation:
  - Focused solution-study tests: `4 passed`.
  - Full local suite: `432 passed, 2 skipped`.

## State as of 2026-06-12 (same-year flow gates CLOSED)

- Downloaded keyless EIA-930 INTERCHANGE six-month files for 2024 and
  2025 (eia.gov/electricity/gridmonitor/sixMonthFiles/, ~100MB each,
  curl -C - resume; now in gitignored domains/grid/data/).
- Added `domains/grid/same_year_flows.py` + `run_same_year_flows.py` +
  `tests/test_grid_same_year_flows.py` (3 tests). Extraction reuses
  `flow_geometry.load_interchange` (sum |hourly flow|, one reporter per
  pair) so cross-year numbers stay comparable with the 2023 baseline.
- Evidence file: `reports/same_year_flows.csv` (committed; both pairs,
  both years):
  - NYIS-PJM 2025: gross 21,635,807 MWh (+12% vs 2023 baseline 19.29M),
    net -21,635,807 — tie ran PJM->NY literally every hour, matching
    the "NY above PJM 97.9% of hours" price finding.
  - NYIS-PJM 2024: gross 19,797,357 MWh, also fully one-directional.
  - MISO-SWPP 2024: gross 4,663,093 MWh (+17% vs 2023 baseline 3.99M).
  - MISO-SWPP 2025: gross 4,249,335 MWh (down from 2024; net collapsed
    2.44M -> 0.73M — direction churns more in 2025, worth a look when
    a 2025 MISO seam rerun lands).
- Reran solution studies with `--same-year-flow reports/same_year_flows.csv`:
  - Both corridors now `same_year_flow` status (gate cleared, no more
    price-year/flow-year mismatch).
  - NYIS-PJM 2025: $142.4M -> **$159.7M/yr** on same-year flow.
  - MISO-SWPP 2024: $25.2M -> **$29.4M/yr** on same-year flow.
- `_study_guidance` now switches the NYIS-PJM caveat on flow status:
  with same-year flow the memo says the remaining gap is project
  costing, not flow evidence.
- Rerun command (after any future flow/price update):

```powershell
python -m domains.grid.run_solution_studies `
  --same-year-flow reports\same_year_flows.csv `
  --project-costs reports\project_cost_template.csv
```

- Validation: full suite `435 passed, 2 skipped`.

## Best next handoff target

- The benefit side of both priority studies is now same-year and
  defensible. The ONLY remaining gap is real costs:
  populate `reports/project_cost_template.csv` with quoted capex/O&M
  (or explicit annual cost) and rerun to emit real B/C in
  `reports/project_cost_results.csv` and the memos.
- Best no-quote task: map CHAWATCHAPAT and Charlie Creek-Watford to
  candidate MISO/SPP upgrade names and owners (MTEP/SPP ITP project
  lists are public), so the cost template can be filled from published
  project estimates rather than waiting on private quotes.
- Cheap follow-on: 2025 MISO seam rerun (loaders are date-parameterized)
  to pair with the MISO-SWPP 2025 flow row already in
  `reports/same_year_flows.csv` — the net-flow collapse there hints the
  seam economics moved again in 2025.
