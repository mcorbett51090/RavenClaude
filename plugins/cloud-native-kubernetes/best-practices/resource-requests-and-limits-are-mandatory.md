# Set resource requests and limits on every container

**Status:** Absolute rule
**Domain:** Kubernetes workload reliability
**Applies to:** `cloud-native-kubernetes`

---

## Why this exists

A container with no `requests` is invisible to the scheduler — it gets bin-packed onto a node the
scheduler believes is empty, then competes for CPU and memory it was never guaranteed. A container
with no memory `limits` can consume the whole node and trigger the kernel OOM killer against its
neighbours. The pod's Quality-of-Service class — `Guaranteed`, `Burstable`, or `BestEffort` — is
derived entirely from how requests and limits are set, and that class decides who gets evicted
first under node pressure. Shipping workloads without them is how a single noisy pod takes down
unrelated services on the same node.

## How to apply

Set `requests` from observed usage (the floor the scheduler reserves) and `limits` as a guardrail
against runaway consumption:

```yaml
resources:
  requests:
    cpu: "100m" # scheduler reserves this; size from p50 observed usage
    memory: "256Mi" # memory request == limit -> avoids OOM surprises
  limits:
    cpu: "500m" # burst ceiling; omitting it allows bursting but risks noisy-neighbour
    memory: "256Mi" # ALWAYS set a memory limit; memory is incompressible
```

**Do:**

- Always set a **memory limit** — memory is incompressible, so an unbounded container is a node-wide risk.
- Set `requests == limits` for memory to land predictable `Guaranteed`/`Burstable` QoS.
- Size requests from real metrics (VPA in recommendation mode, or `kubectl top`), not guesses.
- Enforce presence with a `LimitRange` per namespace and an admission policy that rejects pods missing them.

**Don't:**

- Set a CPU limit so low the app is throttled into latency spikes — CPU is compressible; throttling is silent.
- Copy requests/limits between environments without re-checking; prod traffic shapes differ from staging.

## Edge cases / when the rule does NOT apply

- **Short-lived batch / Jobs** can run `BestEffort` if eviction on contention is acceptable — but still cap memory.
- **CPU limits are debatable**: many teams set CPU requests only (to avoid throttling) and rely on requests + node headroom. Memory limits are never optional.
- **System DaemonSets** tuned by the platform team may intentionally use different ratios — that is a deliberate, documented exception.

## See also

- [`../agents/k8s-platform-operator.md`](../agents/k8s-platform-operator.md) — owns node pressure, eviction, and capacity.
- [`./hpa-with-scale-stabilization.md`](./hpa-with-scale-stabilization.md) — HPA scales on utilization relative to requests, so requests must be right first.

## Provenance

Codifies core Kubernetes scheduling/QoS mechanics and the `kubernetes-architect` / `k8s-platform-operator`
discipline that noisy-neighbour incidents trace back to missing requests/limits.

---

_Last reviewed: 2026-06-05 by `claude`_
