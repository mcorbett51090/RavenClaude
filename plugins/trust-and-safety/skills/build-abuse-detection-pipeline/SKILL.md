---
name: build-abuse-detection-pipeline
description: "Design an abuse/fraud/spam detection pipeline — inventory signals, decide rules vs. ML (or hybrid), wire signal → score → threshold → action/reviewer-queue, and set the operating point from a precision/recall tradeoff. Reach for this when the user asks to catch an abuse type, choose signals, or route to a reviewer queue. Used by abuse-detection-engineer (primary)."
---

# Skill: build-abuse-detection-pipeline

> **Invoked by:** `abuse-detection-engineer` (primary). Co-driven with `trust-safety-policy-lead` so each score band maps to a proportional enforcement action.
>
> **When to invoke:** "catch <abuse type>"; "rules or ML?"; "build a detection pipeline"; "where do I set the threshold?"; "how do I route to a reviewer queue?".
>
> **Output:** a signal inventory + a rules-vs-ML decision + a signal → score → threshold → action/queue pipeline + the operating point (threshold + precision/recall + FP/FN rationale) + a reviewer-label feedback loop.

## Procedure

1. **Inventory the signals first (signals before models).** Sweep five families: **content** (text/image/URL features), **behavioral** (action rate, session shape), **graph/relationship** (shared device/IP, follow rings), **velocity** (burst/new-account), and **reputation** (account age, prior strikes). Many abuses fall to a cheap rule on a strong signal.
2. **Decide rules vs. ML vs. hybrid.** Traverse [`../../knowledge/enforcement-decision-tree.md`](../../knowledge/enforcement-decision-tree.md): rules for the obvious, explainable, cold-start case; ML for the gray zone, high-volume, and adapting adversary. Mature stacks are **hybrid** — rules gate the obvious, the model scores the rest.
3. **Wire the pipeline:** signal → **score** → **threshold** → **action vs. reviewer-queue**. Auto-action only in the **high-precision band**; route the gray zone to a human-review queue (whose volume must be survivable).
4. **Set the operating point from cost, not 0.5.** Choose the threshold from the cost of a **false positive** (a real user wrongly punished) vs. a **false negative** (abuse that gets through) for that policy. State the precision/recall at that point on the PR curve.
5. **Close the loop.** Reviewer decisions are labels — feed them back to recalibrate the threshold and retrain. Monitor for evasion and drift; a static threshold decays as the adversary adapts.
6. **Confirm the eval is sound, then mark seams.** Send the eval to `applied-statistics` for metric CIs / sample size / class-imbalance handling; map the score band to an action via `trust-safety-policy-lead`; an LLM classifier → `claude-app-engineering`.

## Worked example

> User: "Catch fake-review spam on our product pages."

- **Signals:** velocity (N reviews / account / hour), graph (reviews from accounts sharing a device fingerprint), content (near-duplicate text), reputation (account age < 24h).
- **Approach:** hybrid — a rule auto-removes the device-ring burst (precision ~0.99, explainable); an ML scorer handles the gray zone of single suspicious reviews.
- **Pipeline:** score → ≥0.9 auto-remove (high-precision band) → 0.6–0.9 reviewer queue → <0.6 allow.
- **Operating point:** 0.9 chosen because a false positive (removing a genuine review) costs seller trust; precision 0.96 / recall 0.71 at that cutoff. Eval CI confirmed via `applied-statistics`.
- **Loop:** reviewer overturns recalibrate the 0.6–0.9 band weekly.

## Guardrails
- Never report a threshold without the precision/recall it buys on a named eval set at a stated date.
- Never auto-action outside the high-precision band — the gray zone is a human-review case.
- A detector with no feedback loop rots; wire reviewer labels back in. See [`../../knowledge/trust-safety-metrics.md`](../../knowledge/trust-safety-metrics.md).
