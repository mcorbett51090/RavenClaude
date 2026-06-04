# AWS Cloud

The **aws-cloud** plugin — designing and operating well-architected AWS — multi-account landing zones, least-privilege IAM, VPC networking, the right compute (Lambda/ECS/EKS/Fargate), event-driven integration, and observability + FinOps.

## Agents

- **`aws-architect`** — AWS architecture and the account strategy: Well-Architected trade-offs, multi-account landing zone (Organizations/Control Tower/SCPs), region/AZ design, service selection across the estate, and resilience/DR posture
- **`aws-iam-identity-engineer`** — AWS identity and access: least-privilege IAM policies, roles over keys, permission boundaries, SCPs, IAM Identity Center (SSO), cross-account access, IRSA for EKS, and OIDC federation for CI
- **`aws-network-engineer`** — AWS networking: VPC and subnet design, security groups vs NACLs, PrivateLink and VPC endpoints, Transit Gateway / peering, NAT and egress control, Route 53, and private-by-default connectivity
- **`aws-compute-platform-engineer`** — Compute selection and configuration: Lambda, ECS/Fargate, EKS, App Runner, EC2; the serverless-vs-containers-vs-VMs decision, autoscaling, and the data/integration services (RDS/DynamoDB/S3, SQS/SNS/EventBridge/Step Functions) at a selection level
- **`aws-ops-finops-engineer`** — Operations and cost: CloudWatch/X-Ray observability hooks, cost allocation tags, budgets and anomaly detection, rightsizing and Savings Plans/RIs, backup/DR operations, and Well-Architected operational excellence

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install aws-cloud@ravenclaude
```

## Seams

- **Multi-cloud / which-cloud and Azure/GCP equivalents** → `azure-cloud` / `gcp-cloud` (reciprocal); this team owns AWS specifics.
- **Provisioning all of this as IaC** → `terraform-iac` (modules/state/policy); Azure-native Bicep lives in `azure-cloud`.
- **Running workloads on EKS (manifests, mesh, workload design)** → `cloud-native-kubernetes`; we own the cluster's AWS control plane and IAM↔IRSA.
- **Telemetry design & SLOs over CloudWatch/X-Ray signals** → `observability-sre`.
- **The security verdict on a posture finding** → `security-engineering/cloud-security-engineer` → `ravenclaude-core/security-reviewer`.
- **CI deploy with OIDC federation to AWS** → `devops-cicd`.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
