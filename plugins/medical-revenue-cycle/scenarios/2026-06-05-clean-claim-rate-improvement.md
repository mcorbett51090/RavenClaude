---
scenario_id: 2026-06-05-clean-claim-rate-improvement
contributed_at: 2026-06-05
plugin: medical-revenue-cycle
product: clean-claims
product_version: "n/a"
scope: likely-general
tags: [clean-claims, first-pass, scrubber, front-end, edits]
confidence: medium
reviewed: false
---

## Problem

A practice's first-pass / clean-claim rate was stuck in the high 80s while the team treated it as acceptable because "most claims still get paid eventually." But every point below the 95–98% clean-claim benchmark is rework — a claim that has to be touched again is cost plus delayed cash, and the "eventually paid" framing hid how much labor and A/R-days that rework was consuming (§3 #2, first-pass resolution is the master efficiency number).

## Context

- Segment: physician-group, mixed payer, claims sent through a clearinghouse with a basic scrubber whose edit set had not been tuned in years.
- Constraint: the scrubber was running generic edits, not payer-specific ones, so claims passed the scrubber and then failed at the payer — the worst place to find an error (after submission, consuming a denial + a rework cycle).
- The team conflated "claims get paid eventually" (true) with "the clean-claim rate is fine" (false) — ignoring the rework cost and the days-in-A/R drag that a sub-95% first-pass rate creates.

## Attempts

- Tried: **traced the rejections/denials back to a small set of recurring edit failures** rather than treating each as a one-off (§3 #5, §3 #6). The cluster was front-end and edit-tunable: missing/invalid information (CARC **CO-16**), eligibility/coverage mismatches caught only at the payer, and a recurring diagnosis-procedure inconsistency (CARC **CO-11**) from one service line. Outcome: a short, high-yield list of preventable failure modes.
- Tried: **tuned the scrubber with payer-specific edits** for the recurring failures and pushed eligibility verification to the front end so coverage mismatches were caught before submission, not after (§3 #6). Outcome: the recurring CO-16/CO-11 cluster stopped reaching the payer.
- Tried: instrumented **first-pass rate as a standing monthly metric** (not just "did it get paid") so a regression is visible the month it happens (§3 #2). Outcome: clean-claim rate climbed toward the 95%+ benchmark [ESTIMATE — validate against the client's clearinghouse acceptance report].

## Resolution

The sub-95% clean-claim rate was a **tunable-edits + front-end-eligibility** problem, not an unavoidable cost of doing business. The fix: trace rejections to a small recurring set, tune the scrubber with payer-specific edits, verify eligibility upstream, and track first-pass rate as a first-class metric. The payoff is compounding — fewer reworks means lower cost-to-collect *and* lower days-in-A/R at the same time.

**Action for the next consultant hitting this pattern:** treat a clean-claim rate below ~95% as **rework you are paying for**, not "fine because it pays eventually" (§3 #2). Trace rejections to the recurring CARC cluster (CO-16 missing info and CO-11 dx/procedure mismatch are common, tunable ones), tune the scrubber with **payer-specific** edits, and move eligibility to the front end (§3 #6). Track first-pass rate monthly so a regression surfaces immediately. The [`../scripts/rcm_calc.py`](../scripts/rcm_calc.py) `clean-claim` mode quantifies the rework cost of each point below your target.

**Sources (retrieved 2026-06-05):** clean-claim / first-pass benchmarks (95%+ good, 98%+ excellent) — https://www.mdclarity.com/blog/rcm-benchmarks and https://www.hfma.org/revenue-cycle/kpis/7-kpis-providers-should-be-tracking/ ; CARC code meanings (CO-16, CO-11) — https://www.sprypt.com/denial-codes/carc-and-rarc-codes . Specific rate figures are practice-dependent; treat any number here as `[ESTIMATE]` and validate against the client's clearinghouse report (§3 #8).
