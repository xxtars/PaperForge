#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_workspace, load_config, read_json, utc_now, write_json


REQUIRED_FIELDS = [
    "status",
    "summary_short",
    "problem",
    "contributions",
    "limitations",
    "idea_hooks",
    "updated_by",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist executor-generated paper memory into the local workspace.")
    parser.add_argument("--config", type=Path, default=Path("paperforge.config.json"))
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--input", type=Path, required=True, help="Path to a JSON file following references/schemas.md")
    args = parser.parse_args()

    config = load_config(args.config)
    paths = ensure_workspace(config)
    paper_dir = paths["papers"] / args.paper_id
    if not paper_dir.exists():
        raise SystemExit(f"Unknown paper_id: {args.paper_id}")

    payload = read_json(args.input)
    validate_payload(payload)
    payload["updated_at"] = payload.get("updated_at") or utc_now()
    write_json(paper_dir / "memory.json", payload)
    pending = refresh_pending_queue(paths["papers"], paths["index"] / "pending_summaries.json")
    print(f"Saved memory for {args.paper_id}")
    print(f"{pending} papers are still waiting for AI summary")
    return 0


def validate_payload(payload: dict) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise SystemExit(f"Missing required fields: {', '.join(missing)}")
    list_fields = ["contributions", "limitations", "idea_hooks"]
    for field in list_fields:
        if not isinstance(payload.get(field), list):
            raise SystemExit(f"Field '{field}' must be a JSON list")
    if payload.get("status") not in {"pending", "summarized", "needs_review"}:
        raise SystemExit("Field 'status' must be one of: pending, summarized, needs_review")


def refresh_pending_queue(papers_dir: Path, output_path: Path) -> int:
    pending_items = []
    for paper_dir in sorted(path for path in papers_dir.iterdir() if path.is_dir()):
        source = read_json(paper_dir / "source.json")
        memory = read_json(paper_dir / "memory.json")
        if memory.get("status") != "summarized":
            pending_items.append(
                {
                    "paper_id": source["paper_id"],
                    "title": source["title"],
                    "pdf_path": source.get("pdf_path"),
                    "paper_dir": str(paper_dir.resolve()),
                }
            )
    write_json(output_path, pending_items)
    return len(pending_items)


if __name__ == "__main__":
    raise SystemExit(main())
