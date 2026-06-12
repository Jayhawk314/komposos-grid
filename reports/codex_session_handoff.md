# Codex Session Handoff

## Scope

Goal from James: continue Claude/Opus/Fable grid work, but improve it in a
grounded way that produces useful results for an audience.

I kept `komposos_patterns` out of the main system and worked on the actual
grid runtime path:

`PlantRecord -> Section -> coherence reports -> Category morphisms`

## Completed Edits

### Thermodynamic/sheaf cleanup

- Replaced corrupted prose/API in
  `src/komposos_wesys/validation/thermodynamic_probe.py`.
- `ThermodynamicAudit.assignment` is now the clean public field.
- Kept compatibility alias `asefficiencyment` so older generated code still
  works.
- `domains/grid/sheaf_audit.py` now reports:
  - source gauges
  - calibration multipliers
  - fused per-entity estimates on a reference-source scale
  - worst calibrated spread

### BA repair proposal layer

Added `domains/grid/ba_repair.py`.

Purpose: turn BA-level EIA-930/accounting mismatch into actionable candidate
`plant/facility -> BA` moves.

Key APIs:

- `consensus_accounting(sections, records_by_source)`
- `consensus_entity_states(sections, records_by_source, entity_to_ba)`
- `propose_ba_footprint_repair(...)`
- `write_repair_to_category(category, report)`

Repair proposals are state-footprint constrained. They are hypotheses, not
authoritative corrections.

### Validated footprint crosswalk layer

Added `domains/grid/ba_footprint_crosswalk.py`.

Purpose: promote only reviewable/validated repair candidates into an accepted
crosswalk.

Key APIs:

- `score_ba_mapping(...)`
- `build_ba_footprint_crosswalk(...)`
- `interchange_neighbors_from_ties(ties)`
- `write_crosswalk_to_category(...)`
- `BAFootprintCrosswalk.export_csv(...)`
- `BAFootprintCrosswalk.export_json(...)`

Validation supports:

- confidence threshold
- target BA must have observed state footprint
- optional EIA-930 interchange adjacency constraint
- move must improve the current validated BA score

Accepted moves are written to Category as `footprint_correction`.
Rejected proposals keep explicit reasons.

### Audience report layer

Added `domains/grid/ba_footprint_report.py`.

Purpose: build a before/after proof artifact:

- original BA coherence
- corrected BA coherence after applying accepted footprint crosswalk
- before/after BA absolute error
- before/after contradiction count
- before/after sheaf H^1 leak
- accepted/rejected correction tables
- unresolved largest BA deltas
- Markdown/JSON export

The report layer is now wired into the CLI, covered by focused tests, and
generates audience-facing Markdown/JSON artifacts.

### Human review layer

Added `domains/grid/ba_review.py`.

Purpose: keep machine validation separate from human/curated approval.
Machine `footprint_correction` rows remain hypotheses until a reviewer marks
them `accepted`.

Key APIs:

- `export_review_template_csv(...)`
- `export_review_template_json(...)`
- `load_review_decisions(path)`
- `apply_review_decisions(...)`
- `write_review_to_category(category, review)`

Review statuses:

- `accepted` - apply the move in the curated crosswalk.
- `rejected` - record the rejection and leave the current mapping unchanged.
- `needs_review` - defer the move; it is not applied.

Approved moves are written to the Category as
`reviewed_footprint_correction`. Rejected/deferred rows are written as
`footprint_review` evidence.

### Static dashboard layer

Added `domains/grid/ba_dashboard.py`.

Purpose: write dependency-free HTML dashboards for audience review without
requiring readers to inspect terminal logs or Markdown tables.

Key APIs:

- `footprint_report_to_html(report, ...)`
- `export_footprint_report_html(report, path, ...)`
- `review_to_html(review, reviewed_report=..., ...)`
- `export_review_html(review, path, reviewed_report=..., ...)`

The footprint dashboard shows before/after agreement, contradictions,
absolute BA error, sheaf H1 leak, accepted corrections, rejected candidates,
and remaining BA deltas. The review dashboard separates machine-accepted
corrections from approved-only corrections.

### Interchange bottleneck report layer

Added `domains/grid/flow_report.py`.

Purpose: turn the EIA-930 interchange Ricci/spectral output into an audience
proof artifact for T&D-loss/congestion follow-up.

