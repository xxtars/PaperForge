#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_workspace, load_config, read_json, slugify, utc_now, write_json


REQUIRED_FIELDS = [
    "status",
    "query",
    "resolved_title",
    "zotero_imported",
    "external_actions",
    "updated_by",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist the outcome of an executor-driven paper acquisition task.")
    parser.add_argument("--config", type=Path, default=Path("paperforge.config.json"))
    parser.add_argument("--input", type=Path, required=True, help="Acquisition result JSON")
    args = parser.parse_args()

    config = load_config(args.config)
    paths = ensure_workspace(config)
    payload = read_json(args.input)
    validate_payload(payload)
    payload["updated_at"] = payload.get("updated_at") or utc_now()

    query = payload.get("query", {})
    slug = slugify(query.get("title") or query.get("doi") or query.get("url") or "acquisition")[:80]
    output_path = paths["acquisition"] / "results" / f"{slug}.json"
    write_json(output_path, payload)
    print(f"Saved acquisition result to {output_path}")
    return 0


def validate_payload(payload: dict) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise SystemExit(f"Missing required fields: {', '.join(missing)}")
    if payload.get("status") not in {"completed", "partial", "failed"}:
        raise SystemExit("Field 'status' must be one of: completed, partial, failed")
    if not isinstance(payload.get("external_actions"), list):
        raise SystemExit("Field 'external_actions' must be a JSON list")


if __name__ == "__main__":
    raise SystemExit(main())
