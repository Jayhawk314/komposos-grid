# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Reliability waste from EAGLE-I county outage data (ORNL).

EAGLE-I records customers-without-power per county at 15-minute
intervals (~92% of US customers). One row of `sum` customers out for
one interval is sum * 0.25 customer-hours of lost service. Aggregated
to states and normalized by the modeled county customer (MCC)
denominators, this yields a SAIDI-like figure -- average hours of
outage per customer per year -- computed identically across all
states, which utility-reported SAIDI is not.

The yearly file is ~1.1 GB, so aggregation is chunked; nothing but
the state rollup is held in memory.

Join to the rest of the grid domain: states are already objects in
the coherence Category (plant -in_state-> state), so outage burden
becomes a hom-value (state -outage_burden-> grid:reliability with
confidence = relative service retention), comparable against the
flow-geometry bottlenecks' endpoint regions.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

CUSTOMER_HOURS_PER_ROW = 0.25  # 15-minute interval

# State FIPS -> the state names used in the EAGLE-I outage files
STATE_FIPS = {
    1: "Alabama", 2: "Alaska", 4: "Arizona", 5: "Arkansas", 6: "California",
    8: "Colorado", 9: "Connecticut", 10: "Delaware", 11: "District of Columbia",
    12: "Florida", 13: "Georgia", 15: "Hawaii", 16: "Idaho", 17: "Illinois",
    18: "Indiana", 19: "Iowa", 20: "Kansas", 21: "Kentucky", 22: "Louisiana",
    23: "Maine", 24: "Maryland", 25: "Massachusetts", 26: "Michigan",
    27: "Minnesota", 28: "Mississippi", 29: "Missouri", 30: "Montana",
    31: "Nebraska", 32: "Nevada", 33: "New Hampshire", 34: "New Jersey",
    35: "New Mexico", 36: "New York", 37: "North Carolina", 38: "North Dakota",
    39: "Ohio", 40: "Oklahoma", 41: "Oregon", 42: "Pennsylvania",
    44: "Rhode Island", 45: "South Carolina", 46: "South Dakota",
    47: "Tennessee", 48: "Texas", 49: "Utah", 50: "Vermont", 51: "Virginia",
    53: "Washington", 54: "West Virginia", 55: "Wisconsin", 56: "Wyoming",
    60: "American Samoa", 66: "Guam", 69: "Northern Mariana Islands",
    72: "Puerto Rico", 78: "United States Virgin Islands",
}


