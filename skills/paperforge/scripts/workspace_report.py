#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_workspace, load_config, load_paper_dirs, read_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Report local workspace status for the research agent.")
    parser.add_argument("--config", type=Path, default=Path("paperforge.config.json"))
    args = parser.parse_args()

    config = load_config(args.config)
    ensure_workspace(config)

    total = 0
    summarized = 0
    pending = 0
    for paper_dir in load_paper_dirs(config):
        total += 1
        memory = read_json(paper_dir / "memory.json")
        if memory.get("status") == "summarized":
            summarized += 1
        else:
            pending += 1

    print(f"Workspace: {config['workspace_dir']}")
    print(f"Total papers: {total}")
    print(f"Summarized: {summarized}")
    print(f"Pending: {pending}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
