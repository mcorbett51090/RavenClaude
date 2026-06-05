---
scenario_id: 2026-06-05-embedded-rls-leak-via-cube-securitycontext
contributed_at: 2026-06-05
plugin: data-platform
product: cube
product_version: "unknown"
scope: likely-general
tags: [multi-tenant, cube, securitycontext, rls, embed, denial-test]
confidence: high
reviewed: false
---

## Problem

A productized multi-tenant SaaS dashboard (Cube semantic layer → Next.js + Tremor, embedded per-tenant) shipped to its second customer. During onboarding the new tenant's admin opened the network tab, replayed a dashboard query with a hand-edited filter, and **saw a row count that included the first tenant's data**. The tenant filter was present in the front-end query the dashboard *sent*, but it was not enforced by Cube — so a viewer who could influence the query (any viewer, via the browser) could remove or widen it. A textbook tenant-isolation leak, caught by a customer rather than by us.

## Context

- The Cube cubes defined measures and dimensions correctly, but tenant scoping was done by the **front end passing a `tenant_id` filter** in the query body, with no `securityContext`/`access_policy` enforcement inside Cube.
- The embed JWT *did* carry a `tenant_id` claim — but Cube wasn't reading it into a query-rewrite rule; the claim was decorative.
- The DB connection account behind Cube was a single tenant-blind role with access to all rows (correct for a semantic-layer architecture — the boundary is supposed to live *in Cube*, not the DB).
- There was **no cross-boundary denial test** in the pipeline. The house contract ("every stack ships a cross-boundary denial test, no test no merge") had been skipped because "Cube isn't Postgres, the RLS hook didn't fire" — exactly the false-comfort the plugin warns about: the RLS hook is Postgres-only by design and does *not* catch a missing Cube scope rule.

## Attempts

- Tried: tightening the front-end query to always inject the filter and "lock" it in the UI. Outcome: rejected — this is app-code/rendering-layer filtering on a viewer-facing read path, the explicitly-forbidden load-bearing control. Anything the browser sends, the browser can edit. Not a fix.
- Tried: moving enforcement **into Cube** — a `securityContext` (a.k.a. `security_context` / `access_policy` depending on Cube version `[verify-at-use]`) that reads `tenant_id` from the verified JWT and injects a mandatory `WHERE tenant_id = ${securityContext.tenant_id}` into every generated query, so the filter is added server-side *after* the untrusted client query and cannot be removed by the viewer. Outcome: the boundary now lives at the semantic layer — the closest layer the viewer's token cannot influence — and the replayed-query attack returns zero cross-tenant rows.
- Tried: adding the mandatory **cross-boundary denial test** to CI — issue a JWT for tenant A, run tenant B's query, assert **zero rows**; run it on every deploy. Outcome: the leak class is now a build-gating regression, and a future refactor that breaks the scope rule fails CI instead of shipping.
- Tried: as defense-in-depth, also enabling a warehouse row-access policy as a backstop where the warehouse supported it. Outcome: a second independent layer, so a single mistake in the Cube rule is not catastrophic.

## Resolution

The root cause was **tenant isolation enforced at the rendering layer (a client-supplied filter) instead of the semantic layer**. The fix was to make Cube the boundary — `securityContext` reading the verified JWT claim and injecting the tenant filter server-side — plus the mandatory cross-boundary denial test in CI, plus a warehouse-policy backstop. This is the §3 #3 house opinion ("tenant isolation lives at the closest-to-data layer the viewer's token cannot influence, and never at the rendering layer") applied to a Cube stack, and the answer to the §4 anti-pattern "a dashboard built on a semantic layer where the cross-boundary denial test was skipped."

**Action for the next consultant hitting this pattern:** for any Cube (or other semantic-layer) embed, the tenant filter must be injected **by the semantic layer from a verified JWT claim**, never trusted from the client query — and you must ship the cross-boundary denial test even though the Postgres RLS hook will *not* fire on a non-Postgres stack (that silence is not a pass). Route any embed/RLS/JWT change through `ravenclaude-core/security-reviewer`. Traverse the `## Decision Tree: RLS / tenant-isolation enforcement layer` and `## Decision Tree: Embed authentication` trees in [`../knowledge/data-platform-decision-trees.md`](../knowledge/data-platform-decision-trees.md) before designing isolation.

**Sources (retrieved 2026-06-05):** Cube data-access-control / `securityContext` + `access_policy` (the API name and shape are version-dependent — `[verify-at-use]`): https://cube.dev/docs/product/auth/context — confirm against the installed Cube version before quoting the exact key. Canonical rules this corroborates — [`../best-practices/enforce-tenant-isolation-closest-to-data.md`](../best-practices/enforce-tenant-isolation-closest-to-data.md), [`../best-practices/semantic-layer-no-raw-sql-to-viewer.md`](../best-practices/semantic-layer-no-raw-sql-to-viewer.md), [`../best-practices/issue-short-lived-jwts-for-embeds.md`](../best-practices/issue-short-lived-jwts-for-embeds.md). See also [`../knowledge/multi-tenant-rls-patterns.md`](../knowledge/multi-tenant-rls-patterns.md).
