# Configure HPA with scale-down stabilization to prevent flapping

**Status:** Pattern
**Domain:** Kubernetes / autoscaling
**Applies to:** `cloud-native-kubernetes`

---

## Why this exists

A Horizontal Pod Autoscaler without a stabilization window reacts to every CPU/memory spike by adding pods and every quiet period by removing them — producing a "flapping" pattern where pods are constantly added and removed. This causes rolling disruptions, eviction of cached state, and repeated cold starts. The scale-down stabilization window (`scaleDown.stabilizationWindowSeconds`) tells the HPA to wait before scaling down, averaging out transient load dips. Scale-up can be aggressive (fast response to load); scale-down should be conservative (avoid removing pods before the next spike).

## How to apply

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60   # target 60% CPU — gives headroom before saturation
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 70
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30   # fast scale-up: react within 30s
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60   # can double in 60s
    scaleDown:
      stabilizationWindowSeconds: 300   # wait 5 minutes of sustained low load before scaling down
      policies:
        - type: Percent
          value: 20
          periodSeconds: 60   # remove at most 20% of pods per minute
```

**Do:**
- Set `minReplicas >= 2` for any service that needs HA — HPA can scale to 1 without a minimum floor.
- Set CPU target at 60–70% utilization, not 80–90% — give headroom for spikes before the scaler reacts.
- Use custom metrics (requests per second, queue depth) for application-aware scaling via KEDA or the custom metrics API.
- Add a `PodDisruptionBudget` alongside HPA — see the `pdb-with-every-rollout` rule.

**Don't:**
- Set `stabilizationWindowSeconds: 0` for scale-down — it makes flapping worse.
- Rely solely on CPU for services with I/O-bound work — CPU stays low while response time degrades.
- Set `maxReplicas` without considering cluster node capacity — HPA can request more pods than the cluster can schedule.

## Edge cases / when the rule does NOT apply

- **Scale-to-zero** (minReplicas = 0): use KEDA for event-driven scale-to-zero rather than HPA — native HPA does not scale to zero.
- **Stateful workloads**: HPA does not apply to StatefulSets in the same way; use it carefully and only for stateless aspects of a StatefulSet.

## See also

- [`../agents/kubernetes-architect.md`](../agents/kubernetes-architect.md) — owns HPA configuration, probes, and resource design.
- [`./set-requests-and-limits.md`](./set-requests-and-limits.md) — HPA requires accurate resource requests to compute utilization percentages correctly.
- [`./pdb-with-every-rollout.md`](./pdb-with-every-rollout.md) — HPA scale-down must respect PDB min-available constraints.

## Provenance

Codifies the `kubernetes-architect` remit from `CLAUDE.md` §1: "autoscaling (HPA/VPA)." The stabilization window behavior is documented in the Kubernetes HPA documentation (autoscaling/v2 API). Standard k8s production readiness pattern.

---

_Last reviewed: 2026-06-05 by `claude`_
