# Changelog — ravenclaude-core

All notable changes to the `ravenclaude-core` plugin. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions in `.claude-plugin/plugin.json`.

## [Unreleased]

_(Currently aligns with the version pinned in `plugin.json`. Add entries here as PRs land.)_

## [0.3.0] — Pending merge (PR #10)

### Added
- `agents/data-engineer.md` — domain-neutral data-engineering specialist (pipelines, modeling, ELT/ETL, query performance, lineage, quality testing). Routes Power BI / DAX work to `power-platform/power-bi-engineer`; routes product-feature schema work to `architect`.

## [0.2.6] — 2026-05-18

### Changed
- Audit cleanup: section numbering in `CLAUDE.md`, doc drift fixes, hook path safety.

## [0.2.5] — 2026-05-17

### Changed
- External-review polish across agents, rules, and templates.

## [0.2.0] — 2026-05-10

### Added
- Tiered-knowledge support (Consensus / Divergent) for specialist agents.
- `deep-researcher` meta-skill + daily/weekly research-refresh automation.
- Researcher-reminder workflow.

## [0.1.0] — 2026-05-01

### Added
- Initial release: Team Lead + 13 specialist agents (architect, coders, reviewers, designer, documentarian, deep-researcher, project-manager, partner-success-manager, prompt-engineer, etc.).
- Dispatch playbook in `skills/`.
- Format / lint / test gate hooks.
- Rules: coding-standards, security, git-workflow, agent-collab.
- Templates: memos, runbooks, design specs, RAID logs, partner-success artifacts.
