# Source-control operating practices

> **Last verified:** 2026-11-05. **Refresh trigger:** GitHub changes `mergeStateStatus`, what counts as a successful required check, or merge-queue rules; DORA restates the trunk-based bar; the fleet retires behind-first merge order.

The checklist an agent follows when it branches, updates a pull request, or merges. Specialist CI settings (strict checks versus a merge queue, `merge_group`, External Secrets) live in `devops-cicd` and are named at the bottom. This file is the procedure. It does not loosen a required check, raise a file budget, or authorize a production deploy.

## 1. Branch lifetime

Merge to the default branch at least daily. A branch that still exists the next day is late.

`rules/git-workflow.md` still says to merge `main` into a long-lived feature branch periodically and not to drift more than a week. This section supersedes that sentence. A same-day edit of that file was refused by command review, because the file also documents the force-push prohibition and the review treats a rewrite of the file as that prohibition. Until that sentence is updated, follow this section.

DORA's trunk-based capability, retrieved 2026-11-05 from <https://dora.dev/capabilities/trunk-based-development/>: higher delivery performance correlates with **three or fewer active branches**, **merging to trunk at least once a day**, and **no code freeze and no integration phase**. The same page: branches in trunk-based development "typically last no more than a few hours," while a feature branch that lives for days or weeks is a different, slower pattern. Fowler, retrieved the same day from <https://martinfowler.com/articles/branching-patterns.html>: "you should never have more than a day's work sitting unintegrated." *Software Engineering at Google*, chapter 16, <https://abseil.io/resources/swe-book/html/ch16.html>: development branches "should be minimal, or at best be very short lived."

