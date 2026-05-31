---
description: Design passwordless identity and least-privilege RBAC for an Azure workload — managed identity / workload-identity-federation for runtime and CI/CD, narrowly-scoped built-in or custom roles at RG scope, PIM for elevation, no standing Owner.
argument-hint: "[the workload + access need, e.g. 'app reading Key Vault + a CI/CD pipeline']"
---

# Design identity and RBAC

You are running `/azure-cloud:design-identity-and-rbac`. Model the identity and authorization for what the user described (`$ARGUMENTS`), following this plugin's `entra-identity-engineer` discipline — passwordless by default, least-privilege always.

## When to use this

A workload or pipeline needs Azure access designed (or an existing over-broad grant needs tightening). If the question is purely "which network can reach this resource," that's `/azure-cloud:harden-network-and-data-planes`; this command owns *who can do what*.

## Steps

1. **Pick the auth mechanism passwordless:** managed identity for app-to-Azure-service auth; workload identity federation (OIDC trust) for CI/CD — no client secret on either side (`passwordless-by-default.md`). Any unavoidable third-party secret goes in Key Vault with a rotation policy, referenced, never inlined.
2. **Scope RBAC to the RG or resource,** not the subscription/MG — the path-of-least-resistance `Contributor`-at-subscription is exactly how an estate ends up with a dozen do-anything principals (`identity-rbac-least-privilege-and-custom-roles.md`).
3. **Reach for the most specific built-in role** that grants exactly the needed data/control actions (`Key Vault Secrets User`, `Storage Blob Data Reader`) over a broad one (same file).
4. **Write a custom role only when no built-in fits** — enumerate explicit `Actions`/`DataActions` with RG-scoped `assignableScopes`, never a `*` wildcard, and never a `DataActions` role at MG scope (RBAC forbids it) (same file).
5. **Grant platform/admin elevation through PIM** — eligible/just-in-time/time-bound/approval-gated, not a standing assignment; keep subscription owners ≤3 (same file).
6. **For the CI/CD federation:** configure a federated credential on the Entra app/UAMI per pipeline and pass only the public client/tenant/subscription IDs (`passwordless-by-default.md`). Use the `templates/entra-identity-design.md` shape.

## Guardrails

- Never store an `AZURE_CREDENTIALS` JSON or service-principal client secret when federation is available; never commit any credential, even temporarily (the hook flags it).
- Never assign `Owner`/`Contributor` at subscription/MG scope in IaC (the hook flags it) or hand out standing `Owner`.
- The identity/secret/RBAC/federated-credential *design* (which identity, which scope, which subject claim) is a security decision and routes to `ravenclaude-core/security-reviewer` — mandatory. This plugin supplies the craft; core owns the verdict.
