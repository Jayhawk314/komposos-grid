# Grid Domain - Categorical Analysis of Electrical Grid Waste

Domain package built on the KOMPOSOS-IV categorical runtime (`core.category`).
It targets the three bottlenecks where grid waste concentrates:

| Bottleneck | What is wasted | Primary datasets |
|---|---|---|
| **Curtailment** | Renewable energy discarded when the grid cannot absorb or store it | LBNL Queued Up, EIA-930, storage profiles |
| **T&D losses** | Energy dissipating as heat; congestion trapping electricity | LMPs (gridstatus), PSML, ACTIVSg, EAGLE-I |
| **Peaker reliance** | Inefficient fossil plants covering demand spikes | eGRID, EIA-923, EIA-930, Electricity Maps |

The full dataset catalog, with access notes and implementation status, is in
`sources/registry.py`.

## Phase 0: Data Coherence

Before optimizing anything, confirm the data describes the same grid. Each
dataset is a section of the plant-data presheaf over the plants it covers
(keyed by EIA ORIS code). The sheaf gluing condition - sections agree on
overlaps - is the categorical statement of "the data is trustworthy".

```bash
python -m domains.grid.run_coherence --synthetic
python -m domains.grid.run_coherence --egrid egrid2023_data_rev2.xlsx \
    --eia923 EIA923_Schedules_2_3_4_5_M_12_2023_Final.xlsx
```

Per-plant verdicts:

- `GLUE`: sources agree within tolerance.
- `TENSION`: known adjustment territory, such as CHP, station use, or
  net-vs-gross conventions.
- `CONTRADICT`: at least one source or key mapping is wrong.

Results are written back into the `Category` as morphisms:

- `source:A -coheres_with-> source:B`, confidence = agreement rate.
- `source:A -disputes-> plant:X`, confidence = discrepancy.

## Level 1: Facility Crosswalk

When eGRID reports a multi-block facility as one ORIS plant and EIA-923 reports
the blocks separately, the plant-ID gluing check finds contradictions. The
facility crosswalk discovers quotient maps `plant -> facility` that close those
gaps while conserving generation. Accepted merges are written back as
`part_of` morphisms.

## Level 2: BA Telemetry

Plant or facility sections are pushed forward along the
`plant -> balancing-authority` map and compared against EIA-930 hourly
telemetry, an independent measurement pathway. Run by adding:

```bash
--eia930 EIA930_BALANCE_2023_Jan_Jun.csv EIA930_BALANCE_2023_Jul_Dec.csv
```

Real-data finding for 2023: the two accounting datasets agree with each other
at BA level, but both disagree identically with EIA-930 telemetry for a small
set of BAs concentrated in the Pacific Northwest and federal power-marketing
territories. That localizes the issue to the plant-to-BA functor: plant
registration and metered BA footprint are not always the same map.

## BA Footprint Repair Candidates

After the BA-level check, `run_coherence` builds an accounting consensus
section, compares it to EIA-930 telemetry, and proposes reviewable
`plant/facility -> BA` moves that reduce BA-level error while conserving total
generation. These are written back as `footprint_candidate` morphisms with
confidence and improvement metadata. They are hypotheses for domain review,
not authoritative registrations.

## BA Correction Review

Machine validation promotes conservative candidates into
`footprint_correction` morphisms, but those are still hypotheses. The review
layer exports an editable evidence table and only applies rows explicitly
marked `accepted` by a reviewer.

```bash
python -m domains.grid.run_coherence ... \
    --eia930 EIA930_BALANCE_2023_Jan_Jun.csv EIA930_BALANCE_2023_Jul_Dec.csv \
    --eia930-interchange EIA930_INTERCHANGE_2023_Jan_Jun.csv EIA930_INTERCHANGE_2023_Jul_Dec.csv \
    --ba-review-template-csv reports/ba_review_template.csv
```

Reviewers edit `review_status` to one of:

- `accepted`: apply the move in the curated crosswalk.
- `rejected`: record the rejection and leave the registration unchanged.
- `needs_review`: defer the move; it is not applied.

Then rerun with the decision file:

