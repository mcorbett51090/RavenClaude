# Tune transaction-monitoring thresholds with data, never with opinion

**Status:** Absolute rule
**Domain:** AML / KYC — transaction monitoring
**Applies to:** `regulatory-compliance`

---

## Why this exists

Transaction-monitoring rules drift out of calibration the moment they ship and are rarely re-tuned. The two failure modes are mirror images: thresholds left so loose that alert volume swamps the team (so genuine alerts are triaged in a hurry, or auto-closed in batches), or tightened on a hunch to "reduce noise" with no analysis of what slipped below the line. Both are indefensible because both are *opinion-driven*. A threshold change is a model change: it moves the false-positive rate, the false-negative exposure, and the population of activity that now does or does not alert. An examiner reviewing a tuning decision wants the before/after alert population, the false-positive-rate impact, and the named approver — not "we felt 10k was too low." A monitoring rule never tuned since rollout, with alert volume disconnected from the firm's actual risk, is a standing finding.

## How to apply

Treat every threshold or rule change as a documented model change with an impact analysis:

```
Baseline       current rule + threshold + alert volume + current false-positive rate (sampled)
Proposed       new threshold/logic + the population it adds or removes from alerting
Impact         false-positive-rate delta + false-negative exposure (what now falls below the line)
                + tie to risk: does the change track a real shift in customer/product risk, or just noise?
Approval       named approver (model-risk / MLRO) + date + the analysis attached
Back-test      re-run the proposed rule over a historical window before going live
```

Threshold changes require a false-positive-rate impact analysis — the rule that the `aml-kyc-analyst` enforces as "tuned with data, not opinion."

**Do:**
- Back-test a proposed threshold over a historical window before it goes live; record what it would have alerted on and what it would have missed.
- Tie tuning to a risk rationale — a new product, a new geography, a typology trend — not to alert-volume comfort.
- Keep an auditable change log: who changed what threshold, when, on what analysis, approved by whom.

**Don't:**
- Tighten a threshold to cut noise without quantifying the false-negative exposure it creates.
- Leave a rule un-tuned since rollout while the customer base, products, or risk profile have moved.
- Auto-close alert backlogs to clear volume — that converts a tuning problem into an un-investigated-suspicion problem.

## Edge cases / when the rule does NOT apply

- **A brand-new rule with no history** can't be back-tested against itself — calibrate against the closest proxy population and flag it for early post-go-live review.
- **Regulator-mandated thresholds** (a specific cash-reporting amount) are not "tunable" — they are fixed by the regime `[verify-at-build — amounts are jurisdiction-specific]`; tuning applies to the firm's *internal* suspicious-activity rules, not statutory thresholds.
- **Model validation proper** (independent model-risk review) is a separate, deeper exercise than routine threshold tuning; a material model change routes there.

## Edge note — this is not the same as the reportability threshold

A *monitoring* threshold (when does an alert fire) is internal and tunable. A *reporting* threshold (when must a report be filed) is statutory and fixed — see [`./aml-reportability-before-you-file.md`](./aml-reportability-before-you-file.md). Don't conflate the two.

## See also

- [`./aml-sanctions-screening-hygiene.md`](./aml-sanctions-screening-hygiene.md) — fuzzy-match thresholds carry the same data-not-opinion discipline.
- [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md) — "Transaction monitoring is tuned with data, not opinion."; anti-pattern "rule never tuned since rollout."

## Provenance

Codifies the `aml-kyc-analyst` opinion "Transaction monitoring is tuned with data, not opinion. Threshold changes require false-positive-rate impact analysis" and the anti-pattern "transaction-monitoring rule never tuned since rollout; alert volume disconnected from risk" ([`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md)), plus house opinion #13 (risk quantified where possible) in [`../CLAUDE.md`](../CLAUDE.md) §3.

---

_Last reviewed: 2026-05-30 by `claude`_
