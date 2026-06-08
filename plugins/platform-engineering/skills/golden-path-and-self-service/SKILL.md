---
name: golden-path-and-self-service
description: "Pave a golden path as real self-service (no human in the loop): pick the self-service interface and provisioning primitive (Terraform module/Crossplane/Score/Kratix), bake guardrails-as-defaults enforced by policy-as-code, version and own the path, and measure adoption with paved-road coverage + DORA + DevEx + a platform SLO."
---

# Golden Path & Self-Service

## Self-service means no human in the loop
If "self-service provisioning" still ends in a ticket a platform engineer actions, it's a faster queue. The bar: a stream-aligned team gets the thing end-to-end themselves. Design the human out.

## Pave the road that's already worn
Pave where 2+ teams keep re-deriving the same setup, not where you wish they'd walk. A golden path nobody was going to take is wasted asphalt.

## Guardrails-as-defaults, not gates
The secure / tagged / compliant configuration is what you get **by default** on the paved road; opting out is the deliberate, owned, harder path. Encode the policy into the template/module; enforce off-road usage with **policy-as-code** (OPA/Conftest/Kyverno) — advisory first, blocking only for the genuinely irreversible (prod data, security, spend).

## Pick the primitive
Terraform modules behind a templated PR/portal action for IaC reuse; Crossplane compositions or Kratix promises for a K8s-native control plane; Score as the developer-facing workload spec mapped to platform primitives. The build of the primitive routes to `terraform-iac` / `cloud-native-kubernetes`.

## A path is a versioned, owned product surface
It has a maintainer, a version, and a deprecation/migration story. Breaking a path is a breaking change for every consumer. Abandonware paths are worse than no path.

## Measure adoption + outcomes, not vanity
Paved-road coverage (% of services on the path) + **DORA** (deploy frequency, lead time, change-failure rate, time-to-restore) + a **DevEx/SPACE** signal + a **platform SLO** (availability/latency of the self-service surface). Pair every throughput metric with an experience signal — throughput can be bought with developer misery. Catalog count and "platform users" are vanity.

## Output
A golden-path spec: the self-service interface, the provisioning primitive, the guardrails-as-defaults + policy check, the owner/version, the build handoff, and the adoption metrics. Platform SLO routes to `observability-sre`.
