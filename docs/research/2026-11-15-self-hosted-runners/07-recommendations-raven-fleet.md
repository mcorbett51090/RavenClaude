# 07: Recommendations for the Raven fleet

Fleet on 2026-11-15:
- **Linux box:** 16 GB, 8 cores, 4 GB swap. It sometimes pauses or sleeps. Runs about 14 persistent runners across a web lane and a light lane.
- **Yoga laptop:** 2 persistent runners in a sandboxed Linux capped at 1.5 CPU threads and 3.5 GB soft memory, plus a secrets/deploy runner.
- **Planned:** a 16 GB MacBook and a 16 GB Mac mini.
- **Routing:** repo variables hold JSON label arrays, so lanes can move without workflow edits. A runner-name guard regex in CI and a deploy-runner guard script add checks. GitHub-hosted runners aren't an option (billing).

Host-specific runbooks (ports, ids, paths) stay in the private product repo and on the machines. This page covers the design.

## R1. Make labels describe capacity, and stop the laptop matching heavy lanes (highest value)

The laptop runners carry the same lane labels as the box runners, so GitHub hands them heavy test shards whenever they're idle. That fits the vitest "Test timed out in 20000ms" failures seen there ([02](02-heterogeneous-fleets-and-routing.md) §Consequences 1).

Target scheme. Each runner gets lane labels, a host label, and trust labels. OS and arch labels are automatic.

| Host | Lane labels (superset style) | Host label | Trust label | Slots |
|---|---|---|---|---|
| Linux box | `lane-light`, `lane-web`; `lane-heavy` on **3** runners only | `host-box` | `trust-pr` | about 10 web + 3 light (current measured ceiling: about 12 web) |
| Mac mini, Linux arm64 VM (8 GB / 5 vCPU) | `lane-light`, `lane-web`; `lane-heavy` on 1 | `host-macmini` | `trust-pr` | 2 web + 1 light |
| Mac mini, macOS | `lane-macos` | `host-macmini` | `trust-pr` or the deploy lane | 1 |
| MacBook (on AC only) | `lane-light` | `host-mbp` | `trust-pr` | 1–2 |
| Yoga sandbox | `lane-light` only | `host-yoga` | `trust-pr` | 1–2 |
| Deploy/secrets | none of the above | own host label | `trust-deploy` / `trust-secrets` | 1, ephemeral |

Routing variables then become `["self-hosted","lane-heavy"]` (full test matrix), `["self-hosted","lane-web"]` (agents, unit tests), and `["self-hosted","lane-light"]` (bots, fan-out). Heavy work then *can't* reach the laptop, and light work overflows onto everything.

Until the new labels exist, the minimal fix is to **remove the shared box lane labels from the laptop runners** and give them a light-only label. This is a live label change and needs the owner's GO.

## R2. Cap heavy concurrency with label tokens, not runner count

The box measured about 0.4 GB per agent job. A full Commerce CI shard is much heavier, and the box fits only 2–3 at once. Give `lane-heavy` to exactly 3 box runners and 1 Mac-VM runner. More web runners then add agent and job throughput without letting the box run 10 heavy builds at once and swap ([02](02-heterogeneous-fleets-and-routing.md) §3, [04](04-resource-limits-and-sizing.md)).

## R3. Per-lane test knobs instead of global timeouts

- Set a timeout multiplier and a worker cap **in each runner's `.env`**, not in workflows. The product repo already reads a timeout-scale knob from the runner env. Add a matching worker-cap knob that feeds vitest's `maxWorkers` (1 on the 1.5-CPU lane, unset elsewhere), and use `pool: "forks"` there.
- This also covers the libuv nested-cgroup bug, where Node can report more CPUs than the sandbox allows ([04](04-resource-limits-and-sizing.md)).

## R4. Make the name guard survive new machine types