Key APIs:

- `build_flow_bottleneck_report(ties, geometry=None)`
- `FlowBottleneckReport.export_markdown(path)`
- `FlowBottleneckReport.export_json(path)`
- `FlowBottleneckReport.export_html(path)`

The report ranks BA ties by flow-weighted negative Ollivier-Ricci curvature:
`priority_score = max(0, -curvature) * gross_mwh`. This makes the report
prefer ties that are both structurally tree-like and materially used.

Also fixed `domains/grid/flow_geometry.py` summary/statistics so hyperbolic
edge count falls back to the actual negative-curvature bottleneck list. The
old terminal summary could report too few hyperbolic edges.

### Congestion evidence join layer

Added `domains/grid/congestion_evidence.py` and
`domains/grid/run_congestion_evidence.py`.

Purpose: join structural flow bottlenecks to measured congestion evidence
without overclaiming. The evidence contract accepts:

- direct `congestion_cost_usd`; or
- `mean_price_spread_usd_mwh`, used as the explicit proxy
  `mean_price_spread_usd_mwh * gross_mwh`.

Rows without evidence remain `structural_only`; they are not upgraded into
measured waste claims.

Key APIs:

- `export_evidence_template_csv(flow_report_path, path)`
- `load_congestion_evidence_csv(paths)`
- `build_congestion_evidence_report(flow_report_path, evidence=None)`
- `CongestionEvidenceReport.export_csv/markdown/json/html(...)`

Generated:

- `reports/congestion_evidence_template.csv`
- `reports/congestion_evidence_report.csv`
- `reports/congestion_evidence_report.md`
- `reports/congestion_evidence_report.json`
- `reports/congestion_evidence_dashboard.html`

Current state: no local LMP or congestion-cost data exists in the repo, so the
generated report has 25 structural bottlenecks, 0 evidence matches, and 0
measured/proxy claims. This is intentional and prevents topology-only results
from being presented as measured cost.

### EAGLE-I reliability waste layer

Completed the stalled EAGLE-I 2023 outage download and report path.

The previous file was partial and visibly truncated at `2023-12-20 23`.
Resumed `https://ndownloader.figshare.com/files/44574907` with `curl -C -`
until the file ended cleanly at `2023-12-31 23:45:00`.

Updated `domains/grid/outages.py`:

- `OutageReport` now carries `rows_processed`, `first_timestamp`, and
  `last_timestamp`.
- Added CSV/Markdown/JSON/HTML exports.
- Chunked aggregation still keeps only state rollups in memory.

Updated `domains/grid/run_outages.py`:

- `--report-csv <path>`
- `--report-md <path>`
- `--report-json <path>`
- `--report-html <path>`

Generated:

- `reports/outage_reliability_report.csv`
- `reports/outage_reliability_report.md`
- `reports/outage_reliability_report.json`
- `reports/outage_reliability_dashboard.html`

Full 2023 EAGLE-I result:

- 26,101,051 rows processed.
- Time range: `2023-01-01 00:00:00` -> `2023-12-31 23:45:00`.
- 1.059B customer-hours lost.
- Worst normalized burdens:
  - United States Virgin Islands: 41.9 h/customer.
  - Maine: 38.9 h/customer.
  - Puerto Rico: 34.3 h/customer.
  - Michigan: 26.5 h/customer.
  - Kentucky: 14.9 h/customer.

### CLI wiring

Updated `domains/grid/run_coherence.py`.

Existing BA check now additionally:

- builds accounting consensus
- proposes BA footprint repair candidates
- validates/promotes them through `BAFootprintCrosswalk`
- writes `footprint_candidate` and `footprint_correction` morphisms
- supports exports:
  - `--ba-repair-csv <path>`
  - `--ba-repair-json <path>`
  - `--ba-footprint-report-md <path>`
  - `--ba-footprint-report-json <path>`
  - `--ba-footprint-report-html <path>`
  - `--ba-review-template-csv <path>`
  - `--ba-review-template-json <path>`
  - `--ba-review-decisions <path>`
  - `--ba-reviewed-csv <path>`
  - `--ba-reviewed-json <path>`
  - `--ba-reviewed-report-md <path>`
  - `--ba-reviewed-report-json <path>`
  - `--ba-reviewed-report-html <path>`
- supports optional interchange constraint:
  - `--eia930-interchange <INTERCHANGE csvs>`

