# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Curtailment waste quantification from CAISO published data.

CAISO's production-and-curtailments workbook (caiso.com, keyless)
reports 5-minute wind/solar curtailment in MW with a *reason* code:

- ``Local``  -- congestion-driven: the energy existed, the wires
  couldn't carry it (T&D-losses waste class).
- ``System`` -- oversupply: the grid couldn't absorb it at all
  (curtailment waste class; the storage/flexibility target).

Energy per 5-minute interval is MW / 12 MWh. Production sheet gives
the realized Solar/Wind output, so curtailment share = curtailed /
(curtailed + produced) -- the fraction of available renewable energy
thrown away.

Valuation is reported as a band, not a number: curtailed energy is
worth less than the annual average price (it occurs in low-price
hours), so the average-price figure is an upper bound and is labeled
as such.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

MWH_PER_INTERVAL = 1.0 / 12.0  # 5-minute MW reading -> MWh


@dataclass
class CurtailmentReport:
    year: int
    ba: str
    curtailed_mwh: Dict[str, Dict[str, float]]  # fuel -> reason -> MWh
    produced_mwh: Dict[str, float]              # fuel -> MWh realized
    avg_price_usd_mwh: Optional[float] = None

    def total(self, fuel: Optional[str] = None) -> float:
        fuels = [fuel] if fuel else list(self.curtailed_mwh)
        return sum(
            v for f in fuels for v in self.curtailed_mwh.get(f, {}).values()
        )

    def by_reason(self, reason: str) -> float:
        return sum(
            reasons.get(reason, 0.0) for reasons in self.curtailed_mwh.values()
        )

    def share(self, fuel: str) -> float:
        """Curtailed fraction of available (curtailed + produced) energy."""
        curtailed = self.total(fuel)
        produced = self.produced_mwh.get(fuel, 0.0)
        avail = curtailed + produced
        return curtailed / avail if avail else 0.0

    def summary(self) -> str:
        lines = [
            f"Curtailment report {self.ba} {self.year}: "
            f"{self.total()/1e6:.2f} TWh renewable energy curtailed"
        ]
        for fuel, reasons in sorted(self.curtailed_mwh.items()):
            parts = ", ".join(
                f"{r.lower()} {v/1e6:.2f} TWh" for r, v in sorted(reasons.items())
            )
            lines.append(
                f"  {fuel}: {self.total(fuel)/1e6:.2f} TWh ({parts}) "
                f"-- {self.share(fuel):.1%} of available {fuel}"
            )
        all_reasons = sorted({
            r for reasons in self.curtailed_mwh.values() for r in reasons
        })
        congestion = {"Local", "Redispatch"}
        oversupply = {"System", "Energy"}
        lines.append(
            "  by reason: "
            + "; ".join(
                f"{r}{' (congestion)' if r in congestion else ''}"
                f"{' (oversupply)' if r in oversupply else ''} "
                f"{self.by_reason(r)/1e6:.2f} TWh"
                for r in all_reasons
            )
        )
        if self.avg_price_usd_mwh:
            upper = self.total() * self.avg_price_usd_mwh
            lines.append(
                f"  value at annual avg ${self.avg_price_usd_mwh:.2f}/MWh: "
                f"<= ${upper/1e6:,.0f}M (upper bound: curtailment clusters "
                f"in low-price hours)"
            )
        return "\n".join(lines)


def aggregate_curtailments(
    curtailments,
    production,
    year: int = 2023,
    ba: str = "CISO",
    avg_price_usd_mwh: Optional[float] = None,
) -> CurtailmentReport:
    """Aggregate CAISO-format DataFrames into a CurtailmentReport.

    ``curtailments``: columns Date/Hour/Interval, '<Fuel> Curtailment'
    (MW per 5-min interval), Reason. ``production``: columns include
    Solar/Wind MW per 5-min interval.
    """
    curtailed: Dict[str, Dict[str, float]] = {}
    fuel_cols = [
        c for c in curtailments.columns if c.endswith(" Curtailment")
    ]
    for col in fuel_cols:
        fuel = col.replace(" Curtailment", "").lower()
        grouped = (
            curtailments.groupby("Reason")[col].sum() * MWH_PER_INTERVAL
        )
        curtailed[fuel] = {
            str(reason): float(v) for reason, v in grouped.items() if v > 0
        }

    produced = {}
    for fuel in ("Solar", "Wind"):
        if fuel in production.columns:
            produced[fuel.lower()] = float(
                production[fuel].sum() * MWH_PER_INTERVAL
            )

    return CurtailmentReport(
        year=year,
        ba=ba,
        curtailed_mwh=curtailed,
        produced_mwh=produced,
        avg_price_usd_mwh=avg_price_usd_mwh,
    )


def load_caiso_report(
    workbook_path: str | Path,
    year: int = 2023,
    avg_price_usd_mwh: Optional[float] = None,
) -> CurtailmentReport:
    import pandas as pd

    xl = pd.ExcelFile(workbook_path)
    return aggregate_curtailments(
        xl.parse("Curtailments"),
        xl.parse("Production"),
        year=year,
        avg_price_usd_mwh=avg_price_usd_mwh,
    )


def write_to_category(category, report: CurtailmentReport) -> None:
    """Curtailment as structure: fuel -curtailed_in-> ba, confidence =
    retained fraction (1 - curtailment share), volumes in metadata."""
    ba_obj = f"ba:{report.ba}"
    if category.get(ba_obj) is None:
        category.add(ba_obj, type_name="balancing_authority")
    for fuel, reasons in report.curtailed_mwh.items():
        fuel_obj = f"fuel:{fuel}"
        if category.get(fuel_obj) is None:
            category.add(fuel_obj, type_name="fuel")
        category.connect(
            fuel_obj,
            ba_obj,
            name="curtailed_in",
            confidence=max(1.0 - report.share(fuel), 1e-6),
            curtailed_mwh=report.total(fuel),
            year=report.year,
            **{f"reason_{r.lower()}_mwh": v for r, v in reasons.items()},
        )
