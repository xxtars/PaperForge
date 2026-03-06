# Schemas

Use these schemas when the executor reads a paper and prepares structured memory.

## `source.json`

Stored by `sync_zotero.py`.

```json
{
  "paper_id": "6f81e0c4bc0a",
  "title": "Paper title",
  "authors": ["Author One", "Author Two"],
  "year": 2025,
  "abstract": "Original Zotero abstract if present.",
  "pdf_path": "/absolute/path/to/paper.pdf",
  "source": "zotero_export",
  "tags": ["benchmark"],
  "collections": ["reading-inbox"],
  "zotero_key": "ABCD1234"
}
```

## `memory.json`

Stored by `save_memory.py`.

```json
{
  "status": "summarized",
  "summary_short": "2-4 sentence summary for fast recall.",
  "problem": "What exact problem does the paper solve?",
  "contributions": [
    "Contribution 1",
    "Contribution 2"
  ],
  "method": "Short method description.",
  "assumptions": [
    "Assumption 1"
  ],
  "limitations": [
    "Limitation 1"
  ],
  "evidence": [
    "What evidence supports the main contribution?"
  ],
  "idea_hooks": [
    "How this paper could help refine or challenge an idea."
  ],
  "questions_to_verify": [
    "What should be checked in the PDF before trusting the summary?"
  ],
  "keywords": [
    "agents",
    "benchmark"
  ],
  "updated_by": "codex-or-openclaw",
  "updated_at": "2026-03-06T12:00:00Z"
}
```

Required fields:

- `status`
- `summary_short`
- `problem`
- `contributions`
- `limitations`
- `idea_hooks`
- `updated_by`
- `updated_at`

Recommended values for `status`:

- `pending`
- `summarized`
- `needs_review`

## `context/*.json`

Stored by `build_context.py`.

This bundle is what the executor should use as grounded context before answering the final question.

```json
{
  "question": "What are the strongest limitations of papers closest to my idea?",
  "idea_path": "/abs/path/workspace/ideas/current_idea.md",
  "idea_excerpt": "Current idea text...",
  "top_papers": [
    {
      "paper_id": "6f81e0c4bc0a",
      "title": "Paper title",
      "score": 17,
      "source_path": "/abs/path/workspace/papers/6f81e0c4bc0a/source.json",
      "memory_path": "/abs/path/workspace/papers/6f81e0c4bc0a/memory.json",
      "summary_short": "Short summary",
      "contributions": ["..."],
      "limitations": ["..."],
      "idea_hooks": ["..."]
    }
  ],
  "local_gap_flags": [
    "Only 2 relevant papers have structured memory."
  ],
  "web_search_recommended": true
}
```
