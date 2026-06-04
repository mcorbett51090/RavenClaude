# Google Cloud (GCP) Plugin — Team Constitution

> Team constitution for the `gcp-cloud` Claude Code plugin — **4** specialist agents for designing and operating Google Cloud well — the resource hierarchy and org policy, least-privilege IAM, VPC networking, the right compute (Cloud Run/GKE/Functions), and the data services (BigQuery, Pub/Sub) at a selection level. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`gcp-architect`](agents/gcp-architect.md) | GCP architecture and the resource hierarchy: organization/folders/projects layout, org policy constraints, region/zone design, service selection across the estate, and resilience posture | "design our GCP project structure", "how should we lay out folders/projects", "which GCP services for this", "set org policies" |
| [`gcp-iam-engineer`](agents/gcp-iam-engineer.md) | GCP identity and access: predefined/custom roles over primitive, service accounts + Workload Identity Federation (no key files), Workload Identity for GKE, IAM Conditions, and policy at the right hierarchy level | "write least-privilege GCP IAM", "we're using Owner everywhere", "stop exporting SA key files", "federate CI to GCP" |
| [`gcp-network-engineer`](agents/gcp-network-engineer.md) | GCP networking: VPC and Shared VPC design, firewall rules (default-deny + tags/SAs), Private Google Access, Private Service Connect, Cloud NAT, Cloud Load Balancing, and Cloud DNS | "design our VPC / Shared VPC", "is this firewall rule too open?", "make this private", "connect our projects' networks" |
| [`gcp-data-and-compute-engineer`](agents/gcp-data-and-compute-engineer.md) | Compute selection (Cloud Run / GKE / Cloud Functions / GCE) and the data services at a selection level: BigQuery (as a service), Pub/Sub event-driven integration, Cloud SQL/Spanner/Firestore choice, and autoscaling | "Cloud Run or GKE?", "how should this run on GCP?", "design our Pub/Sub flow", "which database — Cloud SQL, Spanner, Firestore?" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Use the resource hierarchy.** Organization → folders → projects is your blast-radius and policy boundary. A pile of unrelated resources in one project is GCP's version of one giant account.
2. **Predefined roles over primitive (Owner/Editor/Viewer).** Primitive roles are wildly over-broad; prefer predefined or custom roles scoped to the job. Owner on a project is rarely the right answer.
3. **No service-account key files.** Use Workload Identity Federation (and Workload Identity for GKE) — exported JSON keys are long-lived secrets that leak. Attach service accounts; don't download keys.
4. **Org policy constraints set guardrails.** Constrain allowed regions, disable SA key creation, enforce no-public-IP — preventive guardrails at the org/folder level beat per-project vigilance.
5. **Private by default.** Private Google Access, Private Service Connect, no public IPs on VMs unless required, firewall default-deny. Public exposure is an exception.
6. **Pick compute by operational burden.** Stateless containers/HTTP → Cloud Run; need k8s → GKE (Autopilot to cut ops); event functions → Cloud Functions; legacy → GCE. Cloud Run is the right default for most services.

## 3. Seams (the bridges to neighbouring plugins)

- **Multi-cloud / which-cloud and AWS/Azure equivalents** → `aws-cloud` / `azure-cloud` (reciprocal); this team owns GCP specifics.
- **BigQuery as the analytics warehouse (modeling, ELT, BI)** → `data-platform` (and `analytics-engineering` for dbt); we own BigQuery as a GCP *service* (IAM, slots, datasets), not the analytics modeling.
- **Provisioning as IaC** → `terraform-iac`.
- **Running on GKE (workload design, mesh)** → `cloud-native-kubernetes`; we own the cluster's GCP control plane + Workload Identity.
- **The security verdict on a posture finding** → `security-engineering/cloud-security-engineer` → `ravenclaude-core/security-reviewer`.
- **CI deploy via Workload Identity Federation to GCP** → `devops-cicd`.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.
