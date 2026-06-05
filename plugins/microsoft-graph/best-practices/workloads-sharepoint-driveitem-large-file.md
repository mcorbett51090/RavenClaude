# Use upload sessions for SharePoint/OneDrive files above 4 MB — not single PUT

**Status:** Absolute rule
**Domain:** Microsoft Graph / SharePoint and OneDrive workloads
**Applies to:** `microsoft-graph`

---

## Why this exists

The Microsoft Graph simple upload endpoint (`PUT /drive/items/{id}/content`) has a hard maximum of **4 MB per request** `[verify-at-build]`. Sending a file larger than the limit produces a `413 Request Entity Too Large` or a `400` depending on the client stack. Developers who test with small files in dev and then encounter real-world document uploads in prod discover the limit at runtime. The upload session API (`createUploadSession`) handles files of any size by uploading in fragments and is the only supportable path for user-generated file uploads where file size is not bounded.

## How to apply

```python
# Step 1: Create an upload session
import requests, os

session_url = (
    f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{parent_id}:/{filename}:/createUploadSession"
)
session = requests.post(session_url, headers={"Authorization": f"Bearer {token}"}, json={
    "item": {"@microsoft.graph.conflictBehavior": "rename", "name": filename}
})
upload_url = session.json()["uploadUrl"]

# Step 2: Upload in 4 MB fragments (must be a multiple of 320 KiB)
CHUNK_SIZE = 4 * 1024 * 1024  # 4 MiB
file_size = os.path.getsize(local_path)
with open(local_path, "rb") as f:
    offset = 0
    while offset < file_size:
        chunk = f.read(CHUNK_SIZE)
        end = offset + len(chunk) - 1
        requests.put(
            upload_url,
            data=chunk,
            headers={
                "Content-Length": str(len(chunk)),
                "Content-Range": f"bytes {offset}-{end}/{file_size}",
            }
        )
        offset += len(chunk)
```

Rules:
- Fragment size must be a **multiple of 320 KiB** (327,680 bytes) — any other size causes a `416` on some backends `[verify-at-build]`.
- Upload sessions expire after a platform-defined idle timeout (typically 30 minutes) — for large files, keep uploading without long pauses.
- On failure, query the upload session URL (`GET {uploadUrl}`) to discover which byte ranges were received and resume from the first missing range.

**Do:**
- Set `@microsoft.graph.conflictBehavior` to `rename` or `replace` explicitly — the default varies by endpoint and is surprising.
- Use the Graph SDK's `LargeFileUploadTask` helper if available in your language SDK — it encapsulates fragment sizing and retry.
- Confirm the target drive supports the file size: OneDrive personal has different quotas than SharePoint document libraries `[verify-at-build]`.

**Don't:**
- Use the simple PUT endpoint for any upload where the file size is not strictly controlled to < 4 MB.
- Store the `uploadUrl` in a long-lived cache — it is session-scoped and expires.
- Send concurrent requests to the same upload session — the upload is sequential by byte range.

## Edge cases / when the rule does NOT apply

For programmatic small-asset uploads (JSON configuration files, thumbnails < 1 MB) where the size is strictly bounded and controlled by the application, the simple PUT endpoint is acceptable. Document the size bound.

## See also

- [`../agents/graph-workloads-engineer.md`](../agents/graph-workloads-engineer.md) — owns SharePoint/OneDrive Graph workloads
- [`./workloads-mail-and-attachments-at-scale.md`](./workloads-mail-and-attachments-at-scale.md) — the same large-file concern for mail attachments

## Provenance

Codifies CLAUDE.md §3 #3/#5 applied to file upload; Microsoft Graph large file upload session documentation (v1.0).

---

_Last reviewed: 2026-06-05 by `claude`_
