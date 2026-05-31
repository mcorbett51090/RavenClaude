---
description: Build an incremental-first custom connector — a monotonic server-set cursor with checkpointed state, a separate resumable backfill window-sweep, Retry-After backoff, and a design-time handoff plan.
argument-hint: "[the source ELT vendors don't ship, e.g. 'Canvas LMS' or 'a niche HRIS']"
---

# Build an incremental connector

You are running `/data-platform:build-incremental-connector`. Author the connector for the source the user named (`$ARGUMENTS`), following this plugin's `connector-developer` discipline. A connector that works on a 100-row dev account and falls over on a 10M-row tenant is the recurring failure.

## When to use this

A source the iPaaS vendors (Fivetran/Airbyte) don't ship a first-class connector for — the EdTech LMS gap (Canvas/Moodle/Schoology) is the canonical case. Not when a vendor connector already exists (configure it via `etl-pipeline-engineer` instead) or for a small dimension table where full-refresh is cheaper than cursor bookkeeping.

## Steps

1. **Incremental by cursor, with a separate backfill path** (`connector-incremental-with-backfill`): choose a **server-set, monotonic** cursor (`updated_at`/sequence — never the client clock, never a rewritable field). Checkpoint cursor state at a bounded interval so a crash resumes mid-stream. Make backfill a **bounded window sweep** (per-day/per-month chunks) so a 6-hour historical pull that dies at hour 5 doesn't restart at hour 0.
2. **Honor rate limits by construction** (`connector-incremental-with-backfill`): read `Retry-After`, use exponential backoff with a ceiling, and prefer cursor/keyset pagination over offset on a mutating table (offset shifts rows under you and skips/duplicates).
3. **Land output idempotently** (`ingest-idempotent-and-replayable`): the connector's destination write is `append_dedup`/upsert on the primary key, so a replayed batch is a no-op — replay-safety is independent of whether the run was incremental or backfill.
4. **Keep the connector dumb — land raw only** (`etl-elt-load-then-transform-in-warehouse`): no business logic in the connector; it lands verbatim and dbt owns the transform downstream.
5. **Decide the maintenance posture at design time** (`connector-document-the-handoff-at-design-time`): community-contribution (gold) / Matt-maintained fork (silver) / client-takes-over (bronze) is a *design* input, not an afterthought — and ship the runbook with it.

## Guardrails

- PII/PHI in transit (HRIS especially) routes through `ravenclaude-core/security-reviewer` — mandatory.
- `[verify-at-build]` Airbyte CDK class/sync-mode names drift across CDK versions — confirm against the current Python CDK reference before quoting them in code.
- If EdTech LMS, surface the connector-gap finding per house opinion #11 and flag the handoff to `edtech-partner-success` for the partner-success motion above the data layer.
