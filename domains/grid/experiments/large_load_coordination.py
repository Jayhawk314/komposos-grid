# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Side Experiment: Large Load Interconnection Coordination Simulation.
Reflecting the recommendations of the June 2026 ESIG Large Loads Report:
"Interconnection Processes for Large Loads: Current Practices and Recommendations"

This script simulates:
1. Isolated Utility Studies vs. Coordinated RTO-Utility Cluster Studies.
2. The risk of cumulative transmission overloads and restudy cascades.
3. The financial NPV trade-offs of Flexible (Non-Firm) Interconnection Services.
"""

from __future__ import annotations

import json
from pathlib import Path
import math

ROOT_DIR = Path(__file__).parent.parent.parent.parent
REPORTS_DIR = ROOT_DIR / "reports" / "experiments"

def run_simulation() -> dict:
    # 1. Announce the Large Load Queue Requests (5 data centers in a region, e.g., PJM-West / MISO-East seam)
    # Total available local transmission headroom: 800 MW
    # Total local upgrades needed above 800 MW: $45M
    loads = [
        {"id": "LD-001", "name": "Hyperscaler Cluster A", "mw": 250, "flexibility": 0.20, "rev_per_mw_hr": 150},
        {"id": "LD-002", "name": "Inference Center B", "mw": 200, "flexibility": 0.15, "rev_per_mw_hr": 180},
        {"id": "LD-003", "name": "AI Training Pod C", "mw": 300, "flexibility": 0.50, "rev_per_mw_hr": 120},
        {"id": "LD-004", "name": "Sovereign Compute D", "mw": 150, "flexibility": 0.10, "rev_per_mw_hr": 200},
        {"id": "LD-005", "name": "Giga-Factory E", "mw": 200, "flexibility": 0.05, "rev_per_mw_hr": 250}
    ]
    
    total_mw_requested = sum(l["mw"] for l in loads) # 1100 MW (exceeds 800 MW headroom by 300 MW)
    
    # -------------------------------------------------------------------------
    # Scenario A: Isolated Utility Studies (Current Practice)
    # -------------------------------------------------------------------------
    # - Studies are sequential.
    # - First 3 loads clear utility studies without triggering transmission upgrades (cumulative = 750 MW <= 800 MW).
    # - 4th and 5th loads trigger a massive transmission overload at the RTO boundary.
    # - The RTO calls a "Restudy Cascade", forcing all 5 loads back into the queue for a re-evaluation of shared upgrade costs.
    # - Delays increase by 24 months; 2 projects withdraw due to timeline inflation.
    
    delays_isolated = {
        "LD-001": 18, # original 18 months + 24 months restudy = 42 months
        "LD-002": 20, # 44 months
        "LD-003": 22, # 46 months
        "LD-004": 48, # withdrawn due to delay
        "LD-005": 48  # withdrawn due to delay
    }
    
    withdrawn_isolated = ["LD-004", "LD-005"]
    operational_isolated = ["LD-001", "LD-002", "LD-003"]
    
    # -------------------------------------------------------------------------
    # Scenario B: Coordinated Cluster Studies (ESIG Recommendation)
    # -------------------------------------------------------------------------
    # - Utility and RTO share a joint data sheaf.
    # - The 1100 MW is studied collectively in a single cycle.
    # - The $45M upgrade is identified upfront and shared proportionally among the 5 loads based on MW share.
    # - No restudy cascade is triggered.
    # - Siting timeline is shortened to a flat 24 months for all projects.
    
    cost_upgrade = 45000000.0 # $45M
    allocated_costs = {}
    for l in loads:
        share = l["mw"] / total_mw_requested
        allocated_costs[l["id"]] = round(cost_upgrade * share, 2)
        
    delays_coordinated = {l["id"]: 24 for l in loads}
    withdrawn_coordinated = []
    
    # -------------------------------------------------------------------------
    # Scenario C: Flexible Interconnection Service (Non-Firm Option)
    # -------------------------------------------------------------------------
    # - Hyperscalers agree to a "Non-Firm" interconnection.
    # - They bypass the $45M transmission upgrade and connect immediately (in 12 months).
    # - In exchange, they agree to curtail their flexible MW portion during the top 120 hours of peak grid congestion.
    # - We compute the NPV for "LD-003" (AI Training Pod C, 300 MW, 50% flexible) under Coordinated vs. Non-Firm.
    
    # Financial parameters for LD-003 (AI Training)
    capacity = 300.0 # MW
    flex_mw = capacity * 0.50 # 150 MW flexible
    firm_mw = capacity * 0.50 # 150 MW firm
    
    annual_generation_hrs = 8760.0 * 0.90 # 90% capacity factor
    rev_per_mwh = 120.0 # $/MWh
    discount_rate = 0.10
    
    # NPV Option 1: Firm Connection (Coordinated Study)
    # - Timeline: 24 months to power (2 years of zero revenue)
    # - Siting cost: Proportional upgrade cost ($12.27M)
    # - Operational Revenue starts in Year 3.
    upgrade_cost_firm = allocated_costs["LD-003"] # $12.27M
    annual_rev_firm = capacity * annual_generation_hrs * rev_per_mwh # 300 * 7884 * 120 = $283.82M
    
    npv_firm = -upgrade_cost_firm
    for year in range(1, 11):
        if year <= 2:
            # Siting phase, zero operating revenue
            cash_flow = 0
        else:
            cash_flow = annual_rev_firm
        npv_firm += cash_flow / ((1 + discount_rate) ** year)
        
    # NPV Option 2: Non-Firm Connection (Flexible Service)
    # - Timeline: 12 months to power (1 year of zero revenue, starts in Year 2)
    # - Siting cost: $0 transmission upgrade (bypasses the overload by agreeing to curtail)
    # - Operational Revenue: Starts in Year 2, but loses revenue on the flexible 150 MW for 120 hours of peak congestion.
    curtailment_hours = 120.0
    lost_revenue_curt = flex_mw * curtailment_hours * rev_per_mwh # 150 * 120 * 120 = $2.16M
    annual_rev_nonfirm = annual_rev_firm - lost_revenue_curt # $281.66M
    
    npv_nonfirm = 0.0
    for year in range(1, 11):
        if year <= 1:
            cash_flow = 0
        else:
            cash_flow = annual_rev_nonfirm
        npv_nonfirm += cash_flow / ((1 + discount_rate) ** year)
        
    npv_gain = npv_nonfirm - npv_firm
    
    return {
        "queue_total_mw": total_mw_requested,
        "scenarios": {
            "isolated": {
                "delays_months": delays_isolated,
                "withdrawn_projects": withdrawn_isolated,
                "operational_projects": operational_isolated,
                "average_delay_months": sum(delays_isolated.values()) / len(loads)
            },
            "coordinated": {
                "delays_months": delays_coordinated,
                "withdrawn_projects": withdrawn_coordinated,
                "allocated_upgrade_costs_usd": allocated_costs,
                "average_delay_months": 24.0
            },
            "flexible_nonfirm_ld003": {
                "upgrade_cost_saved_usd": upgrade_cost_firm,
                "time_to_power_months_saved": 12,
                "annual_curtailment_hours": curtailment_hours,
                "curtailed_energy_mwh": flex_mw * curtailment_hours,
                "curtailed_revenue_loss_usd": lost_revenue_curt,
                "npv_firm_usd": round(npv_firm, 2),
                "npv_nonfirm_usd": round(npv_nonfirm, 2),
                "net_present_value_gain_usd": round(npv_gain, 2)
            }
        }
    }

def main():
    print("Running side experiment: Large Load Interconnection Simulation...")
    results = run_simulation()
    
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "large_load_coordination_experiment.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    print(f"Success! Side experiment results written to {out_path}")

if __name__ == "__main__":
    main()
