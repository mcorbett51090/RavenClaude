# Run, job, and step states

Retrieved 2026-11-16 from the workflow-runs, workflow-jobs, status-checks, and re-run docs linked in [sources.md](sources.md).

## Two fields, and a filter that mixes them

A workflow run has `status` and, once `status` is `completed`, `conclusion`.

| `status` | What it means for an agent |
|---|---|
| `requested` | The record exists. It has not been queued. Only Actions sets this. Alive. |
| `queued` | Waiting for a runner, or (see ghosts) not actually queued. Alive, until the ghost test says otherwise. |
| `pending` | At the front of the queue and the concurrency limit is full. Alive. |
| `waiting` | A deployment protection rule is not satisfied. Alive. |
| `in_progress` | At least one job has been picked up, or the run has started. Alive. |
| `completed` | Stopped. Read `conclusion`. |

Run `conclusion`: `success`, `failure`, `neutral`, `cancelled`, `skipped`, `timed_out`, `action_required`, `stale`. `null` until completed.

`GET /actions/runs?status=` accepts **either** a status or a conclusion. `status=failure` returns completed failures. `status=queued` returns the queue. An agent that filters on `failure` and sees an empty list has not proved the branch is idle.

Check suites add `startup_failure`. That conclusion means the suite died before the work ran. It is an infrastructure outcome, not a test failure. The job object's own conclusion enum, on the list-jobs endpoint, is narrower: `success`, `failure`, `neutral`, `cancelled`, `skipped`, `timed_out`, `action_required`. Do not wait for a job to say `startup_failure`.

Job `status` uses the same alive set as the run: `queued`, `in_progress`, `completed`, `waiting`, `requested`, `pending`.

A step has `status`, `conclusion`, `number`, `started_at`, `completed_at`. While the job is `in_progress`, the step whose `status` is `in_progress` is the live cursor. `started_at` on that step is how you tell a long step from a stuck one. GitHub adds "Set up job" and "Complete job" around the steps you wrote.

## queued versus waiting versus pending versus in_progress

These get collapsed into "not green" by `gh pr checks` (bucket `pending`, exit code 8). They are not the same action.

