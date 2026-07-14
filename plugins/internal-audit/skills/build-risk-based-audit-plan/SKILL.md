---
name: build-risk-based-audit-plan
description: "Build a risk-based internal-audit universe and annual plan by traversing the internal-audit decision tree (assurance-vs-advisory → risk-ranking the universe → coverage/cycle → resourcing), then return the scored audit universe, the resource-balanced annual plan (assurance/advisory mix, cycle coverage), the IIA-Standards/Three-Lines positioning, and the audit-committee residual-risk narrative. Reach for this when the user asks 'how do we rank our audit universe?', 'what should be on this year's audit plan?', 'how much of the universe can we cover?', or 'how do we stay IIA-conformant and independent?'. Used by internal-audit-lead (primary)."
---

# Skill: build-risk-based-audit-plan

> **Invoked by:** `internal-audit-lead` (primary). Also consulted by `audit-engagement-specialist` to place a single engagement in the wider universe and confirm its risk rationale.
>
> **When to invoke:** "how do we build/rank our audit universe?"; "what belongs on this year's audit plan?"; "how much coverage can our hours buy?"; "are we conformant with the IIA Standards and sitting right in the Three Lines Model?"; any "what should internal audit look at, and how do we govern the function?" question.
>
> **Output:** the scored audit universe + the annual plan (assurance/advisory mix, cycle coverage, resourcing) + the IIA-Standards / Three-Lines / independence positioning + the QAIP note + the audit-committee residual-risk narrative + the 1-2 flip conditions.

## Procedure

1. **Restate the situation in the tree's terms.** Capture: the **organization** (size, sector, structure, regulatory load), the **risk landscape** (strategic, operational, financial, compliance, IT/cyber, fraud), the **function's resources** (auditor FTEs, hours, skills, co-source/guest-auditor options), any **mandated coverage** (SOX ICFR, regulatory), and the **maturity** of first- and second-line risk management.
2. **Build the audit universe.** Enumerate the **auditable entities** — processes, business units, systems, key risks, or a hybrid. Keep the grain consistent and the universe complete enough that nothing material is invisible, but coarse enough to be plannable (dozens, not thousands).
3. **Score each entity for risk.** Rate **inherent risk** = impact × likelihood, adjusted for **velocity** (how fast the risk bites) and **fraud exposure**; then factor **control maturity** to get **residual risk**. Use a documented, consistent scale (e.g. 1–5) so the ranking is defensible to the audit committee. Higher residual risk → higher priority.
4. **Traverse the decision tree** in [`../../knowledge/internal-audit-decision-tree.md`](../../knowledge/internal-audit-decision-tree.md) against those inputs:
   - each candidate engagement → **assurance** (independent opinion on control) vs **advisory** (input without owning the decision) — and confirm advisory work never crosses into owning a control,
   - rank the universe by **residual risk**; allocate the finite hours to the top of the stack; give the rest a **defensible cycle** (e.g. high-risk annual, medium every 2 years, low every 3–5),
   - reserve capacity for **mandated** work (SOX/regulatory), **management-requested** advisory, and an **unplanned/emerging-risk** buffer,
   - confirm the **Three Lines** placement (IA is third line — independent assurance to the governing body, not first/second-line ownership).
5. **Balance the plan against resources.** Convert selected engagements into estimated hours; reconcile against available capacity; flag the coverage gap explicitly (what you are *not* auditing this year and why) rather than silently dropping the tail.
6. **Position for conformance and independence.** Note conformance against the 2024 IIA Global Internal Audit Standards (5 domains / 15 principles), the CAE's **functional-to-audit-committee / administrative-to-management** reporting line, and the **QAIP** basis (internal ongoing + periodic assessments; external quality assessment every 5 years).
7. **State the flip conditions** — the 1-2 facts that, if different, change the plan (a new regulation, a major system implementation, a fraud event, an M&A, a control-environment downgrade that raises residual risk).

## Worked example

> User: "Mid-size SaaS company, 4-person audit team, ~3,000 audit hours/year. How do we build this year's plan?"

- **Universe:** ~30 auditable entities across revenue (order-to-cash, revenue recognition), procure-to-pay, payroll, cloud/IT general controls, SDLC, third-party/vendor risk, privacy, and the fraud/entity-level controls.
- **Scoring:** revenue recognition and IT general controls score **high residual** (material + regulatory + a control environment still maturing); payroll scores **medium**; facilities scores **low**.
- **Assurance vs advisory:** revenue-recognition and ITGC → **assurance** engagements (independent opinion); the new billing-system implementation → **advisory** (IA reviews controls-by-design without owning them).
- **Plan:** ~6 assurance engagements on the high-residual top of the stack + 1 advisory + a SOX-support allocation + a ~15% emerging-risk buffer; medium-risk areas on a 2-year cycle, low on 3–5. Hours reconcile to ~3,000 with the coverage gap (facilities, low-risk BUs deferred) stated to the committee.
- **Independence/Three-Lines:** IA gives assurance (third line); the billing-project advisory is explicitly non-owning. CAE reports functionally to the audit committee.
- **Flip condition:** if the company files for IPO, SOX ICFR scoping expands and the plan re-weights toward financial-reporting controls; a major breach would pull IT/cyber forward.

## Guardrails

- Never reflex "audit everything every year" — rank by **residual risk** and allocate finite hours to the top of the stack, with a defensible cycle for the rest.
- Score on a **documented, consistent scale** so the ranking survives audit-committee challenge; don't hand-wave the priorities.
- State the **coverage gap** (what you're not auditing and why) explicitly — silent omission is a governance failure.
- Keep IA in the **third line**: assurance and non-owning advisory only. An advisory engagement that ends with IA owning the control is a defect.
- The plan is **board-approved and revisited** as risks move — it's a hypothesis, not a fixed calendar.
- Security-control depth is **not** this skill — route to `cybersecurity-grc`; AML/financial-reg depth → `regulatory-compliance`; ESG assurance → `esg-sustainability-reporting`.
- Volatile claims (IIA Standard versions/effective dates, regulatory triggers, EQA cadence) carry a **retrieval date** and are re-verified before a board commitment. See [`../../knowledge/internal-audit-patterns-2026.md`](../../knowledge/internal-audit-patterns-2026.md).
