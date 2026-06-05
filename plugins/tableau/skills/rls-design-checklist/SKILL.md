---
name: rls-design-checklist
description: "Gate-by-gate checklist for designing Tableau row-level security (RLS): mechanism selection (user filter vs entitlement table vs data-policy VDM), implementation verification, performance impact assessment, and the mandatory security-reviewer escalation criteria. Owned by tableau-admin."
---

# RLS Design Checklist

## When to invoke

- Designing RLS for a new Tableau workbook or data source.
- Auditing an existing RLS implementation before a security review.
- A user reports seeing data they should not, or not seeing data they should.
- Migrating RLS from user filters to a data-policy / entitlement-table approach.

## Critical preamble

**RLS is a security control, not a convenience filter.** Every RLS design must be reviewed by `ravenclaude-core/security-reviewer` before production publish. This checklist prepares the design for that review — it does not substitute for it.

## Gate 1 — Choose the RLS mechanism

| Mechanism | How it works | Use when |
|---|---|---|
| **User filter (calculated field)** | `USERNAME()` or `USERDOMAIN()` in a calculated filter; user-to-value mapping in the workbook | Small, stable user-to-dimension mapping; Tableau Server/Cloud with named users |
| **Entitlement table (data-source join)** | Join/blend a permission table that maps `[Username]` → `[Allowed Dimension Value]`; filter on match | Dynamic, database-managed entitlements; many users; self-service permission updates |
| **Virtual Connection / Data Policy (Tableau Cloud)** | Centralised RLS defined once in a Virtual Connection; enforced at the data layer for all downstream workbooks | Multi-workbook or multi-user organisation; Tableau Cloud; need central governance |
| **Initial SQL injection** | Session-level variables injected at connect time; filter applied in SQL | Live connections to databases that support session variables (Snowflake, Redshift, BigQuery) |

**Decision rule:** prefer the entitlement-table or data-policy approach for any deployment with > 20 users or > 1 data source — user filters in workbooks are fragile, duplicated, and hard to audit.

## Gate 2 — Implementation checklist (entitlement table approach)

- [ ] The entitlement table is owned and maintained by IT/data-governance, not embedded in the workbook.
- [ ] The join between the data table and the entitlement table uses the same grain as the RLS dimension (e.g., Region, Business Unit, Customer ID).
- [ ] `USERNAME()` (or `USERDOMAIN()+USERNAME()`) is used as the filter key — **not** a parameter (parameters are not security controls; users can override them).
- [ ] The filter is applied as a **data source filter**, not a view-level filter (data source filters apply to every sheet in the workbook; view-level filters apply only to one sheet).
- [ ] The filter has been tested with at least three user accounts representing different entitlement profiles, including a user with no entitlement (should see zero rows, not an error).
- [ ] Null handling: if `USERNAME()` returns null (unauthenticated embed), the filter defaults to zero rows visible — not all rows.

## Gate 3 — Performance impact assessment

RLS implemented via a join to an entitlement table adds a per-query filter. Measure:

1. **Before RLS**: record average query time on the target workbook (Performance Recording).
2. **After RLS**: record the same query with RLS active for a mid-cardinality user (50–200 allowed values).
3. If query time increases > 2×: add an index on the join key in the entitlement table, or materialise the entitlement join in the extract using Tableau Prep.

High-cardinality RLS (e.g., per-customer data in a 10 M row table, 100 K customers) may require partitioned extracts or Virtual Connections — a single filtered extract for all users will not scale.

## Gate 4 — Security escalation criteria

Escalate to `ravenclaude-core/security-reviewer` whenever ANY of the following are true:

- [ ] The RLS-protected data is classified as PII, PHI, financial, or regulated.
- [ ] The entitlement mapping is user-managed (not IT-managed) — users could expand their own access.
- [ ] The workbook is embedded in an application where the authentication layer is not Tableau's own (Connected Apps / JWT) — the embed auth must enforce the RLS identity.
- [ ] The RLS uses a parameter instead of `USERNAME()` — this is not secure; any user can change a parameter.
- [ ] The same data source is used for both RLS-restricted and unrestricted workbooks — verify that the unrestricted workbook does not expose restricted rows.

## Gate 5 — Ongoing governance

- [ ] Document the RLS design in the workbook description: which field(s) are filtered, which entitlement table, who owns it.
- [ ] Add an entitlement-table health check: a scheduled query that alerts if the entitlement table is empty or returns null for active users.
- [ ] Include RLS testing in the content-promotion runbook (dev→test→prod): a named test user per environment whose entitlement is fixed and tested on every promotion.
- [ ] Review entitlement table accuracy quarterly — departed employees who retain entitlements are the most common RLS audit finding.

## Pitfalls

- A user filter built into the workbook as a calculated field with a hardcoded mapping — breaks every time a user is added/removed; must be edited in every workbook.
- RLS applied only on a "Total" sheet but not on the underlying detail sheet — users navigate directly to the detail via a URL and see unfiltered data.
- Testing RLS only with the workbook owner's account — the owner bypasses RLS (Tableau Server). Always test with a named test user with no admin rights.
- Using `ISMEMBEROF()` (group membership) as the RLS control — group membership changes are often delayed by AD sync; test the lag before relying on it.
