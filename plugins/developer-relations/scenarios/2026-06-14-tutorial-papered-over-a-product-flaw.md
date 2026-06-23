---
scenario_id: 2026-06-14-tutorial-papered-over-a-product-flaw
contributed_at: 2026-06-14
plugin: developer-relations
product: getting-started
product_version: "n/a"
scope: likely-general
tags: [time-to-first-success, fix-or-document, product-feedback, activation, onboarding]
confidence: medium
reviewed: false
---

## Situation

A platform's API offered three key scopes (read, write, admin), and the
getting-started flow let a developer create a key without making the right scope
obvious. Roughly one in three new developers picked the wrong scope, hit a 403 on
their first call, and many churned. DevRel's first instinct was to write a longer
tutorial section explaining the scopes in detail.

## Constraints

- The product team's backlog was full; a UI change to the key-creation flow
  "wasn't a priority" without evidence.
- Sign-ups were healthy, so leadership didn't see a problem in the top-line numbers.
- The DevRel team was measured on content output and was happy to ship more docs.

## What we tried

1. Added a detailed "choosing your API key scope" section to the getting-started
   guide. Time-to-first-success didn't move — most developers never read it; they
   pasted the quickstart and hit the 403.
2. Added a callout box higher up. Marginal improvement, still a wall of words in
   front of the first-success moment.

## Resolution

The team ran a getting-started audit from a clean state, **measured** TTFS, and
saw that the 403 sat right at "signup → first call," the most expensive funnel
step. Instead of more docs, they filed a **product-feedback brief** with the
frequency (~1 in 3) and severity (blocks first success) evidence, ranked by
activation impact. Product changed the default: the quickstart now provisions a
correctly-scoped key, and the create-key UI defaulted to the scope the quickstart
needs. First-call success jumped; the tutorial section shrank to a footnote. The
doc was kept only as a clearly-marked stopgap until the UI shipped.

## Lesson

When the getting-started path is painful because the **product** is confusing, the
first move is a product-feedback ticket with evidence — not a longer tutorial. A
tutorial that papers over a product flaw is technical debt with a smile: every new
developer still hits the wall, and the real problem never gets prioritized because
no one filed it. Fix the product before writing around it, and measure
time-to-first-success so the evidence is undeniable.
