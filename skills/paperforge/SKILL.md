---
name: paperforge
description: Use this skill when the user wants a Zotero-bounded local research agent that stores AI summaries, tracks contributions and limitations, and assembles evidence for idea-centered Q&A in OpenClaw or Codex.
---

# PaperForge

This skill turns a Zotero library into a local research memory that OpenClaw or Codex can reason over.

`PaperForge` supports optional built-in acquisition tasks for OpenClaw or Codex, but still treats Zotero as the source boundary for the core memory loop.

## Use This Skill For

- importing Zotero exports and attachment paths into a local workspace
- watching Zotero for changes and triggering incremental sync
- creating executor-facing acquisition tasks for finding and importing papers into Zotero
- working after papers were added to Zotero either manually or through a PaperForge acquisition task
- detecting papers that still need AI summary
- generating executor task files for paper summaries
- storing structured paper memory after the executor reads a paper
- assembling evidence bundles for novelty, limitation, and idea-refinement questions

## Do Not Use This Skill For

- replacing Zotero as the source of truth for raw papers
- embedding model logic into local scripts
- broad web search before checking local evidence

## Core Principle

Split responsibilities cleanly:

- acquisition is optional: human download or PaperForge acquisition task
- Zotero stores papers and human corrections
- local scripts prepare, persist, retrieve, and package evidence
- OpenClaw or Codex performs the actual model reasoning

## Minimal Workflow

1. Optional: create an acquisition task with `python3 skills/paperforge/scripts/init_acquisition_task.py --config paperforge.config.json --title "paper title"`
2. If acquisition happened, save the result with `python3 skills/paperforge/scripts/save_acquisition_result.py --config paperforge.config.json --input /path/to/result.json`
3. Run `python3 skills/paperforge/scripts/watch_zotero.py --config paperforge.config.json --interval 30` for automatic detection, or run `sync_zotero.py` manually.
4. Inspect `workspace/index/pending_summaries.json`
5. For each pending paper:
   - run `python3 skills/paperforge/scripts/init_summary_task.py --config paperforge.config.json --paper-id <paper_id>`
   - read the generated task file and `references/summary_prompt.md`
   - read the linked PDF
   - produce structured memory following `references/schemas.md`
   - persist it with `python3 skills/paperforge/scripts/save_memory.py --config paperforge.config.json --paper-id <paper_id> --input /path/to/memory.json`
6. Before answering a research question, build a context bundle:
   - `python3 skills/paperforge/scripts/build_context.py --config paperforge.config.json --question "..." --idea workspace/ideas/current_idea.md`
7. Read `references/qa_prompt.md` and use the generated context bundle as the grounding package for the executor's final answer.

## When To Read References

- Read `references/schemas.md` when creating or validating AI summary payloads.
- Read `references/acquisition.md` when using PaperForge's built-in acquisition flow.
- Read `references/acquisition_prompt.md` and `references/acquisition_result_schema.md` when completing an acquisition task.
- Read `references/summary_prompt.md` when preparing a single-paper AI summary.
- Read `references/qa_prompt.md` when answering a grounded idea question from a context bundle.
- Read `references/workflow.md` when you need the full end-to-end process for sync, summarization, and idea-centered Q&A.

## File Rules

- `source.json` stores imported Zotero metadata and attachment paths.
- `memory.json` stores structured AI understanding of a paper.
- `context/*.json` stores evidence bundles for downstream reasoning.
- Keep `memory.json` machine-readable and concise. Put the final long-form answer in executor output, not inside the memory file.

## Retrieval Rules

- Always search local `memory.json` files before using the web.
- Use acquisition tasks only to get papers into Zotero.
- Use the web only when the local workspace lacks enough evidence or the user explicitly asks for newer external work.
- When web evidence is added, label it as external rather than Zotero-backed.
