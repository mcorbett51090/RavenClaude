---
name: cross-system-identity-resolution
description: "Use when stitching the same real-world entity — a customer account — across multiple source systems into one conformed spine; e.g. Salesforce + Planhat + Intercom + Slack. Operationalizes the deterministic-keys-before-fuzzy best practice: inventory candidate keys, build the precedence ladder, construct bridge_account_xref with confidence + match_method, quarantine unresolved records, run resolution_audit, and gate on stewardship review for low-confidence matches."
---

# Skill: cross-system-identity-resolution

> **Invoked by:** `etl-pipeline-engineer` (owns the pipeline correctness) + `ravenclaude-core/architect` (owns the cross-system data model). Also consulted by `dashboard-builder` when a mart metric seems wrong and the root cause may be a resolution error.
>
> **When to invoke:** Phase 0 of any multi-source build; whenever a new source system is added to an existing conformed spine; after a "the numbers don't match" incident where the suspected cause is a bad cross-system join.
>
> **Output:** a populated `bridge_account_xref` table seeded with high-confidence rows, a `resolution_audit` dbt model running on schedule, a stewardship surface for low-confidence candidates, and dbt tests guarding the join spine.

## The discipline (the floor, not the ceiling)

**Every metric built on a wrong join is wrong, silently.** Identity resolution is the #1 technical risk in a multi-source analytics build — both expert panels in the CS-health build plan agreed on this independently. The correct shape: exhaust deterministic options first (30 minutes of investigation), fall back to domain matching (imperfect but checkable), and treat name matching as a human-review queue, never an auto-trusted join.

Two-line rule:
1. **No match without a record** — every resolved and every unresolved record gets a row in `bridge_account_xref`
2. **No metric off a name-only match without a review record** — `reviewed_by IS NOT NULL` is a precondition for publishing

## Step 1 — Inventory candidate keys per source system

Before writing any matching code, audit each source system for cross-reference fields. This takes 30 minutes and often eliminates 90% of the resolution problem.

| Source system | Candidate key to check | How to check |
|---|---|---|
| **Planhat** | `externalId` on Company — designed to hold the Salesforce Account ID when the SFDC↔Planhat sync is configured | `GET /companies` for a sample; inspect `externalId` field |
| **Intercom** | `company_id` on Company — populated with Salesforce Account ID when Intercom's Salesforce integration is on | `GET /companies` for a sample; inspect `company_id` |
| **Slack** | No native account concept — see Step 4 | N/A for the ladder; use seed table |
| **HubSpot** | `hs_object_id`, or `salesforce_account_id` custom property if SFDC sync is on | Check HubSpot company properties |
| **Stripe** | `metadata.salesforce_account_id` if set by the billing flow | Check Stripe customer metadata |

**Document what you find.** Record in the Phase 0 notes: which systems have deterministic keys populated, which do not, and what action was taken (configured the sync, escalated for ops setup, proceeded to domain matching).

## Step 2 — Build the resolution precedence ladder

Apply in order. Stop at the first level that resolves the record. Never skip to a lower-confidence level because it is faster to code.

| Priority | Method | Confidence | Auto-resolve? | `match_method` value |
|---|---|---|---|---|
| **1 — Deterministic** | External ID / cross-reference field set by a configured integration | Exact | Yes | `'external_id'` |
| **2 — Email domain** | Derive primary domain per account; join on normalized domain (lowercase, strip `www.`, strip known TLD suffixes) | Strong, not perfect | Yes — unless domain is shared/generic | `'email_domain'` |
| **3 — Normalized name** | Strip legal suffixes, lowercase, collapse whitespace, Levenshtein distance ≤ threshold | Weak | **No — human review required** | `'name_fuzzy'` |
| **Unresolved** | No match found at any level | None | N/A | `'unresolved'` |

**Email domain caveats:** exclude known shared/generic domains (`gmail.com`, `outlook.com`, `yahoo.com`). Maintain a `dim_account_domains(account_key, domain)` table for accounts with multiple legitimate domains (post-acquisition, holding companies). Domain matching on a large consulting firm's domain will produce false positives.

**Name fuzzy caveats:** use normalized Levenshtein (or trigram similarity), not `ILIKE '%acme%'`. Set a threshold (e.g., similarity ≥ 0.85) and never auto-accept — every name-fuzzy candidate goes to the stewardship queue regardless of similarity score.

## Step 3 — Construct `bridge_account_xref`

Every resolution — at any confidence level — is recorded in the bridge table. Unresolved records get a null `account_key` and are retained, never dropped.

