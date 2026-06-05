# Semver is a contract, not a label

**Status:** Absolute rule
**Domain:** Release engineering / versioning
**Applies to:** `devops-cicd`

---

## Why this exists

Consumers of a library, API, or container image make deployment decisions based on the version number. A breaking change shipped under a minor bump, or a patch that changes behavior, silently breaks downstream — without a changelog entry or a migration guide. Treating semver as a convenience label rather than a public contract erodes trust in every downstream integration.

## How to apply

Enforce semver semantics by policy, not by memory.

```
MAJOR.MINOR.PATCH

MAJOR — breaking change to the public interface (incompatible API change, removed endpoint, renamed field)
MINOR — backwards-compatible new capability
PATCH — backwards-compatible bug fix only
```

**Automate with Conventional Commits + a release bot:**

```yaml
# .releaserc.json (semantic-release)
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/github"
  ]
}
```

Commit prefixes drive the bump: `fix:` → patch, `feat:` → minor, `feat!:` or `BREAKING CHANGE:` → major.

**Do:**
- Bump MAJOR before merging any breaking API change — period.
- Tag releases with a signed Git tag (`git tag -s v1.2.3`) so provenance is verifiable.
- Generate a changelog from commits; never hand-edit it retroactively.
- Use `0.x.y` for pre-v1 to signal unstable contract.

**Don't:**
- Use `latest` as a deployment target in production — it resolves to "whatever the registry last received."
- Bump only the patch for something that changes default behavior.
- Skip a major bump because "only internal consumers" use it — they still depend on the contract.
- Re-tag an existing version after publishing it (immutable releases).

## Edge cases / when the rule does NOT apply

Pre-release labels (`1.0.0-alpha.1`, `1.0.0-rc.2`) explicitly signal instability — consumers opt in. Internal-only build artifacts without downstream consumers can use a monotonic build number instead of semver, but must document that explicitly.

## See also

- [`../agents/release-engineer.md`](../agents/release-engineer.md) — owns release versioning and changelogs.
- [`./build-build-once-promote-the-same-artifact.md`](./build-build-once-promote-the-same-artifact.md) — the artifact versioned here is the one promoted unchanged.

## Provenance

Standard semver.org specification (semver 2.0.0) combined with `release-engineer`'s ownership of "release versioning and changelogs" from CLAUDE.md §1. Conventional Commits is the community standard that ties commit discipline to automated version bumps.

---

_Last reviewed: 2026-06-05 by `claude`_
