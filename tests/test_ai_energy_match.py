"""Tests for the AI-energy matching engine (scripts/ai_energy_match.py)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "ai_energy_match", ROOT / "scripts" / "ai_energy_match.py"
)
aem = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = aem  # dataclasses need the module registered before exec
SPEC.loader.exec_module(aem)


@pytest.fixture(scope="module")
def fac():
    return aem.load_facilities(aem.DEFAULT_DATA)


@pytest.fixture(scope="module")
def result(fac):
    return aem.run(fac)


def test_data_file_loads(fac):
    assert len(fac.generators) >= 4
    assert len(fac.loads) >= 4
    assert fac.meta.get("sources"), "provenance sources should be present"


def test_cross_region_never_matches(fac):
    for g in fac.generators:
        for ld in fac.loads:
            if g.region != ld.region:
                assert aem.match_score(g, ld) == 0.0


def test_firm_load_rejects_variable_only_capacity():
    # A firm 24/7 load on variable-only capacity is not a co-location case.
    wind = aem.Generator("W", "X", 1000, 0.4, "wind", True)
    firm_load = aem.Load("F", "X", 200, 0.05, 4)
    assert aem.match_score(wind, firm_load) == 0.0
    # ...but firm generation can serve it.
    gas = aem.Generator("G", "X", 1000, 0.4, "gas", True)
    assert aem.match_score(gas, firm_load) > 0.0


def test_flexible_load_prefers_variable_pairing():
    # An 80%-interruptible load should score well against curtailed solar.
    solar = aem.Generator("S", "X", 1000, 0.5, "solar+storage", True)
    flex_load = aem.Load("B", "X", 250, 0.80, 3)
    assert aem.match_score(solar, flex_load) >= aem.MATCH_THRESHOLD


def test_matches_are_deterministic_and_within_capacity(result):
    # Re-running yields identical served MW (no randomness).
    again = aem.run(result.facilities)
    assert [m.mw_served for m in result.matches] == [m.mw_served for m in again.matches]
    # No match serves more than the load needs.
    for m in result.matches:
        assert m.mw_served <= m.load.needed_mw + 1e-6


def test_no_load_matched_twice(result):
    names = [m.load.name for m in result.matches]
    assert len(names) == len(set(names))


def test_spp_firm_load_is_honestly_stranded(result):
    # The wind-only SPP region cannot serve a firm 24/7 research load.
    stranded_names = {ld.name for ld in result.stranded_loads}
    assert any("Research Supercompute" in n for n in stranded_names)


def test_report_renders_with_provenance(result):
    report = aem.render(result)
    assert "AI-Energy Matching Audit" in report
    assert "Provenance" in report
    assert "hypothesis" in report.lower()
