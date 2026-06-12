"""Energy alignment recommendations for WESyS audit hotspots.

This module turns a physical hotspot into an action design sketch: who is
involved, why the repair may not happen by default, what agreement could unlock
it, and what constraints keep the proposal honest.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class ResourceFamily(Enum):
    LANDFILL = "landfill"
    POTW = "potw"
    CAFO = "cafo"
    UNKNOWN = "unknown"


class TechnologyFamily(Enum):
    ELECTRICITY = "electricity"
    CNG = "cng"
    PNG = "png"
    RNG = "rng"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ActorRole:
    name: str
    role: str
    likely_interest: str
    likely_constraint: str


@dataclass(frozen=True)
class AlignmentRecommendation:
    resource_family: ResourceFamily
    technology_family: TechnologyFamily
    actors: tuple[ActorRole, ...]
    activity_diagnosis: str
    game_diagnosis: str
    contract_path: str
    constraints: tuple[str, ...]
    measurement_needs: tuple[str, ...]
    confidence_tier: str

    def constraints_text(self) -> str:
        return "; ".join(self.constraints) + "."

    def measurement_text(self) -> str:
        return "; ".join(self.measurement_needs) + "."


def recommend_alignment(
    resource: str,
    technology: str,
    *,
    conservative_exposure: float,
    prototype_savings: float,
    gap_type: str = "",
) -> AlignmentRecommendation:
    """Create an alignment recommendation for an audit hotspot."""
    resource_family = classify_resource(resource)
    technology_family = classify_technology(technology)
    actors = actor_roles(resource_family, technology_family)
    return AlignmentRecommendation(
        resource_family=resource_family,
        technology_family=technology_family,
        actors=actors,
        activity_diagnosis=activity_diagnosis(resource_family),
        game_diagnosis=game_diagnosis(conservative_exposure, prototype_savings),
        contract_path=contract_path(resource_family, technology_family, prototype_savings),
        constraints=constraints(prototype_savings, gap_type),
        measurement_needs=measurement_needs(resource_family, technology_family),
        confidence_tier=confidence_tier(conservative_exposure, prototype_savings),
    )


def classify_resource(resource: str) -> ResourceFamily:
    text = str(resource).upper()
    if "LF" in text or "LANDFILL" in text:
        return ResourceFamily.LANDFILL
    if "POTW" in text or "WWTP" in text or "WASTEWATER" in text:
        return ResourceFamily.POTW
    if "CAFO" in text or "FARM" in text:
        return ResourceFamily.CAFO
    return ResourceFamily.UNKNOWN


def classify_technology(technology: str) -> TechnologyFamily:
    text = str(technology).upper()
    if "ELEC" in text or "POWER" in text:
        return TechnologyFamily.ELECTRICITY
    if "CNG" in text:
        return TechnologyFamily.CNG
    if "RNG" in text:
        return TechnologyFamily.RNG
    if "PNG" in text:
        return TechnologyFamily.PNG
    return TechnologyFamily.UNKNOWN


def actor_roles(
    resource_family: ResourceFamily,
    technology_family: TechnologyFamily,
) -> tuple[ActorRole, ...]:
    base = [
        ActorRole(
            "facility operator",
            "maintains the asset and executes repairs",
            "uptime, manageable maintenance, lower operating risk",
            "capital budget, staffing, disruption risk",
        ),
        ActorRole(
            "city or public authority",
            "sets public goals and may coordinate funding",
            "emissions reduction, resilience, public value",
            "procurement rules, budget cycles, proof requirements",
        ),
        ActorRole(
            "community",
            "receives local health, cost, and reliability effects",
            "lower pollution, fair rates, visible benefits",
            "limited technical visibility and negotiating power",
        ),
    ]

    if technology_family == TechnologyFamily.ELECTRICITY:
        base.append(
            ActorRole(
                "utility",
                "interconnects and values grid reliability",
                "stable generation, avoided congestion, reliability",
                "tariff rules, interconnection queues, ratepayer protection",
            )
        )
    else:
        base.append(
            ActorRole(
                "fuel offtaker",
                "buys or credits recovered gas/fuel",
                "reliable volume, quality, low-carbon attributes",
                "quality specs, delivery risk, credit verification",
            )
        )

    if resource_family == ResourceFamily.CAFO:
        base.append(
            ActorRole(
                "farm producer",
                "hosts the waste stream and operational process",
                "margin protection, odor control, operational simplicity",
                "thin margins, biological process risk, labor limits",
            )
        )
    elif resource_family == ResourceFamily.POTW:
        base.append(
            ActorRole(
                "water regulator",
                "protects permit compliance",
                "water quality and reliability",
                "strict compliance and safety obligations",
            )
        )

    return tuple(base)


def activity_diagnosis(resource_family: ResourceFamily) -> str:
    diagnoses: Mapping[ResourceFamily, str] = {
        ResourceFamily.LANDFILL: (
            "landfill operators, utilities, city climate staff, and nearby "
            "communities may not share the same object of action. The operator "
            "sees maintenance and uptime; the city sees methane and emissions; "
            "the utility or fuel buyer sees system value."
        ),
        ResourceFamily.POTW: (
            "water operators prioritize permit compliance and uptime, while "
            "energy recovery may sit outside the core operating mandate."
        ),
        ResourceFamily.CAFO: (
            "farm operators may face thin margins and operational risk, while "
            "public value comes from methane reduction and local resilience."
        ),
        ResourceFamily.UNKNOWN: (
            "the actor who can repair the pathway may not be the actor who "
            "captures the full energy, emissions, or reliability benefit."
        ),
    }
    return diagnoses[resource_family]


def game_diagnosis(conservative_exposure: float, prototype_savings: float) -> str:
    if prototype_savings >= 5_000_000 or conservative_exposure >= 100:
        return (
            "high shared value suggests a coordination problem. Multiple actors "
            "can benefit, but no single actor may rationally carry the full cost."
        )
    if prototype_savings >= 1_000_000:
        return (
            "moderate value suggests a bargaining problem. The repair may need "
            "bundling, a low-friction maintenance window, or a cost-share trigger."
        )
    return (
        "localized value suggests a transaction-cost problem. Keep the agreement "
        "simple or bundle the repair with a larger maintenance program."
    )


def contract_path(
    resource_family: ResourceFamily,
    technology_family: TechnologyFamily,
    prototype_savings: float,
) -> str:
    if technology_family == TechnologyFamily.ELECTRICITY:
        return (
            "use a shared-savings or performance-based interconnection agreement "
            "between facility, city, and utility. Pay only against measured "
            "efficiency, reliability, or emissions improvements."
        )
    if technology_family in (TechnologyFamily.CNG, TechnologyFamily.RNG):
        return (
            "use an offtake or fuel-credit sharing contract that splits measured "
            "gas-quality and throughput gains between the facility and buyer."
        )
    if resource_family == ResourceFamily.POTW:
        return (
            "use a performance maintenance agreement that protects permit "
            "compliance first and shares measured energy savings second."
        )
    if prototype_savings >= 5_000_000:
        return (
            "use a staged energy service contract: small measurement phase, "
            "independent verification, then shared verified savings after repair."
        )
    return (
        "use a measured-efficiency service contract with a small discovery phase, "
        "then share verified savings after repair."
    )


def constraints(prototype_savings: float, gap_type: str = "") -> tuple[str, ...]:
    out = [
        "meter before and after repair",
        "protect uptime",
        "cap public exposure",
        "record maintenance cost changes",
    ]
    if prototype_savings >= 5_000_000:
        out.append("require independent measurement and verification")
    if gap_type == "interchange_failure":
        out.append("verify process sequencing before capital spend")
    return tuple(out)


def measurement_needs(
    resource_family: ResourceFamily,
    technology_family: TechnologyFamily,
) -> tuple[str, ...]:
    needs = [
        "baseline throughput",
        "energy input and useful output",
        "downtime and maintenance events",
        "before/after operating cost",
    ]
    if resource_family in (ResourceFamily.LANDFILL, ResourceFamily.CAFO):
        needs.append("methane capture or destruction rate")
    if technology_family == TechnologyFamily.ELECTRICITY:
        needs.extend(["interconnection availability", "exported kWh"])
    elif technology_family in (TechnologyFamily.CNG, TechnologyFamily.RNG, TechnologyFamily.PNG):
        needs.extend(["fuel quality", "delivered fuel volume"])
    return tuple(needs)


def confidence_tier(conservative_exposure: float, prototype_savings: float) -> str:
    if conservative_exposure <= 0:
        return "screening"
    if prototype_savings >= 5_000_000:
        return "high-priority prototype"
    if prototype_savings >= 1_000_000:
        return "medium-priority prototype"
    return "screening prototype"


__all__ = [
    "ActorRole",
    "AlignmentRecommendation",
    "ResourceFamily",
    "TechnologyFamily",
    "actor_roles",
    "classify_resource",
    "classify_technology",
    "recommend_alignment",
]

