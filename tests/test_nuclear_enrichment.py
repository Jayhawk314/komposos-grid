# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

import sys
import os
import pytest

# Add source path for imports
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dirs = [
    os.path.join(repo_root, "src"),
    os.path.join(repo_root, "src", "komposos_core"),
    os.path.join(repo_root, "src", "komposos_wesys"),
]
for d in src_dirs:
    if os.path.exists(d) and d not in sys.path:
        sys.path.insert(0, d)

from core.category import Category
from cog.session import CogSession
from cog.engine import CogEngine
from cog.schema import CogClaim, VerificationStatus
from domains.nuclear.ingest import NuclearCategoryBuilder
from domains.nuclear.flow_geometry import analyze_enrichment_geometry


def test_nuclear_ingest_baseline():
    cat = Category(name="test_nuclear_ingest", db_path=":memory:")
    builder = NuclearCategoryBuilder(cat)
    stats = builder.ingest_synthetic_baseline()

    assert stats["objects"] == 6
    assert stats["morphisms"] == 5

    # Check objects are present
    assert cat.get("mine:mcclean_lake") is not None
    assert cat.get("conversion:metropolis_converdyn") is not None
    assert cat.get("enrichment:urenco_eunice") is not None
    assert cat.get("reactor:smr_pilot") is not None

    # Check morphisms are present
    mors = cat.morphisms()
    assert len(mors) == 5
    feeds = [m for m in mors if m.source == "mine:mcclean_lake" and m.target == "conversion:metropolis_converdyn"]
    assert len(feeds) == 1
    assert feeds[0].confidence == 0.95


def test_nuclear_flow_geometry():
    cat = Category(name="test_nuclear_geometry", db_path=":memory:")
    builder = NuclearCategoryBuilder(cat)
    builder.ingest_synthetic_baseline()

    report = analyze_enrichment_geometry(cat)
    assert report.num_nodes == 6
    assert report.num_edges == 5
    assert len(report.edge_curvatures) > 0

    # Ensure all edge curvatures are computed
    for u, v, kappa in report.edge_curvatures:
        assert isinstance(u, str)
        assert isinstance(v, str)
        assert isinstance(kappa, float)


def test_nuclear_cog_verification():
    cat = Category(name="test_nuclear_cog", db_path=":memory:")
    builder = NuclearCategoryBuilder(cat)
    builder.ingest_synthetic_baseline()

    session = CogSession(category=cat)
    cog = CogEngine(session=session)

    # Claim checking: enrichment -> demand
    claim = CogClaim(
        source="enrichment:urenco_eunice",
        target="demand:hyperscaler_dc",
        relation="powers",
        confidence=0.50
    )

    check_result = cog.check_claim(claim)
    assert check_result.status == VerificationStatus.PARTIAL or check_result.status == VerificationStatus.AGREE
    assert check_result.confidence > 0.0
    assert len(check_result.supporting_paths) > 0


def test_comprehensive_scenarios():
    from domains.nuclear.run_comprehensive_analysis import configure_scenario_category
    
    # 1. Test baseline vs dual intervention properties
    base_cat = configure_scenario_category("baseline")
    dual_cat = configure_scenario_category("dual_intervention")
    
    base_mors = base_cat.morphisms()
    dual_mors = dual_cat.morphisms()
    
    # Verify that the dual intervention successfully altered the target confidence
    c_base = [m for m in base_mors if m.source == "enrichment:urenco_eunice" and m.target == "fabrication:westinghouse_columbia"][0].confidence
    c_dual = [m for m in dual_mors if m.source == "enrichment:urenco_eunice" and m.target == "fabrication:westinghouse_columbia"][0].confidence
    
    assert c_base == 0.55
    assert c_dual == 0.85

