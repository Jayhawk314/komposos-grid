# SPDX-License-Identifier: Apache-2.0 OR LicenseRef-KOMPOSOS-IV-Commercial
# Copyright (c) 2024-2026 James Ray Hawkins
"""
AI-Energy Matching Engine (KOMPOSOS-WESyS)

Reframes WESyS around the real AI energy dilemma of 2026: the bottleneck is not
generation, it is *interconnection and allocation*. ~2,060 GW sits in U.S.
interconnection queues (LBNL "Queued Up", end of 2025) while AI data-center load
waits 3-7 years to connect — and existing "stranded" generation runs at partial
utilization the whole time.

This is fundamentally a matching + incentive + contract problem, which is exactly
what KOMPOSOS is for:

    Objects   = facilities (stranded generators, AI data-center loads)
    Morphisms = *feasible* power couplings, confidence = match quality
    Composition asks: does this generator + this load + this curtailment rule
                      compose into a stable agreement?

The engine:
  1. Loads facilities from data/ai_energy/facilities.json (calibrated to real
     2026 queue figures and announced co-location deals).
  2. Builds the bipartite coupling Category and scores every feasible match,
     with a reliability gate: a firm 24/7 load cannot co-locate on variable-only
     stranded capacity.
  3. Uses spectral analysis to show how many loads are stranded on their own
     island (no feasible match) by default.
  4. Greedily allocates stranded capacity to flexible load, best matches first.
  5. For each match, sketches the actor / incentive / contract alignment that
     would actually unlock it.

It does NOT generate power or shorten a literal queue. It is a decision layer
that finds feasible matches and the agreement that makes them rational. Every
value figure is an explicit hypothesis until a real match is struck and measured.

Run:
    python scripts/ai_energy_match.py
    python scripts/ai_energy_match.py --data data/ai_energy/facilities.json
    python scripts/ai_energy_match.py --output reports/ai_energy_matching.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "src"))
sys.path.append(str(ROOT))

from komposos_wesys.geometry.grid_spectral import SpectralGraphAnalyzer  # noqa: E402
from core.category import Category  # noqa: E402


DEFAULT_DATA = ROOT / "data" / "ai_energy" / "facilities.json"
DEFAULT_OUTPUT = "reports/ai_energy_matching.md"
MATCH_THRESHOLD = 0.45  # below this, a coupling is not worth proposing
FIRM_KINDS = {"gas", "nuclear", "coal"}          # can serve a 24/7 firm load
VARIABLE_KINDS = {"solar+storage", "wind", "hydro"}  # weather/seasonal, needs flexible load
FIRM_LOAD_FLEX = 0.20  # below this interruptible share, a load is treated as firm 24/7


# --------------------------------------------------------------------------- #
# Facilities
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Generator:
    name: str
    region: str
    nameplate_mw: float
    utilization: float          # fraction of nameplate actually used today
    kind: str                   # coal, gas, nuclear, solar+storage, wind, hydro
    interconnected: bool        # already has an interconnection agreement

    @property
    def available_mw(self) -> float:
        return round(self.nameplate_mw * (1.0 - self.utilization), 1)

    @property
    def is_firm(self) -> bool:
        return self.kind in FIRM_KINDS


@dataclass(frozen=True)
class Load:
    name: str
    region: str
    needed_mw: float
    flexibility: float          # 0..1 share of load that is interruptible
    queue_years: float          # years already waiting / expected to wait

    @property
    def is_firm(self) -> bool:
        return self.flexibility < FIRM_LOAD_FLEX


@dataclass(frozen=True)
class Facilities:
    generators: tuple[Generator, ...]
    loads: tuple[Load, ...]
    meta: dict


def load_facilities(path: str | os.PathLike) -> Facilities:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    generators = tuple(
        Generator(
            name=g["name"], region=g["region"], nameplate_mw=float(g["nameplate_mw"]),
            utilization=float(g["utilization"]), kind=g["kind"],
            interconnected=bool(g["interconnected"]),
        )
        for g in data["generators"]
    )
    loads = tuple(
        Load(
            name=ld["name"], region=ld["region"], needed_mw=float(ld["needed_mw"]),
            flexibility=float(ld["flexibility"]), queue_years=float(ld["queue_years"]),
        )
        for ld in data["loads"]
    )
    return Facilities(generators, loads, data.get("meta", {}))


# --------------------------------------------------------------------------- #
# Matching: morphism confidence = how well a (generator -> load) coupling holds
# --------------------------------------------------------------------------- #
def capacity_fit(gen: Generator, load: Load) -> float:
    """1.0 when available capacity comfortably covers need; falls off if it
    can't cover the firm (non-flexible) portion, and mildly if grossly oversized."""
    firm = load.needed_mw * (1.0 - load.flexibility)
    if gen.available_mw <= 0:
        return 0.0
    if gen.available_mw < firm:
        return max(0.0, gen.available_mw / firm) * 0.6
    coverage = min(1.0, gen.available_mw / max(load.needed_mw, 1e-6))
    oversize_penalty = 0.15 if gen.available_mw > 3 * load.needed_mw else 0.0
    return max(0.0, coverage - oversize_penalty)


