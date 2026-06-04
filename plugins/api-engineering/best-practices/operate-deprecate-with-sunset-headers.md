# Deprecate with Deprecation/Sunset headers and a dated timeline

**Status:** Absolute rule — a silent version retirement is a broken promise to every integrator.

**Domain:** API lifecycle / operations

**Applies to:** `api-engineering`

---

## Why this exists

Retiring an API version without warning breaks live integrations with no recourse. Worse, an old version left running but unmonitored becomes a shadow/zombie API — an unguarded attack surface (OWASP API9). Deprecation is a *process*, not a flag flip: announce in-band (response headers consumers' tooling can detect), publish a dated timeline and migration guide, communicate to known consumers, and *verify* traffic has drained before the sunset date arrives.

## How to apply

Emit the headers, publish the plan, monitor the drain.

```http
GET /v1/orders
200 OK
Deprecation: true
Sunset: Sat, 30 Nov 2026 23:59:59 GMT          # RFC 8594 — when /v1 stops working
Link: <https://api.example.com/docs/migrate-to-v2>; rel="deprecation"
Warning: 299 - "API v1 is deprecated; migrate to v2 before 2026-11-30"
```

```
Rollout: announce -> headers live -> migration guide + consumer comms ->
         monitor v1 traffic by consumer -> chase stragglers -> sunset only when drained
```

**Do:**
- Set `Deprecation` and `Sunset` (RFC 8594) headers and a `Link rel="deprecation"` to the migration guide.
- Track per-consumer traffic to the deprecated version; don't sunset while real traffic remains without explicit sign-off.

**Don't:**
- Turn off a version with no header, no timeline, and no comms; leave the old version running and unmonitored.

## Edge cases / when the rule does NOT apply

A critical security issue may force an accelerated sunset — shorten the clock and escalate, don't skip the announcement. An internal API with one coordinated consumer can compress the process but still records the change. The `Deprecation` header's RFC-vs-draft status is verified before quoting (`[verify-at-build]`); `Sunset` is RFC 8594.

## See also

- [`./design-version-only-for-breaking-changes.md`](./design-version-only-for-breaking-changes.md)
- [`../templates/deprecation-and-sunset-plan.md`](../templates/deprecation-and-sunset-plan.md)
- [RFC 8594 — The Sunset HTTP Header Field](https://www.rfc-editor.org/rfc/rfc8594.html) — authoritative

## Provenance

Codifies house opinion #10 (CLAUDE.md §3) and pairs with OWASP API9 (inventory). `Sunset` = RFC 8594; `Deprecation` header status verified before quoting. Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
