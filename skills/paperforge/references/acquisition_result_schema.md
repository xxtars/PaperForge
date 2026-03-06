# Acquisition Result Schema

Use this schema when the executor completes an acquisition task.

```json
{
  "status": "completed",
  "query": {
    "title": "Paper title or query",
    "doi": "",
    "url": "",
    "notes": ""
  },
  "resolved_title": "Resolved paper title",
  "resolved_doi": "10.xxxx/xxxxx",
  "resolved_url": "https://...",
  "pdf_url": "https://.../paper.pdf",
  "zotero_imported": true,
  "zotero_notes": "Optional note about where it was imported or what failed.",
  "external_actions": [
    "Searched publisher page",
    "Imported metadata into Zotero"
  ],
  "follow_up": [
    "Run sync_zotero.py after import"
  ],
  "updated_by": "codex-or-openclaw",
  "updated_at": "2026-03-06T12:00:00Z"
}
```

Required fields:

- `status`
- `query`
- `resolved_title`
- `zotero_imported`
- `external_actions`
- `updated_by`

Allowed `status` values:

- `completed`
- `partial`
- `failed`
