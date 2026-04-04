# SPDX-License-Identifier: LicenseRef-Proprietary-Commercial
# SPDX-FileCopyrightText: 2026 James Hawkins <jhawk314@gmail.com>

"""KOMPOSOS-IV Core: The Fused Categorical Runtime."""

from .types import Object, Morphism, Path, HigherMorphism, EquivalenceClass, Cone, Cocone
from .enrichment import (
    MonoidalStructure,
    MULTIPLICATIVE_QUANTALE,
    ADDITIVE_QUANTALE,
    PROBABILISTIC_QUANTALE,
    MAX_QUANTALE,
    MIN_QUANTALE,
    get_quantale,
)
from .category import Category
from .bridge import Bridge
from .hooks import HookRegistry
from .functor import Functor, NaturalTransformation
from .adjunction import Adjunction, adjunction_from_hom_iso, free_forgetful
from .limits import (
    product,
    coproduct,
    equalizer,
    pullback,
    pushout,
    terminal,
    initial,
)

__all__ = [
    "Object",
    "Morphism",
    "Path",
    "HigherMorphism",
    "EquivalenceClass",
    "Cone",
    "Cocone",
    "MonoidalStructure",
    "MULTIPLICATIVE_QUANTALE",
    "ADDITIVE_QUANTALE",
    "PROBABILISTIC_QUANTALE",
    "MAX_QUANTALE",
    "MIN_QUANTALE",
    "get_quantale",
    "Category",
    "Bridge",
    "HookRegistry",
    "Functor",
    "NaturalTransformation",
    "Adjunction",
    "adjunction_from_hom_iso",
    "free_forgetful",
    "product",
    "coproduct",
    "equalizer",
    "pullback",
    "pushout",
    "terminal",
    "initial",
]