```sql
-- transform/models/staging/bridge_account_xref.sql (or infra DDL)
create or replace table transform.bridge_account_xref (
    source          varchar not null,        -- 'planhat' | 'intercom' | 'slack' | 'hubspot' | 'stripe'
    source_id       varchar not null,        -- the source system's native primary ID
    account_key     varchar,                 -- FK to dim_account.account_key; NULL = unresolved
    match_method    varchar not null,        -- 'external_id' | 'email_domain' | 'name_fuzzy' | 'manual' | 'unresolved'
    confidence      varchar not null,        -- 'high' | 'medium' | 'low' | 'unresolved'
    similarity_score float,                  -- for name_fuzzy matches; null otherwise
    reviewed_by     varchar,                 -- email of reviewer; required before name_fuzzy used in metrics
    reviewed_at     timestamp,
    created_at      timestamp default current_timestamp,
    updated_at      timestamp default current_timestamp,
    primary key (source, source_id)
);
```

**Seeding order:**
1. Run the deterministic pass first — insert all `external_id` rows with `confidence = 'high'`
2. Run the domain pass for the remaining unresolved records — insert with `confidence = 'medium'`; flag shared/generic domains to stewardship queue
3. Run the name-fuzzy pass for any still-unresolved records — insert with `confidence = 'low'`, `account_key = NULL` until reviewed
4. Insert remaining unresolved records explicitly with `match_method = 'unresolved'`

```sql
-- Example: deterministic pass for Planhat
insert into transform.bridge_account_xref (source, source_id, account_key, match_method, confidence)
select
    'planhat',
    p.planhat_id,
    a.account_key,
    'external_id',
    'high'
from stg_planhat__companies p
join dim_account a
    on p.external_id = a.sfdc_account_id   -- deterministic: Planhat externalId = Salesforce Account ID
where p.external_id is not null
  and a.sfdc_account_id is not null
on conflict (source, source_id) do nothing;   -- idempotent; don't overwrite existing rows

-- Unresolved records (those not matched above)
insert into transform.bridge_account_xref (source, source_id, account_key, match_method, confidence)
select 'planhat', p.planhat_id, null, 'unresolved', 'unresolved'
from stg_planhat__companies p
where p.planhat_id not in (
    select source_id from transform.bridge_account_xref where source = 'planhat'
)
on conflict (source, source_id) do nothing;
```

## Step 4 — Slack channel → account mapping (separate mechanism)

Slack has no native account concept; the three-step ladder does not apply. Use the seed table mechanism instead.

See [`../../knowledge/slack-as-data-source.md`](../../knowledge/slack-as-data-source.md) for the full `slack_channel_account_map` DDL, seeding process, and weekly diff script.

The key discipline: the Slack → account mapping is **always human-confirmed**. The diff script proposes; a human approves. Never auto-insert a channel-to-account mapping from naming-convention heuristics alone.

## Step 5 — Quarantine and null-FK propagation

Unresolved records (`account_key = NULL` in the bridge) are **retained, never dropped**. Downstream models use an explicit `WHERE account_key IS NOT NULL` to exclude them from aggregated metrics. This makes the exclusion visible and auditable.

```sql
-- In mart_cs_health or equivalent: exclude unresolved AND unreviewed low-confidence joins
left join transform.bridge_account_xref xref
    on xref.source = 'planhat'
    and xref.source_id = p.planhat_id
where xref.account_key is not null               -- exclude unresolved
  and (
    xref.match_method != 'name_fuzzy'            -- auto-trusted methods
    or xref.reviewed_by is not null              -- OR name-fuzzy with human review
  )
```

A `null` FK in the mart signals "source record exists but account is unknown" — which is a data quality alert, not a missing record. A silent drop would make an unmatched account look like a healthy account with zero signals.

## Step 6 — `resolution_audit` dbt model + alert

A dbt model that runs daily and alerts when resolution quality degrades. The >5% unresolved threshold comes directly from the build plan's guardrails.

```sql
-- models/marts/resolution_audit.sql
with summary as (
    select
        source,
        count(*) as total_records,
        sum(case when account_key is null then 1 else 0 end) as unresolved_count,
        round(100.0 * sum(case when account_key is null then 1 else 0 end) / count(*), 2)
            as unresolved_pct,
        sum(case when match_method = 'name_fuzzy' and reviewed_by is null then 1 else 0 end)
            as unreviewed_fuzzy_count
    from {{ ref('bridge_account_xref') }}
    group by source
),
slack_unmapped as (
    select channel_id, added_at
    from {{ ref('seed_slack_channel_account_map') }}
    where account_key is null
      and added_at < current_date - 7
)
select 'unresolved_pct_breach' as alert_type, source, unresolved_pct as value, null as channel_id
from summary
where unresolved_pct > 5

union all

select 'unreviewed_fuzzy_match' as alert_type, source, unreviewed_fuzzy_count, null
from summary
where unreviewed_fuzzy_count > 0

union all

select 'slack_channel_unmapped_gt_7d', 'slack', datediff('day', added_at, current_date), channel_id
from slack_unmapped
```

```yaml
# _models.yml — warn severity so the pipeline continues but alert fires
models:
  - name: resolution_audit
    tests:
      - dbt_utils.expression_is_true:
          expression: "count(*) = 0"
          severity: warn
          config:
            error_if: ">= 1"
```

