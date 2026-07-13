---
name: build-budget-and-reserve-plan
description: "Turn a community association's finances into a board-approvable plan by building the annual operating budget, reading the reserve study (component inventory, remaining useful life, and percent funded — reserve balance ÷ fully-funded balance), choosing a funding plan (full / baseline / threshold), setting the assessment off the reserve study rather than off keep-dues-low, modeling a special assessment versus an association loan when a component fails under-funded, and reviewing the vendor contracts and the insurance/master policy — returning the recommended budget, assessment, and reserve plan with adequacy certification flagged to a reserve specialist. Reach for this when the user asks what should dues be, are our reserves adequate, special assessment or a loan, or what do I check on the master policy. Used by association-management-lead (primary)."
---

# Skill: build-budget-and-reserve-plan

> **Invoked by:** `association-management-lead` (primary). Also consulted by `governance-and-covenant-specialist` for the budget/cash-flow impact of delinquency and fine revenue.
>
> **When to invoke:** "What should dues be next year?"; "are our reserves adequate?"; "special assessment or a loan?"; "review the management contract / master policy"; any move from an association's financial picture to a board-approvable budget and reserve plan.
>
> **Output:** the operating budget + the reserve read (percent funded) + a funding plan (full/baseline/threshold) + the recommended assessment + the special-assessment-vs-loan model (if applicable) + the vendor/insurance read, with reserve *adequacy certification* flagged to a reserve specialist. Capture it in [`../../templates/annual-budget-and-reserve-plan.md`](../../templates/annual-budget-and-reserve-plan.md).

## Procedure

1. **Name the finance/ops sub-branch first.** Budget/assessment, reserves/funding, special-assessment-vs-loan, vendor/contract, or insurance/master-policy — traverse [`../../knowledge/community-association-decision-tree.md`](../../knowledge/community-association-decision-tree.md) before prescribing.
2. **Read percent funded before you touch the assessment.** Pull the reserve study: the component inventory (each component's replacement cost and **remaining useful life**), the current reserve **balance**, the **fully-funded balance**, and the resulting **percent funded** (balance ÷ fully-funded balance). The balance flatters; percent funded is the honest number. See [`../../knowledge/community-association-patterns-2026.md`](../../knowledge/community-association-patterns-2026.md). **Adequacy *certification* is a reserve specialist's/engineer's determination — you frame it, you don't certify it.**
3. **Choose the funding plan deliberately.** **Full** (target ~100% funded — highest dues, lowest special-assessment risk), **baseline/cash-flow** (keep the balance above zero — lowest dues, highest special-assessment risk), or **threshold** (fund to a chosen percent-funded floor — the middle path). Don't default to baseline because it keeps dues lowest — that is the choice that produces the surprise special assessment.
4. **Build the operating budget and set the assessment off both halves.** Sum the operating lines (management, utilities, insurance, landscaping, admin, contingency) plus the reserve contribution from the chosen funding plan; the total ÷ the assessable units/lots (by the allocation the documents specify) is the assessment. Set it off the reserve study, not off "keep dues low."
5. **Model special assessment vs loan when a component fails under-funded.** Show the **special assessment** (lump sum / few installments — immediate, no interest, politically hard) against the **association loan** (financed, repaid through assessments — spreads cost, adds interest), the per-owner impact of each, and the approval/notice steps. Note any member-vote or cap the state/documents impose (verify).
6. **Review vendors and the master policy as board controls.** Confirm competitive bids, defined scope, and defined term on the management and service contracts; read the master policy for the **property / general-liability / D&O / fidelity** coverage and the condo **unit-boundary** question. Flag gaps before renewal.
7. **State the flip conditions and the seams.** Name the 1-2 facts that would change the assessment call, route the governance/collections side to the specialist, the *certification* to a reserve specialist, and the legal question to counsel.

## Worked example

> User: "Our reserve has $180k in it — that feels fine. What should dues be next year?"

- **Sub-branch:** reserves/funding + budget/assessment.
- **Reserve read:** the $180k *balance* is not the number. The reserve study's **fully-funded balance** is $510k → **percent funded ≈ 35%** — the roofs (RUL 3 years, $220k) and the private road (RUL 5 years, $160k) are close and under-funded. "Feels fine" is exactly the trap.
- **Funding plan:** the association has been on **baseline** funding (why the balance looks okay while percent funded is low). Model **threshold** (fund toward a 50% floor) and **full** — show the dues delta and the special-assessment risk each carries.
- **Assessment:** operating budget $240k + a reserve contribution that moves toward the chosen threshold → the new assessment, with the reserve rationale on the record so owners see *why* dues move.
- **Special-assessment risk:** if the board stays on baseline, model the ~$220k roof special assessment landing in 3 years (≈ per-unit lump sum) vs a loan — so the choice is explicit, not a surprise.
- **Seam:** the reserve study's adequacy *certification* is the reserve specialist's; a delinquency denting reserve contributions routes to the governance specialist's collections ladder.

## Guardrails

- Never set the assessment before reading **percent funded** — the reserve balance flatters.
- The reserve study's *adequacy certification* is a reserve specialist's/engineer's determination — this skill frames adequacy, it does not certify it.
- Don't default to baseline funding because it keeps dues lowest — name the special-assessment risk it carries.
- A special assessment vs a loan is a modeled trade-off (per-owner impact, interest, approval/notice), not a reflex — show both.
- Vendor contracts get competitive bids + scope + term; the master policy is read for property/liability/D&O/fidelity gaps — insurance is a control, not a renewal formality.
- The legal question (assessment caps, member-vote requirements, notice rules) routes to counsel; volatile claims (statutes, CAM-software features, insurance norms) carry a **retrieval date** — re-verify before a board commitment.
