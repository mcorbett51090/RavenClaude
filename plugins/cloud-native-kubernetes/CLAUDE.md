# Cloud-Native & Kubernetes Plugin — Team Constitution

> Team constitution for the `cloud-native-kubernetes` Claude Code plugin — **4** specialist agents for running workloads on Kubernetes well — container build hygiene, workload and resource design, cluster platform operations, and service-mesh networking — cloud-agnostic, with the per-cloud control plane deferred to the cloud plugins. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`kubernetes-architect`](agents/kubernetes-architect.md) | Workload and resource design: choosing the workload kind (Deployment/StatefulSet/DaemonSet/Job/CronJob), probes, requests/limits and QoS, autoscaling (HPA/VPA), PodDisruptionBudgets, and the Helm/Kustomize packaging shape | "how should this run on k8s?", "Deployment or StatefulSet?", "set resource requests/limits", "add autoscaling" |
| [`container-build-engineer`](agents/container-build-engineer.md) | Container image craft for Kubernetes: minimal multi-stage builds, distroless/non-root, image size and CVE surface reduction, OCI labels, and image-pull/registry configuration in-cluster | "our k8s images are huge/root", "build a Dockerfile for this", "reduce our image CVEs", "set up imagePullSecrets" |
| [`k8s-platform-operator`](agents/k8s-platform-operator.md) | Cluster platform operations: namespaces and multi-tenancy, RBAC, NetworkPolicies (default-deny), resource quotas and LimitRanges, admission control (policy), cluster/add-on upgrades, and capacity | "set up RBAC/namespaces", "lock down pod-to-pod traffic", "enforce resource quotas", "how do we upgrade the cluster safely" |
| [`service-mesh-networking-engineer`](agents/service-mesh-networking-engineer.md) | In-cluster and edge networking: Ingress/Gateway API, service-mesh (mTLS, traffic-splitting for canary, retries/timeouts/circuit-breaking), east-west security, and mesh observability | "set up ingress", "do we need a service mesh?", "mTLS between services", "traffic-split for a canary" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Set requests AND limits — and know the difference.** Requests schedule; limits cap. No requests means the scheduler is guessing and your pod is the noisy neighbor or the one that gets evicted.
2. **Probes are not optional.** Liveness restarts a hung pod; readiness gates traffic; startup protects slow boots. Missing/incorrect probes cause both phantom outages and traffic to dead pods.
3. **Least privilege in the cluster too.** Namespaced RBAC, no cluster-admin for workloads, default-deny NetworkPolicies, no privileged/root containers. A pod is a tenant; treat it like one.
4. **Stateless by default; state is a deliberate StatefulSet.** Most workloads are Deployments. Reach for StatefulSet only when stable identity/storage truly matters, and know what you're signing up for.
5. **Pin and declare everything.** Image digests, chart versions, API versions. `latest` and unpinned charts make a cluster un-reproducible and upgrades terrifying.
6. **The cluster is cattle; GitOps is the herd.** Desired state lives in Git and a reconciler enforces it (devops-cicd). A `kubectl edit` in prod is drift.

## 3. Seams (the bridges to neighbouring plugins)

- **The managed control plane (AKS / EKS / GKE), node pools, and cloud IAM↔cluster identity** → `azure-cloud` / `aws-cloud` / `gcp-cloud`; this team runs *workloads on* the cluster, cloud-agnostically.
- **GitOps reconcile of manifests/Helm into the cluster** → `devops-cicd/gitops-engineer` (Argo/Flux); we author the manifests, they reconcile them.
- **In-cluster telemetry, SLOs, and the metrics pipeline design** → `observability-sre`; we expose the signals, they decide the SLOs and alerts.
- **Image SBOM/provenance and CVE verdicts** → `devops-cicd/build-and-artifact-engineer` + `security-engineering`.
- **Provisioning the cluster + cloud resources via IaC** → `terraform-iac`; we consume what it stands up.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.
