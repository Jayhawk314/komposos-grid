# From Briefing Tool to Community Instrument
## A Critique and Roadmap for Serving the i2X STITCH Webinar Community Across the Full Series

*Prepared July 9, 2026. Covers the June 23, 2026 session ("Regional Study Processes," with Julia Matevosyan of ESIG, Alyssa Hickey of MISO, Vish Sankaran of ENGIE, and Jenifer Fernandes of ERCOT) and — deliberately — every STITCH session still to come.*

---

## 0. The Core Problem This Document Solves

The honest starting point: **most of what the dashboard currently shows, the STITCH audience already knows.**

The people on these webinars are the people who *produce* the numbers we display. Alyssa Hickey does not need a website to tell her MISO's DPP-2022 cycle had 171 GW of requests — she lived it. Julia Matevosyan co-hosts the series with Berkeley Lab, so she has the *Queued Up* data before we do. Vish Sankaran's team at ENGIE runs its own queue analytics desk. Showing them their own figures, however beautifully, earns at most a polite nod: *"correct, and known."*

That is not a failure — reproducing their trusted numbers to the integer is the **admission ticket** (see `docs/webinar_engagement_and_verification_guide.md`, Section 3). But the ticket is not the show. The show is what this repository can compute that **no other tool in the industry computes**, delivered in a form the community can *use between webinars* — for communicating across institutional boundaries and for planning.

This document does four things:

1. **Critiques** the current system and UI, page by page, from the perspective of the webinar stakeholders — including the specific page in question, ⚡ Large Load Siting (ESIG).
2. **Maps the community** — not just the four June 23 presenters, but the full set of personas the STITCH series convenes, and what each one *doesn't already know*.
3. **Centers the demand-side story** — data center consumption as the dominant future demand driver, and how the platform must grow a "load queue" mirror of its generator-queue analytics.
4. **Assigns each advanced backend capability** (Yoneda similarity, right Kan extensions, sheaf cohomology, Dempster–Shafer fusion, fibrations, relief-curve SCMs, OPTIMUS factorization) to a specific stakeholder need, a specific UI surface, and a specific communication or planning act it enables.

Throughout, the design constraint is the user's own instruction: **keep in mind all the other webinars to come.** The platform should be architected as a *series companion*, not a single-session artifact.

---

## 1. Who the STITCH Community Actually Is (and What Each Group Doesn't Know)

The i2X STITCH initiative (Studies, Tools, and Interconnection Consistency and Harmonization) is facilitated by ESIG in collaboration with Berkeley Lab and Elevate Energy Consulting, under DOE's Interconnection Innovation e-Xchange (i2X). Its mandate is to compare interconnection study practices across US regions and find where **harmonization and automation** can speed up reliable interconnection. That mandate defines the audience: it is a *cross-boundary translation community*. Everyone in the room is fluent in their own region's process and semi-literate in everyone else's. The product opportunity lives exactly in that gap.

### 1.1 The persona table

| Persona | Example | What they already know cold | What they typically *don't* know | What the platform can uniquely give them |
|---|---|---|---|---|
| **RTO/ISO queue engineers** | Alyssa Hickey (MISO DPP), Jenifer Fernandes (ERCOT) | Their own tariff, their own cycle stats, their own restudy pain | How their milestones *map onto* other regions' milestones; whether their reforms moved outcome metrics relative to peers; where their published data contradicts neighbors' data | A normalized cross-region funnel with explicit milestone crosswalks; sheaf-audit flags showing where their reported interchange/queue data conflicts with a neighbor's |
| **Developers / IPP analytics teams** | Vish Sankaran (ENGIE) | Their own portfolio's queue positions and study costs | *Conditional* completion probabilities for a hypothetical project (region × fuel × size × era); which stalled third-party projects would relieve congestion that hurts their nodes; lower-bound congestion values on unpriced ties where they're considering projects | The "bring-your-project" screener (OPTIMUS cohort factorization); Stalled Relief Potential scorecard; Kan-extension shadow prices for the non-market Southeast |
| **Facilitators / researchers** | Julia Matevosyan (ESIG), Berkeley Lab, Elevate Energy Consulting | The national aggregate picture, the literature | A *reproducible, neutral* apparatus that both MISO and ERCOT accept as fair; a formal way to say "these two processes are not comparable until you normalize X" | The harmonization matrix backed by coherence checks; the reconciliation walkthrough (numbers tie to LBNL Sheet 25/27 to the integer); structural-equivalence (Yoneda) evidence for which regions are legitimate comparators |
| **Large-load customers** | Hyperscaler energy teams, gigafactory siting teams | Their compute economics, their speed-to-power imperative | What curtailment exposure *actually costs* under flexible service at a specific seam; how cluster-vs-serial load study regimes change their timeline risk; where headroom exists | The NPV siting calculator (once fed real congestion-hour data); coordinated-vs-isolated study simulation; headroom screening against real tie-line data |
| **Utilities / transmission owners** | TO planning departments | Their local system | How load requests landing on *their* system aggregate regionally; which of their data submissions are the source of cross-agency inconsistency | Fibration views (plant/feeder level lifting to BA level); sheaf residual localization ("your node is where the books don't balance") |
| **Regulators & PUC staff** | PUCT, state commissions, FERC staff | The dockets in front of them | Independent, non-party quantification: who pays under different allocation designs, what withdrawal cascades cost, whether a proposed reform's claimed benefits are plausible | The cost-allocation tables; queue mortality benchmarks; before/after reform cohort tracking |
| **Community & ratepayer advocates** | Elevate (see `docs/elevate_energy_playbook.md`) | Community impacts, energy-burden data | The technical vocabulary and defensible numbers to intervene in PUC proceedings; proof that coordinated study designs shield ratepayers | Plain-English mode; the $0-to-ratepayers allocation table; the community-solar-scale NPV walkthrough already in the playbook |
| **DOE / national labs** | i2X program staff | Program goals, national statistics | Whether harmonization is *measurably* progressing session over session | A longitudinal "harmonization index" tracked across the webinar series itself |

