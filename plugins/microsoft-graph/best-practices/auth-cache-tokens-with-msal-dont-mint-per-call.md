# Cache tokens with MSAL; don't mint a token per call

**Status:** Pattern

**Domain:** Identity / Token acquisition

**Applies to:** microsoft-graph

---

## Why this exists

Every token request is a round-trip to Entra and counts against authentication throttling. Code that calls `AcquireToken…` before every Graph request is slow, fragile, and self-throttling — and often re-implements refresh logic incorrectly. MSAL (and the Azure Identity credentials that wrap it) already cache access tokens in memory, reuse them until near expiry, and refresh silently. Let the library own the token lifecycle.

## How to apply

Acquire through MSAL / an Azure Identity credential and reuse the instance; it caches and refreshes for you.

```python
# Python — MSAL confidential client caches tokens; ask for one per call, it serves the cached one
app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=cert)
def token():
    # MSAL returns the cached token until it nears expiry, then refreshes silently
    r = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return r["access_token"]
```

**Do:**

- Reuse one credential/MSAL client instance for the app's lifetime; request a token per call and let it serve from cache.
- Use a persistent/distributed token cache for multi-instance or multi-user (OBO) scenarios.

**Don't:**

- Construct a fresh credential or mint a new token on every request.
- Hand-roll expiry math or refresh-token storage when MSAL does it.

## Edge cases / when the rule does NOT apply

- Multi-user delegated/OBO services need a **per-user** cache partition (keyed by user) — don't share one user's token across users.
- Serverless/short-lived functions benefit from a distributed cache (e.g. Redis) so cold starts don't re-mint every time.

## See also

- [`auth-pick-the-flow-by-client-type.md`](./auth-pick-the-flow-by-client-type.md) · [`auth-certificates-not-secrets-in-production.md`](./auth-certificates-not-secrets-in-production.md)
- [`api-use-the-sdk-not-raw-http-for-resilience.md`](./api-use-the-sdk-not-raw-http-for-resilience.md) — the SDK's auth provider does this for you
- [`../agents/graph-identity-engineer.md`](../agents/graph-identity-engineer.md)

## Provenance

Team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3) + MSAL token-cache behavior. MSAL method names are version- and language-specific — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
