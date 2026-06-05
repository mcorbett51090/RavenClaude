# Route all sensitive data access through a workflow — no ad-hoc grants

**Status:** Absolute rule
**Domain:** Access governance
**Applies to:** `data-governance-privacy`

---

## Why this exists

A database administrator who receives a Slack message "can you give Alice access to the customer table?" and runs `GRANT SELECT` immediately has bypassed every governance control: no steward approval, no purpose documentation, no time-bound grant, no audit trail. When the organization faces a privacy audit or a breach investigation, "the DBA granted it on Slack" is not an acceptable access record. An access request workflow — even a simple one — produces an approver, a documented purpose, a time-bound grant, and an audit log.

## How to apply

Implement an access request workflow appropriate to the organization's maturity:

**Minimum viable workflow (GitHub Issues or Jira):**

```markdown
## Data Access Request

**Requestor:** Alice Chen
**System / table:** marts.fct_customers
**Access level:** SELECT (masked email + phone; unmasked tier and revenue only)
**Purpose:** Q3 churn analysis for product team
**Duration:** 30 days (expires 2026-07-05)
**Steward approval:** [@jane-smith-steward](steward)
**Approved:** [x] Yes / [ ] No

---
_Automated grant will be issued on approval and revoked on expiry._
```

**Automated grant + expiry (dbt/SQL):**

```sql
-- Issued on approval
GRANT SELECT ON marts.fct_customers_masked TO alice_chen_role;

-- Revoked on expiry (via a scheduled job or JIRA automation trigger)
REVOKE SELECT ON marts.fct_customers_masked FROM alice_chen_role;
```

**Access request log table in the catalog:**

```sql
CREATE TABLE access_grants (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    grantee         text NOT NULL,
    asset           text NOT NULL,        -- 'marts.fct_customers'
    access_level    text NOT NULL,        -- 'masked_read', 'pii_read'
    purpose         text NOT NULL,
    steward_id      text NOT NULL,
    approved_at     timestamptz,
    expires_at      timestamptz,
    revoked_at      timestamptz,
    request_url     text                  -- link to the JIRA/GitHub issue
);
```

**Do:**
- Require a written purpose for every access grant to a Confidential or Restricted asset.
- Set an expiry on every grant — default 30 days for analysis; 90 days for recurring operational use.
- Log every grant and revocation in the catalog's access governance record.

**Don't:**
- Accept verbal or Slack-based access requests as sufficient for PII-classified data.
- Grant permanent (no-expiry) access to Confidential or Restricted assets without a documented exception.

## Edge cases / when the rule does NOT apply

- Service accounts (BI tool connections, ELT pipeline connections) follow a separate provisioning process with a service account registry rather than per-request grants. They still require steward approval at provisioning time.

## See also

- [`../agents/data-governance-architect.md`](../agents/data-governance-architect.md) — designs the access request workflow
- [`./least-privilege-data-access.md`](./least-privilege-data-access.md) — the least-privilege rule that this workflow enforces

## Provenance

Standard access governance practice. ISO 27001 A.9.2 (user access management) and GDPR Article 5(1)(f) (integrity and confidentiality) both require documented, controlled access. Codifies data-governance-privacy CLAUDE.md §2 house opinion #1 ("classification precedes control") — the control is the workflow.

---

_Last reviewed: 2026-06-05 by `claude`_
