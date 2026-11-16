# Self-hosted GitHub Actions runners: dynamic fleets and mixed machines (research, 2026-11-15)

Research into running our own GitHub Actions runners ("box runners") well: how a small fleet scales up and down, and how to run one fleet across machines of different types and sizes (Linux box, a CPU-capped laptop, MacBook, Mac mini). Six research passes were run. The last one turned up nothing materially new, so the loop stopped there ([pass log](passes.md)).

Facts are tagged with where they came from and the date they were checked. Treat capability rows as `[verify-at-use]`, because runner and ARC releases ship roughly monthly.

## Files

| File | What it covers |
|---|---|
| [01-autoscaling-and-ephemeral.md](01-autoscaling-and-ephemeral.md) | Persistent vs ephemeral vs JIT runners, scale sets (ARC and the standalone `actions/scaleset` client), webhook autoscalers, GARM, the AWS Terraform module, and a scaling ladder for a fleet without Kubernetes |
| [02-heterogeneous-fleets-and-routing.md](02-heterogeneous-fleets-and-routing.md) | How `runs-on` matching really works (AND-only, no fallback), capacity labelling, superset labels for overflow, limiting heavy-job concurrency with label tokens, runner-name guards vs labels |
| [03-macos-apple-silicon.md](03-macos-apple-silicon.md) | Native macOS runners vs Tart VMs, the two-macOS-VM limit, Linux arm64 VMs on a Mac, LaunchAgent vs LaunchDaemon, sleep and lid behaviour |
| [04-resource-limits-and-sizing.md](04-resource-limits-and-sizing.md) | Runners per machine from RAM and CPU, cgroup/systemd limits, the Node `availableParallelism()` cgroup trap, vitest worker and timeout tuning, WSL2 settings |
| [05-availability-sleep-updates.md](05-availability-sleep-updates.md) | Sleep and pause handling, ghost-offline listeners, the 60 s / 24 h / 14 day timers, auto-update and version enforcement |
| [06-security-and-cost.md](06-security-and-cost.md) | Threat model for self-hosted runners on private repos, secrets lanes, JIT tokens, cache poisoning, cost (the postponed $0.002/min fee, cache billing) |
| [07-recommendations-raven-fleet.md](07-recommendations-raven-fleet.md) | **Concrete recommendations for our fleet** (box + Yoga laptop + MacBook + Mac mini) |
| [sources.md](sources.md) | Every source, grouped by topic |
| [passes.md](passes.md) | The research pass log |

## Top 10 findings

1. **`runs-on` is AND-only, with no fallback.** A job goes to any online, idle runner that has *all* the labels it asks for. There is no OR, no priority, and no "prefer the big machine". If no runner matches, the job waits up to 24 h and then fails. Fallback order has to be built from labels (superset labels), a picker job, or a scale set's capacity. ([02](02-heterogeneous-fleets-and-routing.md))
2. **A weak machine that carries a strong machine's labels gets strong-machine jobs.** GitHub doesn't know how big a runner is, so a 1.5-CPU laptop runner labelled like an 8-core box will be handed heavy test shards whenever it's idle. That is a common cause of "timeouts only on some runs". Labels must describe capacity. ([02](02-heterogeneous-fleets-and-routing.md))
3. **Ephemeral or JIT runners are GitHub's recommended way to autoscale.** A persistent runner can be handed a job while it is shutting down or asleep, while an ephemeral runner takes exactly one job. JIT configs (`POST …/actions/runners/generate-jitconfig`, then `run.sh --jitconfig`) remove the long-lived registration from disk. ([01](01-autoscaling-and-ephemeral.md))
4. **Scale sets work without Kubernetes now.** `actions/scaleset` (Go, public preview, v0.5.0 on 2026-10-23) long-polls GitHub, reports a per-host `maxCapacity`, and tells you how many runners to start (`TotalAssignedJobs`). It needs no inbound webhook, so it works behind home NAT on laptops. Since ARC 0.14 (2026-03) a scale set can have several labels. ([01](01-autoscaling-and-ephemeral.md))
5. **Webhook autoscalers need a public endpoint, and GitHub itself warns about webhook timing.** GARM's pools add a pack or round-robin balancer with pool priority, which gives on-prem-first then overflow. That's useful for multiple machine pools, but it needs an inbound webhook. ([01](01-autoscaling-and-ephemeral.md))
6. **A Mac can run at most 2 macOS VMs at once (Virtualization.framework and the macOS EULA), but Linux VMs aren't capped.** On a 16 GB Mac mini, the best split is one native or Tart macOS slot for Apple-only work plus a Linux arm64 VM for general CI. ([03](03-macos-apple-silicon.md))
7. **On macOS, `svc.sh install` creates a user LaunchAgent.** It starts only after that user logs in and has no KeepAlive. A Mac used as a server needs a LaunchDaemon (through `runsvc.sh`) and `pmset` sleep settings. A MacBook still sleeps when the lid closes unless `pmset disablesleep 1` is set or `caffeinate -s` runs on AC power. ([03](03-macos-apple-silicon.md))
8. **Under nested cgroup limits, Node can over-count CPUs.** libuv's `uv_available_parallelism()` reads cgroup quotas, but it ignores a tighter child `cpu.max` when a parent also sets one (libuv#5375, fix pending). vitest and Jest size their worker pools from it, so a CPU-capped sandbox can oversubscribe and hit timeouts. Set `maxWorkers` explicitly per lane and scale timeouts. ([04](04-resource-limits-and-sizing.md))
9. **Runner lifecycle timers matter for part-time machines.** A runner must pick up an assigned job within 60 s or the job is requeued. Queued jobs fail after 24 h. A runner offline for more than 14 days is deleted (1 day for ephemeral), and laptops that sit off for two weeks come back "registration deleted". Runners must stay within 63 days of the latest release, and on GHEC versions below 2.329.0 can no longer register as of 2026-09-29. ([05](05-availability-sleep-updates.md))
10. **Self-hosted minutes are still free.** The $0.002/min platform fee announced on 2025-12-16 was postponed and had no new date as of Nov 2026. The Actions cache is 10 GB per repo for free and billed above that, so an account that can't pay should keep caches under 10 GB or cache on local disk. ([06](06-security-and-cost.md))

## How this extends what we already had

- `plugins/devops-cicd/knowledge/deployment-strategy-and-runner-cache-decision-trees.md` already had a "runner and build-cache placement" tree. This research adds the dynamic and mixed-machine layer, and that file's capability map now links here.
- Operational runbooks for the actual machines (watchdog, keepalive, ports, labels in force) live with the machines and in the private product repo. This public doc keeps to patterns and leaves out host details.
