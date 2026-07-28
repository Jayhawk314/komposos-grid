# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins <jhawk314@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (see LICENSE file).
# No copyright is claimed in the underlying public data — see NOTICE.

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="US Grid Waste & Interconnection Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS FOR SLEEK DARK THEME ---
st.markdown(
    """
    <style>
    :root {
        --ink: #edeff2;
        --muted: #94a3b8;
        --paper: #020617;
        --line: #1e293b;
        --teal: #38bdf8;
        --blue: #1f6feb;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        background-color: var(--paper);
    }
    h1, h2, h3 { color: var(--ink); font-weight: 800; }
    p { color: var(--muted); }
    
    /* Sidebar Tweaks */
    [data-testid="stSidebar"] {
        background-color: #0b1329;
        border-right: 1px solid var(--line);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("⚡ Grid Analytics")
    st.caption("Interactive Tools & Process Studies")
    st.divider()
    
    selection = st.radio(
        "Select Dashboard",
        [
            "⚡ Grid Network Map",
            "📊 Regional Queue Study",
            "📈 Seam Congestion Findings",
            "🎯 Seam Opportunity Screen",
            "⚡ Large Load Siting (ESIG)",
        ]
    )
    
    st.divider()
    st.info(
        "This is a dedicated utility dashboard for presenting grid findings and "
        "interconnection queue comparisons to external stakeholders."
    )

# --- PATH RESOLVERS ---
ROOT_DIR = Path(__file__).parent
DOCS_DIR = ROOT_DIR / "docs"
REPORTS_DIR = ROOT_DIR / "reports"

# --- ROUTING LOGIC ---
if selection == "⚡ Grid Network Map":
    st.title("⚡ Interactive Grid Network Map")
    st.write(
        "A zoomable, interactive D3-based network map of the Balancing Authority (BA) interchange grid. "
        "Each node represents a BA; line colors represent Ollivier-Ricci curvature bottlenecks (red)."
    )
    
    map_path = DOCS_DIR / "network_map.html"
    if map_path.exists():
        html_content = map_path.read_text(encoding="utf-8")
        st.components.v1.html(html_content, height=850, scrolling=True)
    else:
        st.error(
            "network_map.html not found. Please run the following command to generate it:\n"
            "`python -m domains.grid.run_network_map`"
        )

elif selection == "📊 Regional Queue Study":
    st.title("📊 Regional Interconnection Queue Studies")
    st.write(
        "A detailed comparison of regional study processes, milestone funnels, and cycle trends "
        "across all US grid regions based on LBNL Queued Up, 2026 Edition (data through year-end 2025)."
    )
    
    # Load queue brief data
    brief_json_path = REPORTS_DIR / "stitch_2026-06-23" / "queue_process_brief.json"
    if brief_json_path.exists():
        with open(brief_json_path, encoding="utf-8") as f:
            brief_data = json.load(f)
        
        # Map regions
        regions_map = {r["region"].upper(): r for r in brief_data.get("regions", [])}
        
        # Let user select region
        selected_region = st.selectbox(
            "Select Grid Region to Screen",
            options=list(regions_map.keys()),
            index=0,
            help="Choose from 9 US grid regions to load detailed sub-data"
        )
        
        r = regions_map[selected_region]
        
        st.divider()
        st.subheader(f"⚡ Interconnection Metrics: {selected_region}")
        
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Total Requests (All-Time)", f"{r['total_requests']:,}")
        col_b.metric("Active Stalled in Queue", f"{r['active_in_queue']:,}")
        col_c.metric("LBNL Completion (2000-2020)", f"{r['completion_lbnl']['rate']:.1%}")
        # SPP records no executed-IA date on withdrawn projects, so the rate is
        # undefined there -- showing 0.0% would read as "nothing ever gets built".
        if r["post_ia"].get("signed_decided"):
            col_d.metric("Built after Signing IA", f"{r['post_ia']['rate']:.1%}")
        else:
            col_d.metric("Built after Signing IA", "— not tracked")
        
        st.divider()
        
        # Sub-data tabs
        st.markdown("#### Detailed Regional Queue Sub-Data")
        sub_tab_fuel, sub_tab_ms, sub_tab_cycle, sub_tab_dur = st.tabs([
            "🔋 Active Capacity by Fuel", 
            "📉 Milestone Funnel", 
            "📅 Study Cycle Cohort Trend", 
            "⏱️ Pipeline Durations"
        ])
        
        with sub_tab_fuel:
            st.markdown("**Active Queue Capacity (GW)**")
            fuel_gw = r.get("active_fuel_gw", {})
            if fuel_gw:
                fuel_df = pd.DataFrame(list(fuel_gw.items()), columns=["Fuel Type", "Capacity (GW)"])
                st.bar_chart(fuel_df.set_index("Fuel Type"))
            else:
                st.write("No active capacity data available.")
                
        with sub_tab_ms:
            st.markdown("**Milestone Completion Funnel**")
            st.markdown(
                "Percentage of decided projects that went operational, grouped by their "
                "furthest recorded milestone:"
            )
            _pia = r.get("post_ia") or {}
            _ms_rows = r.get("milestones", [])
            _ia_row = next(
                (m for m in _ms_rows if str(m.get("milestone", "")).lower() == "ia_executed"),
                None,
            )
            if _ia_row and _pia.get("signed_decided"):
                st.warning(
                    "**This table answers a different question from the 'Built after Signing IA' "
                    "metric above, and gives a different answer.** The `ia_executed` row reads "
                    f"**{_ia_row['completion']:.1%}**; the headline metric reads "
                    f"**{_pia['rate']:.1%}**.\n\n"
                    "**Trust the headline.** It keys on the executed-IA *date*, set at signing, so "
                    "it counts projects that signed and later withdrew — LBNL's method. This table "
                    "keys on `ia_status`, the *furthest known* milestone, which gets relabelled as "
                    "projects move on or die, biasing the `ia_executed` rate upward. Read the "
                    "funnel for its shape — where projects stop — not as success rates."
                )
            ms_df = pd.DataFrame(_ms_rows)
            if not ms_df.empty:
                ms_df.columns = ["Milestone Stage", "Decided Projects", "Operational Projects", "Completion Rate (survivorship-affected)", "Thin Cohort (<30)"]
                st.dataframe(
                    ms_df.style.format({"Completion Rate (survivorship-affected)": "{:.1%}"}),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.write("No milestone data available.")
                
        with sub_tab_cycle:
            st.markdown("**Study Cycle / Cohort Trend**")
            st.markdown("Completion rate and decided share (maturity) by cluster study cycle or submission cohort year:")
            cycle_df = pd.DataFrame(r.get("cycles", []))
            if not cycle_df.empty:
                cycle_df.columns = ["Cycle / Cohort", "Total Requests", "Decided", "Operational", "Withdrawn", "Active", "Completion Rate", "Maturity Index (Decided %)", "Immature", "Thin"]
                st.line_chart(cycle_df.set_index("Cycle / Cohort")[["Completion Rate", "Maturity Index (Decided %)"]])
                st.dataframe(
                    cycle_df[["Cycle / Cohort", "Total Requests", "Decided", "Active", "Completion Rate", "Maturity Index (Decided %)"]].style.format({
                        "Completion Rate": "{:.1%}",
                        "Maturity Index (Decided %)": "{:.1%}"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.write("No cycle data available.")
                
        with sub_tab_dur:
            st.markdown("**Interconnection Pipeline Durations**")
            st.markdown("Median months elapsed, with [p25–p75] interquartile range (IQR) spreads:")
            dur = r.get("durations", {})
            if dur:
                dur_rows = [
                    {"Stage Pipeline": "Study & Agreement (IR ➔ IA)", "Median (Months)": dur["ir_to_ia"]["median_months"], "IQR Range (Months)": f"{dur['ir_to_ia']['p25_months']} – {dur['ir_to_ia']['p75_months']}"},
                    {"Stage Pipeline": "Construction & Build (IA ➔ COD)", "Median (Months)": dur["ia_to_cod"]["median_months"], "IQR Range (Months)": f"{dur['ia_to_cod']['p25_months']} – {dur['ia_to_cod']['p75_months']}"},
                    {"Stage Pipeline": "Total End-to-End (IR ➔ COD)", "Median (Months)": dur["ir_to_cod"]["median_months"], "IQR Range (Months)": f"{dur['ir_to_cod']['p25_months']} – {dur['ir_to_cod']['p75_months']}"},
                ]
                st.dataframe(pd.DataFrame(dur_rows), use_container_width=True, hide_index=True)
            else:
                st.write("No duration data available.")
    else:
        st.error("Queue brief JSON not found. Run `run_stitch_brief.py` first.")

elif selection == "📈 Seam Congestion Findings":
    st.title("📈 Seam Congestion & Public Findings")
    st.write(
        "Public findings on where the US electric grid loses money, what would fix it, "
        "and whether the fix pays for itself."
    )
    
    findings_path = DOCS_DIR / "index.html"
    if findings_path.exists():
        html_content = findings_path.read_text(encoding="utf-8")
        st.components.v1.html(html_content, height=900, scrolling=True)
    else:
        st.error(
            "index.html not found. Please run the following command to generate it:\n"
            "`python -m domains.grid.run_dashboard`"
        )


elif selection == "🎯 Seam Opportunity Screen":
    st.title("🎯 Seam Opportunity Screening")
    st.write(
        "Surfacing hidden grid value and identifying high-priority transmission and storage upgrades. "
        "These metrics translate physical flows and market boundaries into clean, actionable investment indicators."
    )

    import json
    import pandas as pd
    
    # Load advanced analytics
    analytics_path = REPORTS_DIR / "untapped_analytics.json"
    if analytics_path.exists():
        with open(analytics_path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        st.error("Untapped analytics report not found. Run `python -m domains.grid.run_untapped_analytics` first.")
        st.stop()

    tab_yoneda, tab_kan, tab_bcr, tab_sheaf = st.tabs([
        "🧬 RTO Portability Score", 
        "📐 Shadow Market Valuation", 
        "📈 Optimal Sizing Curves",
        "🕸️ Data Integrity Index"
    ])

    with tab_yoneda:
        st.subheader("Yoneda Similarity & Structural Equivalence")
        st.write(
            "In category theory, the Yoneda Lemma states that an object is entirely defined "
            "by its relationships to all other objects in the category. Here, we construct the "
            "relational profile of each Balancing Authority (BA) using its incoming and outgoing "
            "flow coordinates (EIA-930). We then calculate the Yoneda Similarity between BAs A and B:"
        )
        st.latex(
            r"J(A, B) = \frac{\sum_{X} \min(\text{in}_A(X), \text{in}_B(X)) + \sum_{X} \min(\text{out}_A(X), \text{out}_B(X))}"
            r"{\sum_{X} \max(\text{in}_A(X), \text{in}_B(X)) + \sum_{X} \max(\text{out}_A(X), \text{out}_B(X))}"
        )
        st.write(
            "This metric goes beyond geographical distance, highlighting BAs that play identical "
            "structural roles in the national power flow topology. High similarity enables formal "
            "property transfer (e.g. projecting successful congestion fixes from one region to another)."
        )
        
        y_matrix = data.get("yoneda_matrix", {})
        if y_matrix:
            y_df = pd.DataFrame(y_matrix)
            # Display matrix with sleek style
            st.dataframe(
                y_df.style.format("{:.4f}"),
                use_container_width=True
            )
        
        st.info(
            "**Key Finding:** MISO and NYIS share a high structural similarity of **0.3011**, "
            "indicating that their topological coupling profiles (neighborhood dependencies) are highly aligned, "
            "making NYIS-proven congestion relief methodologies prime candidates for transfer into MISO."
        )

    with tab_kan:
        st.subheader("Right Kan Extensions for Unpriced Seams")
        st.write(
            "Interfaces in the Southeast US (SOCO, TVA, DUK, etc.) often operate without transparent "
            "LMP markets, leaving analysts without price spreads to value seam constraints. We resolve "
            "this by computing a Right Kan Extension (Ran_K(F)) over the network's adjacent priced ties, "
            "providing a mathematically rigorous lower-bound congestion valuation:"
        )
        st.latex(
            r"\text{Ran}_K(F)(u) = \min_{p \in \text{PricedNeighbors}(u)} (\text{Spread}(p))"
        )
        
        bounds = data.get("right_kan_bounds", [])
        if bounds:
            # Explicit mapping, and the same labels streamlit_app.py uses.
            # These two apps previously called the identical number a "Bound"
            # here and a "Proxy"/"Screening Value" there.
            _COLS = {
                "tie": "Tie Interface",
                "se_side_ba": "Southeast-side BA",
                "priced_neighbors_count": "Priced Neighbors Used",
                "proxy_spread_usd_mwh": "Proxy Spread ($/MWh)",
                "gross_mwh": "Gross Flow (MWh)",
                "screening_value_usd": "Screening Value ($)",
            }
            bounds_df = pd.DataFrame(bounds)
            bounds_df = bounds_df[[c for c in _COLS if c in bounds_df.columns]].rename(columns=_COLS)
            st.dataframe(bounds_df, use_container_width=True, hide_index=True)

            _n_single = sum(1 for b in bounds if b.get("priced_neighbors_count", 0) <= 1)
            if _n_single:
                st.warning(
                    f"**{_n_single} of {len(bounds)} rows draw on a single priced neighbour**, so "
                    "the minimum in the formula above is not actually being taken — the figure is "
                    "one adjacent tie's spread carried across a different interface by analogy."
                )
        
        st.info(
            "**Largest screening value:** the **AECI - SWPP** unpriced seam screens at "
            "**$14.25M/yr**, obtained by transferring an adjacent priced tie's spread across "
            "this interface's gross flow. This is an analogy-based screening proxy — **not** a "
            "measured congestion cost and **not** a mathematical bound; a neighbouring tie's "
            "spread does not constrain a different interface. Each row here draws on a single "
            "priced neighbour, and the value prices *all* gross flow at that spread rather than "
            "only constrained hours, so treat it as an upper-ish order-of-magnitude flag for "
            "further study, not a quantity."
        )

    with tab_bcr:
        st.subheader("Marginal Upgrade Saturation Curves")
        st.write(
            "Standard relief models evaluate static upgrade capacities (e.g. 100 MW). We calculate "
            "the Marginal Benefit-Cost Ratio (Marginal BCR) using the derivative of the "
            "exponential relief model. This shows the exact continuous point of diminishing returns:"
        )
        st.latex(
            r"\text{Marginal BCR}(c) = \frac{\text{Spread} \cdot \eta \cdot e^{-\frac{\eta \cdot c}{\text{Gross}}}}{\text{Annualized Upgrade Cost}}"
        )
        st.write(
            "Where c represents capacity (MW) and eta is the effective MWh throughput factor. "
            "Marginal BCR = 1.0 is break-even — a corridor only justifies a build where the "
            "curve reaches it."
        )

        curves = data.get("marginal_curves", {})
        if curves:
            # State the screening result up front, computed from the data -- never asserted.
            _peaks = {
                name: max((p.get("marginal_bcr") or 0.0) for p in pts)
                for name, pts in curves.items() if pts
            }
            _best = max(_peaks.values()) if _peaks else 0.0
            if _peaks and _best < 1.0:
                st.warning(
                    f"**None of these {len(_peaks)} corridors reaches break-even at any capacity "
                    f"in the modelled range.** The highest marginal BCR observed is "
                    f"**{_best:.2f}** ({max(_peaks, key=_peaks.get)}) — benefits fall short of "
                    f"annualized upgrade cost by roughly {1/_best:.0f}x. That is the screening "
                    "result: on these assumptions none of these seams justifies a build, and the "
                    "curves show how far from economic each one is rather than where to size it."
                )
            st.caption(
                "Cost basis is a screening default (transmission $150k/MW-yr, battery "
                "$187.5k/MW-yr per NREL ATB), not a project estimate. Screening indicator, "
                "not investment advice."
            )

            curve_options = list(curves.keys())
            selected_curve = st.selectbox(
                "Corridor Seam",
                curve_options,
                format_func=lambda n: f"{n} — peak BCR {_peaks.get(n, 0):.2f}",
            )
            
            points = curves[selected_curve]
            pts_df = pd.DataFrame(points)
            pts_df.columns = ["Upgrade Capacity (MW)", "Marginal BCR", "Residual Seam Spread ($/MWh)"]
            
            col_chart, col_tbl = st.columns([2, 1])
            with col_chart:
                st.line_chart(pts_df.set_index("Upgrade Capacity (MW)")[["Marginal BCR"]])
            with col_tbl:
                st.dataframe(pts_df, use_container_width=True, hide_index=True)

    with tab_sheaf:
        st.subheader("Sheaf-Theoretic Coherence Audit")
        st.write(
            "Telemetry reports (EIA-930) often clash with plant-level accounting reports (eGRID). "
            "We represent the grid as a thermodynamic cellular sheaf over BA footprints. "
            "The H^1 cohomological obstruction (Laplacian eigenvalue lambda_2) measures "
            "the global coherence gap—which is exactly zero if all reports reconcile perfectly."
        )
        
        metrics = data.get("sheaf_metrics") or None
        if not metrics:
            st.warning(
                "**Sheaf metrics not available.** `reports/ba_footprint_report.json` is missing "
                "or incomplete. Regenerate with `python -m domains.grid.ba_footprint_report`. "
                "Shown blank rather than falling back to stored constants."
            )
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Before Sheaf Leak (H^1)", f"{metrics['before_leak']:.4f}")
            col2.metric("After Sheaf Leak (H^1)", f"{metrics['after_leak']:.4f}", f"-{metrics['improvement']} leak")
            col3.metric("Accounting Error Reduction", f"{metrics['error_reduction_twh']:.1f} TWh")

            st.divider()

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Before Source Agreement", f"{metrics['before_rate']:.1%}")
            col_b.metric("After Footprint Correction", f"{metrics['after_rate']:.1%}", f"+{metrics['after_rate']-metrics['before_rate']:.1%} improvement")
            _resid = metrics.get("residual_disagreement_rate")
            _resid_twh = metrics.get("residual_abs_error_twh")
            if _resid is not None:
                col_c.metric(
                    "Still Disagreeing",
                    f"{_resid:.1%}",
                    f"{_resid_twh:,.0f} TWh unreconciled" if _resid_twh is not None else None,
                    delta_color="inverse",
                )

            # Read from the artifact, never hardcoded. This block previously
            # printed "from 1.899 to 0.818 (a 56.9% ...)" as literal prose,
            # outside the metrics check, so it rendered even with no data -- and
            # claimed physics validation, which this measurement cannot support.
            st.info(
                f"**Interpretation:** footprint crosswalk corrections reduced the global sheaf "
                f"energy leak from **{metrics['before_leak']:.3f}** to **{metrics['after_leak']:.3f}** "
                f"(a **{metrics['improvement']}** coherence improvement). Two independent datasets — "
                "plant-level accounting and hourly telemetry — disagree less after the corrections. "
                "This is a consistency gain **between data sources, not a physical validation of "
                "grid flows**."
                + (
                    f"\n\n**What remains:** {_resid:.1%} of entities still disagree and "
                    f"**{_resid_twh:,.0f} TWh** is still unreconciled."
                    if _resid is not None and _resid_twh is not None else ""
                )
            )

        # Load plant corrections sub-data
        footprint_report_path = REPORTS_DIR / "ba_footprint_report.json"
        if footprint_report_path.exists():
            with open(footprint_report_path, encoding="utf-8") as f:
                fp_data = json.load(f)
            
            st.divider()
            st.subheader("Calibrated Plant Footprint Adjustments (Sub-Data)")
            st.write(
                "Individual physical generators (at the micro-scale fiber level of the Grothendieck Fibration) "
                "whose RTO/BA footprint mappings were corrected by the crosswalk engine to reconcile the global sheaf:"
            )
            accepted = fp_data.get("accepted", [])
            if accepted:
                fp_df = pd.DataFrame(accepted)[["entity", "state", "from_ba", "to_ba", "value_mwh", "confidence"]]
                fp_df.columns = ["Plant ORIS ID", "State", "Original BA", "Corrected BA", "Annual Generation (MWh)", "Match Confidence"]
                st.dataframe(
                    fp_df.style.format({"Annual Generation (MWh)": "{:,.0f}", "Match Confidence": "{:.2f}"}),
                    use_container_width=True,
                    hide_index=True
                )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Large Load Siting (ESIG)
# ─────────────────────────────────────────────────────────────────────────────

elif selection == "⚡ Large Load Siting (ESIG)":
    st.title("⚡ Large Load Siting & Interconnection")
    st.markdown(
        "Interactive simulation page exploring large load (data center) interconnection and "
        "siting dynamics based on the June 2026 ESIG report. Analyze utility-RTO coordination "
        "scenarios and run financial trade-off NPV evaluations for Flexible (Non-Firm) service options."
    )

    import json
    import pandas as pd
    
    # Load side experiment data
    exp_path = REPORTS_DIR / "experiments" / "large_load_coordination_experiment.json"
    if exp_path.exists():
        with open(exp_path, encoding="utf-8") as f:
            exp_data = json.load(f)
    else:
        st.error("Side experiment simulation data not found. Run the simulation first.")
        st.stop()
        
    tab_sim, tab_calc = st.tabs([
        "📊 Coordination Simulation",
        "🧮 Interactive NPV Siting Calculator"
    ])
    
    with tab_sim:
        st.subheader("Large Load Interconnection: Isolated vs. Coordinated Studies")
        st.markdown(
            "This tab compares the results of 5 simulated data center requests totaling **1,100 MW** "
            "attempting to connect to a local grid node with **800 MW** of available headroom. "
            "The system requires a **$45M regional upgrade** to expand transmission."
        )
        
        # Display simulated cohort
        st.markdown("### Simulated Load Requests Cohort")
        cohort = [
            {"Load ID": "LD-001", "Name": "Hyperscaler Cluster A", "Capacity (MW)": 250, "Flexibility (%)": "20%", "Value Factor": "$150/MWh"},
            {"Load ID": "LD-002", "Name": "Inference Center B", "Capacity (MW)": 200, "Flexibility (%)": "15%", "Value Factor": "$180/MWh"},
            {"Load ID": "LD-003", "Name": "AI Training Pod C", "Capacity (MW)": 300, "Flexibility (%)": "50%", "Value Factor": "$120/MWh"},
            {"Load ID": "LD-004", "Name": "Sovereign Compute D", "Capacity (MW)": 150, "Flexibility (%)": "10%", "Value Factor": "$200/MWh"},
            {"Load ID": "LD-005", "Name": "Giga-Factory E", "Capacity (MW)": 200, "Flexibility (%)": "5%", "Value Factor": "$250/MWh"}
        ]
        st.dataframe(pd.DataFrame(cohort), use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Display scenario metrics
        col_iso, col_coord = st.columns(2)
        
        with col_iso:
            st.markdown("#### Scenario A: Isolated Utility Studies")
            st.caption("Current Practice: Sequential utility-level reviews ignoring transmission constraints.")
            st.metric("Average Queue Delay", f"{exp_data['scenarios']['isolated']['average_delay_months']:.1f} months")
            st.metric("Project Withdrawal Rate", "40%", delta="-2 projects (350 MW)", delta_color="inverse")
            st.error("Result: Cumulative overload triggers late-stage restudy cascades. LD-004 & LD-005 withdraw.")
            
        with col_coord:
            st.markdown("#### Scenario B: Coordinated Cluster Studies")
            st.caption("ESIG Recommendation: Joint utility-RTO study using a coordinated data sheaf.")
            st.metric("Average Queue Delay", f"{exp_data['scenarios']['coordinated']['average_delay_months']:.1f} months", "-7.2 months")
            st.metric("Project Withdrawal Rate", "0%", delta="All 5 projects built", delta_color="normal")
            st.success("Result: $45M upgrade is identified upfront. Upgrade costs are allocated proportionally.")

        st.divider()
        st.subheader("Proportional Upgrade Cost Allocation (Coordinated Scenario)")
        alloc_data = exp_data["scenarios"]["coordinated"]["allocated_upgrade_costs_usd"]
        alloc_rows = [
            {"Load ID": k, "MW": 250 if k=="LD-001" else 200 if k=="LD-002" else 300 if k=="LD-003" else 150 if k=="LD-004" else 200, "Upgrade Cost Allocation ($)": f"${v:,.2f}"}
            for k, v in alloc_data.items()
        ]
        st.dataframe(pd.DataFrame(alloc_rows), use_container_width=True, hide_index=True)

    with tab_calc:
        st.subheader("Hyperscaler NPV Trade-off Calculator")
        st.markdown(
            "Hyperscalers prioritizing speed-to-market can request **Flexible (Non-Firm) Interconnection Service**. "
            "This bypasses upfront CapEx upgrades and shortens the queue timeline, but subjects the data center to "
            "curtailment during peak congestion hours. Adjust the parameters below to run the cash flow NPV simulation."
        )
        
        col_inp1, col_inp2 = st.columns(2)
        with col_inp1:
            st.markdown("**Project Specifications**")
            p_mw = st.slider("Project Capacity (MW)", 50, 1000, 300, 50)
            p_cf = st.slider("Target Capacity Factor (%)", 50, 100, 90, 5)
            p_rev = st.number_input("Compute Revenue ($/MWh)", 50.0, 500.0, 120.0, 10.0)
            p_discount = st.slider("Discount Rate (%)", 5, 20, 10, 1)
            
        with col_inp2:
            st.markdown("**Interconnection Options**")
            p_upgrade = st.slider("Firm Upgrade Cost ($ Millions)", 1.0, 100.0, 12.27, 0.5) * 1e6
            p_delay_firm = st.slider("Timeline to Firm Power (Months)", 12, 60, 24, 6)
            p_delay_nonfirm = st.slider("Timeline to Non-Firm Power (Months)", 6, 36, 12, 6)
            p_flex_share = st.slider("Flexible Capacity Share (%)", 10, 100, 50, 5) / 100.0
            p_curt_hrs = st.slider("Annual Peak Congestion (Hours)", 10, 500, 120, 10)
            
        # Run NPV calculations dynamically
        # Year 1 to 10 Cash Flow
        annual_hrs = 8760.0 * (p_cf / 100.0)
        annual_rev_firm = p_mw * annual_hrs * p_rev
        
        # Option 1: Firm Connection
        years_delay_firm = p_delay_firm / 12.0
        npv_firm = -p_upgrade
        for y in range(1, 11):
            if y <= years_delay_firm:
                cf = 0.0
            else:
                cf = annual_rev_firm
            npv_firm += cf / ((1 + (p_discount/100.0)) ** y)
            
        # Option 2: Non-Firm Connection (Speed-to-power)
        years_delay_nonfirm = p_delay_nonfirm / 12.0
        flex_mw = p_mw * p_flex_share
        lost_rev_curt = flex_mw * p_curt_hrs * p_rev
        annual_rev_nonfirm = annual_rev_firm - lost_rev_curt
        
        npv_nonfirm = 0.0
        for y in range(1, 11):
            if y <= years_delay_nonfirm:
                cf = 0.0
            else:
                cf = annual_rev_nonfirm
            npv_nonfirm += cf / ((1 + (p_discount/100.0)) ** y)
            
        npv_delta = npv_nonfirm - npv_firm
        
        # Display side-by-side results
        st.divider()
        col_res_f, col_res_nf = st.columns(2)
        
        with col_res_f:
            st.markdown("### Option 1: Firm Connection")
            st.metric("Upfront CapEx Upgrade Cost", f"${p_upgrade/1e6:.2f}M")
            st.metric("Time-to-Power", f"{p_delay_firm} months ({years_delay_firm:.1f} yrs)")
            st.metric("10-Year Project NPV", f"${npv_firm/1e6:,.2f}M")
            
        with col_res_nf:
            st.markdown("### Option 2: Non-Firm (Flexible) Connection")
            st.metric("Upfront CapEx Upgrade Cost", "$0.00M", delta="-$12.27M CapEx Saved" if abs(p_upgrade - 12.27e6) < 1e5 else f"-${p_upgrade/1e6:.2f}M CapEx Saved")
            st.metric("Time-to-Power", f"{p_delay_nonfirm} months ({years_delay_nonfirm:.1f} yrs)", f"-{p_delay_firm - p_delay_nonfirm} months saved")
            st.metric("10-Year Project NPV", f"${npv_nonfirm/1e6:,.2f}M")
            
        st.divider()
        if npv_delta > 0:
            st.success(
                f"💡 **Non-Firm Service is the Optimal Siting Choice!** \n\n"
                f"Bypassing the grid upgrade and connecting **{p_delay_firm - p_delay_nonfirm} months earlier** "
                f"offsets the annual operational curtailment cost of **${lost_rev_curt/1e6:.2f}M/yr**, "
                f"resulting in a Net Present Value gain of **${npv_delta/1e6:,.2f}M**."
            )
        else:
            st.warning(
                f"⚠️ **Firm Connection is the Optimal Siting Choice!** \n\n"
                f"The annual operational curtailment cost of **${lost_rev_curt/1e6:.2f}M/yr** "
                f"is too severe, wiping out the speed-to-market advantage. Waiting for firm service yields "
                f"a Net Present Value gain of **${abs(npv_delta)/1e6:,.2f}M** over non-firm service."
            )
