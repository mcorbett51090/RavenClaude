# Identity resolution is upstream — never reimplement it

**Status:** Absolute rule
**Domain:** CS data architecture
**Applies to:** `customer-success-analytics`

---

## Why this exists

Customer-success data comes from multiple systems: a CRM (Salesforce), a CS platform (Planhat, Gainsight), a product-usage warehouse, a support system (Zendesk), and possibly NPS tooling. Each system has its own account identifier. Matching these identifiers — the identity-resolution problem — is a hard data-engineering problem involving fuzzy name matching, company disambiguation, and multi-key joins. When this plugin reimplements the matcher (e.g., by joining on company name in a mart view), it creates a second definition of "what is an account" that will diverge from the authoritative matcher over time. The result is two different account counts in two different dashboards: the CS leader's call list and the CRM's renewal pipeline disagree. Every unmatched row becomes a ghost account — a real customer invisible to the health model.

## How to apply

Consume the identity-resolution output from data-platform's `bridge_account_xref` table as the spine for all joins. Never join source systems on name or email directly in the mart layer.

```sql
-- Correct: consume the resolved spine
-- bridge_account_xref is owned and maintained by data-platform
SELECT
  b.master_account_key,
  b.crm_account_id,
  b.csp_account_id,
  b.support_account_id,
  s.usage_trend_30d,
  c.nps_score
FROM data_platform.bridge_account_xref b
LEFT JOIN product_usage.usage_signals s ON s.account_id = b.csp_account_id
LEFT JOIN nps_tool.responses c         ON c.account_id = b.crm_account_id

-- Wrong: reimplementing identity resolution by name join:
-- SELECT * FROM crm_accounts c
-- JOIN csp_accounts p ON LOWER(TRIM(c.company_name)) = LOWER(TRIM(p.account_name))
-- ^ fuzzy name match — creates a second, diverging identity resolver
```

**Do:**
- Reference `bridge_account_xref` as the authoritative cross-system identity spine.
- Report unresolved accounts (those with no `master_account_key`) to data-platform for investigation.
- Include an "identity confidence" column in the health mart that flags rows resolved only on fuzzy match pending data-platform verification.

**Don't:**
- Join source systems on `company_name`, `email`, or any non-authoritative key.
- Publish a health metric for an account that was resolved only by name match without human verification.
- Build or maintain a local xref table in this plugin's schema — that is data-platform's ownership.

## Edge cases / when the rule does NOT apply

In early-stage implementations before `bridge_account_xref` is available, a documented interim join on a high-confidence business key (e.g., a shared contract ID or domain name) is acceptable — but must be labeled "temporary" with a handoff date and documented as a known resolution gap, not promoted to production without data-platform sign-off.

## See also

- [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md) — designs the health mart and owns the dependency on the xref spine.
- [`./the-mart-is-the-single-source-of-metric-definitions.md`](./the-mart-is-the-single-source-of-metric-definitions.md) — the companion rule on avoiding dual definitions in the analytics layer.

## Provenance

Codifies the plugin's §4 house opinion #5 ("Identity resolution is upstream and owned by data-platform"). The local-name-match anti-pattern is the most common reason for count discrepancies between CS dashboards and CRM renewal pipelines; the xref-spine discipline is the structural fix.

---

_Last reviewed: 2026-06-05 by `claude`_
