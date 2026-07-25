from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OpaqueMeasure:
    name: str
    cost: float
    thermal_resistance: float
    service_life: int
    emissions: float


@dataclass(frozen=True)
class WindowMeasure:
    name: str
    cost: float
    u_factor: float
    shgc: float
    service_life: int
    emissions: float


@dataclass(frozen=True)
class MeasureCatalogue:
    walls: tuple[OpaqueMeasure, ...]
    roofs: tuple[OpaqueMeasure, ...]
    floors: tuple[OpaqueMeasure, ...]
    windows: tuple[WindowMeasure, ...]
    blind_cost: float = 2000.0
    blind_emissions: float = 8.75

    @property
    def wall_map(self) -> dict[str, float]:
        return {item.name: item.thermal_resistance for item in self.walls}

    @property
    def roof_map(self) -> dict[str, float]:
        return {item.name: item.thermal_resistance for item in self.roofs}

    @property
    def floor_map(self) -> dict[str, float]:
        return {item.name: item.thermal_resistance for item in self.floors}

    @property
    def window_u_map(self) -> dict[str, float]:
        return {item.name: item.u_factor for item in self.windows}

    @property
    def window_shgc_map(self) -> dict[str, float]:
        return {item.name: item.shgc for item in self.windows}


def _opaque_series(
    prefix: str,
    baseline_r: float,
    rate: float,
    option_1: tuple[float, float, int, float],
    option_2: tuple[float, float, int, float],
) -> tuple[OpaqueMeasure, ...]:
    values = [OpaqueMeasure(f"{prefix}0", 0, baseline_r, 0, 0)]
    for year, multiplier in zip((5, 10, 15, 20, 25), (4, 9, 14, 19, 24)):
        values.append(
            OpaqueMeasure(
                f"{prefix}0{year:02}",
                0,
                baseline_r - baseline_r * rate * multiplier,
                0,
                0,
            )
        )
    values.extend(
        (
            OpaqueMeasure(f"{prefix}1", *option_1),
            OpaqueMeasure(f"{prefix}2", *option_2),
        )
    )
    return tuple(values)


def reference_catalogue() -> MeasureCatalogue:
    walls = _opaque_series(
        "W", 1.36, 0.005, (292, 1.88, 60, 3.1), (878, 4.90, 60, 9.03)
    )
    roofs = _opaque_series(
        "R", 1.71, 0.015, (393, 5.55, 60, 17), (981, 10.04, 60, 42.5)
    )
    floors = _opaque_series(
        "F", 1.41, 0.005, (190, 4.54, 60, 11.5), (380, 6.25, 60, 23)
    )
    baseline_u = 2.5
    windows = [WindowMeasure("Wi0", 0, baseline_u, 0.65, 0, 0)]
    for year, multiplier in zip((5, 10, 15, 20, 25), (5, 9, 14, 19, 24)):
        windows.append(
            WindowMeasure(
                f"Wi0{year:02}",
                0,
                baseline_u + baseline_u * 0.01 * multiplier,
                0.65,
                0,
                0,
            )
        )
    windows.extend(
        (
            WindowMeasure("Wi1", 3649, 1.0, 0.6, 30, 105.8),
            WindowMeasure("Wi2", 4364, 0.7, 0.6, 50, 221.81),
        )
    )
    return MeasureCatalogue(walls, roofs, floors, tuple(windows))

