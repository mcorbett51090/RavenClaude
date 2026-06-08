---
scenario_id: 2026-06-08-nda-self-serve-without-a-playbook
contributed_at: 2026-06-08
plugin: legal-ops-clm
product: generic
product_version: "unknown"
scope: likely-general
tags: [intake, playbook, escalation-trigger, self-serve, nda, cycle-time]
confidence: high
reviewed: false
---

> Not legal advice — an operational field note. A qualified lawyer owned the legal judgement throughout.

## Problem

A 400-person company's two-lawyer legal team was the bottleneck on every deal: sales waited 3-5 days for a standard mutual NDA because every NDA — including identical ones on the company's own template — landed in the same email inbox and waited for a lawyer to "review." Requests arrived by Slack DM, email, and hallway, so nothing was tracked and nothing could be prioritized; an urgent customer NDA sat behind a low-stakes vendor one because it was first-in.

## Constraints context

- Two lawyers, ~60 contract requests/month, ~70% of them standard NDAs.
- Leadership reported "contracts closed" as the legal metric — which rose even as sales complained loudly about speed.
- The lawyers were (reasonably) nervous about letting non-lawyers sign anything without a guardrail.

## Attempts

- Tried: triaging the shared inbox harder (a lawyer skims and reprioritizes daily). Failed — still a queue, still a lawyer in the loop on every standard NDA, and the daily triage was itself toil.
- Tried: a "just use this template" wiki page with no guardrails. Failed — sales used it but also accepted counterparty edits nobody caught, so a few NDAs went out with unacceptable terms; the lawyers clamped back down.
- Tried: a structured intake form (request type, counterparty, value, deadline) feeding a playbook — standard mutual NDA on the company template is self-serve with **no lawyer in the loop**, with bright-line escalation triggers (any counterparty edit to the confidentiality term, any one-way NDA, any deal over a value threshold, anything touching personal data) that route to a lawyer. This worked.

## Resolution

The escalation triggers were the unlock: they gave sales a clear, testable line for when they could self-serve vs. when they had to stop. Standard-NDA cycle time dropped from days to minutes, the lawyers got ~70% of their NDA volume off their plate, and the "contracts closed" vanity metric was replaced with cycle-time-by-class + self-serve-rate + escalation-mix — which finally showed the real story. The lawyers still owned every escalated and non-standard case.

## Lesson

A playbook is the product and the escalation trigger is its heart: replace ad-hoc intake with one structured front door, self-serve the standard majority on a pre-approved template, and write the "stop and get a lawyer" line as a bright line. A template with no escalation triggers is how unacceptable terms slip out; a queue with a lawyer on every NDA is how legal becomes the bottleneck. Not legal advice — the lawyers set the bounds.
