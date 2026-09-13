from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run multiple training configs")
    parser.add_argument("configs", nargs="+", help="Config paths or directories containing config.json files")
    parser.add_argument("--continue-on-error", action="store_true")
    return parser.parse_args()


def expand_configs(items: list[str]) -> list[Path]:
    paths: list[Path] = []
    for item in items:
        path = Path(item)
        if path.is_dir():
            paths.extend(sorted(path.glob("*.json")))
        else:
            paths.append(path)
    return paths


def main() -> None:
    args = parse_args()
    for config_path in expand_configs(args.configs):
        print(f"Running config: {config_path}")
        result = subprocess.run([sys.executable, "main.py", "--config", str(config_path)])
        if result.returncode != 0 and not args.continue_on_error:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
