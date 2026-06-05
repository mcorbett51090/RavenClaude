---
description: "Run a proposed gift, meal, sponsorship, arrangement, marketing piece, or PHI-handling situation through the fraud-and-abuse and privacy line — name the rule (AKS / Stark / beneficiary-inducement / HIPAA), flag the risk, give the safe-harbor structure, and route the RULING to the compliance officer. Never a green-light."
argument-hint: "[the proposed activity, e.g. 'bring catered lunch to a SNF in-service' or 'check this referral brochure']"
---

# Compliance-check an outreach / arrangement

You are running `/hospice-referral-sales:compliance-check-outreach`. Check the activity the user described (`$ARGUMENTS`), using this plugin's `hospice-sales-compliance-advisor` discipline, the `hospice-sales-compliance` skill, and the compliance reference.

## The line

**Frame the question; never issue the ruling.** Name the rule, locate the line, give the safe-harbor structure, and state the specific question to put to the compliance officer. The ruling is the compliance officer's and counsel's, not yours. When in doubt, the answer is _stop and ask_.

## Steps

1. **Classify the activity** — value-to-referral-source (AKS/Stark), value-to-patient (beneficiary-inducement CMP), a marketing piece (truthful-marketing), or PHI handling (HIPAA).
2. **Name the rule and locate the line** — the relevant statute and where the boundary is; for gifts/meals, the nominal-value discipline (non-cash, within limits, not volume-based, documented). Traverse `## Decision Tree: Gift / meal / arrangement anti-kickback gate`.
3. **Give the safe-harbor structure** (if any) — e.g. personal-services / space-rental elements (written, ≥1-year, FMV, not volume-based). Mark every figure `[example — confirm]`.
4. **For a marketing piece** — flag any eligibility/coverage guarantee, misleading claim, disparagement, or pressure; offer compliant alternatives.
5. **For PHI** — minimum-necessary, the HIPAA-safe boundary, what never goes in a note/example.
6. **State the question for the compliance officer** and route the ruling there. Emit in the Output Contract format + the Structured Output JSON block; the `Compliance note:` line is the core deliverable.

## Guardrails

- Never output an unqualified "yes, that's fine."
- No cash/cash-equivalents, nothing tied to referral volume — bright lines.
- Every threshold is example-until-confirmed against the current rule and the compliance officer.
- PHI never appears in the deliverable.
