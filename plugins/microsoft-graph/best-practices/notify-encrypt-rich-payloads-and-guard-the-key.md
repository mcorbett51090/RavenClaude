# Rich notifications carry encrypted payloads — verify the signature and guard the private key

**Status:** Absolute rule — the decryption private key for rich notifications is a security control; it lives in Key Vault and its handling escalates to security review, never decided silently.

**Domain:** Web API / Change notifications / Security

**Applies to:** `microsoft-graph`

---

## Why this exists

A **rich** (resource-data) subscription (`includeResourceData: true`) ships the full changed resource *inside the notification*, encrypted, so you skip a follow-up GET. That convenience hands you a **private key that can decrypt customer data** — mail bodies, chat messages, meeting rosters. If that key leaks, anyone who can intercept (or replay) notifications can read the data. So rich notifications add three obligations basic ones don't: provide an encryption certificate at subscribe time, **verify the payload signature before decrypting** (so you never process tampered data), and **manage the private key as a secret** — Key Vault storage, rotation, least access. Treating the key as "just config" is the failure this rule prevents.

## How to apply

Subscribe with a public-key certificate; decrypt with the matching private key after the signature check.

```http
POST https://graph.microsoft.com/v1.0/subscriptions
Content-Type: application/json

{
  "changeType": "created",
  "notificationUrl": "https://contoso.example/api/notifications",
  "lifecycleNotificationUrl": "https://contoso.example/api/lifecycle",
  "resource": "/teams/{team-id}/channels/{channel-id}/messages",
  "includeResourceData": true,
  "encryptionCertificate": "<base64 Base64-encoded X.509 PUBLIC key only>",
  "encryptionCertificateId": "myCertV2",
  "expirationDateTime": "2026-05-30T18:23:45.000Z",
  "clientState": "<opaque-secret>"
}
```

Decryption is two-step (per-item symmetric key, RSA-wrapped). Reverse it **per item**:

1. Match `encryptedContent.encryptionCertificateId` to the right private key in your store.
2. RSA-decrypt `dataKey` with your private key using **OAEP** padding → the symmetric key.
3. Compute **HMAC-SHA256** over `data` with that symmetric key; compare to `dataSignature`. **If they differ, the payload is tampered — discard, do not decrypt.**
4. Only then AES-decrypt `data` to the resource JSON.

**Do:**

- Generate an **RSA 2048–4096-bit** cert; export **public key only** (Base64 X.509) for `encryptionCertificate`. Self-signed is fine — Graph uses it only to encrypt.
- Store the **private key in Azure Key Vault**; give the notification processor read-only access at runtime.
- **Rotate** keys periodically as part of subscription renewal: subscribe new with the new cert, keep the **old private key available** until no notification references its `encryptionCertificateId`, then retire it.

**Don't:**

- Put the private key in source, config, an env var, or the notification URL.
- Decrypt before the `dataSignature` HMAC check passes.
- Assume one symmetric key per notification — each **item** has its own; decrypt them independently.

## Edge cases / when the rule does NOT apply

A **basic** (no-resource-data) subscription needs **no** encryption certificate — Graph sends only IDs and you GET the resource yourself; choose basic when you don't want to hold a decryption key. A `null` `validationTokens`/encryption result means app config is wrong (`appRoleAssignmentRequired` / the *Microsoft Graph Change Tracking* service principal app-role), not a key problem. Some resources (e.g. Teams meeting call events, emergency calls) **only** support rich notifications — there you must hold a key.

## See also

- [`./notify-validate-the-handshake-and-verify-the-sender.md`](./notify-validate-the-handshake-and-verify-the-sender.md) — validate the JWT before you reach decryption
- [`./notify-subscriptions-need-renewal-and-lifecycle-handling.md`](./notify-subscriptions-need-renewal-and-lifecycle-handling.md) — rotate keys during renewal
- [`../knowledge/workloads-notifications-decision-trees.md`](../knowledge/workloads-notifications-decision-trees.md) — basic vs rich decision tree
- [`../agents/graph-workloads-engineer.md`](../agents/graph-workloads-engineer.md) — escalates key handling to `ravenclaude-core/security-reviewer`
- [Set up change notifications with resource data — Decrypting resource data](https://learn.microsoft.com/graph/change-notifications-with-resource-data#decrypting-resource-data-from-change-notifications) — authoritative

## Provenance

From the Microsoft Learn "change notifications with resource data" page (retrieved 2026-05-30 via Microsoft Learn MCP). The two-step encryption, OAEP, HMAC-SHA256 `dataSignature` check, RSA 2048–4096 key requirement, public-key-only export, Key Vault recommendation, and the old-key-retention rotation rule are all quoted directly. Reinforces team house opinion #7/#8 — the decryption key escalates to security review.

---

_Last reviewed: 2026-05-30 by `claude`_
