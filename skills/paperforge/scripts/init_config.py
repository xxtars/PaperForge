#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a local paperforge.config.json from the bundled skill template.")
    parser.add_argument("--output", type=Path, default=Path("paperforge.config.json"))
    parser.add_argument("--force", action="store_true", help="Overwrite the output file if it already exists.")
    args = parser.parse_args()

    template_path = Path(__file__).resolve().parent.parent / "assets" / "paperforge.config.example.json"
    output_path = args.output.expanduser().resolve()

    if output_path.exists() and not args.force:
        raise SystemExit(f"{output_path} already exists. Use --force to overwrite it.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template_path, output_path)
    print(f"Wrote config template to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
