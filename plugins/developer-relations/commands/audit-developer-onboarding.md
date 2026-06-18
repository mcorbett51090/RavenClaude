---
description: "Audit the time-to-first-success path — walk the golden path as a hostile first-timer on a clean environment, count the steps, flag the friction per step, find the first dead end, and produce a drop-off map with a fix per step."
argument-hint: "[the getting-started / quickstart to audit, e.g. 'our API quickstart at docs/quickstart.md']"
---

# Audit developer onboarding

You are running `/developer-relations:audit-developer-onboarding`. Find the drop-off in the
time-to-first-success path for `$ARGUMENTS` — the discipline the `developer-onboarding-funnel` skill enforces.

## When to use this

Activation is leaking ("developers sign up but don't ship"), or before shipping a new quickstart. NOT
for designing the program (that's `design-devrel-program`).

## Steps

1. **Identify the golden path** — the one blessed shortest sequence to first working result
   ([`../knowledge/developer-experience-and-onboarding.md`](../knowledge/developer-experience-and-onboarding.md)).
   No golden path *is* the finding.
2. **Walk it as a hostile first-timer on a clean environment.** Assume nothing installed.
3. **Count the steps to first success** — the count is the metric.
4. **Flag friction per step** — unstated prerequisite, a key with no source, a snippet that doesn't
   run, an error with no recovery.
5. **Find the first dead end** and fix it before anything downstream.
6. **Produce the drop-off map** ([`../templates/developer-onboarding-audit.md`](../templates/developer-onboarding-audit.md))
   with the TTFS before/after and the defects checklist (placeholder secrets, TODOs).

## Guardrails

- Walk it clean — auditing from memory hides the leaks.
- The first dead end dominates; fix it before cosmetic downstream issues.
- A placeholder secret or `TODO` on the happy path is a defect (`sample-code-must-run-as-shipped.md`).
