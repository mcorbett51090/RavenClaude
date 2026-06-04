# Cloud-Native & Kubernetes — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before choosing a workload kind or installing a mesh.

## Decision Tree: Which workload kind?

Most things are Deployments. Reach for StatefulSet only when identity/storage truly matters.

```mermaid
graph TD
  A[A workload] --> B{Runs to completion?}
  B -- Yes, once --> C[Job]
  B -- Yes, on a schedule --> D[CronJob]
  B -- No, long-running --> E{One per node needed?}
  E -- Yes --> F[DaemonSet]
  E -- No --> G{Needs stable identity / per-pod storage / ordered start?}
  G -- Yes --> H[StatefulSet - accept the complexity]
  G -- No --> I[Deployment - the default]
```

_Don't StatefulSet a stateless app; you'll pay for it forever._

## Decision Tree: Do we need a service mesh?

Ingress first. A mesh must earn its complexity.

```mermaid
graph TD
  A[Networking need] --> B{Just expose a service to clients?}
  B -- Yes --> C[Gateway API ingress - no mesh]
  B -- No --> D{Need mTLS for ALL east-west traffic?}
  D -- Yes --> E[Mesh justified]
  D -- No --> F{Need fine-grained traffic-splitting/canary across many services?}
  F -- Yes --> E
  F -- No --> G{Need per-call retries/timeouts/circuit-breaking mesh-wide?}
  G -- Yes --> E
  G -- No --> H[No mesh - use ingress + app-level resilience + NetworkPolicy]
```


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Gateway API | GA (replacing Ingress for new) | Role-oriented, expressive routing |
| HPA / VPA | GA | HPA on custom/external metrics; VPA for right-sizing |
| Pod Security Admission | GA (replaced PSP) | baseline/restricted profiles |
| OPA Gatekeeper / Kyverno | mature | policy-as-code admission |
| Istio / Linkerd | GA | mTLS, traffic-split; weigh sidecar cost (ambient mode emerging) |
| Distroless / minimal base images | mature | non-root, no shell; quiets CVE scans |
