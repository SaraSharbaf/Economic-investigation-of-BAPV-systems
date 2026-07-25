from __future__ import annotations

YEARS_PER_INTERVAL = (5, 5, 5, 5, 5, 5)


def expand_timeline(
    values: list[float] | tuple[float, ...],
    interval_lengths: tuple[int, ...] = YEARS_PER_INTERVAL,
) -> list[float]:
    if len(values) != len(interval_lengths):
        raise ValueError(
            f"Expected {len(interval_lengths)} checkpoint values, got {len(values)}"
        )
    return [
        value
        for value, interval_length in zip(values, interval_lengths)
        for _ in range(interval_length)
    ]


def discounted_difference(
    baseline: list[float],
    scenario: list[float],
    adjustment_factors: list[float],
    value_multiplier: float = 1.0,
    positive_only: bool = False,
) -> float:
    if not (len(baseline) == len(scenario) == len(adjustment_factors)):
        raise ValueError("Annual timelines and adjustment factors must have equal lengths")
    total = 0.0
    for base_value, scenario_value, factor in zip(
        baseline, scenario, adjustment_factors
    ):
        difference = base_value - scenario_value
        if positive_only and difference <= 0:
            continue
        total += difference * value_multiplier * factor
    return round(total, 2)

