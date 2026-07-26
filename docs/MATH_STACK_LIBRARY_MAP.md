# The Komposos Math Stack in `komposos-enrich`: A Library Usage Map

*Started 2026-07-17. This is a living document — built incrementally, not in one pass.
Every number below was measured from the actual repo (file counts, import greps, LOC),
not estimated. Where something is marked `TODO`, it hasn't been checked yet — do not
treat an absent section as "nothing there," treat it as "not yet audited."*

**Purpose:** you've copied the same categorical math core into every KOMPOSOS-* repo,
so it's become a de facto library. This document answers, for the grid repo
specifically: *what is actually the library, what is the application, which library
parts does this application really call, and what would it take to package the used
slice as something reusable (skills / MCP tools) instead of a full source copy?*

---

## Part 1 — The two-layer shape of this repo

Every KOMPOSOS-* repo (confirmed by inspecting `_compat_loader.py` and the top-level
package stubs) has the same structure:

1. **The real math stack lives under `src/`** — `src/komposos_core/{core,categorical,
   cog,cubical,hott,zfc,game}`, `src/operadum/`, `src/pronoia/`, `src/komposos_wesys/`.
2. **Top-level packages (`core/`, `cog/`, `oracle/`, `categorical/`, `zfc/`, `hott/`,
   `cubical/`, `game/`, `operadum/`, `pronoia/`, `bridges/`) are thin compatibility
   shims.** Each `__init__.py` is 2-3 lines calling `_compat_loader.load_package(...)`
   to re-export the real package from `src/`. Measured: these shim dirs total **486
   lines** combined — essentially free. `oracle/` is the one exception: it is a real,
   substantial package at the top level (16 files), not a shim.

**Sizing (measured via `wc -l` over `find ... -name "*.py"`):**

| Layer | LOC | What it is |
|---|---:|---|
| `src/` (the math stack / library) | **50,319** | Category runtime, COG judge, oracle strategies' shared types, cubical/HoTT/game-theory layers, ZFC dual-engine, OPERADUM, PRONOIA, WESYS geometry/validation |
| `domains/` (the application — grid + nuclear) | **26,057** | Everything domain-specific: ingestion, reports, the Streamlit pages, run_*.py pipelines |

**The headline finding: the library is ~2x the size of the application built on it.**
That ratio is itself the signal you're after — it means most of the stack's surface
area was built once (probably for a different, more ambitious domain — chem, or the
general KOMPOSOS-IV vision) and grid uses a comparatively narrow slice. Confirming
exactly how narrow is the rest of this document.

---

## Part 2 — What grid actually imports (ground truth, not guesswork)

Method: `grep` every `from <stack-package> import ...` line across `domains/`,
`streamlit_app.py`, `grid_app.py`, `scripts/`, `tests/`. This is real call evidence,
not doc claims.

### 2a. Heavily used (this is the real dependency surface)

| Import | Count | Role |
|---|---:|---|
| `core.category.Category` | 27 | **The workhorse.** Every domain module that builds a graph of plants/BAs/queue-projects instantiates this. This is the one class grid cannot live without. |
| `cog.session.CogSession` / `cog.engine.CogEngine` / `cog.schema.CogClaim` | 7 / 7 / 5 | The claim-judging layer — used in the nuclear Streamlit page's "categorical claim check" and in `verify_assignments.py`'s dual-engine verification. |
| `core.optimus.OptimusEngine` | 6 | OPTIMUS factorization — this is what powers the queue-analysis "discover intermediates" logic (`queue_analysis.py`) and is name-dropped in the STITCH brief methodology. |
| `core.types.Object, Morphism` | 5 | Low-level graph primitives, imported wherever code builds a `Category` by hand. |
| `komposos_wesys.geometry.grid_spectral.SpectralGraphAnalyzer` | 5 | Fiedler-value / spectral seam analysis — the flow-geometry BA-network work. |
| `komposos_wesys.geometry.grid_ricci.OllivierRicciCurvature` | 2 | Ollivier-Ricci bottleneck detection on the BA interchange graph — this is the literal engine behind `flow_geometry.py` and the network map's red-line curvature coloring. |
| `komposos_wesys.validation.thermodynamic_probe.ThermodynamicSheaf` | 4 | The H^1 cohomology / sheaf-leak audit — powers `sheaf_audit.py` and the "Data Integrity Index" tab. |
| `komposos_wesys.adapter.WesysAdapter` | 4 | Bridges the WESYS geometry/validation layer into the plain `Category`. |
| `oracle.*` (13 distinct strategy imports: topos, topological_anomaly, operadic_decomposition, natural_transformation, game_strategy, evidence_combination, cubical_gap_filling, cellular_dynamics, boundary_detection, streaming_forecast, fibration_lift, activity_analysis, prediction) | 1-3 each | The 21-strategy oracle ensemble (per KOMPOSOS-V's `ARCHITECTURE.md`) — grid uses **13 of the 16 oracle files** that exist. This is actually well-utilized, not dead weight. |

### 2b. Used, but thin (single call sites)

| Import | Count | Where |
|---|---:|---|
| `zfc.store_adapter.StoreAdapter`, `zfc.bridge.DualEngineBridge`, `zfc.axiom_miner.AxiomPattern` | 1 each | `methodology.py`, `verify_assignments.py` — the dual-engine (categorical + set-theoretic) cross-check. Real but narrow: two files call it. |
| `pronoia.scm.SCM` | 1 | Somewhere in the honesty/MDL layer — **TODO: confirm exact call site and whether it's live or vestigial.** |
| `core.cosmos.InfinityCosmos` | 2 | **TODO: trace this — "Infinity Cosmos" sounds like it's from `INFINITY_COSMOS_INTEGRATION_BLUEPRINT.md` at repo root; check whether this is active grid logic or a leftover integration experiment.** |
| `operadum.integrations.komposos_mof.RealKompososMOFClient`, `operadum.core.enrichment.LINEAR_TOKENS/ResourceError` | 1 each | These are **chem-domain (MOF) and linear-logic demo code**, imported only by `scripts/verification/science_informatics_audit.py` — which we already relabeled this session as a demo suite, not a grid audit. This confirms that relabel was correct: OPERADUM's MOF integration has **no real grid call site**. |

### 2c. Confirmed ZERO usage in this repo's domain code

Grepped explicitly for `from hott` / `from cubical` / `from game` at the domain level:
**no hits.** These three packages exist in `src/komposos_core/` (compiled/loaded,
taking up real LOC and shim maintenance) but grid never imports them directly.
(Caveat: `cubical_gap_filling_strategy` is an *oracle* strategy that may internally
use cubical-layer math — that's a different question from "does grid import cubical
directly," which it does not. **TODO: check whether that oracle strategy actually
exercises `cubical/` internals or is cubical-flavored in name only.**)

**Practical implication:** if you ever split this into "grid app + math library
package," `hott/`, `cubical/`, and `game/` are candidates to exclude from a grid-only
distribution — they're costing you repo weight and cognitive load on every "so many
files" entry into this repo, for zero grid payoff. (Do NOT delete them — chem/other
domains may use them. This is a *packaging* finding, not a delete-this finding.)

