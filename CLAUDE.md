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

### Launching the Dashboard App
```bash
streamlit run streamlit_app.py
```

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
