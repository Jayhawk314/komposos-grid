from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

import streamlit as st


# --- CONSTANTS & CONFIG ---
CONTACT_EMAIL = "jhawk314@gmail.com"
ASSET_DIR = Path(__file__).parent / "assets"
HERO_IMAGE = ASSET_DIR / "komposos-system-map.png"
REGISTRY_PATH = Path(__file__).parent / "ecosystem_registry.json"

st.set_page_config(
    page_title="James Hawkins | KOMPOSOS",
    page_icon="⚗",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- DATA LOADING ---
def load_registry():
    if not REGISTRY_PATH.exists():
        st.error(f"Registry file not found: {REGISTRY_PATH}")
        return {"projects": [], "engines": [], "pipeline_layers": []}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Load registry on every run to ensure no staleness
REGISTRY = load_registry()


# --- STYLING ---
def apply_custom_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #edeff2;
            --muted: #94a3b8;
            --paper: #020617;
            --line: #1e293b;
            --teal: #a855f7;
            --blue: #8b5cf6;
            --red: #f43f5e;
            --gold: #22c55e;
            --green: #10b981;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1200px;
            background-color: var(--paper);
        }
        h1, h2, h3, h4 { color: var(--ink); font-weight: 800; }
        p, li { color: var(--ink); line-height: 1.6; }

        /* Hero Section */
        .hero-wrap {
            border: 1px solid var(--line);
            background: linear-gradient(135deg, #0f172a 0%, #020617 100%);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
        }
        .kicker {
            color: var(--gold);
            font-weight: 900;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.1em;
            margin-bottom: 0.5rem;
        }
        .hero-title {
            font-size: clamp(2rem, 5vw, 3.5rem);
            line-height: 1.1;
            margin: 0;
            color: #ffffff;
        }
        .hero-subtitle {
            font-size: 1.15rem;
            max-width: 800px;
            color: var(--muted);
            margin-top: 1rem;
        }

        /* Common Components */
        .tile {
            border: 1px solid var(--line);
            border-left: 4px solid var(--teal);
            background: #0f172a;
            border-radius: 8px;
            padding: 1.25rem;
            height: 100%;
        }
        .tile-number { font-size: 2rem; font-weight: 900; color: #ffffff; }
        .tile-label { color: var(--muted); font-size: 0.95rem; margin-top: 0.5rem; }

        .tag {
            display: inline-block;
            border: 1px solid var(--line);
            background: #1e293b;
            border-radius: 4px;
            padding: 0.2rem 0.6rem;
            margin: 0 0.4rem 0.4rem 0;
            color: var(--muted);
            font-size: 0.8rem;
            font-weight: 600;
        }
        .note {
            border: 1px solid var(--line);
            background: #1e1b4b;
            border-left: 5px solid var(--teal);
            border-radius: 8px;
            padding: 1.5rem;
            color: #e0e7ff;
            margin: 1.5rem 0;
        }
        .card-title { color: #ffffff; font-weight: 800; font-size: 1.2rem; margin-bottom: 0.5rem; }
        .card-short { color: var(--teal); font-weight: 700; font-size: 0.95rem; margin-bottom: 0.8rem; }
        .card-summary { color: var(--muted); font-size: 0.95rem; margin-bottom: 1rem; }

        /* Sidebar Tweaks */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid var(--line);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_tags(tags: list[str]) -> str:
    return "".join(f'<span class="tag">{tag}</span>' for tag in tags)


def mailto_link(subject: str, body: str) -> str:
    return f"mailto:{CONTACT_EMAIL}?subject={quote(subject)}&body={quote(body)}"


# --- PAGE RENDERERS ---

def render_home():
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="kicker">Independent AI-native systems builder</div>
            <h1 class="hero-title">KOMPOSOS: Turning Messy Possibility into Explainable Next Actions.</h1>
            <p class="hero-subtitle">
            A universal compositional reasoning framework for high-stakes research,
            industrial infrastructure, and formal foundations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if HERO_IMAGE.exists():
        st.image(str(HERO_IMAGE), use_container_width=True)
    else:
        st.warning("Hero image missing: assets/komposos-system-map.png")

    st.markdown("## The 5-Layer Pipeline")
    st.info("Every system in the ecosystem follows this shared mathematical path to transform raw data into verified insight.")

    cols = st.columns(len(REGISTRY["pipeline_layers"]))
    for col, layer in zip(cols, REGISTRY["pipeline_layers"]):
        with col:
            st.markdown(
                f"""
                <div class="tile">
                    <div class="tile-number">{layer['num']}</div>
                    <div class="card-title" style="color:var(--gold);">{layer['name']}</div>
                    <div class="tile-label">{layer['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    left, right = st.columns([1, 1])
    with left:
        st.markdown("### The Domain Intersection")
        st.write(
            "Systems are not isolated; they share **Categorical Bridges**. "
            "For example, the chemistry logic in `3D-chem` bridges into `MANF` "
            "to verify the curing integrity of aerospace sealants."
        )
        st.code(
            "Bridges: \n"
            "  CHEM ➞ MANF (Material Integrity)\n"
            "  BIT ➞ GDELT (Actor Risk Flow)\n"
            "  MATH ➞ SIMON (Formal Verification)",
            language="text"
        )
    with right:
        st.markdown("### Latest Verification Feed")
        st.markdown(
            """
            <div style="background:#0f172a; padding:1rem; border-radius:8px; border:1px solid var(--line);">
                <div style="color:var(--green); font-family:monospace; font-size:0.85rem;">
                [PASS] PRONOIA: No sheaf contradictions in WESyS CA grid.<br>
                [PASS] COG: ZFC gatekeeper verified GDELT-2026-06-06.<br>
                [WARN] OPTIMUS: 3 missing morphisms detected in MANF thread.<br>
                [INFO] SIMON: Starting formal proof roadmap for CHEM-v4.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_shared_core():
    st.header("Shared Core Machinery")
    st.write(
        "These four engines provide the 'Categorical Runtime' for the entire ecosystem. "
        "They handle the heavy lifting of routing, auditing, and optimization."
    )

    for engine in REGISTRY["engines"]:
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"### {engine['name']}")
                st.write(f"**{engine['short']}**")
            with col2:
                st.write(engine['summary'])
                st.markdown(render_tags(engine['features']), unsafe_allow_html=True)
            st.divider()


def render_project_page(project_id: str):
    project = next((p for p in REGISTRY["projects"] if p["id"] == project_id), None)
    if not project:
        st.error(f"Project {project_id} not found.")
        return

    st.title(project["name"])
    st.subheader(project["short"])

    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown("### The Problem")
        st.write(project["problem"])

        st.markdown("### What It Gives")
        st.success(project["what_it_gives"])

        st.markdown("### Categorical Mapping")
        st.info(project["categorical_mapping"])

        st.markdown("### Proof-of-Work Signals")
        for item in project["proof"]:
            st.markdown(f"- {item}")

    with col2:
        st.markdown("### Identity & State")
        st.markdown(render_tags([project["domain"], project["stage"]] + project["audiences"]), unsafe_allow_html=True)

        st.markdown("**Caveat**")
        st.warning(project["caveat"])

        st.markdown("**Core Engines Used**")
        st.write(", ".join(project["engines_used"]))

        st.markdown("**Local Proof Path**")
        st.code(project["local"], language="text")

        # Links
        links = []
        if project.get("demo"):
            links.append(("Open demo", project["demo"]))
        if project.get("repo"):
            links.append(("Open repo", project["repo"]))

        if links:
            for label, url in links:
                st.link_button(label, url, use_container_width=True)
        else:
            st.caption("No public links recorded yet.")


# --- NEW PAGES (added this session): maturity map + journey ---
# These are purely additive. They do not change any existing page or the CSS;
# the map/journey read an optional "maturity" field on each registry project.

MATURITY = {
    "Live":      {"sym": "◆", "color": "#22c55e", "blurb": "deployed — you can use it right now"},
    "Works":     {"sym": "●", "color": "#38bdf8", "blurb": "runs end-to-end, produces real output"},
    "Demo":      {"sym": "◐", "color": "#a855f7", "blurb": "a runnable demonstration of one idea"},
    "Prototype": {"sym": "○", "color": "#f59e0b", "blurb": "partial and exploratory"},
    "Sketch":    {"sym": "·", "color": "#64748b", "blurb": "an idea I chased for a while"},
}
LADDER = ["Live", "Works", "Demo", "Prototype", "Sketch"]


def _maturity_of(project: dict) -> str:
    return project.get("maturity", "Sketch")


def _badge(maturity: str) -> str:
    m = MATURITY.get(maturity, MATURITY["Sketch"])
    return (
        f'<span style="display:inline-block;font-weight:800;font-size:0.72rem;'
        f'letter-spacing:0.06em;text-transform:uppercase;padding:0.18rem 0.55rem;'
        f'border-radius:999px;color:{m["color"]};border:1px solid {m["color"]}55;'
        f'background:{m["color"]}14;">{m["sym"]} {maturity}</span>'
    )


def render_map():
    projects = REGISTRY["projects"]
    n = len(projects)
    n_runnable = sum(1 for p in projects if _maturity_of(p) in ("Live", "Works", "Demo"))
    domains = sorted({p["domain"] for p in projects if p.get("domain")})

    st.title("The Map")
    st.write(
        "An honest map of everything in the ecosystem, sorted by how far each one "
        "actually got. Finished things are marked finished; the rough ones say so. "
        "**Pick any project in the sidebar to dive in.**"
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Experiments", n)
    c2.metric("You can run", n_runnable)
    c3.metric("Domains", len(domains))
    c4.metric("Shared engines", len(REGISTRY.get("engines", [])))

    legend = "  ".join(
        f'<span style="color:{MATURITY[k]["color"]};font-weight:700;">'
        f'{MATURITY[k]["sym"]} {k}</span>'
        for k in LADDER
    )
    st.markdown(legend, unsafe_allow_html=True)
    st.divider()

    for rung in LADDER:
        group = [p for p in projects if _maturity_of(p) == rung]
        if not group:
            continue
        m = MATURITY[rung]
        st.markdown(
            f'<h3 style="color:{m["color"]};margin-bottom:0.2rem;">{m["sym"]} {rung}'
            f'<span style="color:#94a3b8;font-weight:500;font-size:0.9rem;"> — '
            f'{m["blurb"]}</span></h3>',
            unsafe_allow_html=True,
        )
        for p in group:
            st.markdown(
                f'<div style="border:1px solid #1e293b;background:#0b1220;'
                f'border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.5rem;">'
                f'<span style="color:#fff;font-weight:800;">{p["name"]}</span>'
                f'&nbsp;&nbsp;{_badge(_maturity_of(p))}'
                f'&nbsp;<span style="color:#94a3b8;font-size:0.8rem;">'
                f'{p.get("domain", "")}</span><br>'
                f'<span style="color:#94a3b8;font-size:0.9rem;">'
                f'{p.get("short", "")}</span></div>',
                unsafe_allow_html=True,
            )


def render_journey():
    st.title("How it grew")
    st.write(
        "A short, honest history of one stubborn idea — told in the order I "
        "actually figured things out."
    )
    st.divider()

    st.markdown("### ① KOMPOSOS — the seed")
    st.write(
        "It started small: a categorical reasoning kernel. Facts as **objects**, "
        "relationships as **morphisms**, confidence baked into the arrows themselves. "
        "The bet was simple and a little reckless — that *composition*, the thing "
        "category theory cares about more than anything, could be turned into an "
        "**audit method**. If two things claim to connect but don't compose, "
        "something is wrong. Find the gap, and you've found the bug, the leak, or "
        "the missing step."
    )

    st.markdown("### ② KOMPOSOS-III — the math years")
    st.write(
        "The kernel wasn't enough, so I went deep. III is where the heavy machinery "
        "landed: homotopy type theory, persistent homology, Ricci curvature, an "
        "inference oracle with a dozen strategies, ZFC set-theoretic checks. Most of "
        "it I learned by building it badly first. A lot of those folders are dead "
        "ends — and that's the point of this stage. III is where I found out which "
        "mathematics actually *did work* on real problems and which was just pretty."
    )

    st.markdown("### ③ KOMPOSOS-IV — the architecture")
    st.write(
        "Once the math earned its keep, IV gave it a spine: a layered runtime where "
        "a plugin framework, the categorical core, a higher-categorical layer, a "
        "verification co-processor, and a self-refinement loop each do one job and "
        "hand off cleanly. This is the version that stopped being a pile of scripts "
        "and started being a *system* — something I could point at a new domain "
        "without rewriting from scratch."
    )

    st.markdown("### ④ The domains — the sprawl")
    st.write(
        "Then I let it loose. Drug repurposing. Aerospace process integrity. "
        "Geopolitical risk. Climate signals. Energy grids. Each one is the same core "
        "wearing a different coat. Some clicked into something live and useful; most "
        "are honest prototypes; a few are weekend sketches I haven't let go of. The "
        "Map sorts them by exactly how far each one actually got."
    )

    counts = {r: sum(1 for p in REGISTRY["projects"] if _maturity_of(p) == r) for r in LADDER}
    chips = "  ".join(
        f'<span style="color:{MATURITY[r]["color"]};font-weight:700;">'
        f'{MATURITY[r]["sym"]} {counts[r]} {r}</span>'
        for r in LADDER if counts[r]
    )
    st.markdown(
        f'<div style="margin-top:0.6rem;color:#94a3b8;">Where they stand today: '
        f'&nbsp; {chips}</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("### Where it's going")
    st.write(
        "Inward, not outward. The next stage isn't more domains — it's pulling the "
        "strongest ones into clean, defensible cores: a small formal math layer with "
        "real failure examples, and two or three domain demos that hold up to an "
        "expert poking at them. The rest stays on the Map as what it is — the trail "
        "of how I got here."
    )


# --- SIDEBAR & ROUTING ---

apply_custom_css()

with st.sidebar:
    st.title("KOMPOSOS")
    st.caption("A Proof-of-Work Ecosystem.")

    nav_selection = st.radio(
        "Navigation",
        ["Home", "Shared Core"]
        + [p["id"] for p in REGISTRY["projects"]]
        + ["🗺 The Map", "📖 How it grew"]
    )

    st.divider()
    st.info("This is a data-driven portfolio. Adding a new system only requires updating the registry.")

# Routing Logic
if nav_selection == "Home":
    render_home()
elif nav_selection == "Shared Core":
    render_shared_core()
elif nav_selection == "🗺 The Map":
    render_map()
elif nav_selection == "📖 How it grew":
    render_journey()
else:
    render_project_page(nav_selection)
