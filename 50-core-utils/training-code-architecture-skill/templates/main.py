from __future__ import annotations

import argparse

from src.utils.config import load_config
from src.utils.seed import set_seed
from train import train


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Architecture-first training entrypoint")
    parser.add_argument("--config", type=str, default="config.json", help="Path to a JSON config file")
    return parser.parse_args()


def main() -> None:
    cli_args = parse_args()
    args = load_config(cli_args.config)
    args.config_path = cli_args.config
    set_seed(args.experiment.seed)
    train(args)


if __name__ == "__main__":
    main()
