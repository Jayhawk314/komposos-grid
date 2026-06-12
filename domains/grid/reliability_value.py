# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Monetize EAGLE-I customer-hours with LBNL interruption costs.

Source coefficients: Sullivan, Schellenberg & Blundell, "Updated Value
of Service Reliability Estimates for Electric Utility Customers in the
United States" (LBNL, 2015; osti.gov/servlets/purl/1172643), expressed
as cost per unserved kWh for a one-hour interruption:

    residential        $3.30 / kWh
    small C&I          $295  / kWh   (small loads, huge per-kWh value)
    medium-large C&I   $21.80 / kWh

EAGLE-I counts interrupted *meters* of all classes. Converting
customer-hours to dollars therefore needs two assumption sets, both
explicit and overridable:

1. average class load (kW per metered customer) -- converts $/kWh to
   $/customer-hour;
2. meter mix -- the share of interrupted meters in each class.

Because these assumptions dominate the result, the report is a RANGE:

- **floor**: every interrupted meter valued as residential. The
  defensible minimum.
- **blended**: class mix applied. This is the scenario consistent
  with DOE/LBNL national interruption-cost studies (~$150B/yr scale).
- **high**: blended with the medium/large C&I load at the upper end.

This is a screening valuation, not damage accounting: it assumes
interruption costs scale linearly in duration (Sullivan's data is
per-event for 1 hour) and that outages hit meter classes
proportionally. Both caveats are printed with the result.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

from domains.grid.outages import OutageReport

# $/unserved kWh, Sullivan et al. 2015 (1-hour interruption)
USD_PER_KWH = {"residential": 3.30, "small_ci": 295.0, "medium_large_ci": 21.80}

# average load per metered customer, kW (EIA-861-derived screening values)
CLASS_LOAD_KW = {"residential": 1.25, "small_ci": 2.0, "medium_large_ci": 500.0}
CLASS_LOAD_KW_HIGH = {"residential": 1.25, "small_ci": 2.0, "medium_large_ci": 800.0}

# share of metered customers by class (EIA-861 screening values)
METER_MIX = {"residential": 0.866, "small_ci": 0.129, "medium_large_ci": 0.005}


def usd_per_customer_hour(
    usd_per_kwh: Dict[str, float] = USD_PER_KWH,
    class_load_kw: Dict[str, float] = CLASS_LOAD_KW,
    meter_mix: Dict[str, float] = METER_MIX,
) -> float:
    """Blended $ per interrupted customer-hour."""
    return sum(
        meter_mix[c] * usd_per_kwh[c] * class_load_kw[c] for c in meter_mix
    )


@dataclass
class ReliabilityValuation:
    year: int
    total_customer_hours: float
    floor_rate: float            # $/customer-hour, residential only
    blended_rate: float
    high_rate: float
    state_values_blended: Dict[str, float] = field(default_factory=dict)

    @property
    def floor_usd(self) -> float:
        return self.total_customer_hours * self.floor_rate

    @property
    def blended_usd(self) -> float:
        return self.total_customer_hours * self.blended_rate

    @property
    def high_usd(self) -> float:
        return self.total_customer_hours * self.high_rate

    def summary(self, top: int = 8) -> str:
        lines = [
            f"Reliability waste valuation {self.year} "
            f"({self.total_customer_hours/1e6:,.0f}M customer-hours):",
            f"  floor (all-residential, ${self.floor_rate:.2f}/cust-h): "
            f"${self.floor_usd/1e9:,.1f}B/yr",
            f"  blended (class mix, ${self.blended_rate:.2f}/cust-h): "
            f"${self.blended_usd/1e9:,.1f}B/yr",
            f"  high (large-C&I upper load, ${self.high_rate:.2f}/cust-h): "
            f"${self.high_usd/1e9:,.1f}B/yr",
            "  worst states at blended rate:",
        ]
        ranked = sorted(self.state_values_blended.items(), key=lambda kv: -kv[1])
        for state, usd in ranked[:top]:
            lines.append(f"    {state}: ${usd/1e9:,.2f}B/yr")
        lines.append(
            "  Screening valuation: Sullivan et al. 2015 LBNL coefficients, "
            "linear-in-duration, proportional meter mix. The blended figure "
            "is the scenario consistent with DOE national studies; the floor "
            "is the defensible minimum."
        )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "total_customer_hours": self.total_customer_hours,
            "rates_usd_per_customer_hour": {
                "floor": self.floor_rate,
                "blended": self.blended_rate,
                "high": self.high_rate,
            },
            "totals_usd": {
                "floor": self.floor_usd,
                "blended": self.blended_usd,
                "high": self.high_usd,
            },
            "state_values_blended_usd": self.state_values_blended,
            "source": (
                "Sullivan, Schellenberg & Blundell (LBNL 2015), Updated Value "
                "of Service Reliability Estimates; $/unserved kWh x class "
                "load x meter mix; screening assumptions documented in "
                "domains/grid/reliability_value.py"
            ),
        }

    def export_json(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(self.to_dict(), indent=1), encoding="utf-8"
        )


def value_outages(report: OutageReport) -> ReliabilityValuation:
    floor = USD_PER_KWH["residential"] * CLASS_LOAD_KW["residential"]
    blended = usd_per_customer_hour()
    high = usd_per_customer_hour(class_load_kw=CLASS_LOAD_KW_HIGH)
    return ReliabilityValuation(
        year=report.year,
        total_customer_hours=report.total_customer_hours(),
        floor_rate=floor,
        blended_rate=blended,
        high_rate=high,
        state_values_blended={
            state: ch * blended
            for state, ch in report.state_customer_hours.items()
        },
    )
