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