### 1.2 The key sociological observation

STITCH webinars are one of the few venues where MISO and ERCOT engineers, developers, and researchers are *in the same room being asked to compare themselves*. Comparison across institutions is politically delicate: every region believes cross-region metrics are unfair to them (and they're often right — MISO's cluster batches and ERCOT's serial process don't share a unit of work). The platform's deepest value proposition is therefore not "analytics" but **neutral arbitration infrastructure**: a third-party apparatus that (a) reproduces each party's own numbers exactly, (b) makes every normalization assumption explicit and adjustable, and (c) locates disagreements *in the data itself* rather than in anyone's judgment. The sheaf-theoretic machinery is, genuinely, the right mathematics for this — its entire purpose is detecting when locally-consistent views fail to glue globally. Section 5 makes this concrete.

---

## 2. Critique of the Current System & UI

### 2.1 Global critiques (apply to every page)

**G1. The differentiator is invisible.** The category-theoretic core — the only thing in this repo no other industry tool has — is entirely backstage. A STITCH attendee browsing the app sees LBNL aggregates, a hand-coded harmonization matrix, meeting notes, and a simulation. The Yoneda similarity engine, Kan-extension shadow pricing, sheaf Laplacian audit, and Dempster–Shafer fusion produce zero pixels. The blueprint (`docs/untapped_grid_analytics_blueprint.md`) already diagnosed this; it remains true. **The app currently leads with its least differentiated content.**

**G2. Simulated and measured data share the same visual authority.** The Large Load page presents a synthetic 5-project cohort with the same metric cards, tables, and confidence as the Regional Queue page presents LBNL-validated integers. To a general audience this is fine; to *this* audience it is a credibility landmine. The moment Jenifer Fernandes asks "where did the 31.2 months come from?" and the answer is "a stylized simulation," the reconciled LBNL numbers on the neighboring page get retroactively discounted too. Trust is portfolio-level. **Every figure needs a provenance badge: `Measured (LBNL Sheet 27)` / `Derived (model, assumptions here)` / `Simulated (illustrative)`.** This is cheap to add and is the single highest-leverage credibility fix.

**G3. The app is architected around one session.** The sidebar's session selector has exactly one entry ("2026-06-23 · Regional Study Processes") and a comment saying `# add future sessions here`. Nothing else in the app reacts to the selection. Given the instruction to serve *all the webinars to come*, this should invert: the session registry should become the app's organizing spine (Section 6).

**G4. The region filter is mostly decorative.** `active_regions` is consumed only by the Harmonization Matrix page (streamlit_app.py:366–417). On the Regional Queue Study page, region choice is a separate selectbox; on other pages it does nothing. A user who sets the sidebar filter to `PJM, CAISO` and then opens the queue study reasonably expects the view to follow. Either wire it through everywhere or scope it visually to the pages it affects.

**G5. No shareable state.** Stakeholders on a webinar want to say "look at *this*" — and paste a link. Streamlit supports query params; encoding page + region + scenario sliders into the URL turns every interesting configuration into a communicable artifact. For a community whose whole purpose is communication, this is a first-class feature, not a nicety.

**G6. No narrative for the newcomer.** Each new webinar brings new attendees. There is no "start here" page that explains, in 60 seconds, what this is, whose numbers it reconciles against, and what to click first. The plain-English guide exists in `docs/` but isn't surfaced in-app.

### 2.2 Page-by-page

**📊 Regional Queue Study** — *Strongest page; the reconciliation engine is the right anchor.*
- ✅ The LBNL-matching completion/post-IA rates are the trust walkthrough made interactive. Good.
- ✗ The four headline metrics (total requests, active stalled, LBNL completion, post-IA rate) are exactly what the audience knows. The page should *lead* with something they don't: e.g., the conditional-probability funnel by DPP phase, or the "an IA means 80% in ERCOT but 35% in MISO" gap framed as a **contract-certainty spread** with a time series showing whether reforms are closing it.
- ✗ No cohort-over-time reform tracking. MISO's live question (per the engagement guide) is whether DPP reforms are filtering speculative projects without killing viable ones. The data to answer it (DPP-2016 → DPP-2025 cohort funnels) exists in `run_stitch_brief.py`. Surface a "reform scoreboard": early-withdrawal share by cycle, restudy-burden proxy, survivor completion rate.
- ✗ No load-side funnel at all (see Section 3).

