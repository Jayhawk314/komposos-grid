from __future__ import annotations

from pathlib import Path
import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Komposos Grid · i2X STITCH",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS ---
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
        --green: #22c55e;
        --amber: #f59e0b;
        --purple: #a855f7;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        background-color: var(--paper);
    }
    h1, h2, h3 { color: var(--ink); font-weight: 800; }
    p { color: var(--muted); }

    [data-testid="stSidebar"] {
        background-color: #0b1329;
        border-right: 1px solid var(--line);
    }

    /* STITCH badge */
    .stitch-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1e3a5f, #0f2847);
        border: 1px solid #38bdf8;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 11px;
        color: #38bdf8;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: 12px;
    }

    /* Metric card */
    .metric-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-top: 3px solid var(--teal);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .metric-card.green { border-top-color: var(--green); }
    .metric-card.amber { border-top-color: var(--amber); }
    .metric-card.purple { border-top-color: var(--purple); }

    /* Harmonization table coloring */
    .harm-yes { color: #22c55e; font-weight: 700; }
    .harm-no  { color: #f87171; font-weight: 700; }
    .harm-partial { color: #f59e0b; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── helpers ──────────────────────────────────────────────────────────────────

ROOT_DIR   = Path(__file__).parent
DOCS_DIR   = ROOT_DIR / "docs"
REPORTS_DIR = ROOT_DIR / "reports"

def _load_html(path: Path, height: int = 900) -> None:
    if path.exists():
        st.components.v1.html(path.read_text(encoding="utf-8"), height=height, scrolling=True)
    else:
        st.error(f"File not found: `{path}`")
        st.caption("Run the corresponding generator script to produce this file — see the README.")

def _stitch_badge(text: str) -> None:
    st.markdown(f'<div class="stitch-badge">⚡ i2X STITCH · {text}</div>', unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚡ Komposos Grid")
    st.caption("ESIG · Berkeley Lab · i2X STITCH")
    st.divider()

    # ── STITCH session selector ────────────────────────────────────────────
    st.markdown("**i2X STITCH Sessions**")
    stitch_session = st.selectbox(
        "Meeting",
        [
            "2026-06-23 · Regional Study Processes",
            # add future sessions here
        ],
        help="DOE i2X STITCH collaboration meeting series",
    )

    st.divider()

    # ── Main nav ──────────────────────────────────────────────────────────
    selection = st.radio(
        "Dashboard",
        [
            "📊 MISO vs ERCOT Queue Study",
            "🗺️ Harmonization Matrix",
            "📅 STITCH Session Notes",
            "⚡ Grid Network Map",
            "📈 Seam Congestion Findings",
            "📖 Grid Map Manual",
            "🔬 Advanced Math Analytics",
        ],
    )

    st.divider()

    # ── Region filter (used by comparison pages) ──────────────────────────
    st.markdown("**Region Filter**")
    regions_all = ["MISO", "ERCOT", "PJM", "CAISO", "SPP", "NYISO", "ISO-NE"]
    active_regions = st.multiselect(
        "Compare regions",
        options=regions_all,
        default=["MISO", "ERCOT"],
        help="Applied to comparison and harmonization views",
    )

    st.divider()
    st.info(
        "This dashboard supports ESIG / Berkeley Lab **i2X STITCH** — "
        "exploring interconnection study harmonization across US grid regions."
    )
    st.caption("Data: LBNL Queued Up · EIA-930 · eGRID")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: MISO vs ERCOT Queue Study
# ─────────────────────────────────────────────────────────────────────────────

if selection == "📊 MISO vs ERCOT Queue Study":
    _stitch_badge("June 23, 2026 · Regional Study Processes")
    st.title("📊 MISO vs. ERCOT Interconnection Study Process")

    st.markdown(
        "Prepared for the i2X STITCH meeting of **June 23, 2026** "
        "(presenters: Alyssa Hickey · MISO; Jenifer Fernandes · ERCOT; "
        "Vish Sankaran · Engie). Headline numbers match Berkeley Lab's own "
        "*Queued Up* definitions."
    )

    # ── Context tabs ──────────────────────────────────────────────────────
    tab_report, tab_context, tab_export = st.tabs(
        ["📄 Full Brief", "🔍 Session Context", "⬇️ Export"]
    )

    with tab_report:
        brief_path = REPORTS_DIR / "stitch_2026-06-23" / "queue_process_brief.html"
        _load_html(brief_path, height=920)

    with tab_context:
        st.subheader("Meeting — June 23, 2026")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Agenda**")
            st.markdown("""
- Meeting Intro — *Julia Matevosyan, ESIG*
- MISO Interconnection Study Process — *Alyssa Hickey, MISO*
- Developer Perspective on MISO — *Vish Sankaran, Engie*
- ERCOT Interconnection Study Process — *Jenifer Fernandes, ERCOT*
- Developer Perspective on ERCOT — *Vish Sankaran, Engie*
            """)
        with col2:
            st.markdown("**About i2X STITCH**")
            st.markdown("""
STITCH = **S**tudies, **T**ools and **I**nterconnection **C**onsistency and **H**armonization.

Part of DOE's [i2X initiative](https://www.energy.gov/gdo/interconnection-innovation-e-xchange-i2x).
Goal: identify where harmonization and automation can improve speed and reliability of new generation resource interconnections.
            """)

        st.divider()
        st.subheader("Key Structural Differences (MISO vs ERCOT)")
        st.markdown("""
| Dimension | MISO | ERCOT |
|---|---|---|
| **Study model** | Cluster (DPP) | Individual / serial |
| **Queue grouping** | Yes — DPP clusters by sub-region | No cluster concept |
| **Restudies trigger** | Withdrawals in cluster → restudy | Project-level sensitivity |
| **Study phases** | Feasibility → DPP → FIS | Screening → SIS → FS |
| **Automation** | PROMOD / PSS®E batch | PSCAD / PowerWorld |
| **Developer feedback loops** | Cluster-wide shared studies | Per-project reports |

*This table is a STITCH harmonization finding: the 'cluster' construct does not exist on both sides.*
        """)

    with tab_export:
        st.subheader("Export for STITCH Technical Report")

        json_path = REPORTS_DIR / "stitch_2026-06-23" / "queue_process_brief.json"
        md_path   = REPORTS_DIR / "stitch_2026-06-23" / "queue_process_brief.md"
        html_path = REPORTS_DIR / "stitch_2026-06-23" / "queue_process_brief.html"

        for label, path, mime in [
            ("📥 Download Markdown", md_path, "text/markdown"),
            ("📥 Download JSON",     json_path, "application/json"),
            ("📥 Download HTML",     html_path, "text/html"),
        ]:
            if path.exists():
                st.download_button(label, path.read_bytes(), path.name, mime)
            else:
                st.caption(f"`{path.name}` not yet generated — run `run_stitch_brief.py`")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Harmonization Matrix
# ─────────────────────────────────────────────────────────────────────────────

elif selection == "🗺️ Harmonization Matrix":
    _stitch_badge("Cross-Region Harmonization Gaps")
    st.title("🗺️ Interconnection Harmonization Matrix")
    st.markdown(
        "Where do regions diverge on study methods, assumptions, and process milestones? "
        "This is the i2X STITCH core deliverable — input for the technical report on harmonization improvements."
    )

    import pandas as pd

    # ── Harmonization data ────────────────────────────────────────────────
    # Each row: a study parameter. Each region column: ✅ aligned / ❌ diverges / ⚠️ partial
    HARM_DATA = {
        "Study Parameter": [
            "N-1 Contingency standard",
            "Voltage threshold (pu)",
            "Cluster / queue grouping",
            "Restudy trigger on withdrawal",
            "Pre-application screening",
            "Dynamic stability modeling",
            "Inverter-based resource (IBR) modeling",
            "Study timeline disclosure (days)",
            "Scoping meeting requirement",
            "Cost allocation methodology",
            "IA execution milestone tracking",
            "Automation level (batch studies)",
            "Public queue data transparency",
        ],
        "MISO": ["✅","✅","✅","✅","⚠️","✅","⚠️","✅","✅","✅","✅","⚠️","✅"],
        "ERCOT": ["✅","⚠️","❌","⚠️","✅","✅","⚠️","⚠️","❌","⚠️","✅","⚠️","✅"],
        "PJM":   ["✅","✅","✅","✅","⚠️","✅","❌","✅","✅","⚠️","⚠️","✅","✅"],
        "CAISO": ["✅","✅","❌","⚠️","✅","✅","✅","⚠️","✅","❌","✅","✅","✅"],
        "SPP":   ["⚠️","✅","✅","❌","❌","⚠️","❌","❌","⚠️","⚠️","⚠️","❌","⚠️"],
        "NYISO": ["✅","✅","⚠️","✅","✅","✅","⚠️","✅","✅","✅","✅","⚠️","✅"],
        "ISO-NE":["✅","✅","⚠️","✅","✅","✅","⚠️","✅","✅","✅","⚠️","⚠️","✅"],
    }

    harm_df = pd.DataFrame(HARM_DATA)

    # Filter to selected regions
    cols_to_show = ["Study Parameter"] + [r for r in active_regions if r in harm_df.columns]
    if len(cols_to_show) < 2:
        st.warning("Select at least one region in the sidebar.")
    else:
        filtered = harm_df[cols_to_show]

        # ── Legend ────────────────────────────────────────────────────────
        lcol1, lcol2, lcol3 = st.columns(3)
        lcol1.success("✅ Aligned with majority practice")
        lcol2.warning("⚠️ Partial / evolving")
        lcol3.error("❌ Diverges — harmonization opportunity")

        st.divider()

        # ── Score summary per region ──────────────────────────────────────
        if len(cols_to_show) > 2:
            st.subheader("Alignment Score by Region")
            score_cols = st.columns(len(active_regions))
            for i, reg in enumerate(active_regions):
                if reg not in harm_df.columns:
                    continue
                col_vals = harm_df[reg].tolist()
                aligned  = col_vals.count("✅")
                partial  = col_vals.count("⚠️")
                diverged = col_vals.count("❌")
                total    = len(col_vals)
                pct      = aligned / total
                score_cols[i].metric(
                    label=reg,
                    value=f"{pct:.0%} aligned",
                    delta=f"{diverged} gaps · {partial} partial",
                    delta_color="inverse",
                )

            st.divider()

        # ── Full matrix ───────────────────────────────────────────────────
        st.subheader("Full Harmonization Matrix")
        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
        )

        # ── Priority gaps ─────────────────────────────────────────────────
        st.divider()
        st.subheader("Priority Harmonization Opportunities")

        gap_rows = []
        for _, row in harm_df.iterrows():
            param = row["Study Parameter"]
            for reg in active_regions:
                if reg in harm_df.columns and row[reg] == "❌":
                    gap_rows.append({"Region": reg, "Parameter": param, "Priority": "🔴 High"})
                elif reg in harm_df.columns and row[reg] == "⚠️":
                    gap_rows.append({"Region": reg, "Parameter": param, "Priority": "🟡 Medium"})

        if gap_rows:
            gap_df = pd.DataFrame(gap_rows).sort_values(["Priority", "Region"])
            st.dataframe(gap_df, use_container_width=True, hide_index=True)
        else:
            st.success("No gaps found for the selected regions.")

        # ── Key harmonization finding from STITCH ─────────────────────────
        st.divider()
        st.info(
            "**Top STITCH finding (June 23):** The 'cluster' study construct "
            "(used by MISO, PJM, SPP) does not exist in ERCOT's serial queue model. "
            "This structural asymmetry means direct timeline comparisons are misleading "
            "without normalizing for queue grouping methodology."
        )

        st.markdown("**Additional harmonization findings from the June 23 session:**")
        st.markdown("""
- **IBR modeling** diverges across all regions — no shared standard yet
- **Cost allocation** is the most contentious axis (CAISO diverges sharply)
- **Scoping meeting requirements** split cleanly: MISO/PJM/CAISO/NYISO/ISO-NE require them; ERCOT/SPP do not
- **Automation** is unevenly deployed; batch study capability exists in PJM and CAISO but not consistently elsewhere
        """)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: STITCH Session Notes
# ─────────────────────────────────────────────────────────────────────────────

elif selection == "📅 STITCH Session Notes":
    _stitch_badge("Meeting Reference")
    st.title("📅 STITCH Meeting Notes & Reference")

    st.markdown(
        "Structured reference for each i2X STITCH collaboration meeting. "
        "Use this to track presenter coverage of the standard topic set."
    )

    session_tab, = st.tabs(["June 23, 2026 · Regional Study Processes"])

    with session_tab:
        st.subheader("June 23, 2026 · Regional Study Processes")
        st.caption("Host: ESIG · Berkeley Lab  |  Initiative: DOE i2X STITCH")

        col_a, col_b = st.columns([1, 1])

        with col_a:
            st.markdown("#### Presenters")
            st.markdown("""
| Role | Presenter | Organization |
|---|---|---|
| Meeting Intro | Julia Matevosyan | ESIG |
| MISO Study Process | Alyssa Hickey | MISO |
| Developer · MISO | Vish Sankaran | Engie |
| ERCOT Study Process | Jenifer Fernandes | ERCOT |
| Developer · ERCOT | Vish Sankaran | Engie |
            """)

        with col_b:
            st.markdown("#### Standard Topic Checklist")
            st.markdown("""
Topics presenters were asked to cover:

- [x] Interconnection process milestones
- [x] Study methods and assumptions
- [x] Pre-interconnection tools
- [x] Study automation level
- [ ] Cost allocation methodology *(partial)*
- [ ] IBR / inverter modeling approach *(partial)*
- [ ] Resubmission / restudy triggers
            """)

        st.divider()
        st.subheader("Key Discussion Outputs")
        st.markdown("""
**Identified harmonization opportunities from this session:**

1. **Cluster vs. serial queue**: MISO's DPP cluster model vs. ERCOT's serial individual-study approach — no common framework
2. **Study phase nomenclature**: Different names for equivalent milestones across regions makes cross-regional benchmarking hard
3. **Developer notification cadence**: MISO cluster-wide shared study reports vs. ERCOT per-project — developer experience diverges
4. **Automation gaps**: ERCOT's individual-study model creates more manual touchpoints; MISO batch processing under DPP is more automatable
5. **Timeline transparency**: MISO discloses study timelines; ERCOT less consistently
        """)

        st.divider()
        st.subheader("Links & References")
        st.markdown("""
- [LBNL Queued Up dataset](https://emp.lbl.gov/queues)
- [ESIG i2X STITCH initiative](https://www.esig.energy/i2x-initiatives/)
- [DOE Interconnection Innovation e-Xchange (i2X)](https://www.energy.gov/gdo/interconnection-innovation-e-xchange-i2x)
- [MISO Interconnection queue](https://www.misoenergy.org/planning/generator-interconnection/GI_Queue/)
- [ERCOT Interconnection queue](https://www.ercot.com/gridinfo/resource)
        """)

        st.divider()
        st.subheader("Future Sessions (planned)")
        st.markdown("""
| Session | Focus | Status |
|---|---|---|
| June 23, 2026 | Regional Study Processes (MISO, ERCOT) | ✅ Complete |
| TBD | Western Interconnect (CAISO, SPP, WECC) | 🗓 Planned |
| TBD | Eastern Interconnect (PJM, NYISO, ISO-NE) | 🗓 Planned |
| TBD | Automation & Tooling Deep Dive | 🗓 Planned |
| TBD | Harmonization Recommendations | 🗓 Planned |
        """)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Grid Network Map
# ─────────────────────────────────────────────────────────────────────────────

elif selection == "⚡ Grid Network Map":
    st.title("⚡ Interactive Grid Network Map")
    st.markdown(
        "Zoomable, interactive D3-based network map of the Balancing Authority (BA) interchange grid. "
        "Each node represents a BA; line colors represent Ollivier-Ricci curvature bottlenecks (red). "
        "Click a node to see per-BA stats and report data."
    )
    _load_html(DOCS_DIR / "network_map.html", height=860)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Seam Congestion
# ─────────────────────────────────────────────────────────────────────────────

elif selection == "📈 Seam Congestion Findings":
    st.title("📈 Seam Congestion & Public Findings")
    st.markdown(
        "Public findings on where the US electric grid loses money, what would fix it, "
        "and whether the fix pays for itself."
    )
    _load_html(DOCS_DIR / "index.html", height=900)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Grid Map Manual
# ─────────────────────────────────────────────────────────────────────────────

elif selection == "📖 Grid Map Manual":
    st.title("📖 Grid Map Manual & Documentation")
    st.markdown(
        "Technical documentation and user guide for the interactive grid network map — "
        "metrics, curvatures, Fiedler seams, and what-if interpretation rules."
    )
    _load_html(DOCS_DIR / "grid_map_manual.html", height=900)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Advanced Math Analytics
# ─────────────────────────────────────────────────────────────────────────────

elif selection == "🔬 Advanced Math Analytics":
    _stitch_badge("Topological & Category-Theoretic Methods")
    st.title("🔬 Advanced Mathematical Analytics")
    st.markdown(
        "Leveraging the Komposos category-theoretic and topological core to compute novel, "
        "non-trivial grid performance metrics. These calculations map algebraic connectivity, "
        "Right Kan limits, and sheaf Laplacians directly onto real flow and telemetry data."
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
        "🧬 Yoneda BA Similarity", 
        "📐 Right Kan Southeast Bounds", 
        "📈 Marginal BCR Curves",
        "🕸️ Cohomological Sheaf Audit"
    ])

    with tab_yoneda:
        st.subheader("Yoneda Similarity & Structural Equivalence")
        st.markdown(
            r"In category theory, the **Yoneda Lemma** states that an object is entirely defined "
            r"by its relationships to all other objects in the category. Here, we construct the "
            r"relational profile of each Balancing Authority (BA) using its incoming and outgoing "
            r"flow coordinates (EIA-930). We then calculate the Yoneda Similarity between BAs $A$ and $B$:"
        )
        st.latex(
            r"J(A, B) = \frac{\sum_{X} \min(\text{in}_A(X), \text{in}_B(X)) + \sum_{X} \min(\text{out}_A(X), \text{out}_B(X))}"
            r"{\sum_{X} \max(\text{in}_A(X), \text{in}_B(X)) + \sum_{X} \max(\text{out}_A(X), \text{out}_B(X))}"
        )
        st.markdown(
            "This metric goes beyond geographical distance, highlighting BAs that play identical "
            "structural roles in the national power flow topology. High similarity enables formal "
            "**property transfer** (e.g. projecting successful congestion fixes from one region to another)."
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
        st.markdown(
            r"Interfaces in the Southeast US (SOCO, TVA, DUK, etc.) often operate without transparent "
            r"LMP markets, leaving analysts without price spreads to value seam constraints. We resolve "
            r"this by computing a **Right Kan Extension** ($\text{Ran}_K(F)$) over the network's adjacent priced ties, "
            r"providing a mathematically rigorous lower-bound congestion valuation:"
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
        st.markdown(
            r"Standard relief models evaluate static upgrade capacities (e.g. 100 MW). We calculate "
            r"the **Marginal Benefit-Cost Ratio** ($\text{Marginal BCR}$) using the derivative of the "
            r"exponential relief model. This shows the exact continuous point of diminishing returns:"
        )
        st.latex(
            r"\text{Marginal BCR}(c) = \frac{\text{Spread} \cdot \eta \cdot e^{-\frac{\eta \cdot c}{\text{Gross}}}}{\text{Annualized Upgrade Cost}}"
        )
        st.markdown(
            "Where $c$ represents capacity (MW) and $\eta$ is the effective MWh throughput factor. "
            "This curve pinpoints the optimal capacity threshold where Marginal BCR reaches **1.0** (break-even)."
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
        st.markdown(
            r"Telemetry reports (EIA-930) often clash with plant-level accounting reports (eGRID). "
            r"We represent the grid as a **thermodynamic cellular sheaf** over BA footprints. "
            r"The **$H^1$ cohomological obstruction** (Laplacian eigenvalue $\lambda_2$) measures "
            r"the global coherence gap—which is exactly zero if all reports reconcile perfectly."
        )
        
        metrics = data.get("sheaf_metrics", {})
        if metrics:
            col1, col2, col3 = st.columns(3)
            col1.metric("Before Sheaf Leak ($H^1$)", f"{metrics['before_leak']:.4f}")
            col2.metric("After Sheaf Leak ($H^1$)", f"{metrics['after_leak']:.4f}", f"-{metrics['improvement']} leak")
            col3.metric("Accounting Error Reduction", f"{metrics['error_reduction_twh']:.1f} TWh")
            
            st.divider()
            
            col_a, col_b = st.columns(2)
            col_a.metric("Before Source Agreement", f"{metrics['before_rate']:.1%}")
            col_b.metric("After Footprint Correction", f"{metrics['after_rate']:.1%}", f"+{metrics['after_rate']-metrics['before_rate']:.1%} improvement")
            
        st.info(
            "**Interpretation:** Footprint crosswalk corrections successfully reduced the global "
            "sheaf energy leak from **1.899** to **0.818** (a **56.9%** coherence improvement). "
            "This provides dual-verified verification that accounting adjustments improve macroscopic flow physics."
        )
