# KOMPOSOS: Composition as an Audit Method

## One-Page Thesis

KOMPOSOS is an independent research-and-software portfolio exploring a simple
claim:

> When a system is too complex to understand from its parts alone, composition
> can become an audit method.

The project tries to organize facts, mechanisms, models, and constraints so
that broken connections become visible. The goal is not to replace domain
science. The goal is to help experts see where evidence, flows, incentives, or
rules fail to compose, then decide what should be checked next.

## Why Category Theory

Category theory is useful here because it treats relationships, interfaces, and
composition as first-class objects. KOMPOSOS uses that language as a practical
discipline:

- What are the objects?
- What are the transformations?
- What should compose?
- Where does composition fail?
- What does that failure mean in the domain?

The mathematical ambition is to move from metaphor toward small formal cores:
examples where a composition law, constraint, or proof obligation catches a real
modeling error or reveals a repairable gap.

The current mathematical language is influenced by public work around higher
category theory, homotopy type theory, simplicial type theory, and computer
formalization. In outreach, this should be stated as influence and study
lineage, not as endorsement or collaboration.

One key working term is "Yoneda-profile distance": comparing things by how they
behave across chosen contexts, probes, maps, reactions, observations, or tests,
not only by raw features. The term should be formalized carefully before making
strong mathematical claims.

## Three Concrete Domains

### Drug Repurposing and Cancer

The cancer side is a research-time-saving triage effort around already-known
drugs, mechanisms, and evidence. A public demo is available here:

<https://komposos-iv-pharm.streamlit.app/>

The intended claim is narrow but meaningful. It is not clinical advice and it
does not claim to find cures. Its value is that good mathematical organization
can save research time: narrowing the search space, exposing evidence paths,
ranking plausible repurposing hypotheses, and making the next review step
clearer.

The useful critique is:

> Does this save expert time without hiding uncertainty, and what evidence would
> make a generated hypothesis worth deeper review?

### Chemistry and Materials Computation

The chemistry side is anchored by `KOMPOSOS-IV-CHEM`:

`C:\Users\JAMES\github\KOMPOSOS-IV-CHEM`

This should be framed for computational chemistry and materials discovery. The
claim is not that KOMPOSOS replaces electronic-structure theory, machine
learning, expert judgment, or experiment. The claim is that compositional
organization may save research time by comparing molecules, catalysts, methods,
mechanisms, and evidence through their relational behavior.

Current concrete examples include material compatibility, molecular reasoning,
composition prediction, inverse design, MOF/linker constraints, PFAS screening,
and synthesis-route planning.

The useful critique is:

> Does the math help choose what to calculate, what method to trust, or what
> candidate to inspect next?

### WESyS Energy Alignment

The WESyS side applies the same spirit to energy systems. It looks at waste,
water, biogas, fuel, electricity, utilities, operators, communities, incentives,
and contracts as parts of one repairable system.

The current WESyS prototype turns resource-flow data into an energy-alignment
audit. It asks:

> Where is energy being lost, why does that loss persist, and what agreement or
> constraint would make repair rational?

The current dollar values are planning estimates, not validated savings claims.
The value is in the structure: hotspot, actor, incentive failure, contract path,
and measurement need.

## What KOMPOSOS Needs From Reviewers

KOMPOSOS does not need endorsement first. It needs triage.

The key questions are:

- Is there a mathematically serious core here?
- Which concepts should be formalized first?
- Where is the language currently misleading?
- Which claims should be weakened to heuristic or metaphor?
- Which domain examples are strong enough to keep?
- What would make the work legible to researchers instead of only to the
  builder?

## Near-Term Plan

The next stage is to reduce the portfolio to four clean artifacts:

1. A small mathematical core with definitions, tests, and failure examples.
2. A biomedical research-triage brief with strict medical caveats.
3. A chemistry/materials triage brief with method-selection and search-saving
   examples.
4. A WESyS energy-alignment brief with measurable validation steps.

The longer-term goal is public value: use compositional reasoning to help people
see waste, disease evidence, infrastructure, incentives, and constraints as
systems that can be repaired.
