# Power BI Embedded for consultants

> **Last reviewed:** 2026-05-21. Sources: Azure pricing pages (verify before quoting), Microsoft Fabric documentation, EPC Group ISV guide. Refresh when: (a) Microsoft restructures F-SKU or Pro licensing (annual cadence), (b) Fabric OneLake security model evolves materially, (c) Power BI deprecates a Desktop / Service feature this knowledge file references.

## When Power BI Embedded is the right answer

For an SMB consulting engagement where:

- Client is M365-stack-aligned (Dynamics 365, Power Platform, Microsoft Fabric, Teams-embedded experiences)
- Client already pays for Microsoft 365 + Power BI Pro licenses for builders/admins
- Brand familiarity matters (the "powered by Power BI" feel is *desirable*, not a liability)
- Entra-ID-based RLS is acceptable as the auth source

**Default elsewhere:** Apache Superset / Metabase OSS for non-Microsoft clients.

## The F-SKU pricing (2026)

Power BI Embedded is now sold via **Microsoft Fabric F-SKUs** (Microsoft retired P-SKU Premium to new customers in 2024).

| SKU | PAYG monthly | Reserved (1-year) monthly |
|---|---|---|
| F2 | ~$262.80 | ~$156 (~41% savings) |
| F4 | ~$525 | ~$312 |
| F8 | ~$1,050 | ~$624 |
| F16 | ~$2,100 | ~$1,248 |
| ... up to F2048 | | |