@dataclass
class OutageReport:
    year: int
    state_customer_hours: Dict[str, float]
    state_customers: Dict[str, float]      # MCC denominators
    coverage_note: str = "EAGLE-I covers ~92% of US customers"
    rows_processed: int = 0
    first_timestamp: str = ""
    last_timestamp: str = ""

    def hours_per_customer(self, state: str) -> Optional[float]:
        ch = self.state_customer_hours.get(state)
        n = self.state_customers.get(state)
        if ch is None or not n:
            return None
        return ch / n

    def ranked(self):
        rows = []
        for state, ch in self.state_customer_hours.items():
            hpc = self.hours_per_customer(state)
            if hpc is not None:
                rows.append((state, ch, hpc))
        rows.sort(key=lambda r: -r[2])
        return rows

    def total_customer_hours(self) -> float:
        return sum(self.state_customer_hours.values())

    def total_customers(self) -> float:
        return sum(self.state_customers.values())

    def to_rows(self, top: int | None = None) -> List[Dict[str, Any]]:
        ranked = self.ranked()
        if top is not None:
            ranked = ranked[:top]
        total_hours = self.total_customer_hours()
        rows = []
        for rank, (state, customer_hours, hours_per_customer) in enumerate(ranked, 1):
            customers = self.state_customers.get(state, 0.0)
            rows.append({
                "rank": rank,
                "state": state,
                "customer_hours": customer_hours,
                "customers": customers,
                "hours_per_customer": hours_per_customer,
                "customer_hours_share": (
                    customer_hours / total_hours if total_hours > 0 else 0.0
                ),
            })
        return rows

    def summary(self, top: int = 10) -> str:
        lines = [
            f"EAGLE-I outage report {self.year}: "
            f"{self.total_customer_hours()/1e6:,.0f}M customer-hours lost "
            f"({self.coverage_note})",
            f"  rows processed: {self.rows_processed:,}; "
            f"time range: {self.first_timestamp or '?'} -> "
            f"{self.last_timestamp or '?'}",
            "  worst states (hours per customer per year):",
        ]
        for state, ch, hpc in self.ranked()[:top]:
            lines.append(
                f"    {state}: {hpc:.1f} h/customer ({ch/1e6:,.1f}M customer-hours)"
            )
        return "\n".join(lines)

    def to_dict(self, top: int = 56) -> Dict[str, Any]:
        return {
            "year": self.year,
            "coverage_note": self.coverage_note,
            "rows_processed": self.rows_processed,
            "first_timestamp": self.first_timestamp,
            "last_timestamp": self.last_timestamp,
            "total_customer_hours": self.total_customer_hours(),
            "total_customers": self.total_customers(),
            "states": self.to_rows(top=top),
        }

    def to_markdown(self, top: int = 25) -> str:
        lines = [
            f"# EAGLE-I Reliability Waste Report {self.year}",
            "",
            "## Result",
            "",
            f"- Customer-hours lost: **{self.total_customer_hours()/1e6:,.0f}M**",
            f"- Rows processed: **{self.rows_processed:,}**",
            f"- Time range: **{self.first_timestamp or '?'} -> "
            f"{self.last_timestamp or '?'}**",
            f"- Coverage: **{self.coverage_note}**",
            "",
            "## Worst States",
            "",
            "| Rank | State | Hours/Customer | Customer-Hours | Customers | Share |",
            "|---:|---|---:|---:|---:|---:|",
        ]
        for row in self.to_rows(top=top):
            lines.append(
                f"| {row['rank']} | {row['state']} | "
                f"{row['hours_per_customer']:.1f} | "
                f"{row['customer_hours']:,.0f} | {row['customers']:,.0f} | "
                f"{row['customer_hours_share']:.1%} |"
            )
        return "\n".join(lines) + "\n"

    def to_html(
        self,
        title: str | None = None,
        top: int = 25,
    ) -> str:
        title = title or f"EAGLE-I Reliability Waste Dashboard {self.year}"
        metrics = [
            _metric(
                "Customer-hours lost",
                f"{self.total_customer_hours()/1e6:,.0f}M",
                self.coverage_note,
            ),
            _metric("Rows processed", f"{self.rows_processed:,}", "chunked CSV aggregation"),
            _metric(
                "Time range",
                f"{self.first_timestamp or '?'} to {self.last_timestamp or '?'}",
                "source timestamps observed",
            ),
            _metric("States ranked", str(len(self.ranked())), "normalized by MCC customers"),
        ]
        rows = [
            [
                row["rank"],
                row["state"],
                f"{row['hours_per_customer']:.1f}",
                f"{row['customer_hours']:,.0f}",
                f"{row['customers']:,.0f}",
                f"{row['customer_hours_share']:.1%}",
            ]
            for row in self.to_rows(top=top)
        ]
        body = [
            '<section class="band summary">'
            "<h2>Reliability waste from outage customer-hours</h2>"
            '<div class="chips">'
            f'<span class="chip">{escape(self.coverage_note)}</span>'
            f'<span class="chip">{escape(str(len(self.ranked())))} states ranked</span>'
            "</div>"
            "</section>",
            '<section class="metrics">' + "".join(metrics) + "</section>",
            _section(
                "Worst States",
                _table(
                    [
                        "Rank",
                        "State",
                        "Hours/Customer",
                        "Customer-Hours",
                        "Customers",
                        "Share",
                    ],
                    rows,
                    "No outage rows available.",
                ),
            ),
        ]
        return _page(title, "EAGLE-I outage burden normalized by MCC customers", body)

    def export_csv(self, path: str | Path, top: int | None = None) -> None:
        _write_csv(path, self.to_rows(top=top))

    def export_markdown(self, path: str | Path, top: int = 25) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(top=top), encoding="utf-8")

    def export_json(self, path: str | Path, top: int = 56) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(top=top), indent=2), encoding="utf-8")

    def export_html(
        self,
        path: str | Path,
        title: str | None = None,
        top: int = 25,
    ) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_html(title=title, top=top), encoding="utf-8")


