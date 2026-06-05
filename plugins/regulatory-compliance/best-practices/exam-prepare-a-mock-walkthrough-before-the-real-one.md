# Run a Mock Walkthrough Before the Regulator Does

**Status:** Pattern
**Domain:** Examination preparation
**Applies to:** `regulatory-compliance`

---

## Why this exists

The most expensive thing a firm says during an examination is "I'll have to check on that." A walkthrough that surfaces a gap in front of the examiner — a control the policy describes that no one can demonstrate operating, a system that was supposed to flag something it evidently didn't — becomes a finding. The same gap surfaced during an internal mock walkthrough six weeks earlier is a remediation project. The mock walkthrough shifts the discovery moment from the exam to the preparation phase, where the firm controls the timeline and the response.

## How to apply

At least 4–6 weeks before a scheduled examination, run a structured mock walkthrough for every high-risk control area the regulator is likely to test.

```
Mock Walkthrough — Structure
──────────────────────────────────────────────────────
Phase 1 — SCOPE (Week 0)
  Review the prior-exam findings and MRA/MRIA list.
  Review the regulator's published examination focus areas for the current cycle.
  Identify the top 5–8 control areas most likely to be tested.

Phase 2 — INTERNAL MOCK (Week 1–2)
  For each control area:
  □ Ask the control owner to demonstrate the control as if explaining to an examiner:
    — "Who runs this?" → named individual, not a team
    — "How often?" → frequency per the control narrative
    — "Show me the evidence it fired in the last period" → pull the sample
  □ Second-line (compliance/risk) plays the examiner role.
  □ Document every gap: missing evidence / stale procedure / policy-reality disconnect.

Phase 3 — REMEDIATION (Week 2–4)
  Each gap: owner + target fix date + evidence that it's been fixed.
  Prioritize by examiner-visibility — if an examiner is almost certain to test it,
  it is P0 regardless of the residual-risk rating.

Phase 4 — FINAL DRY RUN (Week 5)
  Repeat the mock for the highest-risk areas only.
  Confirm evidence is organized in the format the examiner expects (paper / portal / screen share).
  Brief the board / audit committee on the preparation status.
```

**Do:**
- Have the mock-walkthrough interviewer be someone who has not been involved in the control's day-to-day operation — the closer to an examiner's independent perspective, the more useful the gap finding.
- Rehearse the Q&A, not just the document retrieval — examiners ask follow-up questions, and "I'll get back to you" in a mock is training for the real thing.
- Log mock findings in the same tracker as the final exam prep; remediation evidence needs to survive post-exam review.

**Don't:**
- Run the mock walkthrough only for controls the firm is confident in — the controls that feel "fine" are where surprises hide.
- Treat the mock as a box-checking exercise; if an issue is found, it must be remediated before the exam, not noted and deferred.
- Brief staff on exact expected questions in a way that produces rote answers rather than genuine demonstration.

## Edge cases / when the rule does NOT apply

- **Surprise examinations** — the mock walkthrough cannot be staged; use the `examination-readiness` skill's standing-ready checklist instead, which is designed for the always-on posture an unscheduled examination demands.
- **Follow-up targeted examinations** (the regulator returns to test a specific prior finding) — the scope narrows to that finding; the mock should rehearse exactly that control and its remediation evidence.

## See also

- [`../agents/examination-prep-specialist.md`](../agents/examination-prep-specialist.md) — owns the mock-walkthrough and exam-readiness playbook.
- [`./exam-remediation-has-an-owner-date-and-independent-tester.md`](./exam-remediation-has-an-owner-date-and-independent-tester.md) — gaps surfaced in the mock walkthrough flow into the remediation tracker this rule governs.

## Provenance

Codifies the examination-prep-specialist's mock-walkthrough discipline from CLAUDE.md §4 anti-pattern ("pre-exam walkthroughs that describe the policy, not what people actually do") and the `examination-readiness` skill. The phase structure reflects standard pre-exam playbook practice from a Tier-1 financial regulator (BMA) field experience.

---

_Last reviewed: 2026-06-05 by `claude`_
