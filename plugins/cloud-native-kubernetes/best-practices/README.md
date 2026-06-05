# cloud-native-kubernetes — best-practice docs

Named, citable rules for the `cloud-native-kubernetes` plugin's specialists. Each file is **one rule**, grounded in this plugin's house opinions ([`../CLAUDE.md`](../CLAUDE.md)) and the decision trees in [`../knowledge/cloud-native-kubernetes-decision-trees.md`](../knowledge/cloud-native-kubernetes-decision-trees.md). Read a doc whole and cite it; don't paraphrase a fragment.

---

## Index

_22 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`admission-control-over-manual-review.md`](./admission-control-over-manual-review.md) | Pattern | Enforcing cluster policies — admission controllers catch violations before they land |
| [`cluster-upgrade-strategy.md`](./cluster-upgrade-strategy.md) | Pattern | Upgrading a Kubernetes cluster — upgrade one minor version at a time |
| [`distroless-base-images.md`](./distroless-base-images.md) | Pattern | Building container images — use distroless/minimal to reduce CVE surface |
| [`gateway-api-for-new-ingress.md`](./gateway-api-for-new-ingress.md) | Pattern | Designing ingress for a new workload — use Gateway API, not the Ingress resource |
| [`helm-chart-values-per-environment.md`](./helm-chart-values-per-environment.md) | Pattern | Packaging with Helm — safe dev defaults in values.yaml, prod overrides separate |
| [`hpa-with-scale-stabilization.md`](./hpa-with-scale-stabilization.md) | Pattern | Configuring autoscaling — add scale-down stabilization to prevent pod flapping |
| [`image-pull-policy-never-always.md`](./image-pull-policy-never-always.md) | Absolute rule | Writing a pod spec — never use mutable tags; use immutable tags with IfNotPresent |
| [`resource-requests-and-limits-are-mandatory.md`](./resource-requests-and-limits-are-mandatory.md) | Absolute rule | Writing a container spec — set requests/limits so the scheduler and QoS class behave; always cap memory |
| [`least-privilege-in-cluster.md`](./least-privilege-in-cluster.md) | Absolute rule | Any RBAC grant or pod security context — minimize permissions, deny by default |
| [`mesh-must-earn-its-complexity.md`](./mesh-must-earn-its-complexity.md) | Pattern | Deciding whether to install a service mesh — justify the overhead before adding it |
| [`namespaces-are-the-tenancy-boundary.md`](./namespaces-are-the-tenancy-boundary.md) | Pattern | Multi-team cluster — use namespaces with RBAC, quotas, and network policies |
| [`network-policy-default-deny.md`](./network-policy-default-deny.md) | Absolute rule | Any production namespace — apply default-deny NetworkPolicy before allow rules |
| [`node-pools-taints-and-affinity.md`](./node-pools-taints-and-affinity.md) | Pattern | Managing multiple node pools — use taints/tolerations and affinity to schedule workloads |
| [`pdb-with-every-rollout.md`](./pdb-with-every-rollout.md) | Pattern | Any Deployment with replicas > 1 — PDB ensures HA during voluntary disruptions |
| [`pin-everything.md`](./pin-everything.md) | Absolute rule | Any manifest or chart — pin image digests, chart versions, and API versions |
| [`pod-security-admission-restricted.md`](./pod-security-admission-restricted.md) | Pattern | Any production namespace — enforce restricted PSA profile to harden pod security |
| [`probes-are-mandatory.md`](./probes-are-mandatory.md) | Absolute rule | Any pod spec — liveness, readiness, and startup probes are not optional |
| [`quotas-and-limitranges-per-namespace.md`](./quotas-and-limitranges-per-namespace.md) | Pattern | Multi-tenant cluster — set ResourceQuota and LimitRange per namespace |
| [`set-requests-and-limits.md`](./set-requests-and-limits.md) | Absolute rule | Any container spec — set CPU/memory requests and limits on every container |
| [`sidecar-or-ambient-mesh-decision.md`](./sidecar-or-ambient-mesh-decision.md) | Primary diagnostic | Installing a service mesh — choose sidecar vs ambient mode deliberately |
| [`stateless-by-default.md`](./stateless-by-default.md) | Pattern | Choosing a workload kind — Deployments for stateless; StatefulSets only when needed |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution + the house opinions these docs codify.
- [`../knowledge/cloud-native-kubernetes-decision-trees.md`](../knowledge/cloud-native-kubernetes-decision-trees.md) — decision trees for workload kind, mesh justification, secrets, routing, tenant isolation, container images, and autoscaling.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
