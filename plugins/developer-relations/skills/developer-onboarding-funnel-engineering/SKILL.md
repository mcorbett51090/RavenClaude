---
name: developer-onboarding-funnel-engineering
description: "Engineer the developer onboarding funnel to first value — instrument sign-up → first-success, find the steepest drop, eliminate hidden steps and undeclared prerequisites, harden error messages, and rewrite the quickstart as a measured funnel rather than a page."
---

# Developer Onboarding Funnel Engineering

**Purpose:** turn a getting-started page into an instrumented funnel and engineer out the friction
between sign-up and first success — the single highest-ROI surface DevRel owns.

---

## Steps

### 1. Instrument the funnel as events, not pageviews

```
sign_up → credential_created → first_api_call → first_success → recurring_use
```

Each arrow is a conversion rate. Use [`../../scripts/devrel_calc.py`](../../scripts/devrel_calc.py)
`funnel_conversion` to compute every step and flag the steepest drop. A pageview is not a funnel
event; a credential created is.

### 2. Locate the steepest drop and form a cause hypothesis

| Drop at… | Usual cause | First probe |
|---|---|---|
| sign-up → credential | auth/key friction, unclear where to start | time the key-creation path yourself |
| credential → first call | hidden prerequisite, wrong default, SDK install pain | run the quickstart on a clean machine |
| first call → first success | cryptic errors, fragile happy path, conceptual gap | trigger the common error and read the message |

### 3. Eliminate hidden steps and undeclare-nothing

The silent killers: undeclared runtime/version, "obviously you also need X", a dashboard toggle the
docs never mention, copy-paste snippets that assume prior state. Run the path on a clean environment
and write down every step the docs skipped.

### 4. Harden the error messages on the critical path

For the 3–5 errors a new developer most likely hits, ensure each message says what went wrong, why,
and the next action. A developer who pastes a snippet and hits a clear, actionable error is still on
the path; one who hits a cryptic stack trace is gone.

### 5. Rewrite the quickstart as a funnel

Declare prerequisites and versions up front, use real runnable commands, keep the path to first
success as short as possible, and end with a **verification step** the developer can run to confirm
success. Re-measure time-to-first-value (`time_to_first_value`) and activation rate after the rewrite.

---

## Output

An instrumented funnel diagnosis (the steepest drop + cause), a list of eliminated hidden steps, the
hardened error messages, and a rewritten quickstart — with before/after TTFV and activation. Pairs
with the [`developer-onboarding-and-activation-reference`](../../knowledge/developer-onboarding-and-activation-reference.md).
