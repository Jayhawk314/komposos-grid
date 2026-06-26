# Elevate Energy Playbook: Leveraging Large Load Interconnection Math for Energy Equity
## A Step-by-Step Practical Guide to Translating Data-Center Grid Metrics into Community Solar & Ratepayer Advocacy
*Prepared for the Policy, Advocacy, and Community Solar Siting Teams at Elevate.*

---

## Overview

This playbook is designed to help **Elevate** translate the mathematical models of large load interconnection (originally simulated for tech company data centers) into concrete figures and tools for clean energy equity, ratepayer protection, and community solar advocacy. 

By following these four "baby steps," your advocacy team can use the dashboard to defend ratepayers and make the case for flexible community solar tariffs before Public Utility Commissions (PUCs).

---

## Step 1: Ground Yourself in the Queue Backlog (The Baseline You Know)

### 1. The Context
Elevate knows that local clean energy projects in Illinois (ComEd/Ameren) and across PJM/MISO face years of queue delays. 

### 2. Siting Steps
1.  Open the live dashboard at `https://komposos-grid.streamlit.app/`.
2.  Navigate to the **`📊 Regional Queue Study`** tab.
3.  Observe the baseline completion funnel for decided cohorts:
    *   **MISO:** Highlight that out of the historical cohort, only **18.1% of projects actually completed**, while **73% withdrew**.
    *   **PJM / MISO Post-IA Gap:** Point out that even after executing a Generator Interconnection Agreement (GIA), **65% of MISO projects still withdrew** due to late-stage cost creep.
4.  **Why this matters to Elevate:** These numbers provide the baseline "mortality rate" of projects in your territory, showing that the pre-reform queue process was structurally broken.

---

## Step 2: Witness the "Crowding Out" of Community Energy

### 1. The Context
When massive 300 MW data centers connect sequentially, they absorb all available local grid capacity, leaving community-scale projects with massive upgrade bills that kill their feasibility.

### 2. Siting Steps
1.  Navigate to the **`⚡ Large Load Siting (ESIG)`** tab.
2.  Select the **`📊 Coordination Simulation`** sub-tab.
3.  Scroll to **Scenario A: Isolated Utility Studies**.
4.  Observe the queue simulation metrics:
    *   Total Requested Capacity: **1,100 MW** trying to squeeze into a **800 MW** headroom slot.
    *   The sequential delay: Average queue delay inflates to **31.2 months**.
    *   The withdrawal list: **LD-004 (150 MW)** and **LD-005 (200 MW)** are forced to withdraw due to restudy delays.
5.  **Why this matters to Elevate:** In a sequential queue, the largest tech companies gobble up the first 750 MW. The smaller, community-focused projects at the tail-end of the queue (LD-004/005) inherit the cumulative overload and are forced to withdraw. Coordinated cluster studies protect these tail-end community projects by allocating costs fairly.

---

## Step 3: Shield Ratepayers from Transmission Upgrade Costs

### 1. The Context
Utilities often attempt to socialize the cost of grid upgrades triggered by data centers onto residential ratepayers, driving up energy burdens.

### 2. Siting Steps
1.  On the **`⚡ Large Load Siting (ESIG)`** tab, look at **Scenario B: Coordinated Cluster Studies**.
2.  Scroll down to the **Proportional Upgrade Cost Allocation** table.
3.  Observe how the $45M transmission upgrade cost is split:
    *   The large 300 MW hyperscaler data center (`LD-003`) is automatically billed **$12,272,727.27** (its exact 27.2% proportional share).
    *   Ratepayers pay **$0.00** for this load-triggered upgrade.
4.  **Why this matters to Elevate:** This table is your empirical precedent for PUC filings. You can show regulators that a coordinated grid-sheaf model allows utilities to allocate 100% of large-load-triggered transmission costs to the beneficiary tech companies, shielding low-income residential ratepayers from bearing the costs of tech expansion.

---

## Step 4: Scale the NPV Calculator down to Community Solar

### 1. The Context
Community solar projects (typically 1–5 MW) are frequently killed by local utilities who hit them with $1M+ substation upgrade fees and 3-year queue delays. We will use the interactive calculator to prove that **Flexible (Non-Firm) Service** makes community solar viable.

### 2. Siting Steps
1.  Select the **`🧮 Interactive NPV Siting Calculator`** sub-tab.
2.  Slide the inputs to model a typical **Community Solar Project**:
    *   **Project Capacity:** Slide to **5 MW** (standard community solar size).
    *   **Target Capacity Factor:** Slide to **25%** (standard solar capacity factor).
    *   **Compute Revenue:** Enter **$80.00 / MWh** (typical community solar subscription credit rate).
    *   **Discount Rate:** Set to **10%**.
    *   **Firm Upgrade Cost:** Slide to **$1.50 Millions** (the substation upgrade fee the utility is demanding).
    *   **Timeline to Firm Power:** Slide to **36 Months** (the 3-year delay to build the upgrade).
    *   **Timeline to Non-Firm Power:** Slide to **6 Months** (the fast-track connection).
    *   **Flexible Capacity Share:** Slide to **15%** (meaning we agree to clip up to 15% of our capacity—0.75 MW—during peak spring congestion).
    *   **Annual Peak Congestion:** Slide to **80 Hours** (hours of spring peak solar clipping).
3.  **Analyze the Output:**
    *   **Option 1 (Firm):** Siting CapEx is **$1.50M**; project NPV is severely depressed or negative due to the 3-year delay and upgrade cost.
    *   **Option 2 (Non-Firm):** Siting CapEx is **$0.00M**; project NPV is highly positive because operations start **30 months earlier**, easily offsetting the minor **$4,800/year** curtailment loss.
4.  **Observe the Green Success Card:**
    > 💡 **Non-Firm Service is the Optimal Siting Choice!**
    > Bypassing the grid upgrade and connecting 30 months earlier offsets the annual operational curtailment cost of $0.00M, resulting in a Net Present Value gain of **+$X.XXM**.

5.  **Why this matters to Elevate:** This is your primary lobbying tool. You can baby-step a state representative or PUC commissioner through this exact calculation to prove that **utilities must offer non-firm, flexible interconnection options for community solar**. It shows that minor spring clipping is a negligible cost compared to the massive value of connecting 30 months earlier.
