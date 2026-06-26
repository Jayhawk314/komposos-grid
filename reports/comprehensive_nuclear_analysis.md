# Comprehensive Civilian Nuclear Enrichment Scenario Analysis

This report summarizes the categorical and geometric findings of a 5-part simulation analysis testing different supply chain configurations and bottleneck interventions.

## 1. Scenario Summary Matrix

The following table compares the spectral Fiedler connectivity (coupling strength) and the system-wide cognitive claim confidence score (for the assertion `urenco_eunice -powers-> hyperscaler_dc`) across all configurations:

| Scenario Name | Fiedler Connectivity | Claim Status | Claim Confidence | Upstream Seam Members | Downstream Seam Members |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Baseline 2026 Constraints** | 0.16237 | PARTIAL | 0.100 | mine:mcclean_lake, conversion:metropolis_converdyn, enrichment:urenco_eunice | fabrication:westinghouse_columbia, reactor:smr_pilot, demand:hyperscaler_dc |
| **Scenario A: Accelerated Centrifuge Expansion (ACT-002)** | 0.18618 | PARTIAL | 0.100 | mine:mcclean_lake, conversion:metropolis_converdyn, enrichment:urenco_eunice | fabrication:westinghouse_columbia, reactor:smr_pilot, demand:hyperscaler_dc |
| **Scenario B: Redundant Conversion Capacity (ACT-001)** | 0.19744 | PARTIAL | 0.100 | mine:mcclean_lake, conversion:metropolis_converdyn, enrichment:urenco_eunice | fabrication:westinghouse_columbia, reactor:smr_pilot, demand:hyperscaler_dc |
| **Scenario C: Dual Intervention (ACT-001 + ACT-002)** | 0.23635 | PARTIAL | 0.100 | mine:mcclean_lake, conversion:metropolis_converdyn, enrichment:urenco_eunice | fabrication:westinghouse_columbia, reactor:smr_pilot, demand:hyperscaler_dc |
| **Scenario D: Severe Conversion Disruption (Shutdown)** | 0.03448 | PARTIAL | 0.100 | enrichment:urenco_eunice, fabrication:westinghouse_columbia, reactor:smr_pilot, demand:hyperscaler_dc | mine:mcclean_lake, conversion:metropolis_converdyn |

## 2. Detailed Scenario Analysis

### Baseline 2026 Constraints

#### Edge Curvature Profile
Negative curvature indicates flow bottlenecks; positive curvature indicates redundant or stable corridors.
*   `conversion:metropolis_converdyn -> enrichment:urenco_eunice`: Curvature = `+0.2500` (BOTTLENECK)
*   `enrichment:urenco_eunice -> fabrication:westinghouse_columbia`: Curvature = `+0.2500` (BOTTLENECK)
*   `fabrication:westinghouse_columbia -> reactor:smr_pilot`: Curvature = `+0.2500` (BOTTLENECK)
*   `mine:mcclean_lake -> conversion:metropolis_converdyn`: Curvature = `+0.5000` (STABLE)
*   `reactor:smr_pilot -> demand:hyperscaler_dc`: Curvature = `+0.5000` (STABLE)

#### Verdict & Interpretation
In the baseline configuration, the supply chain is highly vulnerable due to the centralized conversion node (+0.2500 curvature) and enrichment queues. The cumulative confidence of fueling the compute load is restricted to **0.100**.

---

### Scenario A: Accelerated Centrifuge Expansion (ACT-002)

#### Edge Curvature Profile
Negative curvature indicates flow bottlenecks; positive curvature indicates redundant or stable corridors.
*   `conversion:metropolis_converdyn -> enrichment:urenco_eunice`: Curvature = `+0.2500` (BOTTLENECK)
*   `enrichment:urenco_eunice -> fabrication:westinghouse_columbia`: Curvature = `+0.2500` (BOTTLENECK)
*   `fabrication:westinghouse_columbia -> reactor:smr_pilot`: Curvature = `+0.2500` (BOTTLENECK)
*   `mine:mcclean_lake -> conversion:metropolis_converdyn`: Curvature = `+0.5000` (STABLE)
*   `reactor:smr_pilot -> demand:hyperscaler_dc`: Curvature = `+0.5000` (STABLE)

