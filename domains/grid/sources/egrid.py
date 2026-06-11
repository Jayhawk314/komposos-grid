# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""eGRID (US EPA) plant-level loader.

eGRID ships as an Excel workbook with one sheet per aggregation level.
The plant sheet ("PLNT23" for data year 2023) has two header rows:
row 0 is the human-readable description, row 1 holds the column codes
(ORISPL, PNAME, PLNGENAN, ...). We read with header=1.

Download manually from https://www.epa.gov/egrid/detailed-data and pass
the workbook path. eGRID2023rev2 was current as of mid-2025; eGRID2024
is slated for January 2026.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from domains.grid.sources.base import GridDataSource, PlantRecord

# eGRID plant-sheet column codes (stable across recent editions)
COL_PLANT_ID = "ORISPL"
COL_NAME = "PNAME"
COL_STATE = "PSTATABB"
COL_BA = "BACODE"
COL_FUEL_CATEGORY = "PLFUELCT"
COL_NET_GEN_MWH = "PLNGENAN"


class EGridSource(GridDataSource):
    name = "egrid"

    def __init__(self, workbook_path: str | Path, year: int = 2023):
        self.workbook_path = Path(workbook_path)
        self.year = year

    @property
    def sheet_name(self) -> str:
        return f"PLNT{str(self.year)[-2:]}"

    def load(self) -> List[PlantRecord]:
        import pandas as pd

        df = pd.read_excel(
            self.workbook_path, sheet_name=self.sheet_name, header=1
        )
        records: List[PlantRecord] = []
        for row in df.itertuples(index=False):
            plant_id = getattr(row, COL_PLANT_ID, None)
            if plant_id is None or pd.isna(plant_id):
                continue
            net_gen = getattr(row, COL_NET_GEN_MWH, None)
            records.append(
                PlantRecord(
                    plant_id=str(int(plant_id)),
                    name=str(getattr(row, COL_NAME, "") or ""),
                    state=str(getattr(row, COL_STATE, "") or ""),
                    balancing_authority=str(getattr(row, COL_BA, "") or ""),
                    primary_fuel=str(getattr(row, COL_FUEL_CATEGORY, "") or ""),
                    net_generation_mwh=(
                        float(net_gen) if net_gen is not None and not pd.isna(net_gen) else None
                    ),
                    year=self.year,
                    source=self.name,
                )
            )
        return records
