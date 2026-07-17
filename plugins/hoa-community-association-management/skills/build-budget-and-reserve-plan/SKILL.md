---
name: build-budget-and-reserve-plan
description: "Build an annual operating + reserve budget, set the assessment (dues) level, and set the reserve-funding policy by traversing the community-association decision tree (association authority & governing docs → operating budget → reserve study & percent-funded target → funding method → assessment level → major-project funding: raise reserves / special assessment / association loan / phase), then return the budget, the dues level, the reserve-funding recommendation, the major-project plan, and the conditions that change it. Reach for this when the user asks 'build our annual budget', 'what should the assessments be?', 'how much do we fund the reserves?', 'are our reserves underfunded?', or 'special assessment, loan, or phase the project?'. Used by association-management-lead (primary) and community-operations-specialist."
---

# Skill: build-budget-and-reserve-plan

> **Invoked by:** `association-management-lead` (primary — the budget, assessment, and reserve-funding policy) and `community-operations-specialist` (for the budgeted assessment and reserve line a billing run needs).
>
> **When to invoke:** "build our annual budget"; "what should the assessments (dues) be?"; "how much should we fund the reserves?"; "is our reserve fund underfunded?"; "special assessment, association loan, or phase the roof replacement?"; any "what do we budget and charge" question.
>
> **Output:** the operating + reserve budget + the assessment (dues) level + the reserve-funding policy (percent-funded target + method) + the major-project funding plan + the 1-2 conditions that change it.

## Procedure

1. **Confirm the authority first — the governing documents bound the budget.** Before numbers, check the **CC&Rs / bylaws / articles** and the state condo/HOA act for what the board may do without a member vote: an **assessment-increase cap** (a percent limit per year is common), the **special-assessment threshold** (some require a membership vote above a dollar amount), and any **reserve-study or reserve-funding mandate**. Traverse the authority branch in [`../../knowledge/hoa-community-association-decision-tree.md`](../../knowledge/hoa-community-association-decision-tree.md). A budget the documents don't authorize isn't a budget.
2. **Build the operating budget from the recurring cost of running the community.** Line up the recurring expenses — **management fee, insurance (master policy), utilities (common areas), landscaping/grounds, routine repairs & maintenance, trash, pool/amenity operations, administrative, taxes/audit, and a contingency**. Base each line on the prior year actuals + known changes (a renewed insurance premium, a new landscaping contract), not last year's budget echoed forward.
3. **Set the reserve contribution from the reserve study — not the board's mood.** The **reserve study** inventories the major replaceable components (roofs, roads/asphalt, elevators, painting, pool, fencing, HVAC), each with a **remaining useful life** and **replacement cost**, and produces a **funding plan**. Read the study's **percent-funded** status (reserve balance ÷ fully-funded balance) and pick a **funding method**: **full funding** (target ~100% funded — lowest special-assessment risk), **baseline** (keep the balance above zero across the horizon), **threshold** (hold a chosen floor), or the **statutory minimum**. The reserve line is the study's recommended annual contribution for the chosen method.
4. **Set the assessment (dues) to cover operating _plus_ reserves.** `Annual assessment per unit ≈ (operating budget + reserve contribution) ÷ the ownership-allocation formula` (equal per unit, by unit size / percentage interest, or per the declaration). Check the increase against the **cap** from step 1 — if covering reserves needs more than the cap allows, that's a flag: hold dues down and you underfund reserves (a special assessment later), or seek the member vote. Don't quietly starve reserves to hit a dues target.
5. **For a major project, pick the funding path by the trade-offs.** When a big component is near end-of-life (roofs due in 5 years, roads failing), traverse the major-project branch: **raise reserve contributions now** (spreads cost, least disruptive, needs lead time), **special assessment** (one-time member charge — fast, but painful and may need a vote), **association loan** (spreads cost over time at an interest cost — preserves cash, adds debt), or **phase the work** (do it in stages as funds allow — risks the component failing mid-phase). Compare member burden, cost of capital, and timing risk; flag the vote threshold and any statutory limit for counsel.
6. **State the change conditions** — the 1-2 facts that move the budget/assessment/reserve plan (e.g., "if the insurance premium renews up 40%, the operating budget and the assessment rise"; "if the next reserve-study update shortens the roof's remaining life, the reserve contribution must step up or the special-assessment risk grows").

## Worked example

> User: "We're a 120-unit condo, reserves at 35% funded, roofs due in ~6 years at ~$1.2M. Build our budget and tell us what to charge and how to fund the roofs."

- **Authority:** the declaration caps a board-only assessment increase at 10%/yr; a special assessment over $1,000/unit needs a two-thirds member vote — note both.
- **Operating:** management + insurance (renewing +15%) + utilities + landscaping + pool + admin + contingency = **$720K/yr**.
- **Reserve (from the study):** 35% funded is thin with a $1.2M roof 6 years out. Full-funding contribution ≈ **$260K/yr**; baseline ≈ $190K/yr. Recommend stepping toward full funding.
- **Assessment:** ($720K + $260K) ÷ 120 units ≈ **$8,170/unit/yr (~$680/mo)** — but that reserve step may exceed the 10% cap vs the prior dues; either phase the increase over two years or take the reserve piece to a vote.
- **Roof funding:** raising reserves now over 6 years is cleanest if the cap allows; if not, a special assessment or an association loan closer to the replacement — compare member burden vs interest cost. Flag the vote threshold to counsel.
- **Change condition:** if the reserve study's next update shortens roof life to 3 years, the raise-reserves path loses runway → special assessment or loan moves to the front.

## Guardrails

- **Read the governing documents and the state act first** — the assessment cap, special-assessment vote threshold, and reserve mandate bound everything.
- Budget **operating _and_ reserves** — an operating-only budget that starves reserves is a special assessment waiting to happen.
- Fund reserves **on the study, not the mood of the board** — pick a percent-funded target and method deliberately; deferring is borrowing from the future at a bad rate.
- Set the assessment to the **true cost of ownership**; if the cap blocks proper reserve funding, surface the trade-off — don't hide it by underfunding.
- The budget & reserve-funding **policy** is the `association-management-lead`'s call; the billing execution is the `community-operations-specialist`'s — keep the seam clean.
- This is **not** the association's audit or tax return (`accounting-bookkeeping`), and **not** financial advice; investing the reserve cash is `treasury-management` (safety > liquidity > yield).
- Volatile specifics (assessment caps, special-assessment vote thresholds, reserve-study standards, statutory reserve mandates) are **jurisdiction-specific** — carry a **retrieval date**, verify at use, and route legal questions to counsel. See [`../../knowledge/hoa-community-association-patterns-2026.md`](../../knowledge/hoa-community-association-patterns-2026.md).
