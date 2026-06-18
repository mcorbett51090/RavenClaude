---
scenario_id: 2026-06-18-onboarding-drop-off-time-to-first-call
contributed_at: 2026-06-18
plugin: developer-relations
product: onboarding-funnel
product_version: "n/a"
scope: likely-general
tags: [onboarding, time-to-first-success, activation, golden-path, drop-off]
confidence: medium
reviewed: false
---

## Problem

Sign-ups were healthy but only ~11% `[ESTIMATE]` of registered developers ever made a successful API
call. The PM's instinct was to buy more top-of-funnel — more blog posts, a conference booth — to "get
more developers in." The DevRel advocate was asked to confirm the plan before the spend. The real
question was upstream: why do the developers we already have never ship?

## Context

- Product: a REST API with an OAuth-gated sandbox.
- Funnel state: acquisition fine, **activation leaking hard** (89% of sign-ups never reach first value).
- The getting-started existed and "looked complete"; nobody had walked it as a first-timer on a clean
  machine.
- Constraint: the advocate had the docs but not production analytics on the per-step funnel.

## Attempts

- Tried: a **time-to-first-success audit** ([`../knowledge/developer-experience-and-onboarding.md`](../knowledge/developer-experience-and-onboarding.md))
  — walked the golden path as a hostile first-timer in a clean container, counting steps. Result: **9
  steps** to first success, and a **first dead end at step 4** — the quickstart said "get your API key
  from the dashboard" but linked the dashboard root, not the key page, so a new developer had to hunt
  through settings. Several reasonable testers gave up there.
- Tried: cataloged the rest of the friction ([`../templates/developer-onboarding-audit.md`](../templates/developer-onboarding-audit.md)) —
  step 6's snippet referenced an `API_BASE` env var the docs never told you to set, and step 8 errored
  on an expired sandbox token with no recovery note. Each was a silent leak.
- Tried (the move that worked): fixed the **first dead end first** (showed the key inline with a "copy"
  button, not a link to hunt), then set the env var inside the snippet and added an error-recovery line
  at step 8. Re-counted: **9 steps → 5**. Reframed the PM's plan: pouring reach into a funnel that
  leaks 89% at activation is spending to fill a bucket with a hole — fix the hole first
  ([`../best-practices/optimize-time-to-first-success.md`](../best-practices/optimize-time-to-first-success.md)).

## Resolution

The activation leak wasn't a top-of-funnel problem — it was a **time-to-first-success** problem, and
the dominant cause was a single dead end (the unfindable API key) compounded by two unrunnable steps.
The fix was a getting-started rewrite that collapsed 9 steps to 5 and removed the dead ends, not a
bigger awareness spend. The honest recommendation: re-measure activation after the TTFS fix *before*
buying more reach; reach amplifies whatever activation rate you have, so fix activation first.

**Action for the next advocate hitting this pattern:** when activation leaks, do not buy more
top-of-funnel — run the TTFS audit on a clean machine and find the first dead end. Walk it as a hostile
first-timer (auditing from memory hides the leaks). The first dead end dominates; fix it before any
cosmetic downstream polish. Flag any placeholder secret / `TODO` on the happy path as a defect, not a
style note. Re-measure activation after, and only then decide whether more reach is worth it.

**Note:** figures are illustrative `[ESTIMATE]` ranges — validate against the engagement's actual funnel
instrumentation before a deliverable.
