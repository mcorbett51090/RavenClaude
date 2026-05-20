# Changelog — RavenClaude marketplace

This file tracks **marketplace-level** changes: catalog edits, CI workflows, repo tooling, docs. Per-plugin behavior changes live in each plugin's own `CHANGELOG.md`:

- [`plugins/ravenclaude-core/CHANGELOG.md`](plugins/ravenclaude-core/CHANGELOG.md)
- [`plugins/power-platform/CHANGELOG.md`](plugins/power-platform/CHANGELOG.md)

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions are tracked in `.claude-plugin/marketplace.json` under `metadata.version`.

## [Unreleased]

### Added
- Per-plugin `CHANGELOG.md` files for `ravenclaude-core` and `power-platform`.
- Top-level `CHANGELOG.md` (this file) covering marketplace-level changes.
- `docs/release-checklist.md` — pre-tag release process.

### Notes
- The `release.yml` automation workflow that would auto-publish tagged releases is deferred to a follow-up PR — it requires the `workflow` OAuth scope which the current local `gh` token lacks. Unblock with: `gh auth refresh -s workflow`.

## [0.1.0] — 2026-05-15

### Added
- Initial marketplace catalog with two plugins:
  - `ravenclaude-core` 0.2.6 — Team Lead + 13 specialists, dispatch playbook, gates, templates.
  - `power-platform` 0.5.4 — 10 Power Platform specialists + bundled community `pbix-mcp` server.
- `validate-marketplace` CI workflow: JSON schema, version-pin check (jq-based), hook executability + shell syntax.
- `researcher-reminder` workflow that opens a weekly research-refresh issue.
- `docs/architecture.md`, `docs/access.md`, `docs/best-practices/`, `docs/staging/` directories.
- `SECURITY.md`, `LICENSE` (MIT), comprehensive `.gitignore`.

[Unreleased]: https://github.com/mcorbett51090/RavenClaude/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mcorbett51090/RavenClaude/releases/tag/v0.1.0
