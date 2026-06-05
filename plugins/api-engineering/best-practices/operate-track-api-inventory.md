# Maintain a complete, current API inventory

**Status:** Primary diagnostic
**Domain:** API operations / security
**Applies to:** `api-engineering`

---

## Why this exists

OWASP API9 (2023) — Improper Inventory Management — is exploited by targeting API versions, environments, or endpoints that the team has forgotten about. The shadow API (a v1 endpoint still responding while v2 is the official one, a dev/staging API exposed to the internet, a microservice endpoint not behind the gateway) is the one that doesn't get patched, doesn't get rate-limited, and doesn't appear in security reviews. An inventory is the prerequisite for every other security and lifecycle control.

## How to apply

Maintain the inventory in the OpenAPI spec + a gateway routing manifest:

```yaml
# OpenAPI spec: every published version is a committed document
# Bad: a single spec that is silently updated for v2
# Good: explicit versioned documents
specs/
  openapi-v1.yaml      # deprecated, Sunset: <date>
  openapi-v2.yaml      # current
  openapi-v2-beta.yaml # beta (pre-GA)

# Gateway manifest: every routed endpoint with environment + auth status
endpoints:
  - path: /v1/users
    env: [production]
    auth: bearer
    status: deprecated
    sunset: 2026-12-01
  - path: /v2/users
    env: [production, staging]
    auth: bearer
    status: active
  - path: /internal/metrics
    env: [production]
    auth: internal-only
    exposure: private
```

**Do:**
- Register every API version and environment in the inventory when it is created.
- Include auth requirement, exposure level (public/partner/internal), and deprecation status.
- Run a gateway discovery check in CI to ensure every routed endpoint has a corresponding spec entry.
- Remove deprecated versions from the gateway after the `Sunset` date — don't just ignore them.

**Don't:**
- Leave non-production API instances internet-accessible with the same credentials as production.
- Run undocumented internal endpoints that bypass the gateway or auth middleware.
- Treat the inventory as a one-time setup — it drifts; audit it quarterly.

## Edge cases / when the rule does NOT apply

A completely internal monolith with no external-facing API surface (all callers are trusted internal services under the same deploy) does not need an external consumer-facing inventory, though an internal service catalog is still good practice.

## See also

- [`../agents/api-platform-engineer.md`](../agents/api-platform-engineer.md) — owns API lifecycle and the gateway/portal operate layer.
- [`./operate-deprecate-with-sunset-headers.md`](./operate-deprecate-with-sunset-headers.md) — the inventory's deprecation status drives the sunset rollout.

## Provenance

OWASP API Security Top 10 (2023) — API9 Improper Inventory Management. Codifies `api-platform-engineer`'s lifecycle and governance responsibility.

---

_Last reviewed: 2026-06-05 by `claude`_
