# AWS Cloud — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before choosing compute or an account layout.

## Decision Tree: AWS compute selection

Pick by workload shape and operational burden, not familiarity.

```mermaid
graph TD
  A[A workload] --> B{Event-driven / spiky / short-lived?}
  B -- Yes --> C{Fits 15-min + memory limits?}
  C -- Yes --> D[Lambda]
  C -- No --> E[Fargate / Step Functions]
  B -- No, long-running --> F{Containerized?}
  F -- No --> G{Legacy / specific OS/kernel?}
  G -- Yes --> H[EC2]
  G -- No --> D
  F -- Yes --> I{Need k8s / multi-cloud portability?}
  I -- Yes --> J[EKS -> cloud-native-kubernetes]
  I -- No --> K[Fargate / App Runner]
```

_Don't run EKS to host one container._

## Decision Tree: How many AWS accounts?

Separate by blast radius and billing, governed by Organizations + SCPs.

```mermaid
graph TD
  A[Estate] --> B{More than a single small app?}
  B -- No --> C[One account, tag well - revisit soon]
  B -- Yes --> D[Organizations + separate accounts]
  D --> E[prod]
  D --> F[non-prod/dev]
  D --> G[security/log-archive]
  D --> H[shared-services/network]
  E --> I{Want managed guardrails?}
  I -- Yes --> J[Control Tower + SCPs]
  I -- No --> K[Org + hand-rolled SCPs]
```

## Decision Tree: Which AWS database service?

Pick by data model and access pattern, not by what the team last used.

```mermaid
graph TD
  A[Data need] --> B{Relational / need joins + transactions?}
  B -- No --> C{Key-value / document, predictable access, huge scale?}
  C -- Yes --> D[DynamoDB - design the keys first]
  C -- No, analytics/warehouse --> E[Redshift / Athena-on-S3 -> data-platform]
  B -- Yes --> F{Want cloud-native HA + autoscaling storage?}
  F -- Yes --> G{Need MySQL/PostgreSQL compatibility?}
  G -- Yes --> H[Aurora]
  G -- No, other engine --> I[RDS for that engine]
  F -- No, simplest managed --> I
  H --> J{Spiky/intermittent load?}
  J -- Yes --> K[Aurora Serverless v2]
```

_DynamoDB rewards key design and punishes relational habits; don't pick it to avoid running a database, pick it for its access pattern._

## Decision Tree: How to connect VPCs/accounts?

Few VPCs peer; many VPCs route through a hub; single-service exposure uses PrivateLink.

```mermaid
graph TD
  A[Connect networks] --> B{Just expose ONE service to consumers?}
  B -- Yes --> C[PrivateLink endpoint service - no network merge]
  B -- No, full network reachability --> D{Only 2-3 VPCs, simple, no transitivity?}
  D -- Yes --> E[VPC peering]
  D -- No, many VPCs / hub-and-spoke / transitive --> F[Transit Gateway]
  F --> G{Connect on-prem too?}
  G -- Yes --> H[TGW + Direct Connect / VPN attachment]
  E --> I{Overlapping CIDRs?}
  I -- Yes --> C
```

_Peering is a full mesh that doesn't scale and isn't transitive; reach for Transit Gateway before the mesh gets ugly, and PrivateLink when you want exposure without merging networks._

## Decision Tree: How to expose a workload to the internet?

Public exposure is an explicit decision; pick the front door by protocol and need.

```mermaid
graph TD
  A[Expose a workload] --> B{Static assets / SPA?}
  B -- Yes --> C[S3 + CloudFront]
  B -- No --> D{HTTP/HTTPS app?}
  D -- Yes --> E{Need global edge + caching / DDoS posture?}
  E -- Yes --> F[CloudFront -> ALB]
  E -- No --> G[ALB in public subnet, targets in private]
  D -- No, TCP/UDP / ultra-low-latency --> H[NLB]
  F --> I[WAF + ACM TLS]
  G --> I
```

