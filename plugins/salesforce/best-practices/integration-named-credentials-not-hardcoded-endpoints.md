# Use Named Credentials for callout endpoints and secrets — never hard-code them

**Status:** Absolute rule — a hard-coded endpoint or secret in Apex is a security and portability bug, and the secret-handling verdict escalates to core.

**Domain:** Integration / Identity

**Applies to:** `salesforce`

---

## Why this exists

An outbound callout needs three things that change between sandbox and production and that must not live in source: the endpoint URL, the authentication scheme, and the secret (API key, OAuth client secret, certificate). Hard-coding any of them into Apex means the secret is readable by anyone with code access, the endpoint can't move between orgs without a code change, and the auth handshake is re-implemented (badly) in every class. **Named Credentials** (and the paired **External Credential** that holds the auth) move all three into metadata Salesforce manages: the platform injects the auth header at callout time so the secret never appears in Apex, the URL is environment-specific, and `Remote Site Settings` are no longer needed. Hard-coded secrets are the recurring finding that escalates to `ravenclaude-core/security-reviewer`.

## How to apply

Define a Named Credential (e.g. `My_ERP`) with its External Credential holding the principal/secret, then reference it by the `callout:` URL scheme. Salesforce resolves the host and injects auth — the Apex carries no URL host and no secret.

```apex
// DO — endpoint + auth resolved from the Named Credential; no secret in code
public with sharing class ErpClient {
    public HttpResponse getOrder(String orderId) {
        HttpRequest req = new HttpRequest();
        // 'callout:My_ERP' resolves to the configured host; auth header injected by the platform
        req.setEndpoint('callout:My_ERP/orders/' + EncodingUtil.urlEncode(orderId, 'UTF-8'));
        req.setMethod('GET');
        req.setTimeout(120000);             // cap below the callout time limit
        return new Http().send(req);
    }
}
```

```apex
// DON'T — host and bearer token baked into source
req.setEndpoint('https://erp.acme.com/orders/' + orderId);   // host hard-coded, needs a Remote Site Setting
req.setHeader('Authorization', 'Bearer sk_live_8f3...');     // secret in source control — a leak
```

**Do:**
- Reference every external host with `callout:<NamedCredential>/path`; let the platform inject auth.
- Store secrets in an **External Credential** (per-user or named principal), never in Apex, custom settings, or custom metadata.
- URL-encode any user-supplied path/query segment (`EncodingUtil.urlEncode`).
- Set an explicit `setTimeout` below the per-transaction callout time cap.

**Don't:**
- Concatenate a literal `https://…` host into `setEndpoint`.
- Put an API key in a custom setting, custom metadata, label, or static resource "because it's not the code."
- Re-implement OAuth token refresh in Apex when the External Credential's auth protocol does it for you.

## Edge cases / when the rule does NOT apply

A callout to a fully public, unauthenticated endpoint still benefits from a Named Credential (environment-specific host, no Remote Site Setting), but the secret-handling concern is moot. Legacy orgs may still carry `Remote Site Settings` + hard-coded hosts; treat those as tech debt to migrate, not a pattern to copy. For mutual-TLS or signed-request schemes the certificate lives in the External Credential / a protected custom metadata of type cert, never inline. Any secret-in-code finding is a **security verdict** — escalate it to `ravenclaude-core/security-reviewer` rather than self-certifying.

## See also

- [`./integration-callout-governor-and-async.md`](./integration-callout-governor-and-async.md) — the callout limits the request above must budget
- [`../knowledge/integration-patterns.md`](../knowledge/integration-patterns.md) — the six canonical patterns and the limit budget
- [`../knowledge/integration-data-decision-trees.md`](../knowledge/integration-data-decision-trees.md) — sync-vs-async callout traversal
- [`../agents/salesforce-platform-architect.md`](../agents/salesforce-platform-architect.md) — owns integration-pattern selection
- [`./enforce-sharing-and-crud-fls.md`](./enforce-sharing-and-crud-fls.md) — the sibling least-access security rule

## Provenance

Codifies the secret-handling and integration discipline from [`../CLAUDE.md`](../CLAUDE.md) (escalate secret handling to `ravenclaude-core/security-reviewer`) and the limit-budget guidance in [`../knowledge/integration-patterns.md`](../knowledge/integration-patterns.md). Named Credential / External Credential mechanics are the Salesforce-supported way to externalize callout auth; verify exact External-Credential auth-protocol support `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
