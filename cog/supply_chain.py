"""
COG Supply Chain — Automated dependency graph import and vulnerability detection.

Parses lockfiles (npm, pip, pipenv, cargo, go, composer) and SBOMs
(CycloneDX, SPDX) into the knowledge graph, queries OSV.dev for CVEs,
and runs 6 supply chain security rules:

  unaudited_path      — HOLLOW dependency paths (Tier 3)
  cve_exposure        — Paths from CVE-affected packages to app (Tier 1)
  concentration_risk  — Hub packages via Ricci curvature (Tier 4)
  diamond_dependency  — Same package at different versions, H1 loops (Tier 4)
  dead_dependency     — Declared but unreachable packages (Tier 3)
  stale_dependency    — Unmaintained packages (metadata check)
"""

from __future__ import annotations

import json
import logging
import re
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from .schema import (
    CogConcept, CogRelation, CogClaim,
    ConceptType, RelationType, VerificationStatus,
)

logger = logging.getLogger(__name__)


# ================================================================
# CVSS vector parser
# ================================================================


def parse_cvss_score(score_value) -> float:
    """Extract numeric CVSS base score from various OSV.dev formats.

    OSV.dev may return:
      - A numeric score directly (float/int)
      - A CVSS vector string like "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
      - A string numeric like "9.8"

    For vector strings, we compute the base score from the vector metrics.
    """
    if isinstance(score_value, (int, float)):
        return float(score_value)

    if not isinstance(score_value, str):
        return 0.0

    # Try direct float parse first
    try:
        return float(score_value)
    except (ValueError, TypeError):
        pass

    # Parse CVSS v3 vector string
    if score_value.startswith("CVSS:3"):
        return _compute_cvss3_from_vector(score_value)

    return 0.0


def _compute_cvss3_from_vector(vector: str) -> float:
    """Compute approximate CVSS v3 base score from a vector string.

    This is a simplified calculation that covers the base metrics.
    Follows the CVSS v3.1 specification for base score computation.
    """
    metrics = {}
    for part in vector.split("/"):
        if ":" in part:
            key, val = part.split(":", 1)
            metrics[key] = val

    # Impact weights
    av_weights = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.20}  # Attack Vector
    ac_weights = {"L": 0.77, "H": 0.44}                          # Attack Complexity
    pr_weights_unchanged = {"N": 0.85, "L": 0.62, "H": 0.27}    # Privileges Required (S:U)
    pr_weights_changed = {"N": 0.85, "L": 0.68, "H": 0.50}      # Privileges Required (S:C)
    ui_weights = {"N": 0.85, "R": 0.62}                          # User Interaction
    cia_weights = {"H": 0.56, "L": 0.22, "N": 0.0}              # C/I/A Impact

    scope_changed = metrics.get("S", "U") == "C"

    av = av_weights.get(metrics.get("AV", "N"), 0.85)
    ac = ac_weights.get(metrics.get("AC", "L"), 0.77)
    pr_map = pr_weights_changed if scope_changed else pr_weights_unchanged
    pr = pr_map.get(metrics.get("PR", "N"), 0.85)
    ui = ui_weights.get(metrics.get("UI", "N"), 0.85)

    c = cia_weights.get(metrics.get("C", "N"), 0.0)
    i = cia_weights.get(metrics.get("I", "N"), 0.0)
    a = cia_weights.get(metrics.get("A", "N"), 0.0)

    # ISS (Impact Sub-Score)
    iss = 1.0 - ((1.0 - c) * (1.0 - i) * (1.0 - a))

    if iss <= 0:
        return 0.0

    # Impact
    if scope_changed:
        impact = 7.52 * (iss - 0.029) - 3.25 * ((iss - 0.02) ** 15)
    else:
        impact = 6.42 * iss

    if impact <= 0:
        return 0.0

    # Exploitability
    exploitability = 8.22 * av * ac * pr * ui

    # Base score
    if scope_changed:
        base = min(1.08 * (impact + exploitability), 10.0)
    else:
        base = min(impact + exploitability, 10.0)

    # Round up to 1 decimal (CVSS spec uses "round up")
    import math
    return math.ceil(base * 10) / 10


# ================================================================
# Data types
# ================================================================


@dataclass
class ParsedDependency:
    """A single package extracted from a lockfile or SBOM."""
    name: str
    version: str
    ecosystem: str              # npm, pypi, cargo, go, maven, composer
    is_dev: bool = False
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ParsedLockfile:
    """Result of parsing a lockfile or SBOM."""
    ecosystem: str
    packages: List[ParsedDependency]
    app_name: str


# ================================================================
# Lockfile Parsers
# ================================================================


def parse_npm(content: str, app_name: str = "my_app") -> ParsedLockfile:
    """Parse package-lock.json (lockfileVersion 2/3)."""
    data = json.loads(content)
    packages: List[ParsedDependency] = []
    seen: Set[str] = set()

    # lockfileVersion 2+ uses "packages" dict
    pkgs_dict = data.get("packages", {})
    if pkgs_dict:
        for path, info in pkgs_dict.items():
            if not path:  # root entry
                continue
            # path is like "node_modules/lodash" or "node_modules/a/node_modules/b"
            name = path.split("node_modules/")[-1]
            if name in seen:
                continue
            seen.add(name)

            deps = list(info.get("dependencies", {}).keys())
            deps += list(info.get("optionalDependencies", {}).keys())
            packages.append(ParsedDependency(
                name=name,
                version=info.get("version", "unknown"),
                ecosystem="npm",
                is_dev=info.get("dev", False),
                dependencies=deps,
            ))
    else:
        # lockfileVersion 1 uses "dependencies" dict
        for name, info in data.get("dependencies", {}).items():
            if name in seen:
                continue
            seen.add(name)
            deps = list(info.get("requires", {}).keys())
            packages.append(ParsedDependency(
                name=name,
                version=info.get("version", "unknown"),
                ecosystem="npm",
                is_dev=info.get("dev", False),
                dependencies=deps,
            ))

    return ParsedLockfile(ecosystem="npm", packages=packages, app_name=app_name)


def parse_pip(content: str, app_name: str = "my_app") -> ParsedLockfile:
    """Parse requirements.txt."""
    packages: List[ParsedDependency] = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        # Handle ==, >=, <=, ~=, !=
        match = re.match(r'^([A-Za-z0-9_.-]+)\s*(?:[><=!~]+\s*(.+?))?$', line)
        if match:
            name = match.group(1).lower().replace("-", "_")
            version = match.group(2) or "any"
            # Strip extras like [security]
            name = re.sub(r'\[.*\]', '', name)
            packages.append(ParsedDependency(
                name=name,
                version=version,
                ecosystem="pypi",
            ))
    return ParsedLockfile(ecosystem="pypi", packages=packages, app_name=app_name)


def parse_pipenv(content: str, app_name: str = "my_app") -> ParsedLockfile:
    """Parse Pipfile.lock (JSON)."""
    data = json.loads(content)
    packages: List[ParsedDependency] = []

    for section, is_dev in [("default", False), ("develop", True)]:
        for name, info in data.get(section, {}).items():
            version = info.get("version", "any")
            if version.startswith("=="):
                version = version[2:]
            packages.append(ParsedDependency(
                name=name.lower().replace("-", "_"),
                version=version,
                ecosystem="pypi",
                is_dev=is_dev,
            ))
    return ParsedLockfile(ecosystem="pypi", packages=packages, app_name=app_name)


def parse_cargo(content: str, app_name: str = "my_app") -> ParsedLockfile:
    """Parse Cargo.lock (TOML-like format)."""
    packages: List[ParsedDependency] = []
    current: Optional[Dict[str, Any]] = None
    current_deps: List[str] = []
    in_deps = False

    for line in content.splitlines():
        line_stripped = line.strip()

        if line_stripped == "[[package]]":
            if current and current.get("name"):
                packages.append(ParsedDependency(
                    name=current["name"],
                    version=current.get("version", "unknown"),
                    ecosystem="cargo",
                    dependencies=current_deps,
                ))
            current = {}
            current_deps = []
            in_deps = False
            continue

        if current is None:
            continue

        if line_stripped == "dependencies = [":
            in_deps = True
            continue

        if in_deps:
            if line_stripped == "]":
                in_deps = False
                continue
            # Lines like: "serde 1.0.130",  or  "serde",
            dep_name = line_stripped.strip('" ,').split(" ")[0].strip('"')
            if dep_name:
                current_deps.append(dep_name)
            continue

        if "=" in line_stripped:
            key, _, val = line_stripped.partition("=")
            key = key.strip()
            val = val.strip().strip('"')
            if key == "name":
                current["name"] = val
            elif key == "version":
                current["version"] = val
            elif key == "dependencies":
                # Inline array: dependencies = ["dep1", "dep2"]
                deps_match = re.findall(r'"([^"]+)"', val)
                for d in deps_match:
                    current_deps.append(d.split(" ")[0])

    # Last package
    if current and current.get("name"):
        packages.append(ParsedDependency(
            name=current["name"],
            version=current.get("version", "unknown"),
            ecosystem="cargo",
            dependencies=current_deps,
        ))

    return ParsedLockfile(ecosystem="cargo", packages=packages, app_name=app_name)


