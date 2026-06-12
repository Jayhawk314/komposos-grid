# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""MISO day-ahead binding constraints: constraint-level congestion structure.

Files (docs.misoenergy.org/marketreports, keyless, .xls needing xlrd):

- ``<yyyymmdd>_da_bc.xls``   -- one row per (constraint, hour) binding
  event with the shadow price ($/MWh). Publish date in the filename;
  the *market date* inside the file is the next day -- we key by the
  embedded market date.
- ``<yyyymmdd>_da_bcsf.xls`` -- the constraint catalog (topology):
  Constraint ID -> From Area / To Area control areas. Near-static, so
  one catalog per analysis window suffices.

What this yields, honestly: MISO does not publish constrained flow MW,
so shadow-price x hours is a **severity index** (the $/MWh-hours of
binding pressure per constraint), not congestion dollars. Severity
ranks the physical constraints that drive the seam spreads measured in
sources/miso.py; converting to dollars awaits constraint flows (market
monitor data) or FTR settlement totals. PLAN A2 keyless half.
"""

from __future__ import annotations

import time
import urllib.request
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

BC_URL = "https://docs.misoenergy.org/marketreports/{day:%Y%m%d}_da_bc.xls"
BCSF_URL = "https://docs.misoenergy.org/marketreports/{day:%Y%m%d}_da_bcsf.xls"
POLITE_DELAY_S = 0.3


def _download(url: str, dest: Path) -> None:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (komposos-grid-domain)"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())
    time.sleep(POLITE_DELAY_S)


def _frame_below_header(raw, header_marker: str):
    """MISO xls: banner rows, then the real header row containing the
    marker; return a DataFrame with that row as columns."""
    for idx in range(min(6, len(raw))):
        row = [str(v).strip() for v in raw.iloc[idx].tolist()]
        if header_marker in row:
            df = raw.iloc[idx + 1:].copy()
            df.columns = row
            return df.reset_index(drop=True)
    raise ValueError(f"header row with {header_marker!r} not found")


def fetch_bc_day(day: date, cache_dir: str | Path):
    """Binding events for one publish day: columns constraint_id,
    constraint_name, hour, shadow_price; keyed to the market date."""
    import pandas as pd

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"{day:%Y%m%d}_da_bc.xls"
    if not cached.exists():
        _download(BC_URL.format(day=day), cached)

    raw = pd.read_excel(cached, header=None)
    market_date = str(raw.iloc[0, 0]).split(":", 1)[-1].strip()
    df = _frame_below_header(raw, "Constraint_ID")
    out = pd.DataFrame({
        "market_date": market_date,
        "constraint_id": pd.to_numeric(df["Constraint_ID"], errors="coerce"),
        "constraint_name": df["Constraint Name"].astype(str).str.strip(),
        "hour": pd.to_numeric(df["Hour of Occurrence"], errors="coerce"),
        "shadow_price": pd.to_numeric(df["Shadow Price"], errors="coerce"),
    })
    return out.dropna(subset=["constraint_id", "shadow_price"])


def fetch_catalog(day: date, cache_dir: str | Path) -> Dict[int, Tuple[str, str]]:
    """constraint_id -> (from_area, to_area) from the supplemental file."""
    import pandas as pd

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"{day:%Y%m%d}_da_bcsf.xls"
    if not cached.exists():
        _download(BCSF_URL.format(day=day), cached)

    raw = pd.read_excel(cached, header=None)
    df = _frame_below_header(raw, "Constraint ID")
    df["constraint_id"] = pd.to_numeric(df["Constraint ID"], errors="coerce")
    df = df.dropna(subset=["constraint_id"])
    catalog: Dict[int, Tuple[str, str]] = {}
    for _, row in df.iterrows():
        cid = int(row["constraint_id"])
        if cid not in catalog:
            catalog[cid] = (
                str(row.get("From Area", "")).strip(),
                str(row.get("To Area", "")).strip(),
            )
    return catalog


@dataclass
class ConstraintSeverity:
    constraint_id: int
    constraint_name: str
    from_area: str
    to_area: str
    binding_hours: int
    severity: float        # sum |shadow price| over binding hours, $/MWh*h
    mean_abs_sp: float
    max_abs_sp: float


@dataclass
class ConstraintReport:
    start: str
    end: str
    days_fetched: int
    days_missing: int
    constraints: List[ConstraintSeverity] = field(default_factory=list)

    @property
    def total_severity(self) -> float:
        return sum(c.severity for c in self.constraints)

    def area_pairs(self) -> List[Tuple[str, float]]:
        pairs: Dict[str, float] = {}
        for c in self.constraints:
            key = f"{c.from_area}->{c.to_area}" if c.from_area else "unmapped"
            pairs[key] = pairs.get(key, 0.0) + c.severity
        return sorted(pairs.items(), key=lambda kv: -kv[1])

    def summary(self, top: int = 10) -> str:
        lines = [
            f"MISO DA binding constraints [{self.start}..{self.end}] "
            f"({self.days_fetched} days, {self.days_missing} missing): "
            f"{len(self.constraints)} constraints, total severity "
            f"{self.total_severity:,.0f} $/MWh-hours",
            "  NOTE: severity index, not dollars -- constrained flow MW "
            "is not public; ranking tracks congestion cost ordering.",
            "  top constraints:",
        ]
        ranked = sorted(self.constraints, key=lambda c: -c.severity)
        for c in ranked[:top]:
            lines.append(
                f"    {c.constraint_name} [{c.from_area}->{c.to_area}]: "
                f"{c.binding_hours} binding hours, severity {c.severity:,.0f}, "
                f"max |SP| ${c.max_abs_sp:,.0f}/MWh"
            )
        lines.append("  severity by control-area pair (top 8):")
        for pair, sev in self.area_pairs()[:8]:
            lines.append(f"    {pair}: {sev:,.0f}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
            "days_fetched": self.days_fetched,
            "days_missing": self.days_missing,
            "total_severity_sp_hours": self.total_severity,
            "constraints": [vars(c) for c in
                            sorted(self.constraints, key=lambda c: -c.severity)],
            "area_pairs": self.area_pairs(),
        }


def aggregate_constraints(
    frames,
    catalog: Optional[Dict[int, Tuple[str, str]]] = None,
) -> List[ConstraintSeverity]:
    import pandas as pd

    df = pd.concat(frames, ignore_index=True)
    df["abs_sp"] = df["shadow_price"].abs()
    grouped = df.groupby(["constraint_id", "constraint_name"]).agg(
        binding_hours=("abs_sp", "size"),
        severity=("abs_sp", "sum"),
        mean_abs_sp=("abs_sp", "mean"),
        max_abs_sp=("abs_sp", "max"),
    )
    catalog = catalog or {}
    out = []
    for (cid, name), row in grouped.iterrows():
        from_area, to_area = catalog.get(int(cid), ("", ""))
        out.append(
            ConstraintSeverity(
                constraint_id=int(cid),
                constraint_name=str(name),
                from_area=from_area,
                to_area=to_area,
                binding_hours=int(row["binding_hours"]),
                severity=float(row["severity"]),
                mean_abs_sp=float(row["mean_abs_sp"]),
                max_abs_sp=float(row["max_abs_sp"]),
            )
        )
    return out


def fetch_constraint_report(
    start: date,
    end: date,
    cache_dir: str | Path,
) -> ConstraintReport:
    frames = []
    missing = 0
    cursor = start
    while cursor < end:
        try:
            frames.append(fetch_bc_day(cursor, cache_dir))
        except Exception:
            missing += 1
        cursor += timedelta(days=1)
    catalog = fetch_catalog(start, cache_dir)
    constraints = aggregate_constraints(frames, catalog)
    return ConstraintReport(
        start=start.isoformat(),
        end=(end - timedelta(days=1)).isoformat(),
        days_fetched=(end - start).days - missing,
        days_missing=missing,
        constraints=constraints,
    )
