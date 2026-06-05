# No raw collaboration message bodies in the warehouse

**Status:** Absolute rule
**Domain:** CS data privacy
**Applies to:** `customer-success-analytics`

---

## Why this exists

Raw Slack or Teams message bodies carry an extremely wide PII blast radius: they may contain customer names, financial terms, health information, personal grievances, or credentials — none of which belongs in a data warehouse. Landing raw message bodies creates a permanent record of communications that were not sent expecting to be stored as structured data, and the blast radius if the warehouse is breached or misconfigured is unbounded. The insight value — understanding whether a customer relationship is warm or escalating — does not require the raw text; it requires derived signals like escalation-keyword density, message volume, sentiment bucket, or thread-response lag. Land the derived signal only; never the source body.

## How to apply

Design the collaboration-signal landing pattern to extract derived metrics at ingestion time. Raw message bodies never touch the warehouse; only the derived columns do.

```sql
-- Correct: derived-signal-only collaboration table
fct_collaboration_signals (
  account_key           INT,
  signal_date           DATE,
  channel               VARCHAR(20),  -- 'slack' | 'teams'
  message_volume_7d     INT,          -- count of messages in 7-day window
  escalation_keyword_hit BOOLEAN,     -- TRUE if message contained escalation keywords
  coarse_sentiment      VARCHAR(10),  -- 'positive' | 'neutral' | 'negative' — coarse bucket
  thread_response_lag_hrs FLOAT,      -- avg PSM response time
  mention_count         INT           -- how often vendor/product was mentioned
  -- NO: message_body, raw_text, thread_content, etc.
)

-- Ingestion architecture:
-- Source (Slack/Teams API) → Lambda/function → keyword extraction + sentiment bucket
-- → derived-signal row only → warehouse
-- Raw message body: never written to disk in the pipeline
```

**Do:**
- Extract derived signals (volume, escalation flag, coarse sentiment) in the ingestion function, before anything is written to the warehouse.
- Document the keyword list used for escalation detection — it is part of the signal definition.
- Route any proposed addition of richer collaboration data through the security-reviewer.

**Don't:**
- Land raw message bodies in even a "temporary" or "staging" table with the intention of later deleting them.
- Use a collaboration API integration that stores full message content in an intermediate broker before deriving metrics.
- Define escalation keyword lists without a documented approval process — keyword lists are a form of sentiment policy.

## Edge cases / when the rule does NOT apply

This rule applies to collaboration platforms (Slack, Teams, Google Chat) used for customer-facing communication. Internal-only engineering chat (e.g., on-call Slack channels, incident bridges) has different PII exposure, but the same derived-signal principle applies — land incident count and escalation flag, not the raw thread. The rule does not prevent PSMs from reviewing collaboration content in the source platform; it only governs what enters the warehouse.

## See also

- [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md) — defines the warehouse schema; owns the no-raw-body constraint.
- [`./nulls-are-explicit-missing-signal-is-never-silently-zero.md`](./nulls-are-explicit-missing-signal-is-never-silently-zero.md) — the companion rule on representing absent signals correctly, including when collaboration data is not connected.

## Provenance

Codifies the plugin's §4 house opinion #11 ("No raw collaboration-message bodies in the warehouse"). The raw-body landing pattern is occasionally proposed as "we'll aggregate it later" — this rule documents why "later" never makes the original landing acceptable.

---

_Last reviewed: 2026-06-05 by `claude`_
