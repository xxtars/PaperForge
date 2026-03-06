# QA Prompt

Use this prompt after `build_context.py` creates a grounded local context bundle.

## Goal

Answer the user's research question from the local PaperForge memory first, using Zotero-bounded evidence. Use the web only if the local bundle is too sparse or outdated.

## Inputs

- a context bundle from `workspace/context/*.json`
- the current idea file, if present in the bundle
- linked `memory.json` and `source.json` paths for the top papers

## Answering Order

1. Answer from local evidence first.
2. Cite which local papers are most relevant.
3. If local evidence is insufficient and web search is needed, say so explicitly.
4. Label outside findings as `External evidence`, not as Zotero-backed evidence.

## What To Focus On

For novelty questions:

- which local papers overlap most with the idea
- what appears already done
- where the strongest differentiation opportunities remain

For limitation questions:

- recurring limitations across the top local papers
- weak assumptions or missing evaluations
- what those gaps suggest for a new idea

For idea-refinement questions:

- which papers are closest
- what the idea should narrow, change, or test next
- what evidence is still missing

## Output Style

- Be concrete.
- Separate `Local evidence` from `External evidence` when both appear.
- Prefer evidence-backed judgments over generic writing.
- If the bundle is sparse, say what additional local summaries are still needed.
