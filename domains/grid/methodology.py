# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Grid evidence methodology checks for PLAN C5-C7.

This module makes three methodology moves operational:

* C5: evidence corrections are represented as 2-cells between parallel
  evidence morphisms for the same BA tie.
* C6: unpriced Southeast structural ties get conservative Right Kan
  bounds from adjacent priced measurements.
* C7: repeated proxy-overstatement corrections become a machine-readable
  axiom/warning pattern.

The outputs are proof artifacts. They do not promote bounded or proxy
claims into measured congestion cost.
"""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from categorical.two_categories import TwoCategory
from zfc.axiom_miner import AxiomPattern


SOUTHEAST_BAS = {
    "AECI",
    "CPLE",
    "CPLW",
    "DUK",
    "FMPP",
    "FPC",
    "FPL",
    "GVL",
    "HST",
    "JEA",
    "LGEE",
    "SC",
    "SCEG",
    "SEC",
    "SEPA",
    "SOCO",
    "TAL",
    "TEC",
    "TVA",
    "YAD",
}


@dataclass(frozen=True)
class EvidenceCorrectionCell:
    """A 2-cell correcting one evidence morphism into another."""

    ba_a: str
    ba_b: str
    source_method: str
    target_method: str
    source_spread_usd_mwh: float
    target_spread_usd_mwh: float
    target_component_spread_usd_mwh: float
    ratio: float
    gross_mwh: float = 0.0
    source_value_usd: float = 0.0
    target_value_usd: float = 0.0
    avoided_overclaim_usd: float = 0.0
    source_evidence: str = ""
    target_evidence: str = ""
    note: str = ""

    @property
    def tie(self) -> str:
        return f"{self.ba_a}-{self.ba_b}"

    def to_row(self) -> Dict[str, Any]:
        return {
            "ba_a": self.ba_a,
            "ba_b": self.ba_b,
            "source_method": self.source_method,
            "target_method": self.target_method,
            "source_spread_usd_mwh": self.source_spread_usd_mwh,
            "target_spread_usd_mwh": self.target_spread_usd_mwh,
            "target_component_spread_usd_mwh": self.target_component_spread_usd_mwh,
            "overstatement_ratio": self.ratio,
            "gross_mwh": self.gross_mwh,
            "source_value_usd": self.source_value_usd,
            "target_value_usd": self.target_value_usd,
            "avoided_overclaim_usd": self.avoided_overclaim_usd,
            "source_evidence": self.source_evidence,
            "target_evidence": self.target_evidence,
            "note": self.note,
        }


@dataclass(frozen=True)
class RightKanBound:
    """Conservative bound for an unpriced structural tie."""

    ba_a: str
    ba_b: str
    gross_mwh: float
    net_direction: str
    curvature: float
    bound_spread_usd_mwh: float
    bound_value_usd: float
    adjacent_measurements: List[str]
    status: str
    note: str = ""

    @property
    def tie(self) -> str:
        return f"{self.ba_a}-{self.ba_b}"

    def to_row(self) -> Dict[str, Any]:
        return {
            "ba_a": self.ba_a,
            "ba_b": self.ba_b,
            "gross_mwh": self.gross_mwh,
            "net_direction": self.net_direction,
            "curvature": self.curvature,
            "bound_spread_usd_mwh": self.bound_spread_usd_mwh,
            "bound_value_usd": self.bound_value_usd,
            "adjacent_measurements": "; ".join(self.adjacent_measurements),
            "status": self.status,
            "note": self.note,
        }


@dataclass(frozen=True)
class ProxyWarning:
    """A warning emitted by the mined methodology axiom."""

    ba_a: str
    ba_b: str
    method: str
    spread_usd_mwh: float
    status: str
    warning: str

    def to_row(self) -> Dict[str, Any]:
        return {
            "ba_a": self.ba_a,
            "ba_b": self.ba_b,
            "method": self.method,
            "spread_usd_mwh": self.spread_usd_mwh,
            "status": self.status,
            "warning": self.warning,
        }


@dataclass
class GridMethodologyReport:
    corrections: List[EvidenceCorrectionCell]
    right_kan_bounds: List[RightKanBound]
    axioms: List[AxiomPattern]
    warnings: List[ProxyWarning]

    @property
    def mean_overstatement_ratio(self) -> float:
        if not self.corrections:
            return 0.0
        return sum(c.ratio for c in self.corrections) / len(self.corrections)

    def summary(self) -> str:
        bounded = [b for b in self.right_kan_bounds if b.status == "bounded"]
        lines = [
            "Grid methodology report",
            f"  correction 2-cells: {len(self.corrections)}",
            f"  mean proxy overstatement: {self.mean_overstatement_ratio:.1f}x",
            f"  Right Kan bounds: {len(bounded)} bounded / {len(self.right_kan_bounds)} reviewed",
            f"  mined axioms: {len(self.axioms)}; proxy warnings: {len(self.warnings)}",
        ]
        for cell in sorted(self.corrections, key=lambda c: -c.ratio)[:5]:
            lines.append(
                f"  {cell.tie}: {cell.source_method} -> {cell.target_method}, "
                f"{cell.ratio:.1f}x correction"
            )
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "correction_2cells": [c.to_row() for c in self.corrections],
            "mean_overstatement_ratio": self.mean_overstatement_ratio,
            "right_kan_bounds": [b.to_row() for b in self.right_kan_bounds],
            "axioms": [
                {
                    "name": a.name,
                    "description": a.description,
                    "template": a.template,
                    "support": a.support,
                    "agree_rate": a.agree_rate,
                    "avg_confidence": a.avg_confidence,
                    "domains": a.domains,
                    "example_episodes": a.example_episodes,
                }
                for a in self.axioms
            ],
            "proxy_warnings": [w.to_row() for w in self.warnings],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Grid Methodology Report",
            "",
            "## Summary",
            "",
            f"- Correction 2-cells: **{len(self.corrections)}**",
            f"- Mean proxy overstatement: **{self.mean_overstatement_ratio:.1f}x**",
            f"- Right Kan ties reviewed: **{len(self.right_kan_bounds)}**",
            f"- Mined methodology axioms: **{len(self.axioms)}**",
            f"- Proxy warnings: **{len(self.warnings)}**",
            "",
            "## Evidence Correction 2-Cells",
            "",
            "| Tie | Source Method | Target Method | Source $/MWh | Target $/MWh | Ratio | Avoided Overclaim |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
        if not self.corrections:
            lines.append("| None |  |  |  |  |  |  |")
        for cell in sorted(self.corrections, key=lambda c: -c.ratio):
            lines.append(
                f"| {cell.tie} | {cell.source_method} | {cell.target_method} | "
                f"{cell.source_spread_usd_mwh:.2f} | {cell.target_spread_usd_mwh:.2f} | "
                f"{cell.ratio:.1f}x | ${cell.avoided_overclaim_usd:,.0f} |"
            )

        lines.extend([
            "",
            "## Right Kan Bounds",
            "",
            "Bounds use the minimum adjacent priced spread as the limit/meet. "
            "They are upper-screening bounds for unpriced structural ties, not measured cost.",
            "",
            "| Tie | Status | Bound $/MWh | Bound Value | Adjacent Measurements |",
            "|---|---|---:|---:|---|",
        ])
        if not self.right_kan_bounds:
            lines.append("| None |  |  |  |  |")
        for bound in self.right_kan_bounds:
            adjacent = "; ".join(bound.adjacent_measurements)
            lines.append(
                f"| {bound.tie} | {bound.status} | "
                f"{bound.bound_spread_usd_mwh:.2f} | ${bound.bound_value_usd:,.0f} | "
                f"{adjacent} |"
            )

        lines.extend([
            "",
            "## Mined Axioms",
            "",
        ])
        if not self.axioms:
            lines.append("No methodology axioms met support thresholds.")
        for axiom in self.axioms:
            lines.extend([
                f"### {axiom.name}",
                "",
                f"- Template: `{axiom.template}`",
                f"- Support: **{axiom.support}** correction episodes",
                f"- Agreement rate: **{axiom.agree_rate:.0%}**",
                f"- Average confidence: **{axiom.avg_confidence:.2f}**",
                f"- Description: {axiom.description}",
                "",
            ])

        lines.extend([
            "## Proxy Warnings",
            "",
            "| Tie | Method | Status | Warning |",
            "|---|---|---|---|",
        ])
        if not self.warnings:
            lines.append("| None |  |  |  |")
        for warning in self.warnings:
            lines.append(
                f"| {warning.ba_a}-{warning.ba_b} | {warning.method} | "
                f"{warning.status} | {warning.warning} |"
            )
        return "\n".join(lines) + "\n"

    def export_json(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    def export_markdown(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(), encoding="utf-8")

    def export_corrections_csv(self, path: str | Path) -> None:
        _write_csv(path, [c.to_row() for c in self.corrections])

    def export_bounds_csv(self, path: str | Path) -> None:
        _write_csv(path, [b.to_row() for b in self.right_kan_bounds])

    def export_warnings_csv(self, path: str | Path) -> None:
        _write_csv(path, [w.to_row() for w in self.warnings])


def build_methodology_report(
    legacy_evidence_paths: Iterable[str | Path],
    corrected_evidence_paths: Iterable[str | Path],
    congestion_report: str | Path,
    min_correction_ratio: float = 2.0,
) -> GridMethodologyReport:
    legacy_rows = _load_rows(legacy_evidence_paths)
    corrected_rows = _load_rows(corrected_evidence_paths)
    flow_rows = _load_rows([congestion_report])

    corrections = build_evidence_correction_cells(
        legacy_rows,
        corrected_rows,
        min_ratio=min_correction_ratio,
    )
    bounds = build_right_kan_bounds(flow_rows)
    axioms = mine_proxy_axioms(corrections)
    warnings = build_proxy_warnings(legacy_rows, corrections)
    return GridMethodologyReport(
        corrections=corrections,
        right_kan_bounds=bounds,
        axioms=axioms,
        warnings=warnings,
    )


def build_evidence_two_category(cells: Sequence[EvidenceCorrectionCell]) -> TwoCategory:
    two_cat = TwoCategory("grid_evidence_methodology")
    for cell in cells:
        tie_obj = f"tie:{cell.tie}"
        value_obj = f"spread_claim:{cell.tie}"
        two_cat.add_object(tie_obj, {"ba_a": cell.ba_a, "ba_b": cell.ba_b})
        two_cat.add_object(value_obj, {"unit": "usd_per_mwh"})

        source_mor = _safe_name(f"{cell.tie}:{cell.source_method}")
        target_mor = _safe_name(f"{cell.tie}:{cell.target_method}")
        two_cat.add_morphism(
            source_mor,
            tie_obj,
            value_obj,
            {
                "method": cell.source_method,
                "spread_usd_mwh": cell.source_spread_usd_mwh,
            },
        )
        two_cat.add_morphism(
            target_mor,
            tie_obj,
            value_obj,
            {
                "method": cell.target_method,
                "spread_usd_mwh": cell.target_spread_usd_mwh,
            },
        )
        two_cat.add_two_cell(
            _safe_name(f"corrects:{cell.tie}:{cell.source_method}:to:{cell.target_method}"),
            source_mor,
            target_mor,
            data=cell.to_row(),
        )
    return two_cat


def build_evidence_correction_cells(
    legacy_rows: Sequence[Mapping[str, Any]],
    corrected_rows: Sequence[Mapping[str, Any]],
    min_ratio: float = 2.0,
) -> List[EvidenceCorrectionCell]:
    corrected_by_key = {_tie_key_from_row(row): row for row in corrected_rows}
    cells: List[EvidenceCorrectionCell] = []
    for legacy in legacy_rows:
        key = _tie_key_from_row(legacy)
        if not key:
            continue
        corrected = corrected_by_key.get(key)
        if not corrected:
            continue
        if not _is_hub_proxy(legacy):
            continue
        if _is_hub_proxy(corrected):
            continue

        source_spread = _mean_price_spread(legacy)
        target_spread = _mean_price_spread(corrected)
        if source_spread <= 0 or target_spread <= 0:
            continue
        ratio = source_spread / target_spread
        if ratio < min_ratio:
            continue

        ba_a, ba_b = key
        gross_mwh = _float(corrected.get("gross_mwh"))
        source_value = source_spread * gross_mwh if gross_mwh else 0.0
        target_value = target_spread * gross_mwh if gross_mwh else _float(
            corrected.get("estimated_value_usd")
        )
        cells.append(
            EvidenceCorrectionCell(
                ba_a=ba_a,
                ba_b=ba_b,
                source_method=_method(legacy),
                target_method=_method(corrected),
                source_spread_usd_mwh=source_spread,
                target_spread_usd_mwh=target_spread,
                target_component_spread_usd_mwh=_component_spread(corrected),
                ratio=ratio,
                gross_mwh=gross_mwh,
                source_value_usd=source_value,
                target_value_usd=target_value,
                avoided_overclaim_usd=max(source_value - target_value, 0.0),
                source_evidence=str(legacy.get("evidence_source", "")),
                target_evidence=str(corrected.get("evidence_source", "")),
                note="methodology correction tracked as a 2-cell",
            )
        )
    return sorted(cells, key=lambda c: (-c.ratio, c.tie))


def build_right_kan_bounds(
    congestion_rows: Sequence[Mapping[str, Any]],
    southeast_bas: set[str] | None = None,
) -> List[RightKanBound]:
    southeast_bas = southeast_bas or SOUTHEAST_BAS
    priced: List[tuple[tuple[str, str], float, str]] = []
    structural: List[Mapping[str, Any]] = []
    for row in congestion_rows:
        key = _tie_key_from_row(row)
        if not key:
            continue
        status = str(row.get("evidence_status", ""))
        spread = _component_spread(row) or _mean_price_spread(row)
        if status in {"structural_only", ""} or spread <= 0:
            structural.append(row)
        else:
            priced.append((key, spread, f"{key[0]}-{key[1]} ${spread:.2f}/MWh"))

    bounds: List[RightKanBound] = []
    for row in structural:
        key = _tie_key_from_row(row)
        if not key:
            continue
        ba_a, ba_b = key
        if ba_a not in southeast_bas and ba_b not in southeast_bas:
            continue

        adjacent = [
            (spread, label)
            for priced_key, spread, label in priced
            if ba_a in priced_key or ba_b in priced_key
        ]
        gross_mwh = _float(row.get("gross_mwh"))
        if adjacent:
            bound_spread = min(spread for spread, _ in adjacent)
            labels = [label for spread, label in sorted(adjacent)]
            status = "bounded"
            note = "Right Kan meet over adjacent priced measurements."
        else:
            bound_spread = 0.0
            labels = []
            status = "unbounded_no_priced_neighbor"
            note = "No adjacent priced measurement exists in the current report."

        bounds.append(
            RightKanBound(
                ba_a=ba_a,
                ba_b=ba_b,
                gross_mwh=gross_mwh,
                net_direction=str(row.get("net_direction", "")),
                curvature=_float(row.get("curvature")),
                bound_spread_usd_mwh=bound_spread,
                bound_value_usd=bound_spread * gross_mwh,
                adjacent_measurements=labels,
                status=status,
                note=note,
            )
        )
    return sorted(
        bounds,
        key=lambda b: (b.status == "bounded", b.bound_value_usd, b.gross_mwh),
        reverse=True,
    )


def mine_proxy_axioms(
    corrections: Sequence[EvidenceCorrectionCell],
    min_support: int = 2,
    min_ratio: float = 3.0,
) -> List[AxiomPattern]:
    strong = [c for c in corrections if c.ratio >= min_ratio]
    if len(strong) < min_support:
        return []
    mean_ratio = sum(c.ratio for c in strong) / len(strong)
    min_seen = min(c.ratio for c in strong)
    max_seen = max(c.ratio for c in strong)
    return [
        AxiomPattern(
            name="hub_level_proxy_overstates_hourly_seam_spread",
            description=(
                "Annual or daily hub-level price proxies repeatedly overstated "
                "hourly settlement seam spreads. Future hub proxies require a "
                "settlement or nodal evidence 2-cell before being treated as "
                "actionable congestion value."
            ),
            template=(
                "hub_level_proxy(tie) and no_settlement_2cell(tie) "
                "-> screening_only(tie)"
            ),
            support=len(strong),
            agree_rate=1.0,
            avg_confidence=min(1.0, mean_ratio / 10.0),
            domains=["grid", "congestion_evidence"],
            example_episodes=[c.tie for c in strong[:5]],
        )
    ]


def build_proxy_warnings(
    legacy_rows: Sequence[Mapping[str, Any]],
    corrections: Sequence[EvidenceCorrectionCell],
) -> List[ProxyWarning]:
    corrected = {_tie_key(c.ba_a, c.ba_b) for c in corrections}
    warnings: List[ProxyWarning] = []
    for row in legacy_rows:
        if not _is_hub_proxy(row):
            continue
        key = _tie_key_from_row(row)
        if not key:
            continue
        status = "resolved_by_2cell" if key in corrected else "screening_only"
        warning = (
            "Hub-level proxy has a settlement correction 2-cell; keep the "
            "settlement row as the actionable value."
            if status == "resolved_by_2cell"
            else "Hub-level proxy has no settlement correction in this report; "
            "keep it as screening evidence only."
        )
        warnings.append(
            ProxyWarning(
                ba_a=key[0],
                ba_b=key[1],
                method=_method(row),
                spread_usd_mwh=_mean_price_spread(row),
                status=status,
                warning=warning,
            )
        )
    return warnings


def _load_rows(paths: Iterable[str | Path]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            continue
        if path.suffix.lower() == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                rows.extend(payload)
            elif "claims" in payload:
                rows.extend(payload.get("claims", []))
            elif "audits" in payload:
                rows.extend(payload.get("audits", []))
            elif "bottlenecks" in payload:
                rows.extend(payload.get("bottlenecks", []))
            else:
                rows.append(payload)
        else:
            with path.open(newline="", encoding="utf-8") as handle:
                rows.extend(dict(row) for row in csv.DictReader(handle))
    return rows


def _method(row: Mapping[str, Any]) -> str:
    method = str(row.get("evidence_method", "")).strip()
    if method:
        return method
    source = str(row.get("evidence_source", "")).lower()
    if "ice" in source or "hub" in source:
        return "hub_level_proxy"
    return "unspecified"


def _is_hub_proxy(row: Mapping[str, Any]) -> bool:
    method = _method(row).lower()
    source = str(row.get("evidence_source", "")).lower()
    return "hub" in method or "ice" in source or "wholesale prices" in source


def _mean_price_spread(row: Mapping[str, Any]) -> float:
    return _float(
        row.get("mean_price_spread_usd_mwh")
        or row.get("conservative_spread_usd_mwh")
        or row.get("daily_mean_abs_spread_usd_mwh")
    )


def _component_spread(row: Mapping[str, Any]) -> float:
    return _float(
        row.get("mean_congestion_component_spread_usd_mwh")
        or row.get("mean_congestion_spread_usd_mwh")
    )


def _tie_key_from_row(row: Mapping[str, Any]) -> tuple[str, str]:
    ba_a = str(
        row.get("ba_a")
        or row.get("source_ba")
        or row.get("from_ba")
        or row.get("ba1")
        or ""
    ).strip()
    ba_b = str(
        row.get("ba_b")
        or row.get("target_ba")
        or row.get("to_ba")
        or row.get("ba2")
        or ""
    ).strip()
    return _tie_key(ba_a, ba_b) if ba_a and ba_b else ("", "")


def _tie_key(ba_a: str, ba_b: str) -> tuple[str, str]:
    return tuple(sorted((ba_a.strip(), ba_b.strip())))


def _float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    text = str(value).strip().replace(",", "").replace("$", "")
    if not text or text.lower() == "nan":
        return 0.0
    try:
        out = float(text)
    except ValueError:
        return 0.0
    return 0.0 if math.isnan(out) else out


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.:-]+", "_", value).strip("_")


def _write_csv(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = _fieldnames(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _fieldnames(rows: List[Dict[str, Any]]) -> List[str]:
    if not rows:
        return ["status"]
    seen = {key for row in rows for key in row}
    preferred = [
        "ba_a",
        "ba_b",
        "source_method",
        "target_method",
        "method",
        "status",
        "source_spread_usd_mwh",
        "target_spread_usd_mwh",
        "target_component_spread_usd_mwh",
        "overstatement_ratio",
        "gross_mwh",
        "bound_spread_usd_mwh",
        "bound_value_usd",
        "source_value_usd",
        "target_value_usd",
        "avoided_overclaim_usd",
        "adjacent_measurements",
        "warning",
        "note",
    ]
    return [f for f in preferred if f in seen] + sorted(seen - set(preferred))
