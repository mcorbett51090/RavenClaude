---
name: ingress-and-mesh
description: "Design cluster networking: Gateway API ingress for north-south, and a service mesh ONLY when it earns its complexity (mTLS-everywhere, traffic-splitting, per-call resilience). Wire mTLS, weighted canary routing, and resilience deliberately."
---

# Ingress & Service Mesh

## Start with ingress
Gateway API for north-south + TLS. The cloud LB sits behind it (cloud plugin).

## Mesh: only if it earns it
Add a mesh for **mTLS-everywhere**, **traffic-splitting** (canary), or **per-call resilience** across many services. It costs latency + memory + ops. Name the capability you're buying.

## Once meshed
- **mTLS** east-west by default (+ NetworkPolicy = defense in depth)
- **weighted routing** for canary (promotion signal -> observability-sre; rollout -> devops-cicd)
- timeouts, retries (**idempotent only**), circuit-breaking — set deliberately
