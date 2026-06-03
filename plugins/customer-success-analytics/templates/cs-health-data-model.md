# Reference Data Model — CS Health (template)

> **Use for:** the conformed warehouse data model behind a CS-health / churn-risk dashboard. This is the **domain-layer contract** the `cs-analytics-architect` hands to `data-platform` to build. It defines the entities, grain, and the transparent rule-based tier — not the pipeline that lands them (that is `data-platform`'s).
>
> **Domain-neutral.** Source systems are named by *role* (CRM, CS platform, support tool, collaboration tool), not by a specific vendor. Swap in the actual systems for an engagement. Consistent with the unified-CS-analytics build plan §3.1-3.2.
>
> **How to use:** copy the schema sketches into the dbt mart layer, fill grain/columns for the engagement, then hand to `data-platform/etl-pipeline-engineer` (pipeline) + `database-setup-guide` (warehouse + identity resolution) + `dashboard-builder` (BI surface).

---

## The shape at a glance

```
CRM ─────────┐
CS platform ─┼─▶  (data-platform lands + resolves)  ─▶  dim_account  ◀── join spine, master key = CRM Account ID
support ─────┤                                              │
collab ──────┘                                              ├─▶  fct_account_health_snapshot   (daily, append-only)
                                                            ├─▶  fct_opportunities             (renewals / expansions)
                                                            ├─▶  fct_support_conversations
                                                            ├─▶  fct_nps_responses             (verbatim = PII, masked)
                                                            └─▶  fct_collaboration_signal      (DERIVED only, no raw text)
```

Everything resolves to **one master key** — the CRM Account ID. No fact joins to anything but the conformed `dim_account` spine.

---

## 1. `dim_account` — the join spine

One row per real customer company. Built **before** any fact.

```sql
-- dim_account : conformed account dimension (the join spine)
account_key          surrogate key (warehouse-generated)
crm_account_id       MASTER KEY  -- e.g. Salesforce Account ID; everything resolves to this
account_name
account_domain       used for fuzzy resolution upstream
arr                  from CRM
segment              SMB / Mid-Market / Enterprise (domain-neutral buckets)
csm_owner_id
renewal_date
csp_company_id       resolved FK -> CS platform   (nullable; quarantine if unresolved)
support_company_id   resolved FK -> support tool  (nullable; quarantine if unresolved)
collab_channel_ids   resolved FK[] -> collaboration tool (one account -> many channels)
created_at
updated_at
```

> **Identity-resolution note (read this).** The resolution of `csp_company_id`, `support_company_id`, and `collab_channel_ids` to the master `crm_account_id` is **owned by `data-platform`, not this layer.** This model *consumes* the resolved spine and the cross-reference table; it never builds the matcher. Precedence (highest confidence first): (1) deterministic cross-reference fields if the source systems already store the CRM Account ID; (2) email-domain match; (3) normalized-name match — **last resort, human-reviewed, never auto-trusted.** Unresolved records are **quarantined explicitly (null FK), never silently dropped.** See `data-platform`'s identity-resolution best-practice and the `bridge_account_xref` + `resolution_audit` models below.

---

## 2. `fct_account_health_snapshot` — the daily health fact

**One row per account per day. APPEND-ONLY, never deleted** — the history is the asset; trend (the strongest signal) is only reconstructable from it. **Nulls where source data is absent — explicit, never silently zero.**

```sql
-- fct_account_health_snapshot : daily account-health grain
account_key                FK -> dim_account
snapshot_date

-- ANCHOR (pulled as-is from the CS platform, not recomputed)
csp_health_score                       -- the native CSP score; the phase-1 anchor

-- DERIVED TRENDS (direction beats absolute level)            ★ churn-leading
health_score_trend_7d                  ★
health_score_trend_30d                 ★
usage_trend_30d / _60d / _90d          ★  -- slope, not level

-- USAGE / ADOPTION
product_active_users_7d
feature_adoption_pct

-- SUPPORT (from support tool)
open_support_tickets
p1_p2_rate_30d                         ★  -- rate matters more than raw volume
median_first_response_hrs
support_load                               -- additive, individually-visible sub-indicator

-- SENTIMENT
nps_score
nps_response_date                          -- recency matters; stale NPS is noise

-- COLLABORATION (derived signals only)
collab_message_volume_7d
collab_escalation_signal_7d            ★  -- escalation-keyword density / dead-channel
collab_sentiment_7d
collab_escalation_signal                   -- additive, individually-visible sub-indicator

-- RENEWAL CONTEXT (gates urgency; not risk on its own)
days_to_renewal                            -- context: proximity is a GATE, not a risk term
renewal_stage                              -- from CRM

-- CSM CADENCE
open_tasks_count
overdue_tasks_count

-- THE OUTPUT (rule-based, transparent, explainable)
churn_risk_tier                            -- 'Green' | 'Yellow' | 'Red'
churn_risk_drivers                         -- JSON: the 2-3 signals that drove the tier (see §7)
computed_at
```

---

## 3. `fct_opportunities` — renewals & expansions

```sql
-- fct_opportunities : CRM renewals + expansions
opportunity_key
account_key            FK -> dim_account
opportunity_type       'renewal' | 'expansion'
stage
amount
arr_impact
close_date
created_at / updated_at
```

> A `Closed-Lost` renewal opp is a **lagging** signal — surface it as dashboard context, never as a risk-tier *input* (by then the prediction window has closed).

---

## 4. Signal facts — support, NPS, collaboration

```sql
-- fct_support_conversations : from the support tool
conversation_key, account_key, created_at, resolved_at,
priority, tags, csat, first_response_at

-- fct_nps_responses : from the CS platform
nps_response_key, account_key, score (0-10), responded_at,
verbatim   -- PII: MASK at the warehouse layer; never expose raw in the BI surface

-- fct_collaboration_signal : DERIVED ONLY -- never raw message bodies
collab_signal_key, account_key, channel_id, signal_date,
msg_count, escalation_hits, mention_count, sentiment_score
-- the extractor computes these in-memory and writes ONLY the metrics; raw text never lands.
```

---

## 5. Identity-resolution support tables (built by data-platform; this model depends on them)

```sql
-- bridge_account_xref : every resolved match, with provenance
source            'crm' | 'csp' | 'support' | 'collab'
source_id
account_key       FK -> dim_account
match_method      'deterministic-xref' | 'email-domain' | 'name-normalized'
confidence        0.0 - 1.0

-- resolution_audit (dbt model) : alerts if >5% of CSP or support companies are
--   unresolved, or any collaboration channel is unmapped > 7 days. Unresolved =>
--   quarantined (null FK), surfaced on a stewardship page for human confirmation.
--   No metric is published off a name-only match without review.
```

---

## 6. The mart + BI surface

```sql
-- mart_cs_health        : account list joined to latest snapshot; the who-do-I-call-today surface
-- mart_renewal_pipeline : renewal watchlist sorted by (churn_risk_tier, days_to_renewal)
```

BI-surface contract (built by `data-platform/dashboard-builder`): account list sorted by **risk tier × days-to-renewal**; per-account evidence drill-down (tier drivers, trend sparkline, support, NPS, renewal stage); a **stewardship page** for low-confidence matches; a **"last refreshed"** timestamp on every view; per-CSM RLS. **No raw SQL in the BI tool — datasets read the mart layer only.**

> **Acceptance test:** a CS leader sorts by `(churn_risk_tier = 'Red' AND days_to_renewal < 90)` and gets an actionable call list in under two minutes, every Red showing why.

---

## 7. The transparent rule-based tier

`churn_risk_tier` is computed by a **readable, tunable rule** — no black-box ML in phase 1. Example:

```sql
churn_risk_tier =
  CASE
    WHEN health_score_trend_30d = 'down'
         AND days_to_renewal < 90
         AND (p1_p2_rate_30d > {{ t_support }} OR collab_escalation_signal_7d > {{ t_escalation }})
      THEN 'Red'
    WHEN health_score_trend_30d = 'down'           -- any single leading signal, renewal not imminent
         OR usage_trend_30d = 'down'
      THEN 'Yellow'
    ELSE 'Green'
  END
```

- **Renewal proximity is a GATE, not a standalone term** — it multiplies urgency; it never makes an account Red on its own.
- **`churn_risk_drivers` records the explainability contract** — for every Red/Yellow, the 2-3 driving signals with `{signal, value, threshold, window}`. Every Red shows *why*.
- **Thresholds (`t_support`, `t_escalation`, …) are tuned against actual past churn** — back-tested where outcomes exist; documented provisional defaults where they don't, retuned after the first renewal cycle.

---

## Handoff checklist

- [ ] `dim_account` conformed; master key = CRM Account ID
- [ ] Identity resolution + `bridge_account_xref` + `resolution_audit` → **data-platform** (this model consumes them)
- [ ] `fct_account_health_snapshot` append-only; nulls explicit (never zero)
- [ ] Collaboration signals derived-only (no raw bodies); NPS verbatim masked
- [ ] `churn_risk_tier` rule transparent + tunable; `churn_risk_drivers` populated for every Red
- [ ] Mart-only BI reads; "last refreshed" + stewardship page on the surface
- [ ] Pipeline / warehouse / RLS / BI build → **data-platform**

## References

- Knowledge: [`../knowledge/cs-health-metrics-and-churn-indicators.md`](../knowledge/cs-health-metrics-and-churn-indicators.md)
- Knowledge: [`../knowledge/renewal-and-account-lifecycle.md`](../knowledge/renewal-and-account-lifecycle.md)
- Skill: [`../skills/health-tier-design/SKILL.md`](../skills/health-tier-design/SKILL.md)
- Skill: [`../skills/renewal-workflow-design/SKILL.md`](../skills/renewal-workflow-design/SKILL.md)
- Cross-plugin (build the model): [`../../data-platform/CLAUDE.md`](../../data-platform/CLAUDE.md)