def load_mcc(path: str | Path) -> Dict[str, float]:
    """State name -> modeled customer count.

    MCC.csv is county-keyed (County_FIPS, Customers); the state is the
    leading FIPS component (county_fips // 1000)."""
    import pandas as pd

    df = pd.read_csv(path)
    cols = {c.lower().strip(): c for c in df.columns}
    fips_col = next(cols[k] for k in cols if "fips" in k)
    cust_col = next(cols[k] for k in cols if "customer" in k)
    df["_state"] = (
        pd.to_numeric(df[fips_col], errors="coerce") // 1000
    ).map(STATE_FIPS)
    grouped = df.dropna(subset=["_state"]).groupby("_state")[cust_col].sum()
    return {str(s): float(v) for s, v in grouped.items()}


def aggregate_outages(
    csv_path: str | Path,
    mcc: Dict[str, float],
    year: int = 2023,
    chunksize: int = 2_000_000,
) -> OutageReport:
    import pandas as pd

    state_hours: Dict[str, float] = {}
    rows_processed = 0
    first_timestamp = ""
    last_timestamp = ""
    for chunk in pd.read_csv(
        csv_path,
        usecols=["state", "sum", "run_start_time"],
        dtype={"state": "category", "sum": "float64", "run_start_time": "string"},
        chunksize=chunksize,
    ):
        rows_processed += len(chunk)
        ts = chunk["run_start_time"].dropna()
        if not ts.empty:
            chunk_min = str(ts.min())
            chunk_max = str(ts.max())
            first_timestamp = min(first_timestamp, chunk_min) if first_timestamp else chunk_min
            last_timestamp = max(last_timestamp, chunk_max) if last_timestamp else chunk_max
        grouped = chunk.groupby("state", observed=True)["sum"].sum()
        for state, total in grouped.items():
            state_hours[str(state)] = (
                state_hours.get(str(state), 0.0)
                + float(total) * CUSTOMER_HOURS_PER_ROW
            )

    return OutageReport(
        year=year,
        state_customer_hours=state_hours,
        state_customers=mcc,
        rows_processed=rows_processed,
        first_timestamp=first_timestamp,
        last_timestamp=last_timestamp,
    )


def write_to_category(category, report: OutageReport) -> None:
    """Outage burden as hom-values: confidence = relative retention
    (1 - hours_per_customer / worst observed), so the worst state has
    the lowest hom-value into grid:reliability."""
    target = "grid:reliability"
    if category.get(target) is None:
        category.add(target, type_name="quality")
    ranked = report.ranked()
    if not ranked:
        return
    worst = ranked[0][2]
    for state, ch, hpc in ranked:
        obj = f"state:{state}"
        if category.get(obj) is None:
            category.add(obj, type_name="state")
        category.connect(
            obj,
            target,
            name="outage_burden",
            confidence=max(1.0 - (hpc / worst if worst else 0.0), 1e-6),
            customer_hours=ch,
            hours_per_customer=hpc,
            year=report.year,
        )