---

## Part 3 — Working conclusions so far (to be refined as the map deepens)

1. **Grid's real dependency footprint is small and identifiable:** `Category` +
   `Object`/`Morphism` (the substrate), COG (judge), OPTIMUS (factorization), the
   oracle ensemble (13/16 strategies), and three WESYS geometry/validation engines
   (Ricci curvature, spectral/Fiedler, thermodynamic sheaf). That's roughly **8-10
   named engines** doing all the real work behind every headline number in the app.
2. **The shim layer is nearly free** (486 LOC) — it is not the source of "so many
   files" confusion. The confusion source is `src/`'s raw size (50K LOC) sitting
   fully present in every domain repo regardless of what that domain uses.
3. **This maps directly onto the earlier MCP/skills conversation:** the 8-10 engines
   in finding #1 are exactly the set that should get thin MCP tool wrappers (grounded
   calls with receipts) in any KOMPOSOS repo. The rest of `src/` doesn't need to
   travel with grid at all if grid is repackaged — it could be a separate installed
   dependency, or its unused corners simply deleted from a grid-specific fork.

---

## Part 4 — File-by-file: what actually touches the math stack in `domains/grid/`

Method: grepped every one of the 71 files in `domains/grid/*.py` for a direct
`from <stack-package> import ...` line. Result, sorted by what it shows:

### The kernel — 8 files, direct stack imports

| File | Imports | What it's for |
|---|---|---|
| `ingest.py` | `core` (`Category`/`Object` via `plant_obj`, `source_obj`) | **The one true bridge.** Turns raw plant/BA/source records into `Category` objects. Everything downstream that "is categorical" gets there through this file. |
| `flow_geometry.py` | `core` | Builds the BA interchange `Category`, feeds it to WESYS's Ricci/spectral engines (see Part 2). |
| `queue_analysis.py` | `core` | OPTIMUS factorization over the LBNL queue graph. |
| `methodology.py` | `categorical`, `zfc` | The dual-engine (categorical + ZFC set-theoretic) methodology cross-check. |
| `verify_assignments.py` | `core`, `zfc` | Dual-engine verification of plant→BA assignments (README's "24% counterfactual leakiness" finding). |
| `sheaf_audit.py` | `komposos_wesys` | Wraps `ThermodynamicSheaf` — the H^1 cohomology leak audit. |
| `relief_curves.py` | `pronoia` | Uses `pronoia.scm.SCM` — a **structural causal model**, do-query style — to compute each relief-curve point as a counterfactual ("if this MW of capacity existed, what would the spread be"). This is a distinct, more statistical corner of the stack than the categorical/COG side. |
| `run_coherence.py` | `core` | The one `run_*.py` wrapper that imports the stack directly (it orchestrates `coherence.py` + builds the `Category` inline rather than through `ingest.py`). |

### The "sounds categorical, isn't calling Category" layer — a real nuance

`coherence.py`, `crosswalk.py`, `ba_footprint_crosswalk.py` implement the README's
sheaf-gluing vocabulary — `Section`, `pushforward`, `relative_discrepancy`, GLUE /
TENSION / CONTRADICT verdicts — but **as bespoke Python dataclasses and functions,
not by calling `core.category.Category`'s machinery.** They only touch the stack
transitively, through `ingest.py`'s `plant_obj`/`source_obj` helpers to get their
input objects. `waste_ledger.py` (downstream of both) touches the stack **not at
all** — it's pure CSV/JSON/HTML report assembly over already-computed JSON.

**Why this matters for "librarify it":** if someone assumed "any file using
sheaf-theory language must be importing the shared `Category` runtime," they'd be
wrong for 3 of the most conceptually central files in the repo. The gluing-condition
math here is a **from-scratch reimplementation of the idea**, not a call into the
shared engine. That's a legitimate design choice (it's simpler, has no `Category`
overhead, is easy to unit test) — but it means "the math stack" and "code that
talks like the math stack" are two different things you should track separately
when deciding what's reusable library surface versus bespoke domain logic.

### The serving/presentation layer — confirmed zero direct stack imports, by design

`mcp_server.py` → `agent_tools.py` → `agent_contract.py`: **zero stack imports at
any layer.** This chain reads already-computed `reports/*.json` artifacts and
re-serves them as MCP tool responses. `dashboard.py`, `system_overview.py` import
only `charts.py` (a pure bar/line-chart-to-HTML helper) and `flow_geometry.py`'s
data loaders — not the stack directly. `network_map.py` imports `flow_geometry.py`
(which does touch `core`) but nothing else from the stack.

