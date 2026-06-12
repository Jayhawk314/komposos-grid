PUBLIC : https://github.com/Jayhawk314/komposos-grid.git


# The Grid Waste Project — Master Guide

*Last updated: 2026-06-12. Maintained alongside `reports/agent_handoff.md`
(working state) and `domains/grid/PLAN.md` (roadmap). Everything here is
reproducible from public data; every number names its source.*

---

## 1. What is this?

This project measures **how much money and energy the United States
electric grid wastes**, using only public data, and then asks the only
question that matters about each piece of waste: **what specific thing
would fix it, and would the fix pay for itself?**

> **In plain English:** The power grid is like a highway system for
> electricity. Some roads are congested, so cheap electricity in one
> place can't reach people paying high prices somewhere else. Power
> plants get told to shut off because their power has nowhere to go.
> Outages cost people billions of hours without electricity. All of
> that is *waste*, and all of it leaves fingerprints in public data —
> prices, flows, outage logs. This project reads those fingerprints,
> adds up the waste in dollars, and then checks whether known
> construction projects would be worth building to fix it.

It runs on KOMPOSOS-IV, a categorical AI engine (objects, morphisms,
verified reasoning). The grid work lives in `domains/grid/` and writes
its outputs to `reports/`. You do not need to understand the engine to
use the findings — every result lands in plain CSV and Markdown files.

---

## 2. How to read the numbers

The same few units appear everywhere:

| Unit | Meaning | Plain English |
|---|---|---|
| **MWh** (megawatt-hour) | 1,000 kWh of energy | Roughly what one US home uses in a month |
| **TWh** (terawatt-hour) | 1 million MWh | A million home-months; city-scale energy |
| **$/MWh** | price of energy | The wholesale price; retail is ~3-5x higher |
| **spread ($/MWh)** | price difference between two places at the same hour | If it costs $30 here and $37 there, the spread is $7 — that $7 is what congestion takes |
| **B/C ratio** | benefit ÷ cost, per year | Above 1.0 = the fix pays for itself; below 1.0 = it doesn't (on the measured benefit alone) |
| **capex** | capital expenditure | The construction price tag |
| **FCR** (fixed charge rate) | converts capex to a yearly cost | We use 10%: a $100M project "costs" $10M/yr (covers financing, depreciation, return) |
| **binding hours** | hours a constraint limited flow | Out of 8,760 hours in a year, how often the bottleneck actually pinched |

---

## 3. The headline findings

### 3.1 The waste, measured (2023 baseline year)

| What | Number | Source |
|---|---|---|
| Congestion cost over 7 measured inter-regional ties | **$78.6M/yr** | ISO settlement prices (NYISO, CAISO OASIS, MISO) |
| Waste ledger total (all verified claims) | **$251.0M, 28 claims** | `reports/` waste ledger |
| CAISO curtailment (solar/wind told to shut off) | **2.66 TWh, 78% congestion-driven, ≤$172.5M** | CAISO public curtailment data |
| SPP curtailment | **10.37 TWh — 4x CAISO's, 82% congestion-driven** | SPP public files |
| Reliability: customer-hours without power | **1.059 billion hours** | DOE EAGLE-I, full year 2023 |
| Reliability, in dollars | **floor $4.4B / blended $142.1B / high $176.8B per year** | Sullivan 2015 coefficients × EAGLE-I |
| Interconnection queue completion rate | **16.5% of 29,010 decided projects** | LBNL queue data |
| Withdrawn projects that could have relieved the worst tie | **4,205 projects, 524 GW** (PJM-NYIS alone) | LBNL queue × constraint matching |

> **In plain English:** In 2023 the grid wasted at least a quarter of a
> billion dollars in directly measurable price congestion, threw away
> 13 TWh of clean energy (enough for over a million homes), and people
> lost over a billion combined hours of electric service — worth
> roughly $140B/yr when valued the way the Department of Energy does
> (our independent bottom-up estimate, $142.1B, lands on DOE's ~$150B
> national number — a strong sign the method is sound). Meanwhile,
> 83.5% of proposed power projects die waiting in line to connect.

**A caution that matters:** the blended reliability number ($142.1B)
is screening-grade — it depends on assumed customer mixes. The floor
($4.4B) is the defensible minimum. Always say which one you're using.

