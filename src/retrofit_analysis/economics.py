from __future__ import annotations

from dataclasses import dataclass

from .config import AnalysisConfig
from .measures import MeasureCatalogue
from .scenarios import Scenario
from .timelines import discounted_difference, expand_timeline

TIME_TO_INDEX = {
    "Now": 0, "5_years": 1, "10_years": 2, "15_years": 3,
    "20_years": 4, "25_years": 5,
}


def market_discount_rate(real_rate: float, inflation_rate: float) -> float:
    return round((1 + real_rate) * (1 + inflation_rate) - 1, 3)


def adjustment_factors(
    inflation_rate: float, nominal_discount_rate: float, years: int
) -> list[float]:
    return [
        round(abs(((1 + inflation_rate) / (1 + nominal_discount_rate)) ** year), 3)
        for year in range(years + 1)
    ]


def energy_savings_npv(
    checkpoint_timelines: list[list[float]],
    factors: list[float],
    study_period: int,
    gj_to_kwh: float,
    district_heating_price: float,
) -> list[float]:
    intervals = (5, 5, 5, 5, 5, 6)
    baseline = expand_timeline(checkpoint_timelines[0], intervals)[:study_period]
    return [
        discounted_difference(
            baseline,
            expand_timeline(values, intervals)[:study_period],
            factors[:study_period],
            value_multiplier=gj_to_kwh * district_heating_price,
            positive_only=True,
        )
        for values in checkpoint_timelines
    ]


@dataclass(frozen=True)
class BuildingAreas:
    windows: float
    walls: float
    roof: float
    floor: float


def calculate_npc(
    scenarios: list[Scenario],
    catalogue: MeasureCatalogue,
    areas: BuildingAreas,
    product_factors: list[float],
) -> list[float]:
    costs = {
        item.name: item.cost
        for item in (*catalogue.walls, *catalogue.windows, *catalogue.roofs, *catalogue.floors)
    }
    results = []
    for scenario in scenarios:
        total = 0.0
        items = (
            (scenario.wall, scenario.wall_time, areas.walls),
            (scenario.window, scenario.window_time, areas.windows),
            (scenario.roof, scenario.roof_time, areas.roof),
            (scenario.floor, scenario.floor_time, areas.floor),
        )
        for component, time, area in items:
            if time != "CC":
                total += (
                    costs.get(component, 0)
                    * area
                    * product_factors[TIME_TO_INDEX[time]]
                    * -1
                )
        if scenario.shading == "S1" and scenario.shading_time != "CC":
            total += (
                catalogue.blind_cost
                * areas.windows
                * product_factors[TIME_TO_INDEX[scenario.shading_time]]
                * -1
            )
        results.append(round(total, 2))
    return results


def reference_economic_factors(config: AnalysisConfig) -> tuple[list[float], list[float]]:
    nominal = market_discount_rate(
        config.real_discount_rate, config.general_price_inflation_rate
    )
    dh = adjustment_factors(
        config.district_heating_price_inflation_rate, nominal, config.study_period
    )
    products = adjustment_factors(
        config.products_price_inflation_rate, nominal, config.study_period
    )
    return dh, products