def flexibility_alignment(gen: Generator, load: Load) -> float:
    """Variable/seasonal generation pairs well with interruptible load; firm
    generation pairs well with firm load."""
    if gen.kind in VARIABLE_KINDS:
        return 0.5 + 0.5 * load.flexibility
    return 0.7 + 0.3 * (1.0 - load.flexibility)


def speed_bonus(gen: Generator) -> float:
    """Already-interconnected stranded capacity lets the load skip the queue."""
    return 1.0 if gen.interconnected else 0.55


def match_score(gen: Generator, load: Load) -> float:
    if gen.region != load.region:
        return 0.0  # cross-region coupling needs transmission we don't model here
    # Reliability gate: a firm 24/7 load cannot run on variable-only capacity
    # without storage/firming or grid support — that is not a co-location case.
    if load.is_firm and not gen.is_firm:
        return 0.0
    cap = capacity_fit(gen, load)
    flex = flexibility_alignment(gen, load)
    spd = speed_bonus(gen)
    return round((cap ** 0.5) * (0.5 + 0.5 * flex) * (0.6 + 0.4 * spd), 4)


# --------------------------------------------------------------------------- #
# Alignment sketch (AI-energy actors) — the part that makes a match rational
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Alignment:
    actors: tuple[str, ...]
    activity: str
    game: str
    contract: str
    constraints: tuple[str, ...]
    measurement: tuple[str, ...]
    tier: str


