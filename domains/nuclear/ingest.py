# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Ingest and construct the Civilian Nuclear Enrichment domain Category.

Maps supply chain stages (Mining, Conversion, Enrichment, Fabrication, Demand)
into Category objects, and material/capacity flows into morphisms with quantale values.
"""

from __future__ import annotations

import csv
import os
from typing import Dict, Optional
from core.category import Category


class NuclearCategoryBuilder:
    """Builder class for nuclear fuel cycle and enrichment categories."""

    def __init__(self, category: Category):
        self.category = category

    def _ensure_object(self, name: str, type_name: str, **metadata) -> None:
        """Helper to safely add an object if it does not exist."""
        if self.category.get(name) is None:
            self.category.add(name, type_name=type_name, metadata=metadata)

    def ingest_synthetic_baseline(self) -> Dict[str, int]:
        """Populates the category with baseline 2026 civilian fuel cycle capacities.

        Data reflects (facility names real; capacities/confidences are stylized inputs):
          - McClean Lake (Orano *mill* in Saskatchewan — processes ore from mines such as
            Cigar Lake; modeled here as the upstream supply node)
          - Metropolis (Honeywell's IL conversion plant, marketed via the ConverDyn venture —
            sole domestic conversion facility, known bottleneck)
          - Urenco Eunice, NM (sole operating commercial LEU enrichment facility in the US,
            expanding; Centrus Piketon produces demonstration-scale HALEU separately)
          - Westinghouse Columbia (fabrication facility)
          - Projected next-gen civilian SMR pilot units and Hyperscaler compute loads
        """
        # 1. Add Objects
        self._ensure_object("mine:mcclean_lake", "mine", location="Canada", capacity_tuy="12000")
        self._ensure_object("conversion:metropolis_converdyn", "conversion_facility", location="IL, USA", capacity_tuy="15000")
        self._ensure_object("enrichment:urenco_eunice", "enrichment_facility", location="NM, USA", capacity_swu="4600")
        self._ensure_object("fabrication:westinghouse_columbia", "fabrication_facility", location="SC, USA", capacity_tuy="1200")
        self._ensure_object("reactor:smr_pilot", "reactor", type="HALEU_SMR", capacity_mwe="300")
        self._ensure_object("demand:hyperscaler_dc", "demand", power_mw="1000", customer="AI_Compute_HQ")

        # 2. Add Morphisms (flows and process dependencies)
        # McClean Lake feeds Metropolis ConverDyn
        self.category.connect(
            "mine:mcclean_lake",
            "conversion:metropolis_converdyn",
            name="feeds_into",
            confidence=0.95,
            flow_tuy=8000,
        )

        # Metropolis ConverDyn supplies Urenco Eunice
        # (This is a tight constraint in conversion capacity; confidence indicates supply-chain risk)
        self.category.connect(
            "conversion:metropolis_converdyn",
            "enrichment:urenco_eunice",
            name="processes_to",
            confidence=0.45,  # Moderate confidence due to domestic conversion centralized limits
            flow_tuy=7000,
        )

        # Urenco Eunice feeds Westinghouse Columbia
        # (Centrifuge queues / expansion delays; moderate confidence/lead time risk)
        self.category.connect(
            "enrichment:urenco_eunice",
            "fabrication:westinghouse_columbia",
            name="processes_to",
            confidence=0.55,  # Centrifuge cascade expansion queue bottleneck
            flow_swu=3000,
        )

        # Westinghouse Columbia supplies the SMR pilot reactor
        self.category.connect(
            "fabrication:westinghouse_columbia",
            "reactor:smr_pilot",
            name="powers",
            confidence=0.90,
            assemblies_per_year=60,
        )

        # SMR powers the Hyperscaler data center demand
        self.category.connect(
            "reactor:smr_pilot",
            "demand:hyperscaler_dc",
            name="powers",
            confidence=0.85,
            capacity_mwe=300,
        )

        return {"objects": 6, "morphisms": 5}

    def load_from_csv(self, nodes_csv_path: str, edges_csv_path: str) -> Dict[str, int]:
        """Loads custom nuclear capacity objects and flow edges from CSV files.

        nodes_csv columns: name, type_name, capacity, location
        edges_csv columns: source, target, relation_name, confidence, flow_value
        """
        obj_count = 0
        mor_count = 0

        # Read nodes
        if os.path.exists(nodes_csv_path):
            with open(nodes_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self._ensure_object(
                        row["name"],
                        row["type_name"],
                        capacity=row.get("capacity", ""),
                        location=row.get("location", ""),
                    )
                    obj_count += 1

        # Read edges
        if os.path.exists(edges_csv_path):
            with open(edges_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.category.connect(
                        row["source"],
                        row["target"],
                        name=row["relation_name"],
                        confidence=float(row.get("confidence", 1.0)),
                        flow=row.get("flow_value", ""),
                    )
                    mor_count += 1

        return {"objects": obj_count, "morphisms": mor_count}
