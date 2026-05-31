---
description: Build a Microsoft Graph change-notification subscription that survives production — validate the create-time handshake, verify the sender per notification, renew before expiry, handle lifecycle reauthorization, and keep a delta backstop for the gap.
argument-hint: "[the resource, e.g. 'notify on new Teams channel messages']"
---

# Build change notifications

You are running `/microsoft-graph:build-change-notifications`. Build (or diagnose) the change-notification subscription for what the user described (`$ARGUMENTS`), following this plugin's `graph-workloads-engineer` discipline — a subscription with no renewal timer and no lifecycle handling is a silent outage, not an integration.

## When to use this

You need *push* — react within seconds, or avoid polling. If you only need *pull* ("what changed since last time" on a timer), use `/microsoft-graph:scaffold-delta-sync` instead; it's simpler and stateless on the Graph side.

## Steps

1. **Handle the create-time validation handshake** and verify the sender on every notification (`clientState` match) — don't trust an unverified POST to your endpoint (`notify-validate-the-handshake-and-verify-the-sender.md`).
2. **Set `lifecycleNotificationUrl` at create time** — you can't add it to an existing subscription, and without it you forfeit the early warning and have to poll-guess expiry (`notify-subscriptions-need-renewal-and-lifecycle-handling.md`).
3. **Renew before `expirationDateTime`** on a timer keyed to ~half the resource's max lifetime (Teams `chatMessage` ≈ 60 min → renew ~30 min; a SharePoint list ≈ 30 days) — the renewing `PATCH` also reauthorizes the endpoint (same file).
4. **Handle `reauthorizationRequired`** with a single `PATCH /subscriptions/{id}` + fresh `expirationDateTime` — don't issue a reauthorize POST and a renewing PATCH within a 10-minute window (same file).
5. **Keep a delta-query backstop** — notifications that occur while delivery is paused (token expired, awaiting reauth) are *lost*; re-sync with a delta query to fill the gap (`notify-subscriptions-need-renewal-and-lifecycle-handling.md`, `api-delta-for-what-changed.md`).
6. **For rich payloads, encrypt and guard the decryption key** in Key Vault, never inline (`notify-encrypt-rich-payloads-and-guard-the-key.md`).

## Guardrails

- Never create a subscription without a `lifecycleNotificationUrl`, and never assume the access-token clock equals the subscription clock — the token expires first.
- Max lifetimes are per-resource and volatile — confirm the exact ceiling against the resource type's lifetime table and tag `[verify-at-build]`.
- The decryption-key / sender-verification design is a security control → route to `ravenclaude-core/security-reviewer`. This plugin is advisory: emit the subscription JSON + handler shape the engineer runs in their own tenant.
