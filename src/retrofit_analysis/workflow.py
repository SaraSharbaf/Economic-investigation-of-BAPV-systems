from __future__ import annotations

from .config import ProjectConfig
from .energyplus.model import EnergyPlusModelBuilder
from .energyplus.runner import EnergyPlusRunner
from .measures import reference_catalogue
from .scenarios import generate_scenarios


def simulation_cases_for_scenario(index: int) -> list[tuple[str, str, str, str, int]]:
    scenario = generate_scenarios()[index]
    cases = []
    for identifier in scenario.checkpoint_identifiers():
        wall, window, roof, floor, shading = identifier.split("_")
        cases.append((wall, window, roof, floor, int(shading[1:])))
    return cases


def run_simulations(
    config: ProjectConfig, scenario_indices: list[int]
) -> list[dict]:
    catalogue = reference_catalogue()
    builder = EnergyPlusModelBuilder(
        config.paths.base_model, catalogue, config.energyplus
    )
    runner = EnergyPlusRunner(
        config.paths.energyplus_executable,
        config.paths.weather_file,
        config.paths.simulation_output_dir,
    )
    unique_cases = []
    seen = set()
    for index in scenario_indices:
        for case in simulation_cases_for_scenario(index):
            if case not in seen:
                unique_cases.append(case)
                seen.add(case)
    results = []
    for wall, window, roof, floor, shading in unique_cases:
        if shading == 1 and window.startswith("Wi0"):
            continue
        filename = builder.filename(wall, window, roof, floor, shading)
        model_path = config.paths.simulation_output_dir / filename
        builder.write(builder.build(wall, window, roof, floor, shading), model_path)
        result = runner.run(model_path, filename.replace(".epJSON", ""))
        results.append(
            {"case": filename, "returncode": result.returncode, "stderr": result.stderr}
        )
    return results


def analyze_existing_results(
    config: ProjectConfig, limit: int | None = None
) -> "Path":
    from pathlib import Path
    from .energyplus.parsers import parse_results_directory

    config.paths.tables_dir.mkdir(parents=True, exist_ok=True)
    frame = parse_results_directory(config.paths.existing_results_dir, limit=limit)
    destination = config.paths.tables_dir / "results_df.xlsx"
    frame.to_excel(destination, index=False)
    return destination
