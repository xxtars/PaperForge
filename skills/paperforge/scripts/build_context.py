#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_workspace, load_config, load_paper_dirs, read_json, slugify, tokenize, utc_now, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a grounded local context bundle for executor-driven Q&A.")
    parser.add_argument("--config", type=Path, default=Path("paperforge.config.json"))
    parser.add_argument("--question", required=True)
    parser.add_argument("--idea", type=Path)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    config = load_config(args.config)
    paths = ensure_workspace(config)
    idea_path = (args.idea or config["default_idea_path"]).expanduser().resolve()
    idea_text = idea_path.read_text(encoding="utf-8") if idea_path.exists() else ""

    ranked = rank_papers(config, args.question, idea_text)
    top_papers = ranked[: args.top_k]

    payload = {
        "question": args.question,
        "idea_path": str(idea_path),
        "idea_excerpt": idea_text[:3000],
        "top_papers": top_papers,
        "local_gap_flags": gap_flags(top_papers),
        "web_search_recommended": len(top_papers) < 3 or any(item["score"] < 6 for item in top_papers),
        "generated_at": utc_now(),
    }

    output_path = paths["context"] / f"{slugify(args.question)}.json"
    write_json(output_path, payload)
    write_json(
        paths["tasks"] / "qa" / f"{slugify(args.question)}.json",
        {
            "task_type": "grounded_qa",
            "question": args.question,
            "context_path": str(output_path.resolve()),
            "qa_prompt_path": str((Path(__file__).resolve().parent.parent / "references" / "qa_prompt.md").resolve()),
            "instructions": [
                "Answer from local evidence first.",
                "Use the web only if the local bundle is sparse or outdated.",
                "Label web findings as external evidence.",
            ],
            "generated_at": utc_now(),
        },
    )
    print(f"Wrote context bundle to {output_path}")
    return 0


def rank_papers(config: dict, question: str, idea_text: str) -> list[dict]:
    query_tokens = tokenize(question) | tokenize(idea_text)
    ranked = []
    for paper_dir in load_paper_dirs(config):
        source = read_json(paper_dir / "source.json")
        memory = read_json(paper_dir / "memory.json")
        paper_tokens = tokenize(
            " ".join(
                [
                    source.get("title", ""),
                    source.get("abstract", ""),
                    " ".join(source.get("tags", [])),
                    " ".join(memory.get("contributions", [])),
                    " ".join(memory.get("limitations", [])),
                    " ".join(memory.get("idea_hooks", [])),
                    memory.get("problem", ""),
                    memory.get("summary_short", ""),
                ]
            )
        )
        overlap = len(query_tokens & paper_tokens)
        status_bonus = 5 if memory.get("status") == "summarized" else 0
        score = overlap + status_bonus
        if score == 0:
            continue
        ranked.append(
            {
                "paper_id": source["paper_id"],
                "title": source["title"],
                "score": score,
                "source_path": str((paper_dir / "source.json").resolve()),
                "memory_path": str((paper_dir / "memory.json").resolve()),
                "summary_short": memory.get("summary_short", ""),
                "contributions": memory.get("contributions", []),
                "limitations": memory.get("limitations", []),
                "idea_hooks": memory.get("idea_hooks", []),
            }
        )
    ranked.sort(key=lambda item: (-item["score"], item["title"].lower()))
    return ranked


def gap_flags(top_papers: list[dict]) -> list[str]:
    flags = []
    if len(top_papers) < 3:
        flags.append("Fewer than 3 relevant local papers were found.")
    unsummarized = [paper for paper in top_papers if not paper["summary_short"]]
    if unsummarized:
        flags.append("Some top-ranked papers still lack structured AI summary.")
    return flags


if __name__ == "__main__":
    raise SystemExit(main())
