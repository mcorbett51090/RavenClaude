# Bump the version by the change, not by the feeling

**Status:** Absolute rule
**Domain:** Versioning / release
**Applies to:** `open-source-maintenance`

---

## Why this exists

Semantic versioning is a contract with downstream users: a major says "your code may break," a minor says "new things, safe to upgrade," a patch says "fixes only." When maintainers bump by vibe — calling a big-feeling release a major or sneaking a breaking change into a minor — the contract breaks and every downstream pin becomes untrustworthy. The bump is determined by the *change set*, not the emotional weight of the release.

## How to apply

Traverse [`../knowledge/semver-and-release-decision-tree.md`](../knowledge/semver-and-release-decision-tree.md). Any backward-incompatible change (removed/renamed public API, changed contract, dropped runtime) → **major**, regardless of size. A backward-compatible feature → **minor**. Only fixes → **patch**. A giant internal refactor with no public-surface change is a **patch**.

**Do:**
- Classify each change against the public contract, then take the highest bump any change requires.
- Lead a breaking changelog entry with `**BREAKING:**` and link a migration guide.
- Treat "tighten validation that previously passed" as breaking — it breaks callers relying on the laxity.

**Don't:**
- Inflate a fix-only release to a minor/major because it "feels significant."
- Hide a removed/renamed symbol in a minor or patch.

## Edge cases / when the rule does NOT apply

- **Pre-`1.0.0`:** a `0.x` minor *may* break — but announce it loudly; the rule becomes "communicate the break," not "no break."
- **Fixing a bug to match the documented contract** is a patch, but call it out if anyone plausibly depended on the buggy behavior.

## See also
- [`../knowledge/semver-and-release-decision-tree.md`](../knowledge/semver-and-release-decision-tree.md)
- [`./changelog-is-for-humans-keep-it-current.md`](./changelog-is-for-humans-keep-it-current.md)
- [`../skills/plan-a-release/SKILL.md`](../skills/plan-a-release/SKILL.md)

## Provenance
Codifies SemVer 2.0.0 (semver.org) and the `release-and-versioning-engineer` house opinion "bump by the change, not the feeling". Last reviewed 2026-06-23.

---

_Last reviewed: 2026-06-23 by `claude`_
