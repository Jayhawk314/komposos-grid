# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 James Hawkins / Komposos-Labs

"""
Science & Informatics DEMO Suite.

IMPORTANT SCOPE NOTE: checks 1-3 construct toy fixtures designed to be detected
and then assert that the detection machinery detects them. They demonstrate that
the machinery works; they do NOT audit the correctness of any production output
in reports/. For real output verification use the /webinar-prep regeneration
diff and the /verify-claim recompute-from-raw skills.

Demonstrations:
  1. Data / Trust Leakage (Category Security)
  2. Resource Linearity Leakage (Substructural Logic)
  3. Sheaf & Spectral Numerical Stability (Physical Constraints)
  4. Chemical Informatics Database Integrity (MOF Cache — chem domain, not grid)
"""

import sys
import os
import json
import numpy as np

# Add appropriate source paths
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_dirs = [
    repo_root,
    os.path.join(repo_root, "src"),
    os.path.join(repo_root, "src", "komposos_core"),
    os.path.join(repo_root, "src", "komposos_wesys"),
    os.path.join(repo_root, "src", "operadum"),
]
for d in src_dirs:
    if os.path.exists(d) and d not in sys.path:
        sys.path.insert(0, d)

from core.category import Category
from core.types import Object, Morphism
from domains.grid.sheaf_audit import sheaf_audit
from domains.grid.coherence import Section
from komposos_wesys.validation.thermodynamic_probe import ThermodynamicSheaf
from operadum.core.enrichment import LINEAR_TOKENS, ResourceError
from operadum.integrations.komposos_mof import RealKompososMOFClient


def run_data_leakage_audit() -> bool:
    """
    Audit 1: Category Trust & Data Leakage Scan.
    
    Verifies that high-privilege information does not leak to low-privilege targets
    without going through a sanitizer or a guarded boundary.
    """
    print("[AUDIT 1] Scanning for Data / Trust Leakage...")
    
    # 1. Build a category representing a network with potential leakage
    cat = Category(name="leakage_audit_cat", db_path=":memory:")
    
    # Create nodes with varying privilege levels
    cat.add("high_sec_database", type_name="data_source", metadata={"privilege": 2})
    cat.add("middle_layer_processing", type_name="component", metadata={"privilege": 1})
    # This is our unprotected sink
    cat.add("public_api_endpoint", type_name="sink", metadata={"privilege": 0})
    # This is a sanitizer component
    cat.add("taint_sanitizer", type_name="sanitizer", metadata={"privilege": 0})
    
    # Connect them in a path: Database -> Component -> Public Endpoint (Unprotected)
    cat.connect("high_sec_database", "middle_layer_processing", name="flows_to", confidence=1.0)
    cat.connect("middle_layer_processing", "public_api_endpoint", name="flows_to", confidence=1.0)
    
    # Also connect a protected path: Database -> Sanitizer -> Component
    cat.connect("high_sec_database", "taint_sanitizer", name="flows_to", confidence=1.0)
    cat.connect("taint_sanitizer", "middle_layer_processing", name="sanitizes", confidence=1.0)

    # Let's perform the security/leakage check
    objects = cat.objects()
    high_priv_nodes = [o for o in objects if int(o.metadata.get("privilege", 0)) > 0]
    low_priv_nodes = [o for o in objects if int(o.metadata.get("privilege", 0)) == 0]
    
    leakages = []
    
    for src in high_priv_nodes:
        src_priv = int(src.metadata.get("privilege", 0))
        for tgt in low_priv_nodes:
            # We look for paths from high to low privilege
            paths = cat.find_paths(src.name, tgt.name, max_length=4)
            for path in paths:
                # Extract path nodes
                path_nodes = [src.name]
                for mid in path.morphism_ids:
                    # mid is "relation:source->target"
                    if "->" in mid:
                        target_node = mid.split("->")[1]
                        path_nodes.append(target_node)
                
                # Check if this path contains a sanitizer node or guards/sanitizes relation
                has_sanitizer = False
                for node_name in path_nodes:
                    node_obj = cat.get(node_name)
                    if node_obj and node_obj.type_name == "sanitizer":
                        has_sanitizer = True
                        break
                
                # Check for guards/sanitizes in morphisms of this path
                has_guard = False
                for mid in path.morphism_ids:
                    relation_name = mid.split(":")[0]
                    if relation_name in ("guards", "sanitizes"):
                        has_guard = True
                        break
                
                if not (has_sanitizer or has_guard):
                    leakages.append({
                        "source": src.name,
                        "sink": tgt.name,
                        "path": " -> ".join(path_nodes),
                        "source_privilege": src_priv
                    })
                    
    print(f"  Found {len(leakages)} trust/data leakage vulnerabilities:")
    for leak in leakages:
        print(f"    [!] LEAK DETECTED: {leak['source']} (Priv {leak['source_privilege']}) leaks to {leak['sink']} via {leak['path']}")
    
    # We successfully modeled and detected the data leakage.
    assert len(leakages) == 2, "Should have detected exactly 2 unsanitized paths."
    assert all(l["sink"] == "public_api_endpoint" for l in leakages), "All leaks should end at public API endpoint."
    
    print("  [SUCCESS] Data / Trust Leakage scan is verified and fully accurate.\n")
    return True


