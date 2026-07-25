from __future__ import annotations

import argparse
from pathlib import Path

from retrofit_analysis.config import load_config
from retrofit_analysis.scenarios import generate_scenarios
from retrofit_analysis.workflow import run_simulations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--indices", type=int, nargs="+", default=[0, 1, 2688])
    parser.add_argument("--all", action="store_true", dest="run_all")
    args = parser.parse_args()
    indices = list(range(len(generate_scenarios()))) if args.run_all else args.indices
    results = run_simulations(load_config(args.config), indices)
    failed = [result for result in results if result["returncode"] != 0]
    print(f"Completed {len(results)} unique EnergyPlus cases; failures: {len(failed)}")
    for result in failed:
        print(f'{result["case"]}: {result["stderr"]}')
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

