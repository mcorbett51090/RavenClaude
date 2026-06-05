# Auth-identity scenarios bank

> Unverified, dated, scope-tagged narratives from real end-user-auth & identity engagements. War stories of "we hit X auth problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real authentication / identity work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and [`../best-practices/`](../best-practices/); scenarios never replace it. Every concrete auth/secret/token change still routes through `ravenclaude-core/security-reviewer` (CLAUDE.md §8).

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: auth-identity
product: <supabase-auth | oauth-oidc | webauthn-passkeys | generic | etc.>
product_version: <"2026.06" | "unknown">
scope: tenant-specific | version-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context
## Attempts
## Resolution
```

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-token-in-localstorage-xss-exfil.md`](2026-06-05-token-in-localstorage-xss-exfil.md) | likely-general | xss, localstorage, token-theft, httponly-cookie, session-fixation | high |
| [`2026-06-05-oauth-redirect-uri-and-pkce-misconfig.md`](2026-06-05-oauth-redirect-uri-and-pkce-misconfig.md) | likely-general | oauth, redirect-uri, pkce, implicit-flow, open-redirect | high |
| [`2026-06-05-passkey-rollout-no-fallback-lockout.md`](2026-06-05-passkey-rollout-no-fallback-lockout.md) | likely-general | passkeys, webauthn, fallback, account-recovery, conditional-ui | medium |
| [`2026-06-05-app-authz-filter-vs-rls-tenant-leak.md`](2026-06-05-app-authz-filter-vs-rls-tenant-leak.md) | likely-general | authorization, rls, tenant-isolation, idor, supabase | high |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `best-practices/`. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
