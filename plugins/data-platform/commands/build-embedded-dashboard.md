---
description: Build an embedded dashboard the secure-by-construction way — metric defined once in the semantic layer, tenant scope at the closest-to-data layer, short-lived server-signed JWTs, a locked CSP/iframe boundary, a visible as-of timestamp, and a cross-boundary denial test.
argument-hint: "[the dashboard + stack, e.g. 'tenant-scoped revenue dashboard on Cube + React']"
---

# Build an embedded dashboard

You are running `/data-platform:build-embedded-dashboard`. Build (or harden) the embedded dashboard the user described (`$ARGUMENTS`), following this plugin's `dashboard-builder` discipline. A dashboard that renders the right numbers but leaks across tenants, embed-jacks, or shows silently-stale data is not done.

## When to use this

A customer-facing or client-deliverable dashboard is being built or remediated. Not for an internal admin-only single-tenant view (no tenant axis to enforce) and not when the deliverable is a static Evidence.dev portfolio page (SQL-in-markdown is its own single source of truth).

## Steps

1. **Define every metric once in the semantic layer** (`model-semantic-layer-single-source-of-truth`): "active customer" / "recognized revenue" gets one definition in Cube (Case C) / dbt-MetricFlow / the Power BI model — every widget references it, never re-derives raw SQL inline. Two widgets disagreeing on a KPI means a definition leaked out of the layer.
2. **Enforce tenant scope at the closest-to-data layer the viewer can't influence** (`enforce-tenant-isolation-closest-to-data`): Cube `access_policy` referencing `{ securityContext.tenant_id }`, or Postgres RLS, or Power BI DAX roles — never an app-code `where tenant_id =` on the read path as the load-bearing control.
3. **Issue short-lived, server-signed JWTs** (`issue-short-lived-jwts-for-embeds`): the host app's server issues a 5-15 minute token after authenticating the session, carrying `sub`, `tenant_id` (from the session, never the URL), `iss`, `aud`; the front-end only *requests* and passes it. Signing key from env, never inline; refresh at ~80% of lifetime.
4. **Lock the embed boundary** (`embed-lock-csp-frame-ancestors-and-sandbox`): explicit `frame-ancestors` allow-list (never `*`), least-privilege iframe `sandbox="allow-scripts allow-same-origin"`, and every `postMessage` handler checks `event.origin` and validates `event.data` shape; post with an explicit target origin.
5. **Show the as-of timestamp and a freshness SLA** (`dashboard-set-data-freshness-slas`): surface "current as of <time>" on the dashboard so a broken pipe is visible not silent, and back it with a dbt `source freshness` check that alerts on breach.
6. **Ship the cross-boundary denial test** (`enforce-tenant-isolation-closest-to-data`): issue a token for tenant A, query tenant B, assert zero rows. No test, no merge.

## Guardrails

- Any JWT-issuance, RLS, or CSP/iframe change is security-sensitive — route through `ravenclaude-core/security-reviewer`, mandatory.
- Resist per-viewer-priced BI tools (Looker, Tableau Embedded, Sigma, Metabase Pro) for SMB consulting — flag the 5-50 viewers x 4-6 clients x $400+/viewer math before going down that path.
- Power BI Embedded uses an Azure AD token via MSAL (not an app-issued JWT) and DAX-role scoping — coordinate DAX/PBIP/semantic-model specifics with `power-platform/power-bi-engineer`.