def alignment_for(gen: Generator, load: Load, mw_served: float) -> Alignment:
    actors = (
        "AI operator / hyperscaler: needs power in months not years; will trade flexibility for speed; "
        "constraint: uptime SLA, capex, board timeline",
        f"stranded-generator owner ({gen.kind}): holds an underused interconnection and asset; wants revenue; "
        "constraint: existing PPA terms, ramp limits, fuel/weather availability",
        "utility / ISO-RTO: owns the interconnection queue and reliability; "
        "constraint: queue rules, ratepayer protection, deliverability",
        "regulator / PUC: protects ratepayers and equity; "
        "constraint: cost-allocation rules, who pays for upgrades",
        "local community / ratepayers: bears rate and reliability effects; "
        "constraint: limited visibility and negotiating power",
    )
    activity = (
        "the actor who can energize the load fast (the stranded generator) is not the actor who "
        "captures the AI revenue, and the utility that controls the queue captures neither — so the "
        "match that is obviously good for the system is nobody's job by default."
    )
    if mw_served >= 400:
        game = (
            "high shared value, classic coordination failure: the generator, the AI operator, and grid "
            "reliability all gain, but first-come-first-served queue rules and split cost-allocation mean "
            "no single actor will assemble the deal. Queue-stuffing by speculative projects makes it worse."
        )
        tier = "high-priority prototype"
    elif mw_served >= 200:
        game = (
            "moderate shared value, a bargaining problem: the deal needs a flexibility commitment and a "
            "clear split of who funds any deliverability upgrade before either side moves."
        )
        tier = "medium-priority prototype"
    else:
        game = (
            "localized value, a transaction-cost problem: keep the agreement simple or bundle it with a "
            "larger flexible-load tariff so the paperwork is worth it."
        )
        tier = "screening prototype"

    if gen.interconnected:
        contract = (
            "co-locate behind the existing interconnection: a curtailable-load service agreement where the "
            "AI operator firms up to the generator's reliable output and curtails the flexible portion on the "
            "operator's signal, in exchange for energizing on the generator's existing queue position. "
            "Share the queue-skip value via a capacity payment to the generator."
        )
    else:
        contract = (
            "behind-the-meter bridge: AI operator self-supplies from the new on-site generation to operate now, "
            "while staying in the interconnection queue and selling surplus back under a hybrid tariff once the "
            "grid catches up."
        )
    constraints = (
        "firm only the non-flexible MW; price the interruptible MW separately",
        "no net reliability reduction for existing ratepayers",
        "meter delivered MWh and curtailment events before any value claim",
        "cap ratepayer-funded upgrades; allocate deliverability cost to the beneficiary",
        "respect the generator's existing PPA and ramp limits",
    )
    measurement = (
        "delivered MWh and time-to-power (months saved vs. queue baseline)",
        "curtailment hours actually called and honored",
        "generator utilization before/after",
        "deliverability headroom on the shared interconnection",
    )
    return Alignment(actors, activity, game, contract, constraints, measurement, tier)


# --------------------------------------------------------------------------- #
# Engine
# --------------------------------------------------------------------------- #
@dataclass
class Match:
    gen: Generator
    load: Load
    score: float
    mw_served: float
    alignment: Alignment


@dataclass
class Result:
    facilities: Facilities
    category: Category
    fiedler: float
    components: int
    stranded_loads: list[Load]
    matches: list[Match]
    feasible_edges: int


def build_category(fac: Facilities) -> Category:
    cat = Category(db_path=":memory:")
    for g in fac.generators:
        cat.add(g.name, type_name="generator",
                metadata={"region": g.region, "available_mw": g.available_mw, "kind": g.kind})
    for ld in fac.loads:
        cat.add(ld.name, type_name="load",
                metadata={"region": ld.region, "needed_mw": ld.needed_mw, "flex": ld.flexibility})
    for g in fac.generators:
        for ld in fac.loads:
            s = match_score(g, ld)
            if s >= MATCH_THRESHOLD:
                cat.connect(g.name, ld.name, name=f"supply::{g.name}->{ld.name}",
                            confidence=s, relation="feasible_coupling")
    return cat


def spectral(cat: Category) -> tuple[float, int]:
    analyzer = SpectralGraphAnalyzer(cat)
    analyzer.build_laplacian()
    vals = np.sort(np.linalg.eigvalsh(analyzer.laplacian))
    fiedler = float(vals[1]) if len(vals) > 1 else 0.0
    if abs(fiedler) < 1e-9:
        fiedler = 0.0  # disconnected graph: algebraic connectivity is exactly 0
    components = int(np.sum(vals < 1e-10))
    return fiedler, components


def greedy_match(fac: Facilities) -> list[Match]:
    candidates = []
    for g in fac.generators:
        for ld in fac.loads:
            s = match_score(g, ld)
            if s >= MATCH_THRESHOLD:
                candidates.append((s, g, ld))
    candidates.sort(key=lambda t: t[0], reverse=True)

    used_gen: dict[str, float] = {g.name: g.available_mw for g in fac.generators}
    served_load: set[str] = set()
    matches: list[Match] = []
    for s, g, ld in candidates:
        if ld.name in served_load or used_gen[g.name] <= 0:
            continue
        mw = round(min(used_gen[g.name], ld.needed_mw), 1)
        if mw < ld.needed_mw * (1.0 - ld.flexibility):
            continue  # can't even cover the firm portion
        used_gen[g.name] -= mw
        served_load.add(ld.name)
        matches.append(Match(g, ld, s, mw, alignment_for(g, ld, mw)))
    return matches


