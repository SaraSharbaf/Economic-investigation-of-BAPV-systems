from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
from pathlib import Path

from lxml import html

from retrofit_analysis.comfort import calculate_relative_productivity
from retrofit_analysis.config import load_config
from retrofit_analysis.energyplus.model import EnergyPlusModelBuilder
from retrofit_analysis.energyplus.runner import EnergyPlusRunner
from retrofit_analysis.measures import reference_catalogue

CASES = (
    ("W005", "Wi005", "R005", "F005", 0),
    ("W005", "Wi005", "R1", "F1", 0),
    ("W2", "Wi2", "R2", "F2", 0),
)


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def html_metrics(path: Path) -> tuple[float, float, float, float]:
    """Extract the four notebook-defined values from raw EnergyPlus tables."""
    document = html.parse(str(path))
    tables = document.xpath("//table")
    points = ((0, 1, 3), (3, 1, 12), (3, 2, 1), (3, 8, 1))
    values = []
    for table_index, row_index, column_index in points:
        rows = tables[table_index].xpath(".//tr")
        cells = rows[row_index].xpath("./th|./td")
        values.append(float("".join(cells[column_index].itertext()).strip()))
    return tuple(values)


def csv_metrics(path: Path) -> tuple[float, int, int]:
    total_rp_6 = total_rp_8 = total_rp_10 = 0.0
    heating = cooling = 0
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.reader(stream)
        next(reader)
        for row in reader:
            try:
                timestamp = datetime.strptime(row[0], " %m/%d  %H:%M:%S")
            except ValueError:
                continue
            if float(row[1]) <= 0 or not 8 <= timestamp.hour < 16:
                continue
            total_rp_6 += 1 - calculate_relative_productivity(float(row[6]))
            total_rp_8 += 1 - calculate_relative_productivity(float(row[8]))
            total_rp_10 += 1 - calculate_relative_productivity(float(row[10]))
            pmv = (float(row[39]), float(row[40]), float(row[43]))
            heating += int(pmv[0] < -1) + 3 * int(pmv[1] < -1) + int(pmv[2] < -1)
            cooling += int(pmv[0] > 1) + 3 * int(pmv[1] > 1) + int(pmv[2] > 1)
    total_rp = round(round(total_rp_6, 1) + round(total_rp_8, 1) * 3 + round(total_rp_10, 1), 1)
    return total_rp, heating, cooling


def close_tuple(left: tuple, right: tuple, tolerance: float = 1e-6) -> bool:
    return len(left) == len(right) and all(
        abs(float(a) - float(b)) <= tolerance for a, b in zip(left, right)
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run three representative cases and compare raw EnergyPlus outputs."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--reuse", action="store_true",
        help="Compare already generated validation outputs without rerunning EnergyPlus.",
    )
    args = parser.parse_args()
    config = load_config(args.config)
    catalogue = reference_catalogue()
    builder = EnergyPlusModelBuilder(
        config.paths.base_model, catalogue, config.energyplus
    )
    validation_dir = config.paths.simulation_output_dir / "validation"
    runner = EnergyPlusRunner(
        config.paths.energyplus_executable, config.paths.weather_file, validation_dir
    )
    failures = 0
    for wall, window, roof, floor, shading in CASES:
        filename = builder.filename(wall, window, roof, floor, shading)
        prefix = filename.replace(".epJSON", "")
        model_path = validation_dir / filename
        builder.write(builder.build(wall, window, roof, floor, shading), model_path)
        if not args.reuse:
            result = runner.run(model_path, prefix)
            if result.returncode:
                failures += 1
                print(f"{prefix}: simulation failed: {result.stderr}")
                continue
        generated_csv = validation_dir / f"{prefix}out.csv"
        generated_html = validation_dir / f"{prefix}tbl.htm"
        reference_csv = config.paths.existing_results_dir / f"{prefix}out.csv"
        reference_html = config.paths.existing_results_dir / f"{prefix}tbl.htm"
        if not reference_csv.exists() or not reference_html.exists():
            failures += 1
            print(f"{prefix}: reference output missing")
            continue
        generated_html_values = html_metrics(generated_html)
        reference_html_values = html_metrics(reference_html)
        generated_comfort = csv_metrics(generated_csv)
        reference_comfort = csv_metrics(reference_csv)
        html_ok = close_tuple(generated_html_values, reference_html_values)
        comfort_ok = generated_comfort == reference_comfort
        if not (html_ok and comfort_ok):
            failures += 1
        print(
            f"{prefix}: "
            f"csv_bytes={'exact' if digest(generated_csv) == digest(reference_csv) else 'different'}, "
            f"html_metrics={'match' if html_ok else 'DIFFER'}, "
            f"comfort_metrics={'match' if comfort_ok else 'DIFFER'}"
        )
        if not html_ok:
            print(f"  generated HTML: {generated_html_values}")
            print(f"  reference HTML: {reference_html_values}")
        if not comfort_ok:
            print(f"  generated comfort: {generated_comfort}")
            print(f"  reference comfort: {reference_comfort}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
