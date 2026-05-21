# Changelog

All notable changes to the RavenClaude marketplace and its plugins. Format loosely follows [Keep a Changelog](https://keepachangelog.com/). The marketplace version (`metadata.version` in `.claude-plugin/marketplace.json`) bumps when the catalog shape or cross-plugin contracts change; individual plugins have their own semver tracked in their `plugin.json`.

## marketplace 0.2.0 — 2026-05-21

### ravenclaude-core 0.4.0 (BREAKING)

- All 13 specialist agents now declare the **Structured Output Protocol** block in their Output Contract section. Agents emit a `---RESULT_START--- … ---RESULT_END---` JSON block inline after their Markdown report; the Team Lead parses it to drive routing.
- New **Cited-Adjudicator Escalation** pattern added to `rules/agent-collaboration.md` and the `spawn-team.md` Step 6 re-routing table. Trigger: when Agent A confidently asserts Agent B's prior artifact is wrong (confidence ≥ 0.7) in a correctness-critical domain, the Team Lead spawns `deep-researcher` in citation-only mode for adjudication.
- `/init-agent-ready` now copies the plugin constitution into the consumer repo as `docs/team-constitution.md` at init time, so the consumer-side Team Lead auto-loads the team roster on every session open. Portable across users — replaces an earlier (unshipped) design that imported from `~/.claude/plugins/cache/...`.
- README reconciliation: documented namespaced `subagent_type` form (`ravenclaude-core:architect`, `ravenclaude-core:code-reviewer`, etc.). Bare names remain reserved for built-in agents.
- Constitution language tightened: `.ravenclaude/runs/` artifact substrate is now **recommended for multi-step runs**, not required for every dispatch. Inline SOP JSON covers single-agent handoffs.
- `code-reviewer.md` and `security-reviewer.md` now include a one-line bridge clarifying that the JSON `status` field mirrors the Markdown Verdict.
- `deep-researcher.md` now distinguishes its per-claim Confidence tag (High/Medium/Low/Speculation) from the SOP run-level `confidence` float.
- Drift cleanup: removed legacy `.claude/rules/...`, `.claude/skills/...`, `.claude/agents/...` label references from agent files (10 files affected). Link targets unchanged; only displayed labels.
- Skill flattening: `skills/researcher/SKILL.md` → `skills/researcher.md` (no other files in the folder; flatten matches the other 10 skills).

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins` picks up the new agent contracts automatically. If you have downstream parsers reading agent output as pure Markdown, accept or strip the trailing `---RESULT_START--- … ---RESULT_END---` JSON block. Re-run `/init-agent-ready` in any project that wants the new `docs/team-constitution.md` import.

### power-platform 0.6.0 (BREAKING)

- All 10 specialist agents now emit the same Structured Output Protocol JSON block as `ravenclaude-core`, extended with a `licensing_impact` field that mirrors the mandatory `Licensing impact:` line from the existing Power Platform output block.

**Migration for consumers:** same as `ravenclaude-core` — accept or strip the JSON block; existing Markdown output unchanged.

### Hygiene (both plugins + marketplace)

- Maintainer email scrubbed from `marketplace.json` and both `plugin.json` files (own house rule was being violated). New CI guard in `validate-marketplace.yml` fails on any future regression of `matt@ravenpower.net`.
- `guard-destructive.sh` `git reset --hard` regex tightened: previous anchored variants (`origin|HEAD~|@`) let `git reset --hard <branch>` and `git reset --hard <sha>` slip through. New pattern blocks all destinations; `--soft` and `--mixed` still pass.
- `enforce-layout.sh` adds defense-in-depth `..` path-traversal scrub before the allow-list check, with a header comment documenting bash `[[ == ]]` matching semantics so future refactorers don't break the matcher by porting to `find` / filename-expansion.
- Root `CLAUDE.md`: replaced hardcoded `/home/codespace/.claude/projects/...` memory path with portable `~/.claude/projects/<encoded-project-path>/` form. Marketplace-dev hooks section rewritten to accurately document the dual-registration design (in-repo `.claude/settings.json` + plugin's `hooks/hooks.json`) and the migration path.
- `docs/lab/gis-expert.md` now carries a clear STATUS banner identifying it as experimental and not loaded by any agent runtime.

## ravenclaude-core 0.3.0 — earlier in 2026-05

- Agent-readable repo pattern (AGENTS.md + CLAUDE.md + .repo-layout.json) shipped via `/init-agent-ready` slash command.
- Plugin-distributable hooks (`hooks/hooks.json`) added so consumer projects get the same enforcement as marketplace dev.
- 13 specialist agents finalized; spawn-team dispatch playbook stabilized.

## ravenclaude-core 0.1.0 → 0.2.x — early 2026-05

- Initial public release of the Team Lead + 13 specialists pattern.
