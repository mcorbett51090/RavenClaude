---
name: developer-onboarding-funnel
description: Audit the time-to-first-success path and find the drop-off — walk the golden path as a hostile first-timer on a clean environment, count the steps, flag the friction per step, locate the first dead end, and produce a drop-off map with a fix per step. Reach for this on "developers sign up but don't ship" or "review our getting-started". Used by `devrel-strategist` and `developer-advocate`.
---

# Skill: developer-onboarding-funnel

> **Invoked by:** `devrel-strategist` (the funnel diagnosis) and `developer-advocate` (fixing the artifact).
>
> **When to invoke:** "developers sign up but never ship"; "our getting-started has drop-off";
> "review this quickstart for DX"; anytime activation is the leaking stage.
>
> **Output:** a numbered drop-off map (steps → friction → fix) + the TTFS metric + the §6 Output Contract.

## Procedure

1. **Identify the golden path** — the one blessed shortest sequence to first working result
   ([`../../knowledge/developer-experience-and-onboarding.md`](../../knowledge/developer-experience-and-onboarding.md)).
   If there isn't one, that *is* the finding.
2. **Walk it as a hostile first-timer on a clean environment.** Assume nothing installed, no prior
   context, no patience.
3. **Count the steps to first success.** The count is the metric; every step is a leak point.
4. **Flag the friction per step**: unstated prerequisite, a key with no obvious source, a
   copy-paste block that doesn't run, a step that requires reading elsewhere, an error with no recovery.
5. **Find the first dead end** — fix this before anything downstream; nothing past it matters.
6. **Produce the drop-off map** using [`../../templates/developer-onboarding-audit.md`](../../templates/developer-onboarding-audit.md):
   each step, its friction, and the concrete fix, plus the TTFS before/after estimate.

## Worked example

> User: "Sign-up→active conversion is 11%. Here's our getting-started."

- Golden path counted: 9 steps to first success.
- First dead end: step 4 needs an API key, but the key page is linked, not shown — developer leaves to hunt.
- Other friction: step 6 snippet references an env var never set; step 8 errors with no recovery note.
- Drop-off map: fixes collapse 9 steps → 5, move the key inline, set the env var in the snippet, add an error recovery line.
- Metric: TTFS step count 9→5; re-measure activation after.

## Guardrails

- Don't audit from memory of how it's *supposed* to work — walk it clean, or the leaks stay invisible.
- The first dead end dominates; resist fixing cosmetic issues downstream of it first.
- A placeholder secret or `TODO` in the happy path is a defect, not a style note (the hook flags it).
