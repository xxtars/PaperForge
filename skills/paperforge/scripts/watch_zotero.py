#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

from common import ensure_workspace, file_signature, load_config, read_json, utc_now, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Watch Zotero sources and trigger incremental sync when they change.")
    parser.add_argument("--config", type=Path, default=Path("paperforge.config.json"))
    parser.add_argument("--interval", type=int, default=30, help="Polling interval in seconds")
    parser.add_argument("--once", action="store_true", help="Check once and exit")
    args = parser.parse_args()

    config = load_config(args.config)
    paths = ensure_workspace(config)
    watch_state_path = paths["state"] / "watch_state.json"
    state = read_json(watch_state_path) if watch_state_path.exists() else {"last_seen": {}}

    while True:
        changed, current = detect_changes(config, state.get("last_seen", {}))
        if changed:
            subprocess.run(
                [
                    "python3",
                    str((Path(__file__).resolve().parent / "sync_zotero.py")),
                    "--config",
                    str(args.config),
                ],
                check=True,
            )
            state["last_seen"] = current
            state["last_run_at"] = utc_now()
            write_json(watch_state_path, state)
            print("Detected Zotero changes and ran sync_zotero.py")
        else:
            print("No Zotero changes detected")

        if args.once:
            return 0
        time.sleep(max(args.interval, 1))


def detect_changes(config: dict, previous: dict) -> tuple[bool, dict]:
    current = {
        "zotero_export_path": file_signature(config["zotero_export_path"]),
        "zotero_storage_path": file_signature(config["zotero_storage_path"]),
    }
    return current != previous, current


if __name__ == "__main__":
    raise SystemExit(main())
