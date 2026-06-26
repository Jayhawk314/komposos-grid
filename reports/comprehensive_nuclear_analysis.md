# Comprehensive Civilian Nuclear Enrichment Scenario Analysis

This report summarizes the categorical and geometric findings of a 5-part simulation analysis testing different supply chain configurations and bottleneck interventions.

## 1. Scenario Summary Matrix

The following table compares the spectral Fiedler connectivity (coupling strength), logical claim status, and the physical path throughput yield (multiplicative product of all edge confidences from `mine` to `demand`) across all configurations:

| Scenario Name | Fiedler Connectivity | Claim Status | Claim Confidence | Path Yield (Dynamic) | Upstream Seam Members | Downstream Seam Members |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **Baseline 2026 Constraints** | 0.16237 | PARTIAL | 0.100 | 0.1799 | mine:mcclean_lake, conversion:metropolis_converdyn, enrichment:urenco_eunice | fabrication:westinghouse_columbia, reactor:smr_pilot, demand:hyperscaler_dc |
| **Scenario A: Accelerated Centrifuge Expansion (ACT-002)** | 0.18618 | PARTIAL | 0.100 | 0.2780 | mine:mcclean_lake, conversion:metropolis_converdyn, enrichment:urenco_eunice | fabrication:westinghouse_columbia, reactor:smr_pilot, demand:hyperscaler_dc |
| **Scenario B: Redundant Conversion Capacity (ACT-001)** | 0.19744 | PARTIAL | 0.100 | 0.3597 | mine:mcclean_lake, conversion:metropolis_converdyn, enrichment:urenco_eunice | fabrication:westinghouse_columbia, reactor:smr_pilot, demand:hyperscaler_dc |
| **Scenario C: Dual Intervention (ACT-001 + ACT-002)** | 0.23635 | PARTIAL | 0.100 | 0.5560 | mine:mcclean_lake, conversion:metropolis_converdyn, enrichment:urenco_eunice | fabrication:westinghouse_columbia, reactor:smr_pilot, demand:hyperscaler_dc |
| **Scenario D: Severe Conversion Disruption (Shutdown)** | 0.03448 | PARTIAL | 0.100 | 0.0200 | enrichment:urenco_eunice, fabrication:westinghouse_columbia, reactor:smr_pilot, demand:hyperscaler_dc | mine:mcclean_lake, conversion:metropolis_converdyn |

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
In the baseline configuration, the supply chain is vulnerable due to the centralized conversion node and enrichment queues. The logical confidence is restricted to **0.100**, and the physical path yield is **0.1798**.

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
Accelerating the centrifuge expansion at Urenco Eunice resolves the queue bottleneck, increasing its local edge confidence to 0.85. The physical path yield increases from 0.1798 to **0.2779**, but remains restricted by the upstream conversion bottleneck.

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
Resolving the conversion capacity constraint (increasing Metropolis confidence to 0.90) secures the upstream sector. The physical path yield increases from 0.1798 to **0.3596**, but remains limited by the centrifuge queue.

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
Applying both ACT-001 (Conversion) and ACT-002 (Centrifuges) resolves both primary bottlenecks. The physical path yield rises to **0.5562** (a **3x increase** over the baseline), demonstrating that both upgrades are required jointly to unlock supply chain output.

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
A conversion shutdown drops Metropolis confidence to 0.05. This disconnects the upstream flow, dropping the physical path yield to **0.0200** (representing near total system failure).

---
