---
scenario_id: 2026-06-08-ticket-driven-self-service
contributed_at: 2026-06-08
plugin: platform-engineering-idp
product: crossplane
product_version: "unknown"
scope: likely-general
tags: [self-service, crossplane, guardrails, service-desk, infra]
confidence: medium
reviewed: false
---

## Problem

A platform team announced "self-service infrastructure": developers filled in a form in the portal to
request a database. But the form created a Jira ticket that a platform engineer picked up, reviewed,
and provisioned by hand — median wait ~2 days. Developers (correctly) said this wasn't self-service.
The team's worry was that fully automating it was unsafe: a misconfigured DB request could blow the
cloud budget or expose data.

## Context

- Database provisioning was the single most frequent infra request (~15/week) — squarely in
  self-service territory by frequency.
- The fear driving the human gate was blast radius (cost, exposure), not rarity.
- The cluster was Kubernetes-native; the team already had Terraform modules for RDS.

## Attempts

- Considered: keeping the human gate "for safety." Rejected per **self-service-means-no-ticket-for-the-
  common-case** — a human on the common path re-introduced the exact wait the platform existed to
  remove, and the reviewer was rubber-stamping under load anyway.
- Tried: the self-service-boundary tree (frequency × reversibility × blast radius). Frequent + large
  blast radius → **self-service with guardrails**, not a ticket.
- Tried (the move that worked): a **Crossplane composition** exposing a `Database` claim with the
  unsafe choices removed by construction — fixed instance-size tiers, mandatory encryption + private
  networking, cost quotas per team, and OPA policy enforcing the envelope. The happy path became a
  button (minutes, no human); requests outside the envelope failed closed with a clear message and the
  escape-hatch path (a ticket) for the genuine exception.

## Resolution

**"Self-service" that opens a ticket for the common case is a service desk; the fix for blast-radius
fear is guardrails, not a human gate.** Encoding the safe envelope as a Crossplane composition + OPA
policy made the button safe by construction, cut the median wait from ~2 days to minutes, and reserved
human review for the rare out-of-envelope case.

**Action for the next engineer:** when blast-radius fear tempts you to gate self-service with a human,
encode the safe envelope as policy + bounded defaults instead and keep the happy path human-free.
Cross-reference [`../best-practices/self-service-means-no-ticket-for-the-common-case.md`](../best-practices/self-service-means-no-ticket-for-the-common-case.md)
and [`../best-practices/guardrails-not-gates-on-the-happy-path.md`](../best-practices/guardrails-not-gates-on-the-happy-path.md).

**Sources:** Crossplane composition + OPA guardrail pattern per crossplane.io / OPA docs
`[verify-at-use]`. Figures (2-day wait, 15/week) are illustrative; validate against actuals.
