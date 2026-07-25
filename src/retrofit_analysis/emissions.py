from __future__ import annotations

from .economics import BuildingAreas
from .measures import MeasureCatalogue
from .scenarios import Scenario
from .timelines import expand_timeline


def emission_intensities() -> list[float]:
    result = []
    for year in (0, 5, 10, 15, 20, 25):
        intensity = 8.53 + (1.0 - 8.53) * (year / 7) if year <= 7 else 1.0
        result.append(round(intensity, 4))
    return result


def operational_emission_savings(
    district_heating_timelines: list[list[float | None]],
) -> list[float]:
    intensities = emission_intensities()
    emissions = [
        [
            round(value * intensities[index], 2) if value is not None else None
            for index, value in enumerate(scenario)
        ]
        for scenario in district_heating_timelines
    ]
    baseline = expand_timeline(emissions[0], (5, 5, 5, 5, 5, 6))
    totals = []
    for scenario in emissions:
        expanded = expand_timeline(scenario, (5, 5, 5, 5, 5, 6))
        savings = [
            round(base - current, 2)
            if base is not None and current is not None else None
            for base, current in zip(baseline, expanded)
        ]
        # filter(None, ...) deliberately preserves notebook behavior.
        totals.append(round(sum(filter(None, savings)), 2))
    return totals


def embodied_emissions(
    scenarios: list[Scenario],
    catalogue: MeasureCatalogue,
    areas: BuildingAreas,
) -> list[float]:
    measures = {
        item.name: item for item in
        (*catalogue.walls, *catalogue.windows, *catalogue.roofs, *catalogue.floors)
    }
    values = {
        "W0": 0, "Wi0": 0, "R0": 0, "F0": 0, "S0": 0,
        "W1": round(areas.walls * measures["W1"].emissions, 0),
        "W2": round(areas.walls * measures["W2"].emissions, 0),
        "Wi1": round(areas.windows * measures["Wi1"].emissions, 0),
        "Wi2": round(areas.windows * measures["Wi2"].emissions, 0),
        "R1": round(areas.roof * measures["R1"].emissions, 0),
        "R2": round(areas.roof * measures["R2"].emissions, 0),
        "F1": round(areas.floor * measures["F1"].emissions, 0),
        "F2": round(areas.floor * measures["F2"].emissions, 0),
        "S1": round(areas.windows * catalogue.blind_emissions, 0),
    }
    return [
        -sum(values[item] for item in (
            scenario.wall, scenario.window, scenario.roof, scenario.floor,
            scenario.shading,
        ))
        for scenario in scenarios
    ]

