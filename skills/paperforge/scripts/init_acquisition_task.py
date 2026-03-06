#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_workspace, load_config, slugify, utc_now, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an executor-facing acquisition task for finding and importing a paper into Zotero.")
    parser.add_argument("--config", type=Path, default=Path("paperforge.config.json"))
    parser.add_argument("--title", help="Target paper title or rough query")
    parser.add_argument("--doi", help="DOI if known")
    parser.add_argument("--url", help="Landing page or PDF URL if known")
    parser.add_argument("--notes", default="", help="Extra hints for the executor")
    args = parser.parse_args()

    if not any([args.title, args.doi, args.url]):
        raise SystemExit("Provide at least one of --title, --doi, or --url")

    config = load_config(args.config)
    paths = ensure_workspace(config)
    query = args.title or args.doi or args.url or "paper"
    task_slug = slugify(query)[:80]

    task_payload = {
        "task_type": "paper_acquisition",
        "library_name": config["library_name"],
        "query": {
            "title": args.title or "",
            "doi": args.doi or "",
            "url": args.url or "",
            "notes": args.notes or "",
        },
        "acquisition_prompt_path": str((Path(__file__).resolve().parent.parent / "references" / "acquisition_prompt.md").resolve()),
        "result_schema_path": str((Path(__file__).resolve().parent.parent / "references" / "acquisition_result_schema.md").resolve()),
        "result_output_path": str((paths["acquisition"] / "results" / f"{task_slug}.json").resolve()),
        "instructions": [
            "Search for the paper or its authoritative landing page.",
            "Prefer legal, publisher, author, arXiv, or repository sources.",
            "If possible, add the paper and PDF to Zotero.",
            "Record the exact outcome in the acquisition result JSON.",
        ],
        "generated_at": utc_now(),
    }

    output_path = paths["tasks"] / "acquisition" / f"{task_slug}.json"
    write_json(output_path, task_payload)
    print(f"Wrote acquisition task to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