**🗺️ Harmonization Matrix** — *Right concept, hand-coded substance.*
- ✅ The only page that respects the region filter; the matrix idea is exactly ESIG's mission.
- ✗ It's a static, hand-maintained table. The sheaf machinery could make it *computed*: define each region's process as a small diagram (milestones + data fields + transition rules), and let coherence checking find where a functor between them fails to exist. Then the matrix cells become verdicts ("no consistent mapping exists for ERCOT's 'studied load' concept in MISO's schema") instead of prose. This turns the page from a summary into an instrument (Section 5.3).

**📅 STITCH Session Notes** — *Useful archive, no forward value yet.* Becomes the series spine in Section 6.

**⚡ Grid Network Map / 📈 Seam Congestion Findings / 🎯 Seam Opportunity Screen** — *Real data, real value, but presented as findings rather than tools.* The congestion evidence (ERCOT West–North spread rising $4.94 → $5.78/MWh; MISO–SPP seam at $5.09/MWh) is genuinely useful to developers. Missing: drift/volatility sparklines (are these numbers stale?), Kan-extension estimates for the unpriced Southeast, and the marginal-BCR sizing curves — all specified in the blueprint, all unbuilt.

**📖 Grid Map Manual** — fine as documentation; candidate home for the Grid Data Quality Index status card.

**⚡ Large Load Siting (ESIG)** — *the page in question. Detailed critique:*

1. **Hardcoded synthetic cohort in the view layer.** The 5-project cohort (LD-001…LD-005), the "40%" withdrawal rate, and the "-2 projects (350 MW)" delta are string literals in `streamlit_app.py` (lines 782–801), while other numbers load from `large_load_coordination_experiment.json`. If the experiment is re-run with different parameters, the page silently lies. All scenario facts should come from the JSON.
2. **The MW-per-load inline conditional** (`250 if k=="LD-001" else 200 if ...`, line 814) duplicates data that exists in the experiment file. Fragile and unnecessary.
3. **The CapEx delta hack** (line 886) shows "-$12.27M CapEx Saved" only when the slider sits within $0.1M of its default — a magic-number branch that will confuse anyone who moves the slider slightly.
4. **The NPV model is too coarse for its real audience.** Hyperscaler energy teams model curtailment as a *distribution* over hours and prices, not `flex_share × hours × flat $/MWh`. Minimum upgrades: (a) let curtailment hours come from actual historical congestion-hour counts at a selectable seam (the data exists in the daily spreads pipeline); (b) add a load ramp (data centers phase in over 12–36 months); (c) show NPV sensitivity (tornado chart) rather than a single number, since the sign of the firm-vs-flexible verdict flips inside plausible input ranges — that *flip boundary* is itself the most interesting output. Plot the indifference frontier: curtailment hours vs. months-saved, shaded by which option wins.
5. **No connection to the real large-load pipeline.** ERCOT is now tracking **438 GW of large-load requests, ~90% from data centers**, and the PUCT approved the **Batch Zero** collective-study framework on June 18, 2026 — with batch-inclusion notices due **August 2026** and a final transmission plan expected **fall 2027**. The page simulates a stylized 1,100 MW cohort while the real world offers a 438 GW natural experiment with published milestones. Section 3 proposes the fix.
6. **What the page gets right:** the isolated-vs-coordinated framing is exactly ESIG's June 2026 report recommendation; the proportional cost-allocation table is precisely what advocates (Elevate) and regulators need; the two-tab structure (system view / project view) matches the two personas that visit it. Keep the skeleton; upgrade the substance.

---

## 3. The Demand-Side Pivot: Data Centers as the Future-Demand Engine

The user's instinct is correct and now overwhelmingly supported by the data: **data center consumption is not a side topic; it is becoming the main event**, and STITCH's future sessions will inevitably orbit it.

### 3.1 The numbers to anchor on (mid-2026 vintage)

- US data center grid demand is projected around **75.8 GW in 2026** (up from ~53 GW in 2023), rising to **~108 GW by 2028** and **~134 GW by 2030** — roughly half of all projected US power demand growth through 2030.
- Utility five-year peak-demand growth forecasts jumped from **38 GW (2023) to 128 GW (2024)** — a 3.4× revision in one year, driven by large-load requests.
- **ERCOT alone is tracking 438 GW of large-load requests (~90% data centers)** — more than five times its historical peak load — and responded with the Batch Zero collective study (PUCT-approved June 18, 2026).
- Meanwhile ~**2 TW of generation** sits in interconnection queues nationally — the generator-side crisis STITCH was founded on.

