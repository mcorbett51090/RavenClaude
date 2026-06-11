# Developer content & advocacy — reference

Deep reference for the `developer-advocate` and `developer-marketing-and-growth-strategist`, and the
content/demo/CFP skills. Companion to [`devrel-decision-trees.md`](devrel-decision-trees.md).

---

## Content format ↔ journey stage map

| Stage | Developer's question | Best formats | Goal metric |
|---|---|---|---|
| Awareness | "Does this solve a problem I have?" | conceptual post, conference talk, comparison, launch | reach → quickstart starts |
| Evaluation | "Will this work for my case?" | tutorial, sample app, reference architecture, video walkthrough | sign-ups, trial starts |
| Activation | "How do I get this working?" | quickstart, runnable demo, workshop, recipe | TTFV, activation rate |
| Adoption | "How do I run this in production?" | deep guide, best-practice doc, case study, migration guide | production adoption |

Rule: a topic with no stage and no goal metric is a wishlist item, not a plan.

## The demo trust model

Trust with a technical audience is won or lost on reproducibility. The four trust-killers and their
fixes:

| Trust-killer | Fix |
|---|---|
| Pre-warmed / hidden state | start from a clean, declared state |
| Undeclared versions | pin and declare every version |
| Happy-path-only | show one realistic failure + recovery |
| Glossed setup | make setup part of the demo, timed |

The failure-and-recovery beat is not optional polish — it is where the audience decides whether to
trust you.

## CFP acceptance patterns

Reviewers accept **problem-first** talks with a **concrete takeaway**. Strong CFP angles:

- A specific number/outcome ("800ms → 80ms cold start: what worked").
- A hard-won lesson ("three migrations that failed before one worked").
- A reproducible technique the audience can apply Monday.

Weak angles: product introductions, feature tours, anything titled like a brochure.

## The activation-path principle

Every piece of content ends with a next concrete step toward value — a repo, a quickstart, a sandbox,
a CLI command. Content that informs but provides no path converts nothing. This is the single most
common gap between content that "does well" (impressions) and content that activates.

## Positioning for a technical audience

- Lead with the **job-to-be-done** and the **alternative** the developer would otherwise use.
- Earn trust with **specificity**: numbers, constraints, honest tradeoffs.
- Avoid superlatives developers discount ("seamless", "blazing-fast", "enterprise-grade").
- Segment the message by adopting role: IC builder (time-to-value), tech lead (fit/maintainability),
  platform owner (risk/governance/support).

## Feedback-loop capture format

The unique DevRel asset. Capture field feedback as: `signal` (what was said/struggled with),
`stage` (where in the journey), `frequency` (how often), `route` (product / docs / DX). Triage on a
fixed cadence so recurring friction becomes prioritized input, not anecdotes.
