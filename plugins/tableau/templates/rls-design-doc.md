> Use this template to document a Tableau row-level security (RLS) design before implementation and security review — mechanism, entitlement mapping, test plan, and the escalation checklist.

# RLS Design: [Workbook / Data Source Name]

## Metadata

| Field | Value |
|---|---|
| Workbook / data source | [Name] |
| Data classification | [PII / Financial / Internal / Public] |
| RLS designer | [Name] |
| Security reviewer | [Name — from ravenclaude-core/security-reviewer or equivalent] |
| Review status | [Draft / In review / Approved] |
| Last updated | [YYYY-MM-DD] |

---

## Security requirement

**Who should NOT see whose data?**

[e.g., "Regional sales managers should see only their own region's opportunities. No manager sees another region's pipeline."]

**What is the RLS dimension?**

[e.g., Region / Business Unit / Customer ID / Cost Centre]

**What is the data classification and regulatory context?**

[e.g., "Revenue data — internal confidential. No PII. Not subject to HIPAA/GDPR, but sensitive to the business."]

---

## RLS mechanism selected

| Mechanism | Selected | Reason |
|---|---|---|
| Tableau user filter (workbook-embedded) | [ ] | |
| Entitlement table (join at data source) | [ ] | |
| Virtual Connection / Data Policy (Tableau Cloud) | [ ] | |
| Initial SQL with session variables | [ ] | |

**Justification for chosen mechanism:**

[Explain why this mechanism was selected over the alternatives.]

---

## Entitlement mapping (if entitlement table approach)

**Table name and location:** [Database.Schema.TableName]

**Schema:**

| Column | Type | Description |
|---|---|---|
| `username` | VARCHAR | Tableau `USERNAME()` value (UPN or DOMAIN\user) |
| `[rls_dimension]` | VARCHAR | Allowed dimension value (e.g., 'West Region') |
| `effective_from` | DATE | When this entitlement became active |
| `effective_to` | DATE | NULL = currently active |

**Who maintains the entitlement table?** [Name / Team / system]

**How are changes made?** [Jira ticket / automated HR feed / manual update]

**How often is it refreshed?** [Real-time / Daily sync]

---

## Implementation specification

**Filter field:** `[Field Name]` — applied as: [ ] Data source filter / [ ] View filter (data source filter required for security)

**Calculated field or join condition:**

```
[USERNAME()] = [entitlement_table].[username]
AND [data_table].[rls_dimension] = [entitlement_table].[rls_dimension]
```

**Null handling:** If `USERNAME()` returns NULL (unauthenticated embed), show: [ ] Zero rows (secure default) / [ ] All rows (only for public/unauthenticated embeddings with no sensitive data)

---

## Test plan

| Test case | Test user | Expected result | Actual result | Pass? |
|---|---|---|---|---|
| Standard entitlement | [user@domain] — West Region | Sees only West data | | |
| No entitlement | [user@domain] — no entry | Sees zero rows, no error | | |
| Multiple entitlements | [user@domain] — North + South | Sees North + South data | | |
| Admin account | [admin@domain] | Does NOT bypass RLS (test as non-owner) | | |
| Embed / unauthenticated | [null USERNAME()] | Zero rows returned | | |

---

## Escalation checklist (for security-reviewer)

- [ ] Data classification reviewed and documented above.
- [ ] Filter is a data source filter (not view-level).
- [ ] `USERNAME()` is the filter key (not a parameter — parameters are not security controls).
- [ ] Entitlement table is IT-managed (not user-managed).
- [ ] Null-user case defaults to zero rows.
- [ ] Test plan completed with non-admin test users.
- [ ] Embedded deployment (if any): Connected Apps / JWT auth enforced at the embed layer.

**Security reviewer sign-off:** [Name] [Date]

---

## Ongoing governance

| Item | Owner | Frequency |
|---|---|---|
| Entitlement table accuracy audit | [Name] | Quarterly |
| Departed-user entitlement cleanup | [IT/HR] | Monthly |
| RLS test after every workbook update | [Developer] | Per promotion |
