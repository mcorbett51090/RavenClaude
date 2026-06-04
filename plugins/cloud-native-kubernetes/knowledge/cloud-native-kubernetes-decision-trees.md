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

## Decision Tree: Where do secrets come from?

A Secret object is base64 in etcd, not a vault. Decide the source before you write the manifest.

```mermaid
graph TD
  A[Workload needs a secret] --> B{Is it a credential for a cloud API?}
  B -- Yes --> C[Use workload identity - no stored secret at all]
  B -- No --> D{Have an external secret manager?}
  D -- Yes --> E{Want the manager to stay the source of truth?}
  E -- Yes --> F[Secrets Store CSI driver - mount at runtime]
  E -- No, sync into k8s --> G[External Secrets Operator]
  D -- No --> H[Native Secret + etcd encryption-at-rest + tight RBAC]
  H --> I[Mount as file, not env var]
  F --> I
  G --> I
```

_A secret committed in a manifest is already compromised — never the answer._

## Decision Tree: How to expose / route a service

North-south is Gateway API; a mesh is for east-west, and earns its cost separately.

```mermaid
graph TD
  A[Need to route traffic] --> B{North-south - clients reaching the service?}
  B -- Yes --> C{Need expressive routing / multi-team / TLS termination?}
  C -- Yes --> D[Gateway API]
  C -- No, trivial --> E[Service of type LoadBalancer or simple Ingress]
  B -- No, east-west service-to-service --> F{Need mTLS / traffic-split / per-call resilience across many services?}
  F -- No --> G[Plain Service + NetworkPolicy - no mesh]
  F -- Yes --> H[Mesh - see the mesh-justification tree]
```

_Gateway API is the successor to Ingress for new edge routing; a mesh is an east-west tool, not an ingress replacement._

## Decision Tree: How hard is the tenant isolation?

A namespace is a soft boundary. Match the mechanism to the trust level.

```mermaid
graph TD
  A[Multiple tenants on k8s] --> B{Tenants mutually trusted - same org/team?}
  B -- Yes --> C[Namespace per tenant: RBAC + Quota + LimitRange + default-deny NetworkPolicy]
  B -- No, untrusted / adversarial --> D{Can accept node-level isolation?}
  D -- Yes --> E[Dedicated node pools + taints + RuntimeClass sandbox]
  D -- No, need strong isolation --> F[Separate clusters per tenant]
  C --> G{Hostile-workload risk within the namespace?}
  G -- Yes --> E
```

_A namespace shares a kernel and nodes; it is not a security boundary against a hostile tenant._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Gateway API | GA (replacing Ingress for new) | Role-oriented, expressive routing |
| HPA / VPA | GA | HPA on custom/external metrics; VPA for right-sizing |
| Pod Security Admission | GA (replaced PSP) | baseline/restricted profiles |
| OPA Gatekeeper / Kyverno | mature | policy-as-code admission |
| Istio / Linkerd | GA | mTLS, traffic-split; weigh sidecar cost (ambient mode emerging) |
| Distroless / minimal base images | mature | non-root, no shell; quiets CVE scans |