**F2 is the floor.** Practitioner ISV guides (EPC Group) suggest F4+ for real production loads in customer-facing embedded scenarios; F2 is fine for development and small demos. **Confidence: Medium — verify against [azure.microsoft.com/en-us/pricing/details/power-bi-embedded/](https://azure.microsoft.com/en-us/pricing/details/power-bi-embedded/) before quoting.**

## Pro / Premium-Per-User licenses

- **Power BI Pro:** **$14/user/month** (raised from $10 in April 2025 — no grandfathering for new licenses)
- **Power BI Premium-Per-User (PPU):** **$24/user/month** (raised from $20 in April 2025)
- **For App-Owns-Data scenario:** end users do NOT need PBI Pro licenses — F-SKU capacity covers them. **Only report builders and admins need Pro.**

This is why F-SKU is cost-effective for customer-facing embeds with many viewers — you pay for capacity, not per-viewer.

## App-Owns-Data vs User-Owns-Data

| Scenario | Auth | Use case |
|---|---|---|
| **App-Owns-Data** | Service principal token (MSAL) | **Customer-facing embed.** End users authenticate against the host app; the embed itself uses the service principal. F-SKU capacity covers them. |
| **User-Owns-Data** | Per-user Azure AD token | Internal embed for licensed users. Less common; usually for org-internal dashboards. |

**App-Owns-Data is the standard for SMB consulting engagements** embedding into a client's customer-facing app.

## Auth flow (App-Owns-Data)

```
[Customer logs into host app] (e.g., partner portal)
        |
        v
[Host app's backend authenticates via service principal]
   - MSAL acquires Azure AD token via client_credentials
   - Token scope: https://analysis.windows.net/powerbi/api/.default
        |
        v
[Host app calls Power BI REST API to generate embed token]
   - Includes EffectiveIdentity with username + DAX role(s)
   - Token is short-lived (default 1 hour; configurable to 5-15 min for production)
        |
        v
[Embed token returned to host app's frontend]
        |
        v
[Frontend uses powerbi-client JS library to render the embed]
   - iframe managed by the SDK
   - DAX role enforces tenant scope at query time
```

## DAX role-based RLS

Tenant isolation lives in **DAX roles** at the semantic-model layer:

```dax
[Tenant Filter Role] =
  CALCULATETABLE(
    'fact_orders',
    'fact_orders'[TenantID] = USERNAME()
  )
```

Applied via Workspace → Manage Roles → Add Role → DAX filter expression. The `EffectiveIdentity` in the embed token specifies:

- `username` — the value that `USERNAME()` returns inside DAX
- `roles` — array of DAX role names to apply
- `datasets` — which datasets the identity applies to

**Service principal connecting the model bypasses any underlying-DB RLS by necessity** — the model needs all tenants' rows to slice them per-viewer.

## The DirectQuery + EffectiveIdentity narrow exception

When the embed uses **DirectQuery** mode (queries hit the source DB at runtime, not the imported model), EffectiveIdentity can pass user identity through to the source. **In that narrow mode, DB-level RLS DOES participate** — Postgres RLS, SQL Server Row-Level Security, etc.

For **Import mode** (much more common for customer-facing embeds): the model holds all tenants' data; DAX roles slice per-viewer.

## Coordination with `power-platform` plugin

When the engagement involves Power BI Embedded:

- **`power-platform/power-bi-engineer`** owns: DAX authoring, semantic-model design, PBIP source control + Azure DevOps integration, refresh/gateway issues, Power BI + solution ALM coordination
- **`data-platform/dashboard-builder`** owns: the embed pattern (App-Owns-Data flow, MSAL acquisition, embed-token issuance), CSP/iframe-sandboxing of the embed surface in the host app, multi-tenancy across non-Microsoft data layers

**Boundary:** if the question is "how do I write this DAX measure?" → power-platform. If the question is "how do I embed this dashboard into my client's React app?" → data-platform. Often both plugins coordinate on a single engagement.

## Common gotchas

1. **CSP nonces required** for Power BI embed iframe — Microsoft requires CSP nonce values for the embed page's inline scripts
2. **App-Owns-Data needs the service principal added to the Power BI tenant** — separate Azure AD app + Power BI workspace contributor role
3. **F2 doesn't auto-scale** — if the customer-facing dashboard sees a load spike, F2 throttles. Reserved F4+ for production is the common pattern.
4. **DAX role testing is non-trivial** — there's no `SELECT * FROM role_evaluation` like there is for Postgres RLS. The engagement's CI must include synthetic-data tests that verify each role.
5. **Deny-by-default workspace settings** — viewers with no role assigned should see *nothing*; this is workspace-config, not DAX-config
6. **Token expiry** — Power BI default embed-token lifetime is 1 hour; for production, request 5-15 min and have the host app refresh

## Defense-in-depth posture

- **Primary:** DAX role at the semantic-model layer
- **Backstop for Import mode:** role-coverage tests in CI + deny-by-default workspace
- **Backstop for DirectQuery + EffectiveIdentity:** source DB RLS if same identity passes through

## Recommended stack for a Power BI Embedded engagement

1. **Source data:** wherever the client's data lives (Dynamics 365, Fabric Lakehouse, Azure SQL, on-prem SQL Server via gateway)
2. **Semantic model:** Power BI dataset; PBIP source-controlled in Azure DevOps (route to `power-platform/power-bi-engineer`)
3. **DAX RLS:** role per tenant scope (e.g., `Tenant_Viewer_Role`)
4. **Capacity:** F2 reserved for development; F4+ reserved for production customer-facing
5. **Embed pattern:** App-Owns-Data via MSAL service principal; powerbi-client JS in host React app
6. **Host CSP:** `frame-ancestors` allowing client's app domain; nonce-based script-src
7. **CI tests:** DAX role coverage tests; embed-token-acquisition smoke test; cross-boundary denial test

## Anti-patterns

- F2 capacity recommended for production customer-facing load without flagging that F4+ is the typical floor for real workloads
- "User-Owns-Data" pattern for a customer-facing embed (wrong model — needs App-Owns-Data)
- DAX role with `USERNAME()` filter but no test that verifies enforcement
- Embed page without CSP nonces (Microsoft requires them)
- Service principal not added to the Power BI workspace (auth will succeed at the Azure AD layer but fail at the Power BI layer)
- Long-lived embed tokens (>30 min)
- Pulling Postgres RLS into an Import-mode Power BI engagement (the model needs all tenants — RLS in source is irrelevant)

## Refresh triggers

- F-SKU pricing restructure (Microsoft does annual changes)
- Power BI Pro / PPU price changes
- Fabric OneLake security model material change
- App-Owns-Data flow changes (rare but possible)
- New embed scenario (e.g., Teams-embedded customer-facing dashboards) becomes meaningful