```bash
python -m domains.grid.run_coherence ... \
    --eia930 EIA930_BALANCE_2023_Jan_Jun.csv EIA930_BALANCE_2023_Jul_Dec.csv \
    --eia930-interchange EIA930_INTERCHANGE_2023_Jan_Jun.csv EIA930_INTERCHANGE_2023_Jul_Dec.csv \
    --ba-review-decisions reports/ba_review_template.csv \
    --ba-reviewed-csv reports/ba_reviewed.csv \
    --ba-reviewed-report-md reports/ba_reviewed_report.md \
    --ba-reviewed-report-html reports/ba_reviewed_dashboard.html
```

Approved moves are written back as `reviewed_footprint_correction`; rejected
or deferred rows are written as `footprint_review` evidence.

## Audience Dashboard

Use `--ba-footprint-report-html` to write a standalone dashboard for the
machine-validated correction report:

```bash
python -m domains.grid.run_coherence ... \
    --eia930 EIA930_BALANCE_2023_Jan_Jun.csv EIA930_BALANCE_2023_Jul_Dec.csv \
    --eia930-interchange EIA930_INTERCHANGE_2023_Jan_Jun.csv EIA930_INTERCHANGE_2023_Jul_Dec.csv \
    --ba-footprint-report-html reports/ba_footprint_dashboard.html
```

The HTML export is static and dependency-free. It includes before/after
metrics, accepted corrections, rejected candidates, and unresolved BA deltas.

## Interchange Bottleneck Report

The EIA-930 INTERCHANGE files define the BA flow graph: BAs are nodes and
direct interchange ties are weighted edges. `run_flow_geometry` computes
Ollivier-Ricci bottlenecks and the spectral Fiedler seam, then exports an
audience report:

```bash
python -m domains.grid.run_flow_geometry \
    --interchange EIA930_INTERCHANGE_2023_Jan_Jun.csv EIA930_INTERCHANGE_2023_Jul_Dec.csv \
    --report-md reports/flow_bottleneck_report.md \
    --report-json reports/flow_bottleneck_report.json \
    --report-html reports/flow_bottleneck_dashboard.html
```

The report ranks ties by flow-weighted negative curvature. These are not
claims of physical overload by themselves; they are structural candidates for
follow-up with LMP separation, congestion costs, outage records, or planning
models.

## Congestion Evidence Join

Use `run_congestion_evidence` to join those structural bottlenecks to measured
evidence. The evidence CSV is keyed by BA tie and accepts either direct
`congestion_cost_usd` or an LMP spread proxy:

```bash
python -m domains.grid.run_congestion_evidence \
    --flow-report reports/flow_bottleneck_report.json \
    --template-csv reports/congestion_evidence_template.csv
```

Fill the generated template columns:

- `congestion_cost_usd`: measured annual congestion cost for the tie.
- `mean_price_spread_usd_mwh`: average LMP spread across the tie; when direct
  cost is absent, the report uses `spread * gross_mwh` as an explicit proxy.
- `evidence_source`, `hours_observed`, `notes`: provenance and review context.

Then run:

```bash
python -m domains.grid.run_congestion_evidence \
    --flow-report reports/flow_bottleneck_report.json \
    --evidence-csv reports/congestion_evidence_template.csv \
    --report-md reports/congestion_evidence_report.md \
    --report-json reports/congestion_evidence_report.json \
    --report-html reports/congestion_evidence_dashboard.html
```

Rows without measured evidence remain `structural_only`; the report does not
upgrade them into measured waste claims.

## Phase 1: Math-Layer Analyses

- **Sheaf audit** (`sheaf_audit.py`, runs inside `run_coherence`) - the
  thermodynamic sheaf probe (cellular sheaf, H^1 obstruction) upgrades
  pairwise coherence to a global statement: leak ~ 0 iff one calibration
  glues all sections. 2023: plant level glues at calibration 1.000
  (leak 2e-4); BA level obstructed (leak 2.8) exactly at the disputed
  BAs, telemetry ~2.7% below accounting globally.
- **Flow geometry** (`flow_geometry.py`, `run_flow_geometry.py`) -
  Ollivier-Ricci curvature + spectral analysis on the BA interchange
  graph (EIA-930 INTERCHANGE files). Recovers the known congestion
  corridors from telemetry alone: PJM-NYIS, BPA's radial spokes,
  CISO-SRP, MISO-SOCO/SWPP. Fiedler value 0.0033 (very weak coupling).
  Curvature runs on unit-distance topology: flow magnitude is coupling
  strength, not metric distance.
