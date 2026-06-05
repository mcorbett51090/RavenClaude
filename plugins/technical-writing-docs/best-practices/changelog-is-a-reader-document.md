# Write the Changelog for the Developer Who Will Upgrade, Not for the Commit Log

**Status:** Pattern
**Domain:** Technical Writing — API / SDK documentation
**Applies to:** `technical-writing-docs`

---

## Why this exists

A changelog written for developers produces entries like "Fixed bug in auth token handling" (useful) or "Refactor ApiClient to remove internal state" (useful for the team, useless for the upgrader). A changelog written as a commit-log dump contains hundreds of internal entries that bury the two lines the consumer actually needs: "**Breaking change:** the `refresh_token` field is removed; use `session.refresh()` instead." A reader opening the changelog has one question: "What do I need to change in my code to upgrade to this version?" That question must be answerable in under two minutes.

## How to apply

**Changelog section structure per version (Keep a Changelog format):**

```markdown
## [1.4.0] – 2026-06-05

### Breaking Changes
- `getUser()` now returns `null` instead of throwing for an unknown user ID. Update callers that rely on the caught exception.

### Removed
- `ApiClient.legacyAuth()` (deprecated since v1.2.0). Use `ApiClient.auth()`.

### Added
- `session.refresh()` — explicitly refreshes the access token. Replaces manual `refresh_token` handling.

### Fixed
- Rate-limit headers are now parsed correctly when the response uses non-standard casing.

### Changed
- Default request timeout increased from 10 s to 30 s.
```

**Rules:**
- **Breaking Changes** always head the section. If a release has no breaking changes, omit the section — do not write "None."
- **Use the imperative** ("Update callers…", "Replace X with Y") — the reader needs instructions, not description.
- **Link to the migration guide** when a breaking change requires more than one line of explanation.
- **Group by impact to the reader**, not by the PR that shipped it.
- **Don't include**: internal refactors with no consumer impact, test changes, CI changes, doc typo fixes.

**Do:**
- Write the changelog entry at PR review time, not as an afterthought at release cut.
- Require a changelog entry in the PR template ("Breaking change? Changelog updated?").
- Version the changelog using Semantic Versioning conventions — breaking changes require a major bump.

**Don't:**
- Dump the git log into the changelog.
- Write "Various improvements and bug fixes" for a release that has specific changes.
- Omit the date from a release entry.

## Edge cases / when the rule does NOT apply

- **Internal-only packages with a single consumer team**: a PR description is sufficient; a formal changelog adds overhead that exceeds its value.
- **Pre-1.0 / alpha/beta releases**: the semver stability contract doesn't fully apply; mark breaking changes clearly but the "Breaking Changes" section discipline is still good practice from day one.

## See also

- [`../agents/api-reference-writer.md`](../agents/api-reference-writer.md) — owns changelog authoring for SDKs and APIs
- [`./version-docs-with-the-product.md`](./version-docs-with-the-product.md) — the parent rule that docs ship with the code, including the changelog

## Provenance

Codifies the `api-reference-writer` agent's changelog guidance. Format based on "Keep a Changelog" (keepachangelog.com) and Semantic Versioning (semver.org). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