def _write_csv(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = _fields(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _fields(rows: List[Dict[str, Any]]) -> List[str]:
    preferred = [
        "rank",
        "state",
        "customer_hours",
        "customers",
        "hours_per_customer",
        "customer_hours_share",
    ]
    seen = {field for row in rows for field in row}
    return [field for field in preferred if field in seen] + sorted(seen - set(preferred))


def _page(title: str, subtitle: str, sections: Iterable[str]) -> str:
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"  <title>{escape(title)}</title>\n"
        f"  <style>{_CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        '  <main class="shell">\n'
        "    <header>\n"
        f"      <h1>{escape(title)}</h1>\n"
        f"      <p>{escape(subtitle)}</p>\n"
        "    </header>\n"
        f"    {''.join(sections)}\n"
        "  </main>\n"
        "</body>\n"
        "</html>\n"
    )


def _metric(label: str, value: str, detail: str) -> str:
    return (
        '<article class="metric">'
        f"<span>{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        f"<small>{escape(detail)}</small>"
        "</article>"
    )


def _section(title: str, content: str) -> str:
    return (
        '<section class="band">'
        f"<h2>{escape(title)}</h2>"
        f"{content}"
        "</section>"
    )


def _table(headers: Sequence[str], rows: Sequence[Sequence[Any]], empty: str) -> str:
    if not rows:
        return f'<p class="empty">{escape(empty)}</p>'
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body = []
    for row in rows:
        body.append(
            "<tr>"
            + "".join(f"<td>{escape(str(cell))}</td>" for cell in row)
            + "</tr>"
        )
    return (
        '<div class="table-wrap">'
        "<table>"
        f"<thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body)}</tbody>"
        "</table>"
        "</div>"
    )


_CSS = """
:root {
  color-scheme: light;
  --ink: #17202a;
  --muted: #5b6673;
  --line: #d8dee6;
  --surface: #ffffff;
  --page: #f5f7fa;
  --blue: #1f6feb;
  --green: #1f8f5f;
  --amber: #b7791f;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--page);
  color: var(--ink);
  font: 14px/1.5 Arial, Helvetica, sans-serif;
}
.shell {
  width: min(1180px, calc(100vw - 32px));
  margin: 0 auto;
  padding: 28px 0 40px;
}
header {
  border-bottom: 1px solid var(--line);
  margin-bottom: 18px;
  padding-bottom: 16px;
}
h1 {
  font-size: clamp(26px, 4vw, 38px);
  line-height: 1.1;
  margin: 0 0 8px;
  letter-spacing: 0;
}
h2 {
  font-size: 18px;
  line-height: 1.25;
  margin: 0 0 14px;
  letter-spacing: 0;
}
p { margin: 0; color: var(--muted); }
.band {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  margin: 16px 0;
  padding: 18px;
}
.summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.summary h2 { margin: 0; }
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chip {
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #fbfcfe;
  padding: 6px 10px;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 12px;
  margin: 16px 0;
}
.metric {
  min-height: 128px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-top: 4px solid var(--blue);
  border-radius: 8px;
  padding: 14px;
  display: grid;
  gap: 6px;
  align-content: start;
}
.metric:nth-child(2n) { border-top-color: var(--green); }
.metric:nth-child(3n) { border-top-color: var(--amber); }
.metric span {
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
}
.metric strong {
  font-size: 24px;
  line-height: 1.05;
  letter-spacing: 0;
}
.metric small { color: var(--muted); }
.table-wrap { overflow-x: auto; }
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
}
th, td {
  border-bottom: 1px solid var(--line);
  padding: 9px 10px;
  text-align: left;
  vertical-align: top;
}
th {
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  background: #fbfcfe;
}
tr:hover td { background: #f9fbfd; }
.empty {
  border: 1px dashed var(--line);
  border-radius: 8px;
  padding: 14px;
}
@media (max-width: 640px) {
  .shell { width: min(100vw - 20px, 1180px); padding-top: 18px; }
  .band { padding: 14px; }
  .metric { min-height: 116px; }
  .metric strong { font-size: 21px; }
}
"""
