---
scenario_id: 2026-06-08-self-service-that-was-a-ticket-queue
contributed_at: 2026-06-08
plugin: platform-engineering
product: crossplane
product_version: "unknown"
scope: likely-general
tags: [self-service, golden-path, guardrails-as-defaults, policy-as-code, adoption, dora]
confidence: high
reviewed: false
---

## Problem

A platform team announced "self-service environment provisioning" via a portal form. Adoption was high on paper (lots of form submissions) but developers were furious: each submission opened a Jira ticket that a platform engineer manually approved and applied, with a 1-2 day SLA. It was the old ticket queue with a nicer front door. Separately, teams kept shipping environments that failed the security review (missing tags, public buckets) because the requirements were a checklist a reviewer enforced *after* provisioning.

## Constraints context

- AWS, with a strong (justified) requirement that every resource be tagged and network-isolated by default.
- The platform team feared full automation would let teams provision non-compliant or runaway-cost infra.
- "Adoption" was being reported as form-submission count — a vanity metric that rose while developer experience fell.

## Attempts

- Tried: speeding up the manual approval (more platform engineers on rotation). Failed — it's a queue; throwing people at a queue doesn't make it self-service, and it didn't move lead time much.
- Tried: auto-approving the form but keeping the after-the-fact security review. Failed — non-compliant environments still slipped through during busy weeks because the guardrail depended on a human's diligence.
- Tried: encoding the requirements as defaults in a Crossplane composition (tags, network posture, and a cost guardrail baked in), exposing it as a portal action that provisions with **no human in the loop**, and adding an OPA/Conftest policy-as-code check that blocks the genuinely irreversible (public data exposure) while staying advisory on the rest. This worked.

## Resolution

The composition made the compliant configuration the *default* you get by taking the paved road, so opting out became the deliberate, harder path instead of a thing a reviewer had to catch. Removing the human from the provisioning loop cut lead time from ~1.5 days to minutes. The team replaced the form-submission vanity metric with paved-road coverage + the DORA lead-time and change-failure keys, paired with a quarterly DevEx pulse — and the real story (faster *and* more compliant) finally showed up in the numbers.

## Lesson

Self-service means no human in the loop — a portal form that opens a ticket is a faster queue, not a platform. Bake guardrails in as defaults (enforced by policy-as-code), not as after-the-fact review gates, and measure adoption with paved-road coverage + DORA + a DevEx signal, never submission counts.
