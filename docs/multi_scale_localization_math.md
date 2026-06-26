# Mathematical Foundations of Multi-Scale Grid Localization
## Category-Theoretic and Sheaf-Theoretic Frameworks for Micro-to-Macro Complexity Scaling

---

## 1. Multi-Scale Representation via Grothendieck Fibrations

To model the grid at multiple scales (from regional RTO interfaces down to individual substation pricing nodes) without losing structural context, we define a **Grothendieck Fibration** $p: \mathcal{E} \to \mathcal{B}$.

### 1.1 The Base Category $\mathcal{B}$ (Macro-Scale)
The base category $\mathcal{B}$ represents the macroscopic BA-level interchange grid:
- **Objects ($Ob(\mathcal{B})$)**: Balancing Authorities (BAs), e.g., $\text{MISO}, \text{PJM}, \text{ERCOT}$.
- **Morphisms ($\mathcal{B}(X, Y)$)**: Boundary tie-lines carrying gross/net annual flow volumes.

### 1.2 The Total Category $\mathcal{E}$ (Micro-Scale)
The total category $\mathcal{E}$ represents the localized substation and pricing node (Pnode) network:
- **Objects ($Ob(\mathcal{E})$)**: Individual Pnodes and physical substations, e.g., $\text{sub}_i$.
- **Morphisms ($\mathcal{E}(\text{sub}_i, \text{sub}_j)$)**: Physical transmission lines or local LMP price spreads.

### 1.3 The Fibration Functor $p$
The projection functor $p: \mathcal{E} \to \mathcal{B}$ maps each micro-node $\text{sub}_i$ to the BA $X$ that operates it: $p(\text{sub}_i) = X$.
- For any object $X \in \mathcal{B}$, the **fiber category** $\mathcal{E}_X = p^{-1}(X)$ is the sub-grid consisting of all local nodes and internal lines strictly within the boundary of BA $X$.
- **Cartesian Lifts**: A morphism $f: \text{sub}_i \to \text{sub}_j$ in $\mathcal{E}$ is cartesian if any internal adjustment to local flow lifts uniquely to a boundary interchange flow modification. This defines how local congestion "scales up" to restrict boundary trade.

---

## 2. Localization and Data Consistency via Sheaf Theory

When telemetry data at the micro-scale (plant-level meters) contradicts macro-scale reports (BA boundary flows), we use the **cellular sheaf** to localize and resolve the inconsistency.

### 2.1 The Grid Presheaf
We define a functor $\mathcal{F}: \mathcal{B}^{\text{op}} \to \mathbf{Set}$ that assigns:
- To each BA $X$, the set of telemetry reports for its internal generation: $\mathcal{F}(X)$.
- To each boundary tie $e: X \to Y$, the flow reading: $\mathcal{F}(e)$.

### 2.2 The Cohomological Obstruction
Let $C^0(\mathcal{B}, \mathcal{F})$ be the space of local data sections, and $d: C^0 \to C^1$ be the sheaf coboundary operator. The global data conflict is measured by the **first cohomology group** $H^1(\mathcal{B}, \mathcal{F}) = \ker(d) / \text{im}(d)$.

Using the **Sheaf Laplacian** $L_{\mathcal{F}} = d^* d$:
- The smallest eigenvalue $\lambda_2$ (algebraic connectivity of the sheaf) represents the **global inconsistency metric**.
- **Localization**: If $\lambda_2 > 0$, the corresponding eigenvector $v_2$ acts as a localizer. The magnitude of the entries in $v_2$ maps directly to the specific plants/BAs that are causing the contradiction:

$$\text{Offense}(X) = |v_2(X)|$$

This allows the system to pinpoint exactly *where* the data is broken, without needing ad-hoc tolerances.

---

## 3. Local-to-Global Data Interpolation via Kan Extensions

When pricing data is missing at a local substation node (unpriced Pnode), we interpolate its value by extending the known macro-scale spreads along the grid topology.

```
          F (Known pricing)
   mathcal{B} ───→ V (Prices)
       │         ▲
     K │         │ Ran_K(F) (Interpolated pricing)
       ▼         │
   mathcal{E} ───┘
```

Let $K: \mathcal{B} \to \mathcal{E}$ be the inclusion functor of the macro-grid into the micro-grid. Let $F: \mathcal{B} \to \mathbf{Quantale}$ be the known congestion value mapping on priced seams.
We compute the **Right Kan Extension** $\text{Ran}_K(F): \mathcal{E} \to \mathbf{Quantale}$ to project these values down to the local fiber:

$$\text{Ran}_K(F)(y) = \lim_{y \to K(x)} F(x)$$

For any unpriced node $y \in \mathcal{E}$, this computes the exact localized lower-bound spread by taking the infimum of priced neighbors, preserving topological consistency across scales.
