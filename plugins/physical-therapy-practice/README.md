# physical-therapy-practice

The **plan-of-care-to-reimbursement operating engine** for an outpatient physical therapy practice —
running the clinic operating model, keeping documentation defensible and compliant, managing
scheduling and patient flow, and protecting reimbursement through clean coding and denial prevention.

> **The one-line philosophy:** plan-of-care adherence is the master metric — it is simultaneously the
> clinical outcome and the financial one. Documentation defends the claim, and the 8-minute rule
> governs the units.

---

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Run our clinic operating model / payer mix / productivity" | **physical-therapy-practice** (`pt-practice-lead`) |
| "Make our documentation defensible / compliant" | **physical-therapy-practice** (`clinical-documentation-and-compliance-specialist`) |
| "Reduce cancellations / fix patient flow / plan-of-care adherence" | **physical-therapy-practice** (`scheduling-and-patient-flow-analyst`) |
| "Fix our coding / units / denials" | **physical-therapy-practice** (`billing-and-reimbursement-analyst`) |
| "Set up an outcomes program / MIPS / value-based readiness" | **physical-therapy-practice** (`outcomes-and-quality-analyst`) |
| "Analyze referrals / new-patient conversion / intake verification" | **physical-therapy-practice** (`referral-and-patient-access-strategist`) |
| "General medical revenue cycle (multi-specialty)" | `medical-revenue-cycle` |
| "Dental or veterinary clinic operations" | `dental-practice` / `veterinary-practice` |
| "Behavioral / mental-health practice" | `behavioral-health-practice` |

---

## What's inside

- **6 agents** — `pt-practice-lead`, `clinical-documentation-and-compliance-specialist`,
  `scheduling-and-patient-flow-analyst`, `billing-and-reimbursement-analyst`,
  `outcomes-and-quality-analyst`, `referral-and-patient-access-strategist`.
- **8 skills** — `pt-documentation-and-compliance`, `patient-flow-and-plan-of-care-adherence`,
  `pt-billing-units-and-denials`, `functional-outcomes-and-quality-reporting`,
  `referral-management-and-new-patient-conversion`, `insurance-verification-and-authorization`,
  `pt-clinic-pl-and-payer-mix`, `productivity-and-staffing-model`.
- **6 commands** — `/audit-clinical-documentation`, `/reduce-cancellations-and-no-shows`,
  `/analyze-billing-denials`, `/build-outcomes-program`, `/analyze-referral-pipeline`, `/model-clinic-pl`.
- **4 templates** — a plan-of-care template, a denial-prevention checklist, an outcomes-tracking
  scorecard, and a referral-source scorecard.
- **12 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **A 5-doc knowledge bank** — [`knowledge/pt-practice-decision-trees.md`](knowledge/pt-practice-decision-trees.md)
  plus documentation/compliance, billing/units/denials, outcomes/value-based-care, and
  referral/revenue-cycle references.
- **A scenarios bank** — [`scenarios/README.md`](scenarios/README.md) (field-tested cases).
- **An advisory hook** flagging anti-patterns (timed CPT units with no 8-minute-rule note, billing
  decision with no medical-necessity/documentation basis, cancellation framed as revenue-only).
- **A calculator** — [`scripts/pt_calc.py`](scripts/pt_calc.py) (stdlib only): 8-minute-rule units,
  visit utilization, cancellation/no-show rate, plan-of-care adherence, units-per-visit, referral
  conversion, clinic contribution margin, outcome change vs. MCID.

---

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install physical-therapy-practice@ravenclaude
```

Requires `ravenclaude-core` (inherited protocols). See [`CLAUDE.md`](CLAUDE.md) for the team
constitution and house opinions.

> **Compliance note:** Medicare rules (the 8-minute rule, therapy threshold/KX modifier, MIPS),
> CPT coding, and payer policies change and vary by payer and jurisdiction. This plugin gives
> operational decision-support, not coding, billing, legal, or compliance advice — verify against
> current CMS/payer policy and a certified coder/compliance professional.
