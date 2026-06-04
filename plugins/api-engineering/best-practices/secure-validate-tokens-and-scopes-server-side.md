# Validate tokens and scopes server-side (OWASP API2)

**Status:** Absolute rule — never trust a JWT's claims without validating the JWT; the verdict escalates to security-reviewer.

**Domain:** API security / authentication

**Applies to:** `api-engineering`

---

## Why this exists

A JWT is base64 — anyone can decode and forge one. If your API reads the claims (`sub`, `roles`, `scope`) without verifying the signature against the issuer, an attacker mints a token claiming `roles: ["admin"]` and you believe them. The `alg: none` attack and accepting expired/wrong-audience tokens are the same class. Authentication is only real when you **cryptographically verify** the token before trusting a single claim (OWASP API2:2023 — Broken Authentication).

## How to apply

Verify signature, issuer, audience, and lifetime on every request; reject `alg: none`; map scope to operation.

```
validate(token):
  header, claims, sig = parse(token)
  assert header.alg in ALLOWED_ALGS         # e.g. RS256/ES256 — NEVER "none"
  key = jwks_for(claims.iss)[header.kid]     # fetch issuer's JWKS, cache it
  assert verify_signature(token, key)
  assert claims.iss == EXPECTED_ISSUER
  assert API_AUDIENCE in claims.aud
  assert now() < claims.exp and now() >= claims.nbf
  return principal_from(claims)              # only now trust the claims
# then: require the operation's scope ∈ claims.scope
```

**Do:**
- Pin allowed algorithms; fetch and cache the issuer JWKS; validate `iss`/`aud`/`exp`/`nbf`.
- Use least-privilege scopes (`orders:read`, not `*`/`read:all`); map scope → operation explicitly.
- Pick the OAuth2 grant by client type (see the grant-selection tree) — Authorization Code + PKCE for user clients, Client Credentials for daemons; never Implicit/ROPC.

**Don't:**
- Decode-and-trust without verifying; accept `alg: none`; skip the audience check; ship broad scopes.

## Edge cases / when the rule does NOT apply

Opaque (non-JWT) tokens are validated by introspection at the issuer instead of local signature checks — same principle, different mechanism. API keys are authentication, not authorization — they still need per-object/function checks on top. The end-user *login flow* is `auth-identity`'s; this rule is the API accepting the resulting token.

## See also

- [`./secure-authorize-every-function-bfla.md`](./secure-authorize-every-function-bfla.md)
- [`../knowledge/api-security-decision-trees.md`](../knowledge/api-security-decision-trees.md) — OAuth2 grant selection
- [OWASP API2:2023 — Broken Authentication](https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/) — authoritative

## Provenance

Codifies house opinions #7/#8 (CLAUDE.md §3) and OWASP API2:2023. Web-verified 2026-06-04. **Verdict escalates to `ravenclaude-core/security-reviewer`.**

---

_Last reviewed: 2026-06-04 by `claude`_
