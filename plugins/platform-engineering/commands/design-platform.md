---
description: "Design an internal developer platform as a product: the thinnest viable platform, the self-service API, the Team Topologies model, and build-vs-buy per layer."
argument-hint: "[current friction + teams + existing CI/cluster/IaC stack]"
---

You are running `/platform-engineering:design-platform`. Use `platform-architect` + the `internal-developer-platform-design` skill.

## Steps
1. Map the cognitive load: what toil/decisions are 2+ teams re-deriving? If none, say so (don't build a platform yet).
2. Define the thinnest viable platform — the 1-3 highest-leverage golden paths to pave first, each justified by the load it removes.
3. Define the platform API (self-service capabilities + interface per capability) and the Team Topologies operating model.
4. Draw build-vs-buy per layer (portal / catalog / scaffolder / provisioning) with the TCO trade named; list explicit non-goals.
5. Route the builds: pipeline → devops-cicd, cluster → cloud-native-kubernetes, module → terraform-iac, SLO → observability-sre.
6. Emit the thinnest-viable-platform brief + the Structured Output block (with `Cognitive load removed:` and `Handoff to build teams:`).
