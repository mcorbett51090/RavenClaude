# Sources

Checked 2026-11-16 unless a row says otherwise. A row is a page or a command, not a paraphrase of a page.

## GitHub docs

| Topic | URL |
|---|---|
| Workflow run status and conclusion, list filter that mixes both, re-run endpoints | https://docs.github.com/en/rest/actions/workflow-runs |
| Job and step objects, `filter=latest` vs `all`, download job logs | https://docs.github.com/en/rest/actions/workflow-jobs |
| Check status and conclusion, including `startup_failure`, `pending`, `waiting` | https://docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-checks |
| Status checks: skipped job counts as success; path-filtered workflow stays pending | https://docs.github.com/en/pull-requests/reference/status-checks |
| Required checks troubleshooting, same skip-versus-pending split | https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks |
| Re-run keeps `GITHUB_SHA` and `GITHUB_REF`, 50 re-run cap, 30 days | https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs |
| Actions limits: 24 h queue, 6 h hosted job, 5 day self-hosted job, 35 day run, 500 runs / 10 s blocked, `queue: max` of 100 | https://docs.github.com/en/actions/reference/limits |
| 50 re-run cap changelog (2026-04-10) | https://github.blog/changelog/2026-04-10-actions-workflows-are-limited-to-50-reruns/ |
| Conditional requests, 304, `x-poll-interval`, rate-limit backoff | https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api |
| Rate-limit headers; `GET /rate_limit` is free on the primary limit | https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api |
| Self-hosted runner object: `status` online/offline, `busy` | https://docs.github.com/en/rest/actions/self-hosted-runners |
| `workflow_run` activity types `requested`, `in_progress`, `completed` | https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows |
| `workflow_job` actions `queued`, `in_progress`, `completed`; unmatched label waits until the queue limit | https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/autoscaling-with-self-hosted-runners |
| Workflow commands: `::error` creates an annotation | https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands |
| Using workflow run logs, `gh run view --log` and `--log-failed` | https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs |
| `needs` and `if: always()` | https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs |

## GitHub CLI and product docs

| Topic | URL |
|---|---|
| `gh pr checks`: buckets, exit 8 while pending | https://cli.github.com/manual/gh_pr_checks |
| `gh run watch --help` this session: waits until complete; `--exit-status` for a non-zero failed run | local `gh run watch --help` |
| `gh run view` refuses `--log` until the run is completed; no pending exit code | https://github.com/cli/cli/blob/trunk/pkg/cmd/run/view/view.go |
| Copilot: Actions do not run until workflows are approved; Watch and fix is separate | https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/review-copilot-output |
| Cursor automations: CI completed vs Workflow run completed (push only) | https://cursor.com/docs/cloud-agent/automations |
| Cursor `ci-watcher`: `gh pr checks` then `gh run view --log-failed` | https://github.com/cursor/plugins/blob/main/cursor-team-kit/agents/ci-watcher.md |

## Issues and writeups

| Topic | URL |
|---|---|
| Queued, zero jobs, cancel 409, still happening 2026-08 | https://github.com/actions/runner/issues/3872 |
| 180 queued zero-job runs on 2026-11-11, cancel 409, delete needs admin | https://github.com/boykopovar/AnyPS5/issues/18616 |
| Four ghost runs, list endpoint flickered to total 0 while the ids were still queued | https://github.com/arthurprinsen-ai/Bedrijfsgeheugen/issues/4655 |
| Finished-job logs while the run is open; browser websocket vs API (2023; API half contradicted by the 2026-11-16 measurement) | https://github.com/actions/runner/issues/886 |
| In-progress job log returns 404 until the job completes (third-party client, consistent with 886 for a running job) | https://github.com/austenstone/actions-workflow-viz |
| Shutdown signal, exit 143, `if: always()` does not run | https://compiler.dev/errors/runner-received-a-shutdown-signal |
| Lost communication: process death, OOM, or link; one sentence for three causes | https://latchkey.dev/learn/failures/runner-lost-communication-with-the-server |
| Job re-run gets a new machine; no syntax-level step retry | https://dev.to/kalemi/retry-failed-steps-in-github-actions-at-the-right-level-5fj6 |

## This-session reads (RavenPower-Website, read-only)

| What | Command or file |
|---|---|
| 43 Nov 11 queued runs, 43/43 with zero jobs; 12 later queued runs, 12/12 with jobs | `gh api --paginate repos/mcorbett51090/RavenPower-Website/actions/runs?status=queued&per_page=100`, then `GET .../runs/{id}/jobs` `total_count` for each |
| Live Commerce CI run `43785768235` job labels and states | `GET .../actions/runs/43785768235/jobs` |
| `cursor-gate: missing` while the run was in progress | `GET .../actions/jobs/133032915736/logs` after `gh run view --log` refused |
| Lost-communication re-run rules and the unreadable-log case | `factory/lib/rerun.mjs`, `.github/workflows/runner-lost-comm-rerun.yml` |
| Shard classification | `factory/lib/decide.mjs` `classifyJobs` |
| Failure alert waits, job timeout table, lost-comm deferral | `.github/workflows/ci-failure-alert.yml` |
| Queue alarm 15 / 60 minutes, label prefix `rpbox` | `.github/workflows/ci-queue-watchdog.yml` |
| cursor-gate wait (absent 180 s, pending 1200 s) and the comment that a skipped `build` does not satisfy a required check | `.github/workflows/commerce-ci.yml` jobs `cursor-gate` and `build` |
| Hosted fallback after 10 minutes with no matching runner | `factory/bridge/README.md` |

## Already in RavenClaude

| What | Path |
|---|---|
| Ghost-run runbook (409 / 403 / zero jobs) and the status-page check | `docs/remote-ci-autotrigger-runbook.md`, `scripts/check-github-status.sh`, `scripts/gh-health.py` |
| Runner sleep, 60 s pickup, 24 h queue | `docs/research/2026-11-15-self-hosted-runners/05-availability-sleep-updates.md` |

`commerce-ci-failure-triage` and `pipeline-chunk-resume` were not files on `origin/main` at `ee923b3d`.