The strategic insight for the platform: **the load queue is recapitulating the generator queue's pathologies, about 15 years behind, at higher speed.** Speculative/duplicate requests (developers shopping the same data center to five utilities), serial studies missing cumulative impacts, restudy cascades, cost-allocation fights. This repo has spent years building the mathematics of the *generator* queue funnel. Nearly all of it transfers.

### 3.2 Concrete features

**F1. The Load Queue Funnel (mirror of the generator funnel).** Apply `queue_analysis.py`'s OPTIMUS factorization to large-load requests: Request → Study → Agreement → Energization, with completion probabilities conditional on region, size class, and customer type. ERCOT publishes large-load interconnection data; Batch Zero will generate a clean cohort with published milestones. **The 438 GW number is famously inflated by duplicate shopping — the platform's "phantom-demand discount" estimate (what fraction is real?) would be a genuinely novel figure** nobody on the webinar can currently cite. Even a bounded estimate (Dempster–Shafer belief interval over "real demand") would headline a session.

**F2. Batch Zero Tracker.** A page with the real milestones: August 2026 batch-inclusion notices, fall 2027 transmission plan; base-load vs. studied-load classification counts; MW by status. This is the *first* collective large-load study in the country — tracking it live makes the app the community's reference for a process everyone will discuss for the next three sessions. It also future-proofs: when MISO/PJM adopt analogous processes (they will), the tracker becomes comparative.

**F3. Generation–Load Collision Analysis.** The unique cross-cut this repo can do that neither LBNL (generator-side) nor ERCOT (load-side) publishes: put the 2 TW generator queue and the multi-hundred-GW load queue *on the same map* and compute, per seam/zone, whether queued generation and queued load are co-located (self-resolving) or opposed (transmission-dependent). The flow-geometry and seam-screening machinery already computes zonal headroom and congestion; adding load-request geography yields a **"collision matrix"** — the planning artifact every persona in Section 1 would use.

**F4. Real-data NPV calculator.** Feed the flexible-service calculator from measured congestion: pick a seam → historical binding hours and spread distribution populate curtailment defaults → NPV bands instead of point estimates. Then the calculator's verdict ("non-firm wins by $X M") becomes defensible in a siting meeting rather than illustrative.

**F5. Flexibility-as-capacity scoreboard.** ESIG's central policy recommendation is flexible interconnection; Batch Zero explicitly creates a curtailable-load path. Compute, per region: how many MW of large load could connect *today* at existing headroom if they accepted N hours/year of curtailment — a supply curve of speed-to-power priced in flexibility. The relief-curve SCM (`relief_curves.py`) is structurally identical to this problem (capacity vs. relief saturation); it just needs to be run in the load direction.

---

## 4. What Each Backend Capability Gives Which Stakeholder

This is the heart of the user's request: use the advanced backend to tell the community things they *don't* know, in forms that help them *communicate and plan together*. For each capability: what it computes → who needs it → why it's novel to them → where it lives in the UI → what conversation it enables.

