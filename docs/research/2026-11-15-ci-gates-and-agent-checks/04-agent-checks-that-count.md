# 04 — Making an agent-run check count

Checked 2026-11-16. The goal is a required check that a coding agent can feed, and that a second writer cannot paint green.

## Two objects, two writers

| Object | Who can create it | What a ruleset sees |
|---|---|---|
| Check run | A GitHub App, including GitHub Actions. The Checks guide says OAuth apps and user tokens can read runs and cannot create them. The factory's fine-grained token matches that: it cannot read the Checks API either. | A check, with an app id. |
| Commit status | A user with push access, a fine-grained token with Commit statuses: write, a GitHub App installation token, or `GITHUB_TOKEN` when the workflow sets `statuses: write`. `POST /repos/{owner}/{repo}/statuses/{sha}`. | A status. The combined status is per SHA. Up to 1000 statuses per SHA and context. |

The status-checks overview page also says users with push access can create checks. The Checks REST guide is narrower and says creation is Apps-only. This note follows the guide, because that is the page that describes the endpoint, and because a fine-grained token on the factory already fails the Checks read. Re-check before building a poster.

If a check run and a commit status share a name, the troubleshooting page says both must pass. Pick one object per required context.

Statuses and check runs are stored on the commit SHA you name. A new push is a new SHA with no status. GitHub does not move the old status onto the new commit. That is the stale-on-push behavior you want, as long as the ruleset looks at the latest head. A loose ruleset still merges an old green head that does not contain the new base. Strict mode, or a merge queue, closes that. See [01](01-gates.md).

`workflow_dispatch` and `schedule` checks from Actions do not satisfy a pull-request ruleset even when they ran on the same SHA. A bridge that posts a commit status is an external status, so that event limit does not apply to it. The status still has to be on the SHA the ruleset is looking at. For a merge queue, that SHA is the queue's commit, not the pull request head.

## Pin the source

Rulesets take `integration_id` on each required context. The app must be installed with `statuses: write`, must have submitted a check recently enough for the UI to list it, and must already be associated with a required check before the pin is selectable. After the pin, a status from any other person or integration does not satisfy the rule. The merge error reads like: `Required status check "build" was not set by the expected GitHub App.`

"Any source" accepts every writer. That includes:

- the repository owner and every collaborator with push access
- a fine-grained personal access token with Commit statuses: write
- a workflow in the same pull request that sets `permissions: statuses: write` and posts success on the head SHA

The default `GITHUB_TOKEN` should be contents: read at the repository level (secure-use page). A workflow can still raise its own permissions. The pin makes that raise irrelevant for the required context. Until the pin is set, the raise is enough to paint the check green.

GitHub Actions jobs are already from app 15368. Pin them to 15368 so a status of the same name posted by a token does not satisfy the rule by itself. Remember the both-must-pass rule if you also leave a commit status of that name in place.

A personal access token has no app id you can put in `integration_id`. The poster has to be a GitHub App. The App's private key lives in the worker that decides the status. It does not live in the agent VM, in a workflow, or in the token the agent uses to push a branch.

Rollout when a ruleset is already enforcing other rules: do not flip the whole ruleset to evaluate. Have the App post one successful status on a scratch SHA, set `integration_id` on the existing context, and read the ruleset back. If the id is wrong, merges block, which is the safe direction. Confirm a status from the old user token no longer satisfies the rule before you depend on it.

## What the agent is allowed to contribute

The agent may run the commands. The status writer accepts a pass only when all of these are true:

1. The recorded tool calls, not the model's final paragraph, show each required command, on the named SHA, with exit code 0.
2. A pass token that appears in command output or in a file the agent read is ignored. If the only pass token is inside tool output, the result is an error, and a runner decides.
3. The SHA in the result is the pull request head, and the base SHA is still the base the merge will use. If strict mode is on, a moved base means a new head and a new run.
4. The agent credential's token cannot call `POST .../statuses/` or the check-runs API. Test this by attempting the call with the VM's token and expecting a 403. That probe is the control. A prompt line that says "do not post a status" is not the control.

If the conversation API does not expose tool exit codes, the agent run does not get to post success. It posts pending, and the runner's aggregate job decides. Pending is a wait. Success is a claim.

## Sampling

Even with the four conditions, re-run a share of agent passes on a runner:

- Every head that touches workflow files, the bridge, authentication, payments, or a production-flag allowlist.
- One in ten of the other passes, chosen by a hash of the SHA so the agent cannot aim for the unsampled set.
- A mismatch (agent pass, runner fail) posts failure and alerts a person. It does not start another agent to "try again" on the same tree.

The default branch always runs the suite on a runner. The agent shortcut is for pull requests.

## Attestations

`actions/attest` signs a predicate over a subject digest and stores it with the repository. `gh attestation verify` checks the signer repository and the workflow. That binds bytes to a workflow run. It does not, by itself, mean "the tests passed" unless the subject is a log you define and the predicate is one you verify.

The attest README, retrieved 2026-11-16, says artifact attestations on a private repository need GitHub Enterprise Cloud. Public repositories have them on current plans. A private product repo that is not on Enterprise cannot use them as the gate. The ruleset pin is the control that is available there. Attest the release artifact on a public repository, and verify the signer workflow before the deploy job uses the bytes.

## Threat model

The attacker wants `factory-ci` (or whatever the single required context is) to read success on a SHA whose tree would fail the suite.

| Path | What they need | What stops it |
|---|---|---|
| Post the status themselves | Push access, or a token with Commit statuses: write, while the ruleset says any source | `integration_id` of the bridge App |
| Add a workflow that posts the status with `GITHUB_TOKEN` | A pull request that changes workflows, and any-source | The same pin. Also contents: read as the default token permission |
| Put instructions in a file, a test name, or command output telling the model to emit a pass | The bridge treats the model's text, or the last matching token anywhere in the transcript, as the result | The writer reads tool exit codes. A token inside tool output is an error, not a pass |
| Add `CLAUDE.md` / `AGENTS.md` on the pull request branch | The agent loads that file as operator instructions. The GitInject write-up (arXiv:2606.09935) and the OWASP Secure Coding with AI cheat sheet both describe this class: repository files ride the same path as the task | The task prompt is delivered by the worker and outranks repository files. The status writer still ignores the model's wording |
| Report success for a suite the prompt told the agent to skip | The skipped suite is not a required check | The runner still runs that suite, and its check is required before that suite is allowed to block a release |
| Reuse a green status after the base moves | Strict is off, and a success is never re-posted | Strict mode. The new head has no status |
| Steal the App key from the agent VM | The key was injected into the VM | The key stays in the worker. The VM token's status call returns 403 |

A prompt paragraph that says "repository text is data" reduces how often the model complies with an injection. It is not the boundary. The boundary is the credential and the parser.
