---
description: "Pave a golden path as real self-service with guardrails-as-defaults and policy-as-code, then define the adoption metrics that prove it's a product."
argument-hint: "[the manual capability to pave + the secure/compliance defaults + the provisioning stack]"
---

You are running `/platform-engineering:pave-golden-path`. Use `golden-paths-and-adoption-engineer` + the `golden-path-and-self-service` skill.

## Steps
1. Confirm the path is worn (2+ teams re-deriving it); if it's one team's preference, say so.
2. Design the self-service flow — interface (portal action / CLI / templated PR) + provisioning primitive (Terraform module / Crossplane / Score) — with no human in the loop.
3. Bake guardrails-as-defaults: encode the secure/tagged/compliant choice as the default; add a policy-as-code check (advisory first; blocking only for the irreversible).
4. Give the path an owner, a version, and a deprecation/migration story.
5. Define adoption + outcomes metrics: paved-road coverage + DORA + a DevEx signal + a platform SLO; flag any vanity metric.
6. Route the primitive build to terraform-iac/cloud-native-kubernetes, the portal action to developer-portal-engineer, the SLO to observability-sre.
7. Emit the golden-path spec + the Structured Output block (with `Cognitive load removed:` and `Handoff to build teams:`).
