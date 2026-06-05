# Nulls are explicit — missing signal is never silently zero

**Status:** Absolute rule
**Domain:** CS data quality and signal integrity
**Applies to:** `customer-success-analytics`

---

## Why this exists

Zero and absent are not the same thing. An NPS score that was not collected this quarter is not a 0 — it is unknown. An account with no support tickets filed this month has a support load of 0; an account with no support-ticket data connected has NULL. Coding absent values as zero is a category error that pollutes the tier model: a missing NPS reads as an extremely unhappy customer, and a missing usage metric reads as total disengagement. Downstream, this generates false Reds and causes CS leaders to triage accounts that simply have a data gap — eroding trust in the scoring system within weeks of go-live.

## How to apply

Design all signal columns in the health snapshot with explicit NULL semantics. Build a companion `signal_freshness` or `data_availability` table that tracks, per account, which signals are populated and when each was last updated.

```sql
-- Correct: explicit NULL for absent values
fct_account_health_snapshot (
  nps_score           INT,        -- NULL = not collected this period, NOT zero
  usage_score         FLOAT,      -- NULL = source disconnected, NOT zero
  support_ticket_count INT        -- 0 = genuinely zero tickets; NULL = source not available
)

-- Signal freshness companion table:
dim_account_signal_freshness (
  account_key          INT,
  signal_name          VARCHAR(50),
  last_populated_date  DATE,
  source_status        VARCHAR(20)  -- 'connected' | 'disconnected' | 'pending'
)

-- Tier rule: handle NULLs explicitly
health_tier =
  CASE
    WHEN nps_score IS NULL THEN 'UNKNOWN - no NPS data'  -- NOT 'RED'
    WHEN nps_score < 5     THEN 'RED'
    ...
  END

-- NEVER: COALESCE(nps_score, 0) in a tier rule — this codes absence as terrible NPS
```

**Do:**
- Display a "data gap" indicator in the BI surface whenever a key signal is NULL for a given account.
- Include signal-availability counts in the health mart's metadata columns.
- Write tier rules that explicitly handle NULLs with a distinct outcome (e.g., "Incomplete" tier label) rather than falling through to a numeric comparison.

**Don't:**
- Use `COALESCE(signal, 0)` in a tier rule — zero is a real value, not a safe substitute for absent.
- Suppress NULL-signal accounts from the CS leader's view — they may have a data-pipeline problem that needs fixing.
- Mix zero and NULL treatment across different signal columns without documenting the distinction.

## Edge cases / when the rule does NOT apply

Aggregated count signals (number of feature events, number of logins in a period) where zero is a legitimate and meaningful value can be safely treated as 0 for a connected account — provided the connection status is verified first. The NULL rule applies primarily to scored, derived, or survey-based signals where absence means "not measured," not "none occurred."

## See also

- [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md) — defines the schema and NULL semantics in the health mart.
- [`../agents/churn-signal-analyst.md`](../agents/churn-signal-analyst.md) — validates signal behavior at edge cases including nulls.

## Provenance

Codifies the plugin's §4 house opinion #7 ("Nulls are explicit, never silently zero"). The COALESCE-to-zero anti-pattern is extremely common in first-generation CS health implementations because SQL's default numeric behavior silently converts NULLs; this rule documents the explicit contract that prevents it.

---

_Last reviewed: 2026-06-05 by `claude`_
