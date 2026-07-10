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

DEFAULT_LOADS = [
    {"id": "LD-001", "name": "Hyperscaler Cluster A", "mw": 250, "flexibility": 0.20, "rev_per_mw_hr": 150},
    {"id": "LD-002", "name": "Inference Center B", "mw": 200, "flexibility": 0.15, "rev_per_mw_hr": 180},
    {"id": "LD-003", "name": "AI Training Pod C", "mw": 300, "flexibility": 0.50, "rev_per_mw_hr": 120},
    {"id": "LD-004", "name": "Sovereign Compute D", "mw": 150, "flexibility": 0.10, "rev_per_mw_hr": 200},
    {"id": "LD-005", "name": "Giga-Factory E", "mw": 200, "flexibility": 0.05, "rev_per_mw_hr": 250}
]


def run_simulation(loads: list | None = None,
                   headroom_mw: float = 800,
                   cost_upgrade: float = 45000000.0) -> dict:
    # 1. Announce the Large Load Queue Requests (data centers in a region, e.g., PJM-West / MISO-East seam)
    # `headroom_mw`: available local transmission headroom before upgrades are triggered.
    # `cost_upgrade`: regional upgrade cost once cumulative requests exceed the headroom.
    if loads is None:
        loads = DEFAULT_LOADS

    total_mw_requested = sum(l["mw"] for l in loads)  # default: 1100 MW vs 800 MW headroom

    # -------------------------------------------------------------------------
    # Scenario A: Isolated Utility Studies (Current Practice)
    # -------------------------------------------------------------------------
    # - Studies are sequential (first-come, first-served in list order).
    # - Loads clear utility studies until cumulative capacity exceeds the headroom.
    # - The loads beyond the threshold trigger a transmission overload at the RTO boundary.
    # - The RTO calls a "Restudy Cascade", forcing all loads back into the queue for a
    #   re-evaluation of shared upgrade costs; the tail-end projects withdraw.
    # - Cleared loads take 18 months + 2 per queue position; withdrawn loads stall at 48 months.

    delays_isolated = {}
    withdrawn_isolated = []
    operational_isolated = []
    cumulative_mw = 0.0
    for position, l in enumerate(loads):
        cumulative_mw += l["mw"]
        if cumulative_mw <= headroom_mw:
            delays_isolated[l["id"]] = 18 + 2 * position
            operational_isolated.append(l["id"])
        else:
            delays_isolated[l["id"]] = 48
            withdrawn_isolated.append(l["id"])

    # -------------------------------------------------------------------------
    # Scenario B: Coordinated Cluster Studies (ESIG Recommendation)
    # -------------------------------------------------------------------------
    # - Utility and RTO share a joint data sheaf.
    # - The full cohort is studied collectively in a single cycle.
    # - The upgrade is identified upfront and shared proportionally among the loads by MW share.
    # - No restudy cascade is triggered.
    # - Siting timeline is shortened to a flat 24 months for all projects.

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
    # - They bypass the transmission upgrade and connect immediately (in 12 months).
    # - In exchange, they agree to curtail their flexible MW portion during the top 120 hours of peak grid congestion.
    # - Case-study load: the most flexible member of the cohort (default: LD-003, 300 MW, 50% flexible).

    case_load = max(loads, key=lambda l: (l["flexibility"], l["mw"]))
    capacity = float(case_load["mw"])
    flex_mw = capacity * case_load["flexibility"]

    annual_generation_hrs = 8760.0 * 0.90 # 90% capacity factor
    rev_per_mwh = float(case_load["rev_per_mw_hr"])
    discount_rate = 0.10

    # NPV Option 1: Firm Connection (Coordinated Study)
    # - Timeline: 24 months to power (2 years of zero revenue)
    # - Siting cost: the load's proportional upgrade cost (default LD-003: $12.27M)
    # - Operational Revenue starts in Year 3.
    upgrade_cost_firm = allocated_costs[case_load["id"]]
    annual_rev_firm = capacity * annual_generation_hrs * rev_per_mwh # default: 300 * 7884 * 120 = $283.82M
    
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
    # - Operational Revenue: Starts in Year 2, but loses revenue on the flexible MW for 120 hours of peak congestion.
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
        "provenance": {
            "kind": "simulated",
            "source": "Stylized simulation after the June 2026 ESIG report "
                      "'Interconnection Processes for Large Loads: Current Practices and Recommendations'",
            "generator": "domains.grid.experiments.large_load_coordination",
        },
        "queue_total_mw": total_mw_requested,
        "headroom_mw": headroom_mw,
        "upgrade_cost_usd": cost_upgrade,
        "cohort": loads,
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
            f"flexible_nonfirm_{case_load['id'].replace('-', '').lower()}": {
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

def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(
        description="Large load interconnection coordination simulation (stylized ESIG scenario).")
    parser.add_argument("--headroom-mw", type=float, default=800,
                        help="available local transmission headroom in MW (default: 800)")
    parser.add_argument("--upgrade-cost-musd", type=float, default=45.0,
                        help="regional upgrade cost in $ millions (default: 45)")
    parser.add_argument("--loads", type=Path, default=None,
                        help="path to a JSON list of load dicts "
                             "(keys: id, name, mw, flexibility, rev_per_mw_hr); default: built-in cohort")
    parser.add_argument("--out", type=Path,
                        default=REPORTS_DIR / "large_load_coordination_experiment.json",
                        help="output JSON path (default: the file the Streamlit UI reads)")
    args = parser.parse_args(argv)

    loads = None
    if args.loads is not None:
        with open(args.loads, encoding="utf-8") as f:
            loads = json.load(f)

    print("Running side experiment: Large Load Interconnection Simulation...")
    results = run_simulation(loads=loads,
                             headroom_mw=args.headroom_mw,
                             cost_upgrade=args.upgrade_cost_musd * 1e6)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Success! Side experiment results written to {args.out}")

if __name__ == "__main__":
    main()
