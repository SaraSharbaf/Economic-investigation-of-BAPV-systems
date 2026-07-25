from __future__ import annotations

from dataclasses import dataclass
from itertools import product

TIMES = ("Now", "5_years", "10_years", "15_years", "20_years", "25_years")
TIME_ORDER = {value: index for index, value in enumerate(TIMES)}


@dataclass(frozen=True)
class Scenario:
    wall: str
    window: str
    roof: str
    floor: str
    shading: str
    wall_time: str
    window_time: str
    roof_time: str
    floor_time: str
    shading_time: str

    def as_list(self) -> list[str]:
        return [
            self.wall, self.window, self.roof, self.floor, self.shading,
            self.wall_time, self.window_time, self.roof_time, self.floor_time,
            self.shading_time,
        ]

    def checkpoint_identifiers(self) -> list[str]:
        identifiers: list[str] = []
        choices = (self.wall, self.window, self.roof, self.floor, self.shading)
        upgrade_times = (
            self.wall_time, self.window_time, self.roof_time, self.floor_time,
            self.shading_time,
        )
        prefixes = ("W", "Wi", "R", "F", "S")
        for index, _time in enumerate(TIMES):
            year = index * 5
            suffix = f"{year:02}" if year > 0 else ""
            components = []
            for choice, upgrade_time, prefix in zip(
                choices, upgrade_times, prefixes
            ):
                if upgrade_time != "CC" and index >= TIMES.index(upgrade_time):
                    value = choice
                elif prefix == "S":
                    value = "S0"
                else:
                    value = f"{prefix}0{suffix}"
                components.append(value)
            identifiers.append("_".join(components))
        return identifiers


def generate_scenarios() -> list[Scenario]:
    scenarios: list[Scenario] = []
    for wall, window, roof, floor, shading in product(
        ("W0", "W1", "W2"),
        ("Wi0", "Wi1", "Wi2"),
        ("R0", "R1", "R2"),
        ("F0", "F1", "F2"),
        ("S0", "S1"),
    ):
        if (wall == "W0" and window != "Wi0") or (
            wall != "W0" and window == "Wi0"
        ):
            continue
        valid_times = [
            ("CC",) if value.endswith("0") else TIMES
            for value in (wall, window, roof, floor, shading)
        ]
        for wall_time, window_time, roof_time, floor_time, shading_time in product(
            *valid_times
        ):
            if wall != "W0" and window != "Wi0" and wall_time != window_time:
                continue
            if shading == "S1":
                if window == "Wi0":
                    continue
                if TIME_ORDER[shading_time] < TIME_ORDER[window_time]:
                    continue
            scenarios.append(
                Scenario(
                    wall, window, roof, floor, shading, wall_time, window_time,
                    roof_time, floor_time, shading_time,
                )
            )
    return scenarios

