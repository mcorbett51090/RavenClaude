# Design for the lowest consent tier the scenario allows

**Status:** Pattern

**Domain:** Identity / Consent

**Applies to:** microsoft-graph

---

## Why this exists

Consent is where over-privilege becomes a rollout problem. Every application permission and every high-privilege delegated permission requires a tenant **admin** to consent once, tenant-wide; low-privilege delegated permissions can be self-consented by a user (where the tenant allows it). Apps that request admin-consent scopes they don't need stall at every new customer's IT desk and present a scarier consent prompt than the work warrants. Choosing the least consent tier is both a security and an adoption decision — escalate the scope/consent posture to `ravenclaude-core/security-reviewer`.

## How to apply

Pick the narrowest permission first (see [`identity-least-privilege-permission-selection.md`](./identity-least-privilege-permission-selection.md)), then let that determine the consent tier — don't reach for admin consent by default.

```
Provide admin consent once, tenant-wide, via the admin-consent endpoint:
  https://login.microsoftonline.com/{tenant}/adminconsent?client_id={app-id}

Static consent: permissions on the app registration → consented as a set.
Incremental/dynamic consent: request scopes as features need them (delegated),
  so the first prompt shows only what the first feature uses.
```

**Do:**

- Map each requested permission to its consent tier before shipping; justify any admin-consent scope.
- Use incremental consent for delegated apps so users see a minimal first prompt.
- Document the exact admin-consent URL + scope list for the customer's admin.

**Don't:**

- Request `.ReadWrite.All`/`.All` (always admin) when a resource-scoped or `.Read` permission would self-consent.
- Bundle every conceivable future scope into the initial consent set.

## Edge cases / when the rule does NOT apply

- A daemon/app-only scenario is admin-consent by definition — there's no user to self-consent; minimize the *scope*, not the tier.
- Tenants that disable user consent route **all** delegated permissions to admin — design the admin-consent flow regardless.

## See also

- [`identity-least-privilege-permission-selection.md`](./identity-least-privilege-permission-selection.md) · [`identity-delegated-vs-application-is-a-design-choice.md`](./identity-delegated-vs-application-is-a-design-choice.md) · [`identity-resource-scoped-over-tenant-wide.md`](./identity-resource-scoped-over-tenant-wide.md)
- [`knowledge/identity-auth-decision-trees.md`](../knowledge/identity-auth-decision-trees.md) "user vs admin consent" tree
- [`../agents/graph-identity-engineer.md`](../agents/graph-identity-engineer.md) — escalates to `ravenclaude-core/security-reviewer`

## Provenance

Team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3 house opinion 1, §8) + the Microsoft identity consent framework. Per-permission consent requirements are volatile — `[verify-at-build]` against the current permissions reference.

---

_Last reviewed: 2026-05-30 by `claude`_
