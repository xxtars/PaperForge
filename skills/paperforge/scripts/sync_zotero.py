#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_workspace, extract_year, file_signature, load_config, read_json, stable_id, utc_now, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Zotero metadata and PDFs into the local research workspace.")
    parser.add_argument("--config", type=Path, default=Path("paperforge.config.json"))
    parser.add_argument("--force", action="store_true", help="Ignore sync state and rescan Zotero sources.")
    args = parser.parse_args()

    config = load_config(args.config)
    paths = ensure_workspace(config)
    state_path = paths["state"] / "sync_state.json"
    previous_state = read_json(state_path) if state_path.exists() else {"items": {}, "sources": {}}
    seen_ids: set[str] = set()
    imported = 0
    changed = 0

    export_path = config["zotero_export_path"]
    if export_path and export_path.exists():
        raw = read_json(export_path)
        items = raw if isinstance(raw, list) else raw.get("items", [])
        for item in items:
            title = str(item.get("title") or "").strip()
            if not title:
                continue
            paper_id = stable_id(str(item.get("key") or title))
            item_signature = _signature_for_export_item(item, config)
            seen_ids.add(paper_id)
            if not args.force and previous_state["items"].get(paper_id) == item_signature:
                continue
            _upsert_paper_from_export(paths["papers"], config, paper_id, item)
            previous_state["items"][paper_id] = item_signature
            seen_ids.add(paper_id)
            imported += 1
            changed += 1

    storage_path = config["zotero_storage_path"]
    if storage_path and storage_path.exists():
        for pdf_path in storage_path.rglob("*.pdf"):
            paper_id = stable_id(str(pdf_path))
            pdf_signature = _signature_for_pdf(pdf_path)
            if paper_id in seen_ids and not args.force and previous_state["items"].get(paper_id) == pdf_signature:
                continue
            if not args.force and previous_state["items"].get(paper_id) == pdf_signature:
                seen_ids.add(paper_id)
                continue
            _upsert_paper_from_pdf(paths["papers"], paper_id, pdf_path)
            previous_state["items"][paper_id] = pdf_signature
            seen_ids.add(paper_id)
            imported += 1
            changed += 1

    pending = _refresh_pending_queue(paths["papers"], paths["index"] / "pending_summaries.json")
    previous_state["sources"] = {
        "zotero_export_path": file_signature(export_path),
        "zotero_storage_path": file_signature(storage_path),
    }
    write_json(state_path, previous_state)
    print(f"Synced {imported} papers into {paths['workspace']}")
    print(f"Detected {changed} changed or new papers in this run")
    print(f"{pending} papers are waiting for AI summary")
    return 0


def _upsert_paper_from_export(papers_dir: Path, config: dict, paper_id: str, item: dict) -> None:
    paper_dir = papers_dir / paper_id
    paper_dir.mkdir(parents=True, exist_ok=True)

    authors = []
    for creator in item.get("creators", []):
        first = str(creator.get("firstName") or "").strip()
        last = str(creator.get("lastName") or "").strip()
        name = " ".join(part for part in [first, last] if part).strip()
        if name:
            authors.append(name)

    source_payload = {
        "paper_id": paper_id,
        "title": str(item.get("title") or "").strip(),
        "authors": authors,
        "year": extract_year(item.get("date")),
        "abstract": str(item.get("abstractNote") or "").strip(),
        "pdf_path": _resolve_attachment_path(config, item),
        "source": "zotero_export",
        "tags": [tag.get("tag") for tag in item.get("tags", []) if tag.get("tag")],
        "collections": list(item.get("collections") or []),
        "zotero_key": item.get("key"),
        "synced_at": utc_now(),
    }
    write_json(paper_dir / "source.json", source_payload)
    _ensure_memory_stub(paper_dir)


def _upsert_paper_from_pdf(papers_dir: Path, paper_id: str, pdf_path: Path) -> None:
    paper_dir = papers_dir / paper_id
    paper_dir.mkdir(parents=True, exist_ok=True)
    source_payload = {
        "paper_id": paper_id,
        "title": pdf_path.stem.replace("_", " ").strip(),
        "authors": [],
        "year": None,
        "abstract": "",
        "pdf_path": str(pdf_path.resolve()),
        "source": "zotero_storage",
        "tags": [],
        "collections": [],
        "zotero_key": None,
        "synced_at": utc_now(),
    }
    write_json(paper_dir / "source.json", source_payload)
    _ensure_memory_stub(paper_dir)


def _ensure_memory_stub(paper_dir: Path) -> None:
    memory_path = paper_dir / "memory.json"
    if memory_path.exists():
        return
    write_json(
        memory_path,
        {
            "status": "pending",
            "summary_short": "",
            "problem": "",
            "contributions": [],
            "method": "",
            "assumptions": [],
            "limitations": [],
            "evidence": [],
            "idea_hooks": [],
            "questions_to_verify": [],
            "keywords": [],
            "updated_by": "",
            "updated_at": "",
        },
    )


def _refresh_pending_queue(papers_dir: Path, output_path: Path) -> int:
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


def _resolve_attachment_path(config: dict, item: dict) -> str | None:
    attachments = item.get("attachments") or []
    storage_path = config["zotero_storage_path"]
    for attachment in attachments:
        raw_path = attachment.get("path") or attachment.get("localPath")
        if not raw_path:
            continue
        raw_path = str(raw_path)
        if raw_path.startswith("storage:") and storage_path:
            rel = raw_path.split("storage:", 1)[1].lstrip("/")
            return str((storage_path / rel).resolve())
        return str(Path(raw_path).expanduser().resolve())
    return None


def _signature_for_export_item(item: dict, config: dict) -> dict:
    return {
        "source": "zotero_export",
        "key": item.get("key"),
        "title": str(item.get("title") or "").strip(),
        "date": str(item.get("date") or ""),
        "abstract": str(item.get("abstractNote") or "").strip(),
        "pdf_path": _resolve_attachment_path(config, item),
        "tags": [tag.get("tag") for tag in item.get("tags", []) if tag.get("tag")],
        "collections": list(item.get("collections") or []),
    }


def _signature_for_pdf(pdf_path: Path) -> dict:
    stat = pdf_path.stat()
    return {
        "source": "zotero_storage",
        "path": str(pdf_path.resolve()),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


if __name__ == "__main__":
    raise SystemExit(main())
