# behavioral-mental-health-practice

Operations support for **outpatient behavioral and mental-health clinics**. This plugin's team helps
you design intake workflows, manage access and capacity, structure clinical documentation for
compliance and reimbursement, run telehealth operations safely, and navigate the behavioral-health
billing and regulatory landscape — including **42 CFR Part 2**, HIPAA, prior authorizations, and
measurement-based care.

> **The one-line philosophy:** the practice operates best when every workflow — intake, scheduling,
> documentation, telehealth, and billing — is designed around three things: the patient gets timely
> access, the clinician documents medical necessity, and the regulatory guardrails (Part 2, HIPAA,
> state licensure) are baked in, not bolted on.

> **Scope discipline:** this plugin helps the practice **operate**. It does NOT give clinical advice,
> recommend diagnoses or treatment modalities, or substitute for a licensed clinician, compliance
> officer, or attorney.

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
| --- | --- |
| "Design or fix our intake workflow / reduce no-shows / manage waitlist" | **behavioral-mental-health-practice** (`intake-and-scheduling-analyst`) |
| "How should our treatment plans be structured for billing and compliance?" | **behavioral-mental-health-practice** (`clinical-documentation-advisor`) |
| "Set up telehealth, state licensure obligations, telehealth payer policies" | **behavioral-mental-health-practice** (`telehealth-operations-lead`) |
| "42 CFR Part 2 vs HIPAA, prior auth workflow, CPT/units question" | **behavioral-mental-health-practice** (`behavioral-billing-compliance-advisor`) |
| "Practice capacity model, provider productivity, clinic calendar" | **behavioral-mental-health-practice** (`practice-ops-lead`) |
| "Broader RCM lifecycle — claims scrubbing, ERA/EOB, denial management at scale" | `medical-revenue-cycle` |
| "Geriatric behavioral health, senior care coordination, Medicaid waiver" | `senior-care-operations` |
| "Full regulatory citation analysis — HIPAA Security Rule gap, licensing board" | `regulatory-compliance` |
| "Practice P&L, payer contract modeling, revenue forecasting" | `finance` |

## What's inside

- **5 agents** — `practice-ops-lead`, `intake-and-scheduling-analyst`,
  `clinical-documentation-advisor`, `telehealth-operations-lead`,
  `behavioral-billing-compliance-advisor`.
- **3 skills** — `intake-and-access`, `clinical-documentation-and-treatment-planning`,
  `behavioral-billing-and-authorization`.
- **3 commands** — `/behavioral-mental-health-practice:design-intake-flow`,
  `:prep-treatment-plan`, `:check-billing-compliance`.
- **2 templates** — `intake-packet.md`, `treatment-plan.md`.
- **Knowledge bank** — `knowledge/bh-practice-decision-trees.md`: Mermaid trees for 42 CFR Part 2
  vs HIPAA disclosure routing, authorization-needed determination, and telehealth-eligibility
  checking; plus a dated 2026 capability map (EHR, telehealth, MBC tools).
- **6 best-practices** and **1 advisory hook** (flags PHI exposure, missing Part 2 consent,
  missing medical-necessity documentation, and telehealth cross-state gaps).
- **`scripts/bh_calc.py`** — stdlib calculator: no-show rate, provider utilization,
  units/session, capacity, and authorization-burn.

## House opinions (the short list)

1. Helps the practice operate — not clinical advice; boundary is enforced by every agent.
2. 42 CFR Part 2 is stricter than HIPAA — check it first on every SUD-related disclosure.
3. Document medical necessity for every billable service.
4. Measurement-based care improves outcomes and substantiates continued medical necessity.
5. Telehealth follows the patient's state licensure, not the clinic's.
6. Protect PHI and Part 2 records — minimum-necessary principle by default.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