Unfinished work hides behind a flag on the default branch. A long-lived branch is reserved for a real multi-version release line, and that line is a snapshot plus cherry-picks, not a second trunk (Google's Piper paper, <https://cacm.acm.org/research/why-google-stores-billions-of-lines-of-code-in-a-single-repository/>).

An unshared agent branch may rebase onto current `origin/main`. A branch anyone else has fetched is updated by merging the base in (GitHub's **Update branch**), not by rewriting it.

## 2. Classify the tip before you touch it

Read `gh pr view <n> --json state,mergeStateStatus,mergeable,headRefOid,baseRefName,statusCheckRollup` and `git status --porcelain` in the worktree that owns the branch. Four states:

| State | How you know | Next action |
|---|---|---|
| **Up to date** | `mergeStateStatus` is `CLEAN` (checks may still be `UNSTABLE`), `headRefOid` is the SHA you reviewed, `git status --porcelain` prints no lines | Eligible to merge once checks and review say so |
| **Behind, clean** | The base has commits the PR lacks (`BEHIND`, or `mergeable` is true and the PR is simply not current), and a merge of the base applies with no conflict | Update the branch from the base. Do not open a conflict editor |
| **Dirty** | `mergeStateStatus` is `DIRTY`, **or** porcelain prints any line, **or** the worktree tip is not `headRefOid` | Do not merge. Remount (section 3). `CLEAN` reports committed trees only |
| **Stacked** | This PR's base is another open PR, not the default branch | Merge the bottom of the stack first (section 4). Leave the top unmerged while the parent is open |

`UNSTABLE` means checks have not passed. That is a red tip, not a dirty one. Fix the check or hand it back. Do not merge it.

## 3. Remount a dirty tip

Resolve the conflict on a fresh tree cut from current `origin/<base>`, not inside the worktree you were already editing.

1. Record `headRefOid` and `git log --oneline origin/<base>..<sha>`.
2. Fetch `origin`.
3. Add a new worktree from `origin/<base>`. That checkout is the remount.
4. Replay only those unique commits (`git rebase --onto <new-base> <old-base> <old-tip>`, or cherry-pick that range).
5. On a conflict, stop. The code owner decides the hunk. The person doing source control does not invent the resolution.
6. The result is a new SHA. A replay that only brings the base in, and does not change the PR's own diff, is an update-branch commit. A resolution that edits a hunk is a new diff and needs review (section 6).

Leave the old worktree alone. Uncommitted files there are not on the PR. A later commit from that tree mixes them into the remount.

## 4. Merge order

**Behind-first is the order when a person or a bot merges by hand.** It is already standing practice for this fleet. The rule:

1. Merge **up to date** PRs whose checks are green on `headRefOid`, shortest dependency first.
2. Then **behind, clean** PRs: update from the base, wait for checks on the **new** SHA, then merge. Do this before merging a PR that conflicts with them.
3. A **dirty** PR waits. Remount it after the clean and behind-clean PRs have landed, so the conflict is against the new trunk once.
4. A **stack** merges from the bottom (the PR whose base is the default branch), then the next PR is restacked. Graphite's manual-merge doc, retrieved 2026-11-05 from <https://graphite.com/docs/merge-stack-prs-github>: "We recommend always merging from the bottom of the stack." Their GitHub-settings doc, <https://graphite.com/docs/github-configuration-guidelines>, says GitHub's own merge queue does not understand stacks and can merge them out of order. Leave an upstack PR out of the queue while its parent is open.
5. After each merge, classify the remaining pull requests again. Re-read `mergeStateStatus` before the next merge. Do not reuse the rollup you read before this merge.

A schema or migration merges before the code that reads the new shape (expand, then contract). A shared file is not a reason to merge a dirty PR first.

**Busy default branch, no hand-merge:** use a merge queue. GitHub, retrieved 2026-11-05 from <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue>: the queue "provides the same benefits as the Require branches to be up to date before merging branch protection, but does not require a pull request author to update their pull request branch," and it merges only after the required checks pass on a group built from the latest base plus earlier queue entries. Hand-merging ahead of that queue lands a result the queue was created to test first. Required workflows must also run on `merge_group`, or the queue waits on a check that never starts.

Where repository auto-merge is off on purpose, this section is the substitute. Do not turn auto-merge on to skip it.

## 5. Required checks

Immediately before the merge call, re-read the pull request. Merge only when `state` is `OPEN`, `headRefOid` is still the SHA whose checks you read, and every **required** check reports `success` on that SHA. A rollup with no checks is a stop. A workflow skipped by a `paths:` or `branches:` filter stays pending and blocks a required check for good. Do not put that filter on a required workflow.

GitHub's troubleshooting page for required status checks, retrieved 2026-11-05 from <https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks>, lists conclusions that satisfy a required check as `success`, `skipped`, and `neutral`. A job that exits neutral when it did not review anything therefore satisfies a required check. Keep advisory reviewers (a bot that finishes neutral when it did not run) **off** the required list. A gate you mean to enforce must exit non-zero on failure.

On a product default branch, require the branch to be up to date before merging (**strict**) when you are not using a merge queue. GitHub's protected-branch doc, retrieved 2026-11-05 from <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches>: strict means the head "must be up to date with the base branch before merging"; loose allows a green branch that lags the base to land, and the combined result can fail afterwards. The merge queue replaces that checkbox. It does not replace the checks.

An admin bypass on a product code branch is not a merge path. This marketplace keeps an admin bypass so docs can land on `main` and so a hung required check can be escaped. That bypass is scoped to this marketplace. Do not copy it onto a product repository, and do not use it to land a red check.

**Content placement.** On RavenPower-Website the ship gate is `check-content-placement.mjs` (Website #953). It covers `account/**` and shell/nav files. Do not rename it. A diff that touches those paths does not merge while that check is failing. The workflow that runs it must not carry a `paths:` filter. Prose Keep / Move / Remove review uses the same table and does not replace the check. The pass itself is `web-design`'s `knowledge/content-placement-page-ia-2026-11.md`.

## 6. Reviews

Turn on **dismiss stale pull request approvals when new commits are pushed**, so a later content push cannot reuse an earlier approval. GitHub's current "Approving a pull request with required reviews" page, retrieved 2026-11-05 from <https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews>: when that setting is on, a **code-modifying** commit dismisses the approval.

An update that only merges the base branch in, and does not change the pull request's own diff, is not a new review. The fleet rule matches that split: a merge-from-base or update-branch commit does not go back through AppSec or a full re-review. A conflict resolution that edits a hunk does. The 2023-06-06 changelog, <https://github.blog/changelog/2023-06-06-security-enhancements-to-required-approvals-on-pull-requests/>, says a changed merge base dismisses approvals, and also says approvals stay in place "in most situations where no new changes are introduced." If a repository's "require approval of the most recent push" setting dismisses a pure update-branch commit, that setting is the wrong knob for a repo that updates branches all day. Dismiss-on-content-change is the knob that matches the threat (a content push after approval).

## 7. Secrets

One store is the source of truth. Every other copy is made from it.

External Secrets Operator, retrieved 2026-11-05 from <https://external-secrets.io/latest/introduction/overview/>: the controller reads the external API and "ensures that the secret values stay in sync." OWASP's GitOps secrets page, <https://owasp.github.io/DevSecOpsGuideline/2-Process/2-6-Deploy/2-6-2-Secrets-in-Kubernetes-and-GitOps/>: prefer a reference in git (ExternalSecret, SecretProviderClass) so the value never lands in the repo.

When the runtime cannot pull (a Workers secret, an Actions secret, a host env var), one operator writes the vault entry first and the runtime entry second, in the same change. Verify that the **name** exists and that its updated time moved. Do not print, log, or diff the value. If the second write fails, the two sides name different generations: finish the runtime write, or put the vault entry back, before calling the change done. A preview environment uses its own secret name. It does not read the production secret. Coding agents do not write either copy.

`gitops-no-plaintext-secrets` still forbids a committed value. This section is the case that rule does not spell out: two live copies, one of them outside git.

## 8. Preview, then production

A UI or API change is reviewed on a running preview built from the CI artifact, not by reading the diff alone. Production is a promotion of that same artifact after the pull request merges to the default branch. Rebuilding production from a laptop, or from a branch that has not merged, is a second build. The bytes that were reviewed are then not the bytes that ship.

The pipeline creates the preview and tears it down on merge or close. A bot shelling out to a production deploy command is not the preview path. Production deploy stays behind the product's prod gate and is out of scope for this checklist.

## 9. Ship checklist

Stop on the first no.

1. The branch is under a day old, or it is a release snapshot.
2. The tip is classified (section 2). Dirty tips are remounted, not merged.
3. Order is behind-first, and stacks merge from the bottom (section 4).
4. Required checks are `success` on the current `headRefOid`. Neutral, skipped, and an empty rollup do not count as a pass for a gate you meant to enforce.
5. Placement, where the product has that gate, is green under its real script name.
6. Review covers the current diff. An update-branch commit with an unchanged diff does not reset it. A hunk edit does.
7. Secrets, if this change adds one, were written to the source store and then to the runtime, and the runtime name was confirmed without printing the value.
8. A UI change cites a preview URL from CI. Leave the production deploy on the product's prod gate.

## See also

- [`../rules/git-workflow.md`](../rules/git-workflow.md) — branch names, commit shape, the four branch-hygiene gates.
- [`github-actions-hardening.md`](github-actions-hardening.md) — `paths:` on a required check, merge queue, CODEOWNERS.
- `devops-cicd` best-practices `design-trunk-based-over-long-lived-branches`, `merge-behind-clean-tips-before-dirty-ones`, `pipeline-required-checks-gate-the-merge`, `secrets-sync-from-one-store-do-not-hand-dual-write`, `deploy-ephemeral-preview-environment-per-pr` — the same rules as this plugin's specialists apply them.
- [`../../grok-bot-delegation/skills/fleet-standing-rules/SKILL.md`](../../grok-bot-delegation/skills/fleet-standing-rules/SKILL.md) — what Website and Master Overseer ops adopt on top of this checklist.
