# KOMPOSOS Portfolio Outreach Map

## Purpose

This document gives KOMPOSOS a practical outreach path across the math,
chemistry/materials, biomedical, energy, and public-infrastructure sides of the
work.

The point is not to ask one famous person to bless the whole ecosystem. The
point is to find the right first readers for different parts of the work, ask
them for the right kind of critique, and convert that critique into stronger
math, stronger evidence, and stronger public value.

## Core Position

KOMPOSOS should be presented as an independent compositional reasoning
portfolio: a family of repos trying to use category-theoretic and related
structures to reason across domains where disconnected evidence creates hidden
loss.

The strongest phrasing is:

> KOMPOSOS is trying to turn composition into an audit method. It asks whether
> disconnected scientific, technical, economic, or infrastructure facts can be
> organized so that contradictions, missing links, and useful repair paths
> become visible.

For WESyS, the repair path is energy alignment: show where energy, incentives,
contracts, and measurement fail to compose.

For cancer and drug repurposing, the repair path is research-time-saving
triage: organize already-known drugs, mechanisms, and evidence so a researcher
can see the most plausible next hypotheses faster, without pretending that a
computational result is a treatment recommendation.

For chemistry and materials, the repair path is method and search triage:
organize molecules, catalysts, materials, mechanisms, computational methods, and
evidence so a researcher can choose what to calculate, trust, or inspect next.

## The Critical Rule

Do not send people "all the repos" first.

Send a small packet that proves there is a coherent idea and gives the reader a
clear job:

1. A one-page thesis.
2. One math or architecture note.
3. One working domain example.
4. One concrete question.
5. Links to the larger repo ecosystem only after the first ask is clear.

The math will not speak for itself at first. Serious readers need a clean
bridge from the vision to the artifact in front of them.

## Current Portfolio Anchors

Use these as the first visible anchors:

- One-page KOMPOSOS thesis:
  [KOMPOSOS_ONE_PAGE_THESIS.md](KOMPOSOS_ONE_PAGE_THESIS.md)
- KOMPOSOS math notes:
  [KOMPOSOS_MATH_NOTES.md](KOMPOSOS_MATH_NOTES.md)
- Category-theory ecosystem report:
  `C:\Users\JAMES\github\KOMPOSOS-III-LAMBDA-max-3D-chem\docs\KOMPOSOS_COMPLETE_ECOSYSTEM_REPORT.md`
- Chemistry/materials repo:
  `C:\Users\JAMES\github\KOMPOSOS-IV-CHEM`
- Cancer/drug-repurposing public demo:
  <https://komposos-iv-pharm.streamlit.app/>
- WESyS energy alignment note:
  [ENERGY_ALIGNMENT_ENGINE.md](ENERGY_ALIGNMENT_ENGINE.md)
- WESyS California prototype audit:
  [california_energy_vision_audit.md](../reports/california_energy_vision_audit.md)

These are enough for a first conversation. The rest of the repos can be opened
only when the reader asks where the engine, proof layer, or domain evidence
lives.

## Math Lineage and Yoneda Language

KOMPOSOS can say that its mathematical direction is influenced by public work
around category theory, higher category theory, homotopy type theory, simplicial
type theory, and computer formalization.

Emily Riehl is an appropriate influence to name carefully because her public
profile describes work in higher category theory, homotopy type theory, and
computer formalization. The clean wording is influence and study lineage, not
endorsement:

> The mathematical direction is influenced by ideas I learned from Emily Riehl's
> public writing and lectures around category theory, higher category theory,
> homotopy type theory, and simplicial type theory.

Use "Yoneda-profile distance" rather than bare "Yoneda distance" until the
construction is formalized. The working meaning is:

> Two things are close when they behave similarly under a chosen family of
> probes, contexts, maps, reactions, observations, or tests.

That language is strong enough to be useful and cautious enough for serious
mathematical review.

## Outreach Ring 1: Applied Category Theory and Topos-Like People

This is the best first ring if the main question is:

> Is the mathematical framing coherent enough to formalize, or is it confused?

David Spivak is a reasonable first-resource candidate because his public Topos
profile describes work on category-theoretic ideas in science, technology, and
society, including collaboration across materials science, chemistry, robotics,
aeronautics, and computer science. Topos is also explicitly connected to
applied category theory and interdisciplinary systems modeling.

