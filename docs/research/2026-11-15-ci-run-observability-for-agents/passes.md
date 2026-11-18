# Research pass log

Times are UTC on 2026-11-16. That is the evening of 2026-11-15 in US Eastern. The folder date matches the sibling runner research from that evening.

## Pass 1 — states, conclusions, re-runs, skipped checks

- Workflow run `status`: `queued`, `in_progress`, `completed`, `waiting`, `requested`, `pending`. Conclusion, when completed: `success`, `failure`, `neutral`, `cancelled`, `skipped`, `timed_out`, `action_required`, `stale`. The list-runs `status` filter also accepts conclusion values, so `status=failure` is not a status. https://docs.github.com/en/rest/actions/workflow-runs
- Check `status` adds `startup_failure` as a check-suite conclusion. `pending` is "front of the queue but the concurrency limit is reached". `waiting` is a deployment protection rule. `requested` is created but not queued. Only Actions sets `requested`, `waiting`, and `pending`. https://docs.github.com/en/pull-requests/reference/status-checks and https://docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-checks
- A job skipped by `if:` reports success and does not block a required check. A workflow skipped by a path filter stays pending and blocks. https://docs.github.com/en/pull-requests/reference/status-checks and https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- Re-runs use the original actor's privileges and the original `GITHUB_SHA` and `GITHUB_REF`, for 30 days, at most 50 times including partial re-runs. https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs
- "The runner has received a shutdown signal" is exit 143 (SIGTERM). `if: always()` steps in that job do not run. Lost communication is the same family when the agent dies without the signal. https://compiler.dev/errors/runner-received-a-shutdown-signal and https://latchkey.dev/learn/failures/runner-lost-communication-with-the-server

Pass 1 verdict: large.

## Pass 2 — ghosts, logs, ETags, the Nov 11 count

