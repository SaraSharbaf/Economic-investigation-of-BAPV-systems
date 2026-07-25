import json

from retrofit_analysis.config import EnergyPlusConfig
from retrofit_analysis.energyplus.model import EnergyPlusModelBuilder
from retrofit_analysis.measures import reference_catalogue


def test_exact_energyplus_object_modifications(tmp_path):
    model = {
        "WindowMaterial:SimpleGlazingSystem": {
            "Window before": {"u_factor": 2.5, "solar_heat_gain_coefficient": 0.65}
        },
        "Material:NoMass": {
            "Exterior wall no mass": {"thermal_resistance": 1.36},
            "Exterior roof no mass": {"thermal_resistance": 1.71},
            "Exterior floor no mass": {"thermal_resistance": 1.41},
        },
        "WindowShadingControl": {
            f"Zone{zone}_BlindControl-{blind}": {"setpoint": 60}
            for zone in range(1, 6) for blind in range(1, 5)
        },
    }
    path = tmp_path / "base.epJSON"
    path.write_text(json.dumps(model), encoding="utf-8")
    builder = EnergyPlusModelBuilder(path, reference_catalogue(), EnergyPlusConfig())
    upgraded = builder.build("W2", "Wi2", "R2", "F2", 1)
    assert upgraded["WindowMaterial:SimpleGlazingSystem"]["Window before"] == {
        "u_factor": 0.7, "solar_heat_gain_coefficient": 0.6
    }
    assert upgraded["Material:NoMass"]["Exterior wall no mass"]["thermal_resistance"] == 4.9
    assert upgraded["Material:NoMass"]["Exterior roof no mass"]["thermal_resistance"] == 10.04
    assert upgraded["Material:NoMass"]["Exterior floor no mass"]["thermal_resistance"] == 6.25
    assert all(
        value["setpoint"] == 23
        for value in upgraded["WindowShadingControl"].values()
    )
    assert builder.filename("W2", "Wi2", "R2", "F2", 1) == "W2_Wi2_R2_F2_S1.epJSON"