### 4.1 OPTIMUS factorization → the "Bring Your Project" screener
- **Computes:** conditional completion probabilities along factored paths (proposed → IA → COD), by cohort (region × fuel × MW class × entry era).
- **For:** developers (Vish's persona), large-load customers, investors.
- **Novel because:** everyone knows aggregate completion rates; almost nobody has *conditional* rates for their specific project profile, cross-region, from a neutral source. The 35%-vs-80% post-IA gap generalizes into a full decision surface.
- **UI:** a form — region, fuel/load type, MW, target COD — returning a probability funnel, expected durations with uncertainty bands, and the two or three factored transitions where projects like theirs die.
- **Enables:** capital-allocation conversations ("our MISO solar exposure has a 0.35 post-IA survival; reweight toward ERCOT storage") and, in webinars, gives RTO staff a mirror ("here is what your process looks like as a survival curve to a customer").

### 4.2 Yoneda similarity → "who is a fair comparator?"
- **Computes:** structural similarity of BAs/regions from their full in/out flow relationship profiles ("an object is its relationships").
- **For:** ESIG/facilitators first; RTO staff second.
- **Novel because:** harmonization debates constantly founder on "you can't compare us to them." Yoneda similarity gives a *principled, data-derived* answer to which regions occupy equivalent structural niches — and therefore which cross-region comparisons are legitimate and which are apples-to-oranges. Nobody in this community has a tool that does this.
- **UI:** heatmap on the Harmonization Matrix page ("Structural Twins" tab), with the top-k most similar region pairs called out.
- **Enables:** the single most useful facilitation move in a STITCH session: *"MISO and SPP are structural twins (J = 0.81); MISO and ERCOT are not (J = 0.42). So we benchmark MISO's reform against SPP's, and treat ERCOT as a different species."* It also gates **functorial property transfer**: reforms validated in region A can be projected onto structurally similar region B with a stated confidence — which is literally STITCH's harmonization mission expressed as mathematics.

### 4.3 Right Kan extension → shadow prices for the unpriced Southeast
- **Computes:** rigorous lower-bound congestion values on ties with no LMP markets (SOCO, TVA, DUK…), as the local limit over adjacent priced ties.
- **For:** developers and data-center siting teams evaluating the Southeast (a top relocation destination as PJM prices rise); regulators; researchers.
- **Novel because:** the Southeast's "hidden congestion tax" is invisible by construction — there is no market to publish it. A defensible lower bound is publishable, citable, and unavailable anywhere else. With data centers migrating toward SOCO/TVA territory for cheap power, the question "what congestion cost is hiding there?" is about to become urgent.
- **UI:** "Hidden Congestion" overlay on the Grid Network Map — unpriced ties colored by Ran-extended $/MWh, each with an expandable derivation showing exactly which priced neighbors bound it (the derivation *is* the credibility).
- **Enables:** a new webinar conversation entirely — extending STITCH's harmonization frame from RTO regions into non-market territory, which the series will need as load growth pushes there.

### 4.4 Sheaf Laplacian cohomology (H¹) → the Data Quality Index and inconsistency localization
- **Computes:** whether regional datasets glue into a consistent global picture (λ₂ = 0) or not (λ₂ > 0), and *which nodes/ties carry the obstruction*.
- **For:** RTO data staff, utilities, Berkeley Lab, DOE.
- **Novel because:** everyone suspects inter-agency data is inconsistent (EIA-930 vs eGRID vs ISO reports); nobody can point to *where*. The eigenvector localizes it: "BA X reports exports that BA Y never registers as imports, and this one seam contributes 60% of the national residual."
- **UI:** a single **Grid Data Quality Index** status card (global λ₂, trended over time) + an incoherence hotspot overlay on the map.
- **Enables:** the least confrontational way ever devised to tell two operators their books don't match — the *math* is the accuser, and both parties see the same residual. For a harmonization initiative, "here is a national metric of how un-harmonized the data currently is, and it improved 12% since the last webinar" is a program-level KPI DOE would love.

### 4.5 Dempster–Shafer fusion → honest uncertainty on contested numbers
- **Computes:** belief–plausibility intervals when sources conflict, plus an explicit conflict measure K.
- **For:** everyone, but especially forecasting debates.
- **Novel because:** the data-center demand forecast fight (438 GW requested vs. what's real; 128 GW utility forecasts vs. analyst skepticism) is *exactly* a conflicting-evidence problem. Publishing "real incremental data-center load by 2030: Bel = 62 GW, Pl = 97 GW, conflict K = 0.31" is more honest and more useful than any point forecast — and the community knows it.
- **UI:** interval bars wherever contested aggregates appear; a "Telemetry Conflict" map overlay coloring ties by K (high K = reporting failure, not congestion).
- **Enables:** de-escalating forecast arguments in sessions. Instead of dueling point estimates, panelists argue about *evidence masses*, which is a better argument.

### 4.6 Grothendieck fibrations → the utility↔RTO coordination lens
- **Computes:** formal lifting between plant/feeder-level detail and BA-level flows; how local changes (a plant outage, a 300 MW load) project to boundary constraints.
- **For:** utilities and RTO planners jointly — the *exact* pair whose coordination failure the ESIG large-loads report diagnoses.
- **Novel because:** the isolated-vs-coordinated study problem *is* a fibration problem: the utility sees the fiber, the RTO sees the base, and the restudy cascade is what happens when nobody computes the cartesian lift. The current Large Load page asserts this ("coordinated data sheaf") without showing it.
- **UI:** on the Large Load page, an interactive multi-scale view: drop a load at a node in the fiber, watch the lift propagate to seam-level headroom in the base. Even a simplified version makes the abstract recommendation ("share a data sheaf") *visible*.
- **Enables:** the utility–RTO conversation ESIG is trying to force, with a shared picture both sides can point at.

### 4.7 Relief-curve SCM + marginal BCR → right-sizing the upgrade conversation
- **Computes:** the point where the marginal dollar of transmission/storage/flexibility stops paying for itself (∂BCR/∂MW = 1).
- **For:** planners, regulators, and cost-allocation fights.
- **Novel because:** upgrade debates are conducted in lump sums ("the $45M upgrade"); marginal curves reveal whether the *last* $10M buys anything. Run in the load direction (Section 3, F5), it prices flexibility as an alternative to wires.
- **UI:** interactive curves on Seam Congestion Findings; a "right-size this upgrade" widget on the Large Load page fed by the same seam data.

### 4.8 Stalled Relief Potential + drift detection → the between-webinars pulse
- **SRP** finds stalled queue projects whose completion would relieve the most congestion — the actionable intersection of the queue and seam datasets, and a ready-made "if you fix one thing, fix this" slide for any session.
- **Drift/volatility sparklines** answer the quiet question every returning attendee has: *"is this number still true?"* A corridor whose 30-day mean has drifted >2σ from its annual baseline gets flagged — which is precisely the freshness signal a recurring webinar series needs its reference tool to have.

---

## 5. Serving the Webinar *Series*: the App as a Living Companion

The user's instruction — *keep in mind all the other webinars to come* — should reshape the architecture. STITCH is a multi-year meeting series; ESIG also runs adjacent i2X tracks (e.g., the FIRST forum on IBR reliability standards, with 2026 sessions on grid-forming IBR specifications and an October conformity-assessment workshop). Future STITCH sessions will predictably cover: affected-system studies, study automation and software tools, energy-resource vs. network models, large-load/co-location processes, and cross-seam coordination. The app should be ready for each *before it happens*.

### 5.1 Make the session registry the spine

Replace the decorative selectbox with a real registry (`reports/stitch_sessions/registry.json`):

```json
{
  "sessions": [
    {
      "id": "2026-06-23",
      "title": "Regional Study Processes (MISO vs. ERCOT)",
      "status": "held",
      "presenters": ["Matevosyan/ESIG", "Hickey/MISO", "Sankaran/ENGIE", "Fernandes/ERCOT"],
      "artifacts": ["queue_process_brief.json"],
      "claims": ["miso_post_ia_35pct", "ercot_post_ia_80pct"],
      "relevant_pages": ["Regional Queue Study", "Harmonization Matrix"]
    },
    {
      "id": "next",
      "title": "TBD — likely large loads / affected systems",
      "status": "anticipated",
      "prep_checklist": ["Batch Zero tracker live", "load funnel v1"]
    }
  ]
}
```

Selecting a session then *configures the app*: which pages are highlighted, which claims are pinned, which data vintage is loaded. Past sessions become an archive; the next session becomes a preparation workspace.

### 5.2 The three-phase cadence per webinar

- **Before (T−2 weeks):** auto-generate a *pre-read brief* from live data — "what changed since last session" (drift flags, new cohort data, Batch Zero milestones hit). Share as the static HTML artifact (the `reports/stitch_2026-06-23/queue_process_brief.html` pattern, generalized).
- **During:** a *companion mode* — one page, big numbers, provenance badges, permalink per figure, so anyone can drop a link in the webinar chat that opens the exact chart under discussion.
- **After (T+1 week):** a *claims ledger* — every quantitative claim made by panelists gets an entry: claim → reproducible? → matching artifact → discrepancy notes. Over sessions, this ledger becomes the community's collective memory, and the app becomes the place where webinar assertions go to be verified. **This is the single strongest "communicate better together" feature**: it converts ephemeral webinar talk into durable, checkable shared state.

### 5.3 The computed Harmonization Matrix as the series' long-term deliverable

Session by session, encode each region's process as a formal diagram (milestones, data fields, transition rules — a few dozen lines of structured data per region, entered after each webinar reveals a new region's details). The coherence engine then *computes* the harmonization matrix: which concepts map cleanly, which map partially, which have no counterpart. By the end of the series, the community owns a machine-checked crosswalk of US interconnection processes — arguably the most concrete artifact the STITCH initiative could produce, and this repo is the only participant positioned to build it.

### 5.4 The Harmonization Index (program KPI)

Roll the computed matrix + sheaf λ₂ + milestone-crosswalk coverage into one number tracked across sessions: **how harmonized is US interconnection, and is it improving?** DOE program staff need exactly this; nobody currently produces it.

---

## 6. Communication Features (Cross-Cutting)

1. **Provenance badges everywhere** (G2). Three tiers: Measured / Derived / Simulated, each expandable to source + vintage + method. Non-negotiable for this audience.
2. **Persona lenses.** A sidebar toggle — Operator / Developer / Regulator / Advocate / Researcher — that reorders each page's content and swaps vocabulary (the translation table in `webinar_engagement_and_verification_guide.md` §2, operationalized). The advocate lens reuses the Elevate playbook's plain-English framing; the operator lens leads with process metrics; the developer lens leads with money.
3. **Permalinks for every view** (G5). Query-param state encoding. The webinar-chat use case alone justifies it.
4. **One-click exports.** Every figure downloadable as (a) PNG for slides, (b) CSV for analysts, (c) a self-contained HTML mini-brief for email — extending the existing static-artifact pattern.
5. **Plain-English toggle** integrated from `docs/plain_english_guide.md`, so the same page serves Alyssa Hickey and a community advocate without forking the app.
6. **A "start here" landing page** (G6): 60-second orientation, the trust walkthrough (LBNL reconciliation) as the first stop, then persona-routed suggestions.
7. **Terminology guardrail:** keep category-theory vocabulary out of the default UI (per the engagement guide — it "triggers skepticism"). The math appears as *method notes* behind expanders: lead with "structural twins," footnote "Yoneda profile distance."

---

## 7. The Agent & MCP Layer: Meeting Users Where They Already Work

A growing share of this system's users — starting with its own author — interact with it *through a coding agent* (Claude Code, Gemini CLI, Copilot), not through the browser. Other STITCH participants' analysts increasingly do the same. This changes what "UI" means: for these users, the best interface is not a page but a **tool surface an agent can call**. An MCP (Model Context Protocol) layer is the right move, and it is unusually cheap here because the hard part is already built.

### 7.1 What already exists

`domains/grid/agent_tools.py` is a complete grounded tool surface: `tool_ba`, `tool_tie`, `tool_path`, `tool_similar` (Yoneda structural twins), `tool_bottlenecks`, `tool_seam`, `tool_whatif` (cut simulation), `tool_gaps`, `tool_explain`, and a self-describing `tool_manifest`. `agent_server.py` already routes natural-language questions to these tools over HTTP for the in-app chat. In other words: the deterministic, data-grounded core that MCP servers are hard to build around is **done**. What's missing is only the standard protocol adapter.

### 7.2 Why MCP specifically helps this community

1. **Grounding instead of hallucination.** When an analyst asks their coding agent "what's the congestion spread on the MISO–SPP seam?", today the agent either guesses or greps the repo. With an MCP server, it calls `tool_seam` and gets the same provenance-stamped number the dashboard shows. The agent becomes a *client of the platform's truth* rather than a competing narrator — which is the entire credibility thesis of Section 2 (G2) extended to the agent era.
2. **Every agent, one integration.** MCP is supported by Claude Code, Gemini CLI, and most other agent harnesses. One server serves the user, their "Google friend," and any STITCH participant who clones the repo — no per-agent glue.
3. **The webinar-companion use case.** During a session, an attendee can ask their own agent "verify the 35% post-IA claim" and the agent can call the reconciliation tools live. This is the claims ledger (§5.2) with zero UI work.
4. **Composability.** Agents can chain tools the dashboard never anticipated: `tool_similar(MISO)` → `tool_whatif(cut the twin's binding seam)` → NPV calc. The long tail of stakeholder questions gets served without building a page per question.

### 7.3 Concrete design

- **`domains/grid/mcp_server.py`**: a thin FastMCP (stdio) wrapper — each existing `tool_*` function becomes an `@mcp.tool()` with its docstring as the description. Because the functions already return JSON-safe dicts with a `tool` field, this is largely mechanical (~a day of work including tests).
- **MCP resources** for the canonical report artifacts (`queue_process_brief.json`, `large_load_coordination_experiment.json`, the sessions registry) so agents can read the same data the UI renders — with vintage stamps in the payload.
- **Read-only by design.** No tool mutates state; simulations run on copies. This keeps the server safe to hand to any webinar participant.
- **Provenance in-band:** every tool response should carry `{"provenance": "measured|derived|simulated", "vintage": "...", "source": "..."}` — the badge system (§6.1) applied to the agent surface.
- **New tools to add as the roadmap lands:** `tool_screen_project` (OPTIMUS conditional funnel, §4.1), `tool_npv_flexible` (the calculator as a callable), `tool_batch_zero_status`, `tool_claims_lookup`.

### 7.4 Skills: yes — pair capabilities with procedures

MCP gives agents *capabilities*; **skills** give them *procedures*. The repo's playbooks (`elevate_energy_playbook.md`, the engagement guide's trust walkthrough) are already step-by-step recipes written for humans — converting them to agent skills (e.g., `.claude/skills/` in this repo) means any agent user executes the same verified sequence:

