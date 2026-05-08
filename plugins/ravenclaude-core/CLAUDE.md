# Team Constitution — `ravenclaude-core` plugin

> This file is the team constitution that ships with the `ravenclaude-core` Claude Code plugin. When the plugin is installed in a project, copy this file (or its relevant sections) into your project's root `CLAUDE.md` and adapt it to your stack. Treat every rule here as a hard constraint unless explicitly overridden.

---

## 1. Adapting this constitution to your project

This plugin is **domain-neutral**. It bundles agents, skills, hooks, and rules that work across any project. To make it effective in *your* project:

1. Detect your primary language(s) from lockfiles (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Gemfile`, …) and record them in your project's `CLAUDE.md`.
2. Detect the test runner (`vitest`, `jest`, `pytest`, `go test`, …) and record the exact invocation in §4 of your project's `CLAUDE.md`.
3. Detect the linter/formatter (`eslint`, `ruff`, `gofmt`, `prettier`, `biome`, …) and record exact invocations.
4. Detect the CI provider (`.github/workflows`, `.gitlab-ci.yml`, …) so reviewers know what gates run remotely.

The agents in this plugin (architect, coders, reviewers, etc.) read your project's `CLAUDE.md` for stack-specific commands and your project's git history for stack-specific patterns.

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

See [`rules/coding-standards.md`](rules/coding-standards.md) for the long-form version.

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

See [`skills/create-pr.md`](skills/create-pr.md) and [`rules/git-workflow.md`](rules/git-workflow.md).

---

## 4. Mandatory Quality Gates

**No agent may report a task complete until all of the following pass.** This is non-negotiable.

### Gate template (fill in per project)

Replace the placeholders below with your project's actual commands and record them in your project's `CLAUDE.md`. The agents in this plugin read your project's `CLAUDE.md` to find these commands.

| Gate | Command (fill in per project) | Owner |
|------|-------------------------------|-------|
| Format | `<formatter> --check .` (e.g. `prettier --check .`, `ruff format --check`, `gofmt -l .`) | author agent |
| Lint | `<linter>` (e.g. `eslint .`, `ruff check`, `golangci-lint run`) | author agent |
| Type-check | `<typechecker>` (e.g. `tsc --noEmit`, `mypy`, `pyright`) | author agent |
| Unit tests | `<test runner>` (e.g. `vitest run`, `pytest -q`, `go test ./...`) | author agent |
| Integration tests | project-specific | tester-qa agent |
| Code review | rubric in [`agents/code-reviewer.md`](agents/code-reviewer.md) | code-reviewer agent |
| Security review | rubric in [`agents/security-reviewer.md`](agents/security-reviewer.md) | security-reviewer agent (if touching auth/crypto/IO) |

If a gate fails, **fix the root cause**. Do not silence the gate, do not skip the test, do not `--no-verify`.

The full automated suite is invoked via the [`run-full-test-suite`](skills/run-full-test-suite.md) skill.

---

## 5. Agent Team Rules

The **Team Lead** (top-level Claude session) **delegates** work to specialized sub-agents, integrates their reports, and is the only role allowed to make user-facing commitments. For multi-agent dispatches, the Team Lead loads the [`spawn-team`](skills/spawn-team.md) skill — that's the playbook for picking specialists, sequencing them, and re-routing on blockers.

Sub-agents operate in isolation, see only the brief they're given, and return structured reports. **Sub-agents do not spawn other sub-agents** — the dependency graph stays a flat tree with the Team Lead at the root.

### Team roster
| Agent | When to spawn | Definition |
|-------|---------------|------------|
| Architect | Technical conscience across the software lifecycle — upfront design AND re-consults at phase boundaries (tests contradict plan, scope expands, reviewer flags structural issue, iteration requires re-plan) | [`agents/architect.md`](agents/architect.md) |
| Backend Coder | Server, API, DB, jobs | [`agents/backend-coder.md`](agents/backend-coder.md) |
| Frontend Coder | UI, components, client state | [`agents/frontend-coder.md`](agents/frontend-coder.md) |
| Fullstack Coder | Cross-cutting features touching both ends | [`agents/fullstack-coder.md`](agents/fullstack-coder.md) |
| Tester / QA | Test design, flake hunting, coverage gaps | [`agents/tester-qa.md`](agents/tester-qa.md) |
| Code Reviewer | Pre-merge sanity, style, design | [`agents/code-reviewer.md`](agents/code-reviewer.md) |
| Security Reviewer | Anything touching auth, crypto, secrets, untrusted input | [`agents/security-reviewer.md`](agents/security-reviewer.md) |
| Deep Researcher | Multi-source research, troubleshooting unfamiliar errors, verifying claims, going deeper than a single web search | [`agents/deep-researcher.md`](agents/deep-researcher.md) |
| Documentarian | Stakeholder-facing prose — exec summaries, decision memos, runbooks, release notes, READMEs, partner briefs | [`agents/documentarian.md`](agents/documentarian.md) |
| Designer | UX direction and visual design — wireframes, user flows, screen layouts, accessibility checks, design specs for any visual artifact | [`agents/designer.md`](agents/designer.md) |
| Prompt Engineer | Author / critique / refactor agent definitions, skills, and prompt patterns across the hub and Expert repos; household-wide AI library curator | [`agents/prompt-engineer.md`](agents/prompt-engineer.md) |
| Project Manager | RAID log, task list, weekly status, activity log, stakeholder register (PMP / PMBOK 7 aligned) | [`agents/project-manager.md`](agents/project-manager.md) |
| Partner Success Manager | Partner profiles, success plans, QBR prep, health scores, onboarding, AI workflow library | [`agents/partner-success-manager.md`](agents/partner-success-manager.md) |

### Collaboration protocol
1. **Team Lead briefs the agent like a new colleague.** Include: goal, context, what's been tried, success criteria, response-length cap. Never just delegate "fix the bug."
2. **One agent owns one branch.** Two agents must not edit the same worktree.
3. **Agents do not call other agents.** Only the Team Lead spawns sub-agents. This keeps the dependency graph a tree.
4. **Reports are structured.** Every agent ends with: `Status: ✅/❌`, `Files changed:`, `Gates passed:`, `Open questions:`.
5. **Trust but verify.** The Team Lead reads the diff before reporting to the user — agent self-reports describe intent, not always reality.
6. **No silent escalation.** If an agent hits a blocker (ambiguous spec, missing access, conflicting requirement), it stops and reports — it does not guess.

See [`rules/agent-collaboration.md`](rules/agent-collaboration.md) for the detailed protocol.

---

## 6. Security & Permissions

- **Never commit secrets.** `.env`, `credentials.*`, `*.pem`, `*.key` are gitignored. If you find a secret in the diff, abort the commit and rotate the key.
- **Never log secrets.** Tokens, passwords, PII — redact at the boundary, not at the log line.
- **Untrusted input is hostile.** Treat HTTP bodies, query params, file uploads, and queue messages as adversarial. Validate, then parse.
- **Dependencies are a supply chain.** Pin versions, use lockfiles, prefer the standard library when the std-lib does the job.
- **Least-privilege tools.** Each sub-agent's `tools:` frontmatter lists only what it needs (see agent files). Don't broaden without reason.
- **Destructive commands need explicit user approval** every time, not once: `rm -rf`, `git reset --hard`, `git push --force`, `DROP TABLE`, package downgrades, CI/CD edits.

See [`rules/security.md`](rules/security.md).

---

## 7. Common Skills & Hooks

Reusable, parameterized prompts live in `skills/`. Invoke with `/skill-name`.

| Skill | Purpose |
|-------|---------|
| [`run-full-test-suite`](skills/run-full-test-suite.md) | Run format → lint → typecheck → tests in order, fail fast |
| [`create-pr`](skills/create-pr.md) | Open a PR with the project's standard template |
| [`spawn-team`](skills/spawn-team.md) | Team Lead dispatch playbook: pick specialists, brief them, sequence, and re-route on blockers |
| [`new-worktree`](skills/new-worktree.md) | Create an isolated worktree for a sub-agent |
| [`cleanup-worktrees`](skills/cleanup-worktrees.md) | Remove finished worktrees and prune branches |

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
