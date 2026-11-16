# 01 — Gates

Checked 2026-11-16 against docs.github.com. A gate is a platform rule that refuses the merge. A workflow that goes red and can still be merged is a report, not a gate.

## Rulesets and branch protection

Both can require status checks, reviews, and signed commits. Rulesets are the newer surface and can stack: several rulesets apply at once, each with its own enforcement (`active`, `evaluate`, or `disabled`). Evaluate mode runs the checks and records the result without blocking. That is the way to watch a new rule before it binds, but it is a property of the whole ruleset, not of one check. Turning an existing blocking ruleset to evaluate drops every rule in it.

Bypass is an explicit actor list (`Integration`, `OrganizationAdmin`, `RepositoryRole`, `Team`, `DeployKey`, `User`). An empty list means the ruleset applies to everyone, including admins. A marketplace that keeps an admin bypass so docs can land on the default branch has scoped that bypass to itself. Do not copy it onto a product code branch.

`current_user_can_bypass` on the ruleset API is the reading of whether the caller can ignore the ruleset. Read it back after a change. Do not assume the owner is exempt.

## What satisfies a required check

From [Troubleshooting required status checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks), retrieved 2026-11-16:

| What happened | What the merge box sees | Blocks the merge? |
|---|---|---|
| Workflow skipped by `paths:`, `branches:`, or a commit message | Pending, no run | Yes |
| Workflow ran on an event the pull request does not evaluate (`workflow_dispatch`, `schedule`, and anything outside the list below) | No check on the pull request | Yes |
| Job skipped by `if:` | Success | No |
| Job skipped because a job it `needs` failed, and the dependent job is the required name | May not block | Often no |
| Check passed on an older SHA | Ignored for this head | Yes |
| Conclusion `neutral` | Treated as success | No |
| A check run and a commit status share one name | Both must pass | Yes, if either fails |

Events whose workflow-job checks are evaluated on a pull request: `push`, `pull_request`, `pull_request_review`, `pull_request_target`, `deployment`, `deployment_status`. External GitHub App checks are not limited to that list. Merge queues need `merge_group` as well.

A required check must also have completed successfully in the repository during the past seven days before it can be selected in the UI. The name has to match exactly. Above the repository (organization rulesets), names are not indexed: type the string.

## The aggregate job

Require one job name. That job:

- has no `paths:` on the workflow that creates it
- uses `if: always()` so a failed or skipped dependency does not skip the gate itself
- exits non-zero when any needed dependency is `failure` or `cancelled`
- decides, in that same script, which `skipped` results are allowed

`if: always()` alone is not enough. A gate that only prints "ok" under `always()` is green over a red suite. `contains(needs.*.result, 'failure')` treats a skip as fine, which is what you want for a docs-only diff and what you do not want when the skipped job was the suite. The script has to know the difference. That is the job the product repo calls `ci-gate`.

Do not also require the names of jobs that this gate skips. A skipped required name is a pass, so requiring both the aggregate and the skipped job lets a skip satisfy the second name.

Do not rename the job, and do not set `name:` on it. The check context is the job id. A rename leaves the old required context Pending forever.

## Strict, loose, and the merge queue

| Setting | What it demands |
|---|---|
| Strict (`strict_required_status_checks_policy: true`) | The head contains the latest base before merge. Updating the branch creates a new SHA, which has no status until CI posts one. |
| Loose (strict false) | A green head that lags the base can merge. The combination can fail after it lands. |
| Merge queue | The queue builds a temporary commit from the latest base plus the pull requests ahead, and requires the checks on that commit. |

A merge queue needs `merge_group` on every workflow that reports a required check. Without it the queue waits for a check that will never be created. The queue's `check_response_timeout_minutes` is 1 to 360; after that a check that has not reported is treated as a failure. Build concurrency limits how many `merge_group.checks_requested` events are in flight. Grouping `ALLGREEN` requires every pull request in the group to pass. `HEADGREEN` requires only the combined head. `HEADGREEN` hides a red individual pull request when the combination happens to pass. Use `ALLGREEN` unless you have a written reason not to.

Do not turn on a queue and keep hand-merging ahead of it. Do not turn on a queue for a status that is posted only on the pull request head SHA. The queue's commit is a different SHA. The poster has to write the status there too, or the queue stalls.

`do_not_enforce_on_create` lets a branch be created when the required check is absent. Leave it false on a product default branch unless branch creation is a real workflow.

## Who may report the check

From [Available rules for rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), retrieved 2026-11-16:

> Any person or integration with write permissions to a repository can set the state of any status check in the repository. When you add a required status check rule, you can select an app as the expected source of status updates. The app must be installed with the `statuses:write` permission, must have recently submitted a check run, and must be associated with a pre-existing required status check in the ruleset. If the status is set by any other person or integration, merging will not be allowed.

The REST field is `integration_id` on each `{context, integration_id}` entry. GitHub Actions is the GitHub App `github-actions`. This session read `GET /apps/github-actions` and got id **15368**. Pin Actions jobs to 15368. Pin a bridge-posted status to the App that posts it, not to "any source".

The UI prerequisite ("recently submitted a check run") can hide an App that has only posted commit statuses. If the App does not appear, have it create one check run, then set `integration_id`. After that, keep a single object per context. A check run and a commit status with the same name must both pass.

"Any source" is the hole. A collaborator, a fine-grained token with Commit statuses: write, or a workflow that sets `permissions: statuses: write` can post `success` on that context for the head SHA. The merge box will show the author's login. Nobody reads it on every pull request. The pin is the control.

## Reviews, CODEOWNERS, signatures

CODEOWNERS is read from `.github/`, the repository root, or `docs/`, in that order, first file found. The last matching pattern wins. Owners need write access. One owner from the line is enough. Requiring code-owner review does nothing until the ruleset sets `require_code_owner_review`. Own the file itself, `.github/workflows/`, and the bridge, or the next pull request can change who must review.

`require_last_push_approval` means the last pusher cannot be the approving review. That is the control when an agent pushes. `require_extra_approval_for_unattributed_changes` (public preview) adds one approval when Copilot opens a pull request under its own identity. The same page says the setting has no effect when the required approval count is zero.

Required signed commits use `verified_signature?`. Rulesets, unlike classic branch protection, check signatures on branch creation only for commits that are not already reachable from another branch. On update, both check the range. An unsigned commit on the head can block a squash merge even though GitHub would sign the squash commit. Do not enable the rule until every pusher signs. A signature proves the key, not the review.

## Deploy gates

Two different gates:

- **Ruleset "require deployments to succeed"** names environments that must have a successful deployment before merge. That is a merge gate.
- **Environment protection** holds a job that sets `environment:` until a wait timer, a required reviewer, or a custom GitHub App protection rule says yes. The job's check conclusion stays `waiting`, then succeeds or fails. A custom App rule needs a deployment object: `deployment: false` on that environment fails the job.

Plan split, from the deployments REST page, retrieved 2026-11-16: environments and deployment branch policies exist on private repositories for Pro, Team, and Enterprise. Required reviewers, wait timers, and custom protection rules on a private repository need Enterprise. On Free, Pro, and Team they are for public repositories. Do not write a required-reviewer step into a private product repo until the plan is confirmed.

A job that names an environment records a deployment even when a later step no-ops. A green "production" deployment that did not deploy is a lie in the environments panel. The branch policy does not fix that. The job should not target the production environment unless it is about to deploy.
