from __future__ import annotations

import argparse
from pathlib import Path

from retrofit_analysis.config import load_config
from retrofit_analysis.workflow import analyze_existing_results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    destination = analyze_existing_results(load_config(args.config), args.limit)
    print(f"Wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

