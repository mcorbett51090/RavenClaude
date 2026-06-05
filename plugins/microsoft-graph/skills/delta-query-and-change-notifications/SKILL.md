---
name: delta-query-and-change-notifications
description: "Playbook for tracking Microsoft Graph resource changes using delta queries (polling) and change notifications (webhooks/subscriptions) — choosing between them, bootstrapping delta tokens, handling subscription lifecycle, and the rich-notification decryption hand-off. Owned by graph-workloads-engineer."
---

# Delta Query and Change Notifications

## When to invoke

- Building a sync that needs to detect "what changed" since the last run.
- Deciding between delta queries (polling) and change notifications (webhooks).
- A subscription is silently expiring and missing events.
- Handling rich (encrypted) notification payloads.

## Decision: delta query vs change notification

| Dimension | Delta query (polling) | Change notification (webhook/subscription) |
|---|---|---|
| Latency | Minutes (your poll interval) | Near-real-time (seconds) |
| Infra needed | None beyond your app | An HTTPS endpoint that Graph can reach |
| Delivery guarantee | Pull — you control the window | At-least-once push (duplicate handling required) |
| State management | Store the `@odata.deltaLink` token | Store subscription ID + expiry + renewal logic |
| Best for | Batch sync, nightly jobs, catch-up on restart | Real-time triggers, event-driven pipelines |

**Rule:** if near-real-time response is required → change notifications. If the use case tolerates minutes of latency or runs on a schedule → delta query. Many robust systems use both: delta queries for catch-up on app restart, change notifications for real-time.

## Delta query — bootstrap and iterate

```python
# Phase 1: initial full sync (use $deltaToken=latest for a clean start)
url = "https://graph.microsoft.com/v1.0/users/delta?$select=id,displayName,mail"
headers = {"Authorization": f"Bearer {token}"}

delta_link = None
while url:
    resp = httpx.get(url, headers=headers).json()
    for user in resp.get("value", []):
        process_user(user)  # upsert into your store
    url = resp.get("@odata.nextLink")
    delta_link = resp.get("@odata.deltaLink", delta_link)

store_delta_link(delta_link)  # persist — this is your cursor

# Phase 2: subsequent polls — only changed users returned
url = load_delta_link()
# ... same loop; only changed/deleted users arrive
```

**Deleted resource handling:** Graph signals a deletion with `"@removed": {"reason": "deleted"}` in the resource body. Your sync must process removals, not just upserts.

## Change notifications — subscription lifecycle

A subscription is **stateful and expires**. Expiry = silent event loss. Design for it from day one.

### Create a subscription

```http
POST https://graph.microsoft.com/v1.0/subscriptions
Content-Type: application/json

{
  "changeType": "created,updated,deleted",
  "notificationUrl": "https://app.contoso.com/graph/notify",
  "resource": "me/mailFolders('Inbox')/messages",
  "expirationDateTime": "2026-06-12T18:00:00Z",
  "clientState": "<secret-for-validation>"
}
```

Expiry limits (v1.0, `[verify-at-build]`):
- Mail/Calendar/Contacts: 4230 minutes (~3 days)
- Users/Groups/Drive: 43 200 minutes (30 days)
- Teams channels/chats: 60 minutes

### Validation handshake

Graph sends a `validationToken` query parameter to your `notificationUrl` before creating the subscription. Your endpoint must:
1. Return HTTP 200 with `Content-Type: text/plain` and the `validationToken` value as the body.
2. Respond within 10 seconds.

```python
# FastAPI example
@app.post("/graph/notify")
async def handle_notification(request: Request, validationToken: str = None):
    if validationToken:
        return PlainTextResponse(validationToken, status_code=200)
    # ... handle real notification payload
```

### Renewal strategy

Renew subscriptions before they expire — not after. Silence = expiry, not "no events."

```python
import datetime

RENEW_BEFORE_EXPIRY_MINUTES = 60

def should_renew(expiration_iso: str) -> bool:
    expiry = datetime.datetime.fromisoformat(expiration_iso.replace("Z", "+00:00"))
    return expiry - datetime.datetime.now(datetime.timezone.utc) < \
           datetime.timedelta(minutes=RENEW_BEFORE_EXPIRY_MINUTES)

# Run in a background scheduler every 30 minutes
for sub in load_all_subscriptions():
    if should_renew(sub["expirationDateTime"]):
        renew_subscription(sub["id"])
```

### Lifecycle notifications

For long-running subscriptions, Graph sends lifecycle notifications to a `lifecycleNotificationUrl` signalling `subscriptionRemoved` or `missed`. Handle both:

- `subscriptionRemoved` → re-create the subscription and run a delta-query catch-up.
- `missed` → run a delta-query catch-up to recover missed events.

## Rich notifications and payload decryption

Rich notifications deliver the changed resource inline (encrypted). **This involves key management — escalate the decryption-key rotation plan to `ravenclaude-core/security-reviewer`.**

Summary:
1. Generate an asymmetric key pair; provide the public key in the subscription's `encryptionCertificate` field.
2. Graph encrypts the notification payload with a symmetric key, then encrypts the symmetric key with your public key.
3. Your handler decrypts the symmetric key with your private key, then decrypts the payload.
4. Rotate the asymmetric key pair before the certificate expires; re-create the subscription with the new public key.

## Pitfalls

- A subscription with no renewal logic — it silently expires in 3 days; your app stops receiving events with no error.
- Not storing the `@odata.deltaLink` between runs — the next restart does a full sync instead of incremental.
- Returning `HTTP 200` for a validation request without echoing the `validationToken` body — Graph fails to create the subscription with no useful error.
- Processing only `updated` changeType and omitting `deleted` — deletions pile up silently.
- Storing the decryption private key in the app config file — rotate via Key Vault; never on disk.
