# Document the no-file decision — a "we decided not to report" is itself a record

**Status:** Absolute rule
**Domain:** AML / KYC — reporting discipline
**Applies to:** `regulatory-compliance`

---

## Why this exists

When an alert, a referral, or an EDD review resolves to *no report*, the work is not finished — the decision-not-to-file is a record an examiner is entitled to see. The failure mode is treating a negative as a non-event: the analyst clears the alert, closes the case, and leaves nothing behind explaining *why* the threshold to report was not met. At the next exam the firm cannot demonstrate that it considered the suspicion and reasoned its way to a defensible no-file, so it looks like the suspicion was never evaluated at all. The same applies to applying simplified due diligence (SDD), waiving an EDD trigger, or closing a sanctions/negative-news review: the *reduction* or the *negative* needs a recorded basis. "If it isn't documented, it didn't happen" (house opinion #6) cuts both ways — it governs the decisions to *not* act as much as the decisions to act.

## How to apply

Capture a short, dated, named-author rationale for every consequential negative decision:

```
Trigger        what prompted the review (alert ID, referral, EDD trigger, sanctions/news hit)
Considered     the suspicion/typology that was evaluated — name it even when you're rejecting it
Decision       NO report  /  SDD applied  /  EDD trigger waived  /  hit cleared
Basis          why the threshold was not met / why the reduction is permitted in this regime  [verify-at-build]
Author + date  named, dated; reviewer if the case is higher-risk
```

A defensive-filing reflex ("file it to be safe" with no nameable typology) is itself a smell — if you cannot articulate the *why*, the honest output is often a documented no-file, not a hollow SAR.

**Do:**
- Record the no-file rationale with the same care as a filing — it is the proof the suspicion was evaluated.
- Document the *basis* for any SDD reduction or waived EDD trigger; a reduction without a recorded basis is the same defect as no due diligence.
- Keep no-file records on the same retention schedule as filed reports `[verify-at-build — retention periods are jurisdiction-specific]`.

**Don't:**
- Close an alert to "no action" with an empty disposition field.
- Treat defensive filing as a substitute for the no-file analysis — name the typology or document why it isn't met.
- Apply SDD "because the customer is low-touch" without recording that they sit in a permitted simplified category for the regime.

## Edge cases / when the rule does NOT apply

- **Genuinely trivial auto-closed noise** (a known-good payee matched by a too-loose rule) can be dispositioned in batch with a recorded rule-level rationale — but the *rule* that auto-closes still needs documented tuning (see the transaction-monitoring rule).
- **Continuing activity** — a prior no-file does not bind the next review; a pattern that develops can cross the line a single event did not, including triggering a continuing-activity report once a SAR is later filed.
- **Legal-opinion gate** — whether a disclosure obligation is legally triggered in a genuinely ambiguous case routes to counsel; the operational no-file record continues.

## See also

- [`./aml-reportability-before-you-file.md`](./aml-reportability-before-you-file.md) — the reportability triage whose *no* branch this rule documents.
- [`./aml-sar-narrative-answers-why.md`](./aml-sar-narrative-answers-why.md) — when the decision goes the other way, the narrative answers *why*.
- [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md) — `## Decision Tree: Is this reportable — SAR, threshold report, or none`.

## Provenance

Codifies house opinion #6 (default to written — including no-file decisions) in [`../CLAUDE.md`](../CLAUDE.md) §3, the `aml-reportability-before-you-file.md` "record the no-report decision and its basis" guidance, and the `aml-sar-narrative-answers-why.md` note that "defensive filing is a smell, not a strategy" and "no-file decisions are still documented."

---

_Last reviewed: 2026-05-30 by `claude`_
