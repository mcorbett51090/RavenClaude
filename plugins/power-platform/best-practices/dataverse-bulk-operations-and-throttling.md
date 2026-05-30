# Batch bulk Dataverse writes and honor service-protection limits — back off on 429, don't hammer

**Status:** Absolute rule — ignoring service-protection limits gets your principal throttled or blocked.

**Domain:** Dataverse / Web API

**Applies to:** `power-platform`

---

## Why this exists

Dataverse enforces **service-protection API limits** per user/principal, per server, over a rolling 5-minute window — measured in request *count*, cumulative *execution time*, and *concurrent* request count. Cross any threshold and the platform returns **HTTP 429** with a **`Retry-After`** header telling you how long to wait. A naive bulk importer that fires one request per row as fast as it can will: (a) hit 429 and, if it retries immediately instead of honoring `Retry-After`, dig the hole deeper; (b) waste a request round-trip per row when `$batch` could send hundreds at once; and (c) hold an environment-wide metadata lock if it parallelizes *table creation* (only one `EntityCustomization` runs at a time). The discipline is: **batch the writes, parallelize only what's safe, and treat 429 as "wait exactly `Retry-After`," not "retry now."**

## How to apply

Group writes into `$batch` change sets, and wrap every call in a `Retry-After`-aware backoff.

```http
# Bulk writes via $batch — one HTTP round-trip for many operations.
# A change set is atomic (all-or-nothing); operations outside a change set are independent.
POST /api/data/v9.2/$batch
Content-Type: multipart/mixed; boundary=batch_AAA

--batch_AAA
Content-Type: multipart/mixed; boundary=changeset_BBB

--changeset_BBB
Content-Type: application/http
Content-Transfer-Encoding: binary

PATCH cnt_projects(cnt_code='PRJ-0042') HTTP/1.1   # Upsert by alternate key — GUID-free
Content-Type: application/json

{ "cnt_name": "Atlas" }
--changeset_BBB--
--batch_AAA--
```

```python
# Honor 429 / Retry-After. The header value is authoritative — do NOT retry sooner.
import time, requests
def call_with_backoff(send):
    while True:
        r = send()
        if r.status_code != 429:
            return r
        wait = int(r.headers.get("Retry-After", "5"))   # seconds the SERVER told you to wait
        time.sleep(wait)
```

| Operation | Right tool | Limit / lock to respect |
|---|---|---|
| Insert/update many **data rows** | `$batch` change sets + Upsert by alternate key | 429 + `Retry-After`; keep batch sizes modest (≈100–1000/changeset) |
| Bulk **create/delete** at volume | `CreateMultiple` / `UpdateMultiple` / `DeleteMultiple`, or async **bulk delete** job | Same service-protection window |
| Parallelize **column adds** across *different existing* tables | Multiple workers, post-table-creation | Safe — no env-wide lock once tables exist |
| Create **tables** | **Sequential only** | Env-wide `EntityCustomization` lock — parallel table creation fails |
| Publish customizations | **Once, at the end** | Don't publish incrementally — slower and race-prone |

**Do:**
- Send bulk data writes via **`$batch`** (or `CreateMultiple`/`UpdateMultiple`) instead of one request per row.
- On **429**, sleep for **exactly the `Retry-After` value**, then retry — that's the contract.
- Combine batching with **Upsert by alternate key** so the import is idempotent and re-runnable after a partial failure.
- **Create tables sequentially** (env-wide metadata lock); parallelize only column/view/form work on tables that already exist.
- **Publish once** at the end of a schema build.

**Don't:**
- Fire row-at-a-time requests in a tight loop — you'll exhaust the request-count limit and get throttled.
- Retry a 429 immediately (or with your own fixed sleep) — ignoring `Retry-After` makes throttling worse and can escalate to a temporary block.
- Parallelize **table creation** — `Cannot start another [EntityCustomization] because there is a previous [EntityCustomization] running` is the env-lock telling you to serialize.
- Wrap unrelated independent operations in **one atomic change set** — a single failure rolls them all back; use separate change sets (or batch entries) for independent work.

## Edge cases / when the rule does NOT apply

- **Interactive single-record** operations (a form save, one Patch from a canvas app) don't need batching — this rule is about *bulk*/programmatic volume.
- **Async bulk-delete jobs** and **import jobs** are the right tool for very large deletes/loads — they run server-side under their own scheduling rather than your client loop.
- A change set is **atomic by design** — when you *want* all-or-nothing semantics (e.g. parent + its lines), that's a feature, not the anti-pattern above.
- Some operations (plug-in-heavy writes, long-running messages) consume the **execution-time** budget faster than the request-count budget — a low request rate can still 429 on cumulative time; the same `Retry-After` discipline applies.
- **Service-protection limits are not the same as licensing/Power Platform request entitlements** — a principal can be within entitlement and still hit the per-window protection limit. Mark any specific numeric threshold `[unverified — verify against current Microsoft Learn]` before quoting it.

## See also

- [`../skills/dataverse-web-api/resources/parallelization.md`](../skills/dataverse-web-api/resources/parallelization.md) — the env-wide `EntityCustomization` lock, sequential-table-creation rule, publish-once, idempotent-script guidance
- [`./dataverse-alternate-keys-and-upsert.md`](./dataverse-alternate-keys-and-upsert.md) — Upsert-by-key for idempotent, re-runnable bulk imports
- [`./dataverse-access-error-is-not-a-schema-error.md`](./dataverse-access-error-is-not-a-schema-error.md) — distinguishing a 429 (throttling) from a 403 (access) from a 400 (schema)
- [`../knowledge/dataverse-token-acquisition.md`](../knowledge/dataverse-token-acquisition.md) — getting the bearer token your batch calls need
- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owner of the Dataverse data + write-path surface

## Provenance

Grounded in `skills/dataverse-web-api/resources/parallelization.md` (the env-wide `EntityCustomization` lock with the exact error string, sequential-table-creation rule, publish-once, idempotent re-runnable scripts) and the established Dataverse service-protection-limits contract (429 + `Retry-After`, `$batch`, `CreateMultiple`/`UpdateMultiple`/`DeleteMultiple`). Specific numeric thresholds are intentionally left unquoted and flagged `[unverified]` — they change and must be checked against current Microsoft Learn before being asserted.

---

_Last reviewed: 2026-05-30 by `claude`_
