# Scope Connected App credentials to the minimum required access

**Status:** Absolute rule
**Domain:** Governance / embedding security
**Applies to:** `tableau`

---

## Why this exists

A Tableau Connected App credential (a client secret used to sign JWTs for
embedding or REST API access) is a powerful, long-lived secret. If the Connected
App is configured with broad scopes (site admin, unrestricted user impersonation,
all REST API resources), a compromised secret gives an attacker site-admin-level
access to all content. The principle of least privilege applies: each Connected
App should be scoped to exactly the access its use case requires and no more.
A separate Connected App per use case (embedding app A vs. automation script B)
ensures that a compromise in one use case doesn't expose the other.

## How to apply

**At Connected App creation, define:**
- **Allowed grant types** — only the types the application actually uses
  (e.g. `urn:ietf:params:oauth:grant-type:jwt-bearer` for embedding only).
- **Access level** — restrict to specific users/groups rather than
  "all users on the site" if the embedding audience is bounded.
- **Domain allowlist** — set the embedding domain allowlist to your application's
  exact domain; do not use wildcards `[verify-at-build]`.

**One Connected App per use case:**
```
Connected App: "Embedding — Customer Portal" (embedding JWT, portal domain only)
Connected App: "Automation — Nightly Extract Refresh" (REST API, no embedding)
```

**JWT claims minimum scope:**
```python
import jwt, time, uuid

def generate_embedding_jwt(ca_client_id: str, ca_secret: str,
                            username: str, site_id: str) -> str:
    claims = {
        "iss": ca_client_id,       # Connected App client id
        "exp": int(time.time()) + 300,  # 5-minute TTL — short-lived
        "jti": str(uuid.uuid4()),  # One-time use
        "aud": "tableau",
        "sub": username,           # Exact user, not a wildcard
        "scp": ["tableau:views:embed"],  # Minimum required scope
    }
    return jwt.encode(claims, ca_secret, algorithm="HS256")
```

**Do:**
- Create a separate Connected App for each distinct use case (embedding,
  automation, API integration).
- Use the shortest practical JWT TTL (5–15 minutes for embedding tokens).
- Include only the scopes required by the use case in the `scp` claim.
- Escalate the full Connected App design to `ravenclaude-core/security-reviewer`
  for the security verdict.

**Don't:**
- Reuse a single high-privilege Connected App across multiple use cases.
- Use wildcard domains in the embedding domain allowlist.
- Issue long-lived JWTs (> 1 hour) for embedding contexts.

## Edge cases / when the rule does NOT apply

- Development / local testing environments where a temporary broad-scope
  Connected App is acceptable: rotate and narrow-scope before production.

## See also

- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns Connected App design and JWT configuration
- [`./embed-connected-apps-jwt-not-trusted-tickets.md`](./embed-connected-apps-jwt-not-trusted-tickets.md) — the upstream rule mandating Connected Apps for embedding
- [`./embed-scope-the-jwt-and-rls-together.md`](./embed-scope-the-jwt-and-rls-together.md) — the JWT scope and RLS must be designed together

## Provenance

Codifies the least-privilege principle applied to Tableau Connected Apps.
Tableau Connected App documentation `[verify-at-build]`. Standard JWT security
practice (short TTL, minimum scope, one-use `jti`). House opinion #8 from
`CLAUDE.md` §3 ("embed with Connected Apps + JWT, never a trust ticket hack or
embedded credentials"). Security verdict escalates to `ravenclaude-core/security-reviewer`.

---

_Last reviewed: 2026-06-05 by `claude`_
