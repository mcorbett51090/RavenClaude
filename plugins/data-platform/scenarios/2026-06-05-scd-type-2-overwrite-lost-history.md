---
scenario_id: 2026-06-05-scd-type-2-overwrite-lost-history
contributed_at: 2026-06-05
plugin: data-platform
product: dbt
product_version: "unknown"
scope: likely-general
tags: [scd, dimension, dbt, snapshot, history, type-2]
confidence: high
reviewed: false
---

## Problem

A B2B SaaS engagement built a `dim_customer` mart that overwrote each customer's plan tier, sales rep, and region on every run (a Type-1 dimension — current value only). Three months in, the client asked a "as-of" question the dashboard could not answer: **"what was MRR by plan tier at the start of last quarter?"** Because the dimension only held the *current* plan tier, every historical fact row joined to today's tier — so a customer who upgraded from Starter to Pro in May showed *all* of their Q1 revenue as Pro. The trend chart was silently wrong, and nobody noticed until the client cross-checked against their billing export.

## Context

- The mart was a plain `incremental`/`table` model that `MERGE`d on `customer_id` and overwrote the attribute columns — no history, no effective-dating.
- The fact tables (`fct_invoice`, `fct_usage`) carried only `customer_id` as the dimension FK, resolved to the dimension's *current* row at query time.
- The attributes that changed (plan tier, owner, region, segment) were exactly the ones the client sliced revenue by — so attribute history was load-bearing, not cosmetic.
- Constraint: the source system (the billing platform) did **not** retain a change history of its own — it exposed only the current state per customer, so "go re-pull the history from the source" was not available. If we didn't capture the change when we saw it, it was gone.

## Attempts

- Tried: a point-in-time correction — manually rebuilding the May tier change from a billing CSV the client happened to have. Outcome: fixed *that one* attribute for *that one* customer, but it didn't generalize, didn't capture future changes, and depended on the client having an export we couldn't count on. A patch, not a fix.
- Tried: converting `dim_customer` to a **Type-2 slowly-changing dimension** via a `dbt snapshot` keyed on `customer_id`, with `check` strategy over the volatile columns (plan tier, owner, region, segment), producing `dbt_valid_from` / `dbt_valid_to` and a surrogate key per version. The fact models were re-pointed to join on `customer_id` **AND** `fct.event_date BETWEEN dim.valid_from AND dim.valid_to` (the as-of join), so each fact row resolves to the dimension version that was current *when the event happened*. Outcome: as-of questions became answerable going forward; the snapshot captures every future change at the grain we observe it.
- Tried: guarding the new spine with dbt tests — `unique` on the surrogate key, a `not_null` on `valid_from`, and a singular test asserting **no overlapping validity windows per `customer_id`** (the classic SCD-2 bug: two "current" rows). Outcome: a regression in the snapshot logic now fails the build instead of double-counting.

## Resolution

The root cause was **modeling a history-bearing attribute as Type-1 (overwrite)** when the business sliced metrics by that attribute over time. The fix was a Type-2 SCD via `dbt snapshot` with an as-of (`BETWEEN valid_from AND valid_to`) join from the facts, plus the no-overlapping-windows test. Crucially, **the lost Q1 history could not be fully reconstructed** — once an overwrite has happened and the source keeps no history, that change is gone. That is the real lesson: the cost of getting the dimension type wrong is paid in *unrecoverable* history, so the decision has to be made before the first run, not after the client asks an as-of question.

**Action for the next consultant hitting this pattern:** before you build a dimension, ask the client **"will you ever need to see a metric as-of a past date, sliced by an attribute that changes?"** If yes — and especially if the source keeps no change history of its own — model it Type-2 from day one (`dbt snapshot`, effective-dated, as-of join, no-overlap test). A Type-1 overwrite is correct only when nobody will ever ask the as-of question. Don't default to Type-1 because it's the simpler model; default to asking the question. Traverse the `## Decision Tree: dbt materialization for a support-ticket mart` and the dimension-history tree in [`../knowledge/data-platform-decision-trees.md`](../knowledge/data-platform-decision-trees.md) before choosing.

**Sources (retrieved 2026-06-05):** dbt snapshots / SCD Type-2 mechanics (`check` strategy, `dbt_valid_from`/`dbt_valid_to`): https://docs.getdbt.com/docs/build/snapshots — treat version-specific snapshot-config behavior (e.g. the snapshot YAML-config migration) as `[verify-at-use]`. Canonical rules this corroborates — [`../best-practices/dbt-stage-then-mart-never-skip-the-layer.md`](../best-practices/dbt-stage-then-mart-never-skip-the-layer.md), [`../best-practices/dbt-test-the-floor-unique-not-null-relationships.md`](../best-practices/dbt-test-the-floor-unique-not-null-relationships.md).
