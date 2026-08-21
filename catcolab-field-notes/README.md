# catcolab-field-notes

Notes from using [CatColab](https://catcolab.org)'s experimental **Power
system** logic on real U.S. grid data.

**The short version.** I rebuilt a 13-bus slice of the Eastern Interconnection
seam (EIA-930 balancing-authority interchange, 2023) in the Power system logic,
ran its Kuramoto swing simulation with real tie volumes as capacities and real
net injections as forcing, and compared where the simulation loses synchrony
against the bottlenecks my own Ollivier-Ricci curvature / Fiedler analysis flags
on the same network. They rank the seams the same way — PJM–NYIS first, then
SOCO's hub — with one hole where the logic silently drops Link morphisms.

- **Model:** https://catcolab.org/model/01a0267c-b68e-7c31-89d2-47188cba42f6
- **Analysis:** https://catcolab.org/analysis/01a02690-b96e-7073-924e-2a4f24624843
- **Notes, comparison, and gap list:** [NOTES.md](NOTES.md)
- **Data and curvature pipeline:** [komposos-grid](https://github.com/Jayhawk314/komposos-grid)

## Why these notes exist

I tried Catlab.jl early on and bounced; built a Python stack over public grid
data instead (EIA-930, eGRID/EIA-923, LBNL interconnection queues), with sheaf
Laplacian consistency audits and flow-geometry analysis. CatColab is the first
Topos tool I've come back to as an actual user. The Power system logic is new
(merged November 2025), has no write-up and no issues, so the most useful thing
a domain user can do is put real data through it and say plainly where it could
and couldn't express what the data needs. That's what NOTES.md does — as
questions, not complaints, because several of them are ones the logic's own
source comments already ask.

## Contents

```
README.md                 this file
NOTES.md                  build log, Kuramoto-vs-curvature comparison, gap list
screenshots/
  kuramoto_x1.jpg         real capacities: PJM, NYIS, CPLE run free
  kuramoto_x0.3.jpg       capacities x0.3: SOCO hub (MISO, TVA, FPL) joins them
  kuramoto_x0.1.jpg       capacities x0.1: nearly everything runs free
  parameters_x0.1.jpg     the full parameter table as entered
```
