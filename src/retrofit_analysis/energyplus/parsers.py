from __future__ import annotations

from pathlib import Path

from natsort import natsorted
import pandas as pd

from ..comfort import calculate_relative_productivity

EXTRACTION_POINTS = ((0, 1, 3), (3, 1, 12), (3, 2, 1), (3, 8, 1))
COLUMN_NAMES = (
    "EnergyPerHeatedArea_MJ_per_m2",
    "DistrictHeating_GJ",
    "CoolingElectricity_GJ",
    "PumpsElectricity_GJ",
)


def extract_values_from_html(
    html_file: Path,
    points=EXTRACTION_POINTS,
    column_names=COLUMN_NAMES,
) -> dict[str, float | None]:
    tables = pd.read_html(html_file)
    extracted = {}
    for name, (table_index, row_index, column_index) in zip(column_names, points):
        try:
            extracted[name] = float(tables[table_index].iloc[row_index, column_index])
        except Exception:
            extracted[name] = None
    return extracted


def extract_base_value_from_html(html_file: Path, point: tuple[int, int, int]) -> float:
    table_index, row_index, column_index = point
    return float(pd.read_html(html_file)[table_index].iloc[row_index, column_index])


def extract_areas(eio_file_path: Path) -> tuple[float, float]:
    total_windows = 0.0
    total_walls = 0.0
    with Path(eio_file_path).open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if line.startswith(" Zone Information"):
                parts = line.split(",")
                if len(parts) > 25:
                    total_walls += float(parts[24].strip())
                    total_windows += float(parts[25].strip())
    return total_windows, total_walls


def parse_result_pair(html_path: Path, csv_path: Path | None) -> dict:
    result = {"File": html_path.name.replace("tbl.htm", "").replace("tbl.html", "")}
    result.update(extract_values_from_html(html_path))
    if csv_path is None:
        result.update(
            Total_RP=None,
            Heating_Discomfort_Hours=None,
            Cooling_Discomfort_Hours=None,
        )
        return result
    frame = pd.read_csv(csv_path)
    frame[frame.columns[0]] = pd.to_datetime(
        frame[frame.columns[0]], format=" %m/%d  %H:%M:%S", errors="coerce"
    )
    frame = frame.dropna(subset=[frame.columns[0]])
    frame = frame[frame.iloc[:, 1] > 0]
    frame = frame[
        (frame[frame.columns[0]].dt.hour >= 8)
        & (frame[frame.columns[0]].dt.hour < 16)
    ]
    rp_6 = round((1 - calculate_relative_productivity(frame.iloc[:, 6])).sum(), 1)
    rp_8 = round((1 - calculate_relative_productivity(frame.iloc[:, 8])).sum() * 3, 1)
    rp_10 = round((1 - calculate_relative_productivity(frame.iloc[:, 10])).sum(), 1)
    result["Total_RP"] = round(rp_6 + rp_8 + rp_10, 1)
    result["Heating_Discomfort_Hours"] = (
        (frame.iloc[:, 39] < -1).sum()
        + 3 * (frame.iloc[:, 40] < -1).sum()
        + (frame.iloc[:, 43] < -1).sum()
    )
    result["Cooling_Discomfort_Hours"] = (
        (frame.iloc[:, 39] > 1).sum()
        + 3 * (frame.iloc[:, 40] > 1).sum()
        + (frame.iloc[:, 43] > 1).sum()
    )
    return result


def parse_results_directory(directory: Path, limit: int | None = None) -> pd.DataFrame:
    directory = Path(directory)
    html_files = natsorted(
        path for path in directory.iterdir()
        if path.suffix.lower() in {".htm", ".html"}
    )
    if limit is not None:
        html_files = html_files[:limit]
    all_files = list(directory.iterdir())
    rows = []
    for html_path in html_files:
        base_name = html_path.name.replace("tbl.html", "").replace("tbl.htm", "")
        matching = next(
            (
                path for path in all_files
                if path.name.startswith(base_name) and path.name.endswith("out.csv")
            ),
            None,
        )
        rows.append(parse_result_pair(html_path, matching))
    return pd.DataFrame(rows)

