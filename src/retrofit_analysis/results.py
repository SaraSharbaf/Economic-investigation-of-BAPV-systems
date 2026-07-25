from __future__ import annotations

import pandas as pd

from .scenarios import Scenario

RESULT_COLUMNS = {
    "district_heating": "DistrictHeating_GJ",
    "heating_discomfort": "Heating_Discomfort_Hours",
    "cooling_discomfort": "Cooling_Discomfort_Hours",
    "total_discomfort": "Total_RP",
}


def map_results_to_scenarios(
    results: pd.DataFrame,
    scenario_names: list[list[str]],
    value_column: str,
) -> tuple[dict[str, float], list[list[float | None]]]:
    values_by_name = results.set_index("File")[value_column].to_dict()
    timelines = [
        [values_by_name.get(name) for name in scenario]
        for scenario in scenario_names
    ]
    return values_by_name, timelines


def assemble_results(
    scenarios: list[Scenario],
    npc: list[float],
    energy_npv: list[float],
    comfort_npv_values: list[float],
    district_heating: list[list[float]],
    discomfort: list[list[float]],
) -> pd.DataFrame:
    frame = pd.DataFrame(
        [scenario.as_list() for scenario in scenarios],
        columns=[
            "Wall_Type", "Window_Type", "Roof_Type", "Floor_Type", "Shading",
            "Wall_Time", "Window_Time", "Roof_Time", "Floor_Time", "Shading_Time",
        ],
    )
    frame["NPC"] = npc
    frame["NPV_Energy_Savings"] = energy_npv
    frame["NPV_of_change_in_comfort"] = comfort_npv_values
    frame["Total NPV"] = (
        frame["NPV_Energy_Savings"] + frame["NPV_of_change_in_comfort"] + frame["NPC"]
    )
    frame["Total NPV without comfort"] = frame["NPV_Energy_Savings"] + frame["NPC"]
    frame["Heating energy savings"] = district_heating
    frame["Total_hours_beyond_OT_with_21_22"] = discomfort
    return frame

