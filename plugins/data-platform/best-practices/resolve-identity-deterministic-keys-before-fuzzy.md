# Resolve cross-system identity with deterministic keys first — fuzzy match is the last resort, not the first

**Status:** Absolute rule — every metric built on a wrong join is wrong, silently. Identity resolution must be explicit, auditable, and lowest-confidence-last. A name-only match that auto-publishes to a dashboard is an accuracy liability.

**Domain:** Cross-system data modeling / master data management

**Applies to:** `data-platform`

**Use when:** stitching the same real-world entity — typically a customer account — across two or more source systems (e.g., Salesforce Account → Planhat company → Intercom company → Slack channel) into one conformed spine in the warehouse.

---

## Why this exists

The identity-resolution problem is invisible until a metric is wrong. A Salesforce Account and a Planhat company that look like the same customer might match on name ("Acme Corp" vs. "Acme Corporation"), might share a domain, or might carry a deterministic external ID that makes the match exact and costless. Reaching for a normalized-name fuzzy join first — because it is easy to code — skips the high-confidence options and introduces matches that silently corrupt every downstream metric built on them. The pattern that breaks: an account is matched on name, the join is 90% right, the health scores for the 10% wrong accounts are garbage, and nobody notices until a CSM asks "why is this account showing Red — I just closed them."

The correct precedence: exhausting deterministic options takes a few minutes of investigation; fuzzy matching a name takes a few minutes to code but weeks to undo when a bad match propagates through a mart.

## The resolution precedence ladder

Apply in order. Stop at the first level that resolves the record. Never skip to a lower-confidence level because it is faster to implement.

| Priority | Method | Confidence | When to use | Action on match |
|---|---|---|---|---|
| **1 — Deterministic** | External ID / cross-reference field set by integration (e.g., Planhat `externalId` = Salesforce Account ID; Intercom `company_id` = Salesforce Account ID) | **Exact** | When systems have been configured to exchange IDs | Auto-resolve; record `match_method = 'external_id'` |
| **2 — Email domain** | Derive primary domain per account; join on normalized domain (strip `www.`, lowercase, strip TLD suffixes for known-multi-domain companies) | **Strong, not perfect** | When external IDs are absent; multi-domain accounts need manual annotation | Auto-resolve when domain is unique; flag shared/generic domains for review |
| **3 — Normalized name** | Strip legal suffixes (`Inc`, `LLC`, `Corp`, `Ltd`), lowercase, collapse whitespace, Levenshtein distance ≤ threshold | **Weak — human review required** | Only after 1 and 2 are exhausted | **Never auto-resolve.** Queue to stewardship review. Mark `confidence = 'low'`. |

**Slack has no native account concept** — it requires an entirely separate mechanism: a `slack_channel_account_map` seed table (manually seeded, weekly-diffed), not the three-step ladder above.

## The `bridge_account_xref` table

Every resolution — at any confidence level — is recorded in a bridge table. No silent drops, no undocumented joins.

```sql
-- DDL for the cross-reference bridge
create or replace table transform.bridge_account_xref (
    source          varchar not null,        -- 'planhat' | 'intercom' | 'slack'
    source_id       varchar not null,        -- the source system's native ID
    account_key     varchar,                 -- FK to dim_account.account_key; NULL = unresolved
    match_method    varchar not null,        -- 'external_id' | 'email_domain' | 'name_fuzzy' | 'manual' | 'unresolved'
    confidence      varchar not null,        -- 'high' | 'medium' | 'low' | 'unresolved'
    reviewed_by     varchar,                 -- email of reviewer for low-confidence matches
    reviewed_at     timestamp,
    created_at      timestamp default current_timestamp,
    updated_at      timestamp default current_timestamp,
    primary key (source, source_id)
);
```

**Seed the high-confidence rows first.** Run the name-fuzzy candidates through the stewardship review before inserting them with a non-null `account_key`.

## Quarantine, never drop

An unresolved record gets `account_key = NULL` and `match_method = 'unresolved'` in `bridge_account_xref`. It is retained, not silently dropped. A `LEFT JOIN` through the bridge propagates the null FK; downstream models treat null-keyed records as "unknown account" and exclude them from aggregated metrics with an explicit `WHERE account_key IS NOT NULL`. This makes the exclusion visible and auditable.

**Never silently drop unresolved records.** A silent drop means an account with no match has zero support tickets, zero health signals — which looks like a healthy account rather than a data gap.

## Daily `resolution_audit` model

A dbt model that runs every day and alerts when resolution quality degrades.

```sql
-- models/marts/resolution_audit.sql
-- Fails (warn) when >5% of any source's companies are unresolved.
-- Fails (warn) when any Slack channel has been unmapped for >7 days.
with summary as (
    select
        source,
        count(*) as total_records,
        sum(case when account_key is null then 1 else 0 end) as unresolved_count,
        round(100.0 * sum(case when account_key is null then 1 else 0 end) / count(*), 2)
            as unresolved_pct
    from {{ ref('bridge_account_xref') }}
    group by source
),
slack_unmapped as (
    select channel_id, added_at
    from {{ ref('seed_slack_channel_account_map') }}
    where account_key is null
      and added_at < current_date - 7
)
select 'unresolved_pct_breach' as alert_type, source, unresolved_pct as value
from summary
where unresolved_pct > 5

union all

select 'slack_channel_unmapped_gt_7d', channel_id, datediff('day', added_at, current_date)
from slack_unmapped
```

