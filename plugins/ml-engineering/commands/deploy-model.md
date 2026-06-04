---
description: "Deploy a model: choose online vs batch, serve a registered version, optimize latency, and roll out shadow->canary->full."
argument-hint: "[model + use case + latency budget]"
---

You are running `/ml-engineering:deploy-model`. Use `model-serving-engineer` + the `model-serving` skill.

## Steps
1. Traverse the serving-pattern tree (online vs batch).
2. Serve a registered version; optimize latency to budget.
3. Roll out shadow -> canary -> full; route promotion significance to applied-statistics.
4. Coordinate infra with cloud-native-kubernetes/devops-cicd.
5. Emit (from `templates/serving-rollout.md`) + Structured Output block.
