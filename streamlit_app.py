from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Komposos Grid — Independent Interconnection Analytics",
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

    /* Data provenance badges */
    .prov-badge {
        display: inline-block;
        border-radius: 5px;
        padding: 3px 10px;
        font-size: 10px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: 10px;
        margin-right: 6px;
    }
    .prov-measured  { background: #052e16; border: 1px solid #22c55e; color: #22c55e; }
    .prov-derived   { background: #1e2a05; border: 1px solid #f59e0b; color: #f59e0b; }
    .prov-simulated { background: #2e0a16; border: 1px solid #f87171; color: #f87171; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── helpers ──────────────────────────────────────────────────────────────────

ROOT_DIR   = Path(__file__).parent
DOCS_DIR   = ROOT_DIR / "docs"
REPORTS_DIR = ROOT_DIR / "reports"
REGISTRY_PATH = REPORTS_DIR / "stitch_sessions" / "registry.json"

REGION_DISPLAY = {
    "miso": "MISO", "ercot": "ERCOT", "pjm": "PJM", "caiso": "CAISO",
    "spp": "SPP", "nyiso": "NYISO", "iso_ne": "ISO-NE",
    "southeast": "Southeast (non-market)", "west": "West (non-ISO)",
}

def _load_session_registry() -> list:
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            return json.load(f).get("sessions", [])
    return []

def _load_html(path: Path, height: int = 900) -> None:
    if path.exists():
        st.components.v1.html(path.read_text(encoding="utf-8"), height=height, scrolling=True)
    else:
        st.error(f"File not found: `{path}`")
        st.caption("Run the corresponding generator script to produce this file — see the README.")

def _stitch_badge(text: str) -> None:
    st.markdown(
        f'<div class="stitch-badge">⚡ Independent analysis · i2X STITCH · {text}</div>',
        unsafe_allow_html=True,
    )

_PROV_LABELS = {
    "measured": "📏 Measured",
    "derived": "🧮 Derived",
    "simulated": "🧪 Simulated",
}

def _provenance_badge(kind: str, source: str) -> None:
    """Tag a figure or section with its data provenance tier.

    measured  — reconciles to a published external dataset (e.g. LBNL Queued Up)
    derived   — computed by our models from measured inputs or user parameters
    simulated — stylized/illustrative scenario; numbers are not observations
    """
    label = _PROV_LABELS.get(kind, kind.title())
    st.markdown(
        f'<span class="prov-badge prov-{kind}">{label}</span>'
        f'<span style="font-size:11px;color:#94a3b8;">{source}</span>',
        unsafe_allow_html=True,
    )

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚡ Komposos Grid")
    st.caption("Independent analytics · follows the DOE i2X STITCH series")
    st.divider()

    # ── STITCH session selector (driven by reports/stitch_sessions/registry.json) ──
    st.markdown("**i2X STITCH Sessions**")
    _sessions = _load_session_registry()
    _session_labels = [
        f"{s['id']} · {s['title']}" + (" ✅" if s.get("status") == "held" else " 🔜")
        for s in _sessions
    ] or ["2026-06-23 · Regional Study Processes"]
    stitch_session = st.selectbox(
        "Meeting",
        _session_labels,
        help="DOE i2X STITCH collaboration meeting series — edit "
             "reports/stitch_sessions/registry.json to add or update sessions",
    )

    st.divider()

    # ── Main nav ──────────────────────────────────────────────────────────
    selection = st.radio(
        "Dashboard",
        [
            "📊 Regional Queue Study",
            "🗺️ Harmonization Matrix",
            "📅 STITCH Session Notes",
            "⚡ Grid Network Map",
            "📈 Seam Congestion Findings",
            "📖 Grid Map Manual",
            "🎯 Seam Opportunity Screen",
            "⚡ Large Load Siting (ESIG)",
            "⚛️ Nuclear Enrichment Bottlenecks",
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
        "Independent project prepared to support the **i2X STITCH** conversation on "
        "interconnection study harmonization. **Not affiliated with or endorsed by "
        "DOE, ESIG, or Berkeley Lab.**"
    )
    st.caption("Data: LBNL Queued Up · EIA-930 · eGRID")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Regional Queue Study
# ─────────────────────────────────────────────────────────────────────────────

if selection == "📊 Regional Queue Study":
    _stitch_badge("Regional Interconnection Queue Studies")
    st.title("📊 Regional Interconnection Queue Studies")
    _provenance_badge(
        "measured",
        "LBNL Queued Up (data through 2026) — headline rates reconcile to the published sheets to the integer.",
    )

    st.markdown(
        "Prepared for the i2X STITCH collaboration, exploring interconnection study "
        "processes and cycle timelines across all major US grid regions. "
        "Headline numbers match Berkeley Lab's own *Queued Up* definitions."
    )

    # ── Context tabs ──────────────────────────────────────────────────────
    tab_report, tab_context, tab_export = st.tabs(
        ["📄 Full Brief", "🔍 Session Context", "⬇️ Export"]
    )

    with tab_report:
        # Load queue brief data
        brief_json_path = REPORTS_DIR / "stitch_2026-06-23" / "queue_process_brief.json"
        if brief_json_path.exists():
            with open(brief_json_path, encoding="utf-8") as f:
                brief_data = json.load(f)

            # ── The IA-Certainty Spectrum (cross-region lead figure) ──────
            st.subheader("🎚️ The IA-Certainty Spectrum")
            st.markdown(
                "**What is an executed Interconnection Agreement actually worth?** "
                "The same contract milestone carries very different completion "
                "information depending on where it is signed — the June 23 "
                "MISO/ERCOT finding, extended to all nine LBNL regions."
            )

            def _mo(entry) -> str:
                med = (entry or {}).get("median_months")
                return f"{med:.1f} mo" if med is not None else "—"

            spec_rows = []
            for r0 in brief_data.get("regions", []):
                pia0 = r0.get("post_ia") or {}
                lbnl0 = r0.get("completion_lbnl") or {}
                dur0 = r0.get("durations") or {}
                tracked = bool(pia0.get("signed_decided"))
                spec_rows.append({
                    "Region": REGION_DISPLAY.get(r0["region"], r0["region"].upper()),
                    "Requests": f"{r0.get('total_requests') or 0:,}",
                    "LBNL Completion": f"{lbnl0.get('rate') or 0:.1%}",
                    "Post-IA Completion": (f"{pia0['rate']:.1%}" if tracked else "— (not tracked)"),
                    "Study (Req→IA)": _mo(dur0.get("ir_to_ia")),
                    "Build (IA→COD)": _mo(dur0.get("ia_to_cod")),
                    "_sort": -(pia0.get("rate") or 0) if tracked else 1.0,
                })
            spec_df = pd.DataFrame(
                sorted(spec_rows, key=lambda x: x["_sort"])
            ).drop(columns=["_sort"])
            st.dataframe(spec_df, use_container_width=True, hide_index=True)
            st.caption(
                "“Not tracked” is a finding, not a pipeline gap: that region's LBNL records "
                "do not record IA execution for withdrawn projects, so the milestone's "
                "certainty content cannot be computed there — evidence that milestone data "
                "coverage itself needs harmonizing. Shareable per-region packs: "
                "`python -m domains.grid.run_region_packs`."
            )

            st.divider()

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
            col_b.metric("Active in Queue", f"{r['active_in_queue']:,}")
            col_c.metric("LBNL Completion (2000-2020)", f"{r['completion_lbnl']['rate']:.1%}")
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
        st.subheader("Key Structural Differences (Sample Regions)")
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
        "A cross-region comparison grid assembled to support the i2X STITCH harmonization conversation."
    )
    st.warning(
        "**Uncited working hypothesis.** Every cell below was hand-assembled by the author from "
        "public process documents and session impressions — none has yet been sourced to a specific "
        "tariff, business practice manual, or RTO presentation. Treat this as a discussion draft, "
        "not a measured deliverable, and verify any cell before quoting it."
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
            "**Takeaway from the June 23 session (author's notes):** The 'cluster' study construct "
            "(used by MISO, PJM, SPP) does not exist in ERCOT's serial queue model. "
            "This structural asymmetry means direct timeline comparisons are misleading "
            "without normalizing for queue grouping methodology."
        )

        st.markdown(
            "**Additional takeaways (author's notes — verify against the session "
            "recording before quoting):**"
        )
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

    # ── Upcoming sessions (from reports/stitch_sessions/registry.json) ────
    _upcoming = [s for s in _load_session_registry() if s.get("status") != "held"]
    if _upcoming:
        st.subheader("🔜 Upcoming Sessions")
        up_cols = st.columns(len(_upcoming))
        for up_col, s in zip(up_cols, _upcoming):
            with up_col:
                st.markdown(f"**{s['id']}**")
                st.caption(s.get("title", ""))
                presenters = s.get("presenters", [])
                if presenters:
                    st.markdown("*Presenters:* " + "; ".join(presenters))
                checklist = s.get("prep_checklist", [])
                if checklist:
                    st.markdown("**Prep checklist:**")
                    for item in checklist:
                        st.markdown(f"- {item}")
        st.caption(
            "When ESIG announces presenters, update "
            "`reports/stitch_sessions/registry.json` — this page and the sidebar follow."
        )
        st.divider()

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
        st.caption(
            "Author's takeaways from attending the session — not official minutes. "
            "Verify against the ESIG recording before quoting or attributing to a presenter."
        )
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

elif selection == "🎯 Seam Opportunity Screen":
    _stitch_badge("Economic Seam Screening & Optimization")
    st.title("🎯 Seam Opportunity Screening")
    st.markdown(
        "Surfacing hidden grid value and identifying high-priority transmission and storage upgrades. "
        "These are screening indicators computed from public flow and price data — "
        "starting points for further study, not measured congestion costs and not investment advice."
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

            # Highest off-diagonal pair, read from the report artifact (never hardcoded)
            best_pair = None
            for a in y_df.columns:
                for b in y_df.columns:
                    if a < b and pd.notna(y_df.loc[a, b]):
                        if best_pair is None or y_df.loc[a, b] > best_pair[2]:
                            best_pair = (a, b, float(y_df.loc[a, b]))
            if best_pair:
                st.info(
                    f"**Highest structural overlap:** {best_pair[0]} and {best_pair[1]} at "
                    f"**{best_pair[2]:.4f}** (flow-profile Jaccard similarity). This is a moderate "
                    "overlap — enough to nominate the pair as *screening candidates* for comparing "
                    "congestion-relief approaches, but it is a starting point for study, not proof "
                    "that a fix proven in one region will transfer to the other."
                )

    with tab_kan:
        st.subheader("Right Kan Extensions for Unpriced Seams")
        st.markdown(
            r"Interfaces in the Southeast US (SOCO, TVA, DUK, etc.) often operate without transparent "
            r"LMP markets, leaving analysts without price spreads to value seam constraints. As a "
            r"**screening proxy**, we transfer the smallest spread among the network's *adjacent priced ties* "
            r"across the unpriced interface (formally organized as a Right Kan Extension, $\text{Ran}_K(F)$):"
        )
        st.latex(
            r"\text{Ran}_K(F)(u) = \min_{p \in \text{PricedNeighbors}(u)} (\text{Spread}(p))"
        )
        
        bounds = data.get("right_kan_bounds", [])
        if bounds:
            bounds_df = pd.DataFrame(bounds)
            bounds_df.columns = ["Tie Interface", "Unpriced BA", "Priced Neighbors", "Proxy Spread ($/MWh)", "Gross Flow (MWh)", "Screening Value ($)"]
            st.dataframe(
                bounds_df,
                use_container_width=True,
                hide_index=True
            )

            top = max(bounds, key=lambda b: b.get("bound_value_usd", 0))
            st.info(
                f"**Largest screening value:** the **{top['tie']}** unpriced seam screens at "
                f"**${top['bound_value_usd']/1e6:.1f}M/yr**, obtained by transferring an adjacent "
                f"priced tie's spread (${top['bound_spread_usd_mwh']:.2f}/MWh) across this interface's "
                "gross flow. This is an analogy-based screening proxy — **not** a measured congestion "
                "cost and **not** a mathematical bound; a neighboring tie's spread does not constrain a "
                "different interface. These seams remain `structural_only` in the waste ledger until "
                "priced or planning-grade evidence exists on the tie itself."
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
            
        if metrics:
            st.info(
                f"**Interpretation:** footprint crosswalk corrections reduced the global sheaf "
                f"energy leak from **{metrics['before_leak']:.3f}** to **{metrics['after_leak']:.3f}** "
                f"(a **{metrics['improvement']}** coherence improvement). Concretely: the two "
                "independent datasets — plant-level accounting and hourly telemetry — disagree "
                "substantially less after the corrections. This is a consistency gain between data "
                "sources, not a physical validation of grid flows."
            )

        # Load plant corrections sub-data
        footprint_report_path = REPORTS_DIR / "ba_footprint_report.json"
        if footprint_report_path.exists():
            with open(footprint_report_path, encoding="utf-8") as f:
                fp_data = json.load(f)
            
            st.divider()
            st.subheader("Calibrated Plant Footprint Adjustments (Sub-Data)")
            st.markdown(
                "Individual physical generators whose RTO/BA footprint mappings were corrected "
                "by the crosswalk engine to reconcile the datasets:"
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
    _stitch_badge("Large Load Siting & Interconnection Simulation")
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
    
    # Cohort and scenario facts all come from the experiment JSON — regenerate with
    # `python -m domains.grid.experiments.large_load_coordination`.
    cohort = exp_data.get("cohort", [])
    mw_by_id = {l["id"]: l["mw"] for l in cohort}
    total_mw = exp_data.get("queue_total_mw", sum(mw_by_id.values()))
    headroom_mw = exp_data.get("headroom_mw", 0)
    upgrade_cost = exp_data.get("upgrade_cost_usd", 0.0)
    iso = exp_data["scenarios"]["isolated"]
    coord = exp_data["scenarios"]["coordinated"]

    with tab_sim:
        st.subheader("Large Load Interconnection: Isolated vs. Coordinated Studies")
        _provenance_badge(
            "simulated",
            exp_data.get("provenance", {}).get(
                "source", "Stylized scenario after the June 2026 ESIG Large Loads report."
            ),
        )
        st.markdown(
            f"This tab compares the results of {len(cohort)} simulated data center requests totaling "
            f"**{total_mw:,} MW** attempting to connect to a local grid node with **{headroom_mw:,} MW** "
            f"of available headroom. The system requires a **${upgrade_cost/1e6:.0f}M regional upgrade** "
            "to expand transmission."
        )

        # Display simulated cohort
        st.markdown("### Simulated Load Requests Cohort")
        cohort_rows = [
            {
                "Load ID": l["id"],
                "Name": l["name"],
                "Capacity (MW)": l["mw"],
                "Flexibility (%)": f"{l['flexibility']:.0%}",
                "Value Factor": f"${l['rev_per_mw_hr']}/MWh",
            }
            for l in cohort
        ]
        st.dataframe(pd.DataFrame(cohort_rows), use_container_width=True, hide_index=True)

        st.divider()

        # Display scenario metrics
        iso_withdrawn = iso.get("withdrawn_projects", [])
        iso_withdrawn_mw = sum(mw_by_id.get(pid, 0) for pid in iso_withdrawn)
        iso_withdraw_rate = len(iso_withdrawn) / len(cohort) if cohort else 0.0
        coord_withdrawn = coord.get("withdrawn_projects", [])
        coord_withdraw_rate = len(coord_withdrawn) / len(cohort) if cohort else 0.0
        delay_saved = iso["average_delay_months"] - coord["average_delay_months"]

        col_iso, col_coord = st.columns(2)

        with col_iso:
            st.markdown("#### Scenario A: Isolated Utility Studies")
            st.caption("Current Practice: Sequential utility-level reviews ignoring transmission constraints.")
            st.metric("Average Queue Delay", f"{iso['average_delay_months']:.1f} months")
            st.metric(
                "Project Withdrawal Rate",
                f"{iso_withdraw_rate:.0%}",
                delta=f"-{len(iso_withdrawn)} projects ({iso_withdrawn_mw:,} MW)",
                delta_color="inverse",
            )
            st.error(
                "Result: Cumulative overload triggers late-stage restudy cascades. "
                f"{' & '.join(iso_withdrawn)} withdraw."
            )

        with col_coord:
            st.markdown("#### Scenario B: Coordinated Cluster Studies")
            st.caption("ESIG Recommendation: Joint utility-RTO study using a coordinated data sheaf.")
            st.metric(
                "Average Queue Delay",
                f"{coord['average_delay_months']:.1f} months",
                f"-{delay_saved:.1f} months",
            )
            st.metric(
                "Project Withdrawal Rate",
                f"{coord_withdraw_rate:.0%}",
                delta=f"All {len(cohort) - len(coord_withdrawn)} projects built",
                delta_color="normal",
            )
            st.success(
                f"Result: ${upgrade_cost/1e6:.0f}M upgrade is identified upfront. "
                "Upgrade costs are allocated proportionally."
            )

        st.divider()
        st.subheader("Proportional Upgrade Cost Allocation (Coordinated Scenario)")
        alloc_data = coord["allocated_upgrade_costs_usd"]
        alloc_rows = [
            {"Load ID": k, "MW": mw_by_id.get(k, "—"), "Upgrade Cost Allocation ($)": f"${v:,.2f}"}
            for k, v in alloc_data.items()
        ]
        st.dataframe(pd.DataFrame(alloc_rows), use_container_width=True, hide_index=True)

    with tab_calc:
        st.subheader("Hyperscaler NPV Trade-off Calculator")
        _provenance_badge(
            "derived",
            "10-year cash-flow model computed from the parameters you set below — not observed data.",
        )
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
            st.metric("Upfront CapEx Upgrade Cost", "$0.00M", delta=f"-${p_upgrade/1e6:.2f}M CapEx Saved")
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

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Nuclear Enrichment Bottlenecks
# ─────────────────────────────────────────────────────────────────────────────

elif selection == "⚛️ Nuclear Enrichment Bottlenecks":
    import importlib
    import sys
    # Force reload of nuclear modules to clear cached versions in Streamlit
    for mod in list(sys.modules.keys()):
        if mod.startswith("domains.nuclear"):
            try:
                importlib.reload(sys.modules[mod])
            except Exception:
                pass

    _stitch_badge("Nuclear Enrichment Bottlenecks")
    st.title("⚛️ Civilian Nuclear Enrichment Bottlenecks")

    st.markdown(
        "Hyperscalers prioritizing carbon-free compute are funding next-generation Small Modular Reactors (SMRs). "
        "Many advanced designs require **High-Assay Low-Enriched Uranium (HALEU)**. "
        "Western commercial HALEU capacity is currently far below projected SMR fleet needs — Centrus's Piketon, OH "
        "plant produces demonstration-scale quantities (on the order of ~900 kg/yr), with larger expansions still "
        "years out — so advanced reactors remain fuel-constrained. "
        "This page uses an **illustrative systems model** to reason about supply-chain interventions and timelines."
    )
    _provenance_badge(
        "simulated",
        "Stylized supply-chain model — facility names are real; capacities, flows, and confidence "
        "weights are illustrative inputs, not measured data.",
    )

    st.divider()

    # --- TABS FOR DIFFERENT VIEWPORTS ---
    tab_sim, tab_scenarios, tab_portfolio = st.tabs([
        "📅 SMR Timeline Simulator", 
        "📊 Scenario Comparison Matrix", 
        "🎯 Prioritized Relief Actions"
    ])

    with tab_sim:
        st.subheader("Interactive What-If SMR Timeline Simulator")
        st.markdown(
            "Model the time-delay gap between Urenco's centrifuge expansion and your data center's SMR startup date. "
            "Adjust the timelines below to compute the categorical confidence score for fuel delivery."
        )

        col_timeline_inp, col_timeline_res = st.columns([1, 1])

        with col_timeline_inp:
            st.markdown("**Timeline Configuration**")
            smr_date = st.slider("Target SMR Reactor Startup Year", 2026, 2036, 2028, 1)
            urenco_date = st.slider("Urenco Centrifuge Cascade Completion Year", 2026, 2036, 2032, 1)
            
            st.markdown("**Flow Performance**")
            conversion_stability = st.slider("Conversion Facility Stability (Metropolis)", 10, 100, 45, 5) / 100.0
            fabrication_stability = st.slider("Westinghouse Fuel Fabrication Stability", 50, 100, 90, 5) / 100.0

        with col_timeline_res:
            st.markdown("**Categorical Claim Check Results**")
            
            # Build the custom Category
            from core.category import Category
            from cog.session import CogSession
            from cog.engine import CogEngine
            from cog.schema import CogClaim

            cat = Category(name="web_simulator", db_path=":memory:")
            cat.add("mine:mcclean", type_name="mine")
            cat.add("conversion:metropolis", type_name="conversion_facility")
            cat.add("urenco:eunice", type_name="enrichment_facility")
            cat.add("fabrication:columbia", type_name="fabrication_facility")
            cat.add("reactor:smr", type_name="reactor")
            cat.add("demand:hyperscaler_dc", type_name="demand")

            # Determine temporal mismatch confidence
            if urenco_date <= smr_date:
                mismatch_confidence = 0.90
                st.success("✅ Timelines align: Centrifuge cascades are ready before SMR startup.")
            else:
                mismatch_confidence = 0.05
                st.error(f"❌ Timeline mismatch: Cascades are completed in {urenco_date}, but SMR requires fuel by {smr_date}. Physical delay is {urenco_date - smr_date} years.")

            # Connect morphisms
            cat.connect("mine:mcclean", "conversion:metropolis", name="processes_to", confidence=0.95)
            cat.connect("conversion:metropolis", "urenco:eunice", name="processes_to", confidence=conversion_stability)
            cat.connect("urenco:eunice", "fabrication:columbia", name="processes_to", confidence=mismatch_confidence)
            cat.connect("fabrication:columbia", "reactor:smr", name="powers", confidence=fabrication_stability)
            cat.connect("reactor:smr", "demand:hyperscaler_dc", name="powers", confidence=0.85)

            session = CogSession(category=cat)
            cog = CogEngine(session=session)
            claim = CogClaim(
                source="mine:mcclean",
                target="demand:hyperscaler_dc",
                relation="powers",
                confidence=0.50
            )
            result = cog.check_claim(claim)

            # Calculate the actual path weight (Multiplicative Quantale tensor product)
            opt_path = cat.optimal_path("mine:mcclean", "demand:hyperscaler_dc")
            if opt_path:
                path_nodes, path_weight = opt_path
            else:
                path_weight = 0.0

            # Display metrics
            st.metric("System-Wide Fuel Confidence", f"{result.confidence:.3f}", help="Topological score based on graph path length and count.")
            st.metric("Physical Path Throughput Yield", f"{path_weight:.3f}", delta=f"{path_weight - 0.038:+.3f} vs baseline", help="The multiplicative product of all connection confidences along the path (Quantale weight).")
            st.info(f"**Cognitive Verdict:** {result.status.value.upper()}")
            st.caption(f"**Compositional Proof Path:** {result.supporting_paths}")

    with tab_scenarios:
        st.subheader("5-Part Scenario Incoherence Matrix")
        st.markdown(
            "This matrix compares the Fiedler spectral connectivity (coupling strength) and claim checks across "
            "different industry configurations. Note how **Dual Intervention** is required to unlock real capacity."
        )

        from domains.nuclear.run_comprehensive_analysis import configure_scenario_category
        
        matrix_rows = []
        for key, name in [
            ("baseline", "Baseline 2026 Constraints"),
            ("accelerated_enrichment", "Scenario A: Accelerated Centrifuges (ACT-002)"),
            ("upgraded_conversion", "Scenario B: Upgraded Conversion (ACT-001)"),
            ("dual_intervention", "Scenario C: Dual Intervention (ACT-001 + ACT-002)"),
            ("supply_disruption", "Scenario D: Severe Conversion Disruption"),
        ]:
            scenario_cat = configure_scenario_category(key)
            from domains.nuclear.flow_geometry import analyze_enrichment_geometry
            geom = analyze_enrichment_geometry(scenario_cat)
            
            # Cognitive claim
            session = CogSession(category=scenario_cat)
            cog = CogEngine(session=session)
            claim = CogClaim(
                source="enrichment:urenco_eunice",
                target="demand:hyperscaler_dc",
                relation="powers",
                confidence=0.50
            )
            check_res = cog.check_claim(claim)
            
            # Calculate the actual path weight (Multiplicative Quantale tensor product)
            opt_path = scenario_cat.optimal_path("mine:mcclean_lake", "demand:hyperscaler_dc")
            path_yield = opt_path[1] if opt_path else 0.0

            matrix_rows.append({
                "Scenario Name": name,
                "Fiedler Connectivity": f"{geom.fiedler_value:.5f}",
                "Claim Status": check_res.status.value.upper(),
                "Claim Confidence": f"{check_res.confidence:.3f}",
                "Path Yield (Dynamic)": f"{path_yield:.4f}",
            })

        st.table(pd.DataFrame(matrix_rows).set_index("Scenario Name"))
        st.caption("Fiedler values close to 0 denote weak, vulnerable networks. Higher values show cohesive supply chains.")

    with tab_portfolio:
        st.subheader("Prioritized Interventions for Bottleneck Relief")
        st.markdown("Translating mathematical constraints into decision-ready business packages.")

        col_act1, col_act2, col_act3 = st.columns(3)

        with col_act1:
            st.error("### ACT-001: CRITICAL")
            st.markdown("**Conversion Capacity Expansion**")
            st.caption("Target Node: Metropolis ConverDyn")
            st.markdown(
                "The domestic conversion facility is a high-risk, single-point bottleneck. "
                "**Proposed Action:** Co-fund facility upgrades or secure long-term European conversion contracts."
            )

        with col_act2:
            st.warning("### ACT-002: HIGH")
            st.markdown("**Centrifuge Cascade Acceleration**")
            st.caption("Target Node: Urenco Eunice")
            st.markdown(
                "Centrifuge cascade construction queues limit downstream output. "
                "**Proposed Action:** Coordinate federal DPA capital to pull construction forward from 2032 to 2029."
            )

        with col_act3:
            st.success("### ACT-003: MEDIUM")
            st.markdown("**Tails Re-enrichment**")
            st.caption("Target Node: Co-located SMRs")
            st.markdown(
                "Depleted uranium tails can be re-enriched to supply HALEU. "
                "**Proposed Action:** Contract firm, low-cost power (e.g. co-located generation or "
                "off-peak supply) for secondary enrichment cascades. *Note: centrifuge plants require "
                "continuous, high-reliability power — intermittent curtailment energy cannot directly "
                "run enrichment cascades.*"
            )

