# Version only for breaking changes; deprecate on a clock

**Status:** Absolute rule — additive changes don't bump the version; breaking ones must, with a sunset plan.

**Domain:** API design / lifecycle

**Applies to:** `api-engineering`

---

## Why this exists

Versioning churn is a tax on every consumer — a new version is a migration project. Bumping the major version for an *additive* change (a new optional field, a new endpoint) forces needless work and trains consumers to ignore version bumps. Conversely, shipping a *breaking* change without a version (renaming a field, tightening a type, making an input required) silently breaks live clients. The discipline is knowing the difference and announcing the breaks.

## How to apply

Classify the change first, then act.

```
Additive (NON-breaking) — ship without a version bump:
  + new optional response field        + new endpoint / new optional query param
  + new enum value a tolerant client ignores   (requires consumers be tolerant readers)

Breaking — new major version + deprecation clock:
  - remove/rename a field   - tighten a type / shrink an enum
  - make an optional input required   - change a status code or error semantics
```

For a break: pick the version carrier (URI `/v2` for public/partner; header/media-type for coordinated/internal — see the versioning tree), then run the clock:

```
Deprecation: true                                  # the version is deprecated
Sunset: Sat, 30 Nov 2026 23:59:59 GMT              # RFC 8594 — when it stops working
Link: <https://api.example.com/docs/migrate-v2>; rel="deprecation"
```

**Do:**
- Document every change as additive vs breaking in the changelog.
- Require consumers to be tolerant readers (ignore unknown fields) so additive stays non-breaking.

**Don't:**
- Bump the major version for additive changes; retire a version with no `Sunset` header and no dated timeline.

## Edge cases / when the rule does NOT apply

A security fix that *must* break behavior may need an accelerated sunset — shorten the clock, don't skip the announcement. Pre-1.0/internal-only APIs with a single coordinated consumer can move faster, but still classify changes.

## See also

- [`./operate-deprecate-with-sunset-headers.md`](./operate-deprecate-with-sunset-headers.md)
- [`../knowledge/api-design-decision-trees.md`](../knowledge/api-design-decision-trees.md)
- [RFC 8594 — The Sunset HTTP Header Field](https://www.rfc-editor.org/rfc/rfc8594.html) — authoritative `[verify-at-build]`

## Provenance

Codifies house opinion #10 (CLAUDE.md §3). `Sunset` is RFC 8594; the `Deprecation` header status is verified before quoting. Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
