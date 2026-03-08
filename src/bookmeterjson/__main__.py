# SPDX-License-Identifier: MIT

import argparse
import sys

from .config import load_config
from .scraper import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bookmeter.com scraper with JSON output"
    )
    parser.add_argument(
        "--config",
        "-c",
        default="configs.yaml",
        help="Path to config file (default: configs.yaml)",
    )
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    run(config)


if __name__ == "__main__":
    main()
