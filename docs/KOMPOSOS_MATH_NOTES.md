# KOMPOSOS Math Notes

## Purpose

This note keeps the mathematical language useful and honest when presenting the
KOMPOSOS repos to mathematicians, computational chemists, biomedical
researchers, or energy-system people.

The point is not to make every domain expert learn category theory. The point
is to define the mathematical terms tightly enough that serious reviewers can
tell which parts are formal, which parts are computational heuristics, and which
parts are still metaphor.

## Intellectual Lineage

KOMPOSOS can honestly say that its mathematical direction is influenced by
category theory, higher category theory, homotopy type theory, simplicial type
theory, and computer formalization.

Emily Riehl is an appropriate influence to name carefully because her public
work is directly in higher category theory, homotopy type theory, and computer
formalization. The wording should be:

> This work is influenced by ideas I learned from Emily Riehl's public writing
> and lectures around category theory, higher category theory, homotopy type
> theory, and simplicial type theory.

The wording should not imply endorsement, supervision, collaboration, or review.

## Simplicial Type Theory

For KOMPOSOS, simplicial type theory should be treated as a north-star language
for directed structure, higher cells, and equivalence-aware reasoning.

Practical translation:

- Objects are not isolated data points.
- Relationships between objects matter.
- Relationships between relationships also matter.
- Some domain errors are failures of coherent higher structure, not just bad
  scalar predictions.

In software terms, this points toward models that can represent pathways,
transformations, rewrites, homotopies, witnesses, and proof obligations.

## Formalization Caveat

Some KOMPOSOS-IV-CHEM STT materials may compile, but compilation alone is not
the same thing as mathematical proof completion. If the files rely on
placeholders, postulated constants, axioms, stub definitions, shallow witnesses,
or proof-shaped scaffolding, they should be described as compiled formal
scaffolds, conjecture encodings, concept-graph formalization attempts, or
proof-roadmap artifacts.

They should not be described as completed Lean proofs unless the theorem
statements are proved from accepted imports and explicitly listed assumptions,
with no hidden placeholders doing the mathematical work.

This caveat is not a weakness. It is the honest boundary that makes a serious
mathematician more likely to engage.

## Yoneda Distance

"Yoneda distance" should be used carefully. By itself, it is not a universally
standard metric name. The safest KOMPOSOS term is:

> Yoneda-profile distance

Meaning:

> Two things are close when they behave similarly under a chosen family of
> probes, contexts, maps, reactions, observations, or tests.

This is inspired by the Yoneda idea that an object is known by how it relates to
all other objects. In a practical system, KOMPOSOS cannot usually compare
against "all" contexts, so it chooses a finite probe family and computes a
profile distance.

Generic shape:

```text
object x -> probe profile Y(x)
object y -> probe profile Y(y)
Yoneda-profile distance dY(x, y) = distance(Y(x), Y(y))
```

The important move is that the distance is relational. It compares how objects
act in context, not only what their raw descriptors say.

## Domain Readings

### Chemistry and Materials

In chemistry, a Yoneda-profile distance can compare molecules, materials,
catalysts, ligands, protein environments, or methods by their behavior under
relevant probes:

- predicted properties,
- reaction roles,
- binding contexts,
- DFT method sensitivity,
- multi-reference warning signals,
- synthetic accessibility,
- literature evidence,
- mechanism compatibility.

This is useful if it saves computation or researcher time by saying:

> These candidates look different by raw descriptor, but they behave similarly
> under the probes that matter.

or:

> These candidates look similar, but their method sensitivity or mechanism
> context is different enough that they should not be grouped.

### Drug Repurposing

In drug repurposing, the profile can compare drugs by mechanism, target,
pathway, perturbation signature, cancer context, safety constraints, and
evidence quality.

The value is research triage: reduce wasted search, expose evidence paths, and
preserve uncertainty.

### WESyS Energy

In WESyS, the profile can compare facilities, pathways, or hotspots by physical
flow, conversion route, actor map, incentive conflict, contract path, and
measurement need.

The value is energy alignment: make physical and institutional failures visible
as one repairable system.

## Review Questions

The right questions for a mathematician are:

- Is "Yoneda-profile distance" a defensible name for this construction?
- Which category, enrichment, probes, and distance function are actually being
  used?
- Is the embedding faithful enough for the domain claim?
- Does the profile distance preserve the distinctions that matter?
- Where does this collapse into ordinary feature engineering?

The right questions for a domain expert are:

- Does this distance save time?
- Does it group things a real expert would group?
- Does it separate things a real expert would separate?
- Does it surface uncertainty instead of hiding it?
- Does it suggest the next useful experiment, calculation, or audit?

## Strongest Honest Claim

The strongest honest claim is:

> KOMPOSOS uses Yoneda-inspired profile distances to compare things by their
> behavior across meaningful contexts. The current implementation should be
> judged by whether the chosen probes save expert time and preserve domain
> distinctions. The longer-term mathematical goal is to formalize when these
> profiles are faithful, stable, or predictive.
