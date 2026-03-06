#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_workspace, load_config, read_json, utc_now, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an executor-facing summary task for one paper.")
    parser.add_argument("--config", type=Path, default=Path("paperforge.config.json"))
    parser.add_argument("--paper-id", required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    paths = ensure_workspace(config)
    paper_dir = paths["papers"] / args.paper_id
    if not paper_dir.exists():
        raise SystemExit(f"Unknown paper_id: {args.paper_id}")

    source_path = paper_dir / "source.json"
    memory_path = paper_dir / "memory.json"
    source = read_json(source_path)
    memory = read_json(memory_path)

    task_payload = {
        "task_type": "paper_summary",
        "paper_id": args.paper_id,
        "library_name": config["library_name"],
        "source_path": str(source_path.resolve()),
        "memory_path": str(memory_path.resolve()),
        "pdf_path": source.get("pdf_path"),
        "current_status": memory.get("status"),
        "summary_prompt_path": str((Path(__file__).resolve().parent.parent / "references" / "summary_prompt.md").resolve()),
        "schema_reference_path": str((Path(__file__).resolve().parent.parent / "references" / "schemas.md").resolve()),
        "instructions": [
            "Read source.json first.",
            "Read the PDF if pdf_path exists.",
            "Produce one valid memory.json payload only.",
            "If the evidence is weak, use questions_to_verify instead of pretending certainty.",
        ],
        "generated_at": utc_now(),
    }

    output_path = paths["tasks"] / "summaries" / f"{args.paper_id}.json"
    write_json(output_path, task_payload)
    print(f"Wrote summary task to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