The CI runner-name guard already had to be widened once for a new naming scheme, and the regex is copied into many places. Adopt one scheme, `rp-<host>-<lane>-<n>` (e.g. `rp-macmini-web-1`), and keep the guard in a single shared script that allowlists hosts and refuses deploy and secrets names for PR jobs. Then the Mac mini and MacBook don't each need a guard PR. Keep the existing patterns valid during migration.

## R5. Go dynamic in two steps (no Kubernetes)

1. **Now: an ephemeral slot loop with a memory governor** on each host. N slots, each looping mint token → `config.sh --ephemeral --work <fresh>` → one job → wipe. A new slot starts only while available memory is above a floor (e.g. 3 GB on the box, 2 GB in the Mac VM). The deploy-runner design already uses this loop. Reuse it for the PR lanes on new hosts first (Mac mini, MacBook) so the existing box runners aren't disturbed.
2. **Next: a per-host `actions/scaleset` daemon**, one scale set per (host, lane) named after the lane label with multi-labels. It reports `maxCapacity` from live free RAM and CPU and keeps `minRunners` at 1 for `lane-light` and 0 for `lane-heavy`. It's outbound-only and suits laptops behind NAT. It needs a GitHub App or token with repo Administration: write on a control host, which is the owner's decision ([01](01-autoscaling-and-ephemeral.md)).
3. GARM only if strict "box first, Mac second, laptop last" ordering becomes worth running a webhook endpoint for.

## R6. Mac mini and MacBook setup checklist

- A dedicated non-admin `ghrunner` user. A **LaunchDaemon** through `runsvc.sh` (not `svc.sh`'s LaunchAgent). `pmset -a sleep 0 disksleep 0`. Restart after power failure. FileVault means a login at boot, so plan for it ([03](03-macos-apple-silicon.md)).
- Linux arm64 VM (Lima, Colima or OrbStack) for the general Linux lanes. Check that the lockfile installs arm64 optional packages (`@cloudflare/workerd-linux-arm64`, esbuild, etc.) before adding `lane-heavy` there.
- macOS slot: native first. Use Tart (max 2 macOS VMs) only if macOS jobs need isolation.
- MacBook: `lane-light` only, `caffeinate -s` while on AC. Accept that it's part-time.

## R7. Sleep and pause hygiene

- Keep the keepalive and watchdog on persistent runners. Ephemeral and scale-set runners make pauses cheaper because no job is assigned to a sleeping persistent runner.
- Keep a "rerun once on lost-communication" guard for jobs that die mid-pause.
- Alert before a part-time runner reaches **14 days** offline, when GitHub deletes it. The dead registrations found on 2026-11-15 fit this.
- Keep runner versions current (63-day rule). Check them with the deprecations API in the fleet check.

## R8. Keep trust lanes isolated

Deploy and secrets runners keep hard-coded labels, no `vars.*` override, and ephemeral registration. They never share a host user or work dir with PR lanes. The Mac mini can host the ephemeral deploy runner, but only as a separate OS user and never in the same VM as PR runners ([06](06-security-and-cost.md)).

## Proposed live changes (each needs the owner's GO)

| # | Change | Why | Risk / rollback |
|---|---|---|---|
| L1 | Remove the shared box lane labels from the two laptop runners; leave them light-only | stops heavy shards from landing on a 1.5-CPU sandbox | PC-only jobs keep working; re-add the labels to roll back |
| L2 | Add `lane-heavy`/`lane-web`/`lane-light` (+ host labels) to box runners, `lane-heavy` on 3 only | capacity routing and heavy semaphore | additive; no effect until vars change |
| L3 | Point routing vars at lane labels | uses L2 | revert the vars |
| L4 | Set the timeout-scale and worker-cap knobs in the laptop runners' `.env` | the sandbox stops timing out | delete the lines |
| L5 | Guard PR: structured name scheme, one shared guard | no guard PR per new machine | normal PR plus SHIP |
| L6 | Mac mini: Linux VM runners (ephemeral loop) + macOS/deploy slot | capacity and the planned deploy host | new registrations only |
| L7 | Later: scale-set daemon plus a GitHub App | dynamic capacity | new credential to manage |
