# Subscriptions are stateful and expire — renew before expiry and handle lifecycle notifications

**Status:** Absolute rule — a change-notification subscription with no renewal timer and no lifecycle handling is a silent outage, not a working integration.

**Domain:** Web API / Change notifications

**Applies to:** `microsoft-graph`

---

## Why this exists

A Microsoft Graph subscription has a **limited, resource-specific lifetime** set at creation via `expirationDateTime`. Once it passes, Graph deletes the subscription and stops delivering — silently. There is no error; you find out from the gap in your data. Separately, the **access token** Graph holds for your endpoint expires on a *different, shorter* clock (generally within ~1 hour), and an admin can revoke the app's permission at any time. The only reliable way to keep delivery flowing is to (1) **renew before `expirationDateTime`** and (2) subscribe to **lifecycle notifications** so Graph tells you when to reauthorize. Skipping either is the single most common change-notification production failure.

## How to apply

Set `lifecycleNotificationUrl` at create time, renew on a timer keyed to the resource's max lifetime, and respond to `reauthorizationRequired`.

```http
POST https://graph.microsoft.com/v1.0/subscriptions
Content-Type: application/json

{
  "changeType": "created,updated",
  "notificationUrl": "https://contoso.example/api/notifications",
  "lifecycleNotificationUrl": "https://contoso.example/api/lifecycle",
  "resource": "/teams/{team-id}/channels/{channel-id}/messages",
  "expirationDateTime": "2026-05-30T18:23:45.000Z",
  "clientState": "<opaque-secret-from-key-vault>"
}
```

Renew (this **also reauthorizes** the endpoint — refreshing the access token):

```http
PATCH https://graph.microsoft.com/v1.0/subscriptions/{id}
Content-Type: application/json

{ "expirationDateTime": "2026-05-30T18:53:45.000Z" }
```

**Do:**

- Renew at roughly **half** the resource's max lifetime so a transient failure has a retry window — e.g. Teams `chatMessage` ≈ 60 min, so renew every ~30 min; a SharePoint list ≈ 30 days. `[verify-at-build]`
- Subscribe to lifecycle notifications and handle `reauthorizationRequired` by calling **`PATCH /subscriptions/{id}` with a fresh `expirationDateTime`** (one request reauthorizes *and* renews).
- Keep a **delta-query backstop**: notifications that occur while delivery is paused (token expired, awaiting reauthorization) are **lost** — re-sync with a delta query to fill the gap.

**Don't:**

- Create a subscription without a `lifecycleNotificationUrl` — you forfeit the early warning and have to poll-guess expiry. (Existing subscriptions can't add it; you must delete and recreate.)
- Issue a `reauthorize` POST and a renewing `PATCH` for the same subscription within a 10-minute window — that can cause subscription-state inconsistencies. Use a single `PATCH` to do both.
- Assume the access-token clock equals the subscription clock — they differ; the token expires first.

## Edge cases / when the rule does NOT apply

Max lifetimes are per-resource and **volatile** — confirm the exact ceiling for your resource against the subscription resource type's lifetime table `[verify-at-build]`. Notifications delivered through **Azure Event Hubs / Event Grid** don't validate the `notificationUrl`, so endpoint-validation specifics differ (renewal still applies). A request with `expirationDateTime` under 45 minutes out is auto-clamped to 45 minutes.

## See also

- [`./notify-validate-the-handshake-and-verify-the-sender.md`](./notify-validate-the-handshake-and-verify-the-sender.md) — the create-time handshake + per-notification sender verification
- [`./notify-encrypt-rich-payloads-and-guard-the-key.md`](./notify-encrypt-rich-payloads-and-guard-the-key.md) — rich-notification key handling
- [`../knowledge/workloads-notifications-decision-trees.md`](../knowledge/workloads-notifications-decision-trees.md) — poll/delta vs subscription, basic vs rich
- [`../agents/graph-workloads-engineer.md`](../agents/graph-workloads-engineer.md) — owns the subscription lifecycle
- [Receive change notifications through webhooks — Subscription lifecycle](https://learn.microsoft.com/graph/change-notifications-delivery-webhooks#subscription-lifecycle) — authoritative
- [Reduce missing subscriptions and change notifications](https://learn.microsoft.com/graph/change-notifications-lifecycle-events) — reauthorizationRequired handling

## Provenance

From the Microsoft Learn change-notifications webhook + lifecycle pages (retrieved 2026-05-30 via Microsoft Learn MCP), codifying team house opinion #7 ("subscriptions are stateful and expire"). The "renew also reauthorizes" and "don't reauthorize + PATCH within 10 minutes" rules are quoted directly from the lifecycle-events page. Max-lifetime numbers are per-resource and version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
