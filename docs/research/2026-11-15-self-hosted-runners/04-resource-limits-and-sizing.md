# 04: Resource limits, runners per machine, and test tuning

## One runner = one job

A runner process runs one job at a time. Parallelism on a host means N runner registrations (separate dirs, unique names), and N should come from measured job cost, not core count. RAM is usually the binding limit ([GitLab fleet guide](https://docs.gitlab.com/topics/runner_fleet_design_guides/gitlab_runner_fleet_config_and_best_practices/), [3h4x](https://3h4x.github.io/tech/2026/02/12/github-actions-self-hosted-runners)).

### A sizing formula you can run on any host

```
usable_mem   = total_RAM - OS/desktop reserve (2 GB server, 4 GB laptop/desktop) - 10% headroom
usable_cpu   = cores (or the cgroup quota if capped) - 0.5 for the OS
heavy_slots  = min( floor(usable_mem / heavy_job_peak_mem), floor(usable_cpu / heavy_job_cpu) )
web_slots    = floor((usable_mem - heavy_slots*heavy_peak) / web_job_peak)
light_slots  = 1–3 extra (they idle at ~0.1 GB; job peak < 0.5 GB)
```

Measure `heavy_job_peak_mem` as the PSS of the whole Worker process tree during the worst job (`smem`, or the cgroup's `memory.peak`), not the RSS of one process.

Worked examples (assuming heavy peak 3 GB / 2 cores, web peak 1 GB / 1 core):

| Host | RAM / CPU | heavy | web | light | Notes |
|---|---|---|---|---|---|
| Linux server box | 16 GB / 8 | 3 | 6–8 | 2–3 | idle listeners ~0.12 GB each; swap only to absorb spikes |
| Mac mini (Linux VM 8 GB / 5 vCPU) | 16 GB / 10 | 1–2 | 2 | 1 | plus 1 macOS slot outside the VM |
| MacBook, laptop use | 16 GB / 8–10 | 0 | 0–1 | 1–2 | AC power only |
| CPU-capped sandbox | 3.5 GB soft / 1.5 CPU | 0 | 0 | 1 | light lane only; heavy tests time out here |

## Linux resource controls

- With systemd: put runners in a slice and set `MemoryHigh=` (throttle; the main control) with `MemoryMax=` as the last-resort OOM line, plus `CPUQuota=` (e.g. `150%`), `CPUWeight=` (`idle` gives runners only spare CPU on a shared desktop), `TasksMax=`, and `IOWeight=` ([systemd.resource-control](https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html)).
- `MemoryHigh` is a **soft** limit. Above it the kernel reclaims aggressively and the cgroup crawls rather than dying. That looks like random test timeouts, not OOM kills.
- Without systemd (some containers and VMs), the same knobs are the cgroup v2 files (`memory.high`, `memory.max`, `cpu.max`, `cpu.weight`) when delegated, or a VM-level cap.
- On Debian/Ubuntu with `needrestart`, stop it from restarting `actions.runner.*` services mid-job ([GitHub docs](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application)).

## The Node parallelism trap

- vitest's `maxWorkers` defaults to **all available parallelism** when not in watch mode ([vitest maxWorkers](https://vitest.dev/config/maxworkers)). Jest and many bundlers do the same through `os.availableParallelism()`.
- libuv (Node) reads cgroup CPU quotas ([libuv#4278](https://github.com/libuv/libuv/pull/4278)), but has had bugs: cgroup v2 reporting 1 CPU on a 4-CPU container in Node 22.12+ (fixed, [node#58428](https://github.com/nodejs/node/issues/58428)), and **a tighter child `cpu.max` being ignored when a parent cgroup also has one** ([libuv#5375](https://github.com/libuv/libuv/issues/5375), open as of 2026-11, fix in #5377). A systemd service capped at 2 CPUs inside an 8-CPU slice reports 8.
- Under a 1.5-CPU cap that means up to 8 test workers time-sharing 1.5 cores, and each test takes 5× longer, so 20 s timeouts trip.
- Fix it per lane, not globally:
  1. set `maxWorkers` explicitly from a runner-level env knob (e.g. 1 on a 1.5-CPU lane), and prefer `pool: "forks"` on constrained hosts ([vitest pool](https://vitest.dev/config/pool), [BerryBox](https://berrybox.io/playbooks/slow-tests/match-workers-to-cores))
  2. scale `testTimeout`/`hookTimeout` from a runner-level multiplier set in the runner's `.env` (actions/runner loads that file into every job), never by editing the timeouts in workflows
  3. better still, route heavy suites off constrained hosts with labels ([02](02-heterogeneous-fleets-and-routing.md))

## WSL2 hosts (Windows laptops)

- `%USERPROFILE%\.wslconfig`: `[wsl2] memory=…`, `processors=…`, and **`vmIdleTimeout=-1`**. Under `[general]`, **`instanceIdleTimeout=-1`**. Otherwise WSL stops the VM or distro when idle and the runner goes offline ([wsl-config](https://github.com/MicrosoftDocs/WSL/blob/main/WSL/wsl-config.md), [WSL#9245](https://github.com/microsoft/WSL/discussions/9245)).
- `/etc/wsl.conf` `[boot] systemd=true` allows `svc.sh` and systemd resource controls inside the distro.
- Windows sleep or hibernate suspends WSL too, so it's the same "part-time runner" caveats as a MacBook.

## Containers in jobs

- `container:` and `services:` need Docker on Linux. Rootless Podman can stand in via `ACTIONS_RUNNER_CONTAINER_HOOKS` ([GitHub docs](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/customize-containers), [podman hooks](https://github.com/UniversityofWarwick/github-runner-podman-hooks)).
- Never mount the host Docker socket into PR jobs. Socket access is root on the host.

## Caching on self-hosted runners

- `actions/cache` still uploads to and downloads from GitHub: 10 GB per repo free, billed above that, with entries evicted after 7 days unused ([changelog](https://github.blog/changelog/2025-11-20-github-actions-cache-size-can-now-exceed-10-gb-per-repository/)).
- Persistent runners already keep `~/.npm` and tool caches on local disk. One shared `npm` cache dir per host is usually fine, because npm's cache is content-addressed and written atomically. If `EINTEGRITY` errors show up under heavy parallelism, split the cache per runner. Keep `node_modules` per job.
- Untrusted jobs must not be able to write a cache that trusted jobs later restore ([cache poisoning, see 06](06-security-and-cost.md)).
