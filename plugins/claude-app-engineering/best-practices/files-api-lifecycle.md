# Give Files API files a lifecycle: upload once, reuse, delete on expiry

**Status:** Pattern
**Domain:** Files API / cost
**Applies to:** `claude-app-engineering`

---

## Why this exists

The Files API lets you upload a document once and reference it by `file_id`
across many requests — trading upload latency for per-request base64 overhead.
Teams that don't manage the lifecycle either pay for redundant re-uploads (if they
re-upload the same document per session) or accumulate unbounded file storage
that can expose stale or sensitive documents to later sessions. Neither is
intentional engineering.

## How to apply

Maintain a content-hash → `file_id` registry (a simple key-value store or a
column in your document table). On each upload:

1. Hash the document bytes (`sha256`).
2. Check the registry — if a current `file_id` exists, skip the upload and use
   the cached id.
3. If the `file_id` doesn't exist or has expired, upload with the Files API and
   record the new id + upload timestamp.
4. On a schedule (or at session close for ephemeral docs), delete `file_id`s
   older than your retention policy.

```python
import hashlib, anthropic

client = anthropic.Anthropic()
file_registry: dict[str, str] = {}  # sha256 -> file_id

def get_or_upload(content: bytes, filename: str) -> str:
    digest = hashlib.sha256(content).hexdigest()
    if digest in file_registry:
        return file_registry[digest]
    resp = client.beta.files.upload(
        file=(filename, content, "application/pdf"),
    )
    file_registry[digest] = resp.id
    return resp.id

def cleanup_old_files(older_than_days: int):
    for file in client.beta.files.list().data:
        age = (datetime.utcnow() - file.created_at).days
        if age > older_than_days:
            client.beta.files.delete(file.id)
```

**Do:**
- Deduplicate uploads by content hash; the same document referenced N times costs
  one upload and N cheap `file_id` references.
- Set a retention TTL proportional to the sensitivity of the data.
- Delete files when the conversation or session they were uploaded for ends, for
  ephemeral user-provided documents.

**Don't:**
- Re-upload the same document for every API call (negates the Files API savings).
- Treat the Files API as permanent storage — it is a transient acceleration layer.
- Leave user-uploaded documents indefinitely in the workspace without a deletion
  schedule.

## Edge cases / when the rule does NOT apply

- Very large, unique, one-off documents (e.g. a 500-page regulatory filing used
  once): upload, use, delete immediately; no registry entry needed.
- When the document content changes frequently (> once per cache TTL): uploading
  fresh is correct; just don't forget to delete the old file.

## See also

- [`../agents/mcp-and-server-tools-engineer.md`](../agents/mcp-and-server-tools-engineer.md) — owns Files API + server tools
- [`./multi-tenant-context-isolation.md`](./multi-tenant-context-isolation.md) — Files API namespace must be tenant-scoped

## Provenance

Codifies the Files API lifecycle guidance from
`knowledge/server-side-tools-and-files.md` (retrieved 2026-05-28). Files API
beta status — re-verify GA/beta and per-file limits against the dated capability
map before quoting a client.

---

_Last reviewed: 2026-06-05 by `claude`_
