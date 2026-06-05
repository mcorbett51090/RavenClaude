# Choose basic vs rich change notifications deliberately — rich adds decryption and a Key Vault dependency

**Status:** Pattern
**Domain:** Microsoft Graph / change notifications
**Applies to:** `microsoft-graph`

---

## Why this exists

Microsoft Graph change notifications have two modes: **basic** (the notification contains only the resource ID and change type, requiring a follow-up GET to retrieve the resource) and **rich** (`includeResourceData: true`, the full changed resource is included in the notification payload, encrypted with a consumer-provided public key). Rich notifications save a follow-up GET call per event, which matters at high notification volume — but they require the consumer to manage an asymmetric key pair, store the private key in Key Vault, rotate it, and handle decryption for every notification. Developers who choose rich notifications without understanding the key-management obligation produce systems with hard-coded encryption keys or decryption failures after key expiry.

## How to apply

Decision:

| Scenario | Recommended mode |
|---|---|
| Low notification volume (< 100/min), simple resource (user, group) | Basic — the follow-up GET is cheap |
| High notification volume, large resource payloads (mail, Teams messages) | Rich — eliminates the follow-up GET |
| Any scenario where key management cannot be maintained | Basic — simpler is safer |

For rich notifications, the subscription creation must include:

```json
{
  "changeType": "created,updated",
  "resource": "/me/messages",
  "notificationUrl": "https://your-endpoint.example.com/notify",
  "includeResourceData": true,
  "encryptionCertificate": "<base64-DER-public-key>",
  "encryptionCertificateId": "key-id-v1",
  "expirationDateTime": "2026-06-06T00:00:00Z"
}
```

Key management checklist (rich only):
- [ ] Private key stored in Key Vault, never in code or config.
- [ ] `encryptionCertificateId` is a version-tagged identifier so rotation does not break in-flight decryption.
- [ ] Renewal process updates both `encryptionCertificate` and the stored private key atomically.
- [ ] Decryption code handles the `dataKey` (encrypted symmetric key) → symmetric-decrypt the payload pattern.
- [ ] Security reviewer has approved the key storage and decryption architecture.

**Do:**
- Default to basic notifications unless the volume or payload size explicitly justifies rich.
- Route the key-management design through `ravenclaude-core/security-reviewer` — the private key is a secret.
- Test the decryption path explicitly — it is the most common failure mode in rich notification implementations.

**Don't:**
- Store the encryption private key as a plaintext config value or environment variable.
- Reuse the same key across tenants or environments — each subscription registration should use a key scoped to that environment.
- Use `includeResourceData: true` for resources where the payload includes PII you did not intend to handle at the notification layer.

## Edge cases / when the rule does NOT apply

Some Graph resources support rich notifications only in `/beta` `[verify-at-build]` — if the resource is not GA for rich notifications, basic is the only production-safe option regardless of volume.

## See also

- [`../agents/graph-workloads-engineer.md`](../agents/graph-workloads-engineer.md) — owns change-notification subscription design
- [`./notify-encrypt-rich-payloads-and-guard-the-key.md`](./notify-encrypt-rich-payloads-and-guard-the-key.md) — the security-specific rule for the private key handling obligation

## Provenance

Codifies CLAUDE.md §3 #7 ("subscriptions are stateful and expire; rich notifications need decryption-key management — the last escalates to security review"); Microsoft Graph change notifications documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
