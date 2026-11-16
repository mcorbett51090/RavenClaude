# 06 — Recommendations for this factory

Checked 2026-11-16. The factory posts one commit status on the pull request head. A light job waits for it. On success, the heavy jobs skip and the aggregate job treats those skips as passes. The ruleset is what makes that status a merge gate. The private product guide has the live ruleset reading and the numbered GO list. This page is the pattern those changes implement.

## Keep

- One aggregate job, always scheduled, that knows which skips are allowed. The heavy jobs stay off the required list. A skipped required name would be a pass, so requiring them would make the skip itself satisfy the gate.
- The wait lives in a job with no checkout, before any secret. A missing status after a short wait runs the suite. A failure skips the heavy jobs and fails the aggregate. The default branch never takes the shortcut.
- Concurrency is per pull request, and cancel-in-progress is only for `pull_request`.
- Change detection stays inside the workflow. The pull-request trigger of the required workflow has no `paths:`.
- Browser jobs stay on a runner even when the agent passed, until they are explicitly in the agent's command list and in the required checks.

## Change

1. **The status writer is a GitHub App, and the ruleset names that App.** A user token has no `integration_id`. "Any source" means any writer of commit statuses can satisfy the only required check, including a workflow in the pull request. The App key stays in the worker. The agent's VM token must get a 403 on the statuses API. That call is the control, not a line in the prompt.

2. **The model's paragraph is not the result.** Accept a pass only from recorded tool exit codes for the named commands, on the named SHAs. A pass token that shows up inside command output is an error, and the runner decides. If the API does not expose those exit codes, the agent run stays pending and the aggregate job on a runner posts the result.

3. **Strict mode, not a merge queue, until the poster knows about queue SHAs.** Strict makes a moved base produce a new head with no status, so the suite runs again. A merge queue waits on `merge_group` and on a status on the queue's commit. The bridge posts on the pull request head today. Turning the queue on without both of those stalls every merge. Do one, not both, in the first change.

4. **Sample the agent.** Heads that touch workflows, the bridge, authentication, payments, or production flags stay pending until a runner's aggregate job passes. One in ten of the other agent passes is re-run the same way. A mismatch fails and alerts. The default branch always uses the runner.

5. **Say the skip rule in the workflow comment the way GitHub says it.** A job skipped by `if:` reports Success. The comment that a skipped job fails a required check is the opposite of the troubleshooting page. The protection is "those job names are not required," plus the aggregate script. Do not add the heavy job names back onto the ruleset.

6. **Before browser checks block a release, require the aggregate job from app 15368** (or the browser job's own name, pinned to that app). An agent pass that was told to skip the browsers must not be the only green.

7. **Replace workflow byte-equality with the contract in [05](05-review-and-update.md).** Keep byte equality for the inlined runner-name guard only.

8. **Pin action code.** Adopt `actions.lock` if this repository's plan includes the preview. Otherwise SHA-pin `uses:` and keep the Dependabot `github-actions` updates. Add `actionlint` and `zizmor` on a job the aggregate already requires, with no trigger-level path filter.

9. **Production deploys name an environment with a branch policy, and only when a deploy is about to happen.** Required reviewers on a private repository need Enterprise. Confirm the plan before adding them. A green job that recorded a production deployment and then skipped the upload is a standing bug in the environments panel. Fix it as a workflow change under its own GO.

10. **Run [runbook.md](runbook.md) quarterly.** The first run is the inventory of the one required context, its source app, and every job the aggregate treats as optional.

Signed commits stay off until every pusher, including the agent and the factory, signs. An unsigned head blocks squash merge even when GitHub would sign the squash commit.

CODEOWNERS for workflows and the bridge is worth turning on when an agent can push. With zero required approvals, code-owner review and the extra Copilot approval both do nothing. Pick a count on purpose. `require_last_push_approval` is what stops the last pusher approving their own push.