- **`queued` with jobs:** a runner that has every requested label has not picked the job up. If a matching runner is online and busy, wait. If none is online, the job still waits. It does not fail at queue time. The queue limit is 24 hours, then the job is cancelled ([Actions limits](https://docs.github.com/en/actions/reference/limits)).
- **`pending`:** concurrency. Another run in the group holds the slot. With `cancel-in-progress` left false, a new queued run replaces the previous **pending** run in that group. It does not cancel the one that is running. That replacement is a cancel of the old pending run, not a failure of the code.
- **`waiting`:** an environment protection rule. A person, a wait timer, or a custom rule has to move. Cancelling it does not fix the workflow.
- **`in_progress`:** a runner has the job. `runner_name` is set. Look at steps, not at the run status alone.
- **`requested`:** too early to call queued. The ghost cancel error uses almost this sentence ("has not been queued yet") while `status` already says `queued`. Read jobs before you trust the word.

`in_progress` on the run can be true while most jobs are still `queued`. On run `43785768235` (2026-11-16) three jobs had completed, three were `in_progress`, and four were `queued`. An agent that stops at the first queued job and says the run died is wrong. An agent that stops at the first completed success and says the run passed is also wrong.

## Ghosts

A ghost is a run row GitHub created and then never gave jobs.

| Field | Ghost | Real queue |
|---|---|---|
| `status` | `queued` | `queued` or `in_progress` |
| `jobs.total_count` | 0 | > 0 |
| `updated_at` | equal to `created_at`, and it stays there | moves when a job is assigned |
| Cancel | HTTP 409 "Cannot cancel a workflow run that has not been queued yet" | accepted |
| Force-cancel | HTTP 409, same sentence | accepted when the run is stuck |
| Delete | HTTP 403 "Could not delete the workflow run" is common | not the first tool |

The 409 contradicts the run's own `status: queued`. That contradiction **is** the diagnosis. Retrying cancel does not move it. `docs/remote-ci-autotrigger-runbook.md` already says to run `scripts/check-github-status.sh` first and wait out an Actions incident. This pass adds a count.

**Measured 2026-11-16 ~01:30 UTC, RavenPower-Website, read-only.** Paginated `GET /repos/mcorbett51090/RavenPower-Website/actions/runs?status=queued&per_page=100` returned 55 runs. 43 were created on 2026-11-11. All 43 had `updated_at == created_at`. A `total_count` read of `/actions/runs/{id}/jobs` for each of the 43 returned 0. The other 12, created 2026-11-15 (11) and 2026-11-16 (1), all had `total_count` greater than 0. Sample of the live one, run `43785768235`: 10 jobs on the first page, several `in_progress` on `box-raven-web-*`. RavenClaude had no queued run created on 2026-11-11.

So "55 queued" was two populations. Calling the Nov 15/16 runs ghosts would have been a false stop. Calling the Nov 11 runs "waiting on the box" would have been a false wait. The jobs count is the split.

A public report the same evening (AnyPS5 issue 18616) describes 180 runs created 20:17–20:53 UTC on 2026-11-11, still queued with zero jobs at 00:00 UTC on Nov 12, cancel 409, delete 403 for a non-admin. The RavenPower 43 sit in that same window (20:23–20:47 UTC). That is consistent with one GitHub-side incident, not with 43 box failures. It does not prove a single incident id; the status page was not re-read for Nov 11 in this session.

The list endpoint can also lie for a moment. Bedrijfsgeheugen issue 4655 recorded `total_count: 0` on the queued list while four known ids were still `queued` on a direct GET. If a list says the queue is empty and a run you are watching was a ghost, GET that id. Do not close the incident from the list alone.

A different empty outcome, from the limits page: more than 500 workflow runs triggered in 10 seconds on one repository are **blocked and not queued**. Those runs never appear. A ghost appears and then never grows jobs. Both are GitHub-side. Neither is a test failure.

## Conclusions that look like each other

| Conclusion | What happened | What an agent should not do |
|---|---|---|
| `failure` | A step exited non-zero, or the runner reported a hard failure. | Re-run before classifying. A test failure and a lost runner share this conclusion. |
| `cancelled` | A person, `cancel-in-progress`, the 24 hour queue, or a shutdown. | Treat it as a test failure. If a newer run exists for the same ref, watch that run. |
| `timed_out` | `timeout-minutes`, or the job hit the platform cap (6 hours hosted, 5 days self-hosted). | Confuse it with exit 143. A step timeout fails the step. A shutdown cancels it. |
| `skipped` | `if:` was false, or `needs` failed and the job had no `always()`. | Treat it as "the suite passed". See below. |
| `neutral` | Completed with no success or failure. Dependent jobs treat it as success. | Put it on the required-check list if "did not run" must block. |
| `stale` | Actions left the check incomplete for more than 14 days. Only GitHub sets this. | Re-run a 14-day-old stale check and expect today's code. The re-run still uses the old SHA. |
| `action_required` | A person has to act on the check. | Cancel the workflow. |
| `startup_failure` | The suite died during startup. | Edit application code. |
| `success` | Every job that was not skipped succeeded, at the run level. | Ignore a skipped required job. |

`if: always()` does not run when the runner process is killed. Shutdown and lost communication skip the cleanup step you were counting on. Anything you need after a runner death has to be written before the step ends (compiler.dev shutdown writeup; RavenPower's re-run path reads annotations first because the log itself can 404, `factory/lib/rerun.mjs`).

## Re-runs and the old commit

From the re-run doc, retrieved 2026-11-16:

- The re-run uses the **original** `GITHUB_SHA` and `GITHUB_REF`, and the **original** actor's privileges.
- Failed-job re-runs also re-run jobs that `needs` them. Jobs that already passed keep their outputs.
- The log archive for a partial re-run contains only the jobs from that attempt. Older attempts are separate downloads.
- Cap: 50 re-runs of one run, full and partial together (changelog 2026-04-10). The 51st fails the check suite with an annotation.
- Window: 30 days after the initial run.

`filter=latest` on the jobs endpoint is the attempt you are looking at. `filter=all` includes the failed attempt. An agent that scans `all` and stops at the first `conclusion: failure` will report a live re-run as failed.

A re-run of a job gets a new machine. A retry inside a step does not (dev.to/kalemi, 2026-11-15). Lost communication wants the new machine. A single flaky assertion wants the test runner's own retry, or a code fix. There is no `retry:` key in workflow syntax.

Because the SHA is frozen, a re-run after someone changes the runner guard still executes the guard from the old commit. The corrective action is a new commit (`update_branch` in the classifier), not `gh run rerun`.

## Logs, ETags, rate limits

- `gh run view --log` returns "run {id} is still in progress; logs will be available when it is complete" when the **run** is not completed, even if the job you named has finished (`cli/cli` `view.go`). Measured on run `43785768235`.
- `GET /actions/jobs/{job_id}/logs` can return that finished job while the run is open. Same measurement: HTTP 200, body contained `cursor-gate: missing`. `gh api` without `--allow-escape-sequences` printed an empty body because the log contains color codes. That empty body is a client filter, not a missing log.
- A job that is still `in_progress` should not be expected to have a downloadable log. Third-party clients report 404 `BlobNotFound` until the job completes (actions-workflow-viz; runner issue 886). This session did not probe an in-progress job's log URL, so 404 is not a measurement here. Use `steps[]` until `conclusion` is set.
- Annotations (`::error`, `::warning`, `::notice`) are written as the step runs and are readable from the check-run annotations endpoint without the log blob. RavenPower's re-run workflow reads those first.
- List and get endpoints return `etag`. Send it back as `If-None-Match`. A **304** means the previous body is still true. An authorized 304 does not count against the primary rate limit. Do not treat 304 as an empty run.
- **403** with `x-ratelimit-remaining: 0`, or **429**, or a secondary-limit message: stop. Honor `retry-after`, otherwise wait until `x-ratelimit-reset`. Keep backing off. This is `transport` in the classifier, action `retry_later`.
- `GET /rate_limit` does not spend the primary limit. It can spend the secondary limit. It is the cheap probe when you suspect the limit rather than the run.

## Webhooks versus polling

| Event | When it fires | What it is good for |
|---|---|---|
| `workflow_job` `queued` | A job is waiting for a runner | Queue age, label match, scale-up. Payload includes the labels. |
| `workflow_job` `in_progress` | A runner took the job | The earliest "it is really running" signal. |
| `workflow_job` `completed` | The job finished, any conclusion | Failure class, from `conclusion` plus annotations. |
| `workflow_run` `requested` / `in_progress` | The run was created or started | "A run exists for this SHA", which the no-checks case in the autotrigger runbook needs. |
| `workflow_run` `completed` | The run finished | Too late to answer "is it still running?". `requested` does not fire on a re-run. |
| `check_run` | Created, completed, rerequested | Same job, as a check. Annotations live here. |

Webhooks are at-least-once and can lag. A missing webhook is not proof the job died. Poll the jobs endpoint as the backstop: on a schedule, conditional GET, and only as often as `x-poll-interval` asks. `gh pr checks --watch` and `gh run watch` are that poll with a UI. They are not a second source of truth.