### 3.2 The two seams that matter most (and how fast they're getting worse)

A "seam" is a border between two grid operators. The price spread
across a seam is money lost every hour the border is congested.

| Seam | Congestion spread trend ($/MWh) | 2025 annual value | Status |
|---|---|---|---|
| **PJM ↔ New York (NYIS-PJM)** | 2023: $1.53 → 2024: $2.02 → 2025: **$7.38** (4.8x in two years) | **$159.7M/yr** | Priority study |
| **MISO ↔ Southwest Power Pool (MISO-SWPP)** | 2023: $4.74 → 2024: $6.31 → 2025: **$7.33** (1.5x) | **$31.1M/yr** | Priority study |
| MISO ↔ Southern Co (MISO-SOCO) | 2023: $1.35 → 2024: $1.53 → 2025: $2.09 | $11.2M/yr | Bounded screen |
| California ↔ Arizona (CISO-SRP) | corrected to $1.39 | $14.0M/yr | Validated screen |
| Northwest ↔ California (BPAT-CISO) | corrected to $1.11 | $6.1M/yr | Validated screen |
| ERCOT West-North (Texas, internal) | 2023: $4.94 → 2024: $5.40 → 2025: $5.78 | not yet valued | Watchlist |

> **In plain English:** Two borders are getting dramatically worse.
> New York paid more than PJM (its neighbor to the south/west) in
> **97.9% of all hours in 2025** — New York is almost permanently the
> expensive side, importing every single hour. And in the upper
> Midwest, a wind-country bottleneck keeps growing every year. These
> trends match the national story: electricity demand is growing
> again (data centers, electrification) while new supply is stuck in
> the connection queue.

The annual values use **same-year flows** (fixed 2026-06-12): the
2025 spread × the 2025 actual flow on that border (21,635,807 MWh for
NYIS-PJM; 4,249,335 MWh for MISO-SWPP, from EIA-930). Earlier versions
used 2023 flows; the reports now flag any year mismatch automatically.

### 3.3 The bottleneck with a name, an owner, and a price tag

The single most-binding constraint in the central US is one piece of
physical equipment:

- **What:** the Charlie Creek–Watford City 230 kV line in western
  North Dakota, owned by the federal **Western Area Power
  Administration (WAPA)**.
- It appears in **MISO's** data as `CHAR_CK-WATFORD` (bound 5,138
  hours in 2023 = 59% of the year, MISO's largest congestion cost)
  and in **SPP's** data as flowgate `CHAWATCHAPAT` (bound 5,951
  hours; SPP's highest-priced constraint). **Verified: these are the
  same physical line**, coordinated between the two markets
  ("market-to-market") — so never add the two numbers together.
- **Why it blew up:** a crypto-mining data center (Atlas Power, near
  Williston ND) added huge load behind a line built for a quieter
  era. Two FERC complaints about the cost mess (EL24-61, EL24-85)
  were dismissed in Oct 2024.
- **The named fix:** SPP's 2024 transmission plan selected
  **Patent Gate–Pioneer 345 kV** (Basin Electric, 33.5 miles,
  **$163,714,033**, construction notice issued) explicitly to relieve
  this constraint.
- **Our verdict (2025 evidence):** benefit/cost between **0.85 and
  1.65** counting *only* the MISO-SWPP border value. The honest
  reading: it roughly breaks even on the border alone, and the line's
  *other* benefits (relieving MISO's largest internal congestion
  cost, voltage problems) are not counted yet — so the true B/C is
  likely well above 1.

> **In plain English:** We found the grid's worst traffic jam, the
> agency that owns the road, the reason traffic exploded (a bitcoin
> mine moved in), and the bypass highway that's already been approved
> — and we checked the bypass's price against the traffic it would
> clear. It's worth building.

A useful cost anchor nearby: the very similar Kummer Ridge–Roundup
345 kV line (33.2 mi) cost $78,977,357 and was energized 2024-12-17 —
five months early. New 345 kV transmission in this region runs $2.4M
to $4.9M per mile.

### 3.4 The natural experiment: CHPE just switched on

