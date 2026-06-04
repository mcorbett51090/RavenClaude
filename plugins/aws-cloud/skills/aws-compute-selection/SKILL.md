---
name: aws-compute-selection
description: "Choose AWS compute by workload shape and operational burden: Lambda (event/spiky), Fargate/App Runner (containers, no cluster ops), EKS (k8s/portability), EC2 (legacy/specific); design event-driven integration with idempotency and DLQs."
---

# AWS Compute Selection

| Workload | Compute |
|---|---|
| Event / spiky / short | **Lambda** |
| Long-running container, no cluster ops | **Fargate / App Runner** |
| Need k8s / portability | **EKS** |
| Legacy / specific OS | **EC2** |

Match the shape; don't default to one. Serverless-first for variable load (mind cold starts + limits).

## Integration
SQS (decouple), SNS/EventBridge (fan-out/route), **Step Functions** (orchestrate w/ retries). Every async consumer is **idempotent** + has a **DLQ**. No hand-rolled queues/pollers.