- **Congestion evidence, populated** - 2023 EIA ICE hub spreads plus the
  NYISO hourly seam component audit: four Western ties carry ~$196.2M/yr of
  conservative hub-spread-proxied congestion value (CISO-SRP $141.7M,
  BPAT-CISO $51.7M), and PJM-NYIS uses NYISO settlement congestion-component spread
  ($1.53/MWh, ~$29.5M/yr) instead of the all-in LBMP spread. The remaining
  structural ties stay `structural_only`.
- **Dual-Engine verification** (`verify_assignments.py`,
  `run_verify_assignments.py`) - ZFC/CAT verification of plant->BA
  assignments with flow-scaled counterfactuals. 2023: disputed BAs show
  24% mean counterfactual leakiness vs 2% control (12x); all registered
  assignments AGREE - the level-2 incoherence lives in the assignment
  functor, not the records. Episodes recorded in System 3.
- **Queue factorization** (`queue_analysis.py`, `run_queue_analysis.py`) -
  OPTIMUS categorical gradient on LBNL Queued Up cohorts: discovers
  intermediates (fuel, region, era, size, IA milestone) through which
  `proposed -> operational` factors better than the direct rate.
  Decided projects only; cohorts under `min_cohort` carry no morphism.
  **Real run needs a manual download** (browser challenge): save the
  xlsx from https://emp.lbl.gov/publications/us-interconnection-queue-data-0
  into `domains/grid/data/`, then
  `python -m domains.grid.run_queue_analysis --queue <file>`.

## Phase 2: Measured Waste Claims (in progress)

- **Unified waste ledger** (`waste_ledger.py`, `run_waste_ledger.py`) -
  combines the current proof artifacts into one evidence-separated decision
  product. Current run: 26 claims (`measured` 12, `measured_proxy` 5,
  `structural_only` 8, `validated_hypothesis` 1). Reported/proxy dollar
  total is $398.2M: $172.5M CAISO curtailment upper-bound value plus
  $225.7M congestion price-spread/component proxies. Generate with:
  `python -m domains.grid.run_waste_ledger --report-md
  reports/grid_waste_ledger.md --report-html
  reports/grid_waste_dashboard.html`. Structural-only and hypothesis claims
  are explicitly excluded from measured/proxy dollar totals.
- **Action portfolio** (`action_portfolio.py`,
  `run_action_portfolio.py`) - groups the ledger claims into decision-ready
  work packages without changing claim values. Current run: 10 actions:
  2 `ready_for_scoping`, 5 `validate_proxy`, 1 `review_required`,
  1 `attach_evidence`, and 1 `policy_design`. Reported value stays split as
  $225.7M proxy congestion value plus $172.5M CAISO curtailment upper-bound
  value. Generate with:
  `python -m domains.grid.run_action_portfolio --ledger
  reports/grid_waste_ledger.json --report-md
  reports/grid_action_portfolio.md --report-html
  reports/grid_action_dashboard.html`.
- **PJM-NYIS seam, component-audited** -
  `run_nyiso_seam_evidence.py` reads NYISO DAM zonal LBMP settlement
  components (8,759 hours). Mean absolute all-in LBMP spread is $2.01/MWh,
  but the congestion component alone is $1.53/MWh (75.8% of the spread),
  so the congestion join values PJM-NYIS at ~$29.5M/yr rather than the
  older $38.8M all-in spread proxy. Export:
  `python -m domains.grid.run_nyiso_seam_evidence --report-md
  reports/nyiso_pjm_seam_audit.md --evidence-csv
  reports/nyiso_pjm_seam_evidence.csv`.
- **Western hub proxy audit** -
  `run_western_hub_evidence.py` rebuilds the Western proxy rows from the
  ICE workbook and checks same-day price spreads against EIA-930 interchange
  direction. Dollar values stay conservative, using annual volume-weighted
  hub spreads, while the audit exposes proxy quality: CISO-SRP has weak
  flow/price alignment (39.0%), BPAT-CISO is mixed (58.9%) with thin NP15
  data, BPAT-NEVP is mixed (45.3%), and PACW-CISO is directionally
  supportive (82.5%) but small. Export:
  `python -m domains.grid.run_western_hub_evidence --audit-md
  reports/western_hub_audit.md --evidence-csv
  reports/western_hub_evidence.csv`.
