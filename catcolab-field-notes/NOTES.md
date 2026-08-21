# Field notes: real U.S. grid data in CatColab's experimental Power system logic

*2026-08-21. Model and analysis built live in catcolab.org; everything below is
what the tool actually did, not what the docs say.*

- **Model:** https://catcolab.org/model/01a0267c-b68e-7c31-89d2-47188cba42f6
- **Analysis:** https://catcolab.org/analysis/01a02690-b96e-7073-924e-2a4f24624843
- **Data source:** EIA-930 balancing-authority interchange, 2023, as committed in
  [komposos-grid](https://github.com/Jayhawk314/komposos-grid) `reports/flow_bottlenecks.json`
  (63 BAs / 144 ties; Ollivier-Ricci curvature per tie, Fiedler partition).

## 1. What was built

A 13-bus slice of the Eastern Interconnection seam neighborhood — PJM, NYIS,
ISNE, NBSO, CPLE, MISO, SWPP, SPA, AECI, TVA, SOCO, FPL, FPC — with the 11 ties
that appear in the committed bottleneck list. Each **Bus** is an entire
balancing authority; each **Line** is a BA-to-BA tie oriented along the 2023
net-flow direction. One tie, MISO–SWPP (market-to-market coordinated), was
deliberately declared a **Link** (controllable flow) instead of a Line.

| Tie (net direction) | gross MWh | net MWh | OR curvature | CatColab type |
|---|---|---|---|---|
| NYIS → PJM | 19,294,263 | 19,294,263 | −0.107 | Line |
| SOCO → MISO | 5,355,783 | 5,239,233 | −0.151 | Line |
| SOCO → TVA | 5,660,484 | 3,456,874 | −0.079 | Line |
| CPLE → PJM | 4,242,136 | 3,029,290 | −0.086 | Line |
| MISO → SWPP | 3,989,884 | 849,274 | −0.095 | **Link** |
| FPL → SOCO | 3,527,415 | 2,810,915 | −0.208 | Line |
| SWPP → AECI | 2,800,533 | 2,095,465 | −0.042 | Line |
| SPA → SWPP | 1,512,521 | 595,421 | ~0 | Line |
| AECI → TVA | 1,198,856 | 1,198,716 | −0.036 | Line |
| FPC → SOCO | 419,575 | 81,651 | −0.095 | Line |
| NBSO → ISNE | (not in committed list) | — | +0.5 | Line |

**Known omission:** physically real intra-slice ties that aren't in the
committed bottleneck list (MISO–PJM, NYIS–ISNE, MISO–TVA, PJM–TVA-adjacent
paths) are absent. Nothing was invented to fill them; the gap is stated here
instead. NBSO–ISNE was included for topology only and given the default
capacity of 1.

## 2. Kuramoto analysis — what was entered

The Power system logic attaches a second-order Kuramoto ("swing equation")
simulation. Per-bus fields: Damping, Input power, Initial phase, Initial
frequency. Per-tie field: Capacity. Order = second, Duration = 10 (defaults).

- **Capacity** = gross_MWh / 10⁶ (uniform scaling; 19.29 for NYIS–PJM … 0.42 for FPC–SOCO).
- **Input power** = within-slice net injection, Σ signed net_MWh / 10⁶
  (exports positive). Computed from the table above, sums to zero:

  | PJM | NYIS | ISNE | NBSO | CPLE | MISO | SWPP | SPA | AECI | TVA | SOCO | FPL | FPC |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|
  | −22.32 | +19.29 | 0 | 0 | +3.03 | −4.39 | +0.65 | +0.60 | −0.90 | −4.66 | +5.80 | +2.81 | +0.08 |

  These are *within-slice* positions, not total BA generation — PJM's −22 is
  "what PJM absorbs from NYIS and CPLE," nothing more.
- **Damping** = 1 on every bus. (The UI default is 0, not 1 — see gap 9.)
- Initial phase/frequency left at 0.

## 3. Result: where the toy desynchronizes vs. where curvature flags

Three runs, scaling every capacity by ×1, ×0.3, ×0.1 with injections fixed
(screenshots in `screenshots/`). The plot is phase wrapped to ±π versus time;
a node that "saw-tooths" never phase-locks.

| Scale | Runs free (desynchronized) | Locks |
|---|---|---|
| ×1 | **PJM, NYIS, CPLE** | everything else |
| ×0.3 | PJM, NYIS, CPLE + **MISO, SOCO, TVA, FPL** | SWPP, SPA, AECI, FPC, ISNE, NBSO |
| ×0.1 | every bus with non-trivial injection | ISNE, NBSO, FPC (≈ zero injection) |

**Reading it.** A Kuramoto node can lock only if its forcing is no larger than
the coupling it can lean on. NYIS has +19.29 of forcing and exactly one tie of
capacity 19.29 — it is precisely marginal and spins. PJM's −22.3 against
19.29 + 4.24 = 23.5 is barely inside the bound and still fails because its
only large neighbor is itself spinning. CPLE (+3.0 on one 4.24 tie) is dragged
along. So at real 2023 volumes the toy's first seam is **PJM–NYIS**, which is
the top Eastern bottleneck in the curvature analysis (−0.107). The second
cluster to go (×0.3) is **SOCO's hub** — its ties to MISO (−0.151) and FPL
(−0.208) are the two most negatively curved ties in the slice.

**Order of failure agrees with the curvature ranking; the reason is partly
mundane.** Both methods are, in the end, reading the same quantity: how much
net flow a tie carries relative to what's around it. Curvature sees it as
geometry (few alternative paths → negative), Kuramoto sees it as forcing
exceeding coupling. The honest statement for Topos: *their swing simulation
and my curvature pipeline rank the seams the same way on real data*, which is
a good demo of the logic — and a caution that neither is seeing something the
other can't.

Where they **disagree**: MISO–SWPP (−0.095) is invisible to the simulation,
because it's a Link (see gap 4). SWPP's only live couplings are to AECI and
SPA, which is why the SWPP/SPA/AECI pocket survives ×0.3 — it has small
injections and nothing pulling on it. That survival is an artifact of a
dropped edge, not a physical finding.

## 4. Gaps — framed as questions for the logic's author

Each entry: what I tried to say → what the logic offered.

1. **No area / balancing-authority grouping.** My whole dataset is BA-level
   aggregation of plants; the logic has only Bus. A Bus here *is* a BA, so the
   plant → BA aggregation story (where my sheaf-consistency work lives) has no
   home. Is a hierarchy of buses (or a "Zone" object with a map from Bus) in
   scope for the logic?
2. **Numbers live only inside one analysis document.** Flows, capacities and
   injections are entered in the Kuramoto pane, not on the model. They don't
   export with the model and can't be reused by another analysis (the
   Visualization can't draw tie width from capacity, for instance). Would
   typed attributes on generators be a natural extension?
3. **Direction is real data and gets thrown away.** Every tie was oriented by
   2023 net flow (NYIS → PJM means something). The Kuramoto builder symmetrizes
   the coupling matrix ("assumed symmetric in the literature", `kuramoto.rs`).
   Recording direction in the model is free documentation, but no analysis
   consumes it.
4. **Links are silently ignored by the simulation.** Verified in
   `catlog-wasm/src/theories.rs`: the Kuramoto analysis registers only `Bus`
   and `Passive` as coupling types; `Branch` (= Link) is not added. But the
   UI **still shows a Capacity field for the Link** and accepts a value —
   which is then discarded. Controllable flows (DC ties, market-to-market
   seams) are exactly the policy-interesting objects. The in-source comment
   "Should we distinguish between lines and transformers?" is the neighbour of
   this question: should Links couple, and with what dynamics?
5. **No time.** EIA-930 is hourly; the model holds one static forcing scalar
   per bus. A year's worth of seasonal reversal on SOCO–TVA is unrepresentable.
6. **No proposed-vs-existing status.** Interconnection-queue semantics (the
   LBNL-reconciled side of my work) can't be stated — a planned tie and an
   energized one are the same Line.
7. **No plant / load entities.** eGRID generator footprints have nowhere to
   attach; "Input power" is the only place generation and load appear, already
   netted.
8. **Composition gives a Line, but nothing uses it.** Series composition of
   Lines is a Line (the logic's one honest categorical idea, and it matches
   physical series reduction). No analysis I found exploits it — e.g. to
   collapse a path into an effective tie. Is that the intended payoff?
9. **UI friction, recorded verbatim:**
   - Shift+Enter / Alt+B create a new cell but keyboard focus stays in the
     *previous* cell's name field, so typing the next name appends it to the
     old one ("ISNENBSOCPLEMISOSWPP" happened). Every cell needed a mouse click.
   - In a Line cell, Tab does not move from the domain field to the codomain
     field; it stays put. Clicking the "…" is the only way.
   - An invalid endpoint name renders in orange but the cell keeps focus, so a
     click on the codomain lands in the domain until the domain is fixed.
   - Kuramoto Damping defaults to 0. With 0 damping and second order the plot
     is unreadable on first open; nothing says "set damping".
   - A "Composition pattern" analysis exists (undirected wiring diagram) that
     isn't mentioned anywhere I looked.
   - Shortcut hints say "Alt B / Alt L" but the cell-type menu is what
     actually takes the click.

## 5. What this is and isn't

This is a real network, real 2023 volumes, run through a toy. The toy's verdict
on the seams matches the curvature ranking, with one hole where the logic
drops Links. It is not a stability study; the scaling runs are a sensitivity
sweep on a 13-node slice with most intra-slice ties missing.
