# Rule: Git Workflow (long form)

Expands on §3 of CLAUDE.md.

## Branch naming
| Prefix | Use |
|--------|-----|
| `feat/` | new functionality |
| `fix/` | bug fix |
| `chore/` | tooling, deps, infra |
| `docs/` | docs only |
| `refactor/` | code shape change, no behavior change |
| `agent/<role>/` | branches owned by a sub-agent worktree |

Slug: kebab-case, ≤ 40 chars, descriptive but tight. `feat/auth-refresh-rotation`, not `feat/stuff`.

## Commits
- Conventional Commits: `type(scope): subject`.
- Subject: imperative, ≤ 72 chars, no trailing period. Capitalize the first word after the colon? Match the repo's existing style.
- Body: wrap at 80 chars. Explain *why*. Reference issues with `Refs #123` or `Fixes #123`.
- One logical change per commit. If a commit has "and" in the subject, split it.
- Test commits: prefer to bundle tests with the code they cover. A standalone "add tests" commit is fine if it's filling pre-existing gaps.

## Sequencing a multi-commit change
1. Refactor commits first (no behavior change).
2. Then the behavior change itself.
3. Then docs/comments/cleanup.
This makes review and bisect dramatically easier.

## What never to do without explicit user approval
- `git push --force` / `--force-with-lease` to a shared branch.
- `git reset --hard` on anything past `HEAD`.
- `git rebase -i` past commits that are pushed.
- `git commit --amend` on a pushed commit.
- `git branch -D` on a branch with unique commits.
- `git clean -fdx`.
- Anything `--no-verify`.

When a hook fails: **fix the underlying issue and create a NEW commit**. Never amend after a hook failure (the failed commit didn't happen — `--amend` would modify the *previous* commit).

## Worktrees (mandatory for parallel agents)
- Path: `.claude/worktrees/<role>-<slug>/`
- Branch: `agent/<role>/<slug>`
- Base from `origin/main` (fetched fresh).
- The Team Lead creates and tears down worktrees via [`new-worktree`](../skills/new-worktree/SKILL.md) and [`cleanup-worktrees`](../skills/cleanup-worktrees/SKILL.md).
- Two agents, two worktrees. Never share.

## Rebases vs. merges
- Within an agent branch: rebase on top of `main` to keep history linear.
- Integrating an agent branch into a feature branch: project preference. Default to fast-forward when possible, `--no-ff` when the feature branch wants explicit branch points for review.
- Merge `main` into a long-lived feature branch periodically; don't let it drift more than a week.

## Pull requests
- Opened by the Team Lead, never by a sub-agent.
- Title in Conventional Commit format, ≤ 72 chars.
- Body uses the template in [`create-pr`](../skills/create-pr/SKILL.md).
- Don't merge your own PR without an explicit user "ship it." Even on solo projects, the human approves the merge.
