# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Same-year tie-flow evidence from EIA-930 INTERCHANGE files.

Closes the `needs_same_year_flow` gate in the solution studies: extracts
gross/net annual flow for specific BA pairs from the same year as the
price evidence, using the identical aggregation as the 2023 baseline
(flow_geometry.load_interchange: sum of |hourly flow|, one reporter per
pair) so values stay comparable across years.

Output rows are in the exact format `solution_studies.load_same_year_flow_csv`
consumes (geography, ba_a, ba_b, year, gross_mwh, net_mwh, source, notes).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List, Sequence

from domains.grid.flow_geometry import load_interchange
from domains.grid.solution_studies import SameYearFlowEvidence


def _tie_key(ba_a: str, ba_b: str) -> tuple[str, str]:
    return tuple(sorted((ba_a.strip().upper(), ba_b.strip().upper())))


def extract_same_year_flows(
    csv_paths: Iterable[str | Path],
    pairs: Sequence[str],
    year: int,
    source: str = "EIA-930 INTERCHANGE six-month files",
) -> List[SameYearFlowEvidence]:
    """Aggregate the year's interchange files and keep the requested pairs.

    `pairs` are "BAA-BAB" strings (order-insensitive). Raises if a
    requested pair has no flow in the files -- silence here would let a
    typo masquerade as missing evidence.
    """
    wanted = {_tie_key(*p.split("-", 1)): p for p in pairs}
    ties = load_interchange(csv_paths)
    found: List[SameYearFlowEvidence] = []
    for tie in ties:
        key = _tie_key(tie.ba_a, tie.ba_b)
        if key not in wanted:
            continue
        found.append(
            SameYearFlowEvidence(
                geography=f"{key[0]}-{key[1]}",
                ba_a=key[0],
                ba_b=key[1],
                year=year,
                gross_mwh=tie.gross_mwh,
                net_mwh=tie.net_mwh,
                source=source,
                notes=f"sum |hourly Interchange (MW)| over {year} files; "
                      "same aggregation as 2023 baseline",
            )
        )
    found_keys = {_tie_key(e.ba_a, e.ba_b) for e in found}
    missing = [p for key, p in wanted.items() if key not in found_keys]
    if missing:
        raise ValueError(f"pairs not found in interchange files: {sorted(missing)}")
    return found


def write_same_year_flow_csv(
    flows: Sequence[SameYearFlowEvidence], path: str | Path, append: bool = False
) -> None:
    """Write (or append to) a CSV consumable by --same-year-flow."""
    path = Path(path)
    fields = ["geography", "ba_a", "ba_b", "year",
              "gross_mwh", "net_mwh", "source", "notes"]
    exists = path.exists() and path.stat().st_size > 0
    mode = "a" if append and exists else "w"
    with path.open(mode, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        if mode == "w":
            writer.writeheader()
        for flow in flows:
            writer.writerow(flow.to_row())
