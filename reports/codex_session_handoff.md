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
  --report-csv reports\congestion_evidence_report.csv `
  --report-md reports\congestion_evidence_report.md `
  --report-json reports\congestion_evidence_report.json `
  --report-html reports\congestion_evidence_dashboard.html
```

Result:

- 25 structural bottlenecks loaded from `flow_bottleneck_report.json`.
- 0 evidence matches because no local LMP/congestion-cost dataset exists yet.
- 0 measured/proxy claims and $0 estimated measured/proxy value.
- `reports/congestion_evidence_template.csv` is ready for gridstatus/ISO
  congestion evidence.

The generated report is intentionally structural-only until real evidence is
attached.

## Tests

Full suite after the latest congestion-evidence/dashboard/review/report edits:

```text
358 passed, 2 skipped
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