def run(fac: Facilities) -> Result:
    cat = build_category(fac)
    fiedler, components = spectral(cat)
    matches = greedy_match(fac)
    matched = {m.load.name for m in matches}
    stranded = [ld for ld in fac.loads if ld.name not in matched]
    feasible = len([m for m in cat.morphisms() if m.metadata.get("relation") == "feasible_coupling"])
    return Result(fac, cat, fiedler, components, stranded, matches, feasible)


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #
def stranded_reason(fac: Facilities, ld: Load) -> str:
    in_region = [g for g in fac.generators if g.region == ld.region]
    if not in_region:
        return "no stranded generation in-region"
    if ld.is_firm and not any(g.is_firm for g in in_region):
        return ("firm 24/7 load; only variable capacity in-region — needs storage/firming "
                "or transmission, not pure co-location")
    return "in-region capacity can't cover the firm (non-flexible) load"


def render(result: Result) -> str:
    fac = result.facilities
    meta = fac.meta
    total_need = sum(ld.needed_mw for ld in fac.loads)
    total_served = sum(m.mw_served for m in result.matches)
    total_available = sum(g.available_mw for g in fac.generators)
    ctx = meta.get("queue_context", {})

    L = [
        "# AI-Energy Matching Audit (KOMPOSOS-WESyS)",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## What This Is",
        "",
        "A reframing of WESyS around the 2026 AI energy dilemma. The bottleneck is not "
        "generation — it is interconnection and allocation. Stranded generation runs at partial "
        "utilization while AI load waits years to connect. This audit treats that as a "
        "categorical matching and contract problem: which stranded generator can energize which "
        "flexible AI load, and what agreement would make the match rational.",
        "",
        "The facilities below are calibrated to real 2026 figures and announced deals (see "
        "Provenance), but they are not a live queue export. Replace the data file with an "
        "ISO/RTO queue + EIA-860 utilization export for a real audit. Every value figure is an "
        "explicit hypothesis, not a validated claim.",
        "",
        "## Real-World Context",
        "",
        f"- U.S. interconnection queue (end 2025): {ctx.get('us_total_queue_gw_end_2025', 'n/a')} GW",
        f"- ERCOT large-load queue: {ctx.get('ercot_large_load_queue_gw', 'n/a')} GW "
        f"(up from {ctx.get('ercot_large_load_queue_gw_year_prior', 'n/a')} GW a year prior)",
        f"- ERCOT solar+storage share of queue: "
        f"{_pct(ctx.get('ercot_solar_storage_share_of_queue'))}",
        "",
        "## Data Loaded",
        "",
        f"- Stranded generators: {len(fac.generators)}  "
        f"(total available headroom: {total_available:.0f} MW)",
        f"- AI data-center loads: {len(fac.loads)}  (total demand: {total_need:.0f} MW)",
        f"- Feasible couplings found (score >= {MATCH_THRESHOLD}): {result.feasible_edges}",
        "",
        "## System Health (coupling graph)",
        "",
        f"- Algebraic connectivity (Fiedler): {result.fiedler:.4f}",
        f"- Connected components: {result.components}",
        "",
        "Interpretation: a high component count means loads and generators sit on separate "
        "islands with no feasible coupling between them — the structural signature of the "
        "allocation failure.",
        "",
        "## Finding",
        "",
        f"- Demand that can be served from stranded headroom: **{total_served:.0f} of "
        f"{total_need:.0f} MW** ({100 * total_served / max(total_need, 1):.0f}%)",
        f"- Matches proposed: {len(result.matches)}",
        f"- Loads left stranded (no feasible in-region match): {len(result.stranded_loads)}",
        "",
        "## Value Hypothesis",
        "",
        "The value here is *time-to-power*, not a fabricated savings number. Each match lets a "
        "load energize on an existing interconnection — months instead of a multi-year queue — "
        "while turning an underused asset into revenue. The unit to validate is **MW energized "
        "x queue-years avoided**, confirmed only after a real agreement and meter.",
        "",
        "## Proposed Matches",
        "",
    ]

    if not result.matches:
        L += ["No feasible matches at the current threshold.", ""]
    for i, m in enumerate(sorted(result.matches, key=lambda x: x.mw_served, reverse=True), 1):
        L += render_match(i, m)

    if result.stranded_loads:
        L += ["## Stranded Loads (the unsolved part)", ""]
        for ld in result.stranded_loads:
            L += [f"- **{ld.name}** ({ld.region}, {ld.needed_mw:.0f} MW, "
                  f"{ld.queue_years:.0f}-yr queue): {stranded_reason(fac, ld)}."]
        L += ["",
              "These are honest negatives: the engine should say where no match exists, not "
              "invent one. They are the queue-reform, firming, and transmission cases — not "
              "co-location cases.",
              ""]

    L += [
        "## Limits",
        "",
        "- This is a decision/coordination layer. It does not generate power or shorten a "
        "literal queue; it finds feasible matches and the agreement that unlocks them.",
        "- Cross-region couplings are scored as infeasible here — real transmission and "
        "deliverability modeling is required before claiming an inter-region match.",
        "- Facility data is calibrated but not a live export. Real use needs ISO/RTO queues, "
        "EIA-860 utilization, and the generator's actual PPA and ramp terms.",
        "- Dollar and queue-year values are hypotheses until one match is struck and measured.",
        "",
        "## Next Implementation Targets",
        "",
        "- Ingest a real ISO/RTO interconnection queue (PJM, ERCOT, MISO, SPP are public; "
        "LBNL 'Queued Up' is a clean aggregate).",
        "- Add EIA-860 / EIA-923 generator utilization to find true stranded headroom.",
        "- Model deliverability/transmission so cross-region matches become scoreable.",
        "- Store struck-deal outcomes and compare predicted vs. realized time-to-power.",
        "",
        "## Provenance",
        "",
    ]
    for s in meta.get("sources", []):
        L += [f"- {s}"]
    L += [""]
    return "\n".join(L)


