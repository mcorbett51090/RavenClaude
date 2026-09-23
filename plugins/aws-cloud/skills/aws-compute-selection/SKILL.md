---
name: aws-compute-selection
description: "Choose AWS compute by workload shape and operational burden: Lambda (event/spiky), Fargate/ECS Express Mode (containers, no cluster ops), EKS (k8s/portability), EC2 (legacy/specific); design event-driven integration with idempotency and DLQs."
---

# AWS Compute Selection

| Workload | Compute |
|---|---|
| Event / spiky / short | **Lambda** |
| Long-running container, no cluster ops | **Fargate / ECS Express Mode** |
| Need k8s / portability | **EKS** |
| Legacy / specific OS | **EC2** |

Match the shape; don't default to one. Serverless-first for variable load (mind cold starts + limits). App Runner is closed to new customers since 2026-04-30 (maintenance mode); ECS Express Mode (GA re:Invent 2025) is AWS's recommended replacement, though it has no scale-to-zero.

## Integration
SQS (decouple), SNS/EventBridge (fan-out/route), **Step Functions** (orchestrate w/ retries). Every async consumer is **idempotent** + has a **DLQ**. No hand-rolled queues/pollers.
