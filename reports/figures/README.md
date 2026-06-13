# The Findings in Four Pictures

Every chart on this page is generated straight from the data by
`python -m domains.grid.run_dashboard` — nothing is drawn by hand.
Each one comes with a plain-language explanation. Full details and
sources: [`../MASTER_GUIDE.md`](../MASTER_GUIDE.md).

---

## 1. The problem is getting worse, fast

<img src="seam_trends.svg" width="560" alt="Seam congestion spread by year">

**What it shows:** Each line is a border between two regional grid
operators. The height is the average hourly price gap caused by
congestion across that border, in dollars per megawatt-hour.

**In plain English:** Think of each line as a toll that traffic jams
quietly charge on electricity crossing a border. The blue line is the
New York–PJM border: its toll more than tripled in one year
(2024→2025). When a line goes up, it means wires at that border are
full more often, and someone is paying for it — ultimately, customers.

**What to watch:** Whether the blue line comes down after 2026 (a big
new power line into NYC just opened — see chart 4), and whether the
green line (the Midwest wind belt) keeps climbing.

---

## 2. What each bottleneck costs per year

<img src="corridor_values.svg" width="560" alt="Annual congestion value per corridor">

**What it shows:** The price gap from chart 1 multiplied by the
actual electricity that crossed each border — giving dollars per
year. New York–PJM: about $160M/yr. The Midwest wind belt: $31M/yr.

**In plain English:** Chart 1 was the toll per truck; this is the
total tolls collected per year on each road. It tells you which
bottleneck is worth fixing first. One caution: the tallest bar is an
*upper bound* for future years, because relief just arrived (chart 4).

**What to watch:** These bars set the budget a fix can justify. A fix
costing less per year than the bar is worth doing on congestion
savings alone.

---

## 3. Does the named fix pay for itself?

<img src="project_bc.svg" width="560" alt="Project benefit/cost ratios vs break-even">

**What it shows:** Real projects with real published price tags,
scored as benefit ÷ cost per year. Above the dashed line (1.0), the
project pays for itself from congestion savings alone.

**In plain English:** The two middle/right bars are the *same*
project — a $164M power line in North Dakota that grid planners
already approved to fix the wind-belt jam — scored two ways: if it
clears all the border congestion (1.65, comfortably pays) and under
a deliberately stingy assumption (0.85, almost pays). The truth is
in between, and the project has other benefits we did not count. The
tiny left bar is the $6B Canada–NYC cable: a fine project for other
reasons, but border congestion alone could never justify it — which
is exactly what the chart is for: it tells you *which kind* of fix
matches which problem.

**What to watch:** As real operating costs replace our assumptions,
the bars firm up. Anything that stays above the line is a
ready-to-cite case for construction.

---

## 4. The experiment: did the big new cable help?

<img src="chpe_event_study.svg" width="560" alt="PJM-NYIS seam before and after CHPE">

**What it shows:** The New York–PJM price gap in four windows: the
month before and after May 13 — in 2025 (when nothing changed) and
in 2026 (when the 1,250 MW Champlain Hudson cable switched on).

**In plain English:** Price gaps naturally grow from spring into
summer — you can see that in the 2025 pair. So you can't just compare
before/after in 2026; you compare *the growth* in 2026 against *the
growth* in 2025. The 2026 growth was slightly smaller: the cable is
helping, by about $0.31/MWh so far. But the bars are still taller
than last year's — one cable did not cure New York's import problem
in its first month.

**What to watch:** The summer 2026 bars (rerun in September). Summer
is when congestion money is really made and lost; that data decides
whether the $160M/yr in chart 2 shrinks for good.

---

*Regenerate after any data update: `python -m domains.grid.run_dashboard`.
The same charts appear on the public dashboard (`docs/index.html`).*
