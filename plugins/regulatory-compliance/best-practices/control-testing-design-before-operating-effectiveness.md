# Test Design Effectiveness Before Operating Effectiveness

**Status:** Primary diagnostic
**Domain:** Control testing / assurance
**Applies to:** `regulatory-compliance`

---

## Why this exists

A control cannot be operating effectively if it is not designed effectively. Testing whether a control "worked" before confirming that it is designed to work produces a misleading result: the control may have fired exactly as designed but the design is insufficient to mitigate the risk it is supposed to cover. Regulators and internal auditors distinguish these two questions deliberately — a design deficiency (ToD failure) is a different and often more serious finding than an operating deficiency (ToE failure) because it means the control can never work without being redesigned, regardless of how diligently staff execute it.

## How to apply

Structure every control test in two sequential phases, with a clear stop-gate at the design test.

```
Control Test Phases — Sequential Structure
──────────────────────────────────────────────────────
PHASE 1 — Test of Design (ToD)
  Question: Is this control designed to prevent or detect the risk it is assigned to?
  Test method: Walkthrough — trace one transaction/event through the control;
               interview the control owner; review the written procedure.
  Pass criteria:
    □ Control description matches what the control owner actually does.
    □ The design addresses the identified risk (not a related, adjacent risk).
    □ The frequency is appropriate for the risk (daily for high-frequency risks;
      not monthly for a risk that can fully materialize within a week).
    □ The control produces evidence of operation.
  Gate: If ToD fails → raise design deficiency finding → STOP.
        Do NOT proceed to ToE while the design is deficient.

PHASE 2 — Test of Operating Effectiveness (ToE)
  Runs only if Phase 1 passes.
  Question: Is the control operating as designed, consistently, over the test period?
  Test method: Sample-based testing.
  Sample size: Risk-based; higher-risk controls warrant larger samples.
  Pass criteria:
    □ Sample items show the control fired.
    □ Exception rate is within the firm's pre-defined tolerable rate.
    □ Exceptions have documented escalation records.
  Finding: ToE failure with ToD pass → operating deficiency → rating per severity scale.
```

**Do:**
- Document the ToD outcome before the ToE begins; the two phases are separate workpaper sections, not a combined narrative.
- If a walkthrough reveals that the procedure description does not match actual practice, raise the discrepancy as a ToD issue before testing a sample.
- When a control fails ToD, update the risk register to reflect that the risk is currently unmitigated — don't leave the control rated as it was.

**Don't:**
- Run a sample test and then write a walkthrough finding as an "observation" to soften the finding — a ToD failure is a ToD failure.
- Allow the control owner to be the walkthrough interviewer and the effectiveness tester — second-line independence is required.
- Mix design and operating findings in the same finding description; they have different remediation paths and different urgency.

## Edge cases / when the rule does NOT apply

- **Automated controls** where design and operation are one thing (the system either performs the check or it doesn't) — the distinction collapses; document the configuration test (design proxy) and the exception-log review (operation proxy) as separate sections of the same test, but expect them to be closely intertwined.
- **Detective controls with inherently low frequency** (e.g., an annual board approval of the risk appetite) — ToE sampling cannot apply to a control with a population of one; document the single occurrence and assess completeness of the evidence, not a sample rate.

## See also

- [`../agents/risk-and-controls-specialist.md`](../agents/risk-and-controls-specialist.md) — owns control testing methodology and the ToD/ToE framework.
- [`./controls-classify-the-control-type-before-you-rate-it.md`](./controls-classify-the-control-type-before-you-rate-it.md) — the control type (preventive/detective/directive) affects the ToD criteria; classify first, then test.

## Provenance

Codifies the risk-and-controls-specialist's testing discipline from the `control-testing` skill and CLAUDE.md §4 anti-pattern ("a control narrative without a frequency or named owner"). The ToD/ToE sequential structure reflects PCAOB AS 2201, COSO 2013, and standard second-line compliance testing methodology.

---

_Last reviewed: 2026-06-05 by `claude`_
