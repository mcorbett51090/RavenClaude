---
description: "Design a Kubernetes workload: workload kind, probes, requests/limits + QoS, autoscaling, and a PodDisruptionBudget."
argument-hint: "[app behavior: stateful? bursty? scheduled?]"
---

You are running `/cloud-native-kubernetes:design-workload`. Use `kubernetes-architect` + the `k8s-workload-design` skill.

## Steps
1. Traverse the workload-kind tree.
2. Set the three probes; set requests/limits and state the QoS class.
3. Add HPA on a load-tracking signal + a PDB; add graceful shutdown.
4. Emit manifests (from `templates/deployment-skeleton.yaml`) + Structured Output block.
