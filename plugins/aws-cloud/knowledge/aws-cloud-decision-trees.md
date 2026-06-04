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
