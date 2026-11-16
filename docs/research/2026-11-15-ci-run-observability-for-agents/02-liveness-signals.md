# Liveness: the run is going, or it only looks stopped

## Runner online and busy

`GET /repos/{owner}/{repo}/actions/runners` (and the org endpoint, when the runner is org-owned) returns `status` of `online` or `offline` and a separate `busy` boolean. Retrieved from the self-hosted runners REST docs, 2026-11-16.

A job is eligible for a runner only when the runner is online, not busy, and has **every** label in `runs-on`. Labels are AND-only. That matching rule is already in [`../2026-11-15-self-hosted-runners/02-heterogeneous-fleets-and-routing.md`](../2026-11-15-self-hosted-runners/02-heterogeneous-fleets-and-routing.md). The liveness consequence:

- Online and busy, jobs queued: the run is alive. Wait.
- Online and idle, jobs queued: the run is alive, but something is wrong with pickup (the 60 second assignment window in the same research: a runner that does not take an assigned job within 60 seconds has the job requeued).
- Offline, jobs queued: the run is still alive. The corrective action is the machine, after the queue alarm, not a re-run of a job that has not started.
- Offline, a job already `in_progress`: the runner dropped while holding the job. GitHub has not always flipped the conclusion yet. Give it the sleep grace before you call it dead.

`busy: true` with `status: offline` is a stale combination. Trust `status` for "can it take work" and the job's `runner_name` for "who has it".

If the token cannot list runners, leave `runners` out of the snapshot. An empty list means "the API returned none", which the classifier treats as no match. A missing key means "I did not look", and the classifier will not invent an offline box.

## Step progress is the heartbeat GitHub already sends

For an `in_progress` job, poll the jobs endpoint (conditional GET). You learn:

- which step is `in_progress`
- that step's `started_at`
- that earlier steps gained a `completed_at`

Movement of the current step number, or of `completed_at` on the previous step, is progress. A frozen step number plus a `started_at` that keeps aging is a hang, once it passes the baseline below. You do not need a custom heartbeat to see that. You need the baseline so a 20 minute build is not called a hang at minute 5.

The jobs list is paginated. Compare `total_count` with the page you got. The classifier returns `unknown` / `retry_later` when the snapshot says `jobs_truncated`, because a missing page can hide the one `in_progress` job.

## What a custom heartbeat is for

GitHub's step cursor is coarse. One step that runs for 30 minutes with no internal output looks frozen even when it is healthy, and the log blob is not available until the job completes. Three supplements, in the order an agent can actually read them:

1. **Annotations.** `::notice title=progress::shard 40/120` from a workflow command shows up on the check-run annotations API while the step is still running. This is the one API-visible pulse inside a long step. `::error` is the failure form of the same channel.
2. **Check-run output.** A job can PATCH its check run `output.summary` on a timer. That is a write, so it belongs in a workflow change, not in the agent. The agent only reads it.
3. **A progress artifact.** Uploading an artifact mid-job works only at a step boundary. A single long step cannot upload until it finishes. Prefer the annotation.

`GITHUB_STEP_SUMMARY` is written when the step ends. It is a failure summary, not a liveness pulse. JUnit uploaded as an artifact has the same timing. Both are for the "it failed, why" half in [03](03-failure-classes-and-actions.md).

## Baselines

A hang is "longer than this job usually takes", not "longer than a minute".

RavenPower-Website already has a per-job minute cap in `ci-failure-alert.yml` (`JOB_TIMEOUTS`), duplicated in `commerce/scripts/ci-failure-alert.mjs`. Examples from that object, read 2026-11-16: `commerce-ci.yml` `build` 20, `static` 15, `test-shard` 30, `cursor-gate` 25, `ci-gate` 5. The workflow's own `timeout-minutes` matches those numbers. The classifier's default is twice the supplied `expected_minutes` before it says `hang`. Pass the table in. Without it, the default budget is 30 minutes and a hang call is weak.

The queue alarm in `ci-queue-watchdog.yml` is separate: 15 minutes queued with nothing `in_progress` on that lane, or 60 minutes queued regardless. A lane that is running jobs and has an 18 minute queue does not alert. Copy that split. A busy lane is not a stuck lane.

`RP_TIMEOUT_SCALE` (a repository variable, read by Commerce CI) multiplies test timeouts on a slow runner. A baseline that ignores the scale will call a deliberate slow lane a hang. Read the variable before you escalate.

## Box sleep

The self-hosted research already records that sleep mid-job becomes "lost communication" and that a runner offline more than 14 days is deleted. RavenPower's `runner-lost-comm-rerun.yml` header states the operational version: the box freezes 20–31 minutes about every 35–40 minutes, and a freeze longer than 10 minutes fails in-flight jobs with "The self-hosted runner lost communication with the server".

Liveness rule that matches that header:

- All matching runners `offline`, job still `in_progress`, age under 10 minutes: phase `running`, class `box_offline`, action `wait`. The conclusion has not been written.
- Age past 10 minutes and the conclusion is still empty: phase `stalled`, action `restart_runner`. Do not re-run yet. The run may be about to land as `runner_lost`, and the existing workflow re-runs that class on its own.
- Conclusion already `failure` with the lost-communication annotation: the run has stopped. Classify it. Do not keep waiting on the sleep.

A sleep that takes every runner offline also piles up `queued` jobs. Those queued jobs are alive. Restarting the box drains them. Re-running them creates a second copy.

## Queue alarm when no runner matches

If no online runner has every requested label, the job waits out the 24 hour queue. The limits page describes that end as cancellation. The self-hosted runners reference page says the job will fail. Either conclusion means "nothing matched in time", not "the tests failed". That wait looks like a freeze and it is not one. The action is `relabel` (the job asks for a label nobody has) or register a runner. It is not `fix_test`.

The factory bridge, from `factory/bridge/README.md`: when a job has been queued 10 minutes and no online runner has that lane's labels, and the run is not a secret or deploy lane, the bridge points `CI_HOSTED_LIGHT_RUNS_ON` at `ubuntu-latest`, cancels the run, and re-runs so the next attempt reads the new labels. An online runner keeps the job even if the queue is long. An agent that cancels a queued job while a matching runner is online fights that rule.

**The watchdog does not see the current lanes.** `ci-queue-watchdog.yml` sets `LANE_PREFIX: rpbox` and keeps a job only when one of its labels starts with that prefix. Commerce CI jobs on run `43785768235` requested `self-hosted,box,raven-light` and `self-hosted,box,raven-web`. None of those strings start with `rpbox`. Ghost runs have no jobs, so they have no labels either. The alert that exists for "the box is not taking work" does not fire for the labels the box's jobs use, and it cannot see the Nov 11 ghosts. That is proposal O3 and O4 in the RavenPower guide, not a change made here.