Updated `domains/grid/run_flow_geometry.py`:

- `--report-md <path>`
- `--report-json <path>`
- `--report-html <path>`

Added `domains/grid/run_congestion_evidence.py`:

- `--flow-report <flow_bottleneck_report.json>`
- `--template-csv <path>`
- `--evidence-csv <path ...>`
- `--report-csv <path>`
- `--report-md <path>`
- `--report-json <path>`
- `--report-html <path>`

## Real 2023 Run Result

Command used:

```powershell
python -m domains.grid.run_coherence `
  --egrid domains\grid\data\egrid2023_data_rev2.xlsx `
  --eia923 domains\grid\data\f923_2023\EIA923_Schedules_2_3_4_5_M_12_2023_Final_Revision.xlsx `
  --eia930 domains\grid\data\EIA930_BALANCE_2023_Jan_Jun.csv domains\grid\data\EIA930_BALANCE_2023_Jul_Dec.csv `
  --eia930-interchange domains\grid\data\EIA930_INTERCHANGE_2023_Jan_Jun.csv domains\grid\data\EIA930_INTERCHANGE_2023_Jul_Dec.csv `
  --ba-repair-csv reports\ba_repair_candidates.csv `
  --ba-repair-json reports\ba_repair_candidates.json `
  --ba-footprint-report-md reports\ba_footprint_report.md `
  --ba-footprint-report-json reports\ba_footprint_report.json `
  --ba-footprint-report-html reports\ba_footprint_dashboard.html `
  --ba-review-template-csv reports\ba_review_template.csv `
  --ba-review-template-json reports\ba_review_template.json
```

Result:

- Facility crosswalk resolved 11 plant-ID contradictions.
- BA repair candidates reduced absolute BA error from 290.5 TWh to 224.2 TWh
  before interchange validation.
- Validated crosswalk accepted 10 of 13 candidates.
- Validated before/after:
  - absolute BA error: 290.5 TWh -> 231.2 TWh
  - BAs outside 5% tolerance: 41 -> 30
  - improvement: 59.4 TWh (20.4%)
- Audience proof report:
  - BA agreement: 45.2% -> 62.9%
  - contradictions: 11 -> 7
  - sheaf H^1 leak: 1.899e+00 -> 8.185e-01

Example accepted corrections:

- 3082 John Day, OR: BPAT -> GRID
- 3895 The Dalles, OR: BPAT -> GRID
- 2721 Cliffside, NC: DUK -> CPLW
- 55306 Gila River Power Station, AZ: SRP -> AZPS
- 55821, FL: FPC -> FMPP
- 55482, WA: PSEI -> GCPD
- 55700, WA: PSEI -> GCPD

Rejected examples:

- 55112 WALC -> BANC: no observed interchange tie
- 65577 PSEI -> NWMT: no observed interchange tie
- 50188 CPLE -> SEPA: no observed interchange tie

Exports written:

- `reports/ba_repair_candidates.csv`
- `reports/ba_repair_candidates.json`
- `reports/ba_footprint_report.md`
- `reports/ba_footprint_report.json`
- `reports/ba_footprint_dashboard.html`
- `reports/ba_review_template.csv`
- `reports/ba_review_template.json`
- `reports/flow_bottleneck_report.md`
- `reports/flow_bottleneck_report.json`
- `reports/flow_bottleneck_dashboard.html`
- `reports/congestion_evidence_template.csv`
- `reports/congestion_evidence_report.csv`
- `reports/congestion_evidence_report.md`
- `reports/congestion_evidence_report.json`
- `reports/congestion_evidence_dashboard.html`
- `reports/outage_reliability_report.csv`
- `reports/outage_reliability_report.md`
- `reports/outage_reliability_report.json`
- `reports/outage_reliability_dashboard.html`
- `reports/grid_waste_ledger.csv`
- `reports/grid_waste_ledger.json`
- `reports/grid_waste_ledger.md`
- `reports/grid_waste_dashboard.html`

## Flow Bottleneck 2023 Result

Command used:

```powershell
python -m domains.grid.run_flow_geometry `
  --interchange domains\grid\data\EIA930_INTERCHANGE_2023_Jan_Jun.csv domains\grid\data\EIA930_INTERCHANGE_2023_Jul_Dec.csv `
  --report-md reports\flow_bottleneck_report.md `
  --report-json reports\flow_bottleneck_report.json `
  --report-html reports\flow_bottleneck_dashboard.html