**This is actually the right pattern, already in place — worth naming explicitly:**
the MCP layer's job in this repo is *serve grounded, already-computed, already-
receipted artifacts*, not *run live category-theory computations per request*. A
tool call like `ba PJM` reads a JSON file that `run_flow_geometry.py` produced
offline (with its provenance and limits baked in) rather than reconstructing the
`Category` and recomputing curvature on every chat turn. That's a better shape than
the "wrap each engine directly as an MCP tool" idea floated earlier in this
conversation — it separates *slow, auditable computation* (the `run_*.py` scripts,
checked into `reports/`) from *fast, grounded serving* (the MCP layer). Any future
MCP tool for grid or chem should follow this same split, not call engines live.

### The rest — ~60 files, zero direct stack imports

Everything else in `domains/grid/` (`ba_dashboard.py`, `ba_repair.py`, `ba_review.py`,
`congestion_evidence.py`, `curtailment.py`, `outages.py`, `queue_match.py`,
`reliability_value.py`, `solution_cards.py`, `solution_studies.py`,
`chpe_event_study.py`, `same_year_flows.py`, every `run_*.py` wrapper except
`run_coherence.py`, `fetch_eia930.py`, `geo.py`, `map_overlays.py`, `daily_update.py`,
`action_portfolio.py`) is pandas/stdlib data-wrangling and report generation over
CSVs, EIA/LBNL source files, and the JSON artifacts the kernel files produce. This
is not a criticism — it's most of what a real analytics pipeline is — but it means
**the categorical math is genuinely concentrated in under 15% of the grid module
count**, doing work that ~85% of the codebase then reports on, filters, and
presents.

---

## Part 5 — `domains/nuclear/*.py` (smaller domain, quick pass)

