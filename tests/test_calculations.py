import pytest

from retrofit_analysis.comfort import calculate_relative_productivity
from retrofit_analysis.economics import (
    BuildingAreas,
    adjustment_factors,
    calculate_npc,
    market_discount_rate,
)
from retrofit_analysis.emissions import emission_intensities
from retrofit_analysis.measures import reference_catalogue
from retrofit_analysis.scenarios import generate_scenarios
from retrofit_analysis.timelines import discounted_difference, expand_timeline


def test_reference_measure_values():
    catalogue = reference_catalogue()
    assert [item.name for item in catalogue.walls] == [
        "W0", "W005", "W010", "W015", "W020", "W025", "W1", "W2"
    ]
    assert [item.thermal_resistance for item in catalogue.roofs] == pytest.approx(
        [1.71, 1.6074, 1.47915, 1.3509, 1.22265, 1.0944, 5.55, 10.04]
    )
    assert [item.u_factor for item in catalogue.windows] == pytest.approx(
        [2.5, 2.625, 2.725, 2.85, 2.975, 3.1, 1.0, 0.7]
    )
    assert catalogue.roof_map["R005"] == pytest.approx(1.6074)
    assert catalogue.floor_map["F005"] == pytest.approx(1.3818)
    assert catalogue.window_u_map["Wi005"] == pytest.approx(2.625)


def test_relative_productivity_reference_output():
    assert calculate_relative_productivity(27) == 1.0


def test_timeline_and_discounted_difference():
    assert expand_timeline([1, 2, 3, 4, 5, 6])[:7] == [1, 1, 1, 1, 1, 2, 2]
    assert discounted_difference([10, 10], [8, 12], [1, 0.5], positive_only=True) == 2.0


def test_reference_market_and_product_factors():
    nominal = market_discount_rate(0.03, 0.039)
    assert nominal == 0.07
    assert adjustment_factors(0.029, nominal, 2) == [1.0, 0.962, 0.925]


def test_npc_baseline_and_first_floor_upgrade():
    scenarios = generate_scenarios()
    factors = adjustment_factors(0.029, 0.07, 30)
    areas = BuildingAreas(windows=551, walls=1453, roof=813.43, floor=841.67)
    values = calculate_npc(scenarios[:2], reference_catalogue(), areas, factors)
    assert values[0] == 0
    assert values[1] == -159_917.3


def test_emission_intensity_reference_sequence():
    assert emission_intensities() == [8.53, 3.1514, 1.0, 1.0, 1.0, 1.0]
