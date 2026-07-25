from __future__ import annotations

from .timelines import discounted_difference, expand_timeline


def calculate_relative_productivity(temperature):
    """Notebook RP polynomial; works with scalars and pandas Series."""
    return round(
        0.1647524 * temperature
        - 0.0058274 * temperature**2
        + 0.0000623 * temperature**3
        - 0.4685328,
        1,
    )


def wage_adjustment_factors(
    study_period: int, wage_inflation_rate: float, real_discount_rate: float
) -> list[float]:
    return [
        round(
            ((1 + wage_inflation_rate) / (1 + real_discount_rate)) ** year,
            4,
        )
        for year in range(study_period + 1)
    ]


def comfort_npv(
    checkpoint_timelines: list[list[float]],
    hourly_wage: float,
    number_of_employees: float,
    study_period: int,
    wage_factors: list[float],
) -> list[float]:
    baseline = expand_timeline(checkpoint_timelines[0])
    return [
        discounted_difference(
            baseline,
            expand_timeline(scenario),
            wage_factors[:study_period],
            value_multiplier=hourly_wage * number_of_employees,
        )
        for scenario in checkpoint_timelines
    ]

