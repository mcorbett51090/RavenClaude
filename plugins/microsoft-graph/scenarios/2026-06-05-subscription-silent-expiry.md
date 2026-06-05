---
scenario_id: 2026-06-05-subscription-silent-expiry
contributed_at: 2026-06-05
plugin: microsoft-graph
product: graph-api
product_version: "v1.0"
scope: likely-general
tags: [change-notifications, subscription, renewal, lifecycle, webhook]
confidence: high
reviewed: false
---

## Problem

A Teams compliance integration subscribed to `chatMessage` change notifications to capture messages in near-real-time. It ran fine for the first hour of a demo, then silently stopped delivering notifications — no error, no alert, just no more webhook POSTs. Messages sent after the gap were never captured. Because nothing *failed* (the subscription simply expired), monitoring showed green while the integration was effectively dead.

## Constraints context

- `chatMessage` subscriptions have a very short maximum lifetime — **expire in ~60 minutes** `[verify-at-use]`; Microsoft's own guidance is to renew every ~30 minutes for buffer.
- The team had set `expirationDateTime` to the max and assumed "max = set it and forget it." There was no renewal loop and no lifecycle-notification handling.
- This was a per-chat subscription pattern across many chats, so even with renewal, renewing thousands of subscriptions on a 30-minute cadence is itself a load concern (a reason to prefer a coarser subscription where possible).

## Attempts

- Tried: setting `expirationDateTime` to the maximum and nothing else. Failed — every subscription expires; the max for `chatMessage` is ~1 hour, so "max" still dies mid-session. Expiry is silent: no error is raised, notifications just stop.
- Tried: a fixed cron that re-created subscriptions hourly. Partially worked but had gaps (a few minutes of missed messages between expiry and the next cron tick) and created duplicate subscriptions when the old one hadn't actually expired.
- Tried (worked): (1) a **renewal loop** that PATCHes `expirationDateTime` *before* expiry (renew at ~50% of lifetime, e.g. every 30 min for a 60-min resource); (2) a **`lifecycleNotificationUrl`** to receive lifecycle events — `reauthorizationRequired` (renew/reauthorize), `subscriptionRemoved` (recreate), and `missed` (the signal to **resync via a delta query** to backfill the gap); (3) on any detected gap, reconcile by reading messages with delta rather than assuming the webhook stream was complete.

## Resolution

A change-notification subscription is **stateful and expires**, and expiry is **silent** — "green monitoring" is not evidence it's alive. A correct subscription has three parts beyond creation: a **renewal strategy** (PATCH before expiry, well inside the per-resource max), **lifecycle-notification handling** (`reauthorizationRequired` / `subscriptionRemoved` / `missed`), and a **resync path** (delta query) for any missed window, because webhooks are best-effort and a notification can be dropped even when the subscription is healthy. For rich notifications (`includeResourceData: true`) there is an additional decryption-key dimension and the lifetime is shorter still — that key handling escalates to `ravenclaude-core/security-reviewer` (CLAUDE.md §3 #7).

**Action for the next engineer:** if a webhook integration "just stops" with no error, check subscription expiry first — it's almost always an un-renewed subscription. Build renewal + a `lifecycleNotificationUrl` + a delta resync path from day one; don't rely on `expirationDateTime = max`. Prefer the coarsest subscription that meets the need over thousands of per-entity subscriptions you must renew on a tight cadence.

**Sources (retrieved 2026-06-05):**
- Change notifications — subscription lifetime / maximum expiration per resource — https://learn.microsoft.com/graph/change-notifications-overview#subscription-lifetime
- Reduce missing subscriptions and change notifications (lifecycle: reauthorizationRequired, subscriptionRemoved, missed) — https://learn.microsoft.com/graph/change-notifications-lifecycle-events
- Teams chatMessage subscription renewal (~60 min expiry, renew ~30 min) — https://learn.microsoft.com/graph/teams-embed-within-own-app#step-8-renew-change-notification-subscriptions

Expiration numbers are volatile and per-resource — `[verify-at-use]`. Cross-reference: [`../best-practices/notify-subscriptions-need-renewal-and-lifecycle-handling.md`](../best-practices/notify-subscriptions-need-renewal-and-lifecycle-handling.md), [`../best-practices/notify-validate-the-handshake-and-verify-the-sender.md`](../best-practices/notify-validate-the-handshake-and-verify-the-sender.md), [`../best-practices/notify-encrypt-rich-payloads-and-guard-the-key.md`](../best-practices/notify-encrypt-rich-payloads-and-guard-the-key.md), the [`delta-query-and-change-notifications`](../skills/delta-query-and-change-notifications/SKILL.md) skill, the [`change-notification-subscription`](../templates/change-notification-subscription.md) template, and [`workloads-notifications-decision-trees.md`](../knowledge/workloads-notifications-decision-trees.md).
