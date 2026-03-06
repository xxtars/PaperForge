# Acquisition Prompt

Use this prompt when OpenClaw or Codex is asked to find a paper on the web and add it to Zotero.

## Goal

Resolve a paper request into a Zotero item, ideally with a PDF attachment, then record the outcome in a JSON result file.

## Inputs

- the acquisition task JSON under `workspace/tasks/acquisition/`
- optional DOI, title, URL, or free-form notes from the user
- `acquisition_result_schema.md`

## Preferred Behavior

1. Search for the exact paper or its authoritative landing page.
2. Prefer official, lawful sources:
   - publisher page
   - arXiv
   - author or lab page
   - institutional repository
3. If Zotero import is available through the current executor environment, add the item and attachment to Zotero.
4. If a direct PDF cannot be imported, still add metadata to Zotero when possible.
5. Record the outcome in a valid acquisition result JSON.

## Safety Rules

- Do not bypass paywalls or access controls.
- Prefer metadata import over dubious PDF mirrors.
- If multiple papers match, record ambiguity instead of guessing.

## Required Output

Return one valid JSON object matching `acquisition_result_schema.md`.

Do not return markdown or prose around the JSON.
