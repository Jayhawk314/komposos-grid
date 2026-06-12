# Reproduce a Headline Number from Scratch

This walks you from a fresh clone to independently confirming the
project's wind-belt headline:

> **MISO-SWPP seam, 2025: congestion-component spread 7.33 $/MWh,
> corridor value ≈ $31.1M/yr.**

This number was chosen as the reproduction target because every input
is **keyless public data** (no accounts, no API keys) and the
measurement is corroborated from both sides of the seam.

Found a different number, or friction along the way? Please open a
GitHub issue — reproduction reports are the most valuable
contribution this project can receive.

## What you need

- Python 3.10+
- `pip install pandas pytest`
- ~1 GB disk, a normal internet connection
- Time: ~10 minutes of commands; downloads run 30-90 minutes
  depending on connection (365 daily MISO files + two ~100 MB EIA
  files)

## Step 0 — Clone and sanity-check

```bash
git clone https://github.com/Jayhawk314/komposos-grid.git
cd komposos-grid
python -m pytest tests/test_grid_same_year_flows.py tests/test_grid_solution_cards.py -q
```

Expected: all tests pass, no network used.

## Step 1 — Measure the seam spread from MISO's own books

MISO publishes day-ahead settlement prices as daily files. This
command downloads all 365 days of 2025 (cached; safe to re-run after
interruptions) and computes the hourly spread between the
ARKANSAS.HUB reference and the SWPP interface node:

```bash
python -m domains.grid.run_miso_seam_evidence --start 2025-01-01 --end 2026-01-01 --out my_miso_2025.csv
```

Expected output (yours should match to the cent):

```
MISO seam ARKANSAS.HUB vs SWPP [2025-01-01..2025-12-31, 1 days missing]: 8736 hours,
mean LMP $33.46 vs $32.99, mean |spread| $7.85/MWh (max $124.15),
congestion component 93.4%, hub above 50.1% of hours
```

The headline component is **7.85 × 93.4% = 7.33 $/MWh**. Compare your
`my_miso_2025.csv` against the committed
`reports/miso_seam_evidence_2025.csv`.

## Step 2 — Measure how much energy actually crossed that border

The US Energy Information Administration publishes hourly flows
between balancing authorities (form EIA-930). Download 2025 and
extract the MISO-SWPP tie:

```bash
python -m domains.grid.fetch_eia930 --year 2025
python -m domains.grid.run_same_year_flows --interchange domains/grid/data/EIA930_INTERCHANGE_2025_Jan_Jun.csv domains/grid/data/EIA930_INTERCHANGE_2025_Jul_Dec.csv --year 2025 --pairs MISO-SWPP --out my_flows.csv
```

Expected:

```
MISO-SWPP 2025: gross 4,249,335 MWh, net 733,389 MWh
```

## Step 3 — Multiply, the long way

The corridor value is spread × flow. The full pipeline also rebuilds
the ranked corridor cards and applies the same-year gating logic:

```bash
python -m domains.grid.run_solution_cards
python -m domains.grid.run_solution_studies --same-year-flow reports/same_year_flows.csv --project-costs reports/project_costs.csv
```

Expected line in the output:

```
MISO-SWPP: $31,147,626/yr, ...
```

Cross-check by hand: 7.33 $/MWh × 4,249,335 MWh = $31.1M/yr.

## Step 4 — (Optional) check the verdict on the named fix

`reports/project_cost_results.csv` now contains the benefit/cost
bracket for Patent Gate–Pioneer 345 kV (the SPP-approved project
targeting this exact constraint, $163.7M published cost): B/C
**1.65** if it relieves the full observed seam congestion, **0.85**
at a conservative 250 MW attribution — counting *only* seam value.

## Notes and honesty

- "1 days missing" in Step 1: MISO occasionally skips a daily file;
  the loader reports rather than interpolates.
- The spread (Step 1) and the flow (Step 2) come from **two unrelated
  sources** (MISO settlement vs EIA telemetry). There is no shared
  pipeline that could correlate an error between them.
- An independent corroboration exists from the *other* side of this
  seam: SPP's own files give $6.12/MWh for 2023 vs $5.09 from MISO's
  (within ~20%); see `reports/spp_2023.json`.
- What this number is NOT: it is not all congestion between MISO and
  SPP (it's one priced interface), and the corridor value assumes the
  spread applies across the observed gross flow — see
  `reports/MASTER_GUIDE.md` §6 for the full trust ledger.

## Data retention warning

MISO daily files and CAISO OASIS have finite retention windows
(OASIS ≈ 39 months). If a Step 1 download 404s for old dates, open an
issue — we maintain archives of the evidence-chain inputs.
