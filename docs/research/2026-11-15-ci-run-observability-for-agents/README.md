# CI run observability for coding agents (research, 2026-11-15)

How a coding agent tells that a GitHub Actions run is still going, and how it tells that a run has stopped or failed and why. Eight research passes were run. The last one turned up nothing materially new, so the loop stopped ([pass log](passes.md)).

Facts are tagged with the page or the command that produced them and the date they were checked. The agent procedure that came out of this is [`plugins/devops-cicd/knowledge/ci-run-status.md`](../../../plugins/devops-cicd/knowledge/ci-run-status.md). The classifier is `plugins/devops-cicd/scripts/classify_ci_run_state.py`.

This folder does not overlap `docs/research/2026-11-15-runners-for-coding-agents/`, `2026-11-15-mac-mini-m6-runners/`, or `2026-11-15-ci-gates-and-agent-checks/`. Those were being written at the same time. Fleet sizing stays in [`../2026-11-15-self-hosted-runners/`](../2026-11-15-self-hosted-runners/README.md).

## Files

| File | What it covers |
|---|---|
| [01-run-job-step-states.md](01-run-job-step-states.md) | Status versus conclusion, queued / waiting / pending / in_progress, ghosts, cancel 409, conclusions, re-runs and the old merge commit, when logs exist, ETags, rate limits, webhooks versus polling |
| [02-liveness-signals.md](02-liveness-signals.md) | Runner online/busy, step progress, heartbeats, baselines, box sleep, queue alarms when no runner matches |
| [03-failure-classes-and-actions.md](03-failure-classes-and-actions.md) | How to name the failure and the one next action, including the JSON verdict and the rerun guardrails |
| [04-agent-tooling.md](04-agent-tooling.md) | `gh` watch and view, API polling, what Copilot, Claude Code, and Cursor actually see, false "stopped" and false green |
| [sources.md](sources.md) | Every source, grouped |
| [passes.md](passes.md) | The research pass log |

## Top findings

1. **A run has stopped only when `status` is `completed`.** `queued`, `requested`, `pending`, `waiting`, and `in_progress` are alive. `pending` means the concurrency group is full. `waiting` means a deployment protection rule. `requested` means the record exists and has not been queued. Treating any of those as "it stopped" is the false stop. ([01](01-run-job-step-states.md))
2. **A ghost is `status: queued` with zero jobs and a frozen `updated_at`.** Cancel and force-cancel return HTTP 409 "not been queued yet". Delete often returns 403. On 2026-11-16 a full read of RavenPower-Website's queued runs found **43 created on 2026-11-11, every one with `updated_at == created_at` and `jobs.total_count == 0`**. The other 12 queued runs (11 on Nov 15, 1 on Nov 16) all had jobs. Those are a real queue. ([01](01-run-job-step-states.md))
3. **`gh run view --log` hides a finished job until the whole run completes.** The CLI checks the run status and prints "logs will be available when it is complete". The job-log API does not. On run `43785768235`, `GET /actions/jobs/133032915736/logs` returned the line `cursor-gate: missing` while `build` was `in_progress`. Step text for a step that is still running is not on that API. Liveness is `steps[].status` and `started_at`. ([02](02-liveness-signals.md), [04](04-agent-tooling.md))
4. **A job that exits 0 can be the wrong signal.** The same run's `cursor-gate` job concluded `success` while its own log said `missing`, and `build` kept running. The meaningful field is the step output `state`, which the jobs API does not return. ([04](04-agent-tooling.md))
5. **A re-run uses the original SHA and ref, up to 50 times.** It does not pick up a guard or workflow change that landed later. After a runner-guard change, push a new commit. Do not re-run the old attempt. Lost-communication re-runs are only sound when every failed job is that class, and only on attempts 1 and 2. ([03](03-failure-classes-and-actions.md))
6. **Skipped and pending are different kinds of green and red.** A job skipped by `if:` reports success and does not block a required check, so a required job can look green without having run. A workflow skipped by a path filter reports nothing and stays pending, which blocks the pull request. ([01](01-run-job-step-states.md))
7. **304 means "same as last time".** An authorized conditional GET that returns 304 does not spend the primary rate limit. 403 and 429 are transport failures. They are not a dead run. ([01](01-run-job-step-states.md))
8. **`filter=latest` is the current attempt. `filter=all` includes the failed attempt you already re-ran.** An agent that reads `all` and stops at the first `failure` will call a live re-run dead. ([01](01-run-job-step-states.md))
9. **The queue watchdog in RavenPower-Website only sees labels that start with `rpbox`.** Live Commerce CI jobs on 2026-11-16 requested `self-hosted,box,raven-web` and `self-hosted,box,raven-light`. Those do not match. Ghosts have no jobs, so they do not match either. The 43 Nov 11 runs and a stuck light lane are both invisible to that alert. ([02](02-liveness-signals.md))
10. **`gh pr checks` exit 8 means pending, which includes queued and in progress.** `gh run watch` without `--exit-status` returns 0 after a failed run. Copilot does not run Actions until someone approves workflows. Cursor's "Workflow run completed" trigger does not fire for `pull_request` runs. ([04](04-agent-tooling.md))

## What was already in the repo

- [`docs/remote-ci-autotrigger-runbook.md`](../../remote-ci-autotrigger-runbook.md) already names the stuck-queued, zero-job, cancel-409, delete-403 shape, and tells you to run `scripts/check-github-status.sh` first. This research adds the measured 43-run count and the split between those ghosts and a real queue.
- [`../2026-11-15-self-hosted-runners/05-availability-sleep-updates.md`](../2026-11-15-self-hosted-runners/05-availability-sleep-updates.md) already has the 60 second pickup, the 24 hour queue, and sleep causing lost communication. This research uses those timers as the liveness bounds and does not restate the fleet design.
- RavenPower-Website already classifies lost communication and shard timeouts in `factory/lib/rerun.mjs` and opens failure issues from `ci-failure-alert.yml`. The gap is a verdict an agent can read while the run is still going, and a queue alert that matches the labels the jobs actually request.

Searches for the skill names `commerce-ci-failure-triage` and `pipeline-chunk-resume` on `origin/main` at `ee923b3d` (2026-11-16) returned no files. The CI triage that exists is the pipeline-engineer agent, `knowledge/ci-run-status.md` (this change), and the RavenPower factory modules above.
