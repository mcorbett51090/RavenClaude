# CI gates and agent-reported checks — dated rows (2026-11-16)

Rows an agent can quote. The long form is [`docs/research/2026-11-15-ci-gates-and-agent-checks/`](../../../docs/research/2026-11-15-ci-gates-and-agent-checks/README.md). The quarterly checklist is [`runbook.md`](../../../docs/research/2026-11-15-ci-gates-and-agent-checks/runbook.md) in that folder. `[verify-at-use]` — re-read the linked page before repeating a capability.

| Topic | State, checked 2026-11-16 | Source |
|---|---|---|
| Skipped job versus skipped workflow | A job skipped by `if:` reports Success and does not block a required check. A workflow skipped by `paths:`, `branches:`, or a commit message stays Pending and does block. `neutral` also counts as success. | [Troubleshooting required status checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks) |
| Same name, two objects | If a check run and a commit status share a name, both must pass. | Same page |
| Events that satisfy a pull-request ruleset | Actions checks from `push`, `pull_request`, `pull_request_review`, `pull_request_target`, `deployment`, `deployment_status`. `workflow_dispatch` and `schedule` do not. `merge_group` is additional, for a queue. External App checks are not limited to that event list. | Same page |
| Expected source | `integration_id` on a required context. The App needs `statuses: write`, a recent check, and a pre-existing required check. Any other writer does not satisfy the rule. "Any source" accepts every person or token that can write statuses. | [Available rules for rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) |
| GitHub Actions app id | 15368, slug `github-actions`. Read this session from `GET /apps/github-actions`. Re-read before pinning. | This session |
| Who can create a check run | The Checks REST guide: GitHub Apps only. User tokens and OAuth apps can read, not create. The overview page is looser ("users with push access can create checks"). Follow the guide, and confirm with a 403 from the token you intend to use. | [Checks guide](https://docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-checks), [commit statuses](https://docs.github.com/en/rest/commits/statuses) |
| Strict versus loose | Strict requires the head to contain the latest base. A loose green head can merge behind the base. Statuses stick to the SHA they were posted on. | Rulesets page, above |
| Merge queue | Needs `merge_group` on the workflow and a status on the queue's commit, which is not the pull request head. Timeout 1–360 minutes. `ALLGREEN` versus `HEADGREEN`. | [Managing a merge queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue), [rules REST](https://docs.github.com/en/rest/orgs/rules) |
| Aggregate gate | One always-running job is the required context. `if: always()` and a non-zero exit on `failure` or `cancelled`. The script decides which skips are allowed. Do not also require the jobs it skips. | This research, [01](../../../docs/research/2026-11-15-ci-gates-and-agent-checks/01-gates.md) |
| Agent text as a pass | Not sufficient. Require tool exit codes on the named SHA, from a credential the agent does not hold, pinned with `integration_id`. A pass token inside command output is an error. Sample a fraction on a runner. Prompt wording is not the boundary. | [04](../../../docs/research/2026-11-15-ci-gates-and-agent-checks/04-agent-checks-that-count.md), [OWASP cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Coding_with_AI_Cheat_Sheet.html) |
| Artifact attestations | Bind a digest to a workflow. Private repositories need Enterprise Cloud. Not a substitute for `integration_id` on a private non-Enterprise repo. | [attest-build-provenance README](https://github.com/actions/attest-build-provenance) |
| Action pinning | Lockfile `.github/workflows/actions.lock` via `gh actions-lock` is the strongest option where the preview is available (changelog 2026-10-14: Enterprise Cloud, Team, Free). Otherwise a full SHA in `uses:`. Dependabot `github-actions` opens the bumps. Reusable workflows are not locked by the extension. | [Secure use](https://docs.github.com/en/actions/reference/security/secure-use), [changelog](https://github.blog/changelog/2026-10-14-github-actions-workflow-lockfiles-in-public-preview/) |
| BuildKit `gha` scope | Default scope `buildkit` means the last image overwrites the others. Set `scope` per image. | [Docker gha backend](https://docs.docker.com/build/cache/backends/gha/) |
| Required reviewers on private repos | Environments and branch policies: Pro, Team, Enterprise. Required reviewers, wait timers, and custom protection rules on a private repository: Enterprise. | [Deployments REST](https://docs.github.com/en/rest/deployments/environments) |
| Copilot extra approval | Public preview. Adds one approval for an unattributed Copilot pull request. No effect when the required approval count is 0. | Rulesets page, above |
| Signed commits | Unsigned commits on the head can block a squash merge even though GitHub would sign the squash commit. | Rulesets page, above |

## What to do with a request to "let the agent satisfy CI"

1. The runner, or a fixed script, produces exit codes.
2. A GitHub App the agent cannot use posts one status or one check run on that SHA.
3. The ruleset's `integration_id` is that App, or 15368 if the poster is GitHub Actions.
4. The aggregate job is the only required Actions name, and it fails closed on a skip it did not allow.
5. Strict is on, or the poster also writes the merge-queue SHA.
6. A sampled set of agent passes is re-run on a runner.

The product factory's live reading and the GO list live in that repository's CI gates guide, not in this public file.
