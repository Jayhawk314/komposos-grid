from komposos_wesys.alignment import (
    ResourceFamily,
    TechnologyFamily,
    classify_resource,
    classify_technology,
    recommend_alignment,
)


def test_classifies_wesys_resource_and_technology_labels():
    assert classify_resource("ROTUS LF") == ResourceFamily.LANDFILL
    assert classify_resource("CA POTW") == ResourceFamily.POTW
    assert classify_resource("ROTUS CAFO") == ResourceFamily.CAFO
    assert classify_technology("Elec") == TechnologyFamily.ELECTRICITY
    assert classify_technology("CNG") == TechnologyFamily.CNG
    assert classify_technology("PNG") == TechnologyFamily.PNG


def test_landfill_electricity_hotspot_gets_utility_shared_savings_path():
    recommendation = recommend_alignment(
        "ROTUS LF",
        "Elec",
        conservative_exposure=400,
        prototype_savings=20_000_000,
        gap_type="interchange_failure",
    )

    assert recommendation.resource_family == ResourceFamily.LANDFILL
    assert recommendation.technology_family == TechnologyFamily.ELECTRICITY
    assert "utility" in {actor.name for actor in recommendation.actors}
    assert "shared-savings" in recommendation.contract_path
    assert "independent measurement" in recommendation.constraints_text()
    assert "exported kWh" in recommendation.measurement_text()


def test_cafo_cng_hotspot_gets_offtake_and_methane_measurement_path():
    recommendation = recommend_alignment(
        "ROTUS CAFO",
        "CNG",
        conservative_exposure=54,
        prototype_savings=2_700_000,
        gap_type="interchange_failure",
    )

    assert recommendation.resource_family == ResourceFamily.CAFO
    assert recommendation.technology_family == TechnologyFamily.CNG
    assert "fuel offtaker" in {actor.name for actor in recommendation.actors}
    assert "offtake" in recommendation.contract_path
    assert "methane capture" in recommendation.measurement_text()
    assert "fuel quality" in recommendation.measurement_text()


def test_small_hotspot_stays_screening_scale():
    recommendation = recommend_alignment(
        "unknown",
        "unknown",
        conservative_exposure=2,
        prototype_savings=50_000,
    )

    assert recommendation.confidence_tier == "screening prototype"
    assert "transaction-cost problem" in recommendation.game_diagnosis

