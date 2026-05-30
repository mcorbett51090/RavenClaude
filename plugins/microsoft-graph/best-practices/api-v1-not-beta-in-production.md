# v1.0 not /beta in production — beta is unversioned and can break without notice

**Status:** Absolute rule — shipping `/beta` to production is a risk decision someone must own out loud, never a silent default.

**Domain:** Web API / versioning

**Applies to:** `microsoft-graph`

---

## Why this exists

Microsoft Graph exposes two endpoints: `v1.0` (generally available, supported, stable contract) and `beta` (preview — APIs and behaviors can change, and may never ship to GA). A `/beta` dependency that works today can change shape, change behavior, or disappear on any deployment, with no deprecation window and no support path. Teams reach for beta because a capability is only there yet — which is fine for a spike, and a latent production incident when it quietly lands in shipped code.

## How to apply

Default every production call to `https://graph.microsoft.com/v1.0/...`. Use `beta` only for development/evaluation, and when a needed capability is beta-only, surface that as an explicit, flagged decision.

```http
GET https://graph.microsoft.com/v1.0/users?$select=id,displayName    # production
GET https://graph.microsoft.com/beta/users?$select=id,signInActivity # preview-only field — flag it
```

```csharp
// The .NET SDK defaults to v1.0; opting into beta is an explicit, visible choice
// (e.g. the separate Microsoft.Graph.Beta package / a beta base URL) — never accidental.
```

**Do:**
- Pin production to `v1.0`.
- If a feature is beta-only, document it, flag it for review, and track when/if it reaches GA so you can migrate off beta.
- Re-verify beta endpoints before quoting them — shape and availability drift.

**Don't:**
- Copy a beta URL from a docs example into shipped code without flagging it.
- Mix `v1.0` and `beta` URLs in one `$batch` and expect uniform behavior — a `v1.0` URL targeting a beta-only capability fails (e.g. `405`).
- Assume beta behavior equals the eventual v1.0 behavior — it isn't a contract.

## Edge cases / when the rule does NOT apply

Some genuinely useful capabilities live only in beta (certain reporting/identity-protection properties, newer resource types). Using them is legitimate **when the trade-off is acknowledged** — wrap the beta call behind an interface you can swap, and own the migration risk. Dev/test/spike environments may use beta freely. Which capabilities are beta-only is constantly changing — `[verify-at-build]`.

## See also

- [`./api-use-the-sdk-not-raw-http-for-resilience.md`](./api-use-the-sdk-not-raw-http-for-resilience.md) — the SDK makes the version an explicit choice
- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md) — owns the v1.0-vs-beta call
- [`../CLAUDE.md`](../CLAUDE.md) — house opinion #9 ("never ship `/beta` to production without flagging it")
- [Versioning and support in Microsoft Graph](https://learn.microsoft.com/graph/versioning-and-support) — authoritative

## Provenance

From the Microsoft Graph versioning guidance and the team constitution's house opinion #9 (retrieved/aligned 2026-05-30). The set of beta-only capabilities is inherently volatile and must be re-checked at build time — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
