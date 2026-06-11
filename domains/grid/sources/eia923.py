# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""EIA-923 generation loader.

EIA-923 is the primary source eGRID itself is built from, which makes
the eGRID/EIA-923 overlap the calibration check: large disagreement
there means a pipeline bug or a known adjustment (CHP, station use),
not new information.

Reads the annual "Schedules 2_3_4_5" workbook from
https://www.eia.gov/electricity/data/eia923/ -- sheet
"Page 1 Generation and Fuel Data", which has 5 preamble rows and one
row per plant x fuel x prime mover. We aggregate net generation to the
plant level so the section is comparable with eGRID's PLNGENAN.

Prefer PUDL's cleaned tables for production use; this loader exists so
the coherence check can run from the raw federal file with no
intermediary.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from domains.grid.sources.base import GridDataSource, PlantRecord

SHEET_NAME = "Page 1 Generation and Fuel Data"
PREAMBLE_ROWS = 5


def _norm(col: str) -> str:
    """Collapse the multi-line EIA-923 headers to lowercase words."""
    return re.sub(r"\s+", " ", str(col)).strip().lower()


class EIA923Source(GridDataSource):
    name = "eia923"

    def __init__(self, workbook_path: str | Path, year: int = 2023):
        self.workbook_path = Path(workbook_path)
        self.year = year

    def load(self) -> List[PlantRecord]:
        import pandas as pd

        df = pd.read_excel(
            self.workbook_path, sheet_name=SHEET_NAME, header=PREAMBLE_ROWS
        )
        df.columns = [_norm(c) for c in df.columns]

        col_id = "plant id"
        col_gen = next(
            (c for c in df.columns if c.startswith("net generation")), None
        )
        if col_id not in df.columns or col_gen is None:
            raise ValueError(
                f"EIA-923 sheet layout not recognized in {self.workbook_path}; "
                f"columns: {list(df.columns)[:10]}..."
            )
        col_state = "plant state" if "plant state" in df.columns else None
        col_ba = next((c for c in df.columns if "balancing authority cod" in c), None)
        col_name = "plant name" if "plant name" in df.columns else None

        df[col_gen] = pd.to_numeric(df[col_gen], errors="coerce")
        df = df.dropna(subset=[col_id])

        records: List[PlantRecord] = []
        for plant_id, group in df.groupby(col_id):
            first = group.iloc[0]
            total = group[col_gen].sum(min_count=1)
            records.append(
                PlantRecord(
                    plant_id=str(int(plant_id)),
                    name=str(first[col_name]) if col_name else "",
                    state=str(first[col_state]) if col_state else "",
                    balancing_authority=str(first[col_ba]) if col_ba else "",
                    net_generation_mwh=float(total) if pd.notna(total) else None,
                    year=self.year,
                    source=self.name,
                )
            )
        return records
