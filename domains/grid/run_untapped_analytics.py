# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Run script to calculate and export advanced mathematical grid analytics.

This script aggregates raw flow and evidence data to produce:
1. Yoneda similarity matrix for the 7 major US grid regions.
2. Right Kan Extension bounds for unpriced Southeast seams.
3. Sheaf coherence metrics before/after footprint correction.
4. Marginal BCR relief curves.

Outputs:
    reports/untapped_analytics.json
"""

from __future__ import annotations

import json
from pathlib import Path
import math
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "domains" / "grid" / "data"
REPORTS_DIR = ROOT_DIR / "reports"

def calculate_yoneda_similarities(csv_paths) -> dict:
    """Compute Jaccard-like Yoneda similarities between the 7 major RTOs/ISOs."""
    # Major BAs to analyze
    target_bas = {"MISO", "ERCOT", "PJM", "CISO", "SPP", "NYIS", "ISNE"}
    ba_aliases = {
        "ERCO": "ERCOT",
        "ERCOT": "ERCOT",
        "CISO": "CISO",
        "CAISO": "CISO",
        "NYIS": "NYIS",
        "NYISO": "NYIS",
        "ISNE": "ISNE",
        "ISO-NE": "ISNE",
        "SWPP": "SPP",
        "SPP": "SPP"
    }

    # Load and aggregate flows
    flows: dict[str, dict[str, float]] = {}  # ba -> {neighbor -> gross_flow}
    
    pair_gross = {}
    for path in csv_paths:
        if not Path(path).exists():
            continue
        df = pd.read_csv(
            path,
            usecols=["Balancing Authority", "Directly Interconnected Balancing Authority", "Interchange (MW)"],
            thousands=",",
        )
        df["Interchange (MW)"] = pd.to_numeric(df["Interchange (MW)"], errors="coerce")
        df = df.dropna(subset=["Interchange (MW)"])
        grouped = df.groupby(["Balancing Authority", "Directly Interconnected Balancing Authority"])["Interchange (MW)"]
        for pair, gross in grouped.apply(lambda s: s.abs().sum()).items():
            pair_gross[pair] = pair_gross.get(pair, 0.0) + float(gross)

    # Populate flow structure
    for (a, b), gross in pair_gross.items():
        # Canonicalize names
        a_canon = ba_aliases.get(a, a)
        b_canon = ba_aliases.get(b, b)
        
        if a_canon not in flows:
            flows[a_canon] = {}
        if b_canon not in flows:
            flows[b_canon] = {}
            
        flows[a_canon][b_canon] = flows[a_canon].get(b_canon, 0.0) + gross
        flows[b_canon][a_canon] = flows[b_canon].get(a_canon, 0.0) + gross

    # Compute pairwise Yoneda similarity
    matrix = {}
    for ba_a in target_bas:
        matrix[ba_a] = {}
        for ba_b in target_bas:
            if ba_a == ba_b:
                matrix[ba_a][ba_b] = 1.0
                continue
                
            # Get union of all neighbors of a and b
            neighbors = set(flows.get(ba_a, {}).keys()) | set(flows.get(ba_b, {}).keys())
            if not neighbors:
                matrix[ba_a][ba_b] = 0.0
                continue
                
            numerator = 0.0
            denominator = 0.0
            for n in neighbors:
                val_a = flows.get(ba_a, {}).get(n, 0.0)
                val_b = flows.get(ba_b, {}).get(n, 0.0)
                
                numerator += min(val_a, val_b)
                denominator += max(val_a, val_b)
                
            matrix[ba_a][ba_b] = round(numerator / denominator, 4) if denominator > 0 else 0.0
            
    return matrix

def calculate_right_kan_bounds() -> list:
    """Calculate lower-bound spreads for unpriced Southeast balancing authorities."""
    # Southeast BAs
    se_bas = {"SOCO", "TVA", "DUK", "FPL", "AECI", "CPLE", "CPLW", "FPC", "FMPP", "SEC", "TAL", "GVL"}
    
    # Load priced evidence to match priced neighbor spreads
    evidence_path = REPORTS_DIR / "congestion_evidence_report.json"
    if not evidence_path.exists():
        return []
        
    with open(evidence_path, encoding="utf-8") as f:
        ev_data = json.load(f)
        
    # Build maps of priced spreads per BA
    priced_spreads: dict[str, list[float]] = {}
    for claim in ev_data.get("claims", []):
        spread_val = claim.get("mean_price_spread_usd_mwh", 0.0)
        try:
            spread = float(spread_val)
        except (ValueError, TypeError):
            spread = 0.0
        if spread <= 0:
            continue
        a = claim["ba_a"]
        b = claim["ba_b"]
        priced_spreads.setdefault(a, []).append(spread)
        priced_spreads.setdefault(b, []).append(spread)
        
    # We now evaluate unpriced ties: if a tie is between two BAs where at least one is in SE,
    # and has no measured spread, we bound it by the minimum spread of adjacent priced ties.
    bounds = []
    # Identify unpriced Southeast ties
    flow_path = REPORTS_DIR / "flow_bottleneck_report.json"
    if not flow_path.exists():
        return []
        
    with open(flow_path, encoding="utf-8") as f:
        flow_data = json.load(f)
        
    for tie in flow_data.get("bottlenecks", []):
        a = tie["ba_a"]
        b = tie["ba_b"]
        gross = tie.get("gross_mwh", 0.0)
        
        # Check if it's a Southeast tie
        if a in se_bas or b in se_bas:
            has_priced = False
            for claim in ev_data.get("claims", []):
                c_spread_val = claim.get("mean_price_spread_usd_mwh", 0.0)
                try:
                    c_spread = float(c_spread_val)
                except (ValueError, TypeError):
                    c_spread = 0.0
                if ((claim["ba_a"] == a and claim["ba_b"] == b) or 
                    (claim["ba_a"] == b and claim["ba_b"] == a)) and c_spread > 0:
                    has_priced = True
                    break
                    
            if not has_priced:
                # Find priced neighbors
                neighbors = priced_spreads.get(a, []) + priced_spreads.get(b, [])
                if neighbors:
                    proxy_spread = min(neighbors)
                    screening_value = proxy_spread * gross
                    bounds.append({
                        "tie": f"{a} - {b}",
                        # The Southeast-side BA of this UNPRICED TIE. The BA
                        # itself may well have priced ties elsewhere -- the old
                        # name "unpriced_ba" wrongly implied otherwise.
                        "se_side_ba": a if a in se_bas else b,
                        "priced_neighbors_count": len(neighbors),
                        # NOT a bound. A single adjacent tie's spread carried
                        # across a different interface by analogy. Renamed from
                        # bound_spread_usd_mwh / bound_value_usd, which asserted
                        # a mathematical bound the method does not establish.
                        "proxy_spread_usd_mwh": round(proxy_spread, 2),
                        "gross_mwh": gross,
                        # Prices ALL gross flow at the proxy spread. Real
                        # congestion value accrues only in constrained hours, so
                        # this overstates by the unconstrained share.
                        "screening_value_usd": round(screening_value, 2),
                        "method_limits": (
                            f"analogy from {len(neighbors)} adjacent priced tie(s); "
                            "all gross flow priced at the proxy spread; "
                            "not a measured cost and not a bound"
                        ),
                    })

    return sorted(bounds, key=lambda x: x["screening_value_usd"], reverse=True)

def load_sheaf_metrics() -> dict | None:
    """Load sheaf metrics from the footprint correction report.

    Returns None when the report is missing or lacks the required fields.

    This function previously fell back to hardcoded constants (1.899, 0.818,
    0.452, 0.629, 59.3) copied from a past real run. Those were
    indistinguishable from computed output, so a missing input would render six
    plausible numbers on the dashboard with nothing marking them as
    placeholders. A page that shows "not available" is safer than one that
    quietly shows last year's answer as though it were current.
    """
    report_path = REPORTS_DIR / "ba_footprint_report.json"
    if not report_path.exists():
        return None

    with open(report_path, encoding="utf-8") as f:
        data = json.load(f)

    before = data.get("before", {})
    after = data.get("after", {})

    # Every field must be genuinely present -- no substituted defaults.
    required = ("sheaf_energy_leak", "agreement_rate", "abs_error_mwh")
    if not all(k in before and k in after for k in required):
        return None

    before_leak = before["sheaf_energy_leak"]
    after_leak = after["sheaf_energy_leak"]
    improvement = (before_leak - after_leak) / before_leak if before_leak else 0.0
    err_reduction_twh = (before["abs_error_mwh"] - after["abs_error_mwh"]) / 1e6

    return {
        "before_leak": round(before_leak, 4),
        "after_leak": round(after_leak, 4),
        "improvement": f"{improvement:.1%}",
        "before_rate": round(before["agreement_rate"], 3),
        "after_rate": round(after["agreement_rate"], 3),
        # Residual disagreement, not just the delta -- see §7 of the audit.
        # Reporting only the improvement hid that ~37% of entities still
        # disagree and 231 TWh remains unreconciled after correction.
        "residual_disagreement_rate": round(1.0 - after["agreement_rate"], 3),
        "residual_abs_error_twh": round(after["abs_error_mwh"] / 1e6, 1),
        "error_reduction_twh": round(err_reduction_twh, 1),
    }

def main():
    print("Calculating advanced mathematical grid analytics...")
    
    # 1. Yoneda similarities (using 2025 interchange data)
    csv_paths = [
        DATA_DIR / "EIA930_INTERCHANGE_2025_Jan_Jun.csv",
        DATA_DIR / "EIA930_INTERCHANGE_2025_Jul_Dec.csv"
    ]
    print("- Calculating Yoneda similarities...")
    yoneda_matrix = calculate_yoneda_similarities(csv_paths)
    
    # 2. Right Kan Southeast bounds
    print("- Calculating Right Kan bounds...")
    kan_bounds = calculate_right_kan_bounds()
    
    # 3. Sheaf coherence metrics
    print("- Loading sheaf metrics...")
    sheaf_metrics = load_sheaf_metrics()
    
    # 4. Generate some illustrative Marginal BCR points for top seams
    # MISO-SOCO seam (baseline spread $5.09/MWh, gross 3.99M MWh)
    # Annual Upgrade Cost = $150,000/MW-yr
    # Throughput (Transmission) = 8760 h/yr
    print("- Simulating Marginal BCR curves...")
    seams_to_evaluate = [
        {"name": "PJM - NYIS", "spread": 2.01, "gross": 19294263.0},
        {"name": "MISO - SWPP", "spread": 5.09, "gross": 3989884.0},
        {"name": "CISO - SRP", "spread": 4.12, "gross": 10099478.0}
    ]
    
    marginal_curves = {}
    for seam in seams_to_evaluate:
        name = seam["name"]
        spread = seam["spread"]
        gross = seam["gross"]
        
        # steps in MW
        steps = [50, 100, 200, 400, 600, 800, 1000]
        points = []
        for mw in steps:
            # relief value derivative: Spread * 8760 * exp(-8760 * mw / gross)
            deriv = spread * 8760 * math.exp(-8760 * mw / gross)
            marginal_bcr = deriv / 150000.0  # cost = $150k/MW-yr
            points.append({
                "mw": mw,
                "marginal_bcr": round(marginal_bcr, 2),
                "residual_spread": round(spread * math.exp(-8760 * mw / gross), 2)
            })
        marginal_curves[name] = points

    # Save consolidated report
    report = {
        "yoneda_matrix": yoneda_matrix,
        "right_kan_bounds": kan_bounds,
        "sheaf_metrics": sheaf_metrics,
        "marginal_curves": marginal_curves
    }
    
    out_path = REPORTS_DIR / "untapped_analytics.json"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"Success! Advanced analytics written to {out_path}")

if __name__ == "__main__":
    main()
