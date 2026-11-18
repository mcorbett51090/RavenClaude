# CI review runbook

Run this quarterly, and again whenever a ruleset or a required workflow changes. Record the date, the ruleset id, and the head SHA you read. Capability facts are `[verify-at-use]`: open the linked doc if the quarter has turned.

The private product repo keeps its own GO list. This checklist is the one any repository can run.

## 1. Inventory the gate

- [ ] `GET /repos/{owner}/{repo}/rulesets` and then each ruleset. Record enforcement, bypass actors, and `current_user_can_bypass` if the API returns it.
- [ ] For every `required_status_checks` entry: context string, `integration_id` or any-source, strict flag, `do_not_enforce_on_create`.
- [ ] Find the workflow job whose id equals that context. Confirm the job has no `name:` key (a name replaces the context).
- [ ] Confirm the workflow's `pull_request` trigger has no `paths:` or `paths-ignore:`. A filter there leaves the check Pending.
- [ ] List the events. A required Actions check needs one of `push`, `pull_request`, `pull_request_review`, `pull_request_target`, `deployment`, `deployment_status`. Add `merge_group` only when a queue is on.
- [ ] If a check run and a commit status share the context name, both must pass. Confirm you meant that.

## 2. The aggregate job

- [ ] Exactly one required Actions context, unless you have a written reason for a second.
- [ ] That job uses `if: always()` and exits non-zero on `failure` and `cancelled`.
- [ ] Its script names which `skipped` dependencies are allowed. A blanket "skip is fine" is a hole when the skipped job was the suite.
- [ ] A job the script can skip is not itself a required context. A skipped required name reports Success.
- [ ] `timeout-minutes` is set. The platform default is 6 hours.
- [ ] The first step does not need a checkout or a secret, if the job's job is to refuse the wrong runner.

## 3. Source of the status

- [ ] Every required context has an `integration_id`. "Any source" is a finding.
- [ ] The App behind that id is installed with `statuses: write`, and its key is not in an agent VM or a workflow.
- [ ] A token the agent holds gets 403 from `POST /repos/{owner}/{repo}/statuses/{sha}`. Record the status code.
- [ ] Actions contexts use app id 15368 (`GET /apps/github-actions`), re-read this quarter.
- [ ] Repository default `GITHUB_TOKEN` permission is contents: read. Any job with `statuses: write` is listed and justified.

## 4. Agent shortcut, if there is one

- [ ] Success is posted from tool exit codes on the named SHA, not from the model's last paragraph.
- [ ] A pass token inside command output is an error, and the runner decides.
- [ ] The default branch does not take the shortcut.
- [ ] Heads that touch workflows, the status writer, authentication, payments, or production flags wait for the runner.
- [ ] A sampled fraction of other passes is re-run on a runner. A mismatch fails and alerts.
- [ ] Strict is on, or a merge queue is on and the poster writes the status on the queue SHA. Not a loose status that is never refreshed when the base moves.
- [ ] Browser or other skipped suites are still required, from the runner, before they are allowed to block a release.

## 5. Speed and cost

- [ ] Concurrency group includes the workflow and the pull request number. `cancel-in-progress` is true only for `pull_request`.
- [ ] Default-branch and `merge_group` runs are not cancelled.
- [ ] Dependency cache keys include the lockfile hash. No constant key.
- [ ] Each BuildKit `gha` cache has its own `scope`.
- [ ] The long job is behind the cheap job in `needs`.
- [ ] Shards are balanced by duration. One shard is not most of the wall clock.
- [ ] Flakes have an owner and a date they leave the required job. Assertion retries are counted, not hidden.

## 6. The workflow code

- [ ] `actionlint` and `zizmor` run on `.github/workflows`. If that job is required, it has no trigger-level path filter.
- [ ] Actions are locked with `actions.lock`, or each `uses:` is a full SHA with the version in a comment.
- [ ] Dependabot `github-actions` is enabled so the pins move in a pull request.
- [ ] Tests pin the contract (job id, permissions, guard-is-first-step, no path filter, aggregate decision). They pin bytes only for a script that is copied into many jobs.
- [ ] CODEOWNERS covers `.github/workflows/`, the CODEOWNERS file, and the status writer. `require_code_owner_review` is on if agent pushes must be reviewed. The required approval count is a deliberate number, not an accidental zero.

## 7. Deploy

- [ ] Production environment has a deployment branch policy.
- [ ] A job names the production environment only on the path that deploys. A skipped upload does not record a production deployment.
- [ ] Required reviewers are available on this plan. On a private repository they need Enterprise. If the plan does not have them, say so in the row instead of documenting a control you do not have.

## 8. Close

Write one paragraph: contexts added, contexts removed, any "any source" still present, the slowest job, the flakiest job, and the date of the next review. Attach it to the inventory. A row with no owner does not survive the review.
