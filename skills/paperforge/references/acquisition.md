# Acquisition

Paper acquisition is an optional but built-in pre-step to `PaperForge`.

## Allowed Acquisition Modes

1. Human import
   - download the paper manually
   - attach it in Zotero
   - optionally add tags, collections, and notes

2. OpenClaw-assisted import through PaperForge tasks
   - create an acquisition task with `init_acquisition_task.py`
   - let OpenClaw or Codex search the web and import the result into Zotero
   - save the result with `save_acquisition_result.py`
   - let `PaperForge` pick it up on the next sync

## Boundary

`PaperForge` acquisition support exists to get papers into Zotero, but the core memory loop still starts from Zotero.

That means:

- acquisition tasks are optional helper flows
- sync only needs Zotero metadata and attachment paths
- the same sync pipeline works for both manual and OpenClaw-assisted acquisition

## Recommended Flow

```text
manual download
OR
PaperForge acquisition task -> executor web import -> Zotero item + attachment
-> PaperForge sync
-> executor summary
-> memory save
-> grounded Q&A
```

## Built-In Acquisition Task Flow

1. Create a task:

```bash
python3 skills/paperforge/scripts/init_acquisition_task.py \
  --config paperforge.config.json \
  --title "paper title or rough query"
```

2. Let the executor read:

- `workspace/tasks/acquisition/*.json`
- `references/acquisition_prompt.md`
- `references/acquisition_result_schema.md`

3. Persist the result:

```bash
python3 skills/paperforge/scripts/save_acquisition_result.py \
  --config paperforge.config.json \
  --input /path/to/result.json
```

4. If Zotero import succeeded, run `sync_zotero.py`.
