from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from ..config import EnergyPlusConfig
from ..measures import MeasureCatalogue


class EnergyPlusModelBuilder:
    def __init__(
        self,
        base_model_path: Path,
        catalogue: MeasureCatalogue,
        config: EnergyPlusConfig,
    ) -> None:
        with Path(base_model_path).open(encoding="utf-8") as stream:
            self._base_model = json.load(stream)
        self.catalogue = catalogue
        self.config = config

    def build(
        self, wall: str, window: str, roof: str, floor: str, shading: int
    ) -> dict:
        model = deepcopy(self._base_model)
        if window != "Wi0":
            glazing = model["WindowMaterial:SimpleGlazingSystem"]["Window before"]
            glazing["u_factor"] = self.catalogue.window_u_map[window]
            glazing["solar_heat_gain_coefficient"] = (
                self.catalogue.window_shgc_map[window]
            )
        if wall != "W0":
            model["Material:NoMass"]["Exterior wall no mass"][
                "thermal_resistance"
            ] = self.catalogue.wall_map[wall]
        if roof != "R0":
            model["Material:NoMass"]["Exterior roof no mass"][
                "thermal_resistance"
            ] = self.catalogue.roof_map[roof]
        if floor != "F0":
            model["Material:NoMass"]["Exterior floor no mass"][
                "thermal_resistance"
            ] = self.catalogue.floor_map[floor]
        setpoint = (
            self.config.no_shading_setpoint
            if shading == 0 else self.config.shading_setpoint
        )
        for zone in range(1, self.config.zones + 1):
            for blind in range(1, self.config.blinds_per_zone + 1):
                name = f"Zone{zone}_BlindControl-{blind}"
                model["WindowShadingControl"][name]["setpoint"] = setpoint
        return model

    @staticmethod
    def filename(wall: str, window: str, roof: str, floor: str, shading: int) -> str:
        return f"{wall}_{window}_{roof}_{floor}_S{shading}.epJSON"

    @staticmethod
    def write(model: dict, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as stream:
            json.dump(model, stream, indent=4)

