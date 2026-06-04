# Google Cloud (GCP)

The **gcp-cloud** plugin — designing and operating Google Cloud well — the resource hierarchy and org policy, least-privilege IAM, VPC networking, the right compute (Cloud Run/GKE/Functions), and the data services (BigQuery, Pub/Sub) at a selection level.

## Agents

- **`gcp-architect`** — GCP architecture and the resource hierarchy: organization/folders/projects layout, org policy constraints, region/zone design, service selection across the estate, and resilience posture
- **`gcp-iam-engineer`** — GCP identity and access: predefined/custom roles over primitive, service accounts + Workload Identity Federation (no key files), Workload Identity for GKE, IAM Conditions, and policy at the right hierarchy level
- **`gcp-network-engineer`** — GCP networking: VPC and Shared VPC design, firewall rules (default-deny + tags/SAs), Private Google Access, Private Service Connect, Cloud NAT, Cloud Load Balancing, and Cloud DNS
- **`gcp-data-and-compute-engineer`** — Compute selection (Cloud Run / GKE / Cloud Functions / GCE) and the data services at a selection level: BigQuery (as a service), Pub/Sub event-driven integration, Cloud SQL/Spanner/Firestore choice, and autoscaling

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install gcp-cloud@ravenclaude
```

## Seams

- **Multi-cloud / which-cloud and AWS/Azure equivalents** → `aws-cloud` / `azure-cloud` (reciprocal); this team owns GCP specifics.
- **BigQuery as the analytics warehouse (modeling, ELT, BI)** → `data-platform` (and `analytics-engineering` for dbt); we own BigQuery as a GCP *service* (IAM, slots, datasets), not the analytics modeling.
- **Provisioning as IaC** → `terraform-iac`.
- **Running on GKE (workload design, mesh)** → `cloud-native-kubernetes`; we own the cluster's GCP control plane + Workload Identity.
- **The security verdict on a posture finding** → `security-engineering/cloud-security-engineer` → `ravenclaude-core/security-reviewer`.
- **CI deploy via Workload Identity Federation to GCP** → `devops-cicd`.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
