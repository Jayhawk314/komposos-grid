# Feasibility Study: Integrating Sub-Data Granularity into the Komposos Grid System
## Analysis of Value, Feasibility, Computational Limits, and Operational Risk

---

## Executive Summary

Grid analysts and investors frequently ask if we can drill down from macroscopic regional figures (like state-level outages or RTO-level queues) to "sub-data" (county-level outages, technology-specific queue cohorts, or nodal curtailments).

This study investigates:
1. **Where sub-data is technically feasible** (where raw data already exists in the workspace).
2. **Where sub-data is computationally impossible or dangerous** (due to memory, performance, or statistical sparsity).
3. **The potential negative effects** of over-slicing.
4. **A safe, high-value implementation strategy** to surface sub-data without breaking the system.

---

## 1. Sub-Data Feasibility & Impact Matrix

The table below outlines the primary candidates for sub-data integration, their data availability, value, and technical risk.

| Data Dimension | Sub-Data Target | Raw Data Availability | Value Proposition | Technical Risk / Negative Effects |
| :--- | :--- | :--- | :--- | :--- |
| **Interconnection Queue** | Fuel/Technology (Solar, Wind, Battery, Gas) | **Available** (in `LBNL_Ix_Queue_Data_File_thru2026.xlsx`) | High. Reveals which clean energy technologies are getting through and which are stalled. | **Low**. Slicing by fuel is lightweight and mathematically clean. |
| **Interconnection Queue** | Size Classes (<50 MW vs >500 MW) | **Available** (in `LBNL_Ix_Queue_Data_File_thru2026.xlsx`) | Medium. Shows if larger projects suffer worse delays. | **Low**. Easy to compute via size ranges. |
| **Grid Outages** | County-Level or Utility-Level Outages | **Available** (in `eaglei_outages_2023.csv`) | High. Pinpoints localized reliability weak spots and grid vulnerabilities. | **CRITICAL**. The raw file is **1.2 GB**. Loading or processing county-level rows directly in the Streamlit app will **exhaust RAM and crash the server** (Streamlit Cloud has a 1GB limit). |
| **Grid Outages** | Temporal Outage Profiles (Hourly/Seasonal) | **Available** (in `eaglei_outages_2023.csv`) | Medium. Shows if winter storms or summer peaks dominate. | **High**. Increases memory footprint and processing times significantly. |
| **Renewable Curtailment** | Fuel-Specific Hourly Profiles | **Partial** (in `caiso_production_curtailments_2023.xlsx`) | High. Visualizes the exact hours when solar clipping or wind dumping happens. | **Medium**. Could clutter the UI if not presented in a clean, tabbed format. |

---

## 2. Detailed Assessment of Sub-Data Dimensions

### 2.1 Queue Slicing by Fuel & Size
* **Feasibility**: Already supported by the raw loader (`QueueProject` class has `fuel` and `mw` fields).
* **The Opportunity**: We currently report overall MISO and ERCOT completion rates. Slicing this by technology reveals that **Battery Storage** in ERCOT has a completion rate of **~47%** and moves from Request to Operation (IR $\to$ COD) in **~35 months**, whereas **Solar** in ERCOT has a completion rate of **~25%** and takes **~45 months**. This shows that queue bottlenecks are highly technology-dependent.
* **Negative Effect (Thin Cohorts)**: If we slice the data too finely (e.g., MISO offshore wind in 2011), the sample size ($n$) drops below a meaningful statistical threshold. This is called the **Sparse Cohort Problem**. 
* **Mitigation**: We must maintain a strict cohort size floor (e.g., `min_cohort = 30` decided projects) and flag any "thin" cohorts on the UI (as the system currently does in the backend).

### 2.2 Outages at County-Level (The 1.2 GB RAM Threat)
* **Feasibility**: The ORNL EAGLE-I county outage dataset is highly detailed, but the file size is **1.2 GB**. 
* **The Negative Effect**: Streamlit servers run on shared cloud containers with limited CPU and RAM (Streamlit Cloud restricts apps to **1.0 GB of RAM**). If the app attempts to load or aggregate county-level CSV rows dynamically:
  1. The app will immediately run out of memory (OOM) and terminate.
  2. The page load time will exceed 30 seconds, driving away users.
* **Mitigation**: **Do not run raw county-level aggregation in the app.** Instead, run the heavy county-level aggregation offline (via a background Python script) and output a tiny pre-aggregated JSON summary (e.g., `reports/outages_top_counties.json`, size: 5 KB). The Streamlit app can then render this pre-computed sub-data instantly.

### 2.3 Sheaf Cohomology at Node-Level
* **Feasibility**: Currently, the Sheaf Coherence Audit (`sheaf_audit.py`) aggregates plant data up to the BA level. We can drill down to the **plant-level sheaf residuals**.
* **The Opportunity**: Instead of just showing that the "West region is uncalibrated," we can list the exact physical power plants (with ORIS IDs) that are causing the data conflicts.
* **Negative Effect**: Cognitive overload. Non-technical users do not care about ORIS plant ID 3082 or 3895.
* **Mitigation**: Present this plant-level sub-data under an "Advanced Data Diagnostics" expander, keeping the main view clean and business-focused.

---

## 3. Recommendations & Implementation Plan

To safely introduce sub-data granularity without performance or usability penalties, we recommend:

1. **Queue Fuel & Size Slicing**:
   - Add a "Technology" and "Capacity Size" filter dropdown to the **📊 MISO vs ERCOT Queue Study** page.
   - Run the calculations dynamically in the app because the pre-filtered pandas arrays are tiny and take less than 10ms to process.
2. **County-Level Outage Summaries (Offline-First)**:
   - Create a background run script (`domains/grid/outages.py` upgrades) to extract the **top-10 worst counties** by SAIDI-like burden.
   - Save this to a small JSON file.
   - Surface this on the **💡 Seam Opportunity Screen** under the "Data Integrity" tab.
3. **Curtailment Reason Slicing**:
   - Split CAISO curtailment into **Local (Transmission-driven)** vs. **System (Oversupply-driven)**. This directly informs whether the solution should be a transmission line or a battery.