def parse_go(content: str, app_name: str = "my_app") -> ParsedLockfile:
    """Parse go.sum."""
    packages: List[ParsedDependency] = []
    seen: Set[str] = set()

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        module = parts[0]
        version = parts[1].split("/")[0]  # strip /go.mod suffix
        key = f"{module}@{version}"
        if key in seen:
            continue
        seen.add(key)
        packages.append(ParsedDependency(
            name=module,
            version=version,
            ecosystem="go",
        ))

    return ParsedLockfile(ecosystem="go", packages=packages, app_name=app_name)


def parse_composer(content: str, app_name: str = "my_app") -> ParsedLockfile:
    """Parse composer.lock (JSON)."""
    data = json.loads(content)
    packages: List[ParsedDependency] = []

    for section, is_dev in [("packages", False), ("packages-dev", True)]:
        for pkg in data.get(section, []):
            deps = list(pkg.get("require", {}).keys())
            # Filter out PHP version constraints
            deps = [d for d in deps if not d.startswith("php") and not d.startswith("ext-")]
            packages.append(ParsedDependency(
                name=pkg.get("name", "unknown"),
                version=pkg.get("version", "unknown"),
                ecosystem="composer",
                is_dev=is_dev,
                dependencies=deps,
            ))

    return ParsedLockfile(ecosystem="composer", packages=packages, app_name=app_name)


LOCKFILE_PARSERS = {
    "npm": parse_npm,
    "pip": parse_pip,
    "pipenv": parse_pipenv,
    "cargo": parse_cargo,
    "go": parse_go,
    "composer": parse_composer,
}


# ================================================================
# Registry API Enrichment — fetch publish dates for stale_dependency
# ================================================================

# Registry URLs per ecosystem
REGISTRY_URLS = {
    "npm": "https://registry.npmjs.org/{name}",
    "pypi": "https://pypi.org/pypi/{name}/json",
    "composer": "https://repo.packagist.org/p2/{name}.json",
}


def _fetch_registry_metadata(
    name: str, version: str, ecosystem: str
) -> Dict[str, str]:
    """Fetch publish date and maintainer count from package registry.

    Returns a dict with optional keys: last_updated, maintainer_count.
    Fails silently — returns empty dict on any error.
    """
    meta: Dict[str, str] = {}

    if ecosystem == "npm":
        meta = _fetch_npm_metadata(name, version)
    elif ecosystem == "pypi":
        meta = _fetch_pypi_metadata(name, version)

    return meta


def _fetch_npm_metadata(name: str, version: str) -> Dict[str, str]:
    """Fetch metadata from npm registry."""
    meta: Dict[str, str] = {}
    try:
        url = f"https://registry.npmjs.org/{name}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        # Get publish time for specific version
        time_map = data.get("time", {})
        if version in time_map:
            meta["last_updated"] = time_map[version]
        elif "modified" in time_map:
            meta["last_updated"] = time_map["modified"]

        # Maintainer count
        maintainers = data.get("maintainers", [])
        if maintainers:
            meta["maintainer_count"] = str(len(maintainers))

    except Exception:
        pass
    return meta


def _fetch_pypi_metadata(name: str, version: str) -> Dict[str, str]:
    """Fetch metadata from PyPI JSON API."""
    meta: Dict[str, str] = {}
    try:
        url = f"https://pypi.org/pypi/{name}/{version}/json"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        # Upload time from release info
        urls = data.get("urls", [])
        if urls:
            upload_time = urls[0].get("upload_time_iso_8601", "")
            if upload_time:
                meta["last_updated"] = upload_time

        # Maintainer info
        info = data.get("info", {})
        author = info.get("author", "")
        maintainer = info.get("maintainer", "")
        if maintainer:
            meta["maintainer_count"] = "1"  # PyPI doesn't expose count
        elif author:
            meta["maintainer_count"] = "1"

    except Exception:
        pass
    return meta


# ================================================================
# SBOM Parsers
# ================================================================


def parse_cyclonedx(content: str, app_name: str = "my_app") -> ParsedLockfile:
    """Parse CycloneDX SBOM (JSON)."""
    data = json.loads(content)
    packages: List[ParsedDependency] = []
    ref_to_name: Dict[str, str] = {}

    # Build ref -> name map from components
    for comp in data.get("components", []):
        name = comp.get("name", "unknown")
        version = comp.get("version", "unknown")
        bom_ref = comp.get("bom-ref", name)
        ref_to_name[bom_ref] = name

        # Detect ecosystem from purl
        ecosystem = "unknown"
        purl = comp.get("purl", "")
        if "pkg:npm/" in purl:
            ecosystem = "npm"
        elif "pkg:pypi/" in purl:
            ecosystem = "pypi"
        elif "pkg:cargo/" in purl:
            ecosystem = "cargo"
        elif "pkg:golang/" in purl:
            ecosystem = "go"
        elif "pkg:maven/" in purl:
            ecosystem = "maven"
        elif "pkg:composer/" in purl:
            ecosystem = "composer"

        packages.append(ParsedDependency(
            name=name,
            version=version,
            ecosystem=ecosystem,
        ))

    # Parse dependency tree
    pkg_by_name = {p.name: p for p in packages}
    for dep_entry in data.get("dependencies", []):
        ref = dep_entry.get("ref", "")
        parent_name = ref_to_name.get(ref, ref)
        if parent_name in pkg_by_name:
            for child_ref in dep_entry.get("dependsOn", []):
                child_name = ref_to_name.get(child_ref, child_ref)
                pkg_by_name[parent_name].dependencies.append(child_name)

    # Detect primary ecosystem
    ecosystem_counts: Dict[str, int] = {}
    for p in packages:
        ecosystem_counts[p.ecosystem] = ecosystem_counts.get(p.ecosystem, 0) + 1
    primary_eco = max(ecosystem_counts, key=ecosystem_counts.get) if ecosystem_counts else "unknown"

    return ParsedLockfile(ecosystem=primary_eco, packages=packages, app_name=app_name)


def parse_spdx(content: str, app_name: str = "my_app") -> ParsedLockfile:
    """Parse SPDX SBOM (JSON)."""
    data = json.loads(content)
    packages: List[ParsedDependency] = []
    spdx_id_to_name: Dict[str, str] = {}

    for pkg in data.get("packages", []):
        name = pkg.get("name", "unknown")
        version = pkg.get("versionInfo", "unknown")
        spdx_id = pkg.get("SPDXID", "")
        spdx_id_to_name[spdx_id] = name

        # Detect ecosystem from externalRefs (purl)
        ecosystem = "unknown"
        for ref in pkg.get("externalRefs", []):
            locator = ref.get("referenceLocator", "")
            if "pkg:npm/" in locator:
                ecosystem = "npm"
            elif "pkg:pypi/" in locator:
                ecosystem = "pypi"
            elif "pkg:cargo/" in locator:
                ecosystem = "cargo"
            elif "pkg:golang/" in locator:
                ecosystem = "go"
            elif "pkg:maven/" in locator:
                ecosystem = "maven"

        packages.append(ParsedDependency(
            name=name,
            version=version,
            ecosystem=ecosystem,
        ))

    # Parse relationships
    pkg_by_name = {p.name: p for p in packages}
    for rel in data.get("relationships", []):
        if rel.get("relationshipType") == "DEPENDS_ON":
            parent_id = rel.get("spdxElementId", "")
            child_id = rel.get("relatedSpdxElement", "")
            parent_name = spdx_id_to_name.get(parent_id)
            child_name = spdx_id_to_name.get(child_id)
            if parent_name and child_name and parent_name in pkg_by_name:
                pkg_by_name[parent_name].dependencies.append(child_name)

    ecosystem_counts: Dict[str, int] = {}
    for p in packages:
        ecosystem_counts[p.ecosystem] = ecosystem_counts.get(p.ecosystem, 0) + 1
    primary_eco = max(ecosystem_counts, key=ecosystem_counts.get) if ecosystem_counts else "unknown"

    return ParsedLockfile(ecosystem=primary_eco, packages=packages, app_name=app_name)