- **Curtailment, quantified** (`curtailment.py`, `run_curtailment.py`) -
  CAISO production+curtailments workbook (keyless): 2023 CISO curtailed
  2.66 TWh of renewables (solar 5.9% of available). Decomposition:
  78% is *Local* (congestion-driven) vs 22% *System* (oversupply) -
  CAISO's curtailment problem is mostly a wires problem. Value
  <= $172M/yr at the SP15 annual average (labeled upper bound).
- **Reliability waste** (`outages.py`, `run_outages.py`) - EAGLE-I
  county outages (figshare mirror of the ORNL data, ~1.1GB/yr) chunked
  to state-level customer-hours with MCC denominators: a SAIDI-like
  hours-per-customer figure computed identically across states. Full 2023
  run processed 26,101,051 rows from `2023-01-01 00:00:00` through
  `2023-12-31 23:45:00`: 1.059B customer-hours lost, worst normalized
  burdens USVI 41.9 h/customer, Maine 38.9, Puerto Rico 34.3, Michigan
  26.5. Export with:
  `python -m domains.grid.run_outages --outages <eaglei.csv> --mcc <mcc.csv>
  --report-md reports/outage_reliability_report.md --report-json
  reports/outage_reliability_report.json --report-html
  reports/outage_reliability_dashboard.html`. The same report can be written
  back as `outage_burden` hom-values.
- **Queue factorization, real data** - LBNL thru-2025 file: 29,010
  decided projects, 16.5% completion. IA-executed cohort completes at
  65.5% (4.0x direct); decided projects still in study phases withdraw
  at 100%; ERCOT completes at 2.1x. The queue bottleneck is the IA
  pipeline itself.

## Phase 3: Proxy Validation via CAISO OASIS (implemented)

`sources/caiso_oasis.py` + `run_caiso_oasis_evidence.py` pull CAISO's
own DAM settlement prices (PRC_LMP v12, keyless, cached; ~39-month
retention so Apr 2023+ of the ledger year is available) at seam nodes:

- `PALOVRDE_ASR-APND` (Arizona border / CISO-SRP corridor)
- `MALIN_5_N101` (COI / BPAT-CISO corridor)

Result (Apr-Dec 2023, 6,600 hours each): the true hourly settlement
spread is **$1.55/MWh** for SP15-Palo Verde (89% congestion component)
and **$1.37/MWh** for NP15-Malin (81%) - the annual ICE hub level
differences had overstated these seams by 7-9x. After correction the
congestion proxy total fell from $234.9M to **$52.4M**, the unified
ledger from $398.2M to **$224.9M**, and the action portfolio now leads
with CAISO curtailment reduction ($172.5M upper bound) rather than the
deflated proxies. Caveat carried in the evidence rows: the OASIS window
misses Q1 2023 (western gas crisis) due to retention.

This is the system working as designed: structural candidates ->
proxy screening -> settlement-grade validation, with each stage
allowed to shrink the previous one.

## Roadmap

1. **Reviewed dashboard pass** - after a domain reviewer edits the review
   template, generate `ba_reviewed_dashboard.html` as the approved-only
   audience artifact.
2. **Remaining seam validation** - PJM-NYIS is component-measured
   (NYISO); BPAT-NEVP and PACW-CISO still carry ICE level proxies;
   eastern seams (MISO-SOCO, TVA spokes) have no evidence yet.
4. **Congestion horns** - use LMP price separations as 2-cells and fill the
   inner horn `plant -> ? -> congestion-cost` to attribute congestion.
5. **Gray coherence** - wire carefully into
   `komposos_wesys.core.energy_coherence` only after the data contracts above
   are stable.

## Data Sources

- eGRID: https://www.epa.gov/egrid/detailed-data
- EIA-923: https://www.eia.gov/electricity/data/eia923/
- PUDL: https://catalystcoop-pudl.readthedocs.io/
- EIA-930 API: https://www.eia.gov/electricity/gridmonitor/about
- LBNL queues: https://emp.lbl.gov/queues
- EAGLE-I: https://doi.ccs.ornl.gov/
- gridstatus: `pip install gridstatus`
