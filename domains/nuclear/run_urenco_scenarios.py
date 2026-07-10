# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""What-if scenario runner mapping Urenco USA expansion capacity phases and timelines.

Illustrates how to model multi-phase expansion projects and evaluate capacity claims
using CogEngine and Category standalone.
"""

from __future__ import annotations

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


async def run_scenarios():
    print("======================================================================")
    print("      Modeling Urenco USA Capacity Expansion & SMR Timelines")
    print("======================================================================")

    # 1. Initialize Category
    cat = Category(name="urenco_expansion_scenarios", db_path=":memory:")

    # 2. Add Urenco USA Capacity Nodes for different historical/planned phases
    cat.add("urenco:eunice_2025_baseline", type_name="enrichment_facility", metadata={"capacity_swu": "4.3M", "status": "active"})
    cat.add("urenco:eunice_2027_expansion", type_name="enrichment_facility", metadata={"capacity_swu": "5.0M", "status": "planned_refurb"})
    cat.add("urenco:eunice_2032_expansion", type_name="enrichment_facility", metadata={"capacity_swu": "7.1M", "status": "future_construction"})
    
    # 3. Add Reactor Demand Nodes (Tech hyperscaler SMR timelines)
    cat.add("reactor:smr_pilot_2028", type_name="reactor", metadata={"demand_date": "2028", "req_haleu": "yes"})
    cat.add("reactor:smr_fleet_2035", type_name="reactor", metadata={"demand_date": "2035", "req_haleu": "yes"})

    # 4. Connect Urenco capacities to their target timelines via morphisms
    # The 2027 refurb is highly likely to meet a 2028 reactor timeline
    cat.connect(
        "urenco:eunice_2027_expansion",
        "reactor:smr_pilot_2028",
        name="can_supply_by",
        confidence=0.85,
        target_year=2028
    )

    # The massive 7.1M SWU expansion (online 2032) is physically delayed and CANNOT meet the 2028 timeline
    cat.connect(
        "urenco:eunice_2032_expansion",
        "reactor:smr_pilot_2028",
        name="can_supply_by",
        confidence=0.05,  # Low confidence due to temporal mismatch (2032 vs 2028)
        delay_years=4,
        target_year=2028
    )

    # The 7.1M SWU expansion is well aligned to power the 2035 fleet target
    cat.connect(
        "urenco:eunice_2032_expansion",
        "reactor:smr_fleet_2035",
        name="can_supply_by",
        confidence=0.90,
        target_year=2035
    )

    # 5. Initialize CogEngine
    session = CogSession(category=cat)
    cog = CogEngine(session=session)

    # 6. Verify Logistics Claims
    print("\n[SCENARIO 1] Claim: Can the 2032 expansion plant power the 2028 pilot reactor?")
    claim_1 = CogClaim(
        source="urenco:eunice_2032_expansion",
        target="reactor:smr_pilot_2028",
        relation="can_supply_by",
        confidence=0.50
    )
    result_1 = cog.check_claim(claim_1)
    print(f"  Verdict: {result_1.status.value.upper()}")
    print(f"  Confidence: {result_1.confidence:.3f}")
    print(f"  Explanation: {result_1.explanation}")

    print("\n[SCENARIO 2] Claim: Can the 2032 expansion plant power the 2035 reactor fleet?")
    claim_2 = CogClaim(
        source="urenco:eunice_2032_expansion",
        target="reactor:smr_fleet_2035",
        relation="can_supply_by",
        confidence=0.50
    )
    result_2 = cog.check_claim(claim_2)
    print(f"  Verdict: {result_2.status.value.upper()}")
    print(f"  Confidence: {result_2.confidence:.3f}")
    print(f"  Explanation: {result_2.explanation}")
    print("======================================================================\n")


if __name__ == "__main__":
    asyncio.run(run_scenarios())