- **`/webinar-prep`** — regenerate the pre-read brief: run the pipelines, diff against last session, flag drifted numbers, emit the static HTML artifact.
- **`/verify-claim <claim>`** — the trust walkthrough as a procedure: locate the claim's cohort, recompute from LBNL definitions, report match/mismatch to the integer.
- **`/screen-project <region> <fuel> <MW>`** — the bring-your-project funnel with the correct caveats attached.
- **`/large-load-scenario`** — re-run the coordination experiment with new parameters and refresh the JSON the UI reads (fixing §2.2's drift risk by making regeneration one command).

The division of labor: **MCP tools guarantee the numbers are grounded; skills guarantee the workflow around the numbers is followed** — including the provenance labeling and neutrality guardrails (§9) that a free-styling agent would otherwise skip. For a community trying to communicate across institutions, this means every participant's agent gives the *same answer with the same caveats* — harmonization applied to the tooling itself.

---

## 8. Prioritized Roadmap

### Near term (before the next STITCH session)
| # | Item | Why first | Effort |
|---|---|---|---|
| 1 | Provenance badges (Measured/Derived/Simulated) | Credibility guardrail; protects everything else | S |
| 2 | Large Load page data-hygiene fixes (§2.2: hardcoded cohort, MW conditional, CapEx delta hack) | The page in question; cheap correctness | S |
| 3 | Batch Zero tracker (Aug 2026 batch notices are imminent) | Time-sensitive; makes the app the series' reference on the hottest topic | M |
| 4 | Session registry v1 + "what changed since last session" | Series-companion foundation | M |
| 5 | NPV calculator fed by real seam congestion hours + indifference frontier | Turns illustration into tool | M |
| 5b | MCP server wrapping `agent_tools.py` + `/verify-claim` and `/large-load-scenario` skills | Serves the agent-using analysts (§7); mostly mechanical | S–M |

### Mid term (next 2–3 sessions)
| # | Item | Effort |
|---|---|---|
| 6 | Load Queue Funnel + phantom-demand belief interval (Dempster–Shafer) | L |
| 7 | Yoneda "Structural Twins" heatmap on Harmonization page | M |
| 8 | Kan-extension Hidden Congestion overlay (Southeast) | M |
| 9 | Bring-Your-Project screener (OPTIMUS conditional funnel) | M |
| 10 | Claims ledger + permalinks | M |
| 11 | Drift sparklines on all congestion figures | S |

### Long term (the series deliverables)
| # | Item | Effort |
|---|---|---|
| 12 | Computed harmonization matrix (coherence-checked process diagrams) | L |
| 13 | Generation–Load collision matrix | L |
| 14 | Grid Data Quality Index (λ₂) trended + hotspot map | L |
| 15 | Fibration-based utility↔RTO coordination view | L |
| 16 | Harmonization Index as program KPI | M (after 12–14) |

### Explicitly deprioritized
- Homotopy path classification: intellectually rich, but no stakeholder in Section 1 has a live decision it changes yet. Revisit if a session covers transmission-corridor planning.
- More static report pages: the marginal static brief is worth less than any interactive item above.

---

## 9. Risks & Guardrails

1. **Overclaiming.** Kan-extension values are *lower bounds*; SRP is a *screening* metric; the simulation is *illustrative*. Say so, in the UI, every time. This community punishes overclaim harshly and permanently.
2. **Math-forward alienation.** The category theory is the engine, not the hood ornament (§6.7).
3. **Stale data as reputation risk.** A reference tool that shows June numbers in November is worse than no tool; drift flags (§4.8) plus visible data-vintage stamps mitigate.
4. **Neutrality.** The moment the app appears to take MISO's or ERCOT's side (or a developer's side against an RTO), it loses the arbitration role that is its deepest value. Symmetric framing, always: every regional comparison shows both regions' *strengths* (MISO: post-IA build speed; ERCOT: contract certainty and study speed — recall end-to-end it's roughly a tie at ~3.5–4 years).
5. **Simulation drift** (technical): any figure duplicated between backend JSON and UI literals will eventually disagree (§2.2 item 1). Single source of truth: the report JSONs.

---

## 10. Sources

- ESIG, [DOE i2X Initiatives](https://www.esig.energy/i2x-initiatives/) — STITCH facilitation by ESIG, Berkeley Lab, and Elevate Energy Consulting; [ESIG events calendar](https://www.esig.energy/events/); [i2X FIRST forum materials](https://www.esig.energy/wp-content/uploads/2026/02/v2-February-i2X-combined-presentations.pdf).
- Utility Dive, [Texas, facing 438 GW queue, approves initial large-load interconnection process](https://www.utilitydive.com/news/texas-facing-438-gw-queue-approves-initial-large-load-interconnection-pro/823367/).
- ERCOT, [PUCT Approves ERCOT's Batch Zero Process](https://www.ercot.com/news/release/06182026-puct-approves-ercots) and [Batch Zero explainer](https://www.ercot.com/files/docs/2026/06/18/ERCOT-Trending-Topic-New-Batch-Connection-Process-for-Large-Electricity-Users.pdf); [Large Load Integration](https://www.ercot.com/services/rq/large-load-integration).
- Willkie, [ERCOT Approves Implementing New "Batch Zero Process"](https://www.willkie.com/publications/2026/06/ercot-approves-implementing-new-batch-zero-process-for-large-load-interconnections); Sheppard Mullin, [PUCT Approves "Batch Zero" Framework](https://www.sheppard.com/insights/blogs/puct-approves-batch-zero-framework-that-will-provide-a-pathway-for-large-load-to-connect-to-the-grid-and-receive-electricity).
- KilowattLogic, [Data Center Grid Demand 75.8 GW Analysis](https://kilowattlogic.com/news/data-center-electricity-demand-reshaping-grid-2026); S&P Global, [Data center grid-power demand to rise 22% in 2025, nearly triple by 2030](https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/101425-data-center-grid-power-demand-to-rise-22-in-2025-nearly-triple-by-2030); WRI, [Powering the US Data Center Boom](https://www.wri.org/insights/us-data-centers-electricity-demand); Belfer Center, [AI, Data Centers, and the U.S. Electric Grid](https://www.belfercenter.org/research-analysis/ai-data-centers-us-electric-grid); EPRI, [Data Center Load Growth in Context](https://powering-intelligence.epri.com/load-growth.html); Deloitte, [2026 Power and Utilities Industry Outlook](https://www.deloitte.com/us/en/insights/industry/power-and-utilities/power-and-utilities-industry-outlook.html).
- Internal: `docs/webinar_research_brief.md`, `docs/webinar_engagement_and_verification_guide.md`, `docs/untapped_grid_analytics_blueprint.md`, `docs/elevate_energy_playbook.md`, `reports/experiments/esig_large_loads_audit.md`, `streamlit_app.py`.
