import json
from pathlib import Path


def test_versioned_reference_cases_are_complete():
    path = Path(__file__).parent / "reference" / "representative_cases.json"
    reference = json.loads(path.read_text(encoding="utf-8"))
    assert reference["energyplus_version"] == "24.2.0"
    assert set(reference["cases"]) == {
        "W005_Wi005_R005_F005_S0",
        "W005_Wi005_R1_F1_S0",
        "W2_Wi2_R2_F2_S0",
    }
    required = {
        "EnergyPerHeatedArea_MJ_per_m2",
        "DistrictHeating_GJ",
        "CoolingElectricity_GJ",
        "PumpsElectricity_GJ",
        "Total_RP",
        "Heating_Discomfort_Hours",
        "Cooling_Discomfort_Hours",
    }
    assert all(set(values) == required for values in reference["cases"].values())

