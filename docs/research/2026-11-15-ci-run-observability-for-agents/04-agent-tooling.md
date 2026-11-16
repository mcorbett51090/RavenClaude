# How agents check CI, and the two false readings

## GitHub CLI

Checked this session with `gh run watch --help`, and against the manual pages linked in [sources.md](sources.md).

| Command | What it is for | The false reading |
|---|---|---|
| `gh pr checks` | One pull request. `--json` adds `bucket`: `pass`, `fail`, `pending`, `skipping`, `cancel`. | `pending` covers queued and in progress. Exit code **8** means "still pending", not "failed". |
| `gh pr checks --watch` | Polls until the checks finish. `--fail-fast` returns on the first failure. | A required job that is `skipping` can sit beside `pass` buckets. Read `bucket`, do not grep for the word pass. |
| `gh run watch` | Polls one run until `status` is completed. Default interval 3 seconds. | Without `--exit-status` the command returns 0 when the watch ends, including after `conclusion: failure`. The CLI source has a TODO that there is no separate exit code for pending. |
| `gh run view --log` | Full log for a run or `--job`. | Refuses while the **run** is `in_progress`, even if that job has finished. Measured on run `43785768235`: the message was "run 43785768235 is still in progress; logs will be available when it is complete". |
| `gh run view --log-failed` | Failed steps only. | Same refusal. And `gh api` drops the body unless you pass `--allow-escape-sequences`, because logs contain color codes. An empty capture is not an empty log. |
| `gh run list --status queued` | The queue. | Mixes ghosts (zero jobs) with a real queue. Always read `/jobs` `total_count`. |

The job-log REST endpoint is not the same gate as `gh run view --log`. `GET /actions/jobs/133032915736/logs` returned the finished `cursor-gate` log while that run was still in progress. Prefer the API for a completed job. Prefer `steps[]` for a job that is still `in_progress`.

Polling pattern when you do not have a webhook: `gh pr checks --watch --interval 15`, or a conditional GET of the jobs endpoint with the saved `etag`. On 304, keep the previous verdict. On 403 or 429, `retry_later`. Do not shorten the interval because a run looks stuck. The best-practices page says to honor `x-poll-interval` and to back off on the secondary limit, because continuing can get the token banned.

## What each host actually does

**GitHub Copilot cloud agent.** Actions workflows do not run on a Copilot pull request until someone uses "Approve and run workflows", unless the repository has been set to allow them unattended. An agent that sees zero checks on a Copilot PR should check that approval before it calls the push a missing-webhook incident. "Watch and fix" (Agent Merge) is a separate setting in the merge box. It is not on by default. Source: GitHub Docs "Review output from Copilot", retrieved 2026-11-16.

**Claude Code on the web, this marketplace.** `docs/remote-ci-autotrigger-runbook.md` is the procedure: after a push, confirm a run exists for the current head; zero checks is a missing `pull_request` event, not a failed run; a queued run with zero jobs is the ghost case, and `scripts/check-github-status.sh` comes before any cancel. `scripts/gh-health.py` answers "is this GitHub or us" and refuses to say LOCAL when a probe did not run. Neither tool classifies a single run's jobs. That is what `classify_ci_run_state.py` adds.

**Cursor.** Automations can trigger on "CI completed" for a pull-request check. "Workflow run completed" fires for a workflow run started by `push` only. A `pull_request` run does not match it. An automation that waits on "Workflow run completed" to see Commerce CI will never wake up for a PR. Source: Cursor automations docs, retrieved 2026-11-16.

Cursor's published `ci-watcher` agent (`cursor/plugins` `cursor-team-kit/agents/ci-watcher.md`) does `gh pr checks --json`, then `gh pr checks --watch --fail-fast`, then `gh run view --log-failed`. That sequence is right for "wait, then read the failure". It is wrong if `--log-failed` is called while the run is `in_progress` (the CLI refuses) or if a `skipping` bucket is ignored on the way to "passed". The knowledge file in this plugin is the check to add in front of that sequence.

**Cursor cloud agents on RavenPower-Website** do not post a check named for the agent. The factory bridge writes a commit status `factory-ci`. Commerce CI's `cursor-gate` job polls `GET /repos/{repo}/commits/{head}/status` for context `factory-ci`. Absent for 180 seconds (`RP_WAIT_SECONDS`) sets state `missing` and the rest of the workflow runs. `pending` is polled up to 1200 seconds (`RP_PENDING_SECONDS`). The job itself exits 0 in every branch. On run `43785768235` the job conclusion was `success` and the log line was `cursor-gate: missing`, and `build` was `in_progress`. An agent that treats `cursor-gate` success as "Cursor already ran the suite" will skip the reading of `build`.

The bridge README says a skipped `build` does not satisfy a ruleset that requires it, and `commerce-ci.yml` says the same in the `build` job comment. GitHub's status-checks page, retrieved the same day, says a skipped job reports success and does not block a required check. Those three sentences disagree. This research does not pick a winner from a live ruleset evaluation; no ruleset was queried. Until that is read on one pull request, an agent should not treat a skipped required job as either "merge is blocked" or "the suite ran". It should report `false_green` and leave the merge decision to the ruleset result (`gh pr view --json mergeStateStatus`).

## False "stopped"

Call the run stopped only when `status` is `completed`, or when the ghost test passes (queued, zero jobs, `updated_at` frozen, older than 10 minutes).

Not stopped:

- `queued` jobs while a matching runner is online, including when that runner is busy
- `pending` because the concurrency group is full
- `waiting` on a protection rule
- `cursor-gate` in progress for up to 20 minutes while `factory-ci` is pending (the job `timeout-minutes` is 25)
- runners offline for less than the sleep grace while a job is `in_progress`
- a 304
- a 403 or 429
- `gh run view --log` refusing because the run is open
- the Nov 15/16 queued Commerce CI runs, which had jobs

Stopped, and not a test failure:

- the 43 Nov 11 runs (zero jobs, frozen timestamps)
- `startup_failure`
- `cancelled` because a newer push replaced the run
- queue waited out the 24 hour limit

## False green

Call the suite green only when the run `conclusion` is `success` **and** every required job concluded `success` rather than `skipped` or `neutral`, **and** `head_sha` is the commit you are judging.

Not green:

- a required job with conclusion `skipped` (GitHub may still allow the merge; the suite did not run)
- `cursor-gate` conclusion `success` with output state `missing`, `skip`, or `error`
- a success on an older SHA, including a re-run of that SHA after the branch moved
- `neutral` from an advisory bot that was mistakenly added to the required set (this plugin's `pipeline-required-checks-gate-the-merge.md` already says to keep that bot off the list)
- `gh pr checks` with only `skipping` and `pass` when the `pass` rows are the skipped jobs reported as success

A path filter on a required workflow is the opposite bug: the check stays pending and the pull request cannot merge. Commerce CI's file header explains why its path filter is on the job, not the workflow. An agent that "fixes" a pending required check by adding `paths:` to the workflow trigger will hang the next pull request. The fix for a pending check that never appears is in the autotrigger runbook (`workflow_dispatch`), not a path filter.
