# Send and read mail (and attachments) at scale

**Status:** Pattern — strong default for mail/attachment work; deviate only with a written reason.

**Domain:** Web API / Outlook workloads

**Applies to:** `microsoft-graph`

---

## Why this exists

Mail looks simple (`POST /sendMail`) until the real cases hit: an attachment larger than the inline limit, a mailbox with tens of thousands of messages, or a list-then-read loop that over-fetches the full body of every message. Each has a specific Graph mechanism, and using the wrong one fails loudly (413 / size error) or quietly (truncated body, throttling from N serial reads). This rule names the mechanism per case so you don't re-derive it under load.

## How to apply

**Attachments by size.** Inline `fileAttachment` is only for **small** files (the documented ceiling is ~3 MB `[verify-at-build]`). Above that, create an **upload session** against the draft message and upload in ranges — the same chunked, resumable pattern as drive-item large-file upload.

```http
# small attachment — inline on create
POST /me/messages
{ "subject":"...", "attachments":[ {"@odata.type":"#microsoft.graph.fileAttachment",
  "name":"a.pdf","contentBytes":"<base64>"} ] }

# large attachment — draft, then upload session, then send
POST /me/messages                              # create draft, get {id}
POST /me/messages/{id}/attachments/createUploadSession
PUT  <uploadUrl>  Content-Range: bytes 0-...   # repeat per range
POST /me/messages/{id}/send
```

**Reading at scale.** `$select` the fields you need and **never `$expand=attachments` on a list** — it pulls every attachment's bytes for every message. Read the message list with `$select=id,subject,from,receivedDateTime`, then fetch attachments per-message only when needed. Use `$batch` to fold independent reads, and page to exhaustion (a large mailbox is many pages).

**Do:**

- Switch to an upload session the moment an attachment may exceed the inline ceiling.
- `$select` mail fields; fetch bodies/attachments lazily, not in the list call.
- `$batch` independent per-message reads; honor `429`/`Retry-After`.

**Don't:**

- Base64 a large file into `contentBytes` (it inflates ~33% and trips the size limit).
- `$expand=attachments` across a collection.
- Loop serial single-message GETs where a `$batch` (or `delta`) fits.

## Edge cases / when the rule does NOT apply

A one-off send of a small text body with no attachment is just `sendMail` — don't over-engineer it. Item attachments (`itemAttachment`, an embedded message/event) and reference attachments (a link to a file in OneDrive) are different `@odata.type`s with their own rules. The exact inline-vs-session size boundary is version-sensitive — `[verify-at-build]`.

## See also

- [`./api-batch-to-cut-round-trips.md`](./api-batch-to-cut-round-trips.md) — fold independent reads
- [`./api-select-only-what-you-need.md`](./api-select-only-what-you-need.md) — don't over-fetch bodies
- [`./api-page-to-exhaustion.md`](./api-page-to-exhaustion.md) — a large mailbox is many pages
- [`../agents/graph-workloads-engineer.md`](../agents/graph-workloads-engineer.md) — owns mail/calendar
- [Add attachments / large attachments to a message](https://learn.microsoft.com/graph/outlook-large-attachments) — authoritative

## Provenance

From the Microsoft Learn pages on sending mail, file attachments, and large-attachment upload sessions (retrieved 2026-05-30 via Microsoft Learn MCP), codifying house opinions #3 (`$select`) and #5 (`$batch`, throttling) for the mail surface specifically. The inline-attachment size ceiling is version-sensitive — `[verify-at-build]`. Surfaced by the two-panel coverage audit 2026-06-01.

---

_Last reviewed: 2026-06-01 by `claude`_
