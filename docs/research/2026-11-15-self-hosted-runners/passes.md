# Research pass log (2026-11-15, times ET)

## Pass 1 — official GitHub docs + scaleset/ARC (started 7:52 PM ET)
- docs.github.com self-hosted runners reference: routing (idle match → 60 s pickup else requeue; no match → queued; 24 h → fail), ephemeral recommended for autoscaling (persistent can get jobs while shutting down), `--disableupdate` + 63-day rule, `registration_deprecates_at`/`runtime_deprecates_at`, workflow_job webhook autoscaling caveat, domains list. https://docs.github.com/en/actions/reference/runners/self-hosted-runners
- runs-on semantics: array = AND of labels, no OR/fallback; `group:` + `labels:`; `--no-default-labels`; ARC doesn't support `self-hosted` label. https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job
- actions/scaleset Go client (public preview, v0.5.0 2026-10-23): scale sets outside k8s, TotalAssignedJobs, maxCapacity header, JIT configs, examples/dockerscaleset (minRunners). https://github.com/actions/scaleset
- ARC 0.14.0 (2026-03-19) multilabel scale sets; ARC gha-runner-scale-set 0.15.1 (2026-10-23). https://github.blog/changelog/2026-03-19-actions-runner-controller-release-0-14-0/
- Secure use: self-hosted runners not for public repos; JIT runners `./run.sh --jitconfig`; secrets in argv visible via `ps` to co-resident jobs. https://docs.github.com/en/actions/reference/security/secure-use
- philips-labs → github-aws-runners terraform module: webhook→SQS (30 s delay) scale-up, idle pools, experimental scale-set controller. https://github-aws-runners.github.io/terraform-aws-github-runner/
- systemd resource-control: MemoryHigh (throttle) vs MemoryMax (OOM), CPUQuota, CPUWeight=idle, AllowedCPUs, TasksMax. https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html
- Live check (read-only, 8:05 PM ET): current runner version has no deprecation date; the laptop runners were found carrying the same lane labels as the box runners (see 07 R1).
Pass 1 verdict: large — foundation.

## Pass 2 — macOS / Apple Silicon / sleep (7:58 PM ET)
- Apple Virtualization.framework + macOS EULA: max 2 macOS guest VMs per Mac; Linux guests are not limited. Tart / Tartelet ephemeral loop (clone → boot → register → 1 job → delete); ~12% slowdown running 2 VMs. https://github.com/framna-dk/tartelet , https://josephduffy.co.uk/posts/self-hosting-macos-github-runners , https://github.com/cirruslabs/tart/issues/237 , https://github.com/apple/container/discussions/234
- `svc.sh install` on macOS = user LaunchAgent (needs login; no KeepAlive); LaunchDaemon via `runsvc.sh` for boot without login; `pmset -a sleep 0`, lid-close forced sleep, `pmset disablesleep 1`, `caffeinate -s` on AC. https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application , https://keepmacawake.com/blog/github-runner-mac-sleep , https://aipps.dev/articles/self-hosted-mac-mini-runner-github-actions-keychains-xcodes
- Sleep mid-job → "lost communication with the server", rerun needed. https://github.com/actions/runner/issues/3862
Pass 2 verdict: large.

## Pass 3 — scaling tools, cost, lifecycle (8:01 PM ET)
- Runner groups = organizations only; a user-owned repo uses repo-level runners + labels (JIT `runner_group_id` 1 = Default). https://github.blog/changelog/2024-10-17-actions-runner-groups-now-available-for-organizations-on-free-plan/ , https://docs.github.com/en/rest/actions/self-hosted-runners
- GARM: pools (webhook) with round-robin or pack balancer + priority = on-prem-first fallback; also native scale sets; LXD/Incus/k8s providers. https://github.com/cloudbase/garm , https://github.com/cloudbase/garm/blob/main/doc/pools-and-scaling.md
- $0.002/min self-hosted fee announced 2025-12-16, postponed; still free Nov 2026. https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions/ , https://runs-on.com/blog/github-self-hosted-runner-fee-2026/
- Cache: 10 GB/repo free, above that billed; 7-day eviction. https://github.blog/changelog/2025-11-20-github-actions-cache-size-can-now-exceed-10-gb-per-repository/
- Offline runner auto-removed after 14 days (ephemeral: 1 day). https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/remove-runners
- Version enforcement (GHEC) 2026-09-29: <2.329.0 can't register; deprecations REST API. https://github.blog/changelog/2026-09-28-self-hosted-runner-version-enforcement-date-has-moved/
- ARC 0.15.0 (2026-10-01) reliability items. https://github.blog/changelog/2026-10-01-actions-runner-controller-release-0-15-0/
- Node `os.availableParallelism()` / libuv cgroup handling: v2 fixed 2024–25, but nested cgroup child quota ignored (libuv#5375, open fix #5377) → test runners oversubscribe in nested limits. https://github.com/libuv/libuv/issues/5375 , https://github.com/libuv/libuv/pull/4278 , https://github.com/nodejs/node/issues/58428
- vitest `maxWorkers` default = all available parallelism (non-watch). https://vitest.dev/config/maxworkers
- WSL2: `vmIdleTimeout=-1`, `instanceIdleTimeout=-1`, `[boot] systemd=true`, `.wslconfig` memory/processors. https://github.com/MicrosoftDocs/WSL/blob/main/WSL/wsl-config.md , https://github.com/microsoft/WSL/discussions/9245
Pass 3 verdict: large.

## Pass 4 — containers, test tuning (8:06 PM ET)
- Container jobs/service containers need Linux + Docker; `ACTIONS_RUNNER_CONTAINER_HOOKS` lets rootless Podman stand in (community hooks). https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/customize-containers , https://github.com/UniversityofWarwick/github-runner-podman-hooks
- Constrained CI: `pool: "forks"`, cap `maxWorkers` to the effective CPU quota, raise test/hook timeouts. https://vitest.dev/config/pool , https://berrybox.io/playbooks/slow-tests/match-workers-to-cores
Pass 4 verdict: small (two new items).

## Pass 5 — arm64 compatibility (8:07 PM ET)
- workerd/wrangler ship `@cloudflare/workerd-linux-arm64`; arm64 Linux VMs on Apple Silicon can run Cloudflare tooling; watch optional native deps in lockfiles. https://www.npmjs.com/package/@cloudflare/workerd-linux-arm64 , https://dev.to/kalemi/github-actions-arm-runners-what-breaks-when-you-switch-1kb2
Pass 5 verdict: small (one gotcha).

## Pass 6 — saturation check (8:08 PM ET)
- General 2026 best-practice round-ups (ephemeral per job, egress-only network, short-lived tokens, monitor offline/disk) only restate passes 1–4. https://lizard.build/blog/github-actions-self-hosted-runner , https://www.stephane-robert.info/en/docs/github-actions/runners/securing/
Pass 6 verdict: **nothing materially new → stop.**
