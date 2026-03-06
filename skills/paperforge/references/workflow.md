# Workflow

## 0. Optional Acquisition

Papers may reach Zotero in two ways:

1. manual download and attachment
2. PaperForge acquisition task handled by OpenClaw or Codex

If you need executor-assisted acquisition, see `acquisition.md`.

## 1. Sync Zotero Into Local Memory

Run:

```bash
python3 skills/paperforge/scripts/sync_zotero.py --config paperforge.config.json
```

This creates:

- `workspace/papers/<paper_id>/source.json`
- `workspace/papers/<paper_id>/memory.json` with `status: pending` if no AI summary exists yet
- `workspace/index/pending_summaries.json`
- `workspace/ideas/current_idea.md` if missing
- `workspace/state/sync_state.json`

To automate this for both manual Zotero imports and acquisition-driven Zotero imports, run:

```bash
python3 skills/paperforge/scripts/watch_zotero.py \
  --config paperforge.config.json \
  --interval 30
```

The watch loop polls Zotero sources and triggers incremental sync whenever the Zotero export or storage changes.

## 2. Let The Executor Summarize Pending Papers

The executor should:

1. pick a paper from `pending_summaries.json`
2. run:

```bash
python3 skills/paperforge/scripts/init_summary_task.py \
  --config paperforge.config.json \
  --paper-id <paper_id>
```

3. read the generated task file under `workspace/tasks/summaries/`
4. read `references/summary_prompt.md`
5. open `source.json` and the linked PDF
6. produce a `memory.json` payload that follows `schemas.md`
7. store it with `save_memory.py`

The local script should not summarize the paper itself. That work belongs to OpenClaw or Codex.

## 3. Build A Grounded Context Bundle For Q&A

Run:

```bash
python3 skills/paperforge/scripts/build_context.py \
  --config paperforge.config.json \
  --question "What are the main limitations of work closest to my idea?" \
  --idea workspace/ideas/current_idea.md
```

This creates a grounded bundle under `workspace/context/`.
It also creates a QA task file under `workspace/tasks/qa/`.

The executor should then read `references/qa_prompt.md` and answer from that bundle first. If the bundle is too sparse, it may browse the web and must label outside findings as external.

## 4. Idea-Centered Question Answering

Preferred order:

1. current idea file
2. top relevant `memory.json` files
3. linked `source.json` metadata
4. web only if the local evidence is insufficient

## 5. Human Review Loop

Zotero remains the manual correction layer:

- fix bad metadata in Zotero
- adjust collections or tags
- rerun sync
- regenerate local context bundles

## 6. Acquisition Variants

PaperForge supports two upstream acquisition variants:

1. human download into Zotero
2. executor-assisted PaperForge acquisition into Zotero

Both feed the same downstream sync and memory workflow.
