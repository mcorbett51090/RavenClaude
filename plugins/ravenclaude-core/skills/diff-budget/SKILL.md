---
target_path: plugins/ravenclaude-core/skills/diff-budget/SKILL.md
description: Enforces a per-PR file-count and LoC budget. PRs touching >5 files or >400 LoC route to architectural review before merge. Counters T-1 (premature abstraction) + T-4 (going off-script) — Copilot CLI degrades sharply past 10 files per file, and uncontrolled diff growth is the strongest predictor of off-pattern mutations.
allowed-tools: Bash, Read
audience: [architect, coder, reviewer]
counters_failure_modes: [T-1 premature abstraction, T-4 going off-script, T-7 lost-in-context]
sources:
  - /tmp/research-codex-failure-modes.md §1 C-1 (Copilot 10+ file degradation), §5 M-15, §8 #9, §9a
---

# diff-budget

Per-PR diff budget: aborts (or routes to architectural review) when a single PR's diff exceeds documented file-count or LoC thresholds. Implements the M-15 "diff-size circuit breaker" from research §5.

## The failure mode it counters

From research §1 (Copilot CLI failure pattern C-1):

> "Copilot Coding Agent performs reasonably well on tasks touching one or two files, but tasks requiring changes across 10+ files with architectural implications produce noticeably more mistakes than competing tools."

And §5 M-15 (Onsen DEV):

> "You can automate a diff review to abort the loop if the diff is much larger than expected or touches critical files outside the task scope, indicating the agent might have 'gone rogue'."

Bigger diffs correlate with:
- **T-1 premature abstraction** — agent built a `ChartFactoryProvider` for 3 components
- **T-4 going off-script** — agent edited files outside the task scope to "fix" a related concern
- **T-7 lost-in-context** — agent reimplemented helpers it couldn't find in the time it had

## The thresholds (defaults — overridable per brief)

| Tier | Files | LoC | Action |
|---|---|---|---|
| **Green** | ≤ 5 | ≤ 400 | Proceed without gating |
| **Yellow** | 6-10 | 401-800 | Route to architect for review **before merge**; require justification in PR body |
| **Red** | > 10 | > 800 | **Block** — split the PR or route to architectural review **before further work** |

> **Why 5 files / 400 LoC for the Green tier.** Copilot's documented degradation threshold is ~10 files; we set Green at half that to leave headroom for the agent's working memory. 400 LoC is the practical ceiling for one human reviewer in one sitting without losing the architectural shape.

## When invoked

The skill fires:

- **PreToolUse on `Write` / `Edit` / `MultiEdit`** — checks if the staged diff would push past the budget BEFORE the write lands.
- **Pre-commit hook** — final check before the commit object is created.
- **Pre-merge CI gate** — backstop; cross-tool (catches PRs created via gh/MCP/direct API).

## How the budget reads from the brief

A brief / task spec can override the defaults via YAML frontmatter:

```yaml
diff_budget:
  files: 8          # this task is genuinely cross-cutting
  loc: 600
  rationale: "Refactoring the chart-renderer hierarchy per ADR-014; expected to touch six files in components/charts/"
```

Without an override, defaults apply. The skill REFUSES an unrestricted budget — you must justify every increase in writing.

## The architectural-review handoff

When the budget is exceeded:

1. **Halt the current Write/Edit.**
2. **Emit the M-15 escalation message** with:
   - Files touched / LoC delta so far
   - List of files outside the brief's declared scope
   - The task ID / spec section the diff was supposedly satisfying
3. **Route to architect agent** (or the tribunal's decision-review for binding yes/no) with the question: "Should this diff exceed budget? Justification: [agent's stated rationale]."
4. **Default to NO** — if the architect can't be reached or the verdict is `defer`, the diff is blocked.

## Composition with `enforce-layout.sh`

`enforce-layout.sh` (existing) catches *off-pattern paths* — a Write to a directory not in `.repo-layout.json` `allowed_globs`. `diff-budget` catches *on-pattern but oversize* — many writes to allowed paths that together exceed the budget. They're complementary; both fire on PreToolUse.

## Composition with `wall-handling`

A blown diff budget is often the *symptom* of a wall. When the budget trips:

1. First check: is the agent in a wall-hit loop (same tool + error 3+ times)?  → invoke `wall-handling` first.
2. If not a wall, it's likely **T-1 premature abstraction** or **T-4 going off-script** — route to architectural review.

## Anti-patterns

| Symptom | Likely failure |
|---|---|
| 9 files changed for a "fix typo in label" task | T-4 going off-script |
| A new `utils/`, `lib/`, or `helpers/` directory created in this PR | T-1 premature abstraction + T-7 reimplemented helpers |
| A `Provider` / `Factory` / `Registry` for ≤3 instances | T-1 premature abstraction |
| The brief said "one component" and the diff has 11 files | The brief and the work disagree — architectural review |
| File count is in budget but LoC is 4× expected | The agent expanded scope inside files instead of across — same review needed |

## Configuration

The skill reads `.ravenclaude/diff-budget.yaml` for project-level overrides:

```yaml
defaults:
  files: 5
  loc: 400
yellow:
  files: 10
  loc: 800
red:
  files: 11   # anything over this is auto-blocked
  loc: 801
exempt_paths:
  - "docs/**/*.md"         # docs PRs are commonly large; exempt
  - "**/*.snap"            # snapshot test files
  - "**/CHANGELOG.md"
```

`exempt_paths` allows generated artifacts (snapshot tests, dashboard generated HTML, CHANGELOG bumps) without inflating the LoC count.

## What "done" looks like

The skill succeeds when:

1. Each Write/Edit/MultiEdit checked the running diff total before landing.
2. The Green-tier PR landed without prompting.
3. Any Yellow/Red trip was logged to `.ravenclaude/runs/diff-budget/` with the architect verdict.
4. The PR body cites the budget tier and the rationale (auto-populated by the skill).

## Sources

- NxCode — *Is GitHub Copilot Getting Worse in 2026?* (research ledger [5]; the 10+ file degradation finding)
- Developers Digest — *GitHub Copilot Coding Agent and CLI* (ledger [7])
- Onsen (DEV) — *AI Code Editing Gone Too Far: Stop Over-Editing Now* (ledger [19])
- Anthropic Engineering — *Effective harnesses for long-running agents* (ledger [15])

Full ledger: `/tmp/research-codex-failure-modes.md` §Sources.
