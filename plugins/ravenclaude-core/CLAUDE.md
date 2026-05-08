# RavenClaude — Project Constitution

> This file is the **single source of truth** for how Claude Code (and every spawned sub-agent) operates in this repository. It is loaded automatically into every Claude session. Treat every rule here as a hard constraint unless the user explicitly overrides it in-session.

---

## 1. Project Overview

**Name:** RavenClaude
**Purpose:** A production-grade Claude Code template that bootstraps the *Team Lead + Specialized Agents* manager pattern (Architect, Coder, Tester, Reviewer, Security, and more) with git worktrees, hooks, and strict quality gates.
**Status:** Template repository. The "product" of this repo is the `.claude/` directory plus this constitution.

### Detected stack (this repo, as of 2026-05-07)
This is a **meta-template**, not an application. Stack-detection probes returned:

| Probe | Result |
|-------|--------|
| Application lockfiles (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Gemfile`, `pom.xml`, …) | none present |
| CI configuration (`.github/workflows/`, `.gitlab-ci.yml`) | none present |
| Source-file extensions present | `.md` (24), `.sh` (3), `.json` (2) |

Concretely, this repo consists of:
- **Markdown** — the constitution (`CLAUDE.md`), 7 agent definitions, 5 skills, 4 rules, 1 README. Authoring style: GFM, ATX headings, no trailing whitespace, fenced code blocks with language tags.
- **Bash** — 3 hooks under `.claude/hooks/` (`format-on-write.sh`, `guard-destructive.sh`, `remind-tests.sh`). All start with `#!/usr/bin/env bash` and use `set -euo pipefail`.
- **JSON** — `.claude/settings.json` (shared) and `.claude/settings.local.json` (gitignored). Both reference the Claude Code settings JSON Schema.

There is no language runtime or build step. Validation = JSON-parse the settings, syntax-check the shell scripts, sanity-check the Markdown links.

### Auto-detect targets (Team Lead checklist when this template is applied to a real repo)
When you copy `.claude/` and `CLAUDE.md` into an actual project, replace the table above with that project's real stack and update §4 commands. Use this checklist:

- [ ] Detect primary language(s) from lockfiles (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Gemfile`, …)
- [ ] Detect test runner (`vitest`, `jest`, `pytest`, `go test`, …) and record the exact invocation in §4
- [ ] Detect linter/formatter (`eslint`, `ruff`, `gofmt`, `prettier`, `biome`, …) and record exact invocations
- [ ] Detect CI provider (`.github/workflows`, `.gitlab-ci.yml`, …) so reviewers know what gates run remotely

---

## 2. Coding Standards & Style

These apply to every line of code Claude or any sub-agent writes:

1. **Match existing style first.** Before writing new code, read 1–2 nearby files and mirror their patterns (naming, imports, error handling, file layout). Do not impose a style the codebase has not adopted.
2. **No speculative abstraction.** Three similar lines beats a premature helper. Don't add config knobs, feature flags, or extension points for hypothetical future needs.
3. **No comments that restate code.** Only comment the *why*: a non-obvious invariant, a workaround for a known bug, a constraint from an external system. If removing the comment wouldn't confuse a future reader, delete it.
4. **No backwards-compat shims unless asked.** When refactoring, delete the old path; don't leave `// removed` markers, unused re-exports, or `_legacyFoo` aliases.
5. **Trust internal callers.** Validate at system boundaries (HTTP handlers, queue consumers, CLI entry points). Don't re-validate inside helpers.
6. **Errors are values, not decorations.** Catch only what you can meaningfully handle. Re-throwing with a wrapper message that adds nothing is noise.
7. **Names carry the docs.** Identifiers should make docstrings unnecessary. If you reach for a long comment, first try a better name.
8. **Format on save.** Every file written by an agent must pass the project's formatter before the agent reports completion (see §4).

See [`.claude/rules/coding-standards.md`](.claude/rules/coding-standards.md) for the long-form version.

---

## 3. Git Workflow

### Branch model
- `main` — always green, always deployable. Direct pushes are forbidden.
- `feat/<short-slug>` — new functionality.
- `fix/<short-slug>` — bug fixes.
- `chore/<short-slug>` — tooling, deps, infra.
- `agent/<role>/<slug>` — branches owned by a specific agent worktree (e.g. `agent/coder/auth-rewrite`).

### Commits
- Conventional Commits format: `type(scope): subject` (`feat(auth): add refresh-token rotation`).
- Subject ≤ 72 chars, imperative mood, no trailing period.
- Body explains *why*, not *what* — the diff already shows what.
- One logical change per commit. If you find yourself writing "and" in the subject, split it.
- **Never** `--amend` a pushed commit. **Never** `--no-verify`. **Never** force-push `main`.

### Worktrees (mandatory for parallel agents)
Every long-running sub-agent task runs in an isolated git worktree under `.claude/worktrees/<role>-<slug>/`. This prevents agents from stomping on each other's working trees.

```bash
git worktree add .claude/worktrees/coder-auth agent/coder/auth-rewrite
# … agent works here …
git worktree remove .claude/worktrees/coder-auth   # when done
```

The Team Lead is responsible for cleanup. Stale worktrees are pruned weekly via `git worktree prune`.

See [`.claude/skills/create-pr.md`](.claude/skills/create-pr.md) and [`.claude/rules/git-workflow.md`](.claude/rules/git-workflow.md).

---

## 4. Mandatory Quality Gates

**No agent may report a task complete until all of the following pass.** This is non-negotiable.

### Gates for this repo (template-only)
Because there is no application code, the gates check that the template itself is valid:

| Gate | Command | Owner |
|------|---------|-------|
| JSON validity | `python3 -m json.tool .claude/settings.json > /dev/null && python3 -m json.tool .claude/settings.local.json > /dev/null` | author agent |
| Shell syntax | `bash -n .claude/hooks/*.sh` | author agent |
| Hook executability | `test -x .claude/hooks/format-on-write.sh -a -x .claude/hooks/guard-destructive.sh -a -x .claude/hooks/remind-tests.sh` | author agent |
| Markdown link sanity | `grep -rEn '\]\(\.\./?[^)]+\)' .claude/ CLAUDE.md` then spot-check that referenced paths exist | author agent |
| Code review | rubric in [`.claude/agents/code-reviewer.md`](.claude/agents/code-reviewer.md) | code-reviewer agent |
| Security review | rubric in [`.claude/agents/security-reviewer.md`](.claude/agents/security-reviewer.md) | security-reviewer agent (when touching hooks or `settings.json` permissions) |

### Gate placeholders for downstream projects
When this template is applied to a real repo, replace the table above with the project's actual gates. Reference shape:

| Gate | Command (fill in per project) | Owner |
|------|-------------------------------|-------|
| Format | `<formatter> --check .` (e.g. `prettier --check .`, `ruff format --check`, `gofmt -l .`) | author agent |
| Lint | `<linter>` (e.g. `eslint .`, `ruff check`, `golangci-lint run`) | author agent |
| Type-check | `<typechecker>` (e.g. `tsc --noEmit`, `mypy`, `pyright`) | author agent |
| Unit tests | `<test runner>` (e.g. `vitest run`, `pytest -q`, `go test ./...`) | author agent |
| Integration tests | project-specific | tester-qa agent |
| Code review | rubric in [`.claude/agents/code-reviewer.md`](.claude/agents/code-reviewer.md) | code-reviewer agent |
| Security review | rubric in [`.claude/agents/security-reviewer.md`](.claude/agents/security-reviewer.md) | security-reviewer agent (if touching auth/crypto/IO) |

If a gate fails, **fix the root cause**. Do not silence the gate, do not skip the test, do not `--no-verify`.

The full automated suite is invoked via the [`run-full-test-suite`](.claude/skills/run-full-test-suite.md) skill.

---

## 5. Agent Team Rules

The **Team Lead** (top-level Claude session) **delegates** work to specialized sub-agents, integrates their reports, and is the only role allowed to make user-facing commitments. For multi-agent dispatches, the Team Lead loads the [`spawn-team`](.claude/skills/spawn-team.md) skill — that's the playbook for picking specialists, sequencing them, and re-routing on blockers.

Sub-agents operate in isolation, see only the brief they're given, and return structured reports. **Sub-agents do not spawn other sub-agents** — the dependency graph stays a flat tree with the Team Lead at the root.

### Team roster
| Agent | When to spawn | Definition |
|-------|---------------|------------|
| Architect | Technical conscience across the software lifecycle — upfront design AND re-consults at phase boundaries (tests contradict plan, scope expands, reviewer flags structural issue, iteration requires re-plan) | [`.claude/agents/architect.md`](.claude/agents/architect.md) |
| Backend Coder | Server, API, DB, jobs | [`.claude/agents/backend-coder.md`](.claude/agents/backend-coder.md) |
| Frontend Coder | UI, components, client state | [`.claude/agents/frontend-coder.md`](.claude/agents/frontend-coder.md) |
| Fullstack Coder | Cross-cutting features touching both ends | [`.claude/agents/fullstack-coder.md`](.claude/agents/fullstack-coder.md) |
| Tester / QA | Test design, flake hunting, coverage gaps | [`.claude/agents/tester-qa.md`](.claude/agents/tester-qa.md) |
| Code Reviewer | Pre-merge sanity, style, design | [`.claude/agents/code-reviewer.md`](.claude/agents/code-reviewer.md) |
| Security Reviewer | Anything touching auth, crypto, secrets, untrusted input | [`.claude/agents/security-reviewer.md`](.claude/agents/security-reviewer.md) |
| Deep Researcher | Multi-source research, troubleshooting unfamiliar errors, verifying claims, going deeper than a single web search | [`.claude/agents/deep-researcher.md`](.claude/agents/deep-researcher.md) |
| Documentarian | Stakeholder-facing prose — exec summaries, decision memos, runbooks, release notes, READMEs, partner briefs | [`.claude/agents/documentarian.md`](.claude/agents/documentarian.md) |
| Designer | UX direction and visual design — wireframes, user flows, screen layouts, accessibility checks, design specs for any visual artifact | [`.claude/agents/designer.md`](.claude/agents/designer.md) |
| Prompt Engineer | Author / critique / refactor agent definitions, skills, and prompt patterns across the hub and Expert repos; household-wide AI library curator | [`.claude/agents/prompt-engineer.md`](.claude/agents/prompt-engineer.md) |
| Project Manager | RAID log, task list, weekly status, activity log, stakeholder register (PMP / PMBOK 7 aligned) | [`.claude/agents/project-manager.md`](.claude/agents/project-manager.md) |
| Partner Success Manager | Partner profiles, success plans, QBR prep, health scores, onboarding, AI workflow library | [`.claude/agents/partner-success-manager.md`](.claude/agents/partner-success-manager.md) |

### Collaboration protocol
1. **Team Lead briefs the agent like a new colleague.** Include: goal, context, what's been tried, success criteria, response-length cap. Never just delegate "fix the bug."
2. **One agent owns one branch.** Two agents must not edit the same worktree.
3. **Agents do not call other agents.** Only the Team Lead spawns sub-agents. This keeps the dependency graph a tree.
4. **Reports are structured.** Every agent ends with: `Status: ✅/❌`, `Files changed:`, `Gates passed:`, `Open questions:`.
5. **Trust but verify.** The Team Lead reads the diff before reporting to the user — agent self-reports describe intent, not always reality.
6. **No silent escalation.** If an agent hits a blocker (ambiguous spec, missing access, conflicting requirement), it stops and reports — it does not guess.

See [`.claude/rules/agent-collaboration.md`](.claude/rules/agent-collaboration.md) for the detailed protocol.

---

## 6. Security & Permissions

- **Never commit secrets.** `.env`, `credentials.*`, `*.pem`, `*.key` are gitignored. If you find a secret in the diff, abort the commit and rotate the key.
- **Never log secrets.** Tokens, passwords, PII — redact at the boundary, not at the log line.
- **Untrusted input is hostile.** Treat HTTP bodies, query params, file uploads, and queue messages as adversarial. Validate, then parse.
- **Dependencies are a supply chain.** Pin versions, use lockfiles, prefer the standard library when the std-lib does the job.
- **Least-privilege tools.** Each sub-agent's `tools:` frontmatter lists only what it needs (see agent files). Don't broaden without reason.
- **Destructive commands need explicit user approval** every time, not once: `rm -rf`, `git reset --hard`, `git push --force`, `DROP TABLE`, package downgrades, CI/CD edits.

See [`.claude/rules/security.md`](.claude/rules/security.md).

---

## 7. Common Skills & Hooks

Reusable, parameterized prompts live in `.claude/skills/`. Invoke with `/skill-name`.

| Skill | Purpose |
|-------|---------|
| [`run-full-test-suite`](.claude/skills/run-full-test-suite.md) | Run format → lint → typecheck → tests in order, fail fast |
| [`create-pr`](.claude/skills/create-pr.md) | Open a PR with the project's standard template |
| [`spawn-team`](.claude/skills/spawn-team.md) | Team Lead dispatch playbook: pick specialists, brief them, sequence, and re-route on blockers |
| [`new-worktree`](.claude/skills/new-worktree.md) | Create an isolated worktree for a sub-agent |
| [`cleanup-worktrees`](.claude/skills/cleanup-worktrees.md) | Remove finished worktrees and prune branches |

### Hooks (configured in `.claude/settings.json`)
- **PostToolUse on Edit/Write** → run formatter + linter on the touched file
- **Stop** → reminder to run the full test suite if any source files changed
- **PreToolUse on Bash** → block destructive commands without explicit user confirmation

---

## 8. House Rules (short version)

1. Read before you write.
2. Match existing style; don't invent new ones.
3. Make it work, then make it clean — never the reverse.
4. Tests are part of the change, not a follow-up PR.
5. If you don't understand the code, ask — don't guess.
6. Commit small, commit often, commit green.
7. The Team Lead is the only voice the user hears.