On **2026-05-13**, the Champlain Hudson Power Express (CHPE) — a
1,250 MW, ~$6 billion underground/underwater power line from Quebec
to New York City — went live. If New York's import hunger drove the
exploding PJM-NYIS spread, CHPE should shrink it.

First measurement (one month of data, `reports/chpe_event_study.md`):

| Window | Mean spread | Congestion part | NY more expensive |
|---|---|---|---|
| Spring 2025, pre-May-13 | $1.11 | $0.41 | 95.7% of hours |
| Spring 2025, post-May-13 | $2.10 | $1.35 | 98.8% |
| Spring 2026, pre-CHPE | $2.64 | $1.42 | 97.4% |
| Spring 2026, post-CHPE | $3.24 | $2.05 | 97.8% |

Result: a **difference-in-differences of −0.31 $/MWh** — mild relief
beyond normal seasonal patterns, but **the spread did not collapse**.
New York is still the expensive side ~98% of hours.

> **In plain English:** A "difference-in-differences" is how you
> tell whether a medicine worked when the patient was getting sicker
> anyway. Spreads always rise from spring into summer (seasonality) —
> so we compare this year's rise against last year's rise. This
> year's was slightly smaller, by $0.31/MWh. So CHPE is helping a
> little, but one new power line did not cure New York's import
> problem — at least not in its first month, in the low season. The
> summer data will tell the real story.

**Consequence:** the $159.7M/yr NYIS-PJM value is an **upper bound**
for any decision made after 2026 — and the first month of evidence
says it is not collapsing to zero either.

### 3.5 The methodology lesson worth more than any single number

Early versions of this work used annual *hub price level* differences
(from ICE trading data) as congestion estimates. When validated
against actual hourly settlement data, those proxies were
**overstated 7–9x** (mean 8.0x): CISO-SRP fell from $142M to $14M;
BPAT-CISO from $9.47 to $1.37/MWh.

This correction is now baked in as a permanent rule (formally: a
2-cell methodology axiom in the engine): **hub-level proxies without
an hourly settlement correction are screening-only, never decision
numbers.** And the reverse lesson from NYISO: annual *average* price
differences understate congestion, because the sign flips hour to
hour — you must average the hourly *absolute* spread.

> **In plain English:** Comparing two cities' average yearly prices
> tells you almost nothing about the traffic between them. You have
> to compare prices *hour by hour* and look at the hourly gap. When
> we fixed this, some scary-big numbers shrank 9x — and we made the
> system remember the lesson so no future analysis can repeat the
> mistake quietly.

### 3.6 Other findings worth knowing

- **Constraint severity tables** (2023, "severity" = shadow-price ×
  hours index, NOT dollars): MISO 2,463 constraints / 10.07M index;
  SPP 1,532 / 7.78M; PJM 857 / 3.81M. PJM's worst: Nottingham 230 kV,
  binding 69% of the year. Cross-checks: two flowgates (Chicago-
  Praxair3, Turkey Hill-Hilgard) rank high in *both* MISO and PJM
  tables independently — corroboration the data is real.
- **Two-sided seam check:** the MISO-SPP border measured from SPP's
  own data gives $6.12/MWh vs $5.09 from MISO's data (2023) — within
  ~20%. Two operators' independent books agree on the same border.
- **Queue dynamics:** projects that reach a signed interconnection
  agreement complete at ~4x the base rate. The queue is not a lottery
  — it's a funnel with one decisive gate.
- **Texas:** ERCOT's West-North spread grows every year (wind in the
  west, load in the north) — same national pattern, no seam involved.
- **NYIS-PJM flow is one-directional:** in 2025, every single hour
  of net flow went PJM → New York (21.6M MWh gross). New York's
  dependence is structural, not occasional.

---

## 4. How the pieces fit (the chain of reasoning)

1. **Find the bottleneck** — price spreads and binding constraints
   say *where* (Section 3.2, 3.6).
2. **Price the waste** — spread × actual flow = dollars per year
   (Section 3.2: $159.7M, $31.1M).
3. **Name the fix** — match constraints to real projects: queue
   projects that died, or planned lines (Section 3.3: Patent
   Gate–Pioneer).
4. **Gate the fix** — does benefit ÷ cost clear 1.0? With what
   counted and what not? (B/C 0.85–1.65.)