```

Result:

- 63 BAs, 144 direct interchange ties.
- 499.7 TWh gross interchange.
- 25 hyperbolic/negative-curvature ties (17.4%).
- Spectral coupling: very weak; Fiedler value 0.0033.
- Top 10 prioritized bottlenecks carry 62.8 TWh (12.6% of gross interchange).

Top prioritized bottlenecks:

- PJM - NYIS: curvature -0.107, gross 19.3 TWh.
- BPAT - NWMT: curvature -0.122, gross 7.2 TWh.
- MISO - SOCO: curvature -0.151, gross 5.4 TWh.
- SOCO - FPL: curvature -0.208, gross 3.5 TWh.
- BPAT - LDWP: curvature -0.098, gross 6.8 TWh.

Important caveat: these are structural bottleneck candidates, not standalone
claims of physical overload. Next evidence join should attach LMP separation,
congestion cost, outage, or planning-model data.

## Congestion Evidence Join Result

Command used:

```powershell
python -m domains.grid.run_congestion_evidence `
  --flow-report reports\flow_bottleneck_report.json `
  --template-csv reports\congestion_evidence_template.csv `
  --evidence-csv reports\congestion_evidence_2023_hubs.csv reports\nyiso_pjm_seam_evidence.csv `
  --report-csv reports\congestion_evidence_report.csv `
  --report-md reports\congestion_evidence_report.md `
  --report-json reports\congestion_evidence_report.json `
  --report-html reports\congestion_evidence_dashboard.html
```

Result:

- 25 structural bottlenecks loaded from `flow_bottleneck_report.json`.
- 5 evidence matches.
- 5 measured/proxy claims.
- Estimated measured/proxy value: $225.7M.
- Four Western ties still use EIA ICE hub-spread proxies, now generated by
  `run_western_hub_evidence.py`:
  CISO-SRP $141.7M, BPAT-CISO $51.7M, BPAT-NEVP $2.2M,
  PACW-CISO $0.7M.
- PJM-NYIS now uses `lmp_component_proxy` from NYISO settlement
  congestion-component data: $1.53/MWh over 19.3 TWh gross interchange,
  valued at $29.5M.
- Remaining ties stay `structural_only` until LMP/congestion-cost evidence
  is attached.

Generated additionally:

- `reports/nyiso_pjm_seam_evidence.csv`
- `reports/nyiso_pjm_seam_audit.json`
- `reports/nyiso_pjm_seam_audit.md`
- `reports/nyiso_pjm_seam_audit.html`
- `reports/western_hub_evidence.csv`
- `reports/western_hub_audit.csv`
- `reports/western_hub_audit.json`
- `reports/western_hub_audit.md`
- `reports/western_hub_audit.html`

NYISO audit result: 8,759 hours; mean absolute all-in LBMP spread
$2.01/MWh; mean absolute congestion-component spread $1.53/MWh; mean
absolute loss-component spread $0.52/MWh; congestion component is 75.8% of
the all-in LBMP spread.

## Tests

Full suite after the latest congestion-evidence/dashboard/review/report edits:

```text
381 passed, 2 skipped
```

Latest focused dashboard/report/review run:

```text
10 passed
tests/test_grid_ba_dashboard.py
tests/test_grid_ba_footprint_report.py
tests/test_grid_ba_review.py
```

Focused flow geometry/report tests:

```text
7 passed directly; 17 passed in the combined flow/dashboard/report/review run
tests/test_grid_flow_geometry.py
tests/test_grid_flow_report.py
```

Focused congestion evidence tests:

```text
5 passed directly; 12 passed in the combined congestion/flow run
tests/test_grid_congestion_evidence.py
```

Focused outage tests:

```text
4 passed
tests/test_grid_outages.py
```

Focused waste ledger tests:

```text
5 passed
tests/test_grid_waste_ledger.py
```

Compile smoke on touched grid code also passed.

## Important Caveats

- `footprint_candidate` and `footprint_correction` moves are not official BA
  registrations. They are validated hypotheses for review.
- EIA-930 BA telemetry and accounting plant records measure different
  operational/accounting boundaries. The system correctly treats the functor
  as the hypothesis to repair.
