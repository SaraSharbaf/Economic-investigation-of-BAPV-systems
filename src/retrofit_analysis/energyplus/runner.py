from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class SimulationResult:
    prefix: str
    returncode: int
    stdout: str
    stderr: str


class EnergyPlusRunner:
    def __init__(self, executable: Path, weather_file: Path, output_dir: Path) -> None:
        self.executable = Path(executable)
        self.weather_file = Path(weather_file)
        self.output_dir = Path(output_dir)

    def run(self, model_path: Path, prefix: str) -> SimulationResult:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        command = [
            str(self.executable),
            "--output-prefix", prefix,
            "--readvars",
            "--output-directory", str(self.output_dir),
            "--weather", str(self.weather_file),
            str(model_path),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        return SimulationResult(
            prefix, completed.returncode, completed.stdout, completed.stderr
        )