5. **Watch reality answer** — when something big changes (CHPE),
   measure the before/after (Section 3.4).

Every step has a guard: same-year flow gates (price year must match
flow year), proxy-correction axioms, "do not double-count the two
sides of one seam," and relief capped at the border's observed flow
(a project can't claim to relieve more congestion than exists).

---

## 5. How to use it

### Setup

Python 3.10+, `pip install -r requirements.txt`, run everything from
the repo root. Most data sources are keyless (no account needed).
Large data files live in `domains/grid/data/` (gitignored — you
re-download them; the handoff documents every URL pattern).

### The five commands that matter

```powershell
# 1. The decision products: corridor studies, memos, project B/C
python -m domains.grid.run_solution_studies `
  --same-year-flow reports\same_year_flows.csv `
  --project-costs reports\project_costs.csv

# 2. Rebuild the ranked corridor cards (feeds #1)
python -m domains.grid.run_solution_cards

# 3. The CHPE natural experiment (rerun as new months land)
python -m domains.grid.run_chpe_event_study

# 4. Refresh seam evidence for a new year (example: MISO 2025)
python -m domains.grid.run_miso_seam_evidence `
  --start 2025-01-01 --end 2026-01-01 `
  --out reports\miso_seam_evidence_2025.csv

# 5. Extract actual border flows for a year (feeds #1)
python -m domains.grid.run_same_year_flows `
  --interchange domains\grid\data\EIA930_INTERCHANGE_2025_Jan_Jun.csv `
                domains\grid\data\EIA930_INTERCHANGE_2025_Jul_Dec.csv `
  --year 2025 --pairs NYIS-PJM MISO-SWPP `
  --out reports\same_year_flows.csv --append
```

There is also a zero-credential daily pulse
(`python -m domains.grid.run_daily_update`) that appends yesterday's
seam metrics to `reports/daily/`.

### Feeding it your own data (the two intake files)

- **`reports/same_year_flows.csv`** — border flows by year. Add a row
  when you have flow evidence for a new corridor/year.
- **`reports/project_costs.csv`** — real project costs. Add a row per
  project (capex, O&M or explicit annual cost, capacity, owner,
  source) and rerun command #1; you get B/C, net annual value, and a
  clears/doesn't-clear verdict per project in
  `reports/project_cost_results.csv` and in the memos.

**Do not edit `*_template.csv` files** — they are regenerated on
every run and your edits will be overwritten. The two files above are
the durable ones.

### Where the answers land

| File | What it is |
|---|---|
| `reports/energy_solution_studies.md` | The main report: both priority corridors, all gates |
| `reports/solution_studies/nyis_pjm.md`, `miso_swpp.md` | One-page decision memos per corridor |
| `reports/project_cost_results.csv` | B/C verdict for every costed project |
| `reports/energy_solution_cards.md` | All six corridors ranked, with status labels |
| `reports/chpe_event_study.md` | The CHPE before/after measurement |
| `reports/agent_handoff.md` | Full working history, gotchas, next steps |
| `tests/` | 438 passing tests; run `pytest -q` after any change |

### Status labels, decoded

- **priority_solution_study** — value is large and growing; worth
  real engineering/costing effort now.
- **methodology_validated_screen** — number is trustworthy but small;
  use for siting screens, not investment cases.
- **bounded_solution_screen** — we can only bound it (data gap);
  treat as a ceiling, not a measurement.
- **watchlist** — a real trend with no dollars attached yet.

---

## 6. What to trust, and how much

| Claim type | Trust level | Why |
|---|---|---|
| Seam spreads & congestion components | **Measured** | Hourly settlement data from the operators' own books; two-sided cross-check agrees within 20% |
| Corridor annual values ($159.7M, $31.1M) | **Measured × measured** | Same-year spread × same-year actual flow |
| Constraint identities (CHAWATCHAPAT = Charlie Creek) | **Verified** | SPP market monitor's own definition table |
| Project costs (Patent Gate–Pioneer $163.7M) | **Published estimate** | SPP planning document, 2024 dollars; actuals may differ |
| B/C brackets | **Screening** | Honest about what's counted; O&M is assumed (1.5%/yr); relief attribution is bracketed, not known |
| Reliability blended $142.1B | **Screening** | Coefficient assumptions; the $4.4B floor is the defensible number |
| Curtailment dollar caps | **Upper bounds** | "≤" means at most |
| CHPE DiD (−0.31) | **Early signal** | One month, low season; rerun in September |
| Severity indexes (10.07M etc.) | **Index only** | Useful for ranking, meaningless as dollars |

The general rule baked into everything: **screening numbers find
where to look; only measured numbers justify spending money.** The
reports enforce this by flagging year mismatches, capping relief at
observed flows, and carrying caveats into every memo automatically.

---

## 7. Glossary (plain English)

- **Balancing Authority (BA):** the organization keeping supply =
  demand in one region. The US has ~70. NYIS = New York, PJM =
  mid-Atlantic, MISO = upper Midwest, SWPP/SPP = central plains,
  CISO = California, ERCO/ERCOT = Texas, SOCO = Southern Co, BPAT =
  Bonneville (Northwest).
- **Seam:** the border between two of them.
- **LMP / LBMP (locational marginal price):** the wholesale price of
  electricity *at a specific place and hour*. Prices differ by
  location precisely because wires fill up.
- **Congestion component:** the slice of that price caused by full
  wires (the operators publish the breakdown — price = energy +
  congestion + losses).
- **Constraint / flowgate:** a specific piece of equipment (line,
  transformer) that hits its limit. "Binding" = at its limit right
  now, forcing more expensive plants to run.
- **Shadow price:** what one more MW of room on that wire would have
  been worth that hour. The operator's own number for "this
  bottleneck is costing us $X right now."
- **Market-to-market (M2M):** when one physical line is congested,
  the two markets on either side coordinate (and pay each other) to
  manage it. One line, two ledgers — count it once.
- **Curtailment:** ordering a wind/solar plant to stop producing,
  usually because the wires can't carry it. Free energy, discarded.
- **Interconnection queue:** the waiting line to plug a new power
  plant into the grid. Multi-year waits; 83.5% never make it.
- **EIA-930:** the federal hourly dataset of demand, generation, and
  flows between BAs. Public, no key needed.
- **Gross flow vs net flow:** gross = total traffic both directions;
  net = the imbalance. NYIS-PJM 2025: net = gross — *all* traffic
  ran one way.
- **DAM (day-ahead market):** prices set the day before, hourly.
  Most settlement happens here; it's the cleanest public record.
- **HVDC:** high-voltage direct current — long-distance point-to-
  point power lines (CHPE is one). Like an express train: huge
  capacity, no intermediate stops.
- **NTC (Notification to Construct):** SPP's formal "you are
  directed to build this" letter. NTC-C = conditional version.
- **Fixed charge rate (FCR):** the fraction of construction cost a
  utility effectively pays per year to own the asset (financing +
  depreciation + return). 10% is a standard screening default.
- **Difference-in-differences (DiD):** before/after comparison with
  a control year, so seasonal patterns don't fool you.
- **Screening-grade:** good enough to decide where to dig deeper;
  not good enough to commit money.
- **2-cell (engine term):** a recorded, verified relationship between
  two *methods* — e.g. "the hub-proxy method overstates the
  settlement method by 9x here." It's how the system remembers
  methodology corrections permanently.
- **Right Kan bound (engine term):** the most conservative estimate
  consistent with neighboring measurements — used to put a ceiling
  on seams we can't price directly (the Southeast ones).

---

## 8. One-paragraph summary, no jargon at all

We used public data to find where America's electric grid wastes the
most money. Two border crossings stand out and are getting worse
fast: New York's connection to the mid-Atlantic grid (now ~$160M a
year of congestion, quadrupled in two years) and a wind-country
bottleneck in North Dakota (~$31M a year and climbing, made worse by
a bitcoin mine). For the North Dakota one, we found the exact
approved construction project that would fix it and showed it
roughly pays for itself from the border savings alone — before even
counting its other benefits. For New York, a giant new cable from
Canada just switched on; our first measurement says it's helping
slightly but hasn't solved the problem. Beyond these, the grid threw
away enough clean energy in 2023 to power a million homes, and
outages cost Americans over a billion hours without power. All of it
is reproducible: the data is public, the code is here, and every
number tells you where it came from.