- The repo has a large dirty working tree unrelated to my edits. Do not reset
  or revert broad changes.

## Next Immediate Task

The grid BA footprint repair, reporting, and review paths are implemented and
validated. The machine-validated dashboard is also generated. Suggested next
work:

1. Have a domain reviewer edit `reports/ba_review_template.csv`, setting
   `review_status` to `accepted`, `rejected`, or `needs_review`.
2. Rerun `run_coherence` with `--ba-review-decisions` plus
   `--ba-reviewed-report-md` and `--ba-reviewed-report-html` to produce an
   approved-only proof report/dashboard.
3. Populate `reports/congestion_evidence_template.csv` from gridstatus or ISO
   congestion-cost reports, then rerun `run_congestion_evidence` with
   `--evidence-csv` to produce measured/proxy congestion claims.

### Unified grid waste ledger

Added `domains/grid/waste_ledger.py` and
`domains/grid/run_waste_ledger.py`.

James asked to move forward with a unified grid waste ledger and reminded me
to keep this working summary current.

Ledger shape:

- standard `WasteClaim` schema across BA coherence, congestion, curtailment,
  reliability outages, queue factorization, and structural flow bottlenecks;
- evidence levels kept explicit: `measured`, `measured_proxy`,
  `validated_hypothesis`, `structural_only`;
- exports: `reports/grid_waste_ledger.csv`,
  `reports/grid_waste_ledger.json`, `reports/grid_waste_ledger.md`, and
  `reports/grid_waste_dashboard.html`;
- do not add topology-only or hypothesis claims into measured dollar/TWh
  totals.

Generated:

- `reports/grid_waste_ledger.csv`
- `reports/grid_waste_ledger.json`
- `reports/grid_waste_ledger.md`
- `reports/grid_waste_dashboard.html`

Current result:

- 26 claims total.
- Evidence mix: `measured` 12, `measured_proxy` 5, `structural_only` 8,
  `validated_hypothesis` 1.
- Reported/proxy dollar total: $398.2M.
- Direct/upper-bound measured dollar component: $172.5M CAISO curtailment
  upper-bound valuation.
- Measured-proxy congestion component: $225.7M from five congestion evidence
  rows. PJM-NYIS now uses NYISO settlement congestion-component spread
  rather than all-in LBMP spread.
- Structural-only flow bottlenecks and BA-footprint validated hypotheses are
  present as action items but excluded from measured/proxy dollar totals.

Validation:

- Focused ledger tests: `5 passed` (`tests/test_grid_waste_ledger.py`).
- Full suite after ledger layer: `381 passed, 2 skipped`.

Input inspection found:

- measured congestion evidence exists in `reports/congestion_evidence_report.csv`
  and `reports/congestion_evidence_2023_hubs.csv` (5 proxy/measured rows);
- CAISO curtailment workbook exists locally;
- LBNL queue workbook exists locally;
- EAGLE-I, BA footprint, flow bottleneck, and congestion evidence JSON/CSV
  reports exist.

## Grid Action Portfolio

James asked for the next layer after the unified waste ledger.

Added `domains/grid/action_portfolio.py` and
`domains/grid/run_action_portfolio.py`.

Purpose: turn the ledger's evidence-separated claims into a ranked action
portfolio without changing claim values:

- `ready_for_scoping` for measured claims where project/program design can
  start;
- `validate_proxy` for LMP/hub-spread proxy claims that need direct
  congestion-cost or nodal validation;
- `review_required` for validated hypotheses such as BA footprint corrections;
- `attach_evidence` for structural-only flow bottlenecks;
- `policy_design` for queue-factorization/process-reform claims.

Generated:

- `reports/grid_action_portfolio.csv`
- `reports/grid_action_portfolio.json`
- `reports/grid_action_portfolio.md`
- `reports/grid_action_dashboard.html`

Current result:

- 10 actions total.
- Status mix: `ready_for_scoping` 2, `validate_proxy` 5,
  `review_required` 1, `attach_evidence` 1, `policy_design` 1.
- Reported value remains evidence-separated:
  - $225.7M proxy congestion value.
  - $172.5M CAISO curtailment upper-bound value.
  - $398.2M total reported/proxy/upper-bound value.
