# PaperForge

This repository is an OpenClaw-style skill for a local research agent built around Zotero.

The system is intentionally split into three layers:

- `Acquisition`
  Optional. Papers may be imported manually into Zotero or through built-in PaperForge acquisition tasks handled by OpenClaw or Codex.
- `Zotero`
  Collects papers, attachments, highlights, and human corrections.
- `Local scripts`
  Prepare data, persist structured paper memory, rank local evidence, and assemble context bundles.
- `OpenClaw / Codex`
  Read PDFs, generate AI summaries, answer questions, refine ideas, and browse the web when local evidence is insufficient.

The repository does not ship a model runtime. The local scripts are the durable memory and retrieval layer that both executors can use.
Acquisition is still upstream and optional, but the repository now includes built-in acquisition task helpers so it does not depend on separate download skills.

## Repository layout

```text
skills/paperforge/
  SKILL.md
  agents/openai.yaml
  references/
    summary_prompt.md
    qa_prompt.md
    acquisition.md
    acquisition_prompt.md
    acquisition_result_schema.md
    schemas.md
    workflow.md
  scripts/
    common.py
    init_acquisition_task.py
    save_acquisition_result.py
    sync_zotero.py
    watch_zotero.py
    init_summary_task.py
    save_memory.py
    build_context.py
    workspace_report.py
examples/
  zotero-export.sample.json
paperforge.config.example.json
```

## Setup

1. Copy `paperforge.config.example.json` to `paperforge.config.json`.
2. Fill in your local Zotero paths.
3. Run:

```bash
python3 skills/paperforge/scripts/sync_zotero.py --config paperforge.config.json
```

This builds `workspace/` with one folder per paper and a queue of papers that still need AI summary.

## Intended workflow

0. Optional acquisition:
   `init_acquisition_task.py` creates a download/import task for OpenClaw or Codex, and `save_acquisition_result.py` records the outcome.
1. `watch_zotero.py`
   Polls Zotero sources and triggers incremental `sync_zotero.py` whenever Zotero changes.
2. `sync_zotero.py`
   Imports Zotero export data and PDF paths into the local workspace after papers have entered Zotero.
3. OpenClaw or Codex reads `workspace/index/pending_summaries.json`.
4. For each pending paper, `init_summary_task.py` creates a task bundle for the executor.
5. OpenClaw or Codex reads the task bundle, `summary_prompt.md`, and the PDF, then creates a structured summary JSON that follows the schema in `skills/paperforge/references/schemas.md`.
6. `save_memory.py`
   Persists that structured memory to the matching paper folder.
7. `build_context.py`
   Assembles the most relevant local evidence for idea-centered question answering.
8. `build_context.py` also writes a QA task file under `workspace/tasks/qa/`.
9. OpenClaw or Codex uses `qa_prompt.md` plus the generated context bundle to answer questions, refine the idea, and optionally browse the web for missing external evidence.

## Why local scripts exist

Without a local persistence layer, the executor would have to re-read the same PDFs and re-summarize the same papers on every question.

The local scripts make the system cumulative:

- summaries are stored once
- questions reuse the stored evidence
- idea refinement works against a stable local memory
- Zotero remains the source boundary, not the reasoning engine

Upstream acquisition stays flexible:

- you can download and attach papers by hand in Zotero
- or OpenClaw/Codex can use PaperForge's built-in acquisition tasks to populate Zotero first
- `PaperForge` treats both as equivalent once the item exists in Zotero
