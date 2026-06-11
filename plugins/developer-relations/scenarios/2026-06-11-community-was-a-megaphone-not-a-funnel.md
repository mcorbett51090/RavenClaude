---
scenario_id: 2026-06-11-community-was-a-megaphone-not-a-funnel
contributed_at: 2026-06-11
plugin: developer-relations
product: community
product_version: "n/a"
scope: likely-general
tags: [community, funnel, recognition, answer-rate, docs-gap]
confidence: medium
reviewed: false
---

## Problem

A Discord with a growing member count felt unhealthy: questions sat unanswered, the same people
carried every conversation, and no one new ever started helping. The team pointed to the rising member
count as evidence of health. The risk: member count is a top-of-funnel input that says nothing about
whether the community converts lurkers into answerers and contributors.

## Context

- Surface: a developer community treated as an announcement channel.
- Constraint: a healthy community answers itself (the self-answer ratio is the scaling metric); this
  one depended entirely on two staff members.
- The team reasoned from headcount, not from stage conversion.

## Attempts

- Tried: **modeled the funnel** (lurker → asker → answerer → contributor → champion) via
  `devrel_calc.py community_health`. Outcome: a dead `asker → answerer` transition — almost all answers
  came from staff, self-answer ratio near zero.
- Tried: **installed a recognition loop** — surfaced top answerers, public thanks, a helper role.
  Outcome: a handful of members began answering, and the self-answer ratio started to climb.
- Tried: **clustered the recurring questions** and routed the top three to docs. Outcome: question
  volume on those topics dropped and the answerers were freed for harder ones.

## Resolution

The fix was to **treat the community as a funnel, unstick the asker→answerer transition with
recognition, and feed recurring questions back into docs** — not to broadcast more. The output was the
funnel model, the stuck-stage diagnosis, the recognition intervention, and the docs-gap routing.

**Action for the next consultant hitting this pattern:** **size the funnel before celebrating the
member count.** Find the stuck transition; if it's asker→answerer, the lever is recognition. See
`best-practices/community-is-a-funnel-not-a-megaphone.md`,
`best-practices/recognize-answerers-or-the-community-stalls.md`, and
`knowledge/community-and-ecosystem-reference.md`.
