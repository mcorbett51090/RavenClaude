---
description: Design Microsoft Graph auth for an app — decide delegated vs application by "is there a signed-in user?", pick the OAuth2 flow from the client type, select the least-privilege permission, and use a certificate or managed identity, never a secret.
argument-hint: "[the client + operation, e.g. 'a nightly daemon that reads all users']"
---

# Design Graph auth

You are running `/microsoft-graph:design-graph-auth`. Design the identity, flow, permission, and credential for what the user described (`$ARGUMENTS`), following this plugin's `graph-identity-engineer` discipline — state each choice as a sentence before any auth code.

## When to use this

You're about to call Graph and need to settle the permission model and auth flow. If the permission *list already exists* and you just want it tightened/reviewed, run `/microsoft-graph:audit-graph-permissions`. The scope verdict escalates to `ravenclaude-core/security-reviewer`.

## Steps

1. **Decide delegated vs application by one question — is there a signed-in user at call time?** Yes → delegated (a *scope*, capped by the user's own rights); no (daemon/background/connector) → application (an *app role*, tenant-wide, admin-consent-only). Write it as a sentence (`identity-delegated-vs-application-is-a-design-choice.md`).
2. **Pick the OAuth2 flow from the client type** — web app w/ backend → auth-code; SPA/native → auth-code + PKCE (never implicit); daemon → client-credentials with `.default`; web API calling Graph as the user → on-behalf-of; browserless device → device-code. Never ROPC (`auth-pick-the-flow-by-client-type.md`).
3. **Select the least-privilege permission** — climb from the operation to the *smallest* scope that works (`User.Read` < `User.ReadBasic.All` < `User.Read.All` < `Directory.Read.All`); prefer `.Read` over `.ReadWrite` and resource-specific over umbrella (`identity-least-privilege-permission-selection.md`).
4. **Verify the actual least-privilege permission against the permissions reference** — the obvious-named one isn't always narrowest (e.g. reading users app-only needs only `User.Read.All`, not `Directory.Read.All`) (same file).
5. **Flag high-trust scopes loudly** — `Application.ReadWrite.All`, `AppRoleAssignment.ReadWrite.All`, `RoleManagement.*` let an app act as other identities (same file).
6. **Use a certificate or managed identity in production, never a client secret** — managed identity on Azure-hosted compute, certificate off-Azure; a secret only for short-lived local dev, never committed (`auth-certificates-not-secrets-in-production.md`).

## Guardrails

- Never reach for an application permission "so it always works" — that trades a user ceiling for tenant-wide exposure; never use a delegated permission for an unattended job.
- Never commit a secret or put one in a config shipped to clients or a notification URL.
- Permission names / flow availability are volatile — carry a retrieval date and tag `[verify-at-build]`. The scope-list verdict routes to `ravenclaude-core/security-reviewer` (mandatory); tenant identity governance (Conditional Access, PIM, B2B/B2C) routes to `azure-cloud/entra-identity`.
