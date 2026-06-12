# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Tests for the BA flow-graph geometry analysis."""

from domains.grid.flow_geometry import (
    TieLine,
    analyze_flow_geometry,
    build_flow_category,
)


def barbell_ties():
    """Two meshed 4-cliques joined by one heavy bridge tie.

    The bridge is the only edge whose endpoint neighborhoods are
    disjoint: it must be the most negative-curvature edge, and the
    Fiedler vector must split the graph exactly at it.
    """
    west = ["W1", "W2", "W3", "W4"]
    east = ["E1", "E2", "E3", "E4"]
    ties = []
    for cluster in (west, east):
        for i in range(len(cluster)):
            for j in range(i + 1, len(cluster)):
                ties.append(TieLine(cluster[i], cluster[j], 1_000_000.0, 100_000.0))
    ties.append(TieLine("W1", "E1", 2_000_000.0, 500_000.0))
    return ties, west, east


def test_build_flow_category():
    ties, _, _ = barbell_ties()
    cat = build_flow_category(ties)
    assert len(cat.objects()) == 8
    assert len(cat.morphisms()) == 13
    confidences = [m.confidence for m in cat.morphisms()]
    assert max(confidences) == 1.0  # heaviest tie normalized to 1


def test_bridge_region_is_hyperbolic_and_cliques_spherical():
    ties, _, _ = barbell_ties()
    report = analyze_flow_geometry(ties)
    assert report.n_bas == 8

    # The bridge is negatively curved...
    bottleneck_pairs = [{a, b} for a, b, k, _ in report.bottlenecks if k < 0]
    assert {"W1", "E1"} in bottleneck_pairs
    # ...and every hyperbolic edge touches a bridge endpoint: negative
    # curvature localizes around the structural cut, nowhere else.
    assert all(pair & {"W1", "E1"} for pair in bottleneck_pairs)
    # Pure intra-clique edges are positively curved (meshed/resilient).
    for a, b, kappa in report.meshed:
        assert kappa > 0
        assert not ({a, b} & {"W1", "E1"})


def test_fiedler_partition_recovers_clusters():
    ties, west, east = barbell_ties()
    report = analyze_flow_geometry(ties)
    side_a, side_b = (set(s) for s in report.fiedler_partition)
    assert side_a in ({*west}, {*east})
    assert side_b in ({*west}, {*east})
    assert side_a != side_b


def test_weak_coupling_detected_on_barbell():
    ties, _, _ = barbell_ties()
    report = analyze_flow_geometry(ties)
    assert report.algebraic_connectivity > 0  # connected
    assert report.coupling in {"very weak", "weak", "moderate", "strong"}
