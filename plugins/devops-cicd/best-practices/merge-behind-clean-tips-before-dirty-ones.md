# Merge behind-clean tips before dirty ones

**Status:** Pattern
**Domain:** CI/CD pipeline design
**Applies to:** `devops-cicd`

When more than one pull request is ready, the order is part of the merge. Merging a conflicting pull request first forces every sibling to conflict against a base that is about to move again. Classify each tip, merge the clean ones, and remount a conflicting tip onto the trunk you actually have.

The procedure, the `gh` fields, and the ship checklist are [`../../ravenclaude-core/knowledge/source-control-operating-practices.md`](../../ravenclaude-core/knowledge/source-control-operating-practices.md). This file is the CI-side rule those steps sit on. Behind-first hand-merge order is already standing practice for the fleet that consumes this marketplace. Do not re-litigate it.

## Classify, then act

Read `gh pr view <n> --json state,mergeStateStatus,mergeable,headRefOid,statusCheckRollup` and `git status --porcelain`.

| State | Signal | Action |
|---|---|---|
| Up to date | `mergeStateStatus` is `CLEAN`, porcelain prints no lines, tip equals `headRefOid` | Merge once required checks are `success` on that SHA |
| Behind, clean | `BEHIND`, or the base has commits the PR lacks and the merge applies with no conflict | Update from the base. Wait for checks on the new SHA. Merge before any sibling that conflicts |
| Dirty | `DIRTY`, or porcelain prints a line, or the worktree tip is not `headRefOid` | Do not merge. Remount |
| Red | `UNSTABLE` | Hand the check back. A red tip is not a dirty tip |

`CLEAN` describes the committed trees. It says nothing about uncommitted files.

## Remount

Cut a new worktree from current `origin/<base>`. Replay only `origin/<base>..<old-headRefOid>`. Stop on a conflict and let the code owner decide the hunk. A replay that leaves the pull request's own diff unchanged is an update-branch commit. A hunk edit is a new diff and needs review.

## Order

1. Up to date and green, shortest dependency first.
2. Behind and clean, after the update's checks pass on the new SHA.
3. Dirty, remounted only after those have landed.
4. Stacks from the bottom. Graphite, retrieved 2026-11-05 from <https://graphite.com/docs/merge-stack-prs-github>: merge "from the bottom of the stack." Their settings note, <https://graphite.com/docs/github-configuration-guidelines>, says GitHub's merge queue can merge a stack out of order. Leave an upstack PR out of the queue while its parent is open.
5. Re-read `mergeStateStatus` after every merge. The rollup from before that merge does not describe the new base.

A migration merges before the code that reads the new shape.

## What the server should enforce

- **No queue:** require branches to be up to date before merging (strict). GitHub's protected-branch doc, retrieved 2026-11-05 from <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches>: strict means the head "must be up to date with the base branch before merging." Loose lets a green, lagging branch land.
- **Queue:** GitHub's merge-queue doc, retrieved the same day from <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue>, says the queue provides the same up-to-date benefit and tests each group against the latest base plus earlier entries. Required workflows must also trigger on `merge_group`, or the queue waits on a check that never starts. Do not hand-merge ahead of the queue.
- Where auto-merge is off on purpose, the hand procedure above is the substitute. Turning auto-merge on is a separate decision.

## See also

- [`./pipeline-required-checks-gate-the-merge.md`](./pipeline-required-checks-gate-the-merge.md) — which conclusions count, and which bots stay off the required list.
- [`./design-trunk-based-over-long-lived-branches.md`](./design-trunk-based-over-long-lived-branches.md) — why the branch should not have lived long enough to need this often.
