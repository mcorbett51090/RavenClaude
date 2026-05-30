# Certificates (or managed identity), not client secrets, in production

**Status:** Absolute rule

**Domain:** Identity / Credentials

**Applies to:** microsoft-graph

---

## Why this exists

A client secret is a long, guessable-if-leaked string that is trivially copy-pasted into logs, config files, source control, and notification URLs. A certificate credential proves possession of a private key that never travels as a bearer value, and a managed identity removes the stored credential entirely. Production app-only access to Graph is exactly the high-value target attackers hunt for; a leaked secret with `.ReadWrite.All` is a tenant breach. This is a security control — the credential choice escalates to `ravenclaude-core/security-reviewer`.

## How to apply

Prefer **managed identity** on Azure-hosted compute; **certificate** off-Azure; **client secret** only for local dev with a short expiry.

```csharp
// Production off-Azure: certificate credential (no secret string anywhere)
var cert = new X509Certificate2("graph-app.pfx", pfxPassword, X509KeyStorageFlags.MachineKeySet);
var credential = new ClientCertificateCredential(tenantId, clientId, cert);

// Azure-hosted: managed identity — nothing to store or rotate by hand
var credential = new ManagedIdentityCredential();
```

**Do:**

- Use a certificate (or managed identity) for any production or sensitive-scope confidential client.
- Store the cert in Key Vault / the platform cert store; rotate before expiry; monitor expiry.

**Don't:**

- Commit a secret to source, bake it into config shipped to clients, or put it in a webhook/notification URL.
- Use a long-lived client secret as the production credential because "it was faster to set up."

## Edge cases / when the rule does NOT apply

- Local development or a short-lived spike may use a client secret **with a short expiry**, never committed — and swapped for a cert before production.
- Public clients (SPA, mobile, CLI) hold **no** credential at all (auth-code + PKCE / device-code) — see [`auth-pick-the-flow-by-client-type.md`](./auth-pick-the-flow-by-client-type.md).

## See also

- [`auth-pick-the-flow-by-client-type.md`](./auth-pick-the-flow-by-client-type.md) · [`auth-cache-tokens-with-msal-dont-mint-per-call.md`](./auth-cache-tokens-with-msal-dont-mint-per-call.md)
- [`knowledge/identity-auth-decision-trees.md`](../knowledge/identity-auth-decision-trees.md) "app credential type" tree
- [`../agents/graph-identity-engineer.md`](../agents/graph-identity-engineer.md) — escalates to `ravenclaude-core/security-reviewer`

## Provenance

Team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3 house opinion 8, §4) + Entra app-credential guidance. Credential-type availability and `ManagedIdentityCredential` usage are version-specific — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
