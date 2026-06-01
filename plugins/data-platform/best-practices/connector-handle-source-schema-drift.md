# Handle source schema drift on purpose — detect, classify, then adapt or fail

**Status:** Absolute rule — a pipeline that ingests a changed source shape without a defined drift policy is silently corrupting the warehouse; the only defensible postures are *detect-and-adapt* or *detect-and-halt*, never *don't-detect*.

**Domain:** ELT / connectors

**Applies to:** `data-platform`

---

## Why this exists

SaaS sources change their schema without warning — a vendor renames a field, drops a column, widens a type, splits one object into two. A connector that maps source→warehouse with no drift policy does one of two silently-wrong things: it **drops** the new/renamed column (the dashboard quietly goes stale on that metric), or it **coerces** a changed type and writes garbage (a `decimal` that became a `string`, a date format that flipped). Either way the failure surfaces weeks later as a client asking "why is this number wrong?" — the most expensive way to find a pipeline defect. The handoff'd pipeline (`connector-document-the-handoff-at-design-time`) makes this worse: the client now owns a pipeline that can break invisibly. This rule makes drift a **first-class, classified event** with a decided response, not an accident.

## How to apply

**1. Detect drift at ingestion.** The connector must compare the source's current shape against the last-known schema on every sync, not assume it's static. Airbyte/Fivetran surface this as schema-change detection; a custom connector must implement it (capture the source schema in state, diff on each run).

**2. Classify the change — the response depends on the kind:**

| Drift kind | Default response |
|---|---|
| **New column** (additive) | Auto-propagate to a nullable column; safe — no existing data invalidated. Surface in the sync log so the dbt layer can adopt it. |
| **Dropped column** | **Halt if load-bearing** (a mart/dashboard depends on it); warn-and-continue only if provably unused. Never silently null it out. |
| **Type widened** (int→bigint, varchar grow) | Auto-adapt; lossless. |
| **Type changed/narrowed** (decimal→string, date format flip) | **Halt** — coercion loses or corrupts data. Quarantine to a raw/`_airbyte_raw`-style landing column; do not cast into the typed model until a human decides the mapping. |
| **Renamed column** | Treated as drop+add by most connectors — **halt** and map explicitly; an auto drop+add loses history on the old name. |
| **Primary-key / cursor field change** | **Halt always** — breaks incremental state (`connector-incremental-with-backfill`) and dedup; requires a re-plan. |

**3. Land raw, type in the model.** Ingest source data into a raw/landing layer with permissive types (the ELT "EL"); enforce the contract in the dbt **staging** layer (`dbt-stage-then-mart-never-skip-the-layer`). Drift then breaks a *test*, not the dashboard — `dbt-test-the-floor-unique-not-null-relationships` and the source `freshness` + column tests are the tripwire.

**4. Decide fail-open vs fail-closed by criticality.** A revenue/financial fact pipeline fails **closed** (halt, alert, no partial write). A low-stakes enrichment source can fail **open** (warn, continue on last-good). State which posture each pipeline takes in the handoff runbook.

**Do:** diff the source schema every run; classify the change; halt on type-narrowing / renames / key changes; auto-adopt purely-additive changes; land raw and enforce types in dbt staging; write the per-pipeline fail-open/closed posture into the runbook.

**Don't:** let a connector silently drop or coerce columns; cast a changed type straight into the typed model; treat "the sync succeeded" as "the data is correct" (a sync can succeed *and* have dropped a column); ship a handoff'd pipeline without a documented drift response.

## Edge cases / when the rule does NOT apply

A genuinely **schema-on-read** target (raw JSON landed and parsed downstream, no typed contract) defers drift to the read layer — but then the dbt/staging layer *is* where this rule applies, just shifted one hop. A **one-shot backfill / migration** (not a recurring pipeline) has no future drift to manage — but if it becomes recurring, it inherits the rule. Sources you fully control (your own app's DB via CDC) have drift coupled to your own deploys, so a schema migration there is a planned event, not external drift — still detect it, but the response is "coordinate with the deploy," not "halt and investigate."

## See also

- [`./connector-incremental-with-backfill.md`](./connector-incremental-with-backfill.md) — cursor/PK changes break incremental state; this rule halts on them
- [`./dbt-stage-then-mart-never-skip-the-layer.md`](./dbt-stage-then-mart-never-skip-the-layer.md) · [`./dbt-test-the-floor-unique-not-null-relationships.md`](./dbt-test-the-floor-unique-not-null-relationships.md) — the staging contract + tests that turn drift into a caught test failure
- [`./connector-document-the-handoff-at-design-time.md`](./connector-document-the-handoff-at-design-time.md) — the runbook where each pipeline's fail-open/closed posture is recorded
- [`../knowledge/data-platform-decision-trees.md`](../knowledge/data-platform-decision-trees.md) — the **pipeline-failure-recovery** tree (drift is one of its failure classes)
- [`../skills/data-quality-tests/SKILL.md`](../skills/data-quality-tests/SKILL.md) — the test taxonomy + row-count-drift bands that detect the downstream symptom

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01). Panel 3 verdict: `data-platform` had four connector-hygiene BPs (handoff, incremental, webhooks, pricing) but none for **source schema drift** — the single most common way a handed-off SaaS pipeline breaks silently. (The companion `pipeline-failure-recovery` decision tree, which routes drift alongside auth/rate-limit/data-quality failures, ships in the same campaign batch.) Grounded in this plugin's `data-quality-tests` skill, the dbt staging-contract BPs, and the `etl-pipeline-engineer` agent.

---

_Last reviewed: 2026-06-01 by `claude`_
