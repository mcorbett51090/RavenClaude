---
scenario_id: 2026-06-05-denial-rate-root-cause-capa
contributed_at: 2026-06-05
plugin: medical-revenue-cycle
product: denials
product_version: "n/a"
scope: likely-general
tags: [denials, root-cause, capa, eligibility, authorization, carc]
confidence: medium
reviewed: false
---

## Problem

A mid-size multi-specialty physician group's initial denial rate had climbed into the low double digits and the billing office was drowning in an appeal queue. The practice manager wanted "more appeal staff." The denial rate was reported as a single aggregate number with no category breakdown — so nobody could say *which* denials were driving it, and the proposed fix (more appellers) treated the symptom, not the cause.

## Context

- Segment: physician-group, multi-specialty, independent, in-house billing.
- Constraint: the PM/EHR system *could* report denials by CARC/payer, but the denial worklist was being worked FIFO (oldest first), not by category or recoverable dollars — so the same preventable denial recurred while staff chased one-off appeals.
- The manager conflated "denial rate is high" (a back-end symptom) with "we need more appeal capacity" (one possible fix among several). Classic single-cause story the decision trees warn against (§3 #5, §3 #6).

## Attempts

- Tried: **categorized the denials by CARC root cause and owner before adding any headcount** (§3 #5). The Pareto landed where it usually does — a front-end cluster dominated: eligibility/coverage (CARC CO-22/CO-27 family) and prior-authorization (CARC **CO-197** — service required prior auth and none was obtained) together accounted for the largest share by both count and dollars. Coding-driven denials (CARC CO-11 — diagnosis/procedure inconsistency; CO-16 — missing information) were the next band. Outcome: reframed from "appeal faster" to "stop generating the top two categories upstream."
- Tried: a **CAPA loop** (corrective and preventive action) on the top two categories — real-time eligibility verification at scheduling/check-in, and an authorization checklist gated before the date of service (§3 #6, front-end errors are back-end denials). Outcome: the eligibility and CO-197 categories fell over the following quarters [ESTIMATE — validate against the client's denial report].
- Tried: re-sequenced the denial worklist to **timely-filing risk first, then recoverable-dollar-weighted** rather than FIFO (§3 #3). Outcome: stopped the silent timely-filing write-offs (CARC CO-29) that FIFO had been letting age out.

## Resolution

The high denial rate was **mostly front-end-born and preventable**, not an appeal-capacity problem. The fix was a categorize-then-CAPA discipline: fix eligibility and prior-auth at registration/scheduling, work the queue by deadline-and-dollars not FIFO, and measure denial rate **by category** going forward so a recurrence is visible immediately.

**Action for the next consultant hitting this pattern:** before recommending more appeal staff, **categorize denials by CARC and owner** (§3 #5) and build the Pareto — the top two are almost always front-end (eligibility + prior auth) and preventable upstream far more cheaply than they are appealed (§3 #1, §3 #6). Worth knowing: industry studies report that **50–65% of denied claims are never reworked** and roughly **two-thirds are recoverable** — so an unworked queue is lost cash, but the cheaper win is preventing the denial. The cheapest denial is the one that never happens.

**Sources (retrieved 2026-06-05):** denials-never-reworked / recoverable share — https://www.os-healthcare.com/news-and-blog/measuring-the-cost-of-denials-and-impact-of-prevention and https://www.mdclarity.com/rcm-metrics/denial-recovery-rate ; CARC code meanings (CO-197, CO-11, CO-16, CO-29) — https://www.sprypt.com/denial-codes/carc-and-rarc-codes and https://x12.org/codes/claim-adjustment-reason-codes . Specific category percentages are practice-dependent; treat any number here as `[ESTIMATE]` and build the Pareto from the client's own denial report (§3 #8).
