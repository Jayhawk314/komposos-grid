from __future__ import annotations

from pathlib import Path
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
            "📊 MISO vs ERCOT Queue Study",
            "📈 Seam Congestion Findings",
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

elif selection == "📊 MISO vs ERCOT Queue Study":
    st.title("📊 MISO vs. ERCOT Interconnection Study Process")
    st.write(
        "A detailed comparison of regional study processes, milestone funnels, and cycle trends "
        "based on LBNL Queued Up data through 2026. This was prepared for the i2X STITCH webinar."
    )
    
    brief_path = REPORTS_DIR / "stitch_2026-06-23" / "queue_process_brief.html"
    if brief_path.exists():
        html_content = brief_path.read_text(encoding="utf-8")
        st.components.v1.html(html_content, height=900, scrolling=True)
    else:
        st.error(
            "queue_process_brief.html not found. Please run the following command to generate it:\n"
            "`python -m domains.grid.run_stitch_brief --queue domains/grid/data/LBNL_Ix_Queue_Data_File_thru2026.xlsx --out reports/stitch_2026-06-23`"
        )

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