The ask should be humble and technical:

> I built an independent ecosystem around compositional reasoning, category
> theory, drug repurposing, and energy-system alignment. I am not asking you to
> validate the whole thing. I am asking whether the core mathematical analogy is
> worth formalizing, and where it is wrong.

Good targets in this ring:

- Topos Institute people working on applied category theory, systems,
  polynomial functors, lenses, wiring diagrams, categorical databases, or
  collective intelligence.
- Applied Category Theory conference and Adjoint School communities.
- Researchers around compositional decision making, open games, categorical
  cybernetics, and categorical systems modeling.

Best artifact to send:

- One-page thesis.
- Ecosystem report.
- WESyS energy alignment note.
- One small code or diagram example showing a composition failure turning into a
  domain finding.

Best question:

> What is the smallest mathematically serious version of this idea?

## Outreach Ring 2: Network, Stock-Flow, and Systems Modelers

This ring is strong for WESyS and the energy side.

The target reader may care less about the word "category" and more about
whether the model can represent flows, interfaces, process boundaries, and
feedback loops without losing meaning.

Good targets:

- Network theory researchers.
- Stock-flow and open-system modelers.
- Algebraic or compositional modeling tool communities.
- Infrastructure modelers who already think in diagrams, flows, and constraints.

Best artifact to send:

- WESyS California prototype audit.
- Energy Alignment Engine note.
- A short explanation that the current dollar values are screening estimates,
  not validated savings.

Best question:

> Does this representation expose a real repairable interface, or is it only
> renaming ordinary graph analysis?

## Outreach Ring 3: Formal Methods, Type Theory, and Proof People

This ring is useful if KOMPOSOS wants stronger claims around proof,
consistency, derivation, or machine-checkable structure.

The target reader will be sensitive to overclaiming. They will want definitions,
types, invariants, tests, and examples where the engine rejects a bad
composition.

Good targets:

- Formal-methods researchers.
- Type-theory and HoTT communities.
- Lean, Coq, Agda, and proof-engineering people.
- Categorical-logic researchers.

Best artifact to send:

- A small formal core, not the whole portfolio.
- A minimal example where a composition law catches an error.
- Test results and exact claims the code is allowed to make.
- If Lean or proof artifacts are included, label compiled placeholder-backed
  files as formal scaffolds or conjecture encodings, not completed proofs.

Best question:

> Which claims here can be made precise, and which should be downgraded to
> metaphor or heuristic?

## Outreach Ring 4: Chemistry, Materials, and Method-Selection People

This is the right ring for `KOMPOSOS-IV-CHEM`.

Heather Kulik is a strong model for this audience because the MIT profile for
her group describes multi-scale modeling, electronic-structure calculations,
machine learning, discovery of molecules and mechanisms, and materials ranging
from metal-organic frameworks to enzymes and organometallics. That does not
mean the first outreach must be only to Kulik. It means the project should be
packaged in a way that computational chemistry and materials-discovery people
can judge.

The strongest framing is:

> KOMPOSOS-IV-CHEM is a compositional triage layer for chemistry and materials
> search. It asks whether relational profiles can help decide what to calculate,
> what method to trust, what mechanism to inspect, and where uncertainty is
> dangerous.

Good targets:

- Computational chemistry groups.
- Materials-discovery and catalyst-design groups.
- Electronic-structure and DFT-method-selection people.
- MOF, transition-metal, organometallic, enzyme, and biomimetic-catalyst groups.
- Active-learning, Bayesian-optimization, and uncertainty-estimation
  researchers in chemistry.

Best artifact to send:

- One-page KOMPOSOS thesis.
- KOMPOSOS math notes.
- `KOMPOSOS-IV-CHEM` repo link.
- One worked example where the system saves a calculation, flags method
  sensitivity, or ranks candidates by relational behavior.
- For a Kulik-style first contact, prefer zero-friction proof: a CSV, screenshot,
  and live demo before asking anyone to install Docker or clone a repo.

Best question:

> Does the Yoneda-profile distance or compositional structure save chemistry
> research time, or is it just ordinary feature engineering with category
> language?

Hard constraint:

Do not imply that the math replaces DFT, experiment, expert judgment, or
chemical validation. The value claim is search reduction, method triage,
uncertainty surfacing, and better next-step selection.

