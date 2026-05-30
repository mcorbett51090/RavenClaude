# Remediation has a named owner, a date, and an independent tester — never the person who built the broken control

**Status:** Absolute rule
**Domain:** Examination response — remediation tracking
**Applies to:** `regulatory-compliance`

---

## Why this exists

A remediation commitment without a named owner and a target date is, in the constitution's words, a finding waiting to be re-raised at the next exam — and a remediation verified by the same person who designed it is no verification at all. Two failures recur. First, "remediation in progress" with no owner or date: the regulator reads that as a non-commitment, and a slipped milestone that nobody owned surfaces as an open item next cycle. Second, the person who built the broken control marking their own fix "done" — the conflict of interest that produces "remediated" findings that recur at the very next exam. Independent verification (a tester who is not the designer) is what makes "fully remediated" mean to the regulator what the firm claims it means internally. The calendar is the strategy: a milestone slipping silently, with no rolling update to the regulator on an open item past its target, is the dominant failure mode.

## How to apply

Track every remediation with owner, date, evidence, and an independent verifier — and keep the regulator updated on slippage:

```
Finding           the finding + its severity tier (traverse the severity-triage tree first)
Root cause        the actual cause — not the symptom ("the control failed" is a symptom)
Remediation       what changes; named OWNER accountable
Target date       a real date, not "in progress"
Evidence          what will prove it operates once fixed
Independent tester DIFFERENT person from the designer; verifies the fix actually works
Rolling update     if a milestone slips, the regulator gets a proactive update on the open item — never silent
```

Response tone is professional and structured — acknowledge → root cause → remediation → date → owner → verification — never defensive; defensive responses age badly.

**Do:**
- Give every remediation a named owner, a target date, and an independent tester who didn't design the fix.
- Root-cause the finding (the actual cause, not the symptom) before committing a remediation.
- Send the regulator a rolling update the moment a milestone slips — silence on an open past-target item is the worst posture.

**Don't:**
- Write "remediation in progress" with no date or owner — that re-raises at the next exam.
- Let the person who built the broken control verify their own fix.
- Mark a finding "remediated" without independent evidence it operates — recurrence next exam is the predictable result.

## Edge cases / when the rule does NOT apply

- **Severity sets the rigor** — an MRIA-driven remediation needs interim controls within days and board-reported progress; route through the severity-triage tree first so the timeline and board-involvement match the tier.
- **Self-identified issues** follow the firm's internal issue-management cadence, but the owner/date/independent-tester discipline still applies — self-identified is not self-excused.
- **Legal-exposure remediations** (where the fix touches penalty or litigation risk) route the legal dimension to counsel; the operational remediation tracking continues.

## See also

- [`./classify-severity-before-you-respond.md`](./classify-severity-before-you-respond.md) — classify the finding's tier before setting remediation rigor.
- [`./exam-evidence-on-every-pbc-item.md`](./exam-evidence-on-every-pbc-item.md) — the evidence the independent tester collects.
- [`../knowledge/regulator-finding-severity-triage.md`](../knowledge/regulator-finding-severity-triage.md) — the tier sets timeline + board involvement.
- [`../agents/examination-prep-specialist.md`](../agents/examination-prep-specialist.md) — "Remediation has a tester"; "Calendar is the strategy"; "Tone is professional."

## Provenance

Codifies the `examination-prep-specialist` opinions "Remediation has a tester. Not the same person who designed the remediation," "Calendar is the strategy," and "Tone is professional," plus the anti-patterns "remediation done by the person who built the broken control," "'remediated' finding that recurs the next exam," and "open MRA/MRIA past its target with no rolling update" ([`../agents/examination-prep-specialist.md`](../agents/examination-prep-specialist.md)), and house opinion #5 (remediation has a date and an owner) in [`../CLAUDE.md`](../CLAUDE.md) §3.

---

_Last reviewed: 2026-05-30 by `claude`_