```yaml
# _models.yml severity — warn so the pipeline runs but alert fires
models:
  - name: resolution_audit
    tests:
      - dbt_utils.expression_is_true:
          expression: "count(*) = 0"
          severity: warn
```

Wire the `warn` severity to a Slack alert channel — a degrading match rate is a correctness risk, not an outage.

## Stewardship review surface

Low-confidence (name-fuzzy) matches queue to a stewardship view in the BI tool before they are published to any metric. The stewardship view surfaces:

- `source`, `source_id`, source-system name
- Candidate `account_key` and the account name from `dim_account`
- `confidence`, `match_method`, the similarity score that produced the candidate
- An approval / reject action (write back to `bridge_account_xref.reviewed_by` + `reviewed_at`)

**No metric published off a name-only match without a review record.** In dbt, enforce this:

```sql
-- In mart_cs_health or equivalent, exclude unreviewed low-confidence joins:
where xref.match_method != 'name_fuzzy'
   or (xref.match_method = 'name_fuzzy' and xref.reviewed_by is not null)
```

## Manual top-N review before launch

Before Phase 1 launch, manually audit the top ~20 accounts by ARR. For each: confirm the correct Planhat company, Intercom company, and Slack channel are mapped. Document the match evidence. This catches systematic resolution errors before they compound through a quarter of health-score data.

## Do

- Investigate whether the source systems have been configured to share IDs (e.g., Planhat `externalId` field, Intercom Salesforce integration) **before writing any matching code** — this takes 30 minutes and can eliminate 90% of the resolution problem.
- Seed `bridge_account_xref` for every source system, even systems where resolution is 100% deterministic — the table is the audit trail.
- Make the quarantine count visible in the BI stewardship page at all times. An analyst who never sees unresolved counts loses awareness of the problem.
- Treat a rising unresolved percentage as a data-quality incident: someone deleted or renamed an account in the source system without updating the bridge.

## Don't

- Auto-publish a metric for a record matched on normalized name without a human review record.
- Drop records that don't resolve — null FK, retain, alert, review.
- Match on `company_name ILIKE '%acme%'` as the join condition in a dbt model — this bypasses the bridge entirely and produces invisible duplicates.
- Reuse email-domain matching for known-shared-domain companies (consulting firms, holding companies) without a domain-exclusion list.
- Skip the resolution audit model because "the data looks clean" — it only looks clean until it doesn't.

## Edge cases

- **Multi-domain accounts** — one Salesforce Account maps to multiple email domains (e.g., a company that acquired a smaller one). Add a `dim_account_domains(account_key, domain)` table and join from it.
- **Shared generic domains** (`gmail.com`, `outlook.com`) — exclude from email-domain matching; send directly to manual review.
- **Source system record splits / merges** — a Planhat company split into two after an acquisition. The bridge will carry the old mapping until manually updated; the resolution audit will not catch this automatically. Consider a quarterly bridge-integrity review for large accounts.
- **Slack → account** — the naming-convention script is not identity resolution in the three-step sense; it is a best-effort proposal surface. The human confirmation step is not optional.

## See also

- [`./ingest-idempotent-and-replayable.md`](./ingest-idempotent-and-replayable.md) — raw data must land before resolution can run; MERGE-on-key discipline applies to the bridge too
- [`../knowledge/planhat-integration.md`](../knowledge/planhat-integration.md) — Planhat `externalId` is the single most important deterministic key in the CS-health build
- [`../knowledge/intercom-integration.md`](../knowledge/intercom-integration.md) — Intercom `company_id` / external field as the Salesforce ID hook
- [`../knowledge/slack-as-data-source.md`](../knowledge/slack-as-data-source.md) — the `slack_channel_account_map` seed-table pattern
- [`../skills/cross-system-identity-resolution/SKILL.md`](../skills/cross-system-identity-resolution/SKILL.md) — the operationalized step-by-step procedure for this best practice
- [`../skills/data-quality-tests/SKILL.md`](../skills/data-quality-tests/SKILL.md) — the `resolution_audit` model is a cross-source reconciliation test in disguise

## Provenance

Distilled from `docs/analytics-dashboard-plan.md` §3.3 (identity resolution as "the #1 technical risk — both panels agreed"), §6 risk #2 ("Identity resolution wrong → every metric wrong, silently"), and the tie-breaker's guardrails. The `bridge_account_xref` schema and the >5% unresolved alert threshold come directly from the plan. Name-fuzzy-last discipline is standard master-data-management practice; the human-review gate on name-only matches is non-negotiable given the downstream impact on health scores and churn tiers.

---

_Last reviewed: 2026-06-03 by `claude`_
