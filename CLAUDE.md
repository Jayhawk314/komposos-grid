# CLAUDE.md - Grid app build and command reference

## Project Overview
This repository (`komposos-grid`) contains the **STITCH Grid Interconnection & Seam screening platform**. It performs topological similarity matching (Yoneda Similarity), unpriced boundary shadow pricing (Right Kan Extensions), sheaf-theoretic data auditing (Sheaf Laplacian Cohomology), and interconnection queue funnel analysis (MISO DPP vs. ERCOT C&M).

## Common Developer Commands

### Environment Setup
```bash
pip install pandas pytest streamlit
```

### Running Backend Analytical Pipelines
*   **Run Seam Opportunity Analytics:**
    ```bash
    python -m domains.grid.run_untapped_analytics
    ```
*   **Run 9-Region Interconnection Queue Study:**
    ```bash
    python -m domains.grid.run_stitch_brief --with-peers
    ```
*   **Run Large Load Interconnection Simulation (ESIG):**
    ```bash
    python -m domains.grid.experiments.large_load_coordination
    ```
*   **Generate Static HTML Dashboard:**
    ```bash
    python -m domains.grid.run_dashboard
    ```
*   **Generate Per-Region STITCH Engagement Packs (all 9 regions + IA-certainty index):**
    ```bash
    python -m domains.grid.run_region_packs
    ```
    Session registry for the STITCH webinar series: `reports/stitch_sessions/registry.json`.

### Launching the Dashboard App
```bash
streamlit run streamlit_app.py
```

### MCP Server (grounded tools for coding agents)
```bash
# stdio MCP server wrapping domains/grid/agent_tools.py (requires: pip install "mcp[cli]")
python -m domains.grid.mcp_server
```
Project-scoped config lives in `.mcp.json`; Claude Code picks it up automatically. Tools: `ba`, `tie`, `path`, `similar`, `bottlenecks`, `seam`, `whatif`, `gaps`, `explain`, `manifest`.

### Agent Skills (`.claude/skills/`)
*   **`/verify-claim <claim>`** — fact-check a queue metric against the repo's artifacts (recomputes from the raw workbook if needed). Note the provenance boundary: LBNL completion reconciles to their Sheet 25; post-IA and durations are our own computation, since LBNL publishes post-IA nationally only.
*   **`/large-load-scenario`** — re-run the ESIG large-load simulation with new headroom/cost/cohort parameters; the Streamlit page renders the refreshed JSON.
*   **`/webinar-prep`** — regenerate all pipelines, diff figures against the committed baseline, and draft a pre-read brief for the next STITCH session.

The large-load experiment CLI accepts `--headroom-mw`, `--upgrade-cost-musd`, `--loads <json>`, and `--out <path>`; run with no flags to restore the default scenario.

### Running Tests
```bash
# Run grid tests
python -m pytest tests/test_grid_same_year_flows.py tests/test_grid_solution_cards.py -q
```

## Code Guidelines & Constraints

*   **Matplotlib Dependency Constraint:** Do not use `matplotlib` or `pandas.style.background_gradient()` (which imports matplotlib) in files destined for Streamlit Cloud (such as `streamlit_app.py` or `grid_app.py`). It will throw an `ImportError` on Streamlit Cloud. Use standard `.style.format()` instead.
*   **Global Imports:** Ensure core modules (like `json` and `pandas`) are imported globally at the top of the file rather than locally within pages to avoid page-navigation `NameError` exceptions.
*   **Directory Structure:**
    *   `domains/grid/`: Main power grid analysis code.
    *   `domains/grid/experiments/`: Side experiments (e.g. large load queue coordination).
    *   `docs/`: Core documentation and playbooks.
    *   `reports/`: Consolidated output JSONs and markdown briefs.
    *   `tests/`: Unit tests.
