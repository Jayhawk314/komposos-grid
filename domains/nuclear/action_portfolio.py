# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Compiles categorical bottlenecks into actionable intervention portfolios.

Groups supply chain risks and constraints into prioritized work packages
for utilities, hyperscalers, and federal policymakers.
"""

from __future__ import annotations

import os
from typing import Dict, List
from core.category import Category
from domains.nuclear.flow_geometry import analyze_enrichment_geometry


class NuclearActionPortfolio:
    """Compiles bottleneck analysis into an actionable relief report."""

    def __init__(self, category: Category):
        self.category = category

    def compile_portfolio(self) -> List[Dict[str, str]]:
        """Analyzes flow geometry and groups risks into action items."""
        report = analyze_enrichment_geometry(self.category)
        actions = []

        # Check for Conversion constraint
        conversion_edges = [e for e in report.edge_curvatures if "conversion" in e[0]]
        if conversion_edges:
            worst_conv = min(conversion_edges, key=lambda x: x[2])
            if worst_conv[2] < 0.50:  # Constrained path
                actions.append({
                    "id": "ACT-001",
                    "title": "Conversion Capacity Expansion (ConverDyn Seam)",
                    "constraint_level": f"High (Curvature: {worst_conv[2]:+.3f})",
                    "description": f"The transport edge from {worst_conv[0]} to {worst_conv[1]} is highly centralized.",
                    "intervention": "Co-fund domestic conversion facility upgrades or secure long-term European conversion contracts (e.g. Orano) to mitigate single-source failure.",
                    "priority": "CRITICAL"
                })

        # Check for Enrichment centrifuge queue constraint
        enrichment_edges = [e for e in report.edge_curvatures if "enrichment" in e[0] and "fabrication" in e[1]]
        if enrichment_edges:
            worst_enr = min(enrichment_edges, key=lambda x: x[2])
            if worst_enr[2] < 0.60:
                actions.append({
                    "id": "ACT-002",
                    "title": "Centrifuge Cascade Acceleration (Urenco USA)",
                    "constraint_level": f"Medium-High (Curvature: {worst_enr[2]:+.3f})",
                    "description": f"Centrifuge cascade capacity at {worst_enr[0]} limits downstream output.",
                    "intervention": "Provide federal Defense Production Act (DPA) matching capital to accelerate Urenco's Phase C construction timeline (shifting output from 2032 forward to 2029).",
                    "priority": "HIGH"
                })

        # General Tails Re-feeding / Co-location Opportunity
        actions.append({
            "id": "ACT-003",
            "title": "Co-located Tails Re-enrichment & Grid Curtailment",
            "constraint_level": "Opportunistic",
            "description": "Secondary enrichment of depleted uranium tails requires high steady-state power.",
            "intervention": "Co-locate SMR reactors and centrifuge cascades directly next to gigawatt-scale wind/solar hubs. Use grid curtailment energy (zero-cost excess power) to run secondary tails enrichment.",
            "priority": "MEDIUM"
        })

        return actions

    def write_report(self, output_path: str) -> None:
        """Writes the action portfolio report to a markdown file."""
        actions = self.compile_portfolio()
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        lines = [
            "# Nuclear Bottleneck Relief - Action Portfolio",
            "",
            "This report translates the flow geometry and curvature constraints of the nuclear fuel cycle into discrete, decision-ready intervention packages.",
            "",
            "---",
            ""
        ]

        for act in actions:
            lines.extend([
                f"## [{act['priority']}] {act['id']}: {act['title']}",
                f"*   **Constraint Level:** {act['constraint_level']}",
                f"*   **Status:** Pending Scoping",
                "",
                "### Description",
                act['description'],
                "",
                "### Proposed Intervention",
                act['intervention'],
                "",
                "---",
                ""
            ])

        with open(output_path, mode="w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[PORTFOLIO] Action portfolio written to: {output_path}")