- Top actions:
  - Scope CAISO curtailment reduction package.
  - Prioritize reliability hardening in USVI, Maine, Puerto Rico, Michigan,
    and Kentucky.
  - Target queue reform at IA-stage mediators.
  - Validate proxy congestion values for CISO-SRP, BPAT-CISO, PJM-NYIS,
    BPAT-NEVP, and PACW-CISO.
  - Review BA footprint correction candidates.
  - Attach evidence to remaining structural bottlenecks.

Validation:

- Focused action portfolio tests: `4 passed`
  (`tests/test_grid_action_portfolio.py`).
- Full suite after action portfolio layer: `385 passed, 2 skipped`.

## PJM-NYIS Component Evidence Upgrade

James said "lets do it" after the action portfolio pointed to proxy
congestion validation.

Edits:

- Added NYISO component spread analytics in `domains/grid/sources/nyiso.py`.
- Added `domains/grid/run_nyiso_seam_evidence.py`.
- Extended `domains/grid/congestion_evidence.py` with
  `lmp_component_proxy`, `evidence_method`, and settlement component fields.
- Updated `domains/grid/waste_ledger.py` so `lmp_component_proxy` remains a
  measured-proxy claim, but with estimate kind
  `lmp_congestion_component_proxy`.
- Updated `domains/grid/action_portfolio.py` so component proxies get a
  distinct caveat from hub-spread proxies.
- Added focused tests in `tests/test_grid_nyiso.py`,
  `tests/test_grid_congestion_evidence.py`, and
  `tests/test_grid_action_portfolio.py`.

Generated:

- `reports/nyiso_pjm_seam_evidence.csv`
- `reports/nyiso_pjm_seam_audit.json`
- `reports/nyiso_pjm_seam_audit.md`
- `reports/nyiso_pjm_seam_audit.html`
- regenerated congestion evidence, waste ledger, and action portfolio reports.

Result:

- PJM-NYIS value changed from $38.8M all-in LBMP spread proxy to $29.5M
  congestion-component proxy.
- Congestion measured/proxy total changed from $234.9M to $225.6M.
- Overall ledger/action reported value changed from $407.4M to $398.1M.
- This is more defensible because it excludes the loss and non-congestion
  components of the NYISO/PJM price spread.

Validation:

- Focused tests: `18 passed`
  (`tests/test_grid_nyiso.py`, `tests/test_grid_congestion_evidence.py`,
  `tests/test_grid_waste_ledger.py`, `tests/test_grid_action_portfolio.py`).
- Full suite after component evidence upgrade: `387 passed, 2 skipped`.

## Western Hub Proxy Audit

James said yes to the next evidence upgrade after PJM-NYIS.

Edits:

- Added `domains/grid/sources/ice.py`.
- Added `domains/grid/run_western_hub_evidence.py`.
- Added focused tests in `tests/test_grid_ice.py`.
- Updated `domains/grid/action_portfolio.py` so weak/mixed/supportive hub
  alignment is surfaced in action caveats.
- Regenerated congestion evidence using
  `reports/western_hub_evidence.csv` plus
  `reports/nyiso_pjm_seam_evidence.csv`.
- Regenerated waste ledger and action portfolio outputs.

Generated:

- `reports/western_hub_evidence.csv`
- `reports/western_hub_audit.csv`
- `reports/western_hub_audit.json`
- `reports/western_hub_audit.md`
- `reports/western_hub_audit.html`

Result:

- Western dollar values stay conservative: the evidence CSV uses annual
  volume-weighted hub spreads for valuation, not larger daily mean absolute
  spreads.
- CISO-SRP: conservative $14.03/MWh, daily mean |spread| $15.58/MWh,
  flow-weighted alignment 39.0% (weak). Action caveat now marks it as weak.
- BPAT-CISO: conservative $9.47/MWh, daily mean |spread| $32.90/MWh,
  flow-weighted alignment 58.9% (mixed). NP15 volume remains thin.
- BPAT-NEVP: conservative $3.79/MWh, daily mean |spread| $24.02/MWh,
  flow-weighted alignment 45.3% (mixed).
- PACW-CISO: conservative $9.47/MWh, daily mean |spread| $32.90/MWh,
  flow-weighted alignment 82.5% (directionally supportive) but only
  $0.7M proxy value.
- Congestion measured/proxy total is now $225.7M.
- Overall ledger/action reported value is now $398.2M.

Validation so far:

