---
name: plan-and-execute-audit-engagement
description: "Plan and execute a single internal-audit engagement by traversing the internal-audit decision tree (assurance-vs-advisory → scope & criteria → sampling approach → evidence), then return the planning memo, the risk & control matrix (risk → control → type → tests), the walkthrough, the test of design + test of operating effectiveness with an attribute-sampling plan and sample size, and review-ready workpapers. Reach for this when the user asks 'draft the planning memo and RCM', 'how do we test this control?', 'what sample size?', or 'are our workpapers sufficient?'. Used by audit-engagement-specialist (primary)."
---

# Skill: plan-and-execute-audit-engagement

> **Invoked by:** `audit-engagement-specialist` (primary). Also consulted by `internal-audit-lead` to confirm a planned engagement is scopeable and resourced before it enters the annual plan.
>
> **When to invoke:** "draft the planning memo / scope this engagement"; "build the risk & control matrix"; "test of design vs test of operating effectiveness — how?"; "what's the attribute-sample size?"; "are these workpapers sufficient/review-ready?"; any "how do we run this engagement's fieldwork?" question.
>
> **Output:** the planning memo (objectives/scope/criteria/approach/timing) + the risk & control matrix + the walkthrough result + the test-of-design and test-of-operating-effectiveness plan with sampling approach & sample size + the workpaper/evidence sufficiency note. (Findings + ratings are the sister skill `rate-and-report-audit-findings`.)

## Procedure

1. **Restate the engagement in the tree's terms.** Capture: the **auditable area** (from the plan), the **objectives**, whether it's **assurance** or **advisory**, the **period** under review, the **population/data** available, and the **criteria** universe (which policies, regulations, frameworks, or standards define the "should-be").
2. **Write the planning memo first.** Fix **objectives**, **scope** (in and explicitly out), the **key risks** in scope, the **criteria**, the **approach**, the **timing/budget**, and the **stakeholders**. No fieldwork before scope and criteria are set — you cannot conclude against a bar you haven't named.
3. **Build the risk & control matrix (RCM).** For each key risk: name the **control(s)**, the **control type** (preventive vs detective, manual vs automated, key vs non-key, entity- vs process-level), and the two planned tests — **test of design** and **test of operating effectiveness**. The RCM is the engagement's spine.
4. **Walk through before you test operation.** A **walkthrough** (one transaction end-to-end) confirms your understanding and the **design** of the control. A control that fails design can't operate effectively — flag it now rather than sampling a broken design.
5. **Traverse the decision tree** in [`../../knowledge/internal-audit-decision-tree.md`](../../knowledge/internal-audit-decision-tree.md) for the test approach:
   - **automated control** with reliable ITGCs → a **single (or few) well-tested instance(s)** can substitute for a large attribute sample,
   - **manual control** → **attribute sampling**: derive the **sample size** from the population size, the **control frequency** (annual/quarterly/monthly/weekly/daily/many-per-day), and the **tolerable vs expected deviation** rate — not a habitual "25",
   - name the **selection method** (random / systematic / haphazard) and the **definition of a deviation**,
   - for a quantitative/monetary conclusion consider **monetary-unit (dollar-unit) sampling**; for full-population testing use **data analytics / CAATs**.
6. **Test and document to the evidence bar.** Perform the test of operating effectiveness; capture in the **workpaper** the objective, the test performed, the population, the sample and selection, the result, the **deviations**, and the **conclusion** — evidence must be **sufficient, relevant, and reliable** (inspection / re-performance / third-party > inquiry alone), with a reference and review trail.
7. **Conclude and hand off.** State whether the controls over the in-scope risks are designed effectively and operating effectively; route deviations to `rate-and-report-audit-findings` for 5-C write-up and rating. State the flip conditions (a compensating control found, a population wider than assumed).

## Worked example

> User: "We're auditing procure-to-pay. Draft the memo and RCM, and how do we test the three-way-match control (~4,000 POs/year)?"

- **Planning memo:** objective — assurance that P2P controls prevent unauthorized/inaccurate disbursements; scope — PO creation → three-way match → payment for the FY; **out of scope** — vendor master governance (separate engagement); criteria — the P2P policy, delegation-of-authority matrix, and segregation-of-duties standard.
- **RCM:** risk "payment without valid PO/receipt" → control "system three-way match (PO ↔ receipt ↔ invoice) before payment", type **preventive / automated / key**; tests = **design** (does the config actually block a mismatch?) + **operating effectiveness** (did it over the year?).
- **Walkthrough:** push one transaction through; confirm the match is enforced by config, not a manual override.
- **Because it's an automated control with reliable ITGCs:** test the **configuration once** plus a small confirmatory sample (e.g. 25 attempts including forced mismatches), rather than an attribute sample sized for a manual control. If ITGCs are *weak*, revert to a manual-control **attribute sample** sized from the ~4,000 population, control frequency (many/day), and a 0% tolerable-deviation posture for a key control.
- **Workpaper:** config evidence + the mismatch-block test screenshots + the conclusion, referenced and review-signed.
- **Flip condition:** if manual overrides to the match exist, the automated conclusion collapses and the override population needs its own attribute sample.

## Guardrails

- **Scope and criteria before fieldwork** — no conclusion without a named "should-be."
- **Walkthrough / test design before testing operation** — sampling a badly designed control wastes the sample.
- **The sample size is a calculation** (population × frequency × tolerable/expected deviation), not a reflexive "25"; for a key control the tolerable deviation is often near zero.
- **Automated + reliable ITGCs** lets one well-tested instance stand in for a large sample; **weak ITGCs** force you back to attribute sampling — the ITGC conclusion gates the reliance.
- **Evidence is sufficient, relevant, reliable, and in the workpaper** — inquiry alone is the weakest evidence; corroborate with inspection or re-performance.
- IA **tests and concludes**; it does not own or design the control. Keep the engagement independent.
- Volatile claims (framework versions, sample-size tables, regulatory criteria) carry a **retrieval date** and are re-verified before finalizing. See [`../../knowledge/internal-audit-patterns-2026.md`](../../knowledge/internal-audit-patterns-2026.md).
