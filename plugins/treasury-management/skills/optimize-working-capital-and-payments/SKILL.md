---
name: optimize-working-capital-and-payments
description: "Optimize working capital and harden the payments flow by traversing the treasury decision tree (cash-conversion cycle: DSO/DIO/DPO levers → DPO extension vs supply-chain finance / dynamic discounting → DSO reduction → inventory financing → payment-method choice → payment fraud controls: positive pay, dual auth, SoD, BEC), then return the working-capital levers ranked by cash freed, the payment-method recommendation, and the fraud-control setup. Reach for this when the user asks 'how do we free up working capital?', 'should we extend DPO or offer supply-chain finance?', 'how do we reduce DSO?', 'which payment method?', or 'set up positive pay / dual authorization / BEC controls'. Used by cash-and-risk-operations-specialist (primary) and treasury-strategy-lead."
---

# Skill: optimize-working-capital-and-payments

> **Invoked by:** `cash-and-risk-operations-specialist` (primary — the working-capital execution and the payment-controls setup) and `treasury-strategy-lead` (the controls policy and the DPO/DSO strategy).
>
> **When to invoke:** "how do we free up working capital / cash?"; "extend DPO or offer supply-chain finance / dynamic discounting?"; "how do we reduce DSO?"; "should we finance inventory?"; "which payment method (wire / ACH / card / RTP / check)?"; "set up positive pay / dual authorization / BEC / vendor-bank-change controls."
>
> **Output:** the working-capital levers ranked by cash freed (and their cost/relationship trade-offs) + the payment-method recommendation + the payment-fraud-control setup (positive pay, dual auth, SoD, BEC verification) — with the seams named.

## Procedure

1. **Anchor on the cash-conversion cycle (CCC).** `CCC = DSO + DIO − DPO` (days sales outstanding + days inventory outstanding − days payable outstanding). Every working-capital lever moves one of these three; the CCC in days × daily sales ≈ the cash tied up in operations. Compute it first so levers are ranked by **cash freed**, not by ease.
2. **Reduce DSO — collect faster, without buying the sale twice.** Levers: tighter credit terms / credit limits, invoice accuracy & e-invoicing (disputes are the silent DSO killer), electronic payment options, disciplined collections/dunning, and early-pay incentives (weigh the discount cost vs the days saved). Traverse the DSO branch in [`../../knowledge/treasury-management-decision-tree.md`](../../knowledge/treasury-management-decision-tree.md).
3. **Extend DPO — but choose the mechanism.** Extending payment terms frees cash, but pushed too far it strains suppliers and invites price increases. The structured alternatives:
   - **Supply-chain finance (reverse factoring)** — a bank/platform pays the supplier early at the *buyer's* credit rating; the buyer keeps (or extends) its DPO while the supplier gets cheaper, faster cash. Best when the buyer's rating is materially better than the suppliers'. **Watch the accounting/disclosure** — aggressive SCF that effectively converts payables to debt draws scrutiny (rating agencies / disclosure rules).
   - **Dynamic discounting** — the *buyer* uses its **own cash** to pay early for a sliding discount. Best when the buyer is cash-rich and the discount yield beats its short-term investment alternative — it's a working-capital *investment*, the mirror image of SCF.
4. **Finance inventory only where it earns it.** DIO reduction (demand planning, SKU rationalization, consignment/VMI) frees cash structurally; **inventory financing / warehouse receipts** bridge a seasonal build but cost interest — use for a timing gap, not a permanent DIO problem.
5. **Choose the payment method by cost, speed, finality, and control.** Wire (fast, final, expensive — high-value/urgent), **ACH** (cheap, batch, reversible window — payroll/vendors at volume), **card** (rebate/float but merchant cost + acceptance), **RTP / instant rails** (fast + final for time-critical), **check** (declining, highest fraud exposure — minimize). Match the method to the payment's value, urgency, and finality need.
6. **Harden the disbursement flow — fraud controls are non-negotiable.**
   - **Positive pay** (issued-check file to the bank; mismatches held for review) / **reverse positive pay**; **ACH debit blocks/filters** on the accounts.
   - **Dual authorization** and **segregation of duties**: initiator ≠ approver ≠ reconciler on every payment run.
   - **BEC / vendor-impersonation defense:** any **vendor bank-detail change** is verified by a **callback to a known number** (never the number on the change request), and payment-instruction emails claiming urgency are treated as suspect. BEC is the dominant loss vector.
   - **Sanctions screening** on the payee is required — but deep OFAC/AML program design routes to `regulatory-compliance`.
7. **Rank and name the seams.** Present the levers ranked by cash freed vs cost/relationship risk; route supplier-term *negotiation* to `procurement-sourcing`, rail/API *engineering* to `fintech-payments-engineering`, the AML/OFAC *program* to `regulatory-compliance`, and a controls *audit* to `internal-audit`.

## Worked example

> User: "We're cash-rich but our CCC is 68 days. Free up working capital and tighten our payment controls."

- **CCC:** DSO 55 + DIO 40 − DPO 27 = **68 days**. At ~$1M/day sales that's ~$68M tied up — the DSO and low DPO are the levers.
- **DSO (55 → ~45):** e-invoicing to kill dispute lag, offer ACH/RTP payment, and disciplined dunning — ~10 days ≈ **~$10M** freed.
- **DPO (27, cash-rich):** rather than strong-arm terms, run **dynamic discounting** — use the surplus cash to pay early for a discount whose annualized yield beats the money-market alternative (a working-capital *investment*, not an extension). If some suppliers need the opposite, offer **SCF** so they get early cash at your rating while you hold DPO.
- **Payment method:** move vendor runs to **ACH** (from checks) for cost + fraud reduction; wires only for high-value/urgent.
- **Controls:** stand up **positive pay** + ACH debit blocks, enforce **dual auth + SoD** on the run, and make **vendor-bank-change callbacks** mandatory (BEC defense).
- **Seam:** the actual term renegotiation goes to `procurement-sourcing`; the ACH/RTP integration to `fintech-payments-engineering`.

## Guardrails

- Compute the **CCC (DSO + DIO − DPO)** first — rank levers by **cash freed**, not by which is easiest.
- **DPO extension has a supplier-health limit** — pushed too far it returns as price increases or supply risk; prefer **SCF** (supplier gets your rating) or **dynamic discounting** (you invest surplus cash) over strong-arming terms.
- **SCF has an accounting/disclosure trap** — aggressive reverse factoring can look like hidden debt to rating agencies/regulators; flag it, don't hide it.
- **Dynamic discounting is an investment decision** — only when the discount yield beats the short-term investment alternative and the cash isn't needed for the buffer.
- **Payment fraud controls are non-negotiable:** positive pay, dual auth + SoD (initiator ≠ approver ≠ reconciler), and **callback verification of every vendor bank-detail change** — BEC is when-not-if.
- Minimize **checks** — they carry the highest fraud exposure of any method.
- Supplier-term *negotiation* → `procurement-sourcing`; rail/API *code* → `fintech-payments-engineering`; deep AML/OFAC → `regulatory-compliance`; controls *audit* → `internal-audit`.
- This is **not** legal, tax, or accounting advice; SCF disclosure treatment and payment-rail specifics are volatile — carry a **retrieval date**. See [`../../knowledge/treasury-management-patterns-2026.md`](../../knowledge/treasury-management-patterns-2026.md).