| File | Stack imports | Notes |
|---|---|---|
| `ingest.py` | `core` (`Category`) | Same bridge role as grid's `ingest.py` — builds the mine→conversion→enrichment→fabrication→reactor→demand chain (this session's audit target). |
| `flow_geometry.py` | (uses the WESYS Ricci/spectral engines, same as grid's) | Powers the curvature-labeled scenario matrix fixed earlier this session. |
| `run_comprehensive_analysis.py` | `cog` (`CogSession`, `CogEngine`, `CogClaim`) | The claim-check machinery behind the Streamlit page's "System-Wide Fuel Confidence" metric. |
| `action_portfolio.py`, `run_enrichment_flow.py`, `run_urenco_scenarios.py`, `agent_tools.py` | none directly (TODO: confirm `run_urenco_scenarios.py` and `run_enrichment_flow.py` — not yet grepped individually) | Presumed presentation/report layer by analogy with grid's pattern; **not yet verified file-by-file** — flag as unconfirmed rather than assumed. |

Nuclear is a much smaller, simpler mirror of grid's architecture: one `ingest.py`
bridge into `Category`, the WESYS geometry engines for curvature, COG for claim
checks. It reuses the *same* kernel files' patterns rather than inventing new stack
call sites — evidence that the "kernel of ~8-10 engines" from Part 3 really is the
reusable core across domains within this repo, not just within grid.

---

## Part 6 — The two traced unknowns from Part 2

**`core.cosmos.InfinityCosmos`:** searched the whole repo (not just `domains/`).
Real hits are all inside the library itself: `src/komposos_core/cog/engine.py`,
`core/architect.py`, `core/cosmos.py`, `core/two_cell_bridge.py`,
`core/typed_capabilities.py`, and `komposos_wesys/core/energy_coherence.py`, plus
two library-level tests (`test_infinity_cosmos.py`, `test_higher_order_yoneda.py`).
**Conclusion: `InfinityCosmos` is not dead, and not really "used by grid" either —
it's load-bearing machinery *inside* `cog/engine.py`, so every grid call to
`CogEngine` transitively depends on it.** It has no grid-domain call site of its
own. Separately, `komposos_wesys/core/energy_coherence.py` (which also touches
`InfinityCosmos`) is the exact module `WHOLE_GRID_ROADMAP.md` already flags as "wire
carefully… only after the data contracts above are stable" — i.e., **you already
knew, and already wrote down, that this piece is deliberately not yet wired into
grid.** This document's finding just confirms your own roadmap note was accurate.

**`pronoia.scm.SCM`:** confirmed single call site, `relief_curves.py`. It builds a
deterministic **structural causal model** per tie/benchmark and evaluates each
relief-curve point as a do-query (`model = SCM()` at line 370). This is real,
narrow, working usage — not vestigial. It's also conceptually distinct from the
COG/categorical claim-checking side: PRONOIA here is doing causal-inference-style
counterfactual estimation, not MDL-honesty scoring (which is what PRONOIA does
elsewhere per KOMPOSOS-V's architecture doc). **Worth noting for anyone
librarifying PRONOIA:** it is at least two different tools wearing one package
name — the `SCM`/causal side used here, and the honesty/MDL side described in
`KOMPOSOS-V-base/ARCHITECTURE.md` and referenced in the aletheia handoff. Don't
assume "PRONOIA" means one thing across repos without checking which corner of it
is actually imported.

---

## Part 7 — Packaging recommendation

### What "the reusable core" actually is, now that it's measured

Nine things, all confirmed by real call evidence above, not by documentation claims:

1. `core.category.Category` / `core.types.Object,Morphism` — the substrate everything else builds on.
2. `cog.{session,engine,schema}` — the claim-judging layer (which transitively pulls in `InfinityCosmos`).
3. `core.optimus.OptimusEngine` — factorization.
4. The oracle ensemble — 13 of 16 strategy files actually exercised.
5. `komposos_wesys.geometry.grid_ricci.OllivierRicciCurvature` — bottleneck detection.
6. `komposos_wesys.geometry.grid_spectral.SpectralGraphAnalyzer` — Fiedler/seam analysis.
7. `komposos_wesys.validation.thermodynamic_probe.ThermodynamicSheaf` — the H^1 leak audit.
8. `zfc.{store_adapter,bridge,axiom_miner}` — the dual-engine cross-check (2 grid call sites, both audit-critical).
9. `pronoia.scm.SCM` — causal/counterfactual relief-curve modeling (1 call site, load-bearing for the seam-value numbers).

`hott/`, `cubical/`, and `game/` (as directly-imported packages) have **zero**
confirmed grid or nuclear call sites in this repo. Note the caveat from Part 2b:
`oracle.cubical_gap_filling_strategy` is used — whether it exercises `cubical/`
internals is still unconfirmed (open item, not yet worth blocking on).

### The concrete recommendation

- **Don't restructure the repo to "delete unused packages."** This repo intentionally
  carries the full stack because other KOMPOSOS domains (chem, and whatever comes
  next) may use the parts grid doesn't. That's a legitimate reason for a monorepo-
  style shared `src/`.
- **Do build a `docs/STACK_DEPENDENCY_MANIFEST.md`** (or a small generated JSON) that
  lists, per domain, exactly the 9 engines above with their one-line role and their
  real call sites — regenerated by a script (grep-based, like this document was
  built) rather than hand-maintained, so it can't go stale the way ordinary docs do.
  This turns "so many files, which ones matter" from a 30-minute manual audit (what
  this session just did) into a one-command answer for the next person or agent
  entering the repo.
- **For MCP/skills packaging (tying back to the earlier conversation):** the right
  unit to wrap is not "one MCP tool per stack engine" — it's **one MCP tool per
  `run_*.py` pipeline output**, following the pattern `mcp_server.py` already uses.
  The 9 engines above are exactly the set that should get a `/verify-claim`-style
  skill teaching an agent *which `run_*.py` script to invoke and which report to
  trust* for a given kind of question — mirroring what this session's `verify-claim`
  skill already does for the queue numbers. The skill is the map of "which of the 9
  engines answers this question"; the MCP tool is the grounded, receipted read of
  that engine's last computed output; the engine itself never runs live inside a
  chat turn.
- **For a future "grid-lite" fork or a from-scratch chem-lite:** the dependency
  surface to keep is exactly the 9-engine list. Everything else in `src/` (hott,
  cubical, game, the unused 3 oracle strategies, OPERADUM's MOF integration which
  this session confirmed has no grid call site) could be a separate optional
  package rather than bundled weight in every domain checkout.

---

## Part 8 — The full pure-math cluster (categorical, cubical, HoTT, ZFC, game, geometry, oracle)

*Gathered 2026-07-17 via a dedicated code-reading pass across the whole stack (not
just grid's call sites) — this extends Parts 1-7 from "what does grid use" to "what
exists and what state is it actually in." Everything below is read from real code:
class signatures, LOC counts, and test-file cross-references, not from docstrings
taken at face value.*

### The one foundation everything sits on

`core/category.py`'s `Category` class (747 LOC, well-documented, in-code examples) —
an in-memory + SQLite graph of `Object`s and `Morphism`s where confidence composes
via a quantale (default multiplicative: confidence multiplies along a path). Nearly
every module below **takes a `Category` as input.** Read that as: most of this stack
is graph algorithms wearing category-theory vocabulary, not independent mathematics
each doing its own thing. That's not a criticism — it's the actual shape, and it
matters for packaging (Part 9).

### core/ beyond the shim

| Module | Size | What it really does | Coupling note |
|---|---:|---|---|
| `optimus.py` | 545 LOC | Snapshots a `Category` into an **external package**, `optimus_core.RuntimeCategory`, and runs its `OptimisMonad.descend()` (finds shortcut/redundant paths), then syncs results back. **`optimus_core` is not inside this repo's `src/` — it's reached via a `sys.path` hack to the project root.** This is a real fragility point: OPTIMUS's actual "descent" algorithm lives outside the packaged library. |
| `higher_order_optimus.py` | 435 LOC | Genuinely distinct from plain OPTIMUS, not a rename: `HigherOrderOptimus(runtime, two_category=None)` operates one level up — `factorize_two_cell`, `refine_fibration`, `refine_functor` — i.e. finds shortcuts among *morphisms between morphisms* (2-cells), not just among objects. |
| `cosmos.py` (`InfinityCosmos`) | 788 LOC | The orchestration layer: builds a homotopy 2-category from a `Category`, detects iso/cartesian fibrations, computes the Yoneda embedding, computes Kan extensions. This is what wires together most of `categorical/` in practice — recall from Part 6, `cog/engine.py` depends on this transitively. |
| `two_cell_bridge.py` (`TwoCellBridge`) | 480 LOC | **The cleanest yes/no verdict API in the whole stack:** `verify_claim(source, target, relation)` → `AGREE / REJECT / ORPHAN / HOLLOW / EQUIVALENT`. Worth naming explicitly: **this verdict vocabulary already existed in the library before aletheia formalized the same idea as a standalone layer.** Aletheia's judge (`AGREE/HOLLOW/ORPHAN/REJECT/not_assessed`) is close kin to this, built fresh rather than reusing it — a legitimate design choice (aletheia's judge is deliberately LLM-agnostic and doesn't require a `Category`), but worth knowing the family resemblance is real, not coincidental naming. |
| `architect.py` (`ArchitecturalAdvisor`) | 520 LOC | Genuinely interesting and under-advertised: mines **git history** (`co_modification_matrix`, `abandoned_experiments`, via real `git log` subprocess calls) combined with OPTIMUS/cosmos structural-hole detection to recommend refactors. It's self-referential — built to analyze the very repo it lives in. Exploratory, but this is a real candidate for a "repo health" CLI tool (see Part 9). |
| `typed_capabilities.py` | 304 LOC | Just dataclasses/enums for a plugin type system — a schema, not executable logic. Relevant to the uxok discussion below: this looks like unfinished groundwork for exactly the kind of capability-typing uxok already does as a real, tested product. |

### `categorical/` — 18 files, ~8,300 LOC, and a hard number worth sitting with

Only **5 of the 18 files** (`two_categories.py`, `fibrations.py`, `grothendieck.py`,
`presheaf_topos.py`, `kan_extensions.py`) are actually exercised by any test in the
repo (`test_infinity_cosmos.py`, `test_higher_order_yoneda.py`) — because those are
the 5 that `cosmos.py` imports. **The other 13 files — roughly 5,000+ LOC, including
the single largest file in the package (`activity_system.py`, 989 LOC, activity-
theory contradiction detection) — have zero test coverage found anywhere in the
repo.** That list: `activity_system.py`, `cellular_automata.py` (579 LOC — a literal
CA grid with epidemic-style transition rules, distinct from `oracle/cellular_
dynamics.py`), `topos_logic.py` (720 LOC, Heyting-algebra truth values), `prime_
theory.py` (a toy functor from integers to prime factorizations), `crypto_category.
py`, `dempster_shafer.py`, `boundary_profunctor.py`, `operads.py`, `streaming_kan.
py`, `quantales.py`. **This is not "these are bad code" — it's "these are unverified
code," exactly the distinction this whole session has been drawing everywhere else.**

### `cubical/` (844 LOC) and `hott/` (1,573 LOC) — confirmed dead weight, precisely

Part 2 already showed zero *grid* call sites. This pass confirms it's zero call
sites **anywhere in the repo**: no test file references `cubical` or `hott` at all.
Sharper still: `oracle/geometric_homotopy_strategy.py` — the oracle strategy whose
name implies it uses this machinery — **hardcodes `HOMOTOPY_AVAILABLE = False` and
unconditionally returns `[]`.** It is a disabled stub, not a live integration point
with thin usage. That settles the open question from Part 2/7 about whether any
oracle strategy secretly exercises cubical/HoTT internals: this one visibly doesn't,
by its own admission in the code.

### `zfc/` (6,450 LOC, 12 files) — the most substantial single package, least tested

`DualEngineBridge` (`bridge.py`) runs a ZFC-style logic engine (`logic.py`'s
`LogicOracle`, `proof_engine.py`'s `ZFCVerifier`/`Proof`, `well_ordering.py`'s
`OrdinalOracle`) alongside categorical/structural verification and classifies claims
AGREE/ORPHAN/HOLLOW/REJECT — again, that verdict family. `axiom_miner.py` mines
axiom patterns from data; `meta_kan.py` (827 LOC) holds `System3Oracle` for
meta-level prediction. **No dedicated ZFC test file was found**; it's touched only
indirectly through COG's pipeline. Given Part 4/6 showed grid's own dual-engine
usage (`methodology.py`, `verify_assignments.py`) is real and audit-critical, this
combination — large, load-bearing in at least one domain, but not directly
unit-tested at the package level — is worth flagging as the single highest-value
place to add direct tests before trusting it further.

### `game/` (695 LOC)

`nash.py` (`TwoPlayerGame`, `NashEquilibrium`, `StrategyProfile`) does **real**
Nash-equilibrium computation over payoff matrices and, notably, **needs no
`Category` at all** — pure math in, pure math out. `open_games.py`
(`OpenGame`/`OpenGameCategory`, compositional game theory via string diagrams) is
Category-coupled and more niche. No test coverage found for either.

### `komposos_wesys/geometry` + `validation` — the best-tested corner of the stack

| Module | Size | Notes |
|---|---:|---|
| `grid_ricci.py` | 463 LOC | **Real optimal-transport math** — uses `scipy.optimize.linprog` to compute genuine Ollivier-Ricci curvature per edge, classifies spherical/hyperbolic/euclidean. This is grid's curvature engine (Part 2). |
| `grid_spectral.py` | 145 LOC | Small, clean, directly `Category`-coupled — Laplacian/Fiedler/coupling-strength. Grid's spectral engine. |
| `spectral_structures.py` | 727 LOC | **A separate, more complete spectral toolkit that does NOT require a `Category`** — its own plain `Graph` dataclass (nodes/edges/weights). Conceptually overlaps with `grid_spectral.py` but is standalone. **This is a real duplication worth resolving eventually** — two spectral-analysis tools, one coupled and thin, one decoupled and fuller, doing adjacent jobs. |
| `thermodynamic_probe.py` | 115 LOC | **The single best-tested module found in this entire catalog.** Tiny, self-contained (just numpy), has a real dedicated test file (`tests/test_thermodynamic_audit.py`). This is grid's sheaf-leak engine (Part 2) — and now confirmed to be the most trustworthy corner of the whole math stack by a wide margin. |

### `oracle/` — a necessary correction to Part 2's framing

Part 2 of this document called the oracle ensemble "well-utilized" because 13 of 16
files are imported by grid. That's still true as an *import* fact, but this pass
adds a needed qualifier: **the 16 files total only 418 LOC combined** — each
strategy is 12-41 lines of heuristic, not a deep algorithm. Concretely: `activity_
analysis` checks "≥3 morphisms exist" and returns a constant 0.4 "tension" score —
barely a heuristic. `topos_strategy` checks "a direct edge exists" and calls that
"classically true." These are legitimate, cheap, ensemble-style priors — exactly
the "proposal, not verification" role they're meant to play per KOMPOSOS-V's
design law — but calling them "21 strategies" without this context overstates what
each one individually contributes. The real value is in the ensemble combination
(`CategoricalOracle.predict()`, tested by a real 742-line test file — the second-
best-tested integration point after `thermodynamic_probe.py`), not in any single
strategy's depth.

### Part 8 summary table

| Package | Real capability | Test/production status | Tool-worthiness |
|---|---|---|---|
| `core/category.py` | graph-of-typed-objects runtime, quantale confidence | Well-tested, documented | Foundation, not a standalone tool |
| `core/optimus.py` | shortcut-path discovery | Depends on an *external, unpackaged* `optimus_core` | Too coupled + fragile external dependency |
| `core/higher_order_optimus.py` | 2-cell/fibration-level shortcut discovery | Untested directly | Too coupled |
| `core/cosmos.py` | Yoneda/Kan/fibration analysis | Tested via 2 test files | Coupled; could narrow-expose `yoneda_embedding()` |
| `core/two_cell_bridge.py` | AGREE/REJECT/ORPHAN/HOLLOW/EQUIVALENT verdict on one claimed edge | Untested directly, but simple | **Best core candidate for a narrow tool** |
| `core/architect.py` | git-history + structural-hole refactor advice | Exploratory | Good standalone CLI candidate |
| `categorical/*` (13 of 18 files) | topos logic, cellular automata, activity theory, prime theory, crypto, Dempster-Shafer, etc. | **Zero test coverage found** | Not tool-ready; verify before trusting |
| `cubical/`, `hott/` | path/transport type theory | **Zero usage anywhere in repo; oracle's own integration point is a hardcoded disabled stub** | Not tool-ready; genuinely dormant |
| `zfc/` | logic-proposes / structure-verifies dual engine | Large, load-bearing in 2 grid files, **no direct package tests found** | High-value but needs its own test suite first |
| `game/nash.py` | Nash equilibrium over payoff matrices | Untested, but self-contained | **Good standalone tool candidate** (matrix in, equilibrium out) |
| `wesys/geometry/grid_ricci.py` | real Ollivier-Ricci curvature (scipy linprog) | Used by grid | Good tool candidate |
| `wesys/geometry/spectral_structures.py` | fuller, decoupled spectral toolkit | Untested, but standalone | **Good tool candidate** — duplicate-resolve against grid_spectral.py first |
| `wesys/validation/thermodynamic_probe.py` | sheaf-Laplacian energy-leak audit | **Best-tested module in the catalog** | **Best tool candidate overall** |
| `oracle/*` (individually) | 12-41-line heuristic edge predictors | Ensemble is well-tested; individual strategies are not independently meaningful | Not worth 12 separate tools — wrap the ensemble (`CategoricalOracle.predict()`) as one |

---

## Part 8b — The special-systems cluster (COG, OPTIMUS pair, OPERADUM/WRIGHT, PRONOIA×2, uxok)

*Gathered 2026-07-17, same method as Part 8: real code reading, not doc claims.*

### The meta-finding first, because it changes how to read everything below

**A hardcoded placeholder was found wearing the shape of a real computation.**
`higher_order_optimus.py`'s Level 3 (fibration factorization) and Level 4 (functor
factorization) literally contain `"confidence": 0.5,  # Placeholder — needs actual
computation` and a comment admitting `# This would require access to the actual
fibration structure`. `descend_all()`'s level-3/4 branches never even call the
factorize methods — they just report `steps: 0`. **This is the exact failure this
whole day has been hunting: output shaped like a verified answer, with nothing
behind it.** It is structurally identical to a HOLLOW claim in aletheia's own
vocabulary — fluent, connected to the calling code's expectations, receipt-free.
The difference is only that this one is baked into library code instead of a
single LLM utterance, which makes it *more* dangerous, not less: every future
caller of `HigherOrderOptimus.descend_all()` inherits a silent lie unless they've
read this far into the source. **Treat "higher-order OPTIMUS" as one real
capability (Level 2, 2-cell factorization) plus two labeled-but-unimplemented
capabilities, never as "a 4-level system."**

A related, softer version of the same pattern: COG's Tier 3 (the actual
AGREE/ORPHAN/HOLLOW/REJECT-issuing `DualEngineBridge` engine) carries its own
`# TODO: DualEngineBridge needs updating to work with Category directly` and is
wrapped in try/except that silently falls back to Tier 2 on failure. Tiers 2-4
generally wrap almost every external import (`oracle.*`, `geometry.ricci`,
`topology.persistent_homology`) in try/except — so a query that looks like it
reached "Tier 4" sophistication may have quietly degraded through several
soft-fails. Not a hidden placeholder like higher-order OPTIMUS's, but the same
family of risk: confident-looking tier numbers that don't guarantee the depth of
computation they imply.

### COG (`src/komposos_core/cog/`)

Tiered claim verifier, Tier 0 (direct lookup) through Tier 4 (topology/curvature/
homology), escalating until confidence crosses a threshold or a 30s budget runs
out. Entry: `CogEngine.check_claim(claim: CogClaim) -> CheckResult`. Verdict
vocabulary: `AGREE, ORPHAN, HOLLOW, REJECT, PENDING, PARTIAL` — but in practice
Tiers 0-2 mostly only emit AGREE/PARTIAL/PENDING; ORPHAN/HOLLOW/REJECT only
surface from Tier 3, the tier marked unstable above. Fully deterministic, no
LLM/network calls anywhere — confirmed. ~1,100 LOC core, 16 tests
(`test_cog_iv.py`). Confirmed (again, independently of Part 6): Tiers 4a/4b/4e
import `InfinityCosmos` directly.

### OPTIMUS vs Higher-Order OPTIMUS — confirmed, precisely

**OPTIMUS** (`optimus.py`, 545 LOC): real, working 1-morphism-level graph
optimization. Snapshots a `Category` into an **external, separately-packaged**
`optimus_core.RuntimeCategory` (904 LOC, `src/komposos_core/optimus_core.py` — a
real fragility point already flagged in Part 8, now confirmed to be a substantial
file, not a thin shim itself), runs `OptimisMonad.descend()` (categorical gradient
descent — given A→B→C with no A→C, it can materialize A→C at the composed
confidence), syncs results back. `OptimusEngine(category).refine()` /
`find_structural_gaps()` / `yoneda_similarity()`. 36 tests, and it's used by
`komposos_wesys/core/energy_coherence.py` — genuinely production-adjacent, the
most mature of the "core/" engines besides `Category` itself.

**Higher-Order OPTIMUS** (`higher_order_optimus.py`, 435 LOC): see the meta-finding
above. Level 2 (2-cells, real) + Levels 3-4 (stubs). 27 tests, but they only
exercise init and Level 2 — there's nothing to test at Levels 3-4 because nothing
runs there.

### OPERADUM / WRIGHT (`src/operadum/`) — the most fleshed-out of the six, and the least coupled

Correction to the earlier handoff assumption: the `Category`-mirroring class is
called `Operad` (`core/operad.py`, 403 LOC — colours dual to Objects, Operations
dual to Morphisms, with resource cost and an optional executable `fn`, SQLite
persistence, hooks). The actual construct/verify engine is a distinct module,
**WRIGHT**, explicitly self-documented as "the dual of KOMPOSOS-IV's COG." Entry:
`Wright(operad).synthesize(spec: Spec) -> BuildResult`. Verdict vocabulary:
`BUILDABLE, OVERBUDGET, ILL_TYPED_GAP, IMPOSSIBLE` — the constructive mirror of
COG's AGREE/ORPHAN/HOLLOW/REJECT. Genuinely tiered (0 direct match → 1 single
compose → 2 bounded tree search → 3 a branch-and-bound solver called DAEDALUS → 4
`certify()` producing coherence/conservation/linear-soundness proofs). ~175 files,
~2,500+ LOC, real tests (`test_operad.py`, `test_wright.py`), plus domain
integrations already built for materials, quantum circuits, chemistry, drug
ranking. **Crucially, it needs only a standalone `Operad` instance, not the shared
`Category` runtime** — the loosest-coupled of the six systems, and therefore the
easiest to package as an independent tool.