_The workload stays in a private subnet; only the load balancer (or CloudFront) lives at the edge. Public reachability is reviewed, never a default._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Organizations + Control Tower | GA | Landing zone + guardrails |
| IAM Identity Center (SSO) | GA | Federate humans; no IAM users |
| IRSA / EKS Pod Identity | GA | Pod-level IAM without node keys |
| OIDC federation for CI | GA | Replace long-lived keys |
| Lambda (limits) | 15-min max, mem-bound | Verify limits before designing |
| EventBridge / Step Functions | GA | Event routing + orchestration |
| Savings Plans / RIs | GA | Rightsize FIRST |
| Graviton (Arm) instances | GA — Graviton5 / EC2 M9g, M9gd GA 2026-06-10 | Prefer Arm for price-performance where the runtime/deps support Arm64; up to ~25% compute gain vs Graviton4. [AWS what's-new](https://aws.amazon.com/about-aws/whats-new/2026/06/ec2-m9g-m9gd-instances-graviton5-processors-available/) |

---

## Decision Tree: AWS IAM — role, federated identity, or long-lived key?

**When this applies:** A workload, a CI/CD pipeline, or a human needs AWS credentials. The observable inputs are: what is the caller (EC2 instance, ECS task, Lambda, Kubernetes pod, GitHub Actions runner, human developer), and where does it run. The goal is the shortest-lived credential possible for the job.

**Last verified:** 2026-06-05 against AWS IAM documentation and IRSA/Pod Identity GA release notes.

```mermaid
flowchart TD
    START[Caller needs AWS credentials] --> H{Is the caller a human?}
    H -->|Yes| SSO[IAM Identity Center - federated SSO<br/>short-lived session, no IAM user]
    H -->|No, workload| W{Where does it run?}
    W -->|EC2 instance| IR[Instance profile - IAM role attached to instance]
    W -->|ECS task| TR[Task role - IRSA equivalent for ECS]
    W -->|Lambda| LR[Execution role - attached to function]
    W -->|EKS pod| EKS{EKS Pod Identity or IRSA available?}
    EKS -->|Yes - prefer Pod Identity GA| PI[EKS Pod Identity - pod-level role binding]
    EKS -->|Legacy - IRSA still valid| IRSA[IRSA - SA annotation + OIDC provider]
    W -->|CI runner - GitHub/GitLab/CircleCI| OIDC[OIDC federation - no long-lived key]
    W -->|On-prem or non-AWS runtime| KEY{No other option?}
    KEY -->|Yes - last resort| LK[IAM user + access key - rotate every 90 days, audit use]
    KEY -->|No| OIDC
```

**Rationale per leaf:**
- *IAM Identity Center* — humans must authenticate via SSO so credentials expire with the session and access is centrally revocable.
- *Instance profile* — the EC2 metadata service provides rotating credentials without any key to store.
- *Task role* — ECS tasks inherit a role bound at the task definition level, not the host.
- *Execution role* — Lambda functions get temporary credentials via the execution role without any key.
- *EKS Pod Identity* — the GA successor to IRSA; binds a role to a service account without an OIDC provider per cluster.
- *IRSA* — still valid where Pod Identity is not yet available; the cluster OIDC provider issues pod-scoped credentials.
- *OIDC federation* — CI systems (GitHub Actions, GitLab, CircleCI) can exchange a workflow token for short-lived AWS credentials via AssumeRoleWithWebIdentity.
- *IAM user + access key* — last resort only; a long-lived key is a leak risk and must be rotated and monitored.

**Tradeoffs summary:**

| Method | Credential lifetime | Rotation needed? | Approval gate? | Use when |
|---|---|---|---|---|
| IAM Identity Center | Session-scoped (hours) | No | SSO IdP | Human access |
| Instance / Task / Lambda role | Auto-rotated (minutes) | No | IaC PR review | AWS-native workload |
| EKS Pod Identity | Auto-rotated | No | IaC PR review | EKS pods - GA preferred |
| IRSA | Auto-rotated | No | IaC PR review | EKS pods - OIDC provider |
| OIDC federation | Workflow-scoped | No | Pipeline config | CI/CD runners |
| IAM user + key | Long-lived (permanent until rotated) | Yes - every 90 days | Security review | Last resort only |

---

## Decision Tree: AWS storage — S3, EFS, EBS, or FSx?

**When this applies:** A workload needs persistent storage. The observable inputs are: does data need to be shared across instances/tasks, is it block-level or object-level, is it file-system POSIX semantics, and what are the throughput/latency constraints.

**Last verified:** 2026-06-05 against AWS storage service documentation.

```mermaid
flowchart TD
    START[Workload needs storage] --> OBJ{Object storage - arbitrary files, HTTP GET/PUT, no filesystem?}
    OBJ -->|Yes| S3[S3 - object store<br/>versioning, lifecycle, replication]
    OBJ -->|No, filesystem semantics needed| SHARE{Shared across multiple instances/tasks?}
    SHARE -->|Yes| POSIX{Need POSIX compliance - Linux FS?}
    POSIX -->|Yes| EFS[EFS - POSIX shared filesystem<br/>auto-scaling throughput]
    POSIX -->|No, Windows SMB| FSX[FSx for Windows File Server]
    SHARE -->|No, single instance/task| LATENCY{Need sub-millisecond block IO - databases, boot?}
    LATENCY -->|Yes| EBS[EBS - block device<br/>gp3 default, io2 for high-IOPS DB]
    LATENCY -->|No, high-throughput HPC/ML| FXLFS[FSx for Lustre - HPC parallel filesystem]
```

**Rationale per leaf:**
- *S3* — the default for any object or file that does not need a filesystem mount; scales to any size, cheapest per GB, native lifecycle policies.
- *EFS* — POSIX-compliant, multi-AZ, shared filesystem for multi-instance workloads (web farms, CMS media, home directories); throughput scales automatically.
- *FSx for Windows File Server* — Windows SMB shares (Active Directory integrated) for Windows workloads.
- *EBS (gp3)* — the default block device for single-instance workloads; detach/reattach to a new instance; `gp3` gives baseline 3000 IOPS at any size.
- *EBS (io2)* — provisioned IOPS for high-performance databases where IOPS/throughput must be predictable.
- *FSx for Lustre* — HPC and ML training workloads needing parallel high-throughput filesystem at petabyte scale.

**Tradeoffs summary:**

| Method | Access model | Multi-attach | Cost tier | Use when |
|---|---|---|---|---|
| S3 | Object / HTTP | Yes - unlimited | Lowest per GB | Files, backups, static assets, data lake |
| EFS | POSIX / NFS | Yes - multi-AZ | Mid - pay per GB used | Shared Linux filesystem across instances |
| FSx Windows | SMB | Yes - multi-AZ | Higher | Windows SMB shares |
| EBS gp3 | Block | No - single instance | Low | Single-instance OS, data, app storage |
| EBS io2 | Block | Limited multi-attach | Higher | High-IOPS database volumes |
| FSx Lustre | Parallel FS | Yes | High | HPC / ML training workloads |

---

## Decision Tree: AWS security finding — remediate now or accept risk?

**When this applies:** A Security Hub finding, GuardDuty alert, or Trusted Advisor recommendation surfaces a security issue. The observable inputs are: the severity (Critical/High/Medium/Low), whether it is a preventive or detective control gap, and whether the resource is in production.

**Last verified:** 2026-06-05 against AWS Security Hub finding severity definitions.

```mermaid
flowchart TD
    START[Security finding arrives] --> SEV{Severity?}
    SEV -->|Critical or High| PROD{Is affected resource in production?}
    PROD -->|Yes| IMM[Immediate remediation - open P1 incident<br/>isolate if active exploit suspected]
    PROD -->|No - dev/sandbox| FAST[Remediate within 24 hours<br/>block promotion to prod until fixed]
    SEV -->|Medium| TYPE{Preventive control gap or detective gap?}
    TYPE -->|Preventive - config allows an attack| PLAN[Remediate in next sprint - create tracked ticket]
    TYPE -->|Detective - no alerting on an event| ALERT[Add alarm or log query - schedule within 2 weeks]
    SEV -->|Low or Informational| ACCEPT{Accepted risk with documented rationale?}
    ACCEPT -->|Yes - suppressed with reason| SUPP[Suppress in Security Hub with reason + owner + review date]
    ACCEPT -->|No| BACKLOG[Add to security backlog - review in quarterly sweep]
```

**Rationale per leaf:**
- *Immediate remediation* — Critical/High on a prod resource means the blast radius is live; treat it as an incident.
- *Remediate within 24 hours* — the same finding in non-prod must be fixed before the next production promotion to prevent the pattern from shipping.
- *Remediate in next sprint* — Medium preventive gaps close an attack surface; they are urgent but not incident-level.
- *Add alarm or log query* — a detective gap means you are blind to a class of events; close within two weeks.
- *Suppress with reason* — some findings are accepted design choices (e.g., public bucket for a static website); document it so future sweeps don't re-open it blindly.
- *Security backlog* — Low findings are real but low-urgency; a quarterly review prevents them from accumulating forever.

**Tradeoffs summary:**

| Method | Response time | Owner | Use when |
|---|---|---|---|
| Immediate P1 remediation | Now | On-call + security team | Critical/High on prod |
| Remediate within 24 hours | 24 hours | Service owner | Critical/High on non-prod |
| Next sprint | 2 weeks | Service owner | Medium preventive gap |
| Add alarm | 2 weeks | Ops/SRE | Medium detective gap |
| Suppress with rationale | Document before suppressing | Security team approval | Accepted by design |
| Security backlog | Quarterly review | Security team | Low or informational |
