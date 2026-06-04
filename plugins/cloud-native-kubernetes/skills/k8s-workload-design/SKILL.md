---
name: k8s-workload-design
description: "Design a Kubernetes workload: choose the workload kind by statefulness, set the three probe types correctly, requests/limits with the resulting QoS class, HPA/VPA on a load-tracking signal, and a PodDisruptionBudget."
---

# Kubernetes Workload Design

## Workload kind
| Need | Kind |
|---|---|
| Stateless web/API | **Deployment** |
| Stable identity/storage | **StatefulSet** |
| One per node | **DaemonSet** |
| Run to completion | **Job / CronJob** |

## Probes
- **liveness**: restart if hung
- **readiness**: gate traffic
- **startup**: protect slow boot

## Resources
Requests **schedule**, limits **cap**. Set both -> know your QoS (Guaranteed/Burstable/BestEffort).

## Scale & disruption
HPA on a load-tracking signal (often custom/external, not bare CPU) + a **PodDisruptionBudget** + graceful shutdown (preStop + grace).
