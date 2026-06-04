# Cloud-Native & Kubernetes

The **cloud-native-kubernetes** plugin — running workloads on Kubernetes well — container build hygiene, workload and resource design, cluster platform operations, and service-mesh networking — cloud-agnostic, with the per-cloud control plane deferred to the cloud plugins.

## Agents

- **`kubernetes-architect`** — Workload and resource design: choosing the workload kind (Deployment/StatefulSet/DaemonSet/Job/CronJob), probes, requests/limits and QoS, autoscaling (HPA/VPA), PodDisruptionBudgets, and the Helm/Kustomize packaging shape
- **`container-build-engineer`** — Container image craft for Kubernetes: minimal multi-stage builds, distroless/non-root, image size and CVE surface reduction, OCI labels, and image-pull/registry configuration in-cluster
- **`k8s-platform-operator`** — Cluster platform operations: namespaces and multi-tenancy, RBAC, NetworkPolicies (default-deny), resource quotas and LimitRanges, admission control (policy), cluster/add-on upgrades, and capacity
- **`service-mesh-networking-engineer`** — In-cluster and edge networking: Ingress/Gateway API, service-mesh (mTLS, traffic-splitting for canary, retries/timeouts/circuit-breaking), east-west security, and mesh observability

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install cloud-native-kubernetes@ravenclaude
```

## Seams

- **The managed control plane (AKS / EKS / GKE), node pools, and cloud IAM↔cluster identity** → `azure-cloud` / `aws-cloud` / `gcp-cloud`; this team runs *workloads on* the cluster, cloud-agnostically.
- **GitOps reconcile of manifests/Helm into the cluster** → `devops-cicd/gitops-engineer` (Argo/Flux); we author the manifests, they reconcile them.
- **In-cluster telemetry, SLOs, and the metrics pipeline design** → `observability-sre`; we expose the signals, they decide the SLOs and alerts.
- **Image SBOM/provenance and CVE verdicts** → `devops-cicd/build-and-artifact-engineer` + `security-engineering`.
- **Provisioning the cluster + cloud resources via IaC** → `terraform-iac`; we consume what it stands up.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
