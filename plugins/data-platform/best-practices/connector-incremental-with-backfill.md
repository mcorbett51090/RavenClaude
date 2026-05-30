# Build connectors incremental-first — with an explicit, resumable backfill path

**Status:** Pattern — strong default for every custom or configured connector; deviate only for tables small enough that full-refresh is cheaper than the cursor bookkeeping.

**Domain:** Connector reliability / incremental sync

**Applies to:** `data-platform`

---

## Why this exists

A connector that re-pulls the full source on every run works on a 100-row dev account and falls over on a 10M-row production tenant — it blows the rate-limit budget, the MAR/credit budget, and the sync window. The correct shape is **incremental by cursor** (only pull rows changed since the last watermark) with a **separate, explicit backfill path** for the initial historical load and for re-pulls after a schema change. The two are different code paths with different failure modes: incremental must checkpoint its cursor so a mid-sync crash resumes from the last durable point; backfill must be chunked and resumable so a 6-hour historical pull that dies at hour 5 doesn't restart at hour 0. Conflating them — "just run full refresh nightly" — is the recurring break, and it's invisible until volume arrives.

## How to apply

Pick a monotonic cursor field, checkpoint it per stream, and chunk the backfill by a bounded window so each chunk is independently retryable.

```python
# Airbyte CDK incremental stream: cursor + checkpoint + Retry-After honoring.
class Invoices(IncrementalStream):
    cursor_field = "updated_at"          # monotonic; server-set, not client clock
    primary_key = "id"
    state_checkpoint_interval = 1000     # persist state every N records — resumable

    def request_params(self, stream_state, **kwargs):
        since = (stream_state or {}).get(self.cursor_field, self.start_date)
        return {"updated_since": since, "limit": 200, "order": "updated_at asc"}

    def backoff_time(self, response):
        return float(response.headers.get("Retry-After", 30))  # honor server signal
```

```yaml
# Backfill = a bounded, resumable window sweep, NOT one giant request.
backfill:
  start_date: "2022-01-01"
  window: { count: 30, period: day }   # one chunk per 30-day slice
  resume_from_state: true              # a failed chunk retries; completed chunks skip
```

**Do:**
- Choose a **server-set, monotonic** cursor (`updated_at`/`modified`/sequence) — never the client clock, never a field the source can rewrite backwards.
- Checkpoint cursor state at a bounded interval so a crash resumes mid-stream, not from zero.
- Make backfill a **bounded window sweep** (per-day/per-month chunks) so each chunk is independently retryable and progress survives a failure.
- Honor `Retry-After` and use exponential backoff with a ceiling — rate-limit-naive retry is broken-by-default.

**Don't:**
- Default to full-refresh nightly on a large table "because it's simpler" — it isn't, at volume.
- Page without state checkpointing (one network blip = restart from row 1).
- Use offset pagination on a mutating table (rows shift under you, you skip/duplicate); prefer cursor/keyset.

## Edge cases / when the rule does NOT apply

- **Small dimension tables** (a few thousand rows, no reliable cursor) — full-refresh/overwrite is cheaper and idempotent by construction; skip the cursor bookkeeping.
- **CDC-capable sources** (log-based replication via Fivetran HVR / Debezium-style) — the log *is* the incremental cursor; the rule's spirit holds but the mechanism is the WAL, not a query param.
- **No reliable modified-timestamp** (some legacy APIs) — fall back to full-refresh + dedup, and document the cost so a future cursor addition is on the radar.

## See also

- [`./ingest-idempotent-and-replayable.md`](./ingest-idempotent-and-replayable.md) — the load into raw must be replay-safe regardless of incremental vs backfill
- [`./dbt-incremental-with-unique-key-for-large-facts.md`](./dbt-incremental-with-unique-key-for-large-facts.md) — the dbt-layer analogue of incremental-with-key
- [`../agents/connector-developer.md`](../agents/connector-developer.md) — owns custom Airbyte CDK authoring
- [`../skills/connector-configuration/SKILL.md`](../skills/connector-configuration/SKILL.md) — per-source cursor/rate-limit specifics (QBO, Stripe, Salesforce, HubSpot)

## Provenance

Distilled from `connector-developer.md` ("Pagination + state are the silent killers"; "cursor-based pagination + checkpointed state + resumable runs are non-negotiable"; "Incremental sync — replication key selection, primary key + cursor field combinations") and `etl-pipeline-engineer.md` rate-limit rules. `[verify-at-build]` Airbyte CDK class names (`IncrementalStream`, `state_checkpoint_interval`) drift across CDK versions — confirm against current Airbyte Python CDK reference before quoting in code.

---

_Last reviewed: 2026-05-30 by `claude`_
