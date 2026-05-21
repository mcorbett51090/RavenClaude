# Changelog

All notable changes to the RavenClaude marketplace and its plugins. Format loosely follows [Keep a Changelog](https://keepachangelog.com/). The marketplace version (`metadata.version` in `.claude-plugin/marketplace.json`) bumps when the catalog shape or cross-plugin contracts change; individual plugins have their own semver tracked in their `plugin.json`.

## marketplace 0.4.0 — 2026-05-21 (overnight realignment)

Consolidates the salvageable content from overnight dispatcher PRs #8 / #9 / #10 onto the post-0.3.0 baseline. Stale version bumps (which would have rolled `ravenclaude-core` *back* to 0.3.0 and `power-platform` *back* to 0.6.0) were rejected; the additive content was preserved with version bumps recomputed forward.

### ravenclaude-core 0.6.0

- **New agent `agents/data-engineer.md`** — domain-neutral specialist for pipeline design, dimensional/lakehouse modeling, ELT/ETL, query performance, lineage, quality testing, ingestion patterns. Routes Power BI / DAX work to `power-platform/power-bi-engineer` and product-feature schema work to `architect`. Carries the Structured Output Protocol block.
- **New hook `hooks/guard-recursive-spawn.sh`** — PostToolUse advisory that warns when an edit to a plugin agent definition file looks like the agent is instructing itself to spawn another sub-agent (`Agent(`, `Task(`, `subagent_type:`, plain-English "spawn an agent" tokens). Conservative grep with false-positive guard on escalation-recommendation lines. Advisory by default; set `RC_GUARD_RECURSIVE_SPAWN_STRICT=1` to make it blocking. Registered as the 5th hook in `hooks/hooks.json`.
- **Skill update `skills/spawn-team.md`** — new **Cross-plugin dispatch** section after Step 8: domain-detection trigger table, domain-led playbooks for the seven most common Power Platform request shapes (including the new behavioral-test playbook for `power-platform-tester`), and a symmetric escalation table between `ravenclaude-core` and `power-platform`. Does not modify the Parallel Reviewer Fan-out, Artifact-Based Handoff, or Cited-Adjudicator escalation content from 0.5.0.
- CLAUDE.md narrative updated: 5 hooks, 14 specialist agents.

### power-platform 0.7.0

- **New agent `agents/power-platform-tester.md`** — Power Platform-specific tester. Spawns AFTER a specialist's change but BEFORE `solution-alm-engineer` packages a release. Covers Test Studio + Monitor (canvas), Manual Test + run-history assertions (flows), plug-in execution order + FLS/RLS + cascade (Dataverse), form / business-rule / command-bar (model-driven), DAX measure-tests + VertiPaq + DAX Studio server-timings (Power BI), `pac solution check` as a gate. Carries both the Markdown Output Contract (with mandatory `Licensing impact:` line) and the cross-plugin Structured Output Protocol JSON block.
- **House-opinions hook `hooks/check-house-opinions.sh`** gains three new mechanically-detectable checks (now 8 total):
  - `premium-connector-no-licensing-note` — flow JSON references a premium connector apiId without `_comments` / `// premium:` / `"premium": true` annotation (§3 #8).
  - `powerfx-var-prefix` / `powerfx-col-prefix` — `Set(name, ...)` and `(Clear)Collect(name, ...)` whose first argument doesn't follow the `var*` / `col*` convention (§3 #6). Skips Power Fx built-ins (`Self`, `Parent`, `ThisItem`, `ThisRecord`).
  - `secret-in-env-var` — environment-variable default that looks like a plaintext secret instead of `@Microsoft.KeyVault(...)` (§4 anti-pattern). Conservative — only fires on `password=`, `AccountKey=`, `api_key=`, `client_secret=`, `aws_secret_access_key`, or `Bearer <token>` patterns.
- CLAUDE.md narrative updated: 11 specialist agents, §7 hook table now lists 8 checks.

### Marketplace meta

- **Realignment of overnight dispatcher work**: PRs #11 (per-plugin changelogs, stale version refs) and #12 (CI quality gates that would have *replaced* the v0.5.0 behavioral guard-destructive tests) closed without merge. PRs #8 / #9 / #10 are superseded by this consolidation; closed after merge. PRs #14 / #15 / #16 (finance, regulatory-compliance, web-design plugins) remain queued for separate review.
- **README.md** opener rewritten to acknowledge both shipping plugins, the contribution-staging loop, and updated component counts (14 core agents / 11 PP agents / 5 core hooks / 8 PP checks).
- **`SECURITY.md`** added at repo root — disclosure policy for the private marketplace covering hooks, agent definitions, and bundled MCP server.
- **`.github/ISSUE_TEMPLATE/`** added (`bug_report.md`, `feature_request.md`, `proposed_lesson.md`, `config.yml`). `proposed_lesson.md` mirrors the contribution-staging flow.
- **`checklists/release-checklist.md`** + **`checklists/new-plugin-checklist.md`** added; `checklists/README.md` updated to point to both. Version examples in the release checklist use the post-realignment values (0.6.0 / 0.7.0 / 0.4.0) and acknowledge that `release.yml` workflow auto-publish is still a planned follow-up.
- `docs/architecture.md` Status table aligned to current versions (0.6.0 / 0.7.0); planned-plugins line points to the open PRs #14 / #15 / #16.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. No breaking changes — both plugins are minor bumps. The new `guard-recursive-spawn` hook is advisory by default; existing edits will not be blocked.

## marketplace 0.3.0 — 2026-05-21 (later same day)

### ravenclaude-core 0.5.0

Catch-up release that ports the marketplace's own self-review improvements into the plugin so consumer projects benefit:

- New skill `skills/audit-ci-gates.md` — guides any consuming agent that touches a CI workflow through the gate-audit-by-fixture pattern. Encodes the rule "for every CI step, prove it can fail on a known-bad input AND pass on a known-good input." References the canonical best-practice doc + the runnable scaffold below.
- New template `templates/agent-ready-repo/audit-gates.sh.template` — a runnable Bash scaffold the consumer's `/init-agent-ready` can drop into `scripts/audit-gates.sh`. Includes the gate-audit pattern (backup → mutate → assert → restore, with EXIT trap), idempotent fixture helpers, and a worked example block consumers replace with their own gates.
- New templates `templates/agent-ready-repo/.prettierrc.json.template` + `.prettierignore.template` — sensible prettier defaults (markdown line-wrap preserved; markdown excluded by default to avoid prose-reflow noise) that consumer projects can opt into via the updated `/init-agent-ready` command.
- `commands/init-agent-ready.md` — adds an optional Step 6 / new question 3: "should we add the CI-hygiene scaffold?" Three files written when accepted: `.prettierrc.json`, `.prettierignore`, `scripts/audit-gates.sh` (made executable).

Catch-up version-bump note: this release also captures content shipped in earlier marketplace commits that didn't bump retroactively — agent label drift cleanup (PR 4), constitution downgrade for run artifacts (PR 5), and the `to_specialist` / power-platform §6 SOP cross-link reconciliation (PR 7). Consumers who installed at 0.4.0 before those PRs will get all of that content along with the 0.5.0 additions above on next `/plugin marketplace update`.

### power-platform 0.6.1

- `CLAUDE.md` §6 now references the cross-plugin Structured Output Protocol JSON block that all 10 power-platform agents emit. Previously the section listed only the Markdown Output Contract; consumers reading §6 in isolation would have missed the JSON contract. (PR 7 in the marketplace; catch-up bump.)

### Marketplace meta

- `docs/architecture.md` Status table refreshed (was stale at ravenclaude-core 0.2.4 / power-platform 0.5.2).
- `docs/best-practices/ci-gate-audit.md` added (canonical Absolute Rule for CI gate hygiene).
- `scripts/audit-gates.sh` shipped at the marketplace level and wired into `validate-marketplace.yml` as a meta-test step. 10 gates × 2 fixtures = 21 assertions, all passing.
- `.prettierrc.json` + `.prettierignore` shipped at the marketplace level (the templates above mirror these).
- `.github/workflows/validate-marketplace.yml` gained behavioral hook tests, prettier check, actionlint check, email-leak guard, and the gate-audit meta-step.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins` picks up everything. Re-run `/init-agent-ready` in any project that wants the new optional CI-hygiene scaffold; existing files are not overwritten without explicit approval.

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
