# Failure classes and the one next action

The point of a class is the action it selects. Two failures that share `conclusion: failure` do not share an action. The table the classifier implements is in [`plugins/devops-cicd/knowledge/ci-run-status.md`](../../../plugins/devops-cicd/knowledge/ci-run-status.md). This file is why the rows are shaped that way.

## What already classifies failures

RavenPower-Website, read 2026-11-16:

| Piece | What it decides | What it does not do |
|---|---|---|
| `factory/lib/rerun.mjs` | Lost communication (annotation, else log tail, else a job with no steps) and, on attempt 1, a Commerce CI run whose non-gate failures are all cancelled or timed-out shards | Re-run anything else. It will not re-run when the evidence cannot be read. |
| `runner-lost-comm-rerun.yml` | Runs that module for Commerce CI and Claude Code when conclusion is `failure` and `run_attempt <= 2` | Deploy and D1 workflows. Attempt 3. A run whose conclusion is `cancelled` because a newer run replaced it. |
| `ci-failure-alert.yml` | Opens one issue per workflow file on main. Defers a lost-communication failure on attempt 1 or 2 so the re-run workflow can try first. Counts a cancel only when a job hit its timeout or no newer run replaced it. | Pull-request failures. It never re-runs. |
| `decide.mjs` `classifyJobs` | `flakyOnly` when every judged failure is a cancelled or timed-out shard. Gate jobs `ci-gate` and `test` are left out. | A reason string an agent can read without importing the factory. |
| `ci-queue-watchdog.yml` | A lane is stuck when `rpbox*` jobs are queued 15 minutes with nothing running, or 60 minutes anyway | Jobs whose labels are `box` / `raven-web` / `raven-light`. Ghosts. |

The header on the re-run workflow says a runner drop still counts toward the fleet's 3-failure stop. A re-run is not a reset. The classifier's attempt caps sit under that rule. They do not replace it.

## How a class is chosen

Read annotations first. A missing log is unreadable, not empty. `rerun.mjs` already does this because a killed job's log can 404 (`#1034` in that file). The classifier does the same: `annotations: null` plus no `log_tail` on a `failure` with steps is `unproven`, and `rerun_allowed` is false.

Order for one job:

1. `runner guard: refusing` → `guard_rejection`. This wins over a lost-communication line, because the guard is a policy failure and re-running it on the same runner fails the same way.
2. Zero steps and conclusion `cancelled` or `failure` → `runner_lost`. The job was never acquired (`was not acquired by Runner` is the annotation RavenPower added to the same regex).
3. `lost communication with the server` → `runner_lost`.
4. `The runner has received a shutdown signal` or exit 143 → `runner_shutdown`. Same action as `runner_lost` (a new machine, inside the cap). The class stays distinct so the why is honest.
5. Authentication text → `auth`. Escalate. Do not re-run. `ci-failure-alert.yml` already treats Cloudflare code 10000 as an auth class and mentions the owner once.
6. Conclusion `timed_out` → `timeout`, unless every non-gate failure is a shard, in which case the run is `flake_shard`.
7. Assertion or test-runner text, or a bare `failure` whose text you could read and which matched nothing above → `test`.
8. Otherwise `unproven` or `unknown_failure`.

If the failed jobs (gates excluded) are more than one class, the run is `mixed`. Re-running would hide the job that is a real test failure. RavenPower's lost-communication rule is the same shape: every candidate must be a runner drop, or it re-runs nothing.

## Actions

