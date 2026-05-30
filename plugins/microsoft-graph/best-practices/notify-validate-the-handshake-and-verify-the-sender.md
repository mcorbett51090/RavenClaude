# Validate the notificationUrl handshake, then verify every notification's sender

**Status:** Absolute rule — a webhook endpoint that skips the validation handshake never receives a subscription, and one that processes notifications without verifying the sender is an injection surface.

**Domain:** Web API / Change notifications / Security

**Applies to:** `microsoft-graph`

---

## Why this exists

Change notifications arrive at a **publicly accessible HTTPS endpoint** — which means anyone can POST to it. Two distinct controls protect you, and both are commonly skipped. First, at **subscription-create time** Graph proves it can reach your endpoint with a one-time `validationToken` handshake; fail it and Graph **refuses to create the subscription** (so this one is self-enforcing, but the exact response format trips people up). Second, on **every delivered notification** you must prove the notification actually came from Graph — via the `clientState` you set (basic notifications) or the JWT `validationTokens` array (rich notifications). Without sender verification, a third party can feed your business logic fake notifications. These are different from the *lifecycle/renewal* concern — this doc is about authenticity, not expiry.

## How to apply

**Handshake (create time):** Graph POSTs `?validationToken=...` to your URL. Echo the **URL-decoded plaintext** token, `200`, `text/plain`, within **10 seconds**.

```http
POST https://contoso.example/api/notifications?validationToken={opaqueToken}
Content-Type: text/plain; charset=utf-8
```

```
HTTP/1.1 200 OK
Content-Type: text/plain

{the URL-decoded validationToken, verbatim, no HTML/JSON encoding}
```

**Sender verification (every notification):** respond fast, then verify.

- **Basic:** compare the `clientState` in the payload to the secret you set on the subscription. Mismatch → discard.
- **Rich (resource data):** validate **every** JWT in `validationTokens` (issuer, audience = your app ID, not expired) using MSAL or a JWT library. Any failure → treat the whole notification as suspicious.

```python
# Respond 202 immediately (do NOT wait on validation), then verify and process
def handle(req):
    if "validationToken" in req.query:                 # create-time handshake
        return Response(req.query["validationToken"], 200, content_type="text/plain")
    queue.put(req.body)                                 # persist first
    return Response(status=202)                         # respond within 3 s
    # async worker: verify clientState / each validationTokens JWT, THEN process
```

**Do:**

- Return the validation token in **plain text** — an HTML/URL-encoded token fails validation.
- Respond `202 Accepted` to a real notification within the 3-second window, queue it, and verify+process **out of band**. Accept-then-ignore hides validation results from attackers and avoids delivery retries.
- Verify `clientState` / `validationTokens` **before** acting on the payload — even though you already responded.

**Don't:**

- Run business logic synchronously in the request handler — slow responses get your endpoint marked "slow"/"drop" and notifications are dropped unrecoverably.
- Trust a notification because it reached your URL — verify the sender.
- Echo any value containing HTML/JS (Graph never sends it); escaping protects against XSS-style abuse of the endpoint.

## Edge cases / when the rule does NOT apply

`validationTokens` is **only** present for rich (resource-data) notifications delivered via webhooks; basic notifications rely on `clientState`. Event Hubs / Event Grid delivery does **not** send validation tokens (Graph doesn't validate that `notificationUrl`), so JWT verification doesn't apply there. A `null` `validationTokens` on a rich subscription signals an app-configuration problem (the encryption couldn't happen), not a tampering attempt — fix `appRoleAssignmentRequired`/app-role config.

## See also

- [`./notify-subscriptions-need-renewal-and-lifecycle-handling.md`](./notify-subscriptions-need-renewal-and-lifecycle-handling.md) — the expiry/renewal side
- [`./notify-encrypt-rich-payloads-and-guard-the-key.md`](./notify-encrypt-rich-payloads-and-guard-the-key.md) — decrypting after the JWTs validate
- [`../agents/graph-workloads-engineer.md`](../agents/graph-workloads-engineer.md) — owns notification security (escalates key/secret to security-reviewer)
- [Receive change notifications through webhooks — Create a subscription](https://learn.microsoft.com/graph/change-notifications-delivery-webhooks#create-a-subscription) — handshake spec
- [Set up change notifications with resource data — Validate the authenticity of notifications](https://learn.microsoft.com/graph/change-notifications-with-resource-data#validate-the-authenticity-of-notifications) — validationTokens

## Provenance

From the Microsoft Learn change-notifications webhook + resource-data pages (retrieved 2026-05-30 via Microsoft Learn MCP). The 10-second handshake window, plaintext-token requirement, 3-second delivery window, and "respond before validating" guidance are quoted directly. The `clientState`-vs-`validationTokens` split by notification type is from the same source.

---

_Last reviewed: 2026-05-30 by `claude`_
