---
name: airbyte-cdk-authoring
description: "Author a custom Airbyte connector (low-code manifest.yaml vs Python CDK) — monotonic server-set cursor, checkpointed state, bounded-window backfill, Retry-After backoff, idempotent destination write, maintenance posture at design time. Used by connector-developer. NOT for configuring a vendor-shipped Airbyte/Fivetran connector (that's connector-configuration)."
---

# Skill: airbyte-cdk-authoring

> **Invoked by:** `connector-developer` (primary). `etl-pipeline-engineer` hands off here when the catalog has no connector.
>
> **When to invoke:** a source the iPaaS vendors don't ship a first-class connector for — the EdTech LMS gap (Canvas/Moodle/Schoology) is the canonical case. NOT when a vendor connector already exists (configure it via `connector-configuration` / `etl-pipeline-engineer`) and NOT for a small dimension table where full-refresh is cheaper than cursor bookkeeping.
>
> **Output:** connector design (cursor, streams, pagination, schema declaration, backfill path, rate-limit posture) + maintenance-posture field + handoff runbook. CDK class/sync-mode names are `[verify-at-build]` — confirm against the current Python CDK reference before quoting them in code.

The slash command `/data-platform:build-incremental-connector` is the same playbook on the user surface. This file is what spawned `connector-developer` auto-loads. Do not keep a third copy of these rules.

## Flow

1. **Exhaust the six alternatives first** (catalog connector, Fivetran, Hevo/Stitch/Estuary, Workato/Tray, Merge.dev, REST+cron). The tree lives in [`../../knowledge/ipaas-connector-landscape-2026.md`](../../knowledge/ipaas-connector-landscape-2026.md) and the agent's structured-output `alternatives_exhausted`. Custom CDK is last, not first. If EdTech LMS, also read [`../../knowledge/edtech-lms-connector-gap.md`](../../knowledge/edtech-lms-connector-gap.md).

2. **Low-code `manifest.yaml` vs full Python CDK.** Prefer low-code when the source is REST + one cursor + no exotic auth. Drop to Python when you need custom auth, nested streams, or a non-HTTP transport. `[verify-at-build]` against current CDK docs before naming classes.

3. **Incremental by cursor, with a separate backfill path** ([`connector-incremental-with-backfill`](../../best-practices/connector-incremental-with-backfill.md)): choose a **server-set, monotonic** cursor (`updated_at`/sequence — never the client clock, never a rewritable field). Checkpoint cursor state at a bounded interval so a crash resumes mid-stream. Make backfill a **bounded window sweep** (per-day/per-month chunks) so a 6-hour historical pull that dies at hour 5 doesn't restart at hour 0.

4. **Honor rate limits by construction:** read `Retry-After`, exponential backoff with a ceiling, prefer cursor/keyset pagination over offset on a mutating table (offset shifts rows and skips/duplicates).

5. **Declare schema; don't discover it as the contract.** Discovery is a convenience; the declared schema is what dbt tests against.

6. **Land output idempotently** ([`ingest-idempotent-and-replayable`](../../best-practices/ingest-idempotent-and-replayable.md)): destination write is `append_dedup`/upsert on the primary key, so a replayed batch is a no-op.

7. **Keep the connector dumb — land raw only** ([`etl-elt-load-then-transform-in-warehouse`](../../best-practices/etl-elt-load-then-transform-in-warehouse.md)). dbt owns the transform. Do not clone `analytics-engineering/incremental-model-patterns` here — that is warehouse modeling.

8. **Decide the maintenance posture at design time** ([`connector-document-the-handoff-at-design-time`](../../best-practices/connector-document-the-handoff-at-design-time.md)): community-contribution / Matt-maintained fork / client-takes-over is a *design* input. Ship the runbook with it.

9. **PII/PHI in transit (HRIS especially)** routes through `ravenclaude-core/security-reviewer` — mandatory.

## What this skill does NOT cover

- Configuring a *shipped* QBO/Stripe/Salesforce/… connector → `connector-configuration`
- dbt incremental models → `analytics-engineering` (do not clone)
- The Airbyte vs Fivetran vs n8n *choice* → `stack-selection` + `ipaas-connector-landscape-2026.md`

## References

- Command (same playbook, user-invoked): [`../../commands/build-incremental-connector.md`](../../commands/build-incremental-connector.md)
- Knowledge: [`../../knowledge/edtech-lms-connector-gap.md`](../../knowledge/edtech-lms-connector-gap.md)
- Knowledge: [`../../knowledge/ipaas-connector-landscape-2026.md`](../../knowledge/ipaas-connector-landscape-2026.md)
- Sibling (wrong file for this job): [`../connector-configuration/SKILL.md`](../connector-configuration/SKILL.md)