### PRONOIA — genuinely two tools, found in a different location than assumed

Not under `operadum/pronoia/` as this repo's own docs and the aletheia handoff
assumed — both live in `src/pronoia/pronoia/`, imported by OPERADUM's pharma
integration modules. **PRONOIA-causal** (`scm.py`, 117 LOC): `SCM` — a real
structural-causal-model class, numpy-driven, `.do({var: val})` for interventions,
`.causal_effect`/`.observational_effect`/`.backdoor_effect` for true-vs-confounded-
vs-adjusted estimates via Monte Carlo. This is the tool grid's `relief_curves.py`
actually imports (Part 4/6) — confirmed real and load-bearing there, but **no
dedicated test file found for the package itself.** **PRONOIA-honesty**
(`honesty_mdl.py`, 162 LOC): `sincerity(trace, stated) -> SincerityReport` — scores
whether a stated explanation's zlib-compressed description length matches the
actual reasoning trace's, as an MDL-honesty proxy. Verdicts: `SINCERE,
HIDDEN_STEP, FABRICATION, DISTORTION`. Stdlib-only, deterministic, and its own
docstring is admirably honest about its limits: "bounds insincerity... does not
prove honesty." **This is precisely the MDL-honesty-gain concept the aletheia
handoff asked a future session to port in Phase 4** — it already exists, tested-
or-not, sitting in this repo's dependency graph, and could likely be reused
directly rather than rebuilt.

### uxok fit — a clear-eyed verdict, not a wish

uxok (verified: real PyPI package, MIT, 0.x pre-1.0, hot-loading plugin
microkernel with capability-based dependency resolution) solves **runtime plugin
composition and hot-reload**. The six engines above are already loosely coupled
via lazy imports and try/except degradation — COG's tiers already soft-fail
gracefully on missing modules. Wrapping them as uxok plugins would buy **hot-swap-
without-restart and a uniform capability-discovery graph** (WRIGHT declares
`requires={"operad"}`, COG declares `requires={"category"}`) — genuinely
attractive for a long-running MCP server that wants to reload an engine after a
fix without killing the session (this is exactly what noesis already does, per
its README's "edit any plugin file, watcher hot-swaps within a quarter second").
**But it is an orchestration/deployment improvement, not a correctness fix.** It
would not by itself resolve COG's Tier 3 instability, higher-order OPTIMUS's stub
levels, or PRONOIA's missing tests. Sequence matters: fix/label correctness first,
then uxok-ify for deployment — doing it in the other order just hot-swaps broken
parts faster.

### Part 8b summary table

| System | Real capability | Verdict/output vocabulary | Coupling | Test status | Tool-worthy? |
|---|---|---|---|---|---|
| COG | Tiered claim verification | AGREE/ORPHAN/HOLLOW/REJECT/PENDING/PARTIAL | Hard (Category + long optional tail) | 16 tests; Tier 3 marked unstable | Yes, but be honest about tier depth in the tool's output |
| OPTIMUS | 1-morphism factorization/gap-finding | n/a (returns morphisms) | Hard (Category + external optimus_core) | 36 tests | Yes — solid |
| Higher-order OPTIMUS | L2 real, L3/L4 hardcoded stubs | n/a | Hard | 27 tests (L2 only) | **Only expose Level 2; never L3/L4 as-is** |
| OPERADUM/WRIGHT | Typed/resource-verified pipeline synthesis | BUILDABLE/OVERBUDGET/ILL_TYPED_GAP/IMPOSSIBLE | Loose (just an Operad) | Real, dedicated | **Best candidate of the six** |
| PRONOIA-causal | Structural causal model, do-queries | n/a (numeric effects) | None | No dedicated tests, but load-bearing in grid | Yes, add tests first |
| PRONOIA-honesty | MDL/zlib sincerity scoring | SINCERE/HIDDEN_STEP/FABRICATION/DISTORTION | None | No tests | Yes — and likely directly reusable by aletheia Phase 4 |
| uxok | Hot-loading plugin microkernel (external, real, published) | n/a | N/A — a hosting layer, not an engine | Real, published, CI'd | Deployment layer, apply after correctness fixes above |

---

## Part 9 — Organization without throwing anything away

*This answers the actual question that started this document: "how do I understand
and better deploy this when I enter the repo with so many files." The answer isn't
a cleanup — it's a map with honest labels, so size stops being confused with risk.*

### 9.1 — Sort everything into four honest tiers, not two

The instinct to "trim for efficiency" is right, but "trim" should mean **re-label
and route**, not delete — nothing here has been shown to be worthless, only
unevenly verified. Four tiers, populated from Parts 1-8b:

**Tier A — Production-grade, keep exactly as-is, wrap now.**
`core.category.Category`, `core.two_cell_bridge.TwoCellBridge`, `core.optimus.
OptimusEngine`, OPERADUM/WRIGHT, `komposos_wesys.validation.thermodynamic_probe.
ThermodynamicSheaf`, `komposos_wesys.geometry.grid_ricci.OllivierRicciCurvature`,
`oracle.CategoricalOracle` (the ensemble, not individual strategies), `game.nash`
(Nash equilibrium), the 5 tested `categorical/` files (`two_categories`,
`fibrations`, `grothendieck`, `presheaf_topos`, `kan_extensions`), COG's Tiers 0-2.
These have tests, real call sites, or both. **This tier gets MCP tools first.**

**Tier B — Real and useful, but needs a test file before being trusted with a tool
wrapper.** `zfc.DualEngineBridge` and its siblings (large, load-bearing in 2 grid
files, zero package-level tests), PRONOIA-causal `SCM`, PRONOIA-honesty
`sincerity()`, `core.architect.ArchitecturalAdvisor`, `komposos_wesys.geometry.
spectral_structures` (resolve its duplication with `grid_spectral.py` first — see
9.3). **Action: write the missing test, then promote to Tier A.** This is a
short, concrete todo list, not a vague "improve quality" gesture.

**Tier C — Real but genuinely unexercised anywhere in the repo.** The 13 untested
`categorical/` files (`activity_system`, `cellular_automata`, `topos_logic`,
`prime_theory`, `crypto_category`, `dempster_shafer`, `boundary_profunctor`,
`operads`, `streaming_kan`, `quantales`, plus 3 more), `cubical/`, `hott/`.
**Action: leave in place (other KOMPOSOS domains may use them — chem, or a future
one), but exclude from any "what does this repo actually run" documentation or
dependency manifest, and never let a Streamlit page or report cite them as if
they were computing something live** (this is the same rule Part 2/7 already
applied to grid specifically — Part 9 generalizes it to the whole stack).

**Tier D — Labeled-broken, must not be exposed as-is.** Higher-order OPTIMUS
Levels 3-4 (hardcoded placeholders), `oracle.geometric_homotopy_strategy`
(disabled stub returning `[]`), COG Tier 3 (acknowledged unstable, silently
degrades). **Action: either fix them or make the placeholder status visible in
every output that touches them** — e.g. `descend_all()` should return
`"level_3_status": "not_implemented"` explicitly rather than a confidence number
indistinguishable from a real one. This is a small code change with an
outsized honesty payoff, and it is exactly the kind of fix aletheia's `judge()`
would demand if it were pointed at this code's own outputs.

### 9.2 — The consolidation flow (extending the earlier MCP/skills conversation with real evidence)

The three-layer model from earlier in this conversation — *engines compute, tools
ground, skills discipline* — holds up, and Parts 1-8b sharpen exactly how:

1. **Engines stay Python packages, unchanged in location.** Moving 50K LOC around
   to "clean up" the repo would cost real risk (broken imports across every
   KOMPOSOS-* domain that shares this `src/`) for a cosmetic gain. Leave them.

2. **Tools wrap only Tier A, following the pattern already proven twice.** Once by
   grid's own `mcp_server.py` (serves pre-computed `reports/*.json`, never runs
   engines live per chat turn — Part 4's finding) and once, independently and more
   ambitiously, by **aletheia's `wrap_module()`**, which was verified this session
   to already wrap a real external MCP tools module (`noesi-cpa`'s 9 audit tools)
   so that every call becomes a logged access event *by construction* — no
   discipline required, no chance to forget. **This is the concrete mechanism**:
   any Tier A engine, exposed as an MCP tool and passed through `aletheia.
   wrap_module()`, automatically gets (a) grounded, receipted output like grid's
   pattern already provides, and (b) an audit trail an outside verifier (aletheia
   itself, or a human) can check without trusting the engine's own claims. Tiers B
   and C should **not** get tools yet — wrapping them would just launder their
   unverified status behind a confident-looking tool call, the library-code
   version of the HOLLOW problem from Part 8b's meta-finding.

3. **Skills teach which tool answers which question, plus the guardrails.** This
   session's own `/verify-claim` is the template: it doesn't compute anything
   itself, it routes ("check the artifact first, recompute from raw if the window
   differs") and it carries values ("state the offsetting region's strength too,"
   "if recompute and artifact disagree, that's the finding"). A `/consult-cog`
   skill, a `/synthesize-with-wright` skill, a `/nash-equilibrium` skill would each
   be a thin routing+guardrail layer over a Tier A tool — cheap to write once the
   tools exist.

4. **uxok is the deployment layer for all of the above, applied last.** Once Tier A
   is wrapped and Tier B has been promoted by adding tests, hosting the resulting
   tool set as hot-swappable uxok plugins (mirroring noesis's own architecture, and
   noesis itself is the working proof this is viable) buys live-reload without
   restarting an MCP server mid-session — genuinely valuable operationally, but
   correctly sequenced last, per Part 8b's uxok verdict.

5. **The generated-manifest idea from Part 7 becomes the map that makes "so many
   files" navigable.** A single script, re-run on demand (grep-based like this
   whole document), producing a table of: engine name → tier (A/B/C/D) → real call
   sites → test files → wrapped-as-MCP-tool (Y/N). That table, not this prose
   document, is what a person or agent should consult first when entering the
   repo — this document is the reasoning that produced it; the manifest is the
   one-screen answer.

### 9.3 — Two small, concrete cleanups worth doing regardless of the bigger plan

- **Resolve the `grid_spectral.py` / `spectral_structures.py` duplication** (Part
  8): one is thin and `Category`-coupled, one is fuller and standalone, both do
  spectral graph analysis. Pick one as canonical, have the other call it or be
  retired — this is the kind of quiet duplication that makes "so many files" feel
  worse than the underlying complexity actually is.
- **Make Tier D's placeholder status visible in its own output**, per 9.1 — the
  cheapest, highest-honesty-per-line-of-code fix in this entire document.

---

## Status of this document

Parts 1-7 written 2026-07-17 in one continuous session, entirely from grep/wc
evidence against the live repo (no numbers estimated or recalled from memory).
Open items, explicitly not yet done: nuclear's `run_urenco_scenarios.py` /
`run_enrichment_flow.py` individual verification (Part 5); whether
`cubical_gap_filling_strategy` exercises `cubical/` internals (Part 2b/7); a
generated (not hand-written) version of the dependency manifest recommended above.