If the exact-atom-count MOF/linker example is the strongest demo, lead with that
as a concrete time-saver: "here are candidates matching the constraint, here is
their evidence trail, and here is what still needs DFT or lab validation."

## Outreach Ring 5: Biomedical Drug Repurposing and Cancer Hypothesis People

This is the right ring for the cancer app.

The strongest framing is not "this finds cures." The strongest framing is:

> This is a research-time-saving triage interface for already-known drugs,
> mechanisms, and cancer-relevant evidence. It is intended to reduce wasted
> search time, prioritize what deserves review, and preserve uncertainty. It is
> not treatment guidance.

Good targets:

- Drug-repurposing researchers.
- Cancer bioinformatics groups.
- Translational informatics groups.
- Patient-advocacy science advisors.
- People familiar with Broad's Drug Repurposing Hub, NCATS Translator, LINCS,
  CMap, PRISM, DepMap, or related evidence systems.

Best artifact to send:

- Cancer Streamlit app link.
- A one-page explanation of data sources, assumptions, and what the app does not
  claim.
- One worked example where the app ranks or explains a candidate and shows the
  evidence trail.

Best question:

> Does this save expert time without hiding uncertainty, and what evidence would
> make a generated hypothesis worth deeper review?

Hard constraint:

No medical claims, no treatment guidance, and no patient-facing promises. The
value is in organizing evidence, narrowing search, and finding overlooked
hypotheses for expert review.

## Outreach Ring 6: Energy, Climate, and Public Infrastructure People

This ring is for doing good with WESyS, but it should probably come after at
least one math or systems reviewer has helped sharpen the model.

State agencies, city energy offices, public utilities, landfill operators,
wastewater districts, climate offices, and green banks may care about the
results. They will not care about category theory first. They will care about
whether the report identifies a measurable repair, a responsible actor, and a
safe funding path.

Best artifact to send:

- WESyS California prototype audit.
- A one-page "what this could measure next" note.
- A clear caveat that the current savings values are prototype planning
  estimates.

Best question:

> If this model identifies an energy-waste hotspot, who would need to verify it,
> who would pay to fix it, and who would receive the benefit?

## Outreach Ring 7: Mechanism, Contract, and Constraint Design People

This ring connects directly to the newer WESyS idea: the inverse of game theory
as constraint design.

Game theory asks how actors behave under rules. Constraint design asks what
rules would make the desired behavior rational, measurable, and fair.

Good targets:

- Mechanism-design researchers.
- Contract-theory researchers.
- Public-finance and infrastructure-policy people.
- Energy-market design people.
- People who study procurement, shared savings, tariffs, and verification.

Best artifact to send:

- Energy Alignment Engine note.
- One hotspot from the California report.
- A proposed contract path, such as shared savings, performance-based
  maintenance, or pay-for-measured-efficiency.

Best question:

> What agreement would make this repair rational for every actor without hiding
> cost or shifting risk onto the weakest party?

## Recommended Sequence

Start with the math and systems reviewers, not the environmental agencies.

That does not mean the environmental purpose is secondary. It means the public
impact is stronger if the model has survived technical critique before a state
or agency sees it.

Practical sequence:

1. Use or refine the one-page KOMPOSOS thesis.
2. Send the thesis plus ecosystem report to 3 to 5 applied-category or systems
   people.
3. Ask for triage, not endorsement.
4. Send `KOMPOSOS-IV-CHEM` to 2 to 3 chemistry/materials people as a
   method-selection and search-triage tool.
5. In parallel, send the cancer app to 2 to 3 biomedical hypothesis-generation
   people as a research-time-saving triage tool with strict medical-claim
   caveats.
6. Use feedback to make a cleaner "math core" and three domain briefs:
   chemistry/materials, cancer, and WESyS.
7. Only then approach public-infrastructure or California energy people with a
   narrow WESyS validation ask.

## First Email Draft: Math Triage

Subject: Independent KOMPOSOS portfolio: request for mathematical triage

Hello [Name],

I am building an independent project called KOMPOSOS. It tries to use
compositional reasoning and category-theoretic structure as an audit method
across domains where disconnected evidence creates hidden loss.

