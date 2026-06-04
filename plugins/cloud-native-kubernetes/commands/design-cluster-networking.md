---
description: "Design ingress and decide on a service mesh; wire mTLS, canary traffic-splitting, and resilience if a mesh is justified."
argument-hint: "[north-south + east-west needs]"
---

You are running `/cloud-native-kubernetes:design-cluster-networking`. Use `service-mesh-networking-engineer` + the `ingress-and-mesh` skill.

## Steps
1. Design Gateway API ingress + TLS.
2. Traverse the mesh-justification tree; decide yes/no with the complexity cost named.
3. If meshed: mTLS east-west, weighted canary routing (signal -> observability-sre, rollout -> devops-cicd), deliberate timeouts/retries/circuit-breaking.
4. Emit configs + Structured Output block.
