# The changelog is for humans — keep it current

**Status:** Absolute rule
**Domain:** Release communication
**Applies to:** `open-source-maintenance`

---

## Why this exists

A changelog exists so a user can decide whether and how to upgrade. A raw `git log` dump is not a changelog — it answers "what commits happened," not "what do I need to know." A missing or stale changelog forces every user to read diffs, and a release with no changelog entry is a release nobody can safely adopt.

## How to apply

Keep a top `[Unreleased]` section; group entries as **Added / Changed / Deprecated / Removed / Fixed / Security** (Keep a Changelog). Each line is what a *user* needs, in their terms, with an issue/PR link. At release, move `[Unreleased]` under a dated, versioned header. The advisory hook flags a version bump with no nearby CHANGELOG edit.

**Do:**
- Write entries as you merge, not in a panic at release time.
- Lead breaking entries with `**BREAKING:**` + a migration link.
- Date every released version header (`## [2.1.0] — 2026-06-23`).

**Don't:**
- Paste commit subjects as changelog lines.
- Ship a version bump with no changelog entry.

## Edge cases / when the rule does NOT apply

- **Fully automated release tooling** (release-please / semantic-release) generates the changelog from Conventional Commits — then the discipline shifts to the *commit messages*, which become the human-facing text. Review the generated changelog before publish; the auto-text is a draft.
- **Internal-only `0.0.x` spikes** before any user exists can defer formal changelogs — but start once the first user appears.

## See also
- [`../knowledge/semver-and-release-decision-tree.md`](../knowledge/semver-and-release-decision-tree.md)
- [`../skills/plan-a-release/SKILL.md`](../skills/plan-a-release/SKILL.md)
- [`../templates/release-checklist.md`](../templates/release-checklist.md)

## Provenance
Codifies Keep a Changelog 1.1.0 (keepachangelog.com). Flagged by [`../hooks/flag-oss-hygiene-smells.sh`](../hooks/flag-oss-hygiene-smells.sh). Last reviewed 2026-06-23.

---

_Last reviewed: 2026-06-23 by `claude`_