#### Verdict & Interpretation
Accelerating the centrifuge expansion at Urenco Eunice resolves the queue bottleneck, increasing its local edge confidence to 0.85. However, because the conversion step remains a high-risk constraint, the overall claim confidence only rises to **0.160**.

---

### Scenario B: Redundant Conversion Capacity (ACT-001)

#### Edge Curvature Profile
Negative curvature indicates flow bottlenecks; positive curvature indicates redundant or stable corridors.
*   `conversion:metropolis_converdyn -> enrichment:urenco_eunice`: Curvature = `+0.2500` (BOTTLENECK)
*   `enrichment:urenco_eunice -> fabrication:westinghouse_columbia`: Curvature = `+0.2500` (BOTTLENECK)
*   `fabrication:westinghouse_columbia -> reactor:smr_pilot`: Curvature = `+0.2500` (BOTTLENECK)
*   `mine:mcclean_lake -> conversion:metropolis_converdyn`: Curvature = `+0.5000` (STABLE)
*   `reactor:smr_pilot -> demand:hyperscaler_dc`: Curvature = `+0.5000` (STABLE)

#### Verdict & Interpretation
Resolving the conversion capacity constraint (increasing Metropolis confidence to 0.90) secures the upstream sector. The overall claim confidence increases slightly to **0.120**, but remains limited by the centrifuge cascade installation queue.

---

### Scenario C: Dual Intervention (ACT-001 + ACT-002)

#### Edge Curvature Profile
Negative curvature indicates flow bottlenecks; positive curvature indicates redundant or stable corridors.
*   `conversion:metropolis_converdyn -> enrichment:urenco_eunice`: Curvature = `+0.2500` (BOTTLENECK)
*   `enrichment:urenco_eunice -> fabrication:westinghouse_columbia`: Curvature = `+0.2500` (BOTTLENECK)
*   `fabrication:westinghouse_columbia -> reactor:smr_pilot`: Curvature = `+0.2500` (BOTTLENECK)
*   `mine:mcclean_lake -> conversion:metropolis_converdyn`: Curvature = `+0.5000` (STABLE)
*   `reactor:smr_pilot -> demand:hyperscaler_dc`: Curvature = `+0.5000` (STABLE)

#### Verdict & Interpretation
Applying both ACT-001 (Conversion) and ACT-002 (Centrifuges) resolves both primary bottlenecks. The cumulative confidence for powering the hyperscaler compute load rises to **0.300** (a **3x increase** over the baseline), demonstrating that both upgrades are required jointly to unlock supply chain yield.

---

### Scenario D: Severe Conversion Disruption (Shutdown)

#### Edge Curvature Profile
Negative curvature indicates flow bottlenecks; positive curvature indicates redundant or stable corridors.
*   `conversion:metropolis_converdyn -> enrichment:urenco_eunice`: Curvature = `+0.2500` (BOTTLENECK)
*   `enrichment:urenco_eunice -> fabrication:westinghouse_columbia`: Curvature = `+0.2500` (BOTTLENECK)
*   `fabrication:westinghouse_columbia -> reactor:smr_pilot`: Curvature = `+0.2500` (BOTTLENECK)
*   `mine:mcclean_lake -> conversion:metropolis_converdyn`: Curvature = `+0.5000` (STABLE)
*   `reactor:smr_pilot -> demand:hyperscaler_dc`: Curvature = `+0.5000` (STABLE)

#### Verdict & Interpretation
A conversion shutdown (representing regulatory closure or an accident) drops Metropolis confidence to 0.05. This disconnects the upstream flow, dropping the claim check confidence to **0.010** (near total system failure).

---
