---
name: access-governance
description: "Design and operate data access governance: define role-based access tiers from the classification scheme, implement column-level masking and row-level security, build an access request and review workflow, and produce an access audit report that proves least-privilege is enforced."
---

# Skill: access-governance

**Purpose:** Build the access control engineering that enforces the classification scheme in practice — roles, masking, row-level security, request/review workflow, and the audit trail. Used by `data-governance-architect` (policy definition), `data-catalog-lineage-engineer` (access surface catalogued), and `privacy-compliance-engineer` (GDPR/CCPA access obligations).

## When to use

- A governance program has a classification policy but no corresponding access controls in the data layer.
- Broad `SELECT *` grants exist on tables containing PII or Confidential data.
- An access audit has surfaced over-provisioned users or stale role memberships.
- A new data product is being published and access must be set before any external consumer is connected.

---

## Step 1: Map classification to access tiers

Every classification level maps to a specific access tier. The controls get stricter as classification rises.

**Access tier model:**

| Classification | Tier | Who can access | Controls |
|---|---|---|---|
| Public | Tier 0 | Anyone (authenticated) | No masking; standard read grants |
| Internal | Tier 1 | All employees, contractors | Standard RBAC roles; no masking required |
| Confidential | Tier 2 | Named teams / business function | Column-level masking for non-business-need users; access requires a named role |
| Restricted / PII | Tier 3 | Minimal named individuals | Column-level masking by default; unmasked access requires an approved role with business justification; access review quarterly |
| Restricted / Sensitive PII (health, biometric, etc.) | Tier 4 | Strict need-to-know only | No broad grants; row-level security in addition to column masking; access review monthly |

---

## Step 2: Implement column-level masking

Column-level masking (CLM) ensures that a user who queries a table sees either the real value or a masked value depending on their role membership — without requiring a separate masked view.

**Snowflake example:**

```sql
-- Step 1: Create a masking policy for email
CREATE OR REPLACE MASKING POLICY email_mask AS (val STRING)
  RETURNS STRING ->
    CASE
      WHEN CURRENT_ROLE() IN ('PII_UNMASKED_ROLE', 'DATA_STEWARD_ROLE')
        THEN val                              -- see real value
      WHEN CURRENT_ROLE() = 'ANALYST_ROLE'
        THEN CONCAT(LEFT(val, 2), '***@***.***')   -- partial mask
      ELSE '***MASKED***'                     -- full mask for everyone else
    END;

-- Step 2: Apply to the column
ALTER TABLE customers
  MODIFY COLUMN email SET MASKING POLICY email_mask;
```

**BigQuery equivalent:** Use column-level security with policy tags and BigQuery data policies.

**dbt approach:** Define masking in the warehouse and reference it in `schema.yml` meta blocks for documentation; do not duplicate masking logic in SQL models (the warehouse enforces it, dbt documents it).

---

## Step 3: Implement row-level security (for Tier 4)

Row-level security (RLS) restricts which rows a user can see, not just which columns. Use for:
- Multi-tenant data where each tenant can only see their own rows.
- Health or HR data where access is restricted to the owning department.

**Snowflake row access policy:**

```sql
-- Policy: each user can only see rows for their own customer_region
CREATE OR REPLACE ROW ACCESS POLICY region_filter AS (customer_region STRING)
  RETURNS BOOLEAN ->
    customer_region = CURRENT_ROLE()
    OR CURRENT_ROLE() IN ('GLOBAL_ADMIN', 'DATA_STEWARD');

ALTER TABLE customer_health_records
  ADD ROW ACCESS POLICY region_filter ON (customer_region);
```

**BigQuery equivalent:** Row-level security via authorized views or `CREATE ROW ACCESS POLICY`.

---

## Step 4: Build the access request workflow

An access request workflow replaces ad-hoc Slack requests with a traceable, auditable process.

**Minimum workflow:**

```
1. Requester submits a form:
   - Data asset name / table / schema
   - Access type requested (read / write / unmasked PII)
   - Business justification (one paragraph)
   - Duration required (time-bounded access preferred)
   - Approver notified (line manager + data steward for Tier 3/4)

2. Steward reviews within SLA:
   - Tier 1–2: 2 business days
   - Tier 3: 5 business days (PII review)
   - Tier 4: 5 business days + legal/DPO confirmation

3. Approval:
   - APPROVED → role granted in IAM / warehouse; logged in access register
   - REJECTED → rationale documented; requester notified
   - CONDITIONAL → time-limited grant with review date; calendar reminder set

4. Completion:
   - Log entry: who approved, what was granted, on what date, for how long
   - Access register updated
```

**Tools:** ServiceNow, Jira (create an access-request issue type), or a simple Google Form + Sheets workflow with a manual approval step. The tool matters less than the traceability.

---

## Step 5: Access review cadence

Role membership must be reviewed on a schedule to remove stale access (leavers, movers, project end).

**Review schedule:**

| Tier | Review frequency | Who reviews | Action on stale |
|---|---|---|---|
| Tier 1 (Internal) | Annual | System owner | Remove from role |
| Tier 2 (Confidential) | Quarterly | Data steward + system owner | Remove and log |
| Tier 3 (Restricted/PII) | Quarterly | Data steward + DPO confirmation | Remove and log; flag to DPO |
| Tier 4 (Sensitive PII) | Monthly | Data steward + DPO + CISO | Remove immediately; investigate if unexplained |

**Stale access definition:**
- User is no longer employed (leaver) — revoke immediately via HR trigger.
- User has changed role and the role is no longer relevant — revoke within 5 business days.
- Time-limited grant has expired — auto-revoke or revoke at review.

---

## Step 6: Access audit report

The access audit report is evidence of least-privilege enforcement for internal audit, regulatory review, or a DPIA (Data Protection Impact Assessment).

**Minimum audit report sections:**

1. **Access register snapshot** — all active grants as of the audit date, classified by tier.
2. **Over-provisioned accounts identified** — users with Tier 3/4 access who were not in the approved-access register.
3. **Stale access removed this period** — leavers, movers, expired time-limited grants.
4. **Access requests processed** — approved, rejected, conditional grants by tier.
5. **Masking policy coverage** — % of Tier 3/4 columns covered by a masking policy.
6. **Open exceptions** — any known deviation from least-privilege with a remediation plan and date.

---

## Pitfalls

- **Classification exists but is not connected to access controls** — having a policy document that says "PII is Restricted" but no masking or role policy in the warehouse means classification is decoration, not governance.
- **Broad `SELECT *` grants on warehouse schemas** — common in early data warehouse builds; the analyst habit of "grant all on schema" bypasses all classification-based controls.
- **Stale Tier 3 access not reviewed** — former contractors retaining access to PII columns 6 months after project end is the most common data-access audit finding.
- **Access request workflow that skips the data steward** — a manager-only approval for Tier 3/4 data access bypasses the person who understands the data sensitivity; the steward must be in the loop.
- **No time limit on time-sensitive grants** — a "temporary" access grant with no review date becomes a permanent grant; always set a calendar reminder or an automated expiry.