Wire the `warn` severity to a Slack/email alert channel. A rising unresolved percentage or an accumulating unreviewed-fuzzy queue are correctness risks, not outages — they need visibility, not a wake-up page.

## Step 7 — Stewardship review surface

Low-confidence (name-fuzzy) match candidates queue to a stewardship view in the BI tool before they are published to any metric. The minimum viable stewardship surface:

| Column to surface | Purpose |
|---|---|
| `source`, `source_id` | Identify the source record needing review |
| Source-system display name (e.g., `planhat_company_name`) | Human-readable context |
| Candidate `account_key` and `dim_account.account_name` | The proposed match |
| `match_method`, `confidence`, `similarity_score` | Basis for the proposal |
| `reviewed_by`, `reviewed_at` | Approval status |
| Approve / Reject action | Write back to `bridge_account_xref` |

**The approval action writes `reviewed_by` and `reviewed_at` to the bridge.** Until that write, the name-fuzzy record's `account_key` is excluded from all mart metrics by the WHERE clause in Step 5.

## Step 8 — Manual top-N review before launch

Before Phase 1 launch: manually audit the top ~20 accounts by ARR. For each account:

1. Confirm the correct Planhat company is mapped
2. Confirm the correct Intercom company is mapped
3. Confirm the correct Slack channel(s) are in `slack_channel_account_map`
4. Review the `match_method` and `confidence` for each mapping
5. Document the match evidence in a "pre-launch resolution sign-off" doc

This catches systematic resolution errors before they compound through a quarter of health-score data. The CS team typically knows their top accounts well; this review takes 30–60 minutes and is non-negotiable.

## dbt tests that guard the join spine

Add these to the `bridge_account_xref` model's `_models.yml`:

```yaml
models:
  - name: bridge_account_xref
    columns:
      - name: source
        tests:
          - not_null
          - accepted_values:
              values: ['planhat', 'intercom', 'slack', 'hubspot', 'stripe']
      - name: source_id
        tests:
          - not_null
      - name: match_method
        tests:
          - not_null
          - accepted_values:
              values: ['external_id', 'email_domain', 'name_fuzzy', 'manual', 'unresolved']
      - name: confidence
        tests:
          - not_null
          - accepted_values:
              values: ['high', 'medium', 'low', 'unresolved']
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns: [source, source_id]
```

Also add a singular test asserting no name-fuzzy row with `account_key IS NOT NULL` and `reviewed_by IS NULL` reaches the mart layer (the WHERE clause in Step 5 is the runtime gate; this test catches a missing WHERE clause):

```sql
-- tests/assert_no_unreviewed_fuzzy_in_mart.sql
-- Any name-fuzzy join without a reviewer is an accuracy risk; this catches a missing WHERE clause.
select b.source, b.source_id, b.account_key
from {{ ref('bridge_account_xref') }} b
join {{ ref('fct_account_health_snapshot') }} f on f.account_key = b.account_key
where b.match_method = 'name_fuzzy'
  and b.reviewed_by is null
{{ config(severity='error') }}
```

## Anti-patterns this skill flags

- Writing a `JOIN ON LOWER(TRIM(company_name)) = LOWER(TRIM(account_name))` directly in a dbt model — bypasses the bridge entirely; produces invisible duplicates with no audit trail
- Auto-publishing a metric for a record matched on normalized name without a human review record
- Dropping records that don't resolve — null FK, retain, alert, review
- Treating a rising unresolved percentage as "normal" and not investigating — it means source records exist that are invisible to every CS health metric
- Skipping the Phase 0 candidate-key inventory and jumping straight to fuzzy matching — the highest-value 30-minute investment in the whole build

## See also

- Best practice: [`../../best-practices/resolve-identity-deterministic-keys-before-fuzzy.md`](../../best-practices/resolve-identity-deterministic-keys-before-fuzzy.md) — the named rule this skill operationalizes
- Skill: [`../data-quality-tests/SKILL.md`](../data-quality-tests/SKILL.md) — the `resolution_audit` model is a cross-source reconciliation test in disguise; wire it to the same alert infrastructure
- Skill: [`../dbt-project-scaffolding/SKILL.md`](../dbt-project-scaffolding/SKILL.md) — the dbt project layer that hosts the bridge model and resolution audit
- Knowledge: [`../../knowledge/planhat-integration.md`](../../knowledge/planhat-integration.md) — Planhat `externalId` as the single most important deterministic key for the CS-health build
- Knowledge: [`../../knowledge/intercom-integration.md`](../../knowledge/intercom-integration.md) — Intercom `company_id` as the Salesforce ID hook
- Knowledge: [`../../knowledge/slack-as-data-source.md`](../../knowledge/slack-as-data-source.md) — the `slack_channel_account_map` seed-table pattern; the Slack → account mechanism that supplements the three-step ladder
- Knowledge: [`../../knowledge/salesforce-integration.md`](../../knowledge/salesforce-integration.md) — the Salesforce Account ID is the master key; all resolution ladders converge on it
