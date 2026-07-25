from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class PathsConfig:
    energyplus_install_dir: Path
    weather_file: Path
    base_model: Path
    simulation_output_dir: Path
    existing_results_dir: Path
    tables_dir: Path
    figures_dir: Path

    @property
    def energyplus_executable(self) -> Path:
        windows = self.energyplus_install_dir / "EnergyPlus.exe"
        return windows if windows.exists() else self.energyplus_install_dir / "energyplus"


@dataclass(frozen=True)
class AnalysisConfig:
    base_year: int = 2025
    study_period: int = 30
    general_price_inflation_rate: float = 0.039
    electricity_price_inflation_rate: float = 0.025
    district_heating_price_inflation_rate: float = 0.05
    products_price_inflation_rate: float = 0.029
    real_discount_rate: float = 0.03
    basic_electricity_price_nok_per_kwh: float = 1.0
    district_heating_price_nok_per_kwh: float = 1.0
    gj_to_kwh: float = 277.778
    hourly_wage_nok: float = 200.0
    wage_inflation_rate: float = 0.025
    heated_area_m2: float = 3706.0
    floor_area_m2: float = 841.67
    roof_area_m2: float = 813.43


@dataclass(frozen=True)
class EnergyPlusConfig:
    shading_setpoint: float = 23.0
    no_shading_setpoint: float = 60.0
    zones: int = 5
    blinds_per_zone: int = 4


@dataclass(frozen=True)
class ProjectConfig:
    paths: PathsConfig
    analysis: AnalysisConfig
    energyplus: EnergyPlusConfig


def _resolve(value: str, config_dir: Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else (config_dir / path).resolve()


def load_config(path: str | Path) -> ProjectConfig:
    config_path = Path(path).resolve()
    with config_path.open("rb") as stream:
        raw = tomllib.load(stream)
    paths = raw["paths"]
    return ProjectConfig(
        paths=PathsConfig(
            **{key: _resolve(value, config_path.parent) for key, value in paths.items()}
        ),
        analysis=AnalysisConfig(**raw.get("analysis", {})),
        energyplus=EnergyPlusConfig(**raw.get("energyplus", {})),
    )