def render_match(i: int, m: Match) -> list[str]:
    a = m.alignment
    out = [
        f"### {i}. {m.gen.name}  ->  {m.load.name}",
        "",
        f"- Region: {m.gen.region}",
        f"- Match score (coupling confidence): {m.score:.2f}",
        f"- MW served from stranded headroom: {m.mw_served:.0f} of {m.load.needed_mw:.0f} needed",
        f"- Load flexibility (interruptible share): {m.load.flexibility:.0%}",
        f"- Queue-years potentially avoided: ~{m.load.queue_years:.0f}",
        f"- Alignment tier: `{a.tier}`",
        "",
        "Actors:",
        "",
    ]
    out += [f"- {actor}" for actor in a.actors]
    out += [
        "",
        f"Activity diagnosis: {a.activity}",
        "",
        f"Game diagnosis: {a.game}",
        "",
        f"Contract path: {a.contract}",
        "",
        f"Constraints to design around: {'; '.join(a.constraints)}.",
        "",
        f"Measurement needs: {'; '.join(a.measurement)}.",
        "",
    ]
    return out


def _pct(x) -> str:
    return f"{x:.0%}" if isinstance(x, (int, float)) else "n/a"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI-Energy matching audit (WESyS reframe).")
    parser.add_argument("--data", default=str(DEFAULT_DATA))
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    fac = load_facilities(args.data)
    result = run(fac)
    report = render(result)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")

    served = sum(m.mw_served for m in result.matches)
    need = sum(ld.needed_mw for ld in fac.loads)
    print(f"Wrote {out}")
    print(f"  data file:          {args.data}")
    print(f"  feasible couplings: {result.feasible_edges}")
    print(f"  matches proposed:   {len(result.matches)}")
    print(f"  loads stranded:     {len(result.stranded_loads)}")
    print(f"  MW served:          {served:.0f} / {need:.0f} ({100 * served / max(need,1):.0f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