- Public reports of `status: queued`, zero jobs, cancel and force-cancel HTTP 409 "not been queued yet", delete HTTP 403. Same shape as `docs/remote-ci-autotrigger-runbook.md`. https://github.com/actions/runner/issues/3872 and https://github.com/boykopovar/AnyPS5/issues/18616 (180 runs on 2026-11-11, a different repo, same hour window).
- Measured on RavenPower-Website, read-only, 2026-11-16 ~01:30 UTC. `GET /actions/runs?status=queued` paginated: 55 queued. 43 created 2026-11-11, all with `updated_at == created_at`. Each of those 43 had `GET .../jobs` `total_count` 0. The other 12 (created 2026-11-15 or 2026-11-16) all had `total_count` > 0. RavenClaude had 0 queued runs created 2026-11-11.
- Authorized conditional GET: a 304 does not count against the primary rate limit. 403/429: stop, honor `retry-after` or `x-ratelimit-reset`. https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api
- `workflow_job` actions include `queued`, `in_progress`, and `completed`. A job with no matching runner stays queued until the 24 hour limit. https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/autoscaling-with-self-hosted-runners (the cloud docs page states the same three actions; the Enterprise Server 3.4 URL was what the search returned, and the sentence matches the current autoscaling page's description).

Pass 2 verdict: large. The 43-count is a measurement, not a quote from the prompt.

## Pass 3 — agent tools, cursor-gate, the watchdog's labels

- `gh pr checks` buckets: pass, fail, pending, skipping, cancel. Extra exit code 8 while pending. https://cli.github.com/manual/gh_pr_checks
- `gh run watch` waits until the run completes. `--exit-status` is what makes a failed run non-zero. https://cli.github.com/manual/gh_run_watch (`gh run watch --help` this session).
- Copilot cloud agent does not run Actions until workflows are approved. "Watch and fix" is a separate merge-box setting. https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/review-copilot-output
- Cursor automations: "CI completed" is the pull-request check trigger. "Workflow run completed" matches `push` only, not `pull_request`, `workflow_dispatch`, or `schedule`. https://cursor.com/docs/cloud-agent/automations
- Cursor's published `ci-watcher` agent uses `gh pr checks` then `gh run view --log-failed`. https://github.com/cursor/plugins/blob/main/cursor-team-kit/agents/ci-watcher.md
- Live run `43785768235` (Commerce CI), first jobs page, 2026-11-16 ~01:29 UTC: `cursor-gate`, `changes`, and `factory` completed success on `box-raven-light-*`. `build` and two `test-shard` jobs `in_progress` on `box-raven-web-*`. Four jobs still `queued` with labels `self-hosted,box,raven-web`. `gh run view --log` said the run was still in progress. `GET /actions/jobs/133032915736/logs` returned `cursor-gate: missing`.
- `ci-queue-watchdog.yml` keeps only job labels that `startswith("rpbox")`. The live labels do not. Ghosts have no job labels at all.

Pass 3 verdict: large.

## Pass 4 — rate-limit text and annotations

- Confirmed on the best-practices page: poll on a schedule, honor `x-poll-interval`, conditional requests, 304 does not spend the primary limit when the request is authorized. https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api
- `::error` writes an annotation the Checks API can return before you download the log. https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands
- `GET /rate_limit` does not spend the primary limit. It can spend the secondary limit. https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api

Pass 4 verdict: small (the 304 rule and the annotation command were not in passes 1–3 as cited pages).

## Pass 5 — jobs list filter

- `filter=latest` (default) is the latest attempt. `filter=all` includes older attempts. Job `status` enum on that endpoint: `queued`, `in_progress`, `completed`, `waiting`, `requested`, `pending`. Job `conclusion` enum there: `success`, `failure`, `neutral`, `cancelled`, `skipped`, `timed_out`, `action_required`. `startup_failure` is a check-suite / run conclusion, not in that job enum. https://docs.github.com/en/rest/actions/workflow-jobs

Pass 5 verdict: small (one pitfall: reading `all` and treating an old failure as the live attempt).

## Pass 6 — limits that bound a wait

- Queue time 24 hours, then the job is cancelled. Hosted job execution 6 hours. Self-hosted job execution 5 days. Workflow run 35 days, including waiting. Concurrency `queue: max` holds 100, then further runs are rejected. A repository that triggers more than 500 workflow runs in 10 seconds has the extras **blocked and not queued** (a different empty outcome from a ghost that exists as queued). Re-run cap 50. https://docs.github.com/en/actions/reference/limits
- Exceeding 50 re-runs fails the check suite with an annotation. https://github.blog/changelog/2026-04-10-actions-workflows-are-limited-to-50-reruns/
- A job re-run gets a new machine. A step retry does not. There is no workflow-syntax retry key. https://dev.to/kalemi/retry-failed-steps-in-github-actions-at-the-right-level-5fj6

Pass 6 verdict: small (the 24 h / 6 h / 50 caps were only half-stated in pass 1; the "blocked and not queued" rate and the new-machine point are new).

## Pass 7 — CLI log gate versus the job-log API

- `cli/cli` `pkg/cmd/run/view/view.go`: if the run status is not completed, `--log` returns "run {id} is still in progress; logs will be available when it is complete" before it calls the API. A TODO says pending has no separate exit code. https://github.com/cli/cli/blob/trunk/pkg/cmd/run/view/view.go
- `actions/runner` issue 886 (2023) says a finished job's log is also unavailable from the API while the workflow is open, and describes the browser websocket. The 2026-11-16 measurement on run `43785768235` disagrees with the API half of that comment: the job-log endpoint returned 200 and the `cursor-gate: missing` line while the run was `in_progress`. The CLI half still matches. https://github.com/actions/runner/issues/886

Pass 7 verdict: small (the CLI-versus-API split was measured in pass 3 and explained here).

## Pass 8 — saturation

Re-read the same `view.go` and runner issue 886. The pending-exit TODO is the only line not already written down, and pass 7 includes it. No new status, timer, webhook, or liveness mechanism.

Pass 8 verdict: **nothing materially new → stop.**
