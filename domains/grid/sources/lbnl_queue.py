# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""LBNL "Queued Up" interconnection queue loader.

Dataset: https://emp.lbl.gov/queues -- project-level interconnection
requests from 50+ grid operators (~98% of US capacity), with outcome
status. NOTE: the file download is protected by a browser challenge,
so it must be fetched manually (a browser visit to the publication
page) and saved under domains/grid/data/.

Each project is a morphism  proposed -> {operational | withdrawn}:
the ~13% completion / ~77% withdrawal split for 2000-2019 entrants is
the single largest documented inefficiency in the US grid pipeline.

The loader is defensive about column naming across vintages: the
codebook names (q_id, q_status, type_clean, mw1, ...) are matched
with aliases after whitespace/case normalization.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# canonical field -> acceptable column aliases (normalized lowercase)
ALIASES = {
    "q_id": ["q_id", "queue_id", "qid"],
    "q_status": ["q_status", "queue_status", "status"],
    "q_year": ["q_year", "queue_year", "year_entered"],
    "fuel": ["type_clean", "resource_type", "type1", "fuel"],
    "region": ["region", "iso_region", "ba", "entity"],
    "state": ["state", "state_1", "state1"],
    "mw": ["mw1", "mw_1", "capacity_mw", "mw"],
    "ia_status": ["ia_status", "ia_status_clean", "ia_phase_clean",
                  "interconnection_agreement"],
}

OPERATIONAL = "operational"
WITHDRAWN = "withdrawn"
ACTIVE = "active"
SUSPENDED = "suspended"


@dataclass
class QueueProject:
    q_id: str
    status: str          # operational | withdrawn | active | suspended
    q_year: Optional[int]
    fuel: str
    region: str
    state: str
    mw: Optional[float]
    ia_status: str = ""

    @property
    def decided(self) -> bool:
        return self.status in (OPERATIONAL, WITHDRAWN)


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(s).strip().lower()).strip("_")


def _norm_status(raw: str) -> str:
    s = _norm(raw)
    if "operation" in s or s in ("commercial", "in_service", "online"):
        return OPERATIONAL
    if "withdraw" in s or s in ("cancelled", "canceled"):
        return WITHDRAWN
    if "suspend" in s:
        return SUSPENDED
    return ACTIVE


class LBNLQueueSource:
    name = "lbnl_queue"

    def __init__(self, workbook_path: str | Path, sheet: Optional[str] = None):
        self.workbook_path = Path(workbook_path)
        self.sheet = sheet

    def _find_sheet(self, xl) -> tuple:
        """Return (sheet_name, header_row): the header may sit under
        banner rows like 'RETURN TO CONTENTS'."""
        candidates = [self.sheet] if self.sheet else xl.sheet_names
        for name in candidates:
            head = xl.parse(name, nrows=4, header=None)
            for row_idx in range(len(head)):
                cells = {_norm(v) for v in head.iloc[row_idx].tolist()}
                if any(a in cells for a in ALIASES["q_status"]):
                    return name, row_idx
        raise ValueError(
            f"No sheet with a q_status-like column in {self.workbook_path}; "
            f"sheets: {xl.sheet_names}"
        )

    def load(self) -> List[QueueProject]:
        import pandas as pd

        xl = pd.ExcelFile(self.workbook_path)
        sheet, header_row = self._find_sheet(xl)
        df = xl.parse(sheet, header=header_row)
        cols = {_norm(c): c for c in df.columns}

        def col(field: str) -> Optional[str]:
            for alias in ALIASES[field]:
                if alias in cols:
                    return cols[alias]
            return None

        c_status = col("q_status")
        if c_status is None:
            raise ValueError(f"q_status column not found in {list(cols)[:15]}")

        projects: List[QueueProject] = []
        for idx, row in df.iterrows():
            def get(field, default=""):
                c = col(field)
                v = row[c] if c is not None else None
                return default if v is None or (isinstance(v, float) and v != v) else v

            year = get("q_year", None)
            mw = get("mw", None)
            projects.append(
                QueueProject(
                    q_id=str(get("q_id", idx)),
                    status=_norm_status(get("q_status")),
                    q_year=int(year) if year not in (None, "") else None,
                    fuel=_norm(get("fuel", "unknown")) or "unknown",
                    region=_norm(get("region", "unknown")) or "unknown",
                    state=str(get("state", "")),
                    mw=float(mw) if mw not in (None, "") else None,
                    ia_status=_norm(get("ia_status", "")),
                )
            )
        return projects
