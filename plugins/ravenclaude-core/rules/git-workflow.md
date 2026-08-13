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
- **Conventional Commits — the gate, not just a convention.** Every commit subject is `type(scope): subject` (spec: conventionalcommits.org, retrieved 2026-08-12 — see the catalog below). The `type` prefix is what makes the changelog and the next version **machine-derivable**: `fix:` → a **PATCH** bump, `feat:` → a **MINOR** bump, and a `BREAKING CHANGE:` footer (or a `!` after the type/scope) → a **MAJOR** bump. Keep the mapping honest and a release tool (changesets / semantic-release / release-please) can cut the version and CHANGELOG from history with no hand-editing. **Enforceable:** a semantic-PR-title / commit-message CI check (widely gated — `vitejs/vite`, `django/django`, `microsoft/vscode`, `renovate`, `pnpm`, `cli/cli` all run one). **Teachable:** pick the `type` by the *user-visible effect* of the change, not the size of the diff.
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

## Branch hygiene — retiring merged branches and worktrees

**Default to `delete_branch_on_merge: true` on every repo.** It is the only fix that
prevents the pile instead of clearing it. Verify with
`gh api repos/OWNER/REPO --jq .delete_branch_on_merge`; set it with
`gh api -X PATCH repos/OWNER/REPO -f delete_branch_on_merge=true`. This covers the
remote side only — local branches and worktrees still accumulate, which is what the
rest of this section is for.

**Never sweep on "is it merged?" alone.** That question clears branches that still hold
work. Run all four gates, in order, and delete only what passes every one. They are not
redundant — each catches a case the previous one already cleared:

| # | Gate | Check | Catches |
|---|---|---|---|
| 1 | Merged | `git rev-list --count <base>..<branch>` is `0` **OR** a merged PR whose `headRefOid` equals the local tip | branches whose commits aren't in the base yet |
| 2 | Worktree clean | `git -C <worktree> status --porcelain` is empty | **uncommitted work** — the real loss risk; the branch ref is recoverable, an uncommitted file is not |
| 3 | No open PR | branch is not a `headRefName` in `gh pr list --state open` | deleting it **closes the PR** and loses its review thread |
| 4 | Git's own veto | `git branch -d` (**never `-D`**) | git's independent second opinion on gate 1, incl. a remote ref behind the local branch |

> **⚠ Ancestry alone is NOT proof of merged-ness — squash merges are invisible to it.**
> A squash merge replays the branch as one *new* commit, so the originals are never
> ancestors of the base and `rev-list` reports the branch as unmerged **forever**.
> Two consequences, both load-bearing:
>
> - **Gate 1 needs the second proof** (merged PR whose head SHA equals the local tip —
>   the pre-squash tip). The tip must *match*: `gh pr list --head <branch>` by name alone
>   is unsound when branch names get reused, because a stale merged PR would then clear a
>   branch carrying genuinely unmerged work.
> - **Gate 4 (`git branch -d`) is blind the same way**, so a squash-merged branch cannot be
>   retired with `-d` at all. That case routes to
>   [`${CLAUDE_PLUGIN_ROOT}/scripts/cleanup-branches.sh`](../scripts/cleanup-branches.sh), the **one**
>   sanctioned `-D` escape hatch (house rule 5) — do not add a second force-delete path.
>
> This is not hypothetical: on 2026-08-05 a sweep reported **13 of 15** RavenPower branches
> as "unmerged" when every one had been squash-merged. Ancestry-only had them backwards.

Gate 4 is why this uses `-d`: it is a check by something that doesn't share your
reasoning, and it is also why the sweep doesn't trip `guard-destructive.sh` (which
blocks `-D`). Likewise use `git worktree remove` **without** `--force`, so a dirty
worktree vetoes its own removal. Record branch names + SHAs before deleting.

**Worked example (2026-08-04, RavenPower-Website, 31 branches).** Each of the last
three gates caught something the previous had passed: `forge/configurator-v2` was
fully merged but its worktree held an uncommitted file; `forge/page-allowance-reprice`
was merged and clean but had open PR #184; `forge/portal-intake-tree` passed all three
and git still refused `-d`. Result: 13 deleted, 3 saved that a merged-only sweep would
have destroyed.

**Run it:** [`${CLAUDE_PLUGIN_ROOT}/scripts/branch-hygiene.sh`](../scripts/branch-hygiene.sh) implements
all four gates, is **dry-run by default**, and fails closed if it can't reach `gh` (an
unprovable gate is not a passed gate). _(Consumer fallback if `${CLAUDE_PLUGIN_ROOT}` is unset:
`find ~/.claude/plugins/cache -name branch-hygiene.sh -path '*ravenclaude-core*'`, mirroring `bin/rc`.)_ Note dry-run is deliberately *looser* than
`--execute`, since gate 4 only renders a verdict at delete time.

**Scope — merged branches only.** For **unmerged/abandoned** work whose commits are not
in the base, gate 1 correctly refuses; that case needs
[`${CLAUDE_PLUGIN_ROOT}/scripts/archive-branch.sh`](../scripts/archive-branch.sh), which tags the tip so
it stays recoverable. See AGENTS.md house rule 5.

## Rebases vs. merges
- Within an agent branch: rebase on top of `main` to keep history linear.
- Integrating an agent branch into a feature branch: project preference. Default to fast-forward when possible, `--no-ff` when the feature branch wants explicit branch points for review.
- Merge `main` into a long-lived feature branch periodically; don't let it drift more than a week.

## Pull requests
- Opened by the Team Lead, never by a sub-agent.
- Title in Conventional Commit format, ≤ 72 chars.
- Body uses the template in [`create-pr`](../skills/create-pr/SKILL.md).
- Don't merge your own PR without an explicit user "ship it." Even on solo projects, the human approves the merge.
- **Once the human has approved**, the *mechanics* of landing the PR (including arming auto-merge from a remote/sandboxed session) live in [`../knowledge/remote-mcp-pr-landing.md`](../knowledge/remote-mcp-pr-landing.md) § "Arm auto-merge" — a mechanic that runs **after** approval, never a substitute for it.

## See also — CI & GitHub-development hardening
- [`../knowledge/github-actions-hardening.md`](../knowledge/github-actions-hardening.md) — the rules behind every gold-standard Actions gate (least-privilege `permissions:`, SHA-pinned actions, OIDC, the required-check `paths:`-filter trap, merge queue + CODEOWNERS).
- [`../knowledge/github-gold-standard-repos.md`](../knowledge/github-gold-standard-repos.md) — the durable best-practices catalog + the dated 30-repo exemplar snapshot the rules were extracted from.
