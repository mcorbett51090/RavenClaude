---
scenario_id: 2026-06-05-app-authz-filter-vs-rls-tenant-leak
contributed_at: 2026-06-05
plugin: auth-identity
product: supabase-auth
product_version: "2026.06"
scope: likely-general
tags: [authorization, rls, tenant-isolation, idor, supabase]
confidence: high
reviewed: false
---

## Problem

A multi-tenant SaaS authenticated users correctly with Supabase Auth (Google SSO, valid sessions, server-verified ID tokens — the *authentication* was sound) but enforced **tenant isolation in application code only**: every query carried a `WHERE tenant_id = :currentUserTenant` filter assembled in the API layer. A penetration test found an **IDOR**: one endpoint built its query from a client-supplied `tenant_id` body field instead of the session's tenant, and another (a new "export" route added later) simply forgot the filter. Because the database had **no Row-Level Security**, the missing/forged filter meant a correctly-authenticated user of Tenant A could read Tenant B's rows. The auth was perfect; the *authorization boundary* was a per-query convention that one missed query broke.

## Context

- Surface: Supabase Postgres behind an API; users authenticate via auth-identity's lane, but row scope was enforced in app code, not the database.
- Constraint: this is the **authenticate-the-person vs authorize-the-data** boundary (CLAUDE.md §0). auth-identity establishes a trustworthy `auth.uid()`; **the row/tenant scope of what that identity may read is the `data-platform` plugin's RLS lane** — app-code tenant filtering is not the load-bearing control. A control that depends on *every* query remembering to filter fails the moment one doesn't.
- Concrete change to the authorization boundary on real tenant data → **mandatory `ravenclaude-core/security-reviewer`**, and the RLS work seams to `data-platform` (CLAUDE.md §0/§8).

## Attempts

- Tried: "audit every query and add the missing `WHERE tenant_id` + stop trusting the body field." Outcome: fixes the two known holes but not the *class* — the boundary still lives in app code, so the next new endpoint can reintroduce the leak. Treated as necessary cleanup, not the fix.
- Tried: move the tenant boundary into the database as **Postgres Row-Level Security** keyed on the verified `auth.uid()` → tenant mapping (data-platform's `rls-policy-authoring` lane), so the database itself refuses cross-tenant rows regardless of what the app query says. Outcome: a forgotten or forged app-layer filter can no longer leak — the closest-to-data control holds even when app code is wrong. auth-identity's job ends at handing data-platform the trustworthy `auth.uid()`; data-platform owns the policy.
- Tried (completing the seam): for the embedded analytics dashboard, the per-tenant view now uses a **short-lived embed-JWT carrying the tenant claim** (data-platform's `jwt-embed-issuance`) rather than an app-assembled filter, with RLS scoping the rows under it. Outcome: the gate (auth-identity) and the row scope (data-platform) are now two separate, correctly-owned controls.

## Resolution

The exposure was **treating app-code tenant filtering as the auth boundary** — conflating authentication (sound here) with authorization (a per-query convention). The fix moves the boundary to **Postgres RLS on the verified `auth.uid()`** (data-platform's lane), keeping auth-identity's job to establishing the trustworthy identity and handing off the subject claim. A gate that lets the right person reach the wrong tenant's rows still leaks.

**Action for the next engineer hitting this pattern:** when a multi-tenant app enforces row scope with app-code `WHERE` filters, that *is* the finding — even when the login is flawless. Authentication being correct does not make authorization correct. Establish the identity here (auth-identity), then move row/tenant scope to **Postgres RLS keyed on `auth.uid()`** in the `data-platform` lane; never make an app-code filter the load-bearing isolation control. Apply [`authenticate-the-person-authorize-the-data-separately`](../best-practices/authenticate-the-person-authorize-the-data-separately.md), traverse the **gate-the-dashboard** tree in [`../knowledge/auth-identity-decision-trees.md`](../knowledge/auth-identity-decision-trees.md) to find the seam, and route to `security-reviewer` + `data-platform`.

**Sources (retrieved 2026-06-05):**
- Supabase — Row Level Security; `auth.uid()` in policies — https://supabase.com/docs/guides/database/postgres/row-level-security
- OWASP — Broken Object Level Authorization (IDOR), API Security Top 10 (API1) — https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
- Plugin best-practices: [`../best-practices/authenticate-the-person-authorize-the-data-separately.md`](../best-practices/authenticate-the-person-authorize-the-data-separately.md); the data-platform seam in [`../CLAUDE.md`](../CLAUDE.md) §0
- Cross-plugin: [`../../data-platform/CLAUDE.md`](../../data-platform/CLAUDE.md) §3 (tenant-isolation invariant) + its `rls-policy-authoring` / `jwt-embed-issuance` skills

OWASP/Supabase RLS guidance is stable but versioned; `[verify-at-use]` the current Supabase RLS docs and the live OWASP API Top-10 edition before quoting a specific clause.
