# Summary Prompt

Use this prompt when OpenClaw or Codex is asked to read one paper and produce a `memory.json` payload.

## Goal

Read the paper grounded by `source.json` and produce a concise, evidence-aware `memory.json` that will be reused later for idea-centered Q&A.

## Inputs

- `source.json`
- the PDF at `pdf_path`, if present
- `schemas.md`

## Required Output

Return one valid JSON object matching the `memory.json` schema from `schemas.md`.

Do not return markdown, code fences, or extra explanation.

## Extraction Rules

1. `summary_short`
   Write 2 to 4 sentences for fast recall.
2. `problem`
   State the exact research problem, not a generic theme.
3. `contributions`
   List only substantive contributions. Avoid inflated abstract wording.
4. `method`
   Describe the actual approach briefly.
5. `assumptions`
   Record the strongest assumptions the paper depends on.
6. `limitations`
   Record concrete weaknesses, missing evaluations, narrow scope, or transfer risks.
7. `evidence`
   Record the main evidence that supports the contribution claims.
8. `idea_hooks`
   Explain how this paper could support, challenge, narrow, or differentiate a future idea.
9. `questions_to_verify`
   Use this whenever the paper is unclear, the PDF is missing, or your confidence is limited.

## Quality Bar

- Prefer precise claims over broad summary prose.
- If the paper is a survey or benchmark, say so clearly.
- Distinguish contribution from framing.
- Distinguish limitation from future work marketing.
- If the local evidence is weak, be explicit about uncertainty instead of filling gaps with guesses.

## Field Guidance

- `status`
  Use `summarized` when the summary is usable, or `needs_review` when important uncertainty remains.
- `updated_by`
  Set to `codex` or `openclaw`.
- `updated_at`
  Use an ISO 8601 UTC timestamp.
