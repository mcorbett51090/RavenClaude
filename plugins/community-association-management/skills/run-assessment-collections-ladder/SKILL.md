---
name: run-assessment-collections-ladder
description: "Run a delinquent community-association owner from first missed assessment to lien (and, where applicable, foreclosure) as a disciplined, consistent, state-specific ladder — start with prevention (autopay enrolment and a board-adopted collection policy applied evenly to every owner), then walk the statutory sequence (late fee/interest → reminder and demand → payment-plan offer → pre-lien notice → recorded assessment lien → foreclosure where the state permits it), flagging at every step that collections and lien law varies by US state, attaching the state and a retrieval date, marking the whole thing operational guidance and NOT legal advice, and routing the legal determination and any foreclosure to the association's counsel. Reach for this when the user asks an owner is 90 days delinquent what now, walk me through the assessment lien, when can I lien a unit, or can we foreclose. Used by governance-and-covenant-specialist (primary)."
---

# Skill: run-assessment-collections-ladder

> **Invoked by:** `governance-and-covenant-specialist` (primary). Also consulted by `association-management-lead` for the delinquency's budget/cash-flow impact.
>
> **When to invoke:** "An owner is 90 days delinquent — what now?"; "walk me through the assessment lien"; "when can I lien / record against a unit?"; "can we foreclose the lien?"; "do we have to offer a payment plan?"; any move down the delinquency-to-lien path.
>
> **Output:** a prevention review + a **state-flagged, retrieval-dated** collections-to-lien ladder (captured in [`../../templates/covenant-enforcement-and-collections-timeline.md`](../../templates/covenant-enforcement-and-collections-timeline.md)), every step marked **operational guidance, not legal advice**, with the legal determination and any foreclosure routed to counsel.

> ⚠️ **Collections and lien law varies materially by US state, the statutes change, and this skill is operational guidance — NOT legal advice.** The association's assessment lien is a **statutory** process with strict notice contents, delivery methods, timing, and (in some states) pre-lien and payment-plan requirements that differ by state; a mis-stepped or mis-timed notice can **void the lien**, and foreclosing the lien is squarely a counsel-led legal matter. Attach the **state + a retrieval date** to every specific claim and route the actual legal question to the association's counsel.

## Procedure

1. **Start with prevention — and apply it to EVERY owner consistently.** Confirm **autopay/ACH enrolment** and a **board-adopted collection policy** applied **evenly** to every delinquent owner. Consistency is not only the cheapest control; it is the defense against a selective-enforcement/discrimination claim. See [`../../knowledge/community-association-patterns-2026.md`](../../knowledge/community-association-patterns-2026.md).
2. **Pin the state and the governing rule up front.** Record **which US state** governs and note that the ladder is **state-specific and not legal advice**. Retrieve/confirm the current statute with a retrieval date; if unverified, mark it `[unverified — verify against <state> statute]` and say so. Also confirm the governing documents (some add requirements beyond the statute).
3. **Late fee / interest → the delinquency clock.** After grace, apply the first late fee/interest per the collection policy and state (amounts/caps vary — verify). Record dates in the timeline template.
4. **Reminder → formal demand.** A documented reminder, then a formal demand for the balance — dated and delivered by a recorded method.
5. **Offer a payment plan.** Offer a reasonable payment plan; **some states *require* a plan be offered** before escalating (verify). Document the offer and the response.
6. **Pre-lien notice.** Send the notice of intent to lien with the **required contents and delivery method, after the required delay** — this is highly state-specific and a frequent mis-step. Verify contents + method precisely.
7. **Record the assessment lien.** Record the lien against the unit/lot for the unpaid assessments, fees, and costs, per the state's contents and timing rules. This step is what secures the debt.
8. **Foreclosure — only where applicable, and counsel-led.** Some states permit foreclosing the assessment lien (judicial or non-judicial), often gated by a **minimum amount owed and/or months delinquent** and further notice. This is the **highest-stakes step and squarely a legal matter — route it to counsel**; do not present it as a routine next click.
9. **State the seams.** Route the budget/cash-flow impact of the delinquency to the management lead; route the legal determination and any foreclosure to counsel.

## Worked example

> User: "An owner in California is 90 days behind on dues. When can we lien and foreclose?"

- **State pinned:** California governs (**Davis-Stirling**); the ladder below is **state-specific and not legal advice** — the specific pre-lien notice contents, timing, payment-plan, and foreclosure thresholds must be confirmed against the current statute `[verify — CA Davis-Stirling assessment-collection provisions, retrieval date]` and with counsel.
- **Consistency check:** is the association pursuing every delinquent owner on the same schedule? Selective collection is an exposure — fix it before pursuing one.
- **Prevention:** was the owner on autopay? A failed card + a call may resolve it before the lien path.
- **Sequence (verify each against CA statute):** late fee/interest applied → reminder + formal demand → **offer a payment plan** (CA has specific requirements here) → **pre-lien notice** with the required contents/method/timing → **record the assessment lien** → foreclosure **only** if the amount/time thresholds are met — and that step is **counsel-led**.
- **Routed to counsel:** the exact notice contents, delivery method, waiting periods, payment-plan and foreclosure thresholds are legal questions — this skill sequences the operational steps; counsel confirms the statute and runs any foreclosure.
- **Captured in** [`../../templates/covenant-enforcement-and-collections-timeline.md`](../../templates/covenant-enforcement-and-collections-timeline.md) with each date and the state flag.

## Guardrails

- **Not legal advice, and state-specific** — every step carries the state + a retrieval date; the legal determination and any foreclosure route to the association's counsel.
- **Consistency across owners** is both the cheapest control and the defense against a selective-collection claim — apply the policy evenly.
- Prevention (autopay + a board-adopted policy) comes first — it's cheaper than any lien step.
- Never skip or compress a notice/waiting/payment-plan step to lien or foreclose faster — a mis-timed or mis-addressed notice can void the lien.
- Pre-lien contents, delivery method, timing, payment-plan requirements, lien recording, and foreclosure thresholds **all vary by state** — verify each; never assume one state's rule applies to another.
- Foreclosure is the highest-stakes step and **counsel-led** — never present it as a routine next click.
- CAM-software collections-automation features and statutory figures are volatile — carry a **retrieval date** and re-verify before a board commitment.
