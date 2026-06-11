---
scenario_id: 2026-06-11-quickstart-had-a-hidden-step
contributed_at: 2026-06-11
plugin: developer-relations
product: onboarding-funnel
product_version: "n/a"
scope: likely-general
tags: [onboarding, time-to-first-value, hidden-step, quickstart, activation]
confidence: medium
reviewed: false
---

## Problem

Sign-ups were healthy but a third of new developers never made a successful first API call. The team
assumed the docs were "fine" because the page looked complete and internal engineers could follow it.
The risk: the people who wrote the quickstart already had the hidden prerequisites installed, so the
gap was invisible to them.

## Context

- Surface: the getting-started quickstart and the sign_up → first_success funnel.
- Constraint: activation is `first_success`; everything before it is setup the developer must clear
  unaided.
- The team reasoned from their own machines, which were already configured.

## Attempts

- Tried: **instrumented the funnel** and found the steepest drop at `credential → first_call` via
  `devrel_calc.py funnel_conversion`. Outcome: ~34% never reached the first call.
- Tried: **ran the quickstart on a clean machine** and logged every undocumented step. Outcome: the
  snippet assumed a regional endpoint and an environment variable the docs never mentioned — a classic
  undeclared prerequisite.
- Tried: **rewrote the path** to declare the region/version up front, use real runnable commands, and
  end with a verification step; re-measured TTFV. Outcome: TTFV p90 fell sharply and the
  credential→first_call conversion recovered.

## Resolution

The fix was to **run the quickstart on a clean environment, eliminate the hidden step, and rewrite the
path as a measured funnel** ending in a verification step — not to add more prose. The output was the
funnel diagnosis, the hidden-step list, and the rewritten quickstart with before/after TTFV.

**Action for the next consultant hitting this pattern:** **never trust a quickstart you can already
run.** Instrument the funnel, find the steepest drop, and run the path on a clean machine to surface
the undeclared prerequisites. See `best-practices/time-to-first-value-is-the-north-star.md` and
`knowledge/developer-onboarding-and-activation-reference.md` (hidden-step taxonomy).