- Focused tests: `20 passed`
  (`tests/test_grid_ice.py`, `tests/test_grid_nyiso.py`,
  `tests/test_grid_congestion_evidence.py`, `tests/test_grid_waste_ledger.py`,
  `tests/test_grid_action_portfolio.py`).
- Full suite after Western hub audit: `389 passed, 2 skipped`.

## Current Next Task

Next technical evidence upgrade should fetch direct CAISO/OASIS nodal or
constraint data for CISO-SRP, because the local ICE/EIA-930 audit shows it is
the largest dollar proxy but has weak flow/price alignment. Without that new
data, it should remain a screening target, not a defensible congestion-cost
claim. Highest review path remains processing `reports/ba_review_template.csv`
into approved-only BA corrections.

## Next Agent Brief

James paused the CAISO/OASIS work because the session was almost out of
budget. Do not restart from scratch.

What is complete and verified:

- BA coherence, BA footprint repair candidates, validated crosswalks, human
  review templates, and static dashboards are implemented.
- Flow geometry on EIA-930 interchange is implemented and produces structural
  bottleneck reports.
- Congestion evidence joins structural bottlenecks to external evidence while
  keeping `measured_cost`, `lmp_component_proxy`, `price_spread_proxy`, and
  `structural_only` separate.
- NYISO PJM seam evidence is component-audited:
  - 8,759 NYISO DAM hourly observations.
  - Mean absolute all-in LBMP spread: $2.01/MWh.
  - Mean absolute congestion-component spread: $1.53/MWh.
  - PJM-NYIS value is now $29.5M, not the older $38.8M all-in spread proxy.
- Western ICE hub proxies are audited against EIA-930 flow direction:
  - CISO-SRP: $141.7M proxy, weak flow/price alignment at 39.0%.
  - BPAT-CISO: $51.7M proxy, mixed alignment at 58.9%, thin NP15 data.
  - BPAT-NEVP: mixed alignment at 45.3%.
  - PACW-CISO: directionally supportive at 82.5%, but small value.
- Unified waste ledger and action portfolio are implemented:
  - 26 claims.
  - 10 portfolio actions.
  - Current reported value: $398.2M.
  - Congestion proxy/component value: $225.7M.
  - CAISO curtailment upper-bound value: $172.5M.
- Latest full verification: `389 passed, 2 skipped`.

Important generated artifacts:

- `reports/ba_footprint_report.md/json/html`
- `reports/ba_review_template.csv/json`
- `reports/flow_bottleneck_report.md/json/html`
- `reports/congestion_evidence_report.csv/md/json/html`
- `reports/nyiso_pjm_seam_audit.md/json/html`
- `reports/western_hub_audit.csv/md/json/html`
- `reports/grid_waste_ledger.csv/md/json/html`
- `reports/grid_action_portfolio.csv/md/json/html`

Design principle to preserve:

- Do not promote topology-only or hub-spread evidence into direct measured
  congestion cost. The system's credibility comes from separating evidence
  levels and preserving caveats.
- CISO-SRP is the next target precisely because it is high-dollar and weakly
  aligned. It should remain a screening target until direct CAISO/OASIS nodal,
  constraint, or settlement evidence is attached.

Recommended next implementation:

1. Add a CAISO/OASIS loader under `domains/grid/sources/caiso_oasis.py`.
2. Start with a tiny, testable API wrapper for `PRC_LMP` or congestion
   component queries over small date windows; do not download a full year
   until the schema is proven.
3. Add a runner such as `domains/grid/run_caiso_oasis_evidence.py` that can:
   - fetch/cache daily or monthly zip responses;
   - extract node/hub LMP and congestion component columns;
   - compute CISO-SRP candidate spreads using CAISO-side nodes/hubs and a
     defensible Palo Verde/SRP proxy;
   - write an evidence CSV compatible with `run_congestion_evidence`.
4. If direct CAISO evidence cannot represent SRP/Palo Verde cleanly, keep the
   result as `price_spread_proxy` and only improve the caveat/provenance.
5. Regenerate congestion evidence, waste ledger, and action portfolio only
   after the CAISO evidence row has a clear status and source.

Parallel non-network path:

- Process `reports/ba_review_template.csv` into approved-only BA corrections
  and regenerate a reviewed dashboard. This is lower technical risk and gives
  a cleaner audience artifact without new data downloads.
