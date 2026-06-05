---
scenario_id: 2026-06-05-srm-from-redirect-bot-filter
contributed_at: 2026-06-05
plugin: experimentation-growth-engineering
product: experimentation
product_version: "n/a"
scope: likely-general
tags: [srm, sample-ratio-mismatch, assignment, exposure-logging, chi-square]
confidence: high
reviewed: false
---

## Problem

A 50/50 test reported a clean, significant +8% lift on the primary metric and the team was ready to ship. A reviewer ran an SRM check first and found the arms were **10,243 vs 9,684** — a chi-square statistic of ~15.7, p ≈ 0.00007, far below the p < 0.001 alarm threshold. The split was broken, which meant the +8% "win" was measuring a self-selected population difference, not the treatment. Reading the metric at all was the mistake.

## Context

- Intended 50/50 assignment; consumer web funnel; ~20,000 exposed users.
- Treatment arm used a client-side redirect to a new page; control did not.
- A bot/spam filter ran *after* assignment but its exposure logging differed between arms.

## Attempts

- Tried: trusting the significant result. Wrong — significance on a broken split is meaningless. SRM is a plumbing check that gates the metric; no p-value on the primary metric can rescue a broken randomization (CLAUDE.md §3 #3).
- Tried: re-running the SRM check at a *finer* split granularity (by day, by platform) to localize the leak. The mismatch concentrated on mobile + the first day — pointing at the redirect.
- Tried (the diagnosis): the client-side redirect in the treatment arm dropped a fraction of users before the exposure event fired (slow redirect, users bouncing), and the bot filter scrubbed control and treatment asymmetrically. So treatment under-logged exposures relative to its true assignment — a classic **redirect + asymmetric-filter SRM**.
- Tried (the move that worked): moved assignment + exposure logging **server-side** so exposure is logged at the decision point (not after a client redirect), and applied the bot filter **identically and post-exposure** to both arms. Re-ran: arms came back within noise (p ≈ 0.48), and only then was the metric read.

## Resolution

**Check SRM before believing any metric, and when it trips, find the mechanical asymmetry between arms — don't tune it away.** The usual culprits: client-side redirects/flicker dropping exposures, a filter applied asymmetrically, assignment on an unstable id, or a logging path that differs by arm. The fix is almost always to log exposure at the server-side decision point and treat both arms identically downstream.

**Action for the next engineer:** run `scripts/experiment_calc.py srm --observed <a> <b> --split 50 50` as the **first** gate on any "finished" test, before reading the metric. If p < 0.001, the result is invalid — localize the mismatch by segment (day/platform/browser), find the arm-asymmetric step (redirect, filter, logging), fix it, and re-run. Analyze on exposure, not assignment. The significance verdict only matters *after* SRM passes — and that verdict is `applied-statistics`' (CLAUDE.md §3 #1, #3).

Cross-reference: complements the SRM skill [`../skills/srm-detection/SKILL.md`](../skills/srm-detection/SKILL.md), [`../best-practices/check-srm-before-trusting-a-result.md`](../best-practices/check-srm-before-trusting-a-result.md), [`../best-practices/analyze-on-exposure-not-assignment.md`](../best-practices/analyze-on-exposure-not-assignment.md), [`../best-practices/server-side-assignment-to-prevent-flicker.md`](../best-practices/server-side-assignment-to-prevent-flicker.md), and the "Can I trust this experiment result?" tree in [`../knowledge/experimentation-growth-engineering-decision-trees.md`](../knowledge/experimentation-growth-engineering-decision-trees.md).

**Sources (retrieved 2026-06-05):**
- SRM chi-square goodness-of-fit + the p < 0.001 norm — https://www.convert.com/blog/a-b-testing/sample-ratio-mismatch-srm-guide/ and https://docs.geteppo.com/statistics/sample-ratio-mismatch/
- Chi-square 1-dof: X² > 10.83 ⇔ p < 0.001 — standard; the exact figures here are reproduced by the bundled `scripts/experiment_calc.py srm`.