def detect_sbom_format(content: str) -> Optional[str]:
    """Auto-detect SBOM format from content."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None
    if data.get("bomFormat") == "CycloneDX":
        return "cyclonedx"
    if "spdxVersion" in data:
        return "spdx"
    return None


# ================================================================
# Supply Chain Engine
# ================================================================


# Ecosystem name mapping for OSV.dev
ECOSYSTEM_MAP = {
    "npm": "npm",
    "pypi": "PyPI",
    "cargo": "crates.io",
    "go": "Go",
    "maven": "Maven",
    "composer": "Packagist",
}

SUPPLY_CHAIN_RULES = [
    "unaudited_path", "cve_exposure", "concentration_risk",
    "diamond_dependency", "dead_dependency", "stale_dependency",
    "dev_dependency_cve",
    # Cross-signal correlation rules (require imported Scorecard/VEX data)
    "unmaintained_critical_path", "vex_contradiction", "provenance_gap",
]


# ================================================================
# OpenSSF Scorecard
# ================================================================


SCORECARD_CHECKS = [
    "Binary-Artifacts", "Branch-Protection", "CI-Tests",
    "CII-Best-Practices", "Code-Review", "Contributors",
    "Dangerous-Workflow", "Dependency-Update-Tool", "Fuzzing",
    "License", "Maintained", "Packaging", "Pinned-Dependencies",
    "SAST", "Security-Policy", "Signed-Releases", "Token-Permissions",
    "Vulnerabilities",
]


def fetch_scorecard(repo: str) -> Optional[Dict[str, Any]]:
    """Fetch OpenSSF Scorecard for a GitHub repository.

    Args:
        repo: Repository in format "github.com/owner/name" or "owner/name"

    Returns:
        Dict with score, checks, and metadata, or None on failure.
    """
    # Normalize repo format
    if not repo.startswith("github.com/"):
        repo = f"github.com/{repo}"

    url = f"https://api.securityscorecards.dev/projects/{repo}"

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        result: Dict[str, Any] = {
            "repo": data.get("repo", {}).get("name", repo),
            "score": data.get("score", 0.0),
            "date": data.get("date", ""),
            "checks": {},
        }

        for check in data.get("checks", []):
            name = check.get("name", "")
            score = check.get("score", -1)
            result["checks"][name] = {
                "score": score,
                "reason": check.get("reason", ""),
            }

        return result

    except Exception as e:
        logger.debug(f"Scorecard fetch failed for {repo}: {e}")
        return None


class SupplyChainEngine:
    """Supply chain vulnerability detection built on CogEngine."""

    def __init__(self, engine):
        """
        Args:
            engine: CogEngine instance
        """
        self.engine = engine
        self.store = engine.store

    # ================================================================
    # VEX Import
    # ================================================================

    def import_vex(self, content: str) -> Dict[str, Any]:
        """Import a VEX (Vulnerability Exploitability eXchange) document.

        Supports OpenVEX and CycloneDX VEX formats (JSON).
        Maps VEX status to graph relations:
          - not_affected -> mitigates (CVE to product, suppresses false positive)
          - affected -> supports (CVE to product, confirms exploitability)
          - fixed -> mitigates with version note
          - under_investigation -> evidence (flagged for follow-up)

        Args:
            content: VEX document JSON string

        Returns:
            Dict with import stats.
        """
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {e}"}

        # Detect format
        if data.get("@context", "").startswith("https://openvex.dev"):
            return self._import_openvex(data)
        elif data.get("bomFormat") == "CycloneDX":
            return self._import_cyclonedx_vex(data)
        else:
            return {"error": "Unknown VEX format. Expected OpenVEX or CycloneDX."}

    def _import_openvex(self, data: Dict) -> Dict[str, Any]:
        """Import an OpenVEX document."""
        stats = {"statements_processed": 0, "relations_added": 0,
                 "false_positives_suppressed": 0, "confirmed_affected": 0}

        for stmt in data.get("statements", []):
            vuln = stmt.get("vulnerability", {})
            vuln_id = vuln.get("name", vuln.get("@id", "unknown"))
            status = stmt.get("status", "")
            justification = stmt.get("justification", "")
            status_notes = stmt.get("status_notes", "")

            for product in stmt.get("products", []):
                product_id = product.get("@id", "")
                # Extract package name from purl if available
                identifiers = product.get("identifiers", {})
                purl = identifiers.get("purl", product_id)
                product_name = self._purl_to_package_name(purl) or product_id

                self._apply_vex_status(
                    vuln_id, product_name, status, justification,
                    status_notes, stats,
                )
                stats["statements_processed"] += 1

        return stats

    def _import_cyclonedx_vex(self, data: Dict) -> Dict[str, Any]:
        """Import CycloneDX VEX (from vulnerabilities[].analysis)."""
        stats = {"statements_processed": 0, "relations_added": 0,
                 "false_positives_suppressed": 0, "confirmed_affected": 0}

        for vuln in data.get("vulnerabilities", []):
            vuln_id = vuln.get("id", "unknown")
            analysis = vuln.get("analysis", {})
            status = analysis.get("state", "")
            justification = analysis.get("justification", "")
            detail = analysis.get("detail", "")

            # Map CycloneDX states to OpenVEX-like states
            cdx_to_vex = {
                "not_affected": "not_affected",
                "exploitable": "affected",
                "resolved": "fixed",
                "in_triage": "under_investigation",
                "false_positive": "not_affected",
            }
            vex_status = cdx_to_vex.get(status, status)

            for affects in vuln.get("affects", []):
                ref = affects.get("ref", "")
                self._apply_vex_status(
                    vuln_id, ref, vex_status, justification, detail, stats,
                )
                stats["statements_processed"] += 1

        return stats

    def _apply_vex_status(
        self, vuln_id: str, product_name: str, status: str,
        justification: str, notes: str, stats: Dict[str, Any],
    ) -> None:
        """Apply a VEX status assertion to the graph."""
        if status == "not_affected":
            # Suppress the CVE — add a mitigates relation
            reason = justification or "VEX: not_affected"
            self.engine.assert_knowledge(CogRelation(
                source=f"vex:{vuln_id}:{product_name}",
                target=vuln_id,
                relation_type=RelationType.MITIGATES,
                confidence=0.9,
                evidence=f"VEX not_affected: {reason}. {notes}".strip(),
            ))
            # Also assert the VEX evidence concept
            self.engine.assert_knowledge(CogConcept(
                name=f"vex:{vuln_id}:{product_name}",
                concept_type=ConceptType.EVIDENCE,
                description=f"VEX: {vuln_id} does not affect {product_name}",
                metadata={
                    "vex_status": "not_affected",
                    "justification": justification,
                    "notes": notes,
                    "vuln_id": vuln_id,
                    "product": product_name,
                },
            ))
            stats["relations_added"] += 1
            stats["false_positives_suppressed"] += 1

        elif status == "affected":
            # Confirm the CVE is exploitable
            self.engine.assert_knowledge(CogRelation(
                source=f"vex:{vuln_id}:{product_name}",
                target=vuln_id,
                relation_type=RelationType.SUPPORTS,
                confidence=0.95,
                evidence=f"VEX confirmed affected. {notes}".strip(),
            ))
            self.engine.assert_knowledge(CogConcept(
                name=f"vex:{vuln_id}:{product_name}",
                concept_type=ConceptType.EVIDENCE,
                description=f"VEX: {vuln_id} confirmed to affect {product_name}",
                metadata={
                    "vex_status": "affected",
                    "notes": notes,
                    "vuln_id": vuln_id,
                    "product": product_name,
                },
            ))
            stats["relations_added"] += 1
            stats["confirmed_affected"] += 1

        elif status == "fixed":
            self.engine.assert_knowledge(CogRelation(
                source=f"vex:{vuln_id}:{product_name}",
                target=vuln_id,
                relation_type=RelationType.MITIGATES,
                confidence=0.85,
                evidence=f"VEX: fixed in {product_name}. {notes}".strip(),
            ))
            self.engine.assert_knowledge(CogConcept(
                name=f"vex:{vuln_id}:{product_name}",
                concept_type=ConceptType.EVIDENCE,
                description=f"VEX: {vuln_id} fixed in {product_name}",
                metadata={
                    "vex_status": "fixed",
                    "notes": notes,
                    "vuln_id": vuln_id,
                    "product": product_name,
                },
            ))
            stats["relations_added"] += 1
            stats["false_positives_suppressed"] += 1

        elif status == "under_investigation":
            self.engine.assert_knowledge(CogConcept(
                name=f"vex:{vuln_id}:{product_name}",
                concept_type=ConceptType.EVIDENCE,
                description=f"VEX: {vuln_id} under investigation for {product_name}",
                metadata={
                    "vex_status": "under_investigation",
                    "notes": notes,
                    "vuln_id": vuln_id,
                    "product": product_name,
                },
            ))

    def _purl_to_package_name(self, purl: str) -> Optional[str]:
        """Convert a package URL to a graph package name (name@version)."""
        if not purl or "pkg:" not in purl:
            return None

        # pkg:npm/express@4.18.2 -> express@4.18.2
        # pkg:pypi/requests@2.28.0 -> requests@2.28.0
        try:
            path = purl.split("pkg:")[1]
            # Remove ecosystem prefix
            if "/" in path:
                path = path.split("/", 1)[1]
            # Remove qualifiers (?...) and subpath (#...)
            path = path.split("?")[0].split("#")[0]
            return path
        except (IndexError, ValueError):
            return None

    # ================================================================
    # Scorecard Import
    # ================================================================

    def import_scorecard(self, repo: str,
                         package_name: Optional[str] = None) -> Dict[str, Any]:
        """Import OpenSSF Scorecard data for a repository into the graph.

        Associates scorecard scores with an existing package concept in the graph.
        If no package_name is given, creates a standalone concept for the repo.

        Args:
            repo: GitHub repository (e.g., "expressjs/express" or "github.com/expressjs/express")
            package_name: Optional package name in graph to attach scores to (e.g., "express@4.18.2")

        Returns:
            Dict with import stats and scorecard summary.
        """
        scorecard = fetch_scorecard(repo)
        if not scorecard:
            return {"error": f"Could not fetch scorecard for {repo}"}

        stats = {"concepts_updated": 0, "relations_added": 0}
        checks = scorecard.get("checks", {})

        # Build metadata from scorecard
        sc_metadata = {
            "scorecard_score": scorecard["score"],
            "scorecard_date": scorecard.get("date", ""),
            "scorecard_repo": scorecard.get("repo", repo),
        }
        for check_name, check_data in checks.items():
            key = f"sc_{check_name.lower().replace('-', '_')}"
            sc_metadata[key] = check_data["score"]

        # Attach to existing package or create a standalone concept
        target_name = package_name or scorecard.get("repo", repo)

        existing = self.store.get_object(target_name)
        if existing:
            # Update existing concept's metadata
            merged_meta = dict(existing.metadata or {})
            merged_meta.update(sc_metadata)
            self.engine.assert_knowledge(CogConcept(
                name=target_name,
                concept_type=ConceptType(existing.type_name),
                description=existing.description or "",
                metadata=merged_meta,
            ))
        else:
            self.engine.assert_knowledge(CogConcept(
                name=target_name,
                concept_type=ConceptType.COMPONENT,
                description=f"GitHub: {repo}",
                metadata=sc_metadata,
            ))
        stats["concepts_updated"] += 1

        # Create risk evidence concepts for critical low scores
        risk_checks = {
            "Maintained": ("low_maintenance_risk", "low",
                           "Project may be unmaintained — takeover risk"),
            "Code-Review": ("no_code_review_risk", "medium",
                            "Changes merged without review — malicious commit risk"),
            "Signed-Releases": ("unsigned_releases_risk", "medium",
                                "Releases not signed — artifact tampering risk"),
            "Pinned-Dependencies": ("unpinned_deps_risk", "low",
                                    "Dependencies not pinned — supply chain injection risk"),
            "Branch-Protection": ("unprotected_branch_risk", "medium",
                                  "Default branch unprotected — unauthorized push risk"),
            "Vulnerabilities": ("known_vuln_risk", "high",
                                "Known vulnerabilities detected by Scorecard"),
        }

        for check_name, (evidence_name, severity, desc) in risk_checks.items():
            check = checks.get(check_name, {})
            score = check.get("score", -1)
            if score >= 0 and score <= 3:  # Low score = risk
                evidence_id = f"{target_name}:{evidence_name}"
                self.engine.assert_knowledge(CogConcept(
                    name=evidence_id,
                    concept_type=ConceptType.EVIDENCE,
                    description=f"{desc} (Scorecard {check_name}={score}/10: {check.get('reason', '')})",
                    metadata={
                        "scorecard_check": check_name,
                        "scorecard_score": score,
                        "severity": severity,
                        "reason": check.get("reason", ""),
                    },
                ))
                self.engine.assert_knowledge(CogRelation(
                    source=evidence_id,
                    target=target_name,
                    relation_type=RelationType.EXPOSES,
                    confidence=max(0.3, 1.0 - score / 10.0),
                    evidence=f"Scorecard {check_name} score: {score}/10",
                ))
                stats["concepts_updated"] += 1
                stats["relations_added"] += 1

        return {
            "repo": scorecard.get("repo", repo),
            "overall_score": scorecard["score"],
            "checks": {k: v["score"] for k, v in checks.items()},
            "attached_to": target_name,
            **stats,
        }

    # ================================================================
    # Graph Import
    # ================================================================

    def import_lockfile(self, content: str, fmt: str,
                        app_name: str = "my_app",
                        enrich: bool = True) -> Dict[str, Any]:
        """Parse a lockfile and import into the knowledge graph.

        Args:
            content: Raw lockfile content
            fmt: Format name (npm, pip, pipenv, cargo, go, composer)
            app_name: Application name for the sink node
            enrich: If True, query registry APIs for publish dates (enables stale_dependency)
        """
        parser = LOCKFILE_PARSERS.get(fmt)
        if not parser:
            return {"error": f"Unknown format: {fmt}. Supported: {list(LOCKFILE_PARSERS.keys())}"}

        try:
            parsed = parser(content, app_name)
        except Exception as e:
            return {"error": f"Parse error: {e}"}

        return self._import_to_graph(parsed, enrich=enrich)

    def import_sbom(self, content: str, app_name: str = "my_app") -> Dict[str, Any]:
        """Parse an SBOM and import into the knowledge graph."""
        fmt = detect_sbom_format(content)
        if not fmt:
            return {"error": "Could not detect SBOM format. Expected CycloneDX or SPDX JSON."}

        parser = parse_cyclonedx if fmt == "cyclonedx" else parse_spdx
        try:
            parsed = parser(content, app_name)
        except Exception as e:
            return {"error": f"Parse error: {e}"}

        return self._import_to_graph(parsed)

    def _import_to_graph(self, parsed: ParsedLockfile,
                         enrich: bool = False) -> Dict[str, Any]:
        """Import a parsed lockfile/SBOM into the knowledge graph."""
        stats = {"concepts_added": 0, "relations_added": 0, "packages": 0,
                 "enriched": 0}

        registry_name = f"{parsed.ecosystem}_registry"
        self.engine.assert_knowledge(CogConcept(
            name=registry_name,
            concept_type=ConceptType.DATA_SOURCE,
            description=f"{parsed.ecosystem} package registry",
        ))
        stats["concepts_added"] += 1

        # App sink
        self.engine.assert_knowledge(CogConcept(
            name=parsed.app_name,
            concept_type=ConceptType.SINK,
            description=f"Application entry point: {parsed.app_name}",
        ))
        stats["concepts_added"] += 1

        # Track which packages have declared dependencies
        has_declared_deps: Set[str] = set()
        all_package_names: Set[str] = set()

        for pkg in parsed.packages:
            pkg_id = f"{pkg.name}@{pkg.version}"
            all_package_names.add(pkg_id)

            metadata = {
                "version": pkg.version,
                "ecosystem": pkg.ecosystem,
                "is_dev": pkg.is_dev,
            }

            # Enrich with registry data (publish dates, maintainer count)
            if enrich and pkg.ecosystem in REGISTRY_URLS:
                try:
                    reg_meta = _fetch_registry_metadata(
                        pkg.name, pkg.version, pkg.ecosystem
                    )
                    if reg_meta:
                        metadata.update(reg_meta)
                        stats["enriched"] += 1
                except Exception:
                    pass  # Enrichment is best-effort

            self.engine.assert_knowledge(CogConcept(
                name=pkg_id,
                concept_type=ConceptType.COMPONENT,
                description=f"{pkg.ecosystem} package {pkg.name} v{pkg.version}",
                metadata=metadata,
            ))
            stats["concepts_added"] += 1
            stats["packages"] += 1

            # Registry -> package
            self.engine.assert_knowledge(CogRelation(
                source=registry_name,
                target=pkg_id,
                relation_type=RelationType.DEPENDS_ON,
                confidence=0.9,
                evidence=f"Published on {parsed.ecosystem}",
            ))
            stats["relations_added"] += 1

        # Dependency edges between packages
        pkg_name_to_id: Dict[str, str] = {}
        for pkg in parsed.packages:
            pkg_name_to_id[pkg.name] = f"{pkg.name}@{pkg.version}"

        for pkg in parsed.packages:
            pkg_id = f"{pkg.name}@{pkg.version}"
            if pkg.dependencies:
                has_declared_deps.add(pkg_id)
            for dep_name in pkg.dependencies:
                dep_id = pkg_name_to_id.get(dep_name)
                if dep_id:
                    self.engine.assert_knowledge(CogRelation(
                        source=pkg_id,
                        target=dep_id,
                        relation_type=RelationType.DEPENDS_ON,
                        confidence=0.85,
                        evidence=f"{pkg.name} requires {dep_name}",
                    ))
                    stats["relations_added"] += 1

        # Top-level packages (those not depended on by others) -> app
        depended_on: Set[str] = set()
        for pkg in parsed.packages:
            for dep_name in pkg.dependencies:
                dep_id = pkg_name_to_id.get(dep_name)
                if dep_id:
                    depended_on.add(dep_id)

        top_level = all_package_names - depended_on
        for pkg_id in top_level:
            self.engine.assert_knowledge(CogRelation(
                source=pkg_id,
                target=parsed.app_name,
                relation_type=RelationType.DEPENDS_ON,
                confidence=0.9,
                evidence="Top-level dependency",
            ))
            stats["relations_added"] += 1

        return stats

    # ================================================================
    # CVE Query (OSV.dev)
    # ================================================================

    def query_vulnerabilities(self, ecosystem: str = "") -> Dict[str, Any]:
        """Query OSV.dev for vulnerabilities affecting imported packages."""
        objects = self.store.list_objects(limit=10000)
        components = [
            o for o in objects if o.type_name == "component"
        ]

        if not components:
            return {"error": "No packages in graph. Run cog_import_deps first."}

        # Build package list for OSV query
        packages: List[ParsedDependency] = []
        for comp in components:
            meta = comp.metadata or {}
            pkg_eco = meta.get("ecosystem", "")
            if ecosystem and pkg_eco != ecosystem:
                continue

            # Parse name@version from concept name
            if "@" in comp.name:
                name, version = comp.name.rsplit("@", 1)
            else:
                name = comp.name
                version = meta.get("version", "")

            if version and version != "unknown" and version != "any":
                packages.append(ParsedDependency(
                    name=name,
                    version=version,
                    ecosystem=pkg_eco,
                ))

        if not packages:
            return {"cves_found": 0, "packages_affected": 0, "message": "No versioned packages to check."}

        # Query OSV.dev in batches
        all_vulns = self._query_osv_batch(packages)

        # Assert CVEs into graph
        cves_added = 0
        packages_affected: Set[str] = set()
        for vuln in all_vulns:
            pkg_name = vuln["package"]
            pkg_version = vuln["version"]
            pkg_id = f"{pkg_name}@{pkg_version}"
            cve_id = vuln["id"]

            severity = vuln.get("severity", "unknown")
            cvss = vuln.get("cvss", 0.0)
            summary = vuln.get("summary", "")

            # Assert CVE as a claim
            self.engine.assert_knowledge(CogConcept(
                name=cve_id,
                concept_type=ConceptType.CLAIM,
                description=summary[:200] if summary else f"Vulnerability in {pkg_name}",
                metadata={
                    "cve_id": cve_id,
                    "cvss": cvss,
                    "severity": severity,
                    "summary": summary[:500] if summary else "",
                    "affected_package": pkg_name,
                    "affected_version": pkg_version,
                },
            ))

            # CVE contradicts the affected package's safety
            confidence = min(0.95, cvss / 10.0) if cvss else 0.7
            self.engine.assert_knowledge(CogRelation(
                source=cve_id,
                target=pkg_id,
                relation_type=RelationType.CONTRADICTS,
                confidence=confidence,
                evidence=f"{cve_id}: {summary[:100]}" if summary else cve_id,
            ))

            cves_added += 1
            packages_affected.add(pkg_id)

        return {
            "cves_found": cves_added,
            "packages_affected": len(packages_affected),
            "packages_checked": len(packages),
            "details": all_vulns[:20],  # Cap detail output
        }

    def _query_osv_batch(
        self, packages: List[ParsedDependency]
    ) -> List[Dict[str, Any]]:
        """Query OSV.dev API for vulnerabilities. Returns list of vuln dicts."""
        results: List[Dict[str, Any]] = []
        batch_size = 1000

        for i in range(0, len(packages), batch_size):
            batch = packages[i:i + batch_size]
            queries = []
            for pkg in batch:
                osv_eco = ECOSYSTEM_MAP.get(pkg.ecosystem, pkg.ecosystem)
                queries.append({
                    "version": pkg.version,
                    "package": {"name": pkg.name, "ecosystem": osv_eco},
                })

            try:
                payload = json.dumps({"queries": queries}).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.osv.dev/v1/querybatch",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))

                for idx, result_entry in enumerate(data.get("results", [])):
                    vulns = result_entry.get("vulns", [])
                    if not vulns:
                        continue
                    pkg = batch[idx]
                    for v in vulns:
                        severity = "unknown"
                        cvss = 0.0
                        for s in v.get("severity", []):
                            if s.get("type") == "CVSS_V3":
                                cvss = parse_cvss_score(s.get("score", 0))

                        # Map CVSS to severity
                        if cvss >= 9.0:
                            severity = "critical"
                        elif cvss >= 7.0:
                            severity = "high"
                        elif cvss >= 4.0:
                            severity = "medium"
                        elif cvss > 0:
                            severity = "low"

                        results.append({
                            "id": v.get("id", "unknown"),
                            "package": pkg.name,
                            "version": pkg.version,
                            "ecosystem": pkg.ecosystem,
                            "summary": v.get("summary", ""),
                            "severity": severity,
                            "cvss": cvss,
                        })

            except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
                logger.warning(f"OSV.dev query failed: {e}")
            except Exception as e:
                logger.warning(f"OSV.dev parse error: {e}")

        return results

    # ================================================================
    # Supply Chain Rules
    # ================================================================

    def run_rule(self, rule_name: str, scope: Optional[List[str]],
                 depth: int) -> List:
        """Run a single supply chain rule. Returns SecurityViolation list."""
        from .security import SecurityViolation

        rule_funcs = {
            "unaudited_path": self._rule_unaudited_path,
            "cve_exposure": self._rule_cve_exposure,
            "concentration_risk": self._rule_concentration_risk,
            "diamond_dependency": self._rule_diamond_dependency,
            "dead_dependency": self._rule_dead_dependency,
            "stale_dependency": self._rule_stale_dependency,
            "dev_dependency_cve": self._rule_dev_dependency_cve,
            "unmaintained_critical_path": self._rule_unmaintained_critical_path,
            "vex_contradiction": self._rule_vex_contradiction,
            "provenance_gap": self._rule_provenance_gap,
        }

        func = rule_funcs.get(rule_name)
        if not func:
            return []

        try:
            return func(scope, depth)
        except Exception as e:
            logger.warning(f"Supply chain rule {rule_name} failed: {e}")
            return []

    def _rule_unaudited_path(
        self, scope: Optional[List[str]], depth: int
    ) -> List:
        """
        HOLLOW dependency paths = structural path exists but no proof of safety.
        This is the Log4Shell/xz-utils pattern.
        """
        from .security import SecurityViolation

        violations = []
        objects = self.store.list_objects(limit=10000)

        registries = [o.name for o in objects if o.type_name == "data_source"
                      and o.name.endswith("_registry")]
        sinks = [o.name for o in objects if o.type_name == "sink"]

        for registry in registries:
            for sink in sinks:
                paths = self.store.find_paths(registry, sink, max_length=5)
                for path in paths:
                    nodes = self._extract_path_nodes(path)
                    if len(nodes) < 3:
                        continue

                    # Check middle nodes for HOLLOW status
                    for node in nodes[1:-1]:
                        claim = CogClaim(
                            source=node, target=sink,
                            relation="depends_on", confidence=0.5,
                        )
                        try:
                            result = self.engine.check_claim(claim, depth=3)
                            if result.status == VerificationStatus.HOLLOW:
                                violations.append(SecurityViolation(
                                    rule="unaudited_path",
                                    severity="high",
                                    source=registry,
                                    sink=sink,
                                    path=nodes,
                                    explanation=(
                                        f"HOLLOW: dependency path {' -> '.join(nodes)} "
                                        f"has no proof of safety at {node}. "
                                        f"Structural path exists but is logically unverified."
                                    ),
                                    owasp="A03:2025 Software Supply Chain Failures",
                                ))
                                break  # One violation per path
                        except Exception:
                            pass

        return violations

    def _rule_cve_exposure(
        self, scope: Optional[List[str]], depth: int
    ) -> List:
        """Find CVE-affected packages that are in the app's dependency tree."""
        from .security import SecurityViolation

        violations = []
        objects = self.store.list_objects(limit=10000)

        # Find all CVE concepts
        cve_concepts = [
            o for o in objects
            if o.type_name == "claim" and (o.metadata or {}).get("cve_id")
        ]

        sinks = [o.name for o in objects if o.type_name == "sink"]

        # Build reachability set for each sink
        sink_reachable: Dict[str, Set[str]] = {}
        for sink in sinks:
            reachable: Set[str] = set()
            self._collect_reachable_from_sink(sink, reachable)
            sink_reachable[sink] = reachable

        for cve in cve_concepts:
            meta = cve.metadata or {}
            cve_id = meta.get("cve_id", cve.name)
            affected_pkg = meta.get("affected_package", "")
            affected_ver = meta.get("affected_version", "")
            pkg_id = f"{affected_pkg}@{affected_ver}" if affected_ver else affected_pkg
            severity = meta.get("severity", "high")
            cvss = meta.get("cvss", 0.0)

            # Skip dev dependencies — they're handled by dev_dependency_cve rule
            if self._is_dev_package(pkg_id):
                continue

            for sink, reachable in sink_reachable.items():
                if pkg_id in reachable:
                    # Build a display path by finding how the app reaches this package
                    dep_chain = self._trace_dep_chain(sink, pkg_id)
                    violations.append(SecurityViolation(
                        rule="cve_exposure",
                        severity="critical" if severity in ("critical", "high") else severity,
                        source=cve_id,
                        sink=sink,
                        path=[cve_id] + dep_chain,
                        explanation=(
                            f"{cve_id} (CVSS {cvss}) affects {pkg_id}, "
                            f"which is in {sink}'s dependency tree: "
                            f"{' -> '.join(dep_chain)}. "
                            f"{meta.get('summary', '')[:100]}"
                        ),
                        owasp="A03:2025 Software Supply Chain Failures",
                    ))

        return violations

    def _trace_dep_chain(self, sink: str, target_pkg: str) -> List[str]:
        """Trace the depends_on chain from sink back to target_pkg."""
        # BFS from sink following incoming depends_on edges
        parent: Dict[str, str] = {}
        queue = [sink]
        visited = {sink}

        while queue:
            current = queue.pop(0)
            if current == target_pkg:
                # Reconstruct path
                path = [target_pkg]
                node = target_pkg
                while node in parent:
                    node = parent[node]
                    path.append(node)
                path.reverse()
                return path

            incoming = self.store.get_morphisms_to(current)
            for m in incoming:
                if m.name == "depends_on" and m.source_name not in visited:
                    visited.add(m.source_name)
                    parent[m.source_name] = current
                    queue.append(m.source_name)
                    # Also follow this package's deps
                    outgoing = self.store.get_morphisms_from(m.source_name)
                    for o in outgoing:
                        if o.name == "depends_on" and o.target_name not in visited:
                            visited.add(o.target_name)
                            parent[o.target_name] = m.source_name
                            queue.append(o.target_name)

        return [sink, "...", target_pkg]

    def _rule_concentration_risk(
        self, scope: Optional[List[str]], depth: int
    ) -> List:
        """Hub packages that everything depends on — Ricci curvature analysis."""
        from .security import SecurityViolation

        violations = []

        try:
            from geometry.ricci import compute_graph_curvature
            curvature_result = compute_graph_curvature(self.store)

            # High positive curvature = many convergent paths = concentration risk
            for node, curv in curvature_result.node_curvatures.items():
                if curv <= 0.5:
                    continue

                obj = self.store.get_object(node)
                if not obj or obj.type_name != "component":
                    continue

                # Count dependents
                incoming = self.store.get_morphisms_to(node)
                dep_count = sum(1 for m in incoming if m.name == "depends_on")

                if dep_count >= 3:
                    violations.append(SecurityViolation(
                        rule="concentration_risk",
                        severity="medium",
                        source=node,
                        sink=node,
                        path=[node],
                        explanation=(
                            f"Hub dependency: {dep_count} packages depend on {node} "
                            f"(curvature={curv:.2f}). Compromise here affects "
                            f"the entire dependency tree."
                        ),
                        owasp="A03:2025 Software Supply Chain Failures",
                    ))

        except Exception as e:
            logger.debug(f"concentration_risk rule: curvature unavailable: {e}")
            # Fallback: count incoming depends_on edges
            objects = self.store.list_objects(limit=10000)
            for obj in objects:
                if obj.type_name != "component":
                    continue
                incoming = self.store.get_morphisms_to(obj.name)
                dep_count = sum(1 for m in incoming if m.name == "depends_on")
                if dep_count >= 5:
                    violations.append(SecurityViolation(
                        rule="concentration_risk",
                        severity="medium",
                        source=obj.name,
                        sink=obj.name,
                        path=[obj.name],
                        explanation=(
                            f"Hub dependency: {dep_count} packages depend on {obj.name}. "
                            f"Compromise here affects the entire dependency tree."
                        ),
                        owasp="A03:2025 Software Supply Chain Failures",
                    ))

        return violations

    def _rule_diamond_dependency(
        self, scope: Optional[List[str]], depth: int
    ) -> List:
        """Same package required at different versions — diamond dependency."""
        from .security import SecurityViolation

        violations = []
        objects = self.store.list_objects(limit=10000)
        components = [o for o in objects if o.type_name == "component"]

        # Group by base package name (strip version)
        by_base: Dict[str, List[str]] = {}
        for comp in components:
            if "@" in comp.name:
                base = comp.name.rsplit("@", 1)[0]
                by_base.setdefault(base, []).append(comp.name)

        for base, versions in by_base.items():
            if len(versions) < 2:
                continue

            # Multiple versions of the same package = diamond
            violations.append(SecurityViolation(
                rule="diamond_dependency",
                severity="medium",
                source=versions[0],
                sink=versions[-1],
                path=versions,
                explanation=(
                    f"Diamond dependency: {base} required at "
                    f"{len(versions)} versions: {', '.join(versions)}. "
                    f"Version conflicts can cause subtle bugs or "
                    f"security policy inconsistencies."
                ),
                owasp="A03:2025 Software Supply Chain Failures",
            ))

        # Also try persistent homology for H1 loops if available
        try:
            from topology.persistent_homology import (
                SimplicialComplex, PersistentHomologyComputer,
            )

            sc = SimplicialComplex()
            name_to_idx: Dict[str, int] = {}
            for i, comp in enumerate(components):
                name_to_idx[comp.name] = i
                sc.add_simplex((i,), filtration_value=0.0)

            morphisms = self.store.list_morphisms(limit=100000)
            for m in morphisms:
                if m.name != "depends_on":
                    continue
                src_idx = name_to_idx.get(m.source_name)
                tgt_idx = name_to_idx.get(m.target_name)
                if src_idx is not None and tgt_idx is not None and src_idx != tgt_idx:
                    sc.add_simplex((src_idx, tgt_idx), filtration_value=0.5)

            computer = PersistentHomologyComputer()
            diagram = computer.compute(sc)
            betti = diagram.betti_numbers_at(0.75)
            h1 = betti.get(1, 0)

            if h1 > 0 and not violations:
                violations.append(SecurityViolation(
                    rule="diamond_dependency",
                    severity="medium",
                    source="dependency_graph",
                    sink="dependency_graph",
                    path=[],
                    explanation=(
                        f"Persistent homology detected {h1} H1 loop(s) in "
                        f"the dependency graph, indicating circular or "
                        f"diamond dependency patterns."
                    ),
                    owasp="A03:2025 Software Supply Chain Failures",
                ))

        except Exception as e:
            logger.debug(f"diamond_dependency: homology unavailable: {e}")

        return violations

    def _rule_dead_dependency(
        self, scope: Optional[List[str]], depth: int
    ) -> List:
        """Packages declared in lockfile but not reachable from the app."""
        from .security import SecurityViolation

        violations = []
        objects = self.store.list_objects(limit=10000)

        components = [o.name for o in objects if o.type_name == "component"]
        sinks = [o.name for o in objects if o.type_name == "sink"]

        if not sinks:
            return violations

        # Build the set of all packages reachable from any sink
        # by walking depends_on edges backwards (sink <- top-level <- transitive deps)
        reachable: Set[str] = set()
        for sink in sinks:
            self._collect_reachable_from_sink(sink, reachable)

        for comp in components:
            if comp not in reachable:
                violations.append(SecurityViolation(
                    rule="dead_dependency",
                    severity="low",
                    source=comp,
                    sink="none",
                    path=[comp],
                    explanation=(
                        f"Dead dependency: {comp} is in the lockfile but not "
                        f"reachable from any application entry point. "
                        f"Consider removing to reduce attack surface."
                    ),
                    owasp="A03:2025 Software Supply Chain Failures",
                ))

        return violations

    def _collect_reachable_from_sink(
        self, sink: str, reachable: Set[str]
    ) -> None:
        """Walk depends_on edges backwards from sink to find all reachable packages."""
        # Packages that depend_on the sink (or on something reachable)
        queue = [sink]
        visited = {sink}
        while queue:
            current = queue.pop(0)
            incoming = self.store.get_morphisms_to(current)
            for m in incoming:
                if m.name == "depends_on" and m.source_name not in visited:
                    visited.add(m.source_name)
                    reachable.add(m.source_name)
                    queue.append(m.source_name)
                    # Also follow the source's own dependencies
                    outgoing = self.store.get_morphisms_from(m.source_name)
                    for o in outgoing:
                        if o.name == "depends_on" and o.target_name not in visited:
                            visited.add(o.target_name)
                            reachable.add(o.target_name)
                            queue.append(o.target_name)

    def _rule_stale_dependency(
        self, scope: Optional[List[str]], depth: int
    ) -> List:
        """Packages that haven't been updated in a long time."""
        from .security import SecurityViolation

        violations = []
        objects = self.store.list_objects(limit=10000)
        now = datetime.now(timezone.utc)

        for obj in objects:
            if obj.type_name != "component":
                continue

            meta = obj.metadata or {}
            last_updated = meta.get("last_updated") or meta.get("version_date")
            if not last_updated:
                continue

            try:
                if isinstance(last_updated, str):
                    # Try ISO format
                    update_date = datetime.fromisoformat(
                        last_updated.replace("Z", "+00:00")
                    )
                else:
                    continue

                age_days = (now - update_date).days
                if age_days > 730:  # 2 years
                    years = age_days / 365
                    violations.append(SecurityViolation(
                        rule="stale_dependency",
                        severity="low",
                        source=obj.name,
                        sink=obj.name,
                        path=[obj.name],
                        explanation=(
                            f"Stale dependency: {obj.name} last updated "
                            f"{years:.1f} years ago ({last_updated}). "
                            f"Unmaintained packages may contain unpatched vulnerabilities."
                        ),
                        owasp="A03:2025 Software Supply Chain Failures",
                    ))

            except (ValueError, TypeError):
                continue

        return violations

    # ================================================================
    # Cross-Signal Correlation Rules
    # ================================================================

    def _rule_unmaintained_critical_path(
        self, scope: Optional[List[str]], depth: int
    ) -> List:
        """Unmaintained package on a critical path — correlates Scorecard + topology.

        Fires when a package has:
          1. Low Scorecard maintenance score (sc_maintained <= 3) OR stale metadata
          2. AND is a concentration risk (many dependents) OR on a critical path

        This is COG's unique cross-signal correlation — no single tool detects this.
        """
        from .security import SecurityViolation

        violations = []
        objects = self.store.list_objects(limit=10000)

        for obj in objects:
            if obj.type_name != "component":
                continue

            meta = obj.metadata or {}

            # Check maintenance signals
            sc_maintained = meta.get("sc_maintained", -1)
            sc_code_review = meta.get("sc_code_review", -1)
            last_updated = meta.get("last_updated", "")

            is_unmaintained = False
            reasons = []

            if isinstance(sc_maintained, (int, float)) and 0 <= sc_maintained <= 3:
                is_unmaintained = True
                reasons.append(f"Scorecard Maintained={sc_maintained}/10")

            if isinstance(sc_code_review, (int, float)) and 0 <= sc_code_review <= 2:
                reasons.append(f"Scorecard Code-Review={sc_code_review}/10")

            # Check staleness from metadata
            if last_updated and not is_unmaintained:
                try:
                    update_date = datetime.fromisoformat(
                        last_updated.replace("Z", "+00:00")
                    )
                    age_days = (datetime.now(timezone.utc) - update_date).days
                    if age_days > 730:
                        is_unmaintained = True
                        reasons.append(f"last updated {age_days // 365}y ago")
                except (ValueError, TypeError):
                    pass

            if not is_unmaintained:
                continue

            # Check if this is a critical/hub package
            incoming = self.store.get_morphisms_to(obj.name)
            dep_count = sum(1 for m in incoming if m.name == "depends_on")

            is_critical = dep_count >= 3

            if not is_critical:
                # Check if it's on a path from registry to app
                sinks = [o.name for o in objects if o.type_name == "sink"]
                for sink in sinks:
                    paths = self.store.find_paths(obj.name, sink, max_length=3)
                    if paths:
                        is_critical = True
                        break

            if is_critical:
                violations.append(SecurityViolation(
                    rule="unmaintained_critical_path",
                    severity="high",
                    source=obj.name,
                    sink=obj.name,
                    path=[obj.name],
                    explanation=(
                        f"CROSS-SIGNAL: {obj.name} is unmaintained "
                        f"({'; '.join(reasons)}) AND is a critical dependency "
                        f"({dep_count} dependents). Unmaintained hub packages "
                        f"are prime targets for maintainer takeover attacks "
                        f"(cf. xz-utils CVE-2024-3094)."
                    ),
                    owasp="A03:2025 Software Supply Chain Failures",
                ))

        return violations

    def _rule_vex_contradiction(
        self, scope: Optional[List[str]], depth: int
    ) -> List:
        """Detect contradictory VEX assessments for the same CVE.

        Fires when:
          - Multiple VEX sources disagree (one says not_affected, another says affected)
          - A VEX says not_affected but Scorecard Vulnerabilities check flags it
        """
        from .security import SecurityViolation

        violations = []
        objects = self.store.list_objects(limit=10000)

        # Group VEX evidence by vulnerability ID
        vex_by_vuln: Dict[str, List] = {}
        for obj in objects:
            if obj.type_name != "evidence":
                continue
            meta = obj.metadata or {}
            if "vex_status" not in meta:
                continue
            vuln_id = meta.get("vuln_id", "")
            if vuln_id:
                vex_by_vuln.setdefault(vuln_id, []).append(obj)

        for vuln_id, evidence_list in vex_by_vuln.items():
            statuses = set()
            for ev in evidence_list:
                statuses.add((ev.metadata or {}).get("vex_status", ""))

            # Check for contradiction: not_affected + affected for same CVE
            if "not_affected" in statuses and "affected" in statuses:
                products = [
                    (e.metadata or {}).get("product", "unknown")
                    for e in evidence_list
                ]
                violations.append(SecurityViolation(
                    rule="vex_contradiction",
                    severity="high",
                    source=vuln_id,
                    sink=vuln_id,
                    path=[vuln_id] + products,
                    explanation=(
                        f"VEX CONTRADICTION: {vuln_id} is marked both "
                        f"'not_affected' and 'affected' across different "
                        f"products/assessments. Manual review required. "
                        f"Products: {', '.join(products)}"
                    ),
                    owasp="A03:2025 Software Supply Chain Failures",
                ))

        return violations

    def _rule_provenance_gap(
        self, scope: Optional[List[str]], depth: int
    ) -> List:
        """Packages on critical paths with no provenance/signing evidence.

        Fires when a hub or critical-path package has:
          - No Scorecard Signed-Releases data OR score <= 2
          - AND is depended on by >= 3 packages

        Without provenance, there's no way to verify the package was built
        from its claimed source — making it vulnerable to build tampering.
        """
        from .security import SecurityViolation

        violations = []
        objects = self.store.list_objects(limit=10000)

        for obj in objects:
            if obj.type_name != "component":
                continue

            meta = obj.metadata or {}
            sc_signed = meta.get("sc_signed_releases", -1)

            # No scorecard data at all, or low signing score
            has_provenance = (
                isinstance(sc_signed, (int, float)) and sc_signed > 2
            )

            if has_provenance:
                continue

            # Check if it's a critical package
            incoming = self.store.get_morphisms_to(obj.name)
            dep_count = sum(1 for m in incoming if m.name == "depends_on")

            if dep_count < 3:
                continue

            note = (
                f"no Scorecard data (sc_signed_releases not imported)"
                if sc_signed == -1
                else f"Scorecard Signed-Releases={sc_signed}/10"
            )

            violations.append(SecurityViolation(
                rule="provenance_gap",
                severity="medium",
                source=obj.name,
                sink=obj.name,
                path=[obj.name],
                explanation=(
                    f"PROVENANCE GAP: {obj.name} has {dep_count} dependents "
                    f"but {note}. Without signed releases, there is no proof "
                    f"the published package matches the source code. "
                    f"Import Scorecard data with cog_import_scorecard to verify."
                ),
                owasp="A03:2025 Software Supply Chain Failures",
            ))

        return violations

    # ================================================================
    # Bulk Scorecard Import
    # ================================================================

    def _discover_github_repo(self, name: str, ecosystem: str) -> Optional[str]:
        """Discover the GitHub repo for a package by querying its registry.

        Args:
            name: Package name (without version, e.g. "express" not "express@4.18.2")
            ecosystem: Package ecosystem ("npm", "pypi", etc.)

        Returns:
            GitHub repo in "owner/name" format, or None if not found.
        """
        try:
            if ecosystem == "npm":
                return self._discover_github_repo_npm(name)
            elif ecosystem == "pypi":
                return self._discover_github_repo_pypi(name)
        except Exception as e:
            logger.debug(f"GitHub repo discovery failed for {name} ({ecosystem}): {e}")
        return None

    def _discover_github_repo_npm(self, name: str) -> Optional[str]:
        """Extract GitHub repo from npm registry metadata."""
        url = f"https://registry.npmjs.org/{name}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        repo_info = data.get("repository", {})
        if isinstance(repo_info, str):
            repo_url = repo_info
        elif isinstance(repo_info, dict):
            repo_url = repo_info.get("url", "")
        else:
            return None

        return self._extract_github_repo_from_url(repo_url)

    def _discover_github_repo_pypi(self, name: str) -> Optional[str]:
        """Extract GitHub repo from PyPI metadata."""
        url = f"https://pypi.org/pypi/{name}/json"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        info = data.get("info", {})

        # Check project_urls first (more reliable)
        project_urls = info.get("project_urls") or {}
        for key in ("Source", "Source Code", "Repository", "GitHub", "Homepage", "Code"):
            url_val = project_urls.get(key, "")
            if url_val and "github.com" in url_val:
                repo = self._extract_github_repo_from_url(url_val)
                if repo:
                    return repo

        # Fallback to home_page
        home_page = info.get("home_page", "")
        if home_page and "github.com" in home_page:
            return self._extract_github_repo_from_url(home_page)

        return None

    @staticmethod
    def _extract_github_repo_from_url(url: str) -> Optional[str]:
        """Extract 'owner/name' from a GitHub URL.

        Handles:
          - https://github.com/owner/name
          - git+https://github.com/owner/name.git
          - git://github.com/owner/name.git
          - github:owner/name
          - ssh://git@github.com/owner/name.git
        """
        if not url:
            return None

        # Strip common prefixes
        url = url.replace("git+", "").replace("git://", "https://")
        url = url.replace("ssh://git@github.com", "https://github.com")

        # Handle github:owner/name shorthand
        if url.startswith("github:"):
            path = url[7:]
            parts = path.strip("/").split("/")
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1].replace('.git', '')}"

        # Parse standard URLs
        match = re.search(r'github\.com[/:]([^/]+)/([^/#?]+)', url)
        if match:
            owner = match.group(1)
            name = match.group(2).replace(".git", "")
            return f"{owner}/{name}"

        return None

    def import_scorecards_bulk(self) -> Dict[str, Any]:
        """Import OpenSSF Scorecard for all component packages in the graph.

        Iterates all component concepts, discovers their GitHub repos via
        registry APIs (npm, PyPI), and imports Scorecard data for each.

        Returns:
            Dict with summary: {checked, imported, skipped, errors}
        """
        objects = self.store.list_objects(limit=10000)
        components = [o for o in objects if o.type_name == "component"]

        stats: Dict[str, Any] = {
            "checked": 0,
            "imported": 0,
            "skipped": 0,
            "errors": [],
            "details": [],
        }

        for comp in components:
            meta = comp.metadata or {}
            ecosystem = meta.get("ecosystem", "")

            # Only npm and pypi have registry -> GitHub mapping
            if ecosystem not in ("npm", "pypi"):
                stats["skipped"] += 1
                continue

            # Extract base name (strip version)
            if "@" in comp.name:
                base_name = comp.name.rsplit("@", 1)[0]
            else:
                base_name = comp.name

            stats["checked"] += 1

            # Skip if scorecard already imported for this package
            if meta.get("scorecard_score") is not None:
                stats["skipped"] += 1
                continue

            repo = self._discover_github_repo(base_name, ecosystem)
            if not repo:
                stats["skipped"] += 1
                stats["details"].append({
                    "package": comp.name,
                    "status": "no_github_repo",
                })
                continue

            try:
                result = self.import_scorecard(repo, comp.name)
                if "error" in result:
                    stats["errors"].append({
                        "package": comp.name,
                        "repo": repo,
                        "error": result["error"],
                    })
                else:
                    stats["imported"] += 1
                    stats["details"].append({
                        "package": comp.name,
                        "repo": repo,
                        "score": result.get("overall_score", 0),
                    })
            except Exception as e:
                stats["errors"].append({
                    "package": comp.name,
                    "repo": repo,
                    "error": str(e),
                })

        # Cap details output
        if len(stats["details"]) > 50:
            stats["details"] = stats["details"][:50]
        if len(stats["errors"]) > 20:
            stats["errors"] = stats["errors"][:20]

        return stats

    # ================================================================
    # Bootstrap — auto-populate from project files
    # ================================================================

    def bootstrap(self, directory: str = ".",
                  scan_vulns: bool = True) -> Dict[str, Any]:
        """Auto-populate the graph from project files in the given directory.

        Scans for lockfiles and SBOMs, imports each one found, and
        optionally queries OSV.dev for CVEs.

        Args:
            directory: Directory to scan (default: current working directory)
            scan_vulns: If True, also run cog_import_vulns after importing

        Returns:
            Dict with what was found and imported.
        """
        import os as _os

        stats: Dict[str, Any] = {
            "lockfiles": [],
            "sboms": [],
            "packages": 0,
            "cves": 0,
            "ecosystems": set(),
        }

        # Known lockfile names -> format
        lockfile_map = {
            "package-lock.json": "npm",
            "requirements.txt": "pip",
            "Pipfile.lock": "pipenv",
            "Cargo.lock": "cargo",
            "go.sum": "go",
            "composer.lock": "composer",
        }

        # Known SBOM filenames
        sbom_names = {"sbom.json", "bom.json", "cyclonedx.json", "spdx.json"}

        # Derive app_name from directory
        app_name = _os.path.basename(_os.path.abspath(directory)) or "my_app"

        # Scan for lockfiles
        for filename, fmt in lockfile_map.items():
            filepath = _os.path.join(directory, filename)
            if _os.path.isfile(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    result = self.import_lockfile(
                        content, fmt, app_name, enrich=False,
                    )
                    if "error" not in result:
                        stats["lockfiles"].append({
                            "file": filename,
                            "format": fmt,
                            "packages": result.get("packages", 0),
                        })
                        stats["packages"] += result.get("packages", 0)
                        stats["ecosystems"].add(fmt)
                except Exception as e:
                    stats["lockfiles"].append({
                        "file": filename,
                        "format": fmt,
                        "error": str(e),
                    })

        # Scan for SBOMs
        for filename in sorted(_os.listdir(directory)):
            if filename.lower() in sbom_names or (
                filename.endswith(".json") and "sbom" in filename.lower()
            ):
                filepath = _os.path.join(directory, filename)
                if not _os.path.isfile(filepath):
                    continue
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    fmt = detect_sbom_format(content)
                    if fmt:
                        result = self.import_sbom(content, app_name)
                        if "error" not in result:
                            stats["sboms"].append({
                                "file": filename,
                                "format": fmt,
                                "packages": result.get("packages", 0),
                            })
                            stats["packages"] += result.get("packages", 0)
                except Exception as e:
                    stats["sboms"].append({
                        "file": filename,
                        "error": str(e),
                    })

        # Query CVEs for discovered ecosystems
        if scan_vulns and stats["packages"] > 0:
            eco_map = {
                "npm": "npm", "pip": "pypi", "pipenv": "pypi",
                "cargo": "cargo", "go": "go", "composer": "composer",
            }
            for eco in stats["ecosystems"]:
                osv_eco = eco_map.get(eco, "")
                if osv_eco:
                    try:
                        vuln_result = self.query_vulnerabilities(osv_eco)
                        stats["cves"] += vuln_result.get("cves_found", 0)
                    except Exception:
                        pass

        # Convert set to list for JSON serialization
        stats["ecosystems"] = list(stats["ecosystems"])

        return stats

    # ================================================================
    # Dev dependency helpers
    # ================================================================

    def _is_dev_package(self, pkg_name: str) -> bool:
        """Check if a package is a dev dependency by its metadata."""
        obj = self.store.get_object(pkg_name)
        if obj and obj.metadata:
            return bool(obj.metadata.get("is_dev", False))
        return False

    def _rule_dev_dependency_cve(
        self, scope: Optional[List[str]], depth: int
    ) -> List:
        """CVEs in dev dependencies — lower severity since they don't ship to prod."""
        from .security import SecurityViolation

        violations = []
        objects = self.store.list_objects(limit=10000)

        cve_concepts = [
            o for o in objects
            if o.type_name == "claim" and (o.metadata or {}).get("cve_id")
        ]

        for cve in cve_concepts:
            meta = cve.metadata or {}
            cve_id = meta.get("cve_id", cve.name)
            affected_pkg = meta.get("affected_package", "")
            affected_ver = meta.get("affected_version", "")
            pkg_id = f"{affected_pkg}@{affected_ver}" if affected_ver else affected_pkg

            if not self._is_dev_package(pkg_id):
                continue

            violations.append(SecurityViolation(
                rule="dev_dependency_cve",
                severity="low",
                source=cve_id,
                sink=pkg_id,
                path=[cve_id, pkg_id],
                explanation=(
                    f"{cve_id} affects dev dependency {pkg_id}. "
                    f"Dev dependencies don't ship to production but can "
                    f"compromise the build environment. "
                    f"{meta.get('summary', '')[:100]}"
                ),
                owasp="A03:2025 Software Supply Chain Failures",
            ))

        return violations

    # ================================================================
    # Helpers
    # ================================================================

    def _extract_path_nodes(self, stored_path) -> List[str]:
        """Extract node names from a StoredPath's morphism_ids."""
        nodes = []
        for mid in stored_path.morphism_ids:
            if "->" in mid:
                parts = mid.split("->")
                source_part = parts[0].split(":")[-1] if ":" in parts[0] else parts[0]
                target_part = parts[1]
                if not nodes:
                    nodes.append(source_part)
                nodes.append(target_part)
        if not nodes and stored_path.morphism_ids:
            nodes = [stored_path.morphism_ids[0]]
        return nodes
