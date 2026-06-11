# Grid Domain — Categorical Analysis of Electrical Grid Waste

Domain package built on the KOMPOSOS-IV categorical runtime (`core.category`).
Targets the three bottlenecks where grid waste concentrates:

| Bottleneck | What is wasted | Primary datasets |
|---|---|---|
| **Curtailment** | Renewable energy discarded when the grid can't absorb/store it | LBNL Queued Up, EIA-930, storage profiles |
| **T&D losses** | Energy dissipating as heat; congestion trapping electricity | LMPs (gridstatus), PSML, ACTIVSg, EAGLE-I |
| **Peaker reliance** | Inefficient fossil plants covering demand spikes | eGRID, EIA-923, EIA-930, Electricity Maps |

The full dataset catalog, with access notes and implementation status, is in
`sources/registry.py`.

## Phase 0 (this code): data coherence

Before optimizing anything, confirm the data describes the same grid.
Each dataset is a *section* of the plant-data presheaf over the plants it
covers (keyed by EIA ORIS code). The sheaf gluing condition — sections agree
on overlaps — is the categorical statement of "the data is trustworthy".

```
python -m domains.grid.run_coherence --synthetic          # demo, no downloads
python -m domains.grid.run_coherence --egrid egrid2023_data_rev2.xlsx \
    --eia923 EIA923_Schedules_2_3_4_5_M_12_2023_Final.xlsx
```

Per-plant verdicts: `GLUE` (agree within tolerance), `TENSION` (known
adjustment territory: CHP, station use, net-vs-gross), `CONTRADICT`
(at least one source is wrong). Results are written back into the Category
as morphisms (`source:A -coheres_with-> source:B` with confidence =
agreement rate; `disputes` morphisms for contradictions), so COG
verification and OPTIMUS refinement see data quality as hom-values.

## Roadmap

1. **Level-1 coherence** — aggregate plant sections along the
   plant → balancing-authority functor (left Kan extension along the
   projection) and compare with EIA-930 BA-level hourly data. Disagreement
   at level 1 but not level 0 localizes errors to the plant↔BA assignment.
2. **Queue factorization** — run OPTIMUS factorization on LBNL Queued Up:
   which intermediate objects in `proposed → operational` predict the ~77%
   withdrawal rate.
3. **Congestion horns** — LMP price separations as 2-cells; fill the inner
   horn plant → ? → congestion-cost to attribute congestion to plants.
4. **Gray coherence** — wire into `komposos_wesys.core.energy_coherence`
   (interchange-law failures ↔ grid instability classes).

## Data sources (download manually, not committed)

- eGRID: https://www.epa.gov/egrid/detailed-data (eGRID2024 due Jan 2026)
- EIA-923: https://www.eia.gov/electricity/data/eia923/
- PUDL (cleaned + crosswalked): https://catalystcoop-pudl.readthedocs.io/
- EIA-930 API: https://www.eia.gov/electricity/gridmonitor/about
- LBNL queues: https://emp.lbl.gov/queues
- EAGLE-I: https://doi.ccs.ornl.gov/ (yearly DOIs)
- gridstatus: `pip install gridstatus`
