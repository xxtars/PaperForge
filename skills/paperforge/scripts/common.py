#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def load_config(config_path: Path) -> dict:
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    workspace_dir = Path(raw["workspace_dir"]).expanduser().resolve()
    default_idea_path = Path(raw.get("default_idea_path", workspace_dir / "ideas" / "current_idea.md"))
    return {
        "library_name": raw.get("library_name", "Zotero Research Library"),
        "workspace_dir": workspace_dir,
        "zotero_storage_path": _maybe_resolve(raw.get("zotero_storage_path")),
        "zotero_export_path": _maybe_resolve(raw.get("zotero_export_path")),
        "default_idea_path": default_idea_path.expanduser().resolve(),
    }


def ensure_workspace(config: dict) -> dict[str, Path]:
    workspace = Path(config["workspace_dir"])
    paths = {
        "workspace": workspace,
        "papers": workspace / "papers",
        "index": workspace / "index",
        "ideas": workspace / "ideas",
        "context": workspace / "context",
        "tasks": workspace / "tasks",
        "acquisition": workspace / "acquisition",
        "state": workspace / "state",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    (paths["tasks"] / "summaries").mkdir(parents=True, exist_ok=True)
    (paths["tasks"] / "qa").mkdir(parents=True, exist_ok=True)
    (paths["tasks"] / "acquisition").mkdir(parents=True, exist_ok=True)
    (paths["acquisition"] / "results").mkdir(parents=True, exist_ok=True)

    idea_path = Path(config["default_idea_path"])
    idea_path.parent.mkdir(parents=True, exist_ok=True)
    if not idea_path.exists():
        idea_path.write_text(
            """# Current Idea

## Idea Statement

## Why This Matters

## What Existing Work Still Gets Wrong

## What Could Make This Novel

## Questions To Test
""",
            encoding="utf-8",
        )
    return paths


def stable_id(seed: str) -> str:
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def tokenize(text: str) -> set[str]:
    tokens = set(re.findall(r"[a-zA-Z][a-zA-Z0-9-]+", text.lower()))
    stopwords = {
        "a",
        "an",
        "and",
        "are",
        "for",
        "from",
        "in",
        "into",
        "is",
        "of",
        "on",
        "or",
        "the",
        "this",
        "to",
        "with",
    }
    return {token for token in tokens if len(token) > 2 and token not in stopwords}


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "context"


def extract_year(raw_date: object) -> int | None:
    if raw_date is None:
        return None
    pieces = re.findall(r"\d{4}", str(raw_date))
    return int(pieces[0]) if pieces else None


def load_paper_dirs(config: dict) -> list[Path]:
    papers_dir = Path(config["workspace_dir"]) / "papers"
    if not papers_dir.exists():
        return []
    return sorted(path for path in papers_dir.iterdir() if path.is_dir())


def file_signature(path: Path | None) -> dict | None:
    if not path or not path.exists():
        return None
    stat = path.stat()
    return {
        "path": str(path.resolve()),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def _maybe_resolve(raw: str | None) -> Path | None:
    if not raw:
        return None
    return Path(raw).expanduser().resolve()
