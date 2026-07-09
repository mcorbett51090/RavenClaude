---
name: run-delinquency-and-lien-process
description: Run a self-storage tenant from first missed payment to lien auction as a disciplined, state-specific process — start with prevention (autopay enrolment, late-fee discipline), then walk the statutory lien timeline (late fees → gate lockout/overlock → pre-lien and lien notices → advertising/public notice → auction via StorageTreasures/Lockerfox → sale of goods → surplus handling), flagging at every step that lien law varies by US state, attaching the state and a retrieval date, and marking the whole thing operational guidance and NOT legal advice. Reach for this when the user asks "I have tenants 60+ days past due — what now?", "walk me through the lien and auction process", "when can I overlock a unit?", or "how do I handle auction surplus?". Used by `storage-revenue-and-occupancy-specialist` (primary).
---

# Skill: run-delinquency-and-lien-process

> **Invoked by:** `storage-revenue-and-occupancy-specialist` (primary). Also consulted by `self-storage-operations-lead` for the operational overlock / gate-lockout mechanics.
>
> **When to invoke:** "I have past-due tenants — walk me through the lien and auction"; "when can I overlock / lock out a defaulting tenant?"; "how do I advertise and run the auction?"; "how do I handle the surplus?"; any move down the delinquency-to-auction path.
>
> **Output:** a prevention review + a **state-flagged, retrieval-dated** delinquency-to-lien timeline (captured in [`../../templates/delinquency-lien-timeline.md`](../../templates/delinquency-lien-timeline.md)), every step marked **operational guidance, not legal advice**, with the legal question routed to counsel.

> ⚠️ **Lien law varies materially by US state, the statutes change, and this skill is operational guidance — NOT legal advice.** The self-storage lien is a **statutory** process with strict notice contents, delivery methods, and timing that differ by state; a mis-stepped or mis-timed notice can **void the sale** and expose the operator. Attach the **state + a retrieval date** to every specific claim and route the actual legal question to the client's counsel.

## Procedure

1. **Start with prevention — it's far cheaper than any lien step.** Confirm **autopay enrolment** (a card on file that runs automatically is the single most effective delinquency control) and a disciplined **late-fee** schedule per the rental agreement (amounts/caps vary by state — verify). Most roll-to-delinquent is preventable here. See [`../../knowledge/self-storage-patterns-2026.md`](../../knowledge/self-storage-patterns-2026.md).
2. **Pin the state and the governing rule up front.** Before any step, record **which US state** governs and note that the timeline is **state-specific and not legal advice**. Retrieve/confirm the current statute with a retrieval date; if unverified, mark it `[unverified — verify against <state> statute]` and say so.
3. **Late fee → default clock.** After grace, apply the first late fee; the default clock the state defines starts. Record dates in the timeline template.
4. **Gate lockout / overlock.** Deny gate access and/or place an **overlock** on the unit so a defaulting tenant can't remove goods while in default. *When* this is permitted is state-specific — verify. (The operations lead owns the physical overlock; the economics and timing are the specialist's.)
5. **Pre-lien / default notice.** Send the notice of default and intent to enforce the lien, by the **method and after the delay the state requires** (verify contents + delivery method).
6. **Lien notice.** Send the formal lien notice with the required contents (amount owed, deadline, that the goods will be sold) by the required delivery method (certified/verified mail, or email where the state allows). This is the step most often mis-executed — verify contents and method precisely.
7. **Advertising / public notice.** Advertise the sale as the state requires — newspaper and/or a designated online platform, for the required number of publications/days (verify).
8. **Auction / sale.** Conduct the sale — commonly online via **StorageTreasures** or **Lockerfox**, or a live/onsite auction (platform terms volatile — verify). Follow the state's rules on bidder terms and sale conduct.
9. **Sale of goods → apply proceeds.** Apply proceeds to unpaid rent, fees, and sale costs in the **state-specified order**.
10. **Surplus handling — a frequent liability source.** Any **surplus** over what's owed must be handled per state law (commonly held for / returned to the tenant, or escheated). Mishandling surplus is a common source of operator liability — verify the state rule and document the handling.

## Worked example

> User: "I have a tenant 65 days past due in Texas. When can I auction the unit?"

- **State pinned:** Texas governs; the timeline below is **state-specific and not legal advice** — the specific Texas statute days/notice contents must be confirmed against the current statute `[verify — TX Property Code self-service storage lien, retrieval date]` and with counsel.
- **Prevention check:** was the tenant on autopay? If a card failed, a retry + call may resolve it before the lien path.
- **Sequence (verify each against TX statute):** late fees already applied → overlock the unit → send the notice(s) with the required contents and delivery method → advertise as required → auction (e.g. via StorageTreasures) → apply proceeds → **hold/return any surplus** per TX rule.
- **Routed to counsel:** the exact notice contents, delivery method, waiting periods, and surplus rule are legal questions — this skill sequences the operational steps; counsel confirms the statute.
- **Captured in** [`../../templates/delinquency-lien-timeline.md`](../../templates/delinquency-lien-timeline.md) with each date and the state flag.

## Guardrails

- **Not legal advice, and state-specific** — every step carries the state + a retrieval date; the legal question routes to the client's counsel.
- Prevention (autopay + late-fee discipline) comes first — it's cheaper than any lien step.
- Never skip or compress a notice/waiting step to auction faster — a mis-timed or mis-addressed notice can void the sale.
- Overlock timing, notice contents, delivery method, advertising requirements, and surplus handling **all vary by state** — verify each; never assume one state's rule applies to another.
- Surplus handling is a frequent liability source — document it and verify the state rule.
- Auction-platform terms (StorageTreasures/Lockerfox) and PMS delinquency-automation features are volatile — carry a retrieval date and re-verify.
