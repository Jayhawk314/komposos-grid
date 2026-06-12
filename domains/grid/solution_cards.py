# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Energy solution cards from seam trends, queues, and relief curves.

The waste ledger says where value exists. Relief curves say what generic
interventions cost. Solution cards are the next product layer: concise,
evidence-graded recommendations that tell a human what to do next.

Cards intentionally keep three quantities separate:

* measured or proxy annual value at the seam;
* generic intervention economics from relief curves;
* project-specific next action needed to turn screening into a decision.
"""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence


@dataclass(frozen=True)
class SeamTrend:
    ba_a: str
    ba_b: str
    year: int
    spread_usd_mwh: float
    component_spread_usd_mwh: float
    hours_observed: float = 0.0
    source: str = ""
    notes: str = ""

    @property
    def tie(self) -> str:
        return f"{self.ba_a}-{self.ba_b}"

    @property
    def action_spread_usd_mwh(self) -> float:
        return self.component_spread_usd_mwh or self.spread_usd_mwh


@dataclass(frozen=True)
class EnergySolutionCard:
    card_id: str
    title: str
    geography: str
    solution_status: str
    current_year: int
    evidence_basis: str
    annual_value_usd: float
    spread_usd_mwh: float
    trend_summary: str
    active_queue_gw: float
    withdrawn_queue_gw: float
    active_queue_can_reach_cap: bool
    withdrawn_queue_can_reach_cap: bool
    best_generic_intervention: str
    best_generic_mw: float
    best_generic_benefit_cost_ratio: float
    updated_generic_benefit_cost_ratio: float
    constraints: List[str]
    recommended_solution: str
    next_action: str
    caveat: str
    source_files: List[str]

    def to_row(self) -> Dict[str, Any]:
        return {
            "card_id": self.card_id,
            "title": self.title,
            "geography": self.geography,
            "solution_status": self.solution_status,
            "current_year": self.current_year,
            "evidence_basis": self.evidence_basis,
            "annual_value_usd": self.annual_value_usd,
            "spread_usd_mwh": self.spread_usd_mwh,
            "trend_summary": self.trend_summary,
            "active_queue_gw": self.active_queue_gw,
            "withdrawn_queue_gw": self.withdrawn_queue_gw,
            "active_queue_can_reach_cap": self.active_queue_can_reach_cap,
            "withdrawn_queue_can_reach_cap": self.withdrawn_queue_can_reach_cap,
            "best_generic_intervention": self.best_generic_intervention,
            "best_generic_mw": self.best_generic_mw,
            "best_generic_benefit_cost_ratio": self.best_generic_benefit_cost_ratio,
            "updated_generic_benefit_cost_ratio": self.updated_generic_benefit_cost_ratio,
            "constraints": "; ".join(self.constraints),
            "recommended_solution": self.recommended_solution,
            "next_action": self.next_action,
            "caveat": self.caveat,
            "source_files": "; ".join(self.source_files),
        }


@dataclass
class EnergySolutionReport:
    cards: List[EnergySolutionCard]

    def ranked(self) -> List[EnergySolutionCard]:
        return sorted(
            self.cards,
            key=lambda card: (
                _status_rank(card.solution_status),
                card.annual_value_usd,
                card.updated_generic_benefit_cost_ratio,
            ),
            reverse=True,
        )

    def summary(self, top: int = 8) -> str:
        lines = [f"Energy solution cards: {len(self.cards)}"]
        for card in self.ranked()[:top]:
            lines.append(
                f"  [{card.solution_status}] {card.geography}: "
                f"${card.annual_value_usd:,.0f}/yr, "
                f"spread ${card.spread_usd_mwh:.2f}/MWh, "
                f"generic B/C {card.updated_generic_benefit_cost_ratio:.2f}"
            )
        return "\n".join(lines)

    def to_rows(self) -> List[Dict[str, Any]]:
        return [card.to_row() for card in self.ranked()]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_cards": len(self.cards),
            "cards": self.to_rows(),
        }

    def to_markdown(self) -> str:
        lines = [
            "# Energy Solution Cards",
            "",
            "## Summary",
            "",
            f"- Cards: **{len(self.cards)}**",
            "",
            "## Cards",
            "",
            "| Status | Geography | Value | Spread | Queue | Generic B/C | Recommended Solution | Next Action | Caveat |",
            "|---|---|---:|---:|---:|---:|---|---|---|",
        ]
        for card in self.ranked():
            queue = f"{card.active_queue_gw:,.1f} GW active / {card.withdrawn_queue_gw:,.1f} GW withdrawn"
            lines.append(
                f"| {card.solution_status} | {card.geography} | "
                f"${card.annual_value_usd:,.0f}/yr | "
                f"${card.spread_usd_mwh:.2f}/MWh | {queue} | "
                f"{card.updated_generic_benefit_cost_ratio:.2f} | "
                f"{card.recommended_solution} | {card.next_action} | {card.caveat} |"
            )
        lines.extend(["", "## Detail", ""])
        for card in self.ranked():
            lines.extend([
                f"### {card.geography}",
                "",
                f"- Status: **{card.solution_status}**",
                f"- Evidence: {card.evidence_basis}",
                f"- Trend: {card.trend_summary}",
                f"- Constraints: {'; '.join(card.constraints) if card.constraints else 'not attached'}",
                f"- Best generic intervention: {card.best_generic_intervention} "
                f"at {card.best_generic_mw:,.0f} MW, B/C "
                f"{card.updated_generic_benefit_cost_ratio:.2f}",
                f"- Recommended solution: {card.recommended_solution}",
                f"- Next action: {card.next_action}",
                f"- Caveat: {card.caveat}",
                "",
            ])
        return "\n".join(lines) + "\n"

    def export_csv(self, path: str | Path) -> None:
        _write_csv(path, self.to_rows())

    def export_json(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    def export_markdown(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(), encoding="utf-8")


def build_energy_solution_report(
    congestion_report: str | Path,
    queue_match: str | Path,
    relief_curves: str | Path,
    miso_evidence: str | Path | Sequence[str | Path] | None = None,
    nyiso_2024_2025: str | Path | None = None,
    ercot_spreads: str | Path | None = None,
) -> EnergySolutionReport:
    congestion_path = Path(congestion_report)
    queue_path = Path(queue_match)
    relief_path = Path(relief_curves)
    congestion = _load_congestion(congestion_path)
    queue = _load_queue(queue_path)
    relief = _load_relief(relief_path)
    miso_paths = _as_paths(miso_evidence)
    trends = _collect_trends(congestion, miso_paths, nyiso_2024_2025)

    cards: List[EnergySolutionCard] = []
    priority_ties = [
        ("PJM", "NYIS"),
        ("MISO", "SWPP"),
        ("MISO", "SOCO"),
        ("CISO", "SRP"),
        ("BPAT", "CISO"),
    ]
    for ba_a, ba_b in priority_ties:
        card = _card_for_tie(
            ba_a,
            ba_b,
            congestion=congestion,
            queue=queue,
            relief=relief,
            trends=trends,
            source_files=[
                str(congestion_path),
                str(queue_path),
                str(relief_path),
            ]
            + _existing_source_files(*miso_paths, nyiso_2024_2025),
        )
        if card is not None:
            cards.append(card)

    ercot = _ercot_card(ercot_spreads)
    if ercot is not None:
        cards.append(ercot)

    return EnergySolutionReport(cards=cards)


def load_miso_trends(path: str | Path) -> List[SeamTrend]:
    rows = _read_csv(path)
    trends: List[SeamTrend] = []
    for row in rows:
        year = _year_from_text(str(row.get("evidence_source", "")))
        if year is None:
            continue
        trends.append(
            SeamTrend(
                ba_a=_clean_ba(row.get("ba_a")),
                ba_b=_clean_ba(row.get("ba_b")),
                year=year,
                spread_usd_mwh=_float(row.get("mean_price_spread_usd_mwh")),
                component_spread_usd_mwh=_float(
                    row.get("mean_congestion_component_spread_usd_mwh")
                ),
                hours_observed=_float(row.get("hours_observed")),
                source=str(row.get("evidence_source", "")),
                notes=str(row.get("notes", "")),
            )
        )
    return trends


def load_nyiso_trends(path: str | Path) -> List[SeamTrend]:
    text = _read_text(path)
    pattern = re.compile(
        r"(?P<year>20\d{2}) \| NYISO seam component audit vs PJM: "
        r"(?P<hours>\d+) hours, mean \|LBMP spread\| "
        r"\$(?P<spread>[0-9.]+)/MWh, mean \|congestion-component spread\| "
        r"\$(?P<component>[0-9.]+)/MWh"
    )
    trends: List[SeamTrend] = []
    for match in pattern.finditer(text):
        trends.append(
            SeamTrend(
                ba_a="PJM",
                ba_b="NYIS",
                year=int(match.group("year")),
                spread_usd_mwh=float(match.group("spread")),
                component_spread_usd_mwh=float(match.group("component")),
                hours_observed=float(match.group("hours")),
                source=str(path),
                notes="NYISO component rerun vs PJM proxy",
            )
        )
    return trends


def _card_for_tie(
    ba_a: str,
    ba_b: str,
    congestion: Mapping[tuple[str, str], Mapping[str, Any]],
    queue: Mapping[tuple[str, str], Mapping[str, Any]],
    relief: Mapping[tuple[str, str], Mapping[str, Any]],
    trends: Mapping[tuple[str, str], List[SeamTrend]],
    source_files: List[str],
) -> EnergySolutionCard | None:
    key = _tie_key(ba_a, ba_b)
    base = congestion.get(key)
    q = queue.get(key, {})
    r = relief.get(key, {})
    if base is None and not q:
        return None

    gross_mwh = _float((base or {}).get("gross_mwh"))
    base_spread = _float((base or {}).get("mean_congestion_component_spread_usd_mwh"))
    if base_spread <= 0:
        base_spread = _float(q.get("congestion_spread_usd_mwh"))
    if gross_mwh <= 0 and base_spread > 0:
        gross_mwh = _float(q.get("tie_value_cap_usd")) / base_spread
    if gross_mwh <= 0 or base_spread <= 0:
        return None

    trend_rows = sorted(trends.get(key, []), key=lambda t: t.year)
    latest = trend_rows[-1] if trend_rows else SeamTrend(
        ba_a=key[0],
        ba_b=key[1],
        year=2023,
        spread_usd_mwh=_float((base or {}).get("mean_price_spread_usd_mwh")),
        component_spread_usd_mwh=base_spread,
        source=str((base or {}).get("evidence_source", "")),
    )
    current_spread = latest.action_spread_usd_mwh
    annual_value = gross_mwh * current_spread
    base_value_cap = _float(q.get("tie_value_cap_usd")) or gross_mwh * base_spread

    active = q.get("active", {}) if isinstance(q.get("active"), dict) else {}
    withdrawn = q.get("withdrawn", {}) if isinstance(q.get("withdrawn"), dict) else {}
    active_cap = _float(active.get("capped_value_usd"))
    withdrawn_cap = _float(withdrawn.get("capped_value_usd"))
    active_can_cap = active_cap >= 0.95 * base_value_cap if base_value_cap else False
    withdrawn_can_cap = withdrawn_cap >= 0.95 * base_value_cap if base_value_cap else False

    base_bcr = _float(r.get("best_benefit_cost_ratio"))
    updated_bcr = base_bcr * (current_spread / base_spread) if base_spread > 0 else base_bcr
    constraints = _constraints_from_relief(r)
    status, recommendation, next_action, caveat = _recommendation(
        key,
        latest,
        updated_bcr,
        bool(trend_rows),
    )
    title = _title_for(key)
    evidence_basis = str((base or {}).get("evidence_source", latest.source))
    trend_summary = _trend_summary(key, base_spread, trend_rows)

    return EnergySolutionCard(
        card_id=f"solution_{key[0].lower()}_{key[1].lower()}",
        title=title,
        geography=f"{key[0]}-{key[1]}",
        solution_status=status,
        current_year=latest.year,
        evidence_basis=evidence_basis,
        annual_value_usd=annual_value,
        spread_usd_mwh=current_spread,
        trend_summary=trend_summary,
        active_queue_gw=_float(active.get("gw")),
        withdrawn_queue_gw=_float(withdrawn.get("gw")),
        active_queue_can_reach_cap=active_can_cap,
        withdrawn_queue_can_reach_cap=withdrawn_can_cap,
        best_generic_intervention=str(r.get("best_benchmark", "")),
        best_generic_mw=_float(r.get("best_intervention_mw")),
        best_generic_benefit_cost_ratio=base_bcr,
        updated_generic_benefit_cost_ratio=updated_bcr,
        constraints=constraints,
        recommended_solution=recommendation,
        next_action=next_action,
        caveat=caveat,
        source_files=source_files,
    )


def _ercot_card(path: str | Path | None) -> EnergySolutionCard | None:
    if path is None or not Path(path).exists():
        return None
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    if not rows:
        return None
    rows = sorted(rows, key=lambda row: int(row.get("year", 0)))
    latest = rows[-1]
    first = rows[0]
    spread = _float(latest.get("mean_abs_spread_usd_mwh"))
    trend = (
        f"{first.get('year')} ${_float(first.get('mean_abs_spread_usd_mwh')):.2f}/MWh "
        f"-> {latest.get('year')} ${spread:.2f}/MWh."
    )
    return EnergySolutionCard(
        card_id="solution_ercot_west_north",
        title="ERCOT West-North congestion watch",
        geography="ERCO West-North hubs",
        solution_status="watchlist_for_solution_screen",
        current_year=int(latest.get("year", 0)),
        evidence_basis="ERCOT DAM hub spread series",
        annual_value_usd=0.0,
        spread_usd_mwh=spread,
        trend_summary=trend,
        active_queue_gw=0.0,
        withdrawn_queue_gw=0.0,
        active_queue_can_reach_cap=False,
        withdrawn_queue_can_reach_cap=False,
        best_generic_intervention="not_evaluated",
        best_generic_mw=0.0,
        best_generic_benefit_cost_ratio=0.0,
        updated_generic_benefit_cost_ratio=0.0,
        constraints=[],
        recommended_solution=(
            "Run ERCOT-specific queue/site matching before ranking storage or "
            "transmission interventions."
        ),
        next_action="Attach ERCOT queue and constraint evidence to the West-North spread trend.",
        caveat="Hub spread trend is directional; no BA tie gross-flow value is attached.",
        source_files=[str(path)],
    )


def _as_paths(
    evidence: str | Path | Sequence[str | Path] | None,
) -> List[Path]:
    if evidence is None:
        return []
    if isinstance(evidence, (str, Path)):
        return [Path(evidence)]
    return [Path(p) for p in evidence]


def _collect_trends(
    congestion: Mapping[tuple[str, str], Mapping[str, Any]],
    miso_evidence: Sequence[Path],
    nyiso_2024_2025: str | Path | None,
) -> Dict[tuple[str, str], List[SeamTrend]]:
    trends: Dict[tuple[str, str], List[SeamTrend]] = {}
    for key, row in congestion.items():
        spread = _float(row.get("mean_price_spread_usd_mwh"))
        component = _float(row.get("mean_congestion_component_spread_usd_mwh"))
        if component <= 0 and spread <= 0:
            continue
        trends.setdefault(key, []).append(
            SeamTrend(
                ba_a=key[0],
                ba_b=key[1],
                year=2023,
                spread_usd_mwh=spread,
                component_spread_usd_mwh=component or spread,
                hours_observed=_float(row.get("hours_observed")),
                source=str(row.get("evidence_source", "")),
                notes=str(row.get("notes", "")),
            )
        )
    for evidence_path in miso_evidence:
        if not evidence_path.exists():
            continue
        for trend in load_miso_trends(evidence_path):
            trends.setdefault(_tie_key(trend.ba_a, trend.ba_b), []).append(trend)
    if nyiso_2024_2025 and Path(nyiso_2024_2025).exists():
        for trend in load_nyiso_trends(nyiso_2024_2025):
            trends.setdefault(_tie_key(trend.ba_a, trend.ba_b), []).append(trend)
    for key in list(trends):
        dedup: Dict[int, SeamTrend] = {}
        for trend in trends[key]:
            dedup[trend.year] = trend
        trends[key] = sorted(dedup.values(), key=lambda t: t.year)
    return trends


def _load_congestion(path: Path) -> Dict[tuple[str, str], Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        _tie_key(str(row.get("ba_a", "")), str(row.get("ba_b", ""))): row
        for row in payload.get("claims", [])
        if str(row.get("ba_a", "")).strip() and str(row.get("ba_b", "")).strip()
    }


def _load_queue(path: Path) -> Dict[tuple[str, str], Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        _tie_key(str(row.get("ba_a", "")), str(row.get("ba_b", ""))): row
        for row in payload.get("ties", [])
        if str(row.get("ba_a", "")).strip() and str(row.get("ba_b", "")).strip()
    }


def _load_relief(path: Path) -> Dict[tuple[str, str], Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        _tie_key(str(row.get("ba_a", "")), str(row.get("ba_b", ""))): row
        for row in payload.get("opportunities", [])
        if str(row.get("ba_a", "")).strip() and str(row.get("ba_b", "")).strip()
    }


def _recommendation(
    key: tuple[str, str],
    latest: SeamTrend,
    updated_bcr: float,
    has_trend: bool,
) -> tuple[str, str, str, str]:
    tie = f"{key[0]}-{key[1]}"
    if key == _tie_key("PJM", "NYIS"):
        return (
            "priority_solution_study",
            "Use 2025 congestion economics to scope NY import/export relief, storage, and queue-rescue packages.",
            "Rebuild congestion evidence and relief curves on the 2025 NYISO component spread, then price named projects.",
            "Generic costs still do not clear B/C > 1; the value is now high enough for project-specific costing.",
        )
    if key == _tie_key("MISO", "SWPP"):
        return (
            "priority_solution_study",
            "Target wind-belt transfer relief: transmission upgrades, storage on the export side, and queue rescue on the import side.",
            "Tie CHAWATCHAPAT/Charlie Creek-Watford constraints to candidate upgrades and rerun relief curves on 2024 spread.",
            "Screening uses MISO-side settlement evidence; SPP-side evidence corroborates but should not be double-counted.",
        )
    if key == _tie_key("MISO", "SOCO"):
        return (
            "bounded_solution_screen",
            "Keep as a Southeast import-boundary screen; use targeted price/constraint evidence before spending design effort.",
            "Attach SOCO/neighbor settlement or planning evidence and compare to Right Kan Southeast bounds.",
            "Value is smaller than PJM-NYIS and MISO-SWPP, but it anchors Southeast bounds.",
        )
    if key in {_tie_key("CISO", "SRP"), _tie_key("BPAT", "CISO")}:
        return (
            "methodology_validated_screen",
            "Use OASIS-corrected spreads for Western storage/transmission siting screens, not old ICE hub levels.",
            "Replace generic benchmark costs with project-specific storage, flexible-load, or transmission estimates.",
            "OASIS correction made this defensible but much smaller than the old hub-proxy headline.",
        )
    status = "solution_screen_with_trend" if has_trend else "solution_screen"
    if updated_bcr >= 1.0:
        status = "candidate_for_scoping"
    return (
        status,
        f"Scope targeted relief for {tie} after project-specific costs are attached.",
        "Attach named projects, cost estimates, and operational constraints.",
        "Screening card; not yet decision-grade.",
    )


def _title_for(key: tuple[str, str]) -> str:
    titles = {
        _tie_key("PJM", "NYIS"): "NYISO-PJM 2025 congestion relief",
        _tie_key("MISO", "SWPP"): "MISO-SPP wind-belt transfer relief",
        _tie_key("MISO", "SOCO"): "MISO-SOCO Southeast boundary screen",
        _tie_key("CISO", "SRP"): "CISO-SRP OASIS-corrected Western screen",
        _tie_key("BPAT", "CISO"): "BPAT-CISO OASIS-corrected Western screen",
    }
    return titles.get(key, f"{key[0]}-{key[1]} solution screen")


def _trend_summary(
    key: tuple[str, str],
    base_spread: float,
    trends: Sequence[SeamTrend],
) -> str:
    if not trends:
        return f"Current evidence spread ${base_spread:.2f}/MWh."
    parts = [
        f"{trend.year} ${trend.action_spread_usd_mwh:.2f}/MWh"
        for trend in sorted(trends, key=lambda t: t.year)
    ]
    if len(trends) >= 2:
        first, last = trends[0], trends[-1]
        ratio = last.action_spread_usd_mwh / first.action_spread_usd_mwh if first.action_spread_usd_mwh else 0.0
        return f"{' -> '.join(parts)} ({ratio:.1f}x over observed window)."
    return f"{' -> '.join(parts)}."


def _constraints_from_relief(row: Mapping[str, Any]) -> List[str]:
    text = str(row.get("constraints", "")).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def _existing_source_files(*paths: str | Path | None) -> List[str]:
    return [str(path) for path in paths if path and Path(path).exists()]


def _read_csv(path: str | Path) -> List[Dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _read_text(path: str | Path) -> str:
    data = Path(path).read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _tie_key(ba_a: str, ba_b: str) -> tuple[str, str]:
    return tuple(sorted((_clean_ba(ba_a), _clean_ba(ba_b))))


def _clean_ba(value: Any) -> str:
    return str(value or "").strip()


def _year_from_text(text: str) -> int | None:
    match = re.search(r"(20\d{2})-\d{2}-\d{2}", text)
    return int(match.group(1)) if match else None


def _status_rank(status: str) -> int:
    order = {
        "priority_solution_study": 5,
        "candidate_for_scoping": 4,
        "methodology_validated_screen": 3,
        "bounded_solution_screen": 2,
        "watchlist_for_solution_screen": 1,
        "solution_screen": 1,
    }
    return order.get(status, 0)


def _float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    text = str(value).strip().replace(",", "").replace("$", "")
    if not text:
        return 0.0
    try:
        out = float(text)
    except ValueError:
        return 0.0
    return 0.0 if math.isnan(out) else out


def _write_csv(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = _fields(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _fields(rows: List[Dict[str, Any]]) -> List[str]:
    if not rows:
        return ["status"]
    seen = {field for row in rows for field in row}
    preferred = [
        "card_id",
        "title",
        "geography",
        "solution_status",
        "current_year",
        "annual_value_usd",
        "spread_usd_mwh",
        "active_queue_gw",
        "withdrawn_queue_gw",
        "best_generic_intervention",
        "best_generic_mw",
        "updated_generic_benefit_cost_ratio",
        "recommended_solution",
        "next_action",
        "caveat",
        "trend_summary",
        "constraints",
        "evidence_basis",
        "source_files",
    ]
    return [field for field in preferred if field in seen] + sorted(seen - set(preferred))
