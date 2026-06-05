---
scenario_id: 2026-06-05-crashloopbackoff-oomkilled-triage
contributed_at: 2026-06-05
plugin: cloud-native-kubernetes
product: kubernetes
product_version: "unknown"
scope: likely-general
tags: [crashloopbackoff, oomkilled, resource-limits, probes, exit-137, triage]
confidence: high
reviewed: false
---

## Problem

A Deployment kept flapping: pods cycled `Running → CrashLoopBackOff` with the back-off timer stretching to the 5-minute cap, and the service dropped requests in bursts. `kubectl get pods` showed `RESTARTS` climbing into the dozens. The on-call instinct was "the app is crashing — page the dev team," but the crash and the restart were two different bugs wearing one costume: an **OOMKill** (exit 137) *and* a **liveness probe that was killing a slow-but-healthy pod**.

## Constraints context

- A JVM service with a memory `limit` of 512Mi and **no `request` set** (so it scheduled anywhere and was a first-eviction candidate under node pressure).
- The container's real working set under load was ~700Mi — above the limit — so the kubelet OOMKilled it (exit code 137 = 128 + SIGKILL/9).
- A `livenessProbe` with `initialDelaySeconds: 5` against an endpoint that wasn't ready until the JVM warmed up (~40s). On a cold start the liveness probe failed three times and the kubelet killed the container *before it ever became ready* — a self-inflicted CrashLoop independent of the OOM.
- No `startupProbe`, so liveness and readiness both raced the slow boot.

## Attempts

- Tried: bumping `replicas` from 3 to 8 to "absorb the crashes." More pods, same per-pod OOM + probe-kill — just more flapping pods and more node memory pressure. Scaling out doesn't fix a per-pod resource/probe bug.
- Tried: reading `kubectl describe pod`. The `Last State: Terminated, Reason: OOMKilled, Exit Code: 137` line named the memory bug; the `Events` showed `Liveness probe failed` + `Killing container` *before* readiness — naming the probe bug. **This is the diagnosis step that should come first.** [verify-at-use — exit 137 = SIGKILL, the OOMKill signature; confirm against the kubelet docs.]
- Tried (the fix that worked): (a) set `requests.memory: 768Mi` and `limits.memory: 1Gi` from the observed working set (request ≈ steady state, limit with headroom); (b) added a `startupProbe` with `failureThreshold: 30` + `periodSeconds: 5` (≈150s budget) so liveness doesn't arm until the app has actually booted; (c) raised `livenessProbe.initialDelaySeconds` is *not* the fix — the startupProbe is, because it gates liveness/readiness cleanly. Outcome: restarts went to zero and the cold-start no longer self-killed.

## Resolution

**`CrashLoopBackOff` is a symptom, not a diagnosis — `kubectl describe pod` + the container's `Last State`/exit code tells you which of several distinct causes you have.** The order:

1. **`kubectl describe pod <pod>`** — read `Last State` (Terminated reason + exit code) and the `Events`. Exit 137 = OOMKilled; exit 143 = SIGTERM (graceful, often a failed liveness probe); a non-zero app exit = the app itself crashed.
2. **OOMKilled?** The limit is below the real working set. Set `requests`/`limits` from observed usage (`kubectl top pod` or the metrics pipeline), request ≈ steady state, limit with headroom. Raising the limit is the fix; raising replicas is not.
3. **Killed by a probe before ready?** A slow boot needs a `startupProbe` so liveness/readiness don't race the warm-up. This is the single most common self-inflicted CrashLoop on JVM/large-runtime apps.
4. **App exited non-zero?** Now it's a dev-team bug — `kubectl logs --previous` on the crashed container shows the stack trace.

The trap is that the back-off + restart count are the *loud* symptom and look like "the app is broken," so the instinct is to scale out or restart the Deployment — neither touches the per-pod resource or probe bug, and scaling out makes node memory pressure worse.

**Action for the next engineer:** before paging the app team or scaling, run `kubectl describe pod` and read the exit code. Exit 137 → fix `requests`/`limits` from observed usage. Probe-kill-before-ready → add a `startupProbe`. Only a non-zero *app* exit is a code bug.

Cross-reference: this is the field-note complement to [`../best-practices/resource-requests-and-limits-are-mandatory.md`](../best-practices/resource-requests-and-limits-are-mandatory.md) and [`../best-practices/probes-are-mandatory.md`](../best-practices/probes-are-mandatory.md). The workload-resource-sizing tree in [`../knowledge/workload-resource-and-autoscaling-decision-trees.md`](../knowledge/workload-resource-and-autoscaling-decision-trees.md) walks the request/limit/QoS choice; the cluster-level metrics pipeline that surfaces the working set belongs to `observability-sre`.
