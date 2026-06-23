---
name: plan-a-release
description: Plan a release end to end — decide the semver bump from the change set, assemble a human-readable changelog (Keep a Changelog groups), and run a release checklist (tests green, version bumped, tag signed, artifact + provenance, advisory if needed). Returns the version, the changelog entry, and the release runbook. Used by `release-and-versioning-engineer` (primary).
---

# Skill: plan-a-release

> **Invoked by:** `release-and-versioning-engineer` (primary).
>
> **When to invoke:** "is this a major/minor/patch?"; "cut a release"; "write the changelog".
>
> **Output:** the semver bump + the rule that picked it, the changelog entry, and the release checklist.

## Step 1 — decide the bump (semver)

Traverse [`../../knowledge/semver-and-release-decision-tree.md`](../../knowledge/semver-and-release-decision-tree.md):

| If the change set contains… | Bump |
|---|---|
| Any backward-**incompatible** change (removed/renamed public API, changed contract, dropped runtime) | **MAJOR** |
| A backward-**compatible** new feature or a non-breaking deprecation | **MINOR** |
| Only fixes / internal changes with no API surface change | **PATCH** |

**Pre-`1.0.0`:** a `0.x` minor may break; communicate it. The first stable release is `1.0.0`, a stability commitment — not a marketing milestone.

## Step 2 — write the changelog (for humans)

Group entries per [Keep a Changelog](https://keepachangelog.com): **Added / Changed / Deprecated / Removed / Fixed / Security**. Each line is what a *user* needs to upgrade, not a commit message. Lead breaking changes with `**BREAKING:**` and link the migration guide.

```
## [2.0.0] — 2026-06-23
### Removed
- **BREAKING:** dropped the deprecated `createClient(url)` signature; use `createClient({ url })`. Migration: ./docs/migrate-2.0.md
### Added
- `retry` option on all client calls (#412)
### Fixed
- race in the connection pool under high concurrency (#398)
```

## Step 3 — run the release checklist

Use [`../../templates/release-checklist.md`](../../templates/release-checklist.md). Minimum gates:

- [ ] CI green on the release commit (the actual head — verify a run exists for this SHA)
- [ ] Version bumped in the manifest(s) and consistent across a monorepo
- [ ] CHANGELOG updated and dated
- [ ] Tag created **and signed**; release notes attached
- [ ] Artifact published with **provenance** (Sigstore / SLSA / npm `--provenance`)
- [ ] If security-relevant: advisory published and disclosure timed (see [`coordinate-a-security-release`](../coordinate-a-security-release/SKILL.md))

## Guardrails
- **Bump by the change, not the feeling** — a removed public symbol is a major even if it "feels small". See [`../../best-practices/semver-bump-by-the-change-not-the-feeling.md`](../../best-practices/semver-bump-by-the-change-not-the-feeling.md).
- **No release without a changelog entry** — the advisory hook flags a version bump with no nearby CHANGELOG edit.
- **Automate it if you can** — release-please / semantic-release / Changesets turn this into a single merge; see [`../../knowledge/oss-tooling-2026.md`](../../knowledge/oss-tooling-2026.md). If you automate, the Conventional Commits convention is the input — enforce it.
