---
description: Stand up a multi-tenant Postgres database with isolation designed in, not retrofitted — engine picked by workload, tenant_id on every fact table, RLS ENABLE + FORCE with USING and WITH CHECK, SET LOCAL behind the pool, and a cross-tenant denial test that returns zero rows.
argument-hint: "[the client + tenancy, e.g. 'a mid-sized SaaS, 6 tenants, dashboard reads']"
---

# Stand up a multi-tenant database

You are running `/data-platform:stand-up-multi-tenant-database`. Stand up the system-of-record database the user described (`$ARGUMENTS`), following this plugin's `database-setup-guide` discipline. Retrofitting RLS onto a populated multi-tenant table is far harder than designing it in — so design it in.

## When to use this

Standing up a new database for a client, or migrating a spreadsheet/single-tenant DB to multi-tenant. Not for the analytical warehouse schema (that's the warehouse-schema command) and not for a single-tenant deliverable beyond documenting the missing-axis assumption.

## Steps

1. **Pick the engine by workload and economics** (`warehouse-select-by-workload-not-brand`): for an OLTP system-of-record plus dashboard reads, the SMB default is **Supabase Pro** (Postgres + RLS + auth + storage in one connection string); Neon for branch-per-engagement isolation, RDS for AWS-native IAM-auth shops, Fabric F2 for M365. Make the DB choice *before* the ELT and dashboard choices.
2. **Put tenant_id on every fact table** (`enforce-tenant-isolation-closest-to-data`): `tenant_id` (uuid, NOT NULL, indexed) on every tenant-scoped table; the load-bearing isolation lives at the closest-to-data layer the viewer's token cannot influence — never an app-code filter on the read path.
3. **Author RLS with FORCE on, both USING and WITH CHECK** (`rls-author-using-and-with-check-force-on`): `ENABLE` *and* `FORCE` (owners/ELT bypass without FORCE); a `FOR ALL` policy with `USING` (read guard) *and* `WITH CHECK` (write guard, stops setting another tenant's id); index `tenant_id`; the viewer-facing role never gets `BYPASSRLS`.
4. **Source tenant_id via SET LOCAL behind the pool** (`rls-author-using-and-with-check-force-on`): `SET LOCAL app.tenant_id = '<jwt-claim>'` per request — `SET LOCAL`, not `SET`, or the tenant context leaks to the next request on a pooled connection. The value comes from the signed JWT claim, never a URL/query param.
5. **Separate the build role from the query role** (`rls-author-using-and-with-check-force-on`): the ELT/dbt build role may `BYPASSRLS` for truncate/load; the viewer-facing query role never does — defense-in-depth the cross-boundary test will prove.
6. **Ship the cross-tenant denial test** (`enforce-tenant-isolation-closest-to-data`): set role to viewer, set `app.tenant_id` to A, query for tenant B's rows, assert the count is zero. No test, no merge.

## Guardrails

- Every RLS / tenant_id / role change is security-sensitive — route through `ravenclaude-core/security-reviewer`, mandatory.
- Never hard-code credentials or signing secrets in source or schema files (the advisory hook greps for inline secrets); keep them in env / a secrets manager.
- A hard compliance regime (HIPAA / SOC 2 / GDPR) can override the cost default toward a BAA-backed tier — surface the constraint before recommending one, with a retrieval-dated pricing claim.
