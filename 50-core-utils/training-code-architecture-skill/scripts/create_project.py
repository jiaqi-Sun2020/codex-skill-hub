from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"


def copytree(src: Path, dst: Path, force: bool) -> None:
    if dst.exists():
        if not force:
            raise FileExistsError(f"Output already exists: {dst}. Use --force to overwrite.")
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an architecture-first training project")
    parser.add_argument("--output", required=True, help="Output project directory")
    parser.add_argument("--force", action="store_true", help="Overwrite output directory")
    args = parser.parse_args()

    output = Path(args.output).resolve()
    copytree(TEMPLATES, output, force=args.force)
    print(f"Created project at: {output}")
    print("Run:")
    print(f"  cd {output}")
    print("  python main.py --config config.json")


if __name__ == "__main__":
    main()
