# Separate the dbt build role from the dashboard query role at the DB layer

**Status:** Absolute rule
**Domain:** dbt / security / least privilege
**Applies to:** `data-platform`

---

## Why this exists

A single database user that both writes (runs dbt transforms) and reads (serves dashboard queries) violates least privilege and creates a blast radius when either path is compromised. If a dashboard connection string leaks, an attacker inherits write access to the marts. If the dbt runner is misconfigured, it can overwrite a mart that viewer connections are actively reading. The fix is two separate Postgres roles: `dbt_build_role` (USAGE + CREATE on the transform schema, no SELECT on production viewer tables) and `dbt_query_role` (SELECT only on marts, no CREATE anywhere).

## How to apply

```sql
-- Build role: used by dbt runner (CI, scheduled jobs)
CREATE ROLE dbt_build_role NOLOGIN;
GRANT USAGE ON SCHEMA staging, intermediate, marts TO dbt_build_role;
GRANT CREATE ON SCHEMA staging, intermediate, marts TO dbt_build_role;
-- NO SELECT on viewer tables needed; dbt creates them

-- Query role: used by dashboard connection (Cube, Superset, Metabase)
CREATE ROLE dbt_query_role NOLOGIN;
GRANT USAGE ON SCHEMA marts TO dbt_query_role;
GRANT SELECT ON ALL TABLES IN SCHEMA marts TO dbt_query_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA marts
  GRANT SELECT ON TABLES TO dbt_query_role;

-- Never grant dbt_build_role privileges to the dashboard connection user
-- Never grant dbt_query_role CREATE privileges
```

In `dbt_project.yml`, set `target` profiles to use `dbt_build_role`; in the dashboard's connection config, use a login user that has only `dbt_query_role`.

**Do:**
- Create both roles before the first `dbt build` run.
- Store the query-role connection string in the dashboard tool; store the build-role connection string in CI only.
- Review role grants after schema additions (`ALTER DEFAULT PRIVILEGES` may need re-running).

**Don't:**
- Use a single superuser for both the build pipeline and the dashboard tool.
- Grant `CREATE` to the dashboard query user "just in case."
- Commit either connection string to source control.

## Edge cases / when the rule does NOT apply

- DuckDB file-based deployments (local analytics jobs) may not support multi-role; document the single-user constraint explicitly and accept the reduced blast radius.
- Managed connectors that require superuser for setup should have superuser revoked immediately after setup and replaced with the minimal `dbt_query_role`.

## See also

- [`../agents/database-setup-guide.md`](../agents/database-setup-guide.md) — provisions the roles at schema-setup time
- [`./rls-author-using-and-with-check-force-on.md`](./rls-author-using-and-with-check-force-on.md) — RLS policy design that complements role separation

## Provenance

Codifies `skills/dbt-project-scaffolding/SKILL.md` (RLS-safe `dbt_build_role` / `dbt_query_role` separation) and standard least-privilege database security practice.

---

_Last reviewed: 2026-06-05 by `claude`_
