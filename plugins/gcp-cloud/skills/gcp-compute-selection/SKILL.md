---
name: gcp-compute-selection
description: "Choose GCP compute by operational burden: Cloud Run (default for stateless containers/HTTP, scale-to-zero), GKE/Autopilot (k8s/portability), Cloud Functions (small event handlers), GCE (legacy); design Pub/Sub integration with idempotency + dead-letter topics."
---

# GCP Compute Selection

| Workload | Compute |
|---|---|
| Stateless container / HTTP (most services) | **Cloud Run** (default) |
| Need k8s / portability | **GKE** (Autopilot to cut ops) |
| Small event handler | **Cloud Functions** |
| Legacy / specific OS | **GCE** |

Cloud Run is the right default; reach for GKE only when k8s genuinely earns it.

## Integration
**Pub/Sub** to decouple; consumers **idempotent** + **dead-letter topic**. No hand-rolled queues.
