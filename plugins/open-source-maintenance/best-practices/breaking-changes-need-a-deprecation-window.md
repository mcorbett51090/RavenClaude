# Breaking changes need a deprecation window

**Status:** Absolute rule
**Domain:** API evolution / release
**Applies to:** `open-source-maintenance`

---

## Why this exists

Yanking a public API in a release strands every downstream user who relied on it, with no warning and no path forward. A deprecation window — warn first, keep both paths working for a published period, then remove in the next major — converts a breaking change from a betrayal into a planned migration. Trust in a project's stability is its most valuable, most easily destroyed asset.

## How to apply

Run the lifecycle in [`../skills/manage-breaking-changes-and-deprecations/SKILL.md`](../skills/manage-breaking-changes-and-deprecations/SKILL.md): (1) announce + emit a runtime/compile deprecation warning naming the replacement, in a **minor**, no behavior change; (2) hold the window for at least one minor cycle / a stated duration; (3) remove in the next **major** with a `**BREAKING:**` changelog note and a migration guide. Offer a codemod for large mechanical changes.

**Do:**
- Make the deprecation warning name the replacement and link the migration guide.
- Remove only in a major; publish the support window.

**Don't:**
- Remove or rename a public symbol in a minor or patch.
- Deprecate with no path forward ("deprecated" + silence is just noise).

## Edge cases / when the rule does NOT apply

- **A security fix that forces an immediate break** may skip the window — but say so explicitly in the advisory and changelog, and minimize the blast radius.
- **Pre-`1.0.0`** may break in a minor, but still announce and ideally still warn.
- **A truly never-used API** (provable via telemetry/search) can shorten the window — document the basis.

## See also
- [`../skills/manage-breaking-changes-and-deprecations/SKILL.md`](../skills/manage-breaking-changes-and-deprecations/SKILL.md)
- [`./semver-bump-by-the-change-not-the-feeling.md`](./semver-bump-by-the-change-not-the-feeling.md)

## Provenance
Codifies SemVer major-bump semantics + the `release-and-versioning-engineer` deprecation discipline. Last reviewed 2026-06-23.

---

_Last reviewed: 2026-06-23 by `claude`_
