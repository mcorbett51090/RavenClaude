# CI run status — is it running, stalled, or finished?

Use this before you say a GitHub Actions run stopped, failed, or passed. The machine-readable form is `scripts/classify_ci_run_state.py` in this plugin. The sourced research is [`docs/research/2026-11-15-ci-run-observability-for-agents/`](../../../docs/research/2026-11-15-ci-run-observability-for-agents/README.md).

A run is **alive** while its status is `queued`, `in_progress`, `pending`, `waiting`, or `requested`. It has **stopped** only when status is `completed`. A queue is not a failure. A green job conclusion is not proof the suite ran.

## Read these, in this order

1. **The run.** `GET /repos/{owner}/{repo}/actions/runs/{id}` — `status`, `conclusion`, `run_attempt`, `head_sha`, `created_at`, `updated_at`. If `head_sha` is not the commit you care about, this run is not the verdict for that commit. A re-run keeps the original `GITHUB_SHA` and `GITHUB_REF` ([Re-running workflows and jobs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs), retrieved 2026-11-16).
2. **The jobs, the whole page.** `GET .../actions/runs/{id}/jobs?per_page=100`. Compare `total_count` to how many jobs you received. A short page is not an empty run. `filter=latest` (the default) is the current attempt. `filter=all` also returns older attempts, so a failed attempt sitting next to a live re-run is not "the run failed" ([workflow jobs](https://docs.github.com/en/rest/actions/workflow-jobs), retrieved 2026-11-16).
3. **The current step, while a job is `in_progress`.** Each step has `status`, `started_at`, and `completed_at`. That is the live signal. Do not decide from log text yet.
4. **Annotations, then the log, after a job completes.** `GET /repos/{owner}/{repo}/check-runs/{job_id}/annotations`. Then `GET .../actions/jobs/{job_id}/logs`. On 2026-11-16 the job-log API returned the finished `cursor-gate` log for RavenPower-Website run `43785768235` while the run was still `in_progress`. `gh run view --log` refused with "run is still in progress; logs will be available when it is complete" (`cli/cli` `pkg/cmd/run/view/view.go` checks the run status first). Use the job-log API for a finished job. Do not expect log text for a step that is still running.
5. **Runners, only for a queue or a suspected sleep.** `GET /repos/{owner}/{repo}/actions/runners`. `status` is `online` or `offline`. `busy` is separate. A job runs on a runner that has **every** label it requested. No match means the job waits (up to 24 hours, then it is cancelled) ([Actions limits](https://docs.github.com/en/actions/reference/limits), retrieved 2026-11-16).

If the API returns **304**, the body you already have is still current. An authorized 304 does not spend the primary rate limit ([Best practices for using the REST API](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api), retrieved 2026-11-16). If it returns **403 or 429**, that is a rate limit or a token problem. Back off (`retry-after`, or `x-ratelimit-reset` when remaining is 0). It is not a failed run.

## Decide

| What you see | Phase | Alive | Do this |
|---|---|---|---|
| Status `queued` / `requested`, **no jobs**, `updated_at` still equal to `created_at`, older than 10 minutes | `ghost` | no | `wait_for_github`. Do not cancel in a loop. Cancel and force-cancel answer **409** "not been queued yet"; delete often answers **403**. |
| Same shape, younger than 10 minutes | `queued` | yes | `wait`. Jobs may still be provisioning. |
| Status `pending` | `waiting` | yes | `wait`. The concurrency group is full. |
| Status `waiting` | `waiting` | yes | `wait`, or a person satisfies the protection rule. |
| Jobs `queued`, a matching runner is `online` | `queued` | yes | `wait`. Busy runners with a short queue are normal. |
| Jobs `queued` past 15 minutes, no runner has every label | `queued` | yes | `relabel` or register a runner. The run has not stopped. |
| Jobs `queued` past 15 minutes, every matching runner is `offline` | `queued` | yes | `restart_runner`. |
| A step is `in_progress` inside its baseline | `running` | yes | `wait`. |
| Matching runners just went `offline`, step age inside 10 minutes | `running` | yes | `wait`. A box that sleeps looks like this before GitHub fails the job. |
| One step has run longer than twice its baseline | `stalled` | no | `escalate`. Do not re-run a hang on the first look. |
| Run `completed`, `head_sha` is not the current head | `stale` | no | `watch_head`. Do not treat this conclusion as the new commit. |
| `conclusion: success` and a required job is `skipped` | `false_green` | no | Do not merge on "green" alone. Confirm the suite ran. |
| `conclusion: cancelled` and a newer run exists for the same ref | `failed` | no | `watch_successor`. Do not re-run the old one. |
| `conclusion: failure` and every failed job is a runner drop (below) | `failed` | no | `rerun_failed` only inside the caps below. |
| `conclusion: failure` and the log says the runner guard refused | `failed` | no | `do_not_rerun`. Fix the guard or the labels. |
| `conclusion: failure` and the failure is a test or assertion | `failed` | no | `fix_test`. |
| Failed jobs are more than one class | `failed` | no | `escalate`. Do not re-run. |
| `conclusion: startup_failure` | `failed` | no | `rerun_failed` once, unless the guard changed. |
| `conclusion: timed_out` on the run or the job | `failed` | no | `rerun_failed` within the cap, or raise the baseline if the lane is known-slow. |

## Failure classes

Match the **first** row that fits. Read annotations before the log. A log that 404s is "unreadable", not "no such phrase".

| Class | Evidence | Action | Cap |
|---|---|---|---|
| `infra_ghost` | `status=queued`, zero jobs, `updated_at` frozen | `wait_for_github` | never re-run |
| `concurrency_pending` | status `pending` | `wait` | — |
| `deployment_protection` | status `waiting` | `wait` | — |
| `queue_no_match` | queued, no runner has all labels, past the alarm | `relabel` | — |
| `box_offline` | queued or in progress, every matching runner `offline` | `wait` inside the grace, else `restart_runner` | — |
| `hang` | one step past twice its expected minutes | `escalate` | — |
| `runner_lost` | annotation or log matches `lost communication with the server` or `was not acquired by Runner`, or the job has **no steps** | `rerun_failed` | attempts 1 and 2 |
| `runner_shutdown` | `The runner has received a shutdown signal` or exit 143 | `rerun_failed` | attempts 1 and 2 |
| `guard_rejection` | `runner guard: refusing` | `do_not_rerun` | never |
| `timeout` | conclusion `timed_out`, and not a shard-only flake | `rerun_failed` | attempts 1 and 2 |
| `flake_shard` | every non-gate failure is a cancelled or timed-out matrix shard (name ending in `(...)`) | `rerun_failed` | attempt 1 only |
| `test` | assertion, test runner, or a failure that is not one of the rows above | `fix_test` | never |
| `auth` | authentication or token text | `escalate` | never |
| `cancelled_superseded` | conclusion `cancelled` and a newer run id | `watch_successor` | never |
| `startup_failure` | run conclusion `startup_failure` | `rerun_failed` | attempt 1 |
| `skipped_required` | success, but a required job concluded `skipped` | do not treat as a pass of the suite | never |
| `unproven` | failure, and annotations and the log could not be read | `escalate` | never |
| `mixed` | failed jobs fall into more than one class | `escalate` | never |
| `transport` | 304 is not this; 403, 429, a truncated page, or `gh` missing is | `retry_later` | — |

Gate jobs named `ci-gate` and `test` are left out of the "every failure is the same class" check. They go red because something they need failed. A run whose only other failure is a timed-out shard is `flake_shard`.

## Guardrails

- **Re-run uses the old commit.** It does not pick up a guard change, a new workflow file, or a newer main. If the runner guard changed after this SHA, the action is `update_branch` (a new commit), not `rerun_failed`.
- **Attempt caps above are the maximum.** A re-run still counts toward whatever stop rule the repo already has. It is not a reset.
- **GitHub allows 50 re-runs of one run** (full and partial together). Past that, the check suite fails with an annotation ([changelog, 2026-04-10](https://github.blog/changelog/2026-04-10-actions-workflows-are-limited-to-50-reruns/)). Do not approach that number.
- **Do not cancel ghosts in a loop.** The 409 is the diagnosis. Check GitHub's status (`scripts/check-github-status.sh` in this marketplace) and wait.
- **A skipped job is not "the suite ran".** GitHub's status-check docs say a skipped job reports success and does not block a required check ([Status checks](https://docs.github.com/en/pull-requests/reference/status-checks), retrieved 2026-11-16). A workflow skipped by a path filter reports nothing and stays pending, which **does** block. Read the conclusion. Do not collapse those two.
- **Job conclusion `success` can be a script that exited 0.** On RavenPower-Website run `43785768235` (2026-11-16), `cursor-gate` concluded success while its log said `cursor-gate: missing`, and `build` was `in_progress`. Pass `outputs.state` into the snapshot when you have it.

## JSON verdict

`classify()` returns this object. `--repo` and `--run-id` build the snapshot with `gh` and print the same object. Exit 0 means the JSON was printed, including when the run failed. Exit 2 means the snapshot could not be read.

```json
{
  "phase": "running",
  "alive": true,
  "failure_class": null,
  "action": "wait",
  "rerun_allowed": false,
  "why": "A job is in progress.",
  "guardrails": [],
  "evidence": {}
}
```

`phase` is one of `running`, `queued`, `waiting`, `stalled`, `ghost`, `failed`, `succeeded`, `false_green`, `stale`, `unknown`.

`action` is one of `wait`, `wait_for_github`, `retry_later`, `rerun_failed`, `update_branch`, `fix_test`, `restart_runner`, `relabel`, `escalate`, `watch_successor`, `watch_head`, `do_not_rerun`, `none`.

The script does not post a re-run. `rerun_allowed: true` means a person or a repo workflow may re-run failed jobs. It is not an instruction to do it twice.

```shell
python3 plugins/devops-cicd/scripts/classify_ci_run_state.py --self-test
python3 plugins/devops-cicd/scripts/classify_ci_run_state.py \
  --repo OWNER/REPO --run-id RUN_ID
```

Optional snapshot fields: `expected_minutes` (job name to minutes), `required_jobs`, `expected_head_sha`, `guard_changed`, `successor_run_id`, `runners`, `ghost_minutes` (10), `queue_alarm_minutes` (15), `stall_factor` (2), `sleep_grace_minutes` (10). Omit `runners` when you did not list them. An empty list means the API returned no runners.

## Polling

Prefer `workflow_job` webhooks (`queued`, `in_progress`, `completed`) when you have them. `workflow_run` `completed` only tells you the run ended. Poll the jobs endpoint as the backstop: honor `x-poll-interval` if it is present, send `If-None-Match`, and treat 304 as "same as last time". `gh pr checks --watch` exits **8** while checks are pending ([gh pr checks](https://cli.github.com/manual/gh_pr_checks)). Pending includes queued and in progress. `gh run watch` without `--exit-status` returns 0 when the watch itself finishes, including after a failed run. Pass `--exit-status` when a failed run should fail the command. `gh run watch` has no separate exit code for "still pending" (the CLI source marks that as a TODO).
