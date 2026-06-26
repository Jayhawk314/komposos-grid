# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Command-line runner for the Civilian Nuclear Enrichment Flow pipeline.

Performs ingestion, structural curvature bottleneck checks, and claim verification.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import os

# Ensure local source imports are accessible
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_dirs = [
    os.path.join(repo_root, "src"),
    os.path.join(repo_root, "src", "komposos_core"),
    os.path.join(repo_root, "src", "komposos_wesys"),
]
for d in src_dirs:
    if os.path.exists(d) and d not in sys.path:
        sys.path.insert(0, d)

from core.category import Category
from cog.session import CogSession
from cog.engine import CogEngine
from cog.schema import CogClaim
from domains.nuclear.ingest import NuclearCategoryBuilder
from domains.nuclear.flow_geometry import analyze_enrichment_geometry
from domains.nuclear.action_portfolio import NuclearActionPortfolio


async def main():
    parser = argparse.ArgumentParser(
        description="Run Civilian Nuclear Enrichment & Supply Chain analysis pipeline."
    )
    parser.add_argument(
        "--db", default=":memory:", help="Path to SQLite DB (default :memory:)"
    )
    parser.add_argument(
        "--nodes-csv", help="Optional CSV file path for custom facility objects"
    )
    parser.add_argument(
        "--edges-csv", help="Optional CSV file path for custom flow edges"
    )
    args = parser.parse_args()

    print("======================================================================")
    print("      KOMPOSOS-IV Civilian Nuclear Enrichment Pipeline")
    print("======================================================================")

    # 1. Initialize Category
    cat = Category(name="nuclear_fuel_cycle", db_path=args.db)
    builder = NuclearCategoryBuilder(cat)

    # 2. Ingest data
    if args.nodes_csv and args.edges_csv:
        print(f"Ingesting custom data from CSVs:\n  Nodes: {args.nodes_csv}\n  Edges: {args.edges_csv}")
        stats = builder.load_from_csv(args.nodes_csv, args.edges_csv)
    else:
        print("No CSVs supplied. Loading baseline 2026 civilian enrichment capacity models...")
        stats = builder.ingest_synthetic_baseline()

    print(f"Ingestion Stats: Loaded {stats['objects']} objects, {stats['morphisms']} morphisms.\n")

    # 3. Flow Geometry / Curvature analysis
    print("[GEOMETRY] Executing Flow Geometry & Curvature bottleneck analysis...")
    geom_report = analyze_enrichment_geometry(cat)
    print(f"  Network contains {geom_report.num_nodes} nodes and {geom_report.num_edges} edges.")
    print(f"  Spectral Algebraic Connectivity (Fiedler value): {geom_report.fiedler_value:.5f}")
    
    print("\n  Curvature-Ranked Flow Bottlenecks (negative curvature implies constraints):")
    for u, v, kappa in geom_report.edge_curvatures:
        verdict = "BOTTLENECK" if kappa < 0 else "MESHED"
        print(f"    * {u} -> {v}: Curvature = {kappa:+.4f} [{verdict}]")

    print("\n  Fiedler partition (seams between weakly-coupled regions):")
    part_a, part_b = geom_report.partition
    print(f"    Region A: {part_a}")
    print(f"    Region B: {part_b}")

    # 4. Cognitive verification check
    print("\n[COG] Running Tiered Verification on logistics assertions...")
    session = CogSession(category=cat)
    cog = CogEngine(session=session)

    # Claim: Can the centrifuge cascades sustain the hyperscaler compute load?
    claim = CogClaim(
        source="enrichment:urenco_eunice",
        target="demand:hyperscaler_dc",
        relation="powers",
        confidence=0.50
    )

    check_result = cog.check_claim(claim)
    print(f"  Claim check: {claim.source} --[{claim.relation}]--> {claim.target}")
    print(f"  Verdict status: {check_result.status.value.upper()}")
    print(f"  System confidence: {check_result.confidence:.3f}")
    print(f"  Justification: {check_result.explanation}")
    print(f"  Proof Path: {check_result.supporting_paths}")
    
    # 5. Compile Action Portfolio
    print("\n[PORTFOLIO] Compiling nuclear bottleneck action portfolio...")
    portfolio = NuclearActionPortfolio(cat)
    portfolio.write_report("reports/nuclear_action_portfolio.md")
    print("======================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
