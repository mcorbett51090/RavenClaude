# 05: Availability, sleep and pauses, updates

## Timers that matter

| Timer | Value | Effect |
|---|---|---|
| Job pickup | 60 s | an assigned job not acquired in time is requeued (scale-set clients see `JobAssigned` then `canceled`, up to 3 times) |
| Queue limit | 24 h | a job with no matching online runner fails after 24 h |
| Offline removal | **14 days** (ephemeral: 1 day) | GitHub deletes the registration; the local dir then fails with "registration deleted" or an invalid signature and needs a **new** registration ([remove runners](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/remove-runners)) |
| Update window | 63 days | a runner not updated within 63 days of a newer release gets no jobs; critical security updates can cut that short |
| Auto-update | on job assignment, or within a week of release | `--disableupdate` turns it off (useful for baked images); you then own the 63-day clock |
| Version enforcement (GHEC) | 2026-09-29 | runners below 2.329.0 can't register; a higher runtime minimum applies to running jobs ([changelog](https://github.blog/changelog/2026-09-28-self-hosted-runner-version-enforcement-date-has-moved/)) |

Check any version: `GET /repos/{o}/{r}/actions/runners/deprecations/{version}` returns `registration_deprecates_at` and `runtime_deprecates_at` (null = none scheduled). On 2026-11-15, 2.338.2 returned null/null and 2.329.0 returned registration 2026-09-29.

The runner's internal Node moved to 24 in 2.338.x. `ACTIONS_RUNNER_FORCED_INTERNAL_NODE_VERSION=node20` in `.env` is the temporary escape hatch ([v2.338.2 notes](https://github.com/actions/runner/releases/tag/v2.338.2)). v2.338.2 also adds broker WebSocket connectivity probes (#4753) and owned-session cleanup (#4743), both aimed at listeners that look alive but are disconnected.

## Sleep, pause and network drops

- **Idle runner sleeps:** it shows offline, and queued jobs wait (up to 24 h) until it wakes. Harmless, except for the 14-day removal.
- **Busy runner sleeps:** the job's lease lapses and the run fails with "lost communication with the server". It must be rerun ([actions/runner#3862](https://github.com/actions/runner/issues/3862), [#2040](https://github.com/actions/runner/issues/2040)). An auto-rerun-once workflow for that specific failure is a reasonable guard.
- **Persistent runners after a pause:** the listener can come back "alive but disconnected" (ghost offline). Supervise with a keepalive that restarts dead processes and a watchdog that soft-restarts *idle* listeners which have been offline on GitHub, or without a TCP session, for several checks. Never signal a busy Worker.
- **Ephemeral or scale-set runners** limit the damage: GitHub assigns them exactly one job, and a host that sleeps simply provides no capacity. GitHub's docs give this as the reason to prefer ephemeral for anything that scales or sleeps.
- Prevent sleep where the machine is meant to be a server: `pmset` (macOS), Windows power plan plus WSL idle timeouts, or a host-side keep-awake. Laptops are **part-time capacity**. Route only light or overflow work to them, and never a job whose loss blocks a release.

## Observability for a small fleet

- Poll `GET /repos/{o}/{r}/actions/runners` (status, busy, labels, version) on a schedule and alert on: a lane with 0 online runners, a runner offline for more than 1 h that should be up, a version near its deprecation date, or a registration close to 14 days offline.
- Ship `_diag/Runner_*.log` and `Worker_*.log` off the host if runners are ephemeral. GitHub says to do this before relying on ephemeral autoscaling in production.
- Track queue time per lane (`created_at` → `started_at` of jobs). That's the signal for adding or removing slots.