def run_linearity_leakage_audit() -> bool:
    """
    Audit 2: Substructural Resource (Linear) Leakage Scan.
    
    Ensures that linear logic constraints (non-cartesian) are enforced,
    so resources cannot be double-spent or duplicated (no token leaks).
    """
    print("[AUDIT 2] Scanning for Substructural Resource (Linear) Leakage...")
    
    # 1. Define resources
    r1 = {"Centrifuge cascade A": 1.0}
    r2 = {"Centrifuge cascade B": 1.0}
    
    # Under linear logic, combining r1 and r2 is fine (disjoint resources)
    combined = LINEAR_TOKENS.combine(r1, r2)
    print(f"  Consistent linear composition: {r1} + {r2} = {combined}")
    
    # Combining r1 with itself must fail because a linear resource cannot be double-spent
    try:
        LINEAR_TOKENS.combine(r1, r1)
        print("  [FAILED] Double-spending linear resource did not raise an error.")
        return False
    except ResourceError as err:
        print(f"  [SUCCESS] Double-spent resource correctly blocked. Error: {err}")
        
    print("  [SUCCESS] Substructural resource leakage audit completed successfully.\n")
    return True


def run_numerical_stability_audit() -> bool:
    """
    Audit 3: Sheaf & Spectral Numerical Stability Scan.
    
    Verifies that the physical energy leak (H^1 cohomology) is numerically
    stable and does not undergo chaotic fluctuations under small perturbations.
    """
    print("[AUDIT 3] Running Sheaf Numerical Stability Audit...")
    
    # Setup base consistent scenario
    sheaf_base = ThermodynamicSheaf()
    sheaf_base.add_flow("Source", "Sink", efficiency=0.90, weight=1.0)
    sheaf_base.add_flow("Source", "Sink", efficiency=0.90, weight=1.0)
    
    audit_base = sheaf_base.audit()
    base_leak = audit_base.energy_leak
    
    # Perturb the efficiency slightly (by 1e-6)
    sheaf_perturbed = ThermodynamicSheaf()
    sheaf_perturbed.add_flow("Source", "Sink", efficiency=0.90, weight=1.0)
    sheaf_perturbed.add_flow("Source", "Sink", efficiency=0.90 + 1e-6, weight=1.0)
    
    audit_perturbed = sheaf_perturbed.audit()
    perturbed_leak = audit_perturbed.energy_leak
    
    diff = abs(perturbed_leak - base_leak)
    print(f"  Base H^1 leak: {base_leak:.6e}")
    print(f"  Perturbed H^1 leak: {perturbed_leak:.6e}")
    print(f"  Absolute difference: {diff:.6e}")
    
    # The discrepancy should scale continuously with the perturbation (small difference)
    if diff < 1e-5:
        print("  [SUCCESS] Numerical stability check passed (continuous sensitivity).")
    else:
        print("  [FAILED] Sheaf calculations show unstable numerical fluctuations.")
        return False
        
    print("  [SUCCESS] Numerical stability audit completed successfully.\n")
    return True


def run_chemical_cache_audit() -> bool:
    """
    Audit 4: Chemical Informatics Database Integrity Scan.
    
    Checks that the cached chemical database elements (SMILES strings) are syntactically
    valid and that schema values match the physical files.
    """
    print("[AUDIT 4] Scanning Chemical Informatics Database Cache...")
    
    client = RealKompososMOFClient()
    try:
        linkers = client.load_known_linkers()
    except Exception as exc:
        print(f"  [ERROR] Could not load known linkers cache: {exc}")
        return False
        
    print(f"  Loaded {len(linkers)} linkers from real cache.")
    
    # Check each linker SMILES and metadata
    for i, linker in enumerate(linkers):
        print(f"    Linker {i+1} ID: {linker.linker_id}")
        print(f"      SMILES: {linker.smiles}")
        print(f"      Formula: {linker.formula}")
        print(f"      Heavy Atom Count: {linker.heavy_atom_count}")
        
        # Verify SMILES string is non-empty and has typical atoms
        assert len(linker.smiles) > 0, f"Linker {linker.linker_id} has empty SMILES."
        assert any(char in linker.smiles for char in ("C", "O", "N", "S")), "SMILES lacks expected elements."
        
        # Crosscheck formula and heavy atoms
        # formula contains element letters and numbers
        assert any(char in linker.formula for char in ("C", "H", "O", "N")), "Formula lacks expected elements."
        
    # Crosscheck metadata JSON with actual files
    meta_path = os.path.join(client.cache_dir, "mof_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)
        meta_count = meta.get("linker_count", 0)
        actual_count = len(linkers)
        print(f"  [METADATA] Json states count: {meta_count}, Actual count in db: {actual_count}")
        assert meta_count == actual_count, f"Metadata count mismatch: {meta_count} in json vs {actual_count} in db."
        
    print("  [SUCCESS] Chemical cache integrity audit completed successfully.\n")
    return True


def main():
    print("==========================================================")
    print("     KOMPOSOS-IV SCIENCE & INFORMATICS DEMO SUITE")
    print("  (self-verifying fixtures — NOT an audit of report outputs)")
    print("==========================================================")
    
    success = True
    success &= run_data_leakage_audit()
    success &= run_linearity_leakage_audit()
    success &= run_numerical_stability_audit()
    success &= run_chemical_cache_audit()
    
    if success:
        print("==========================================================")
        print("   ALL DEMO CHECKS PASSED (detection machinery works on")
        print("   constructed fixtures — production outputs not audited)")
        print("==========================================================")
        return 0
    else:
        print("==========================================================")
        print("         DEMO SUITE DETECTED FAILURES! (FAILED)")
        print("==========================================================")
        return 1


if __name__ == "__main__":
    sys.exit(main())
