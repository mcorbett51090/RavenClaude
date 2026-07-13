---
name: manage-valuation-liability-and-claims
description: "Handle the regulated liability side of a household-goods move — explain and set valuation coverage (released value ~60c/lb, the default liability limit, vs full-value protection) and hold the line that valuation is a liability level and NOT insurance, assemble the required documents and federal disclosures (order for service, Bill of Lading, inventory, 'Your Rights and Responsibilities When You Move', 'Ready to Move?'), and run the loss & damage claims process on the valuation basis the customer elected, flagging interstate-FMCSA vs intrastate-state law with a retrieval date and marking the whole thing operational guidance, NOT legal advice. Reach for this when the user asks 'released value or full-value protection?', 'what disclosures must I give?', 'what goes on the Bill of Lading?', or 'how do I handle a damage claim?'. Used by `moving-compliance-and-claims-specialist` (primary)."
---

# Skill: manage-valuation-liability-and-claims

> **Invoked by:** `moving-compliance-and-claims-specialist` (primary). Also consulted by `moving-operations-lead` for the valuation option shown *on the estimate* and the disclosures that must accompany it.
>
> **When to invoke:** "Released value or full-value protection?"; "what disclosures/paperwork must I give an interstate customer?"; "what goes on the Bill of Lading?"; "a customer is claiming damage — how do I handle it?"; any move onto the valuation/liability/disclosures/claims path.
>
> **Output:** the valuation explainer + the required document/disclosure set + a **state/federal-flagged, retrieval-dated** claims workflow (captured in [`../../templates/valuation-and-claims-timeline.md`](../../templates/valuation-and-claims-timeline.md)), every step marked **operational guidance, not legal advice**, with the legal/licensing determination routed to counsel / the state authority / FMCSA.

> ⚠️ **Authority, tariff, valuation, licensing, and claims mechanics vary by state/federal law, change, and this skill is operational guidance — NOT legal advice.** The ~60¢/lb figure, the federal disclosure requirements, and the claims rules are **regulated** and volatile; attach the **state/federal + a retrieval date** to every specific claim and route the actual legal/licensing determination to the client's counsel, the **state licensing authority**, and/or **FMCSA**.

## Procedure

1. **Pin interstate vs intrastate first — it selects the regime.** Interstate → **FMCSA** (federal valuation offer, federal disclosures); intrastate → **that state's** rules (vary materially). Record which governs before any valuation/disclosure/claims call. See [`../../knowledge/moving-relocation-patterns-2026.md`](../../knowledge/moving-relocation-patterns-2026.md).
2. **Explain valuation as a liability level, NOT insurance.** **Released value** = the default liability limit, historically **~60¢/lb per article** _(verify against current FMCSA rule + retrieval date)_, no separate charge, minimal payout. **Full-value protection** = the mover repairs/replaces/settles at value, priced separately, customer elects it. If the customer asks about *insurance*, that's a **separate third-party product** — route it out; valuation ≠ insurance.
3. **Set and disclose the valuation election at booking.** The election drives the later claim payout, so it must be **clearly offered, chosen, and documented** at booking — not after. Show both options and their price/coverage difference.
4. **Assemble the required document + disclosure set (interstate).** The **order for service**, the **Bill of Lading** (the contract of carriage + receipt), the **inventory**, and the mandated FMCSA disclosures — **"Your Rights and Responsibilities When You Move"** and **"Ready to Move?"**. Attach a **retrieval date**; verify the current requirements against FMCSA and, where consequential, counsel.
5. **Run a claim on the elected valuation basis.** A loss & damage claim settles on **whichever valuation the customer chose** (released 60¢/lb vs full-value) — the two pay out very differently. Walk: the **filing window** (interstate has a federal minimum — verify), the **documentation** (inventory + BOL + item/damage/value), the mover's **response/settlement timeline**, and the **dispute path** (arbitration where required for interstate — verify).
6. **Flag the not-legal-advice boundary and route out.** Attach the **state/federal flag + retrieval date** to every regulated step; the exact figures, disclosure requirements, filing windows, and arbitration rules are **legal/licensing determinations** — route them to counsel / the state authority / FMCSA.

## Worked example

> User: "A customer says we scratched their dining table on an interstate move and wants $2,000. They took released value. How do I handle the claim?"

- **Regime pinned:** interstate → **FMCSA**; the claim is **state/federal-flagged and not legal advice** — the current filing window, arbitration requirement, and figures must be verified against FMCSA `[verify — FMCSA claims rule, retrieval date]` and, where consequential, counsel.
- **Governing valuation:** the customer elected **released value (~60¢/lb)** — so the payout is **weight-based**, not the item's market value. A ~120-lb table pays out on the order of ~$72 at 60¢/lb, **not** $2,000. This is why the election at booking governs the outcome.
- **Process:** confirm the claim is within the **filing window**; pull the **inventory + BOL** to document the table's condition at loading; respond within the required **timeline**; settle on the released-value basis; if disputed, follow the **arbitration/dispute path**.
- **Prevention note:** had the customer elected **full-value protection**, the exposure and the conversation would be very different — which is the case for offering and documenting it clearly at booking.
- **Routed out:** the exact figures, filing window, arbitration requirement, and any dispute are legal questions → counsel / FMCSA.
- **Captured in** [`../../templates/valuation-and-claims-timeline.md`](../../templates/valuation-and-claims-timeline.md) with the state/federal flag.

## Guardrails

- **Not legal advice, and state/federal-specific** — every valuation, disclosure, authority, and claims step carries the **state/federal flag + a retrieval date**; the determination routes to counsel / the state authority / FMCSA.
- **Valuation is a liability level, NOT insurance** — never let a customer conflate released value / full-value protection with a third-party insurance product; route the insurance question out.
- **Pin interstate vs intrastate before anything** — it selects the entire regulatory regime; never assume one state's or the federal rule covers the other.
- **The claim settles on the elected valuation basis** — released 60¢/lb and full-value pay out very differently; the outcome is fixed at booking, so offer and document the election clearly.
- **Never dispatch an interstate move without confirmed USDOT/MC operating authority** — route the authority check before the job runs.
- The **~60¢/lb figure, the federal disclosure titles/requirements, filing windows, and arbitration rules are volatile** — carry a **retrieval date** and re-verify against current FMCSA/state rules before a client commitment.
