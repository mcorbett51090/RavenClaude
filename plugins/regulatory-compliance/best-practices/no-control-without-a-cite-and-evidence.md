# No control statement ships without a regulatory cite and evidence it operates

**Status:** Absolute rule
**Domain:** Control mapping / examination evidence
**Applies to:** `regulatory-compliance`

---

## Why this exists

A control statement with no regulatory citation, or one that describes the *policy* rather than what people *actually do*, fails the moment an examiner asks "show me." Regulators want the policy, the procedure, the **evidence the procedure is followed**, the management reporting, and the board/committee minutes that show oversight — in that order. Two failure modes recur: a control written against "applicable AML rules" with no section cite (so nobody can verify it maps to anything), and a walkthrough that recites policy text instead of the operated reality (so the rehearsal looks clean and the exam does not). The traceable chain — citation → control → operating evidence — is what survives an exam, not a friendly internal review.

## How to apply

Every control statement carries the regulator's actual citation (section + subsection + paragraph), a named owner, a frequency, and a pointer to operating evidence:

```
Control:    Sanctions screening of all new customers against the current OFAC SDN list
Cite:       FinCEN/OFAC obligation; FFIEC BSA/AML Manual — Sanctions Screening
            (use the regulator's primary source, not a summary blog)
Owner:      MLRO        Frequency: at onboarding + daily delta re-screen
Evidence:   screening logs w/ list-version captured; cleared-vs-escalated dispositions w/ rationale
```

Sanctions dispositions are **binary**: each hit is *cleared* (documented rationale, named clearer, source-list version) or *escalated*. "Looks fine" is not a disposition.

**Do:**
- Cite the regulator's primary source — "Per BMA Insurance (Group Supervision) Rules 2011, Rule 21(1)(b)", not "per the AML rules".
- Document the control's frequency, named owner, and where the operating evidence lives.
- Write so it survives an exam (house opinion #2: privilege/exam-readiness is a design constraint).

**Don't:**
- Write "the firm complies with all applicable laws" — name the law and how.
- Rely on a public regulator-summary blog as the regulatory basis — a summary is a starting point, not an authority.
- Describe the policy in a walkthrough when the examiner wants the operated practice; rehearse to find that gap and fix it before fieldwork.

## Edge cases / when the rule does NOT apply

- **A genuine policy gap** — when no control yet exists, document the gap (cause-event-consequence, named owner, dated remediation) rather than fabricating a cite. An honest gap with a remediation date beats a hollow control statement.
- **Cross-jurisdiction mapping** — the same control may answer to two regulators with different cites; record both and name which regime governs (house opinion #12). The rule wants *a* primary cite per regime, not a single universal one.
- **Legal-conclusion questions** ("is X lawful") — out of scope; the `Legal-advice gate:` line flips to counsel-required. The control documentation continues; the legal opinion routes to counsel.

## See also

- [`../agents/risk-and-controls-specialist.md`](../agents/risk-and-controls-specialist.md) — owns control mapping; design vs operating effectiveness.
- [`../agents/examination-prep-specialist.md`](../agents/examination-prep-specialist.md) — "walkthroughs reflect actual practice, not the policy"; the evidence-on-every-PBC discipline.
- [`../knowledge/regulator-finding-severity-triage.md`](../knowledge/regulator-finding-severity-triage.md) — the finding that fires when a control has no evidence.

## Provenance

Codifies house opinions #1 (cite the regulation), #6 (default to written), #8 (sanctions screening is binary), and #11 (primary-source provenance) in [`../CLAUDE.md`](../CLAUDE.md) §3, plus the "control without evidence" / "policy not practice" anti-patterns in [`../agents/examination-prep-specialist.md`](../agents/examination-prep-specialist.md) and [`../agents/risk-and-controls-specialist.md`](../agents/risk-and-controls-specialist.md).

---

_Last reviewed: 2026-05-30 by `claude`_
