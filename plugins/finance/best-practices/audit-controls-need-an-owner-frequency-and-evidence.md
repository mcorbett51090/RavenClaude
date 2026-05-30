# Every control names an owner, a frequency, and an evidence type — or it does not exist

**Status:** Absolute rule
**Domain:** Audit readiness / control design
**Applies to:** `finance`

---

## Why this exists

An auditor does not accept that a control exists because someone says it does — they ask "who runs it, how often, and what proves it fired?" A control narrative missing any of those three is a finding waiting to happen. The `audit-prep-specialist` agent's rules are exact: "every control has a documented owner — 'the accounting team' is not an owner, a named person is"; "frequency in writing — daily / weekly / monthly / quarterly / annually / ad-hoc; 'as needed' is not a frequency"; "evidence type predeclared — what evidence proves the control fired? system log, signed report, email trail, ticket?" The agent is "cynical about informal controls: if the control isn't documented and consistently executed, it doesn't exist." A walkthrough must also describe **what actually happens**, not the idealized policy — then fix the gap; an aspirational walkthrough fails on first review.

## How to apply

Document each control with the five auditor dimensions — owner, frequency, activity, evidence type, and the IPE it relies on — and write the walkthrough to actual practice:

```
Control:    Monthly bank reconciliation review
  Owner:        <named person + title>            (not "the accounting team")
  Frequency:    monthly, by WD+5                   (not "as needed")
  Activity:     reviewer compares recon to bank statement, signs, dates
  Evidence:     signed recon PDF + review timestamp in close system
  IPE relied on: bank statement export — has its own completeness/accuracy check
  Test:         ToD (design) once + ToE (operating effectiveness) over a sample of N months
Walkthrough:  describe the process that ACTUALLY happens; flag any gap vs. policy; remediate the gap.
```

**Do:**
- Name a **person** as owner, a concrete **frequency**, and the **evidence type** that proves the control fired — all three, in writing.
- Identify the **IPE** (information produced by entity) each control depends on, and confirm that report has its own completeness/accuracy control — auditors will ask.
- Write walkthroughs to **actual practice**; where reality diverges from policy, the divergence is the finding — document it and remediate, don't paper over it.

**Don't:**
- Mark a PBC item complete with no evidence attached, or claim "we have a review control" with no named reviewer (named anti-patterns).
- Write "as needed" as a frequency or describe the policy instead of the process in a walkthrough.
- Remediate a deficiency by stacking a new manual control on a broken process — fix the root cause; remediation has a target date and a named tester.

## Edge cases / when the rule does NOT apply

- **Genuinely ad-hoc controls** exist (an event-triggered review on a non-routine transaction) — "ad-hoc" is an acceptable frequency *when the trigger is defined*; "as needed" with no trigger is not.
- **Automated/system controls** name the system configuration as the owner-equivalent and the system log as evidence — but a named person still owns monitoring that the automated control is operating.
- **SOC1 vs. SOC2 scoping** changes *which* controls are in scope (ICFR-relevant vs. trust-services criteria) but not the owner/frequency/evidence requirement — applying a SOC1 narrative shape to a SOC2 control (or vice versa) is itself a named anti-pattern.

## See also

- [`./controller-every-journal-entry-carries-a-memo-and-reviewer.md`](./controller-every-journal-entry-carries-a-memo-and-reviewer.md) — the preparer/reviewer split is a control whose evidence auditors test.
- [`./reconcile-before-you-narrate.md`](./reconcile-before-you-narrate.md) — the reconciliation control whose sign-off is the evidence.
- [`../agents/audit-prep-specialist.md`](../agents/audit-prep-specialist.md) — owner/frequency/evidence opinions; IPE controls; walkthrough-to-actual-practice; SOC1/SOC2 distinction.
- [`../skills/soc-control-walkthrough/SKILL.md`](../skills/soc-control-walkthrough/SKILL.md) — the control description's 6 dimensions, ToD vs. ToE, deficiency severity.

## Provenance

Codifies the `audit-prep-specialist` agent's "every control has a documented owner / frequency in writing / evidence type predeclared / IPE has its own controls / walkthroughs reflect actual practice" opinions and the related anti-patterns ([`../agents/audit-prep-specialist.md`](../agents/audit-prep-specialist.md)), plus house opinion #6 (audit trail in every workpaper) in [`../CLAUDE.md`](../CLAUDE.md) §3. New.

---

_Last reviewed: 2026-05-30 by `claude`_
