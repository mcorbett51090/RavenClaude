---
name: run-return-preparation-workflow
description: "Run a return from organizer through e-file by traversing the practice decision tree (organizer & completeness check → entity→form routing: 1040 / 1120 / 1120-S / 1065 → preparation & schedules → self-review vs a separate-reviewer gate → e-file & acknowledgment → extensions 4868/7004 & quarterly estimates), then return the prepared return, the completeness gaps, the review findings, the e-file path, and any extension/estimate schedule. Reach for this when the user asks 'prepare this 1040 / 1120-S / 1065', 'which form does this entity file?', 'review this return before e-file', or 'file an extension and set quarterly estimates'. Used by tax-preparation-specialist (primary) and tax-practice-lead."
---

# Skill: run-return-preparation-workflow

> **Invoked by:** `tax-preparation-specialist` (primary — the intake→prep→review→e-file pipeline) and `tax-practice-lead` (to ground the review-standard and workflow policy in the real pipeline).
>
> **When to invoke:** "prepare this 1040 / 1120 / 1120-S / 1065"; "which form does this entity file?"; "run the completeness check on this client's documents"; "review this return before e-file"; "file an extension (4868 / 7004)"; "set up quarterly estimates"; any "prepare and file this return" task.
>
> **Output:** the prepared return (correct form + schedules) + the completeness gaps found + the self-review findings + the **separate-reviewer sign-off gate** + the e-file/acknowledgment path + any extension & quarterly-estimate schedule.

## Procedure

1. **Confirm the engagement, then drive the organizer.** Verify the engagement letter is signed and scoped (see [`plan-engagement-and-capacity`](../plan-engagement-and-capacity/SKILL.md)), then use the **organizer** to intake documents. This is the step before the step — a return prepped on an unsigned engagement is exposure.
2. **Run the completeness check before you prepare.** Reconcile the intake against the **prior-year return** and the **expected schedules** — every W-2, 1099 (INT/DIV/B/NEC/R), K-1, brokerage basis, and the entity's books. The missing basis figure or the un-received K-1 is found **before** prep, not at review — otherwise it's re-work or an amended return.
3. **Route the entity to the form.** Traverse the entity→form branch in [`../../knowledge/tax-preparation-practice-decision-tree.md`](../../knowledge/tax-preparation-practice-decision-tree.md):
   - **1040** — individual, with Schedules A (itemized), B (interest/dividends), C (sole-prop), D (capital gains), E (rental/K-1 pass-through), SE (self-employment tax) as applicable.
   - **1120** — C-corp (entity-level tax).
   - **1120-S** — S-corp: the K-1s to shareholders, and the **reasonable-compensation** question (wages before distributions).
   - **1065** — partnership: the K-1s to partners, and **basis / at-risk / §704(b)** capital accounts.
4. **Prepare from the drivers, not the plug.** Enter from source documents, tie each figure to its schedule, and reconcile the return to the books/organizer — so a review finding is diagnosable, not a hunt. Flag the judgment positions (a home-office allocation, a §199A/QBI determination, a basis limitation) for the reviewer, not buried.
5. **Self-review, then hand to a separate reviewer — the hard gate.** Run your own pass against [`../../templates/return-review-and-efile-checklist.md`](../../templates/return-review-and-efile-checklist.md) (carryovers, prior-year comparison, e-file diagnostics, bank info, signatures/8879). Then **route to a separate set of eyes** for sign-off — **self-review is not the review gate**; the separate reviewer signs off *before* e-file, and complexity above your sign-off tier goes up.
6. **E-file and track the acknowledgment.** Collect the **8879** (e-file authorization) before transmitting, e-file under the firm's **EFIN**, and **track the acknowledgment** (accepted vs rejected — a rejected return is not a filed return). Reconcile any reject code and re-transmit.
7. **Extensions and estimates — deliberately.** If the deadline forces a rush, file the **extension** (4868 individual / 7004 business) and **pay the estimated balance with it** (an extension is to file, not to pay — interest and failure-to-pay penalty still run). Set **quarterly estimates** via the prior-year **safe harbor** (100%, or 110% for higher-income) or the **annualized** method, with the payment calendar and the underpayment-penalty exposure.

## Worked example

> User: "New client — an S-corp with one shareholder-employee and a rental on the side. Prepare and e-file."

- **Engagement:** confirm the signed letter covers the 1120-S *and* the shareholder's 1040 (two engagements or one scoped letter — not assumed).
- **Completeness:** organizer + prior-year 1120-S → intake the books, payroll (the W-2 for the shareholder), the fixed-asset/depreciation schedule, and the rental's income/expense + basis. Gap found: **no reasonable-compensation support** → request before prep.
- **Form routing:** **1120-S** for the entity (K-1 to the shareholder), the shareholder's **1040** with **Schedule E** for both the K-1 pass-through and the rental, **Schedule SE** not triggered by S-corp distributions (that's the reasonable-comp point).
- **Prepare:** book the depreciation, tie the K-1 to the 1040 Schedule E, compute **QBI/§199A** on the pass-through (net of the reasonable-comp wages).
- **Review:** self-review the checklist, then the **separate reviewer** signs off on the reasonable-comp position and the QBI calc before e-file.
- **E-file:** 8879-S and 8879 collected; e-file both; **track both acknowledgments**.
- **Estimates:** set the shareholder's **quarterly estimates** on the S-corp income (safe harbor off the prior year) since there's no withholding on distributions.

## Guardrails

- **Confirm the engagement and run the completeness check before preparing** — a return on incomplete data is re-work or an amended return.
- **The form follows the entity** — 1040 / 1120 / 1120-S / 1065 with the right schedules; a wrong form is a wrong return.
- **Self-review is not the review gate** — a separate set of eyes signs off before e-file; complexity above your tier goes up.
- **A rejected e-file is not a filed return** — collect the 8879, e-file under the EFIN, and track the acknowledgment to *accepted*.
- **An extension is to file, not to pay** — file the 4868/7004 to protect accuracy and pay the estimated balance with it; estimates use the safe-harbor or annualized method.
- Preparing/reviewing the return is the `tax-preparation-specialist`; the review-standard and workflow **policy** is the `tax-practice-lead` — keep the seam clean.
- This is **not** the books / monthly close (`accounting-bookkeeping`) and **not** tax, legal, or accounting advice. Forms, line numbers, thresholds, and deadlines are volatile — carry a **retrieval date** and verify against current IRS/state guidance before filing. See [`../../knowledge/tax-preparation-practice-patterns-2026.md`](../../knowledge/tax-preparation-practice-patterns-2026.md).