| Class | Action | When the action is refused |
|---|---|---|
| `infra_ghost` | `wait_for_github` | Always refused: do not cancel-storm, do not re-run a run that has no jobs. Check `scripts/check-github-status.sh`. |
| `concurrency_pending`, `deployment_protection` | `wait` | A cancel does not fix the group or the protection rule. |
| `queue_no_match` | `relabel` | Re-running asks for the same labels. |
| `box_offline` | `wait` inside 10 minutes, else `restart_runner` | Re-running while the box is asleep queues another job on the same dead lane. |
| `hang` | `escalate` | A re-run of a hang that is actually a slow lane (`RP_TIMEOUT_SCALE`) wastes an attempt. Confirm the baseline first. |
| `runner_lost`, `runner_shutdown` | `rerun_failed` | Attempt greater than 2. Guard changed since this SHA. Any sibling job is a different class. A newer run already replaced this one. |
| `timeout` | `rerun_failed` | Same cap as runner loss. If the lane is known slow, fix the baseline instead of spending the cap. |
| `flake_shard` | `rerun_failed` | Attempt greater than 1. This matches `shardRule` in `rerun.mjs`. |
| `guard_rejection` | `do_not_rerun` | Always. Fix the guard or the runner name. |
| `test` | `fix_test` | A re-run is how a real failure gets called a flake. |
| `auth` | `escalate` | A re-run with the same missing secret fails again. |
| `cancelled_superseded` | `watch_successor` | Re-running the old attempt fights `cancel-in-progress`. |
| `startup_failure` | `rerun_failed` once | Guard changed, or the attempt is already 2. |
| `skipped_required` | do not treat as a pass | Re-running a skipped job runs it only if the `if:` is now true, which a re-run of the same SHA will not change. |
| `unproven`, `mixed` | `escalate` | Guessing "lost communication" from a 404 log is how a test failure gets re-run. |
| `transport` | `retry_later` | The run was not read. Do not invent a conclusion. |
| stale SHA | `watch_head` | The completed run is not the verdict for the commit you have now. |

`rerun_failed` means "a re-run of failed jobs is allowed", not "this process posted one". The script never calls the re-run API. A repo that already has `runner-lost-comm-rerun.yml` should be left to do it, or the agent and the workflow will each spend an attempt.

## The JSON verdict

One object, so the next agent does not re-derive the class from a log paste.

```json
{
  "phase": "failed",
  "alive": false,
  "failure_class": "runner_lost",
  "action": "rerun_failed",
  "rerun_allowed": true,
  "why": "Run conclusion failure classified as runner_lost.",
  "guardrails": ["A re-run uses the original commit and ref, not the branch tip."],
  "evidence": {"status": "completed", "conclusion": "failure", "run_attempt": 1, "job_count": 1}
}
```

`phase` answers "is it going". `failure_class` answers "why did it stop". `action` is the single next step. `evidence` is the fields the decision used, so a wrong class can be checked without re-reading the log.

`GITHUB_STEP_SUMMARY` and a JUnit artifact are how a **job** should publish the same facts for a human. They are not a substitute for the jobs API while the job is running: the summary is written at the end of the step, and the artifact is uploaded at a step boundary. A workflow that prints a JSON block into the summary at the end of `ci-gate` gives the next agent the class without a second classification. That is a proposed change for the product repo, not something this marketplace can commit into Commerce CI.

## Guardrails that are easy to skip

1. **The SHA is frozen.** Documented in [01](01-run-job-step-states.md). After the runner guard changes, `update_branch`. The new commit is what carries the new guard. A re-run does not.
2. **Caps.** Lost communication and timeouts: attempts 1 and 2. Shards and `startup_failure`: attempt 1. GitHub's own ceiling is 50, and the 51st fails the suite (changelog 2026-04-10). The fleet 3-failure stop, where a repo has one, is tighter than both. Stay inside the tightest cap you know about.
3. **Do not re-run on a guess.** Unreadable annotations and an unreadable log are `unproven`. RavenPower already refuses that case and writes one line to the step summary.
4. **Do not re-run a mix.** One lost runner and one assertion is `mixed`.
5. **Do not cancel a ghost in a loop.** The 409 is the result. Wait for GitHub, then a new push or `workflow_dispatch` creates a run that can actually queue.
6. **A re-run is a new machine for the job, not a new commit.** Use it for `runner_lost` and `runner_shutdown`. Do not use it for `test` or `guard_rejection`.
