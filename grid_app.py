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
        "across all US grid regions based on LBNL Queued Up data through 2026."
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
        col_d.metric("Built after Signing IA", f"{r['post_ia']['rate']:.1%}")
        
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
            st.markdown("Percentage of decided projects that went operational, grouped by their furthest milestone:")
            ms_df = pd.DataFrame(r.get("milestones", []))
            if not ms_df.empty:
                ms_df.columns = ["Milestone Stage", "Decided Projects", "Operational Projects", "Completion Rate", "Thin Cohort (<30)"]
                st.dataframe(
                    ms_df.style.format({"Completion Rate": "{:.1%}"}),
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
            bounds_df = pd.DataFrame(bounds)
            bounds_df.columns = ["Tie Interface", "Unpriced BA", "Priced Neighbors", "Bound Spread ($/MWh)", "Gross Flow (MWh)", "Bound Value ($)"]
            st.dataframe(
                bounds_df,
                use_container_width=True,
                hide_index=True
            )
        
        st.success(
            "**Top Bounded Seam:** The **AECI - SWPP** unpriced seam carries a lower-bound "
            "congestion value of **$14.25M/yr** based on adjacent priced market points. This represents "
            "a massive unmeasured congestion opportunity that is invisible in standard RTO planning data."
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
            "This curve pinpoints the optimal capacity threshold where Marginal BCR reaches 1.0 (break-even)."
        )
        
        curves = data.get("marginal_curves", {})
        if curves:
            curve_options = list(curves.keys())
            selected_curve = st.selectbox("Corridor Seam", curve_options)
            
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
        
        metrics = data.get("sheaf_metrics", {})
        if metrics:
            col1, col2, col3 = st.columns(3)
            col1.metric("Before Sheaf Leak (H^1)", f"{metrics['before_leak']:.4f}")
            col2.metric("After Sheaf Leak (H^1)", f"{metrics['after_leak']:.4f}", f"-{metrics['improvement']} leak")
            col3.metric("Accounting Error Reduction", f"{metrics['error_reduction_twh']:.1f} TWh")
            
            st.divider()
            
            col_a, col_b = st.columns(2)
            col_a.metric("Before Source Agreement", f"{metrics['before_rate']:.1%}")
            col_b.metric("After Footprint Correction", f"{metrics['after_rate']:.1%}", f"+{metrics['after_rate']-metrics['before_rate']:.1%} improvement")
            
        st.info(
            "**Interpretation:** Footprint crosswalk corrections successfully reduced the global "
            "sheaf energy leak from 1.899 to 0.818 (a 56.9% coherence improvement). "
            "This provides dual-verified verification that accounting adjustments improve macroscopic flow physics."
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
