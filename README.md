# Komposos Grid — Independent Interconnection Analytics

An independent, reproducible analysis of U.S. generator interconnection queues,
built to support the DOE **i2X STITCH** conversation on interconnection study
harmonization.

> **Independence.** This is a personal, unfunded project by one analyst. It is
> **not affiliated with, sponsored by, or endorsed by** DOE, ESIG, Berkeley Lab,
> Elevate Energy Consulting, or any ISO/RTO. Any errors are mine alone.

**Interactive dashboard:** https://komposos-grid.streamlit.app

---

## The headline finding

**An executed Interconnection Agreement is not the same milestone in every region.**

Factoring the interconnection completion funnel through the executed-IA milestone,
using Berkeley Lab's *Queued Up* data:

| | Executed IA | Built after signing | Withdrew after signing | **Post-IA completion** |
|---|---:|---:|---:|---:|
| **MISO** | 1,365 | 476 | 889 | **34.9%** |
| **ERCOT** | 610 | 486 | 124 | **79.7%** |

An executed IA is an ~80% completion promise in ERCOT and roughly a coin-flip in
MISO — while **end-to-end timelines are nearly tied** (MISO 39.1 months request→COD,
ERCOT 44.3). ERCOT's advantage is not raw speed; it is a faster path to a
*high-certainty contract*. The two regions distribute certainty differently across
the process.

This matters for harmonization because milestone-based cross-region comparisons —
and developer capital decisions keyed to the IA — are not comparing like with like
until the *certainty content* of each milestone is normalized.

**Coverage note:** post-IA completion is computable in 8 of 9 regions. SPP's
records in this dataset do not associate an executed-IA date with withdrawn
projects, so the milestone's certainty content cannot be computed there. That
gap is itself a harmonization finding about milestone data coverage.

## Verify it yourself

The **baseline** reconciles to Berkeley Lab's published regional table (*Queued
Up* Sheet 25) **to the integer**, denominators included, before any new analysis
is layered on — so the starting point is shared ground truth rather than a new
methodology to argue about.

The **headline finding above is our own computation**, and is labelled that way
throughout. LBNL publishes post-IA completion at national level only (Sheet 27);
the per-region split is ours. It is reproducible from the same public workbook,
but it is not an LBNL-published figure and should never be cited as one.

```bash
git clone https://github.com/Jayhawk314/komposos-grid.git
cd komposos-grid
pip install -r requirements.txt
python -m pytest tests/test_grid_same_year_flows.py tests/test_grid_solution_cards.py -q
```

[`REPRODUCE.md`](REPRODUCE.md) walks from a fresh clone to independently
confirming a separate headline (a MISO–SPP seam spread) using only **keyless
public data** — no accounts, no API keys. Reproduction reports are the single
most valuable contribution this project can receive; please
[open an issue](https://github.com/Jayhawk314/komposos-grid/issues) if your
numbers differ.

## How to read the numbers

Every figure in the dashboard carries a provenance badge. Please respect the tiers:

| Badge | Meaning |
|---|---|
| 📏 **Measured** | Reconciles to a published external dataset (e.g. LBNL *Queued Up*). |
| 🧮 **Derived** | Computed by this project's models from measured inputs or user-set parameters. |
| 🧪 **Simulated** | Stylized/illustrative scenario. **Not observations.** Do not cite as data. |

Two further cautions, stated plainly:

- The **Harmonization Matrix** page is an *uncited working hypothesis*. Every cell
  was hand-assembled from public process documents and session impressions; none is
  yet sourced to a specific tariff, business practice manual, or RTO presentation.
  It is a discussion draft — verify any cell before quoting it.
- **Session notes are the author's own takeaways** from attending, not official
  minutes, and are not attributable to any presenter.

## Dashboard pages

| Page | What it shows | Tier |
|---|---|---|
| Regional Queue Study | 9-region queue funnels, milestone durations, the IA-Certainty Spectrum | 📏 Measured |
| Harmonization Matrix | Cross-region study-practice divergences | ⚠️ Uncited draft |
| STITCH Session Notes | Meeting reference and prep checklists | Author's notes |
| Grid Network Map | Interactive BA interchange map, curvature bottlenecks | 🧮 Derived |
| Seam Congestion Findings | Where the grid loses money, and whether fixes pay | 📏 / 🧮 |
| Seam Opportunity Screen | Yoneda similarity, Kan-extension seam proxies, relief curves | 🧮 Derived |
| Large Load Siting (ESIG) | Data-center interconnection coordination scenarios | 🧪 Simulated |
| Nuclear Enrichment Bottlenecks | HALEU supply-chain systems model | 🧪 Simulated |

The seam-screening page uses category-theoretic machinery (Yoneda similarity for
structural BA matching, right Kan extensions to transfer a priced tie's spread
across an unpriced interface, sheaf cohomology for cross-dataset auditing). These
are **screening indicators** that nominate candidates for study — they are not
measured congestion costs, not mathematical bounds, and not investment advice.

## Running it

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Regenerating the analytical artifacts:

```bash
python -m domains.grid.run_stitch_brief --with-peers      # 9-region queue study
python -m domains.grid.run_region_packs                   # per-region engagement packs
python -m domains.grid.run_untapped_analytics             # seam opportunity screening
python -m domains.grid.experiments.large_load_coordination # ESIG large-load scenario
```

Pipelines that ingest raw market data need source files under `domains/grid/data/`
(not committed — see [`REPRODUCE.md`](REPRODUCE.md) for how to fetch them). A fresh
clone without that directory will see failures in `tests/test_grid_agent_server.py`;
the rest of the suite passes offline.

## Data sources

This project **redistributes no third-party dataset in raw form**. It reads public
data you fetch yourself, and commits only derived summaries.

| Source | Publisher | Status |
|---|---|---|
| *Queued Up* interconnection queue data — 2026 Edition, data through year-end 2025 | Lawrence Berkeley National Laboratory ([emp.lbl.gov/queues](https://emp.lbl.gov/queues)) | Published for public use; cite Berkeley Lab |
| EIA-930 hourly interchange | U.S. Energy Information Administration | U.S. Government work — public domain in the U.S. |
| eGRID plant-level generation | U.S. Environmental Protection Agency | U.S. Government work — public domain in the U.S. |
| Day-ahead LMP / settlement data | MISO, PJM, ERCOT, NYISO, SPP, CAISO | Each operator's own terms of use |
| WESyS waste-to-energy model (`data/external/`) | NREL / Alliance for Sustainable Energy | BSD-2-Clause — see its own LICENSE |

## License

**Code** in this repository is licensed under [Apache License 2.0](LICENSE).

**No copyright is claimed in the underlying public data.** The interconnection
queue, telemetry, emissions, and market data this project analyzes belong to their
respective publishers and remain governed by their terms, not by this repository's
license. See [`NOTICE`](NOTICE) for the full scope statement and third-party
attributions.

Original written analysis and documentation are offered under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — use it, adapt it, just
cite it.

Apache-2.0 already permits commercial use. If your organization wants something
beyond it — support, custom work, or a different arrangement — just email me.

## Contact

James Hawkins · jhawk314@gmail.com

Corrections are genuinely welcome. If a number here disagrees with your own, that
is the most useful message you can send me.