The three concrete domains I can show are chemistry/materials search triage,
drug-repurposing research triage, and energy-system alignment. The chemistry
side asks whether relational profiles can save calculation and review time. The
cancer side organizes already-known drug and mechanism evidence so researchers
can narrow the search space faster, not as clinical advice. The energy side,
WESyS, looks for places where physical flows, human incentives, and contract
constraints fail to compose.

I am not asking for endorsement. I am asking for mathematical triage. Is there a
small, serious version of this idea worth formalizing? If so, what should I
strip down and define first? If not, where is the conceptual failure?

Links:

- Ecosystem report: [link]
- Math notes: [link]
- KOMPOSOS-IV-CHEM: [link]
- Cancer demo: https://komposos-iv-pharm.streamlit.app/
- WESyS energy note: [link]
- WESyS prototype audit: [link]

Thank you for any critique or referral you are willing to offer.

[Name]

## First Email Draft: Chemistry and Materials Review

Subject: KOMPOSOS-IV-CHEM: chemistry search-triage critique

Hello [Name],

I built an independent chemistry/materials repo called KOMPOSOS-IV-CHEM. The
goal is not to replace electronic-structure theory, DFT, machine learning,
expert judgment, or experiment. The goal is research-time savings: organize
molecules, catalysts, mechanisms, methods, and evidence so that a researcher can
choose what to calculate, what method to trust, or what candidate to inspect
next.

One working idea is a Yoneda-profile distance: compare chemical objects by how
they behave across selected probes or contexts, rather than only by raw
features. I am looking for critique on whether this actually helps chemistry
search, method selection, or uncertainty surfacing, or whether it is just
ordinary feature engineering with category-theory language.

Links:

- One-page thesis: [link]
- Math notes: [link]
- KOMPOSOS-IV-CHEM: [link]

The concrete question is: does this save expert or compute time in a way a
computational chemist would recognize?

Thank you for any critique or referral.

[Name]

## First Email Draft: Biomedical Review

Subject: Drug-repurposing research-triage demo: request for critique

Hello [Name],

I built an independent Streamlit app that explores cancer-related
drug-repurposing hypotheses using already-known drugs, mechanisms, and evidence
links. I am treating it as research-time-saving triage: a way to reduce wasted
search, expose evidence paths, and prioritize hypotheses for expert review. It
is not treatment advice or a clinical recommendation.

I would value critique on whether it saves expert time without hiding
uncertainty. What would make a generated hypothesis useful enough for a
translational researcher to inspect? What evidence sources or validation steps
are missing? What claims should be removed or weakened?

Demo: https://komposos-iv-pharm.streamlit.app/

Thank you for any guidance or referral.

[Name]

## First Email Draft: WESyS Energy Review

Subject: WESyS energy-alignment prototype: validation question

Hello [Name],

I am building a prototype called KOMPOSOS-WESyS that turns waste-to-energy and
resource-flow data into an energy-alignment audit. The model looks for physical
hotspots, but also asks who would have to cooperate, what contract would make a
repair rational, and what measurement would be needed before claiming savings.

The current numbers are planning estimates, not validated savings. I am looking
for critique on whether the hotspot structure and measurement path are useful.

Links:

- Energy Alignment Engine note: [link]
- California prototype audit: [link]

The concrete question is: if a hotspot like this appeared in a real system, who
would verify it, who would pay to fix it, and who would receive the benefit?

Thank you for any critique or referral.

[Name]

## Source Notes

- Topos Institute profile for David Spivak:
  <https://topos.institute/people/david-spivak/>
- Applied Category Theory community and conference information:
  <https://www.appliedcategorytheory.org/>
- Heather J. Kulik profile, MIT Department of Chemistry:
  <https://chemistry.mit.edu/profile/heather-j-kulik/>
- Emily Riehl public profile:
  <https://emilyriehl.github.io/>
- Emily Riehl, "On the infinity-topos semantics of homotopy type theory":
  <https://arxiv.org/abs/2212.06937>
- Broad Institute Drug Repurposing Hub:
  <https://www.broadinstitute.org/developing-diagnostics-and-treatments/drug-repurposing-hub>
- NCATS Biomedical Data Translator:
  <https://ncats.nih.gov/translator>
- FDA drug repurposing overview:
  <https://www.fda.gov/drugs/resources-drugs/drug-repurposing>
