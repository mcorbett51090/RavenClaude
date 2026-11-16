# 05: Workload shape, isolation, storms, cost, observability

Checked 2026-11-16 unless a row says otherwise. Fleet mechanics (AND-only labels, 60-second pickup, 24-hour queue, 14-day offline deletion) stay in the [2026-11-15 research](../2026-11-15-self-hosted-runners/README.md).

## Agent jobs are not test jobs

| | Test shard | Agent session on a runner |
|---|---|---|
| CPU | Busy the whole job | Mostly idle, waiting on a model API |
| Duration | Minutes, and it scales with cores | Tens of minutes regardless of cores. Website Claude job: 90 minutes allowed. Copilot on Actions: 59 minutes hard |
| What you run out of | CPU and RAM | Slots. An 8-core box waiting on a model is still "one runner busy" |
| Right lane | `lane-slow` for the heavy matrix (3 box runners). `lane-medium` for ordinary tests | `lane-medium` and `host-box` together. Never `lane-slow` (that spends a heavy token on a waiting job). Never `lane-fast` (that is the Yoga) |
| Timeout | The product repo's scale knob | Set `timeout-minutes` on the job. Do not inherit the self-hosted 5-day ceiling |

Hosted jobs are killed at 6 hours. Self-hosted jobs at 5 days ([limits](https://docs.github.com/en/actions/reference/limits)). The installation token on a self-hosted job refreshes for 24 hours, then API calls with the default token fail even if the job is still inside 5 days ([GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token)). A 90-minute Claude job is inside both. A job left uncapped is not.

A step that sleeps in a loop until checks finish holds the slot for the wait. Replace it with a `workflow_run` trigger, or with Cursor's "CI completed" automation ([04](04-cursor-and-codex.md)). `workflow_run` from a fork still needs the `pull_request_target` cautions below.

## Isolation, in the order this fleet can actually use

1. **Do not run the agent on the public repo's self-hosted runners.** There are none, and there should stay none ([secure use](https://docs.github.com/en/actions/reference/security/secure-use)).
2. **Ephemeral or JIT for any runner that will execute agent shell plus a long-lived secret.** GitHub's Copilot page says the same thing. The box's persistent runners are a known compromise: the Claude install lock exists because the home directory is reused. Until a runner is ephemeral, the secret stays off every runner except the pinned box lane, and the workspace cleanup hooks from the 2026-11-15 security note stay in place.
3. **Host firewall, not the product firewall, once Copilot's integrated firewall is off.** Allow the Actions hosts plus the plan-specific Copilot hosts in [02](02-copilot-actions-path.md). Default-drop everything else. The Yoga and the secrets runner are not in that allow-list's audience, because they should not run the agent.
4. **Least privilege on the workflow.** Authorize job with no secret. Long job with the model credential and a narrow tool list. No deploy secrets. No `pull_request_target` checkout of the pull-request head.
5. **Containers, gVisor, Firecracker.** ARC can set a `runtimeClassName` (Kata, or gVisor where the cluster provides it). A Firecracker microVM per job is a stronger boundary and a new control plane. This fleet's 2026-11-15 decision was no Kubernetes. Do not stand up ARC on the box to get gVisor. The practical boundary remains one ephemeral registration, one job, a fresh work directory, and a host firewall. Revisit a microVM only if untrusted fork code must run on this hardware.

Prompt injection is the threat on a private repo the owner triggers. The model reads issue and pull-request text. Copilot strips hidden characters. Claude's action strips a documented set and still says new bypasses will show up. Codex's action page says to sanitize that text and not to treat a read-only sandbox as secret protection. A tool allow-list reduces the blast radius. It does not make the text trusted. `Bash(git:*)` and `Bash(node:*)` on the live Claude job are the wide edges.

## Storms

A storm here is many agent pull requests, or many pushes, each starting the full test matrix on a fleet that fits two or three heavy shards.

| Control | What it does | Use it on |
|---|---|---|
| Copilot's default "approve workflows" | Agent pushes do not start CI | Leave it on. Turning it off is the storm switch |
| Claude app pushes | Do start CI. Required, or checks sit unstarted | Keep. Cap how many Claude jobs run, do not stop the pushes |
| `concurrency` + `cancel-in-progress: true` | A new push cancels the previous run in the group | Test workflows, pull-request events only. Not the Claude job |
| `concurrency` + `cancel-in-progress: false` | One running, one pending; a newer pending run replaces the older pending run | The Claude job, per issue, as it is today |
| `queue: max` | Up to 100 pending runs, FIFO. Cannot be combined with `cancel-in-progress: true` ([concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)). The `queue` key is documented as not available on GitHub Enterprise Server | Do not use it here. A queue of 100 agent jobs will sit until the 24-hour queue limit |
| Path filters | Skip a workflow when the diff does not touch its paths | Test workflows. They do nothing for `issue_comment` |
| Merge queue `build concurrency` | Caps simultaneous `merge_group` builds, 1 to 100 | Only if a merge queue is turned on. Set it to 1 or 2 so the queue does not multiply the matrix. Workflows must also listen for `merge_group` or required checks never report |
| Event rate | 1500 workflow-triggering events per 10 seconds per repository, then events are dropped. 500 workflow runs queued per 10 seconds | A bug that comments in a loop can hit this. The authorize job's bot exclusion is what keeps the Claude workflow from retriggering on its own replies |

`commerce-ci.yml` does not contain `concurrency` (code search, default branch, 2026-11-16). Every new push, including a Claude app push, starts another matrix beside the one already running.

Other ceilings from the same limits page: 256 jobs in one matrix, 50 re-runs of one workflow run, 1500 cache downloads per minute, 200 cache uploads per minute. A re-run button on a failed agent pull request is cheap to click and expensive on the box. Fifty is the hard stop.

## Cost

| Meter | Rate, retrieved 2026-11-16 | For this factory |
|---|---|---|
| Self-hosted execution | Still described as free in the 2026-11-15 research. The `$0.002`/min private-repo fee was postponed with no new date. Not re-fetched this session | The scarce thing is slots, not minutes |
| Standard Linux 2-core | `$0.006`/min ([Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)) | A 59-minute Copilot Actions session on `ubuntu-latest` is about `$0.35` of the shared entitlement. This account's rule is not to use hosted runners for Website |
| Larger runners | See [02](02-copilot-actions-path.md) | Unavailable on a user account |
| Cloud sandbox | Per-second rates in [02](02-copilot-actions-path.md). Machine size unpublished. Billing starts sometime in November 2026 | Does not use the fleet. Confirm the entitlement has room before relying on it. This session did not open the account's billing page |
| Model tokens | Separate from runner minutes. Claude docs: API tokens, or the subscription if the OAuth token is used | A bigger runner does not reduce token cost. It only frees the slot sooner if the agent compiles locally |

Moving an agent job from the box to an 8-core hosted runner does not pay for itself. The job is waiting on the network. The 8-core box is the right size. The mistake is letting that wait occupy a `lane-slow` token or the Yoga.

## Observability

This is a user account. Organization Actions Insights (usage and performance metrics, including queue time by runner label) do not apply. What does:

| Signal | Where |
|---|---|
| Queued versus running | The repository Actions tab, or `gh run list`. A Claude job queued for more than a few minutes means both agent slots are busy or the label matches nobody |
| Why a run was skipped | The authorize job's notice. A skip is a successful run that did not take the long slot |
| Session transcript | Copilot session logs, linked from the agent's commit message. Claude's workflow log. Leave full output off |
| Runner process left behind | `_diag` on the box, plus the job-completed hook from the 2026-11-15 note. A cancelled Claude job does not restore git config |
| Sandbox dollars | The account billing page, once November sandbox billing is actually charging. The start day is not in the changelog |
| Lost communication | The existing rerun-once workflow. An agent job killed mid-push needs a person, not a blind rerun. Do not point that rerun at the Claude workflow |

Queue time is the number that says the fleet is too small for the agent load. CPU idle during an agent job is normal and is not a reason to add runners.
