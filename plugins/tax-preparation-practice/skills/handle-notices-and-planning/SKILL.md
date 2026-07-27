---
name: handle-notices-and-planning
description: "Respond to an IRS/state notice and run the planning calc by traversing the practice decision tree (identify the notice type & deadline → reconcile the agency figures vs the return → agree/partial/disagree response + substantiation → representation posture: handle vs refer; and for planning: entity-choice SE-tax vs S-corp reasonable-comp → QBI/§199A → retirement & timing levers as scenarios), then return the notice-response plan or the planning scenarios with assumptions and the verify-against-current-law caveat. Reach for this when the user asks 'we got a CP2000 / CP notice — how do we respond?', 'should this client be an S-corp?', 'how do we optimize QBI / retirement / timing?', or 'what's our representation posture?'. Used by tax-preparation-specialist (primary) and tax-practice-lead."
---

# Skill: handle-notices-and-planning

> **Invoked by:** `tax-preparation-specialist` (primary — the notice response and the planning calc) and `tax-practice-lead` (the representation posture and the planning offering).
>
> **When to invoke:** "the client got a CP2000 / CP notice — how do we respond?"; "identify this IRS/state notice and the deadline"; "should this client be an S-corp?"; "how do we optimize QBI / §199A?"; "retirement-plan or timing levers?"; "what's our representation stance — handle or refer?"; any "answer this notice or plan the tax" question.
>
> **Output:** the notice-response plan (type & deadline, reconciliation, agree/partial/disagree + substantiation, handle-vs-refer) **or** the planning scenarios (entity choice, QBI, retirement, timing) with stated assumptions and the verify-against-current-law caveat.

## Procedure — notices

1. **Identify the notice type and the response deadline first.** A **CP2000** is a *proposed* change from document-matching — **not a bill and not an audit** — with a hard response deadline; a **CP14** is a balance-due notice; a **CP2000/CP3219** can escalate to a statutory notice of deficiency (the "90-day letter"). Traverse the notice branch in [`../../knowledge/tax-preparation-practice-decision-tree.md`](../../knowledge/tax-preparation-practice-decision-tree.md). **The deadline governs everything** — calendar it before anything else.
2. **Reconcile the agency's figures against the return.** Match the IRS/state numbers line by line to what was filed — the notice is often right (a missed 1099), sometimes wrong (a basis the IRS didn't have, a wash sale, a already-reported-differently item). You can't respond until you know which.
3. **Draft the agree / partially-agree / disagree response with substantiation.** **Agree** → the corrected balance + payment or installment path. **Disagree** → the explanation + the **substantiation** (the basis records, the corrected 1099, the code section) that supports the return as filed. **Partially agree** → both. Respond **calmly and on time** — a notice answered fast beats one ignored, which becomes a lien or a deficiency.
4. **Set the representation posture — know where preparer help ends.** A notice-response and a CP2000 reply are ordinary **preparer** work (with authorization — 2848 POA / 8821). But **exam / audit, appeals, collections, and Tax Court** cross into representation that a firm handles only to the extent of its credentials (an EA/CPA has practice rights before the IRS; **Tax Court** requires admission) — refer beyond that to a tax attorney / `legal-small-firm`.

## Procedure — planning

5. **Entity choice — model the SE-tax vs S-corp trade-off.** For a profitable sole-prop/partnership, compare **staying as-is** (all net income hit by **self-employment tax**) vs an **S-corp** (reasonable **wages** subject to payroll tax + **distributions** that aren't) — net of the **added cost** (payroll, a separate 1120-S, state fees, and the reasonable-comp exposure if wages are set too low). The S-corp wins above a net-income threshold where the SE-tax saving beats the added cost — model it, don't assume it.
6. **Layer in QBI / §199A.** The 20% **qualified-business-income deduction** interacts with entity choice: the **SSTB** limitation (specified service trades phase out at higher income), the **W-2-wage / UBIA** limits, and the fact that **S-corp wages reduce QBI** — so the reasonable-comp level trades off SE-tax saving against QBI. Model the interaction, not each in isolation.
7. **Retirement and timing levers, then caveat everything.** Retirement-plan choice (SEP-IRA vs solo-401(k) vs defined-benefit for high earners) shifts income and builds basis; **timing** levers (income deferral/acceleration across a bracket, bunching deductions, harvesting losses, estimated-payment timing) smooth the bracket. Present all planning as **scenarios with stated assumptions** and mark each against **current-law verification** — thresholds and phase-outs change yearly. Route investment-dependent planning to `wealth-management-ria`.

## Worked example

> User: "Client got a CP2000 saying they owe $4,200 on unreported brokerage sales — and separately, they're netting $140K in a Schedule C consulting business. Handle the notice and the planning."

- **Notice — type & deadline:** CP2000 (document-matching, *proposed*) — **calendar the response deadline first**.
- **Reconcile:** the IRS saw **gross proceeds** ($60K) with **no basis** (the broker didn't report basis on older lots) — the actual **gain** is ~$8K, not $60K. The notice overstates the tax.
- **Respond:** **disagree (partial)** — supply the **basis substantiation** (purchase confirms) and the corrected Schedule D; the real additional tax is ~$1,200, not $4,200. Respond on time with the workpapers.
- **Posture:** this is preparer work with an 8821/2848 — **no attorney needed** unless it escalates to a deficiency notice or exam.
- **Planning — entity:** $140K Schedule C → all subject to **SE tax** (~$19–20K). Model an **S-corp**: e.g. $70K reasonable wages + $70K distribution saves SE/payroll tax on the distribution, net of ~$2–3K added payroll/compliance cost → a real saving *above* the added cost.
- **QBI interaction:** the S-corp **wages reduce the §199A base**, so push the reasonable-comp level too low and you gain SE-tax saving but lose QBI — **model the combined** optimum, and check the consulting-SSTB phase-out against the client's total income.
- **Retirement/timing:** a **solo-401(k)** (or SEP) defers income and can drop the bracket; caveat all figures against **current-year thresholds** and refer the investment allocation to `wealth-management-ria`.

## Guardrails

- **Identify the notice type and calendar the deadline before anything else** — a CP2000 is a *proposed* change, not a bill and not an audit; the deadline governs.
- **Reconcile before responding** — the notice is sometimes right, sometimes wrong; substantiate a disagree with records/code section.
- **A notice answered fast and calmly beats one ignored** — ignored becomes a lien or a deficiency.
- **Know where preparer representation ends** — CP-notice replies are preparer work (2848/8821); exam/appeals/collections/Tax Court refer to a tax attorney / `legal-small-firm` (Tax Court requires admission).
- **Entity choice and QBI are one model, not two** — S-corp reasonable-comp trades SE-tax saving against the §199A base; model the combined optimum, and reasonable comp too low is an exam exposure.
- **Planning is scenarios with stated assumptions** — never a promise; mark every threshold/phase-out against current-law verification.
- Investment-dependent planning → `wealth-management-ria`; the books → `accounting-bookkeeping`. This is **not** tax, legal, or accounting advice and does not replace a credentialed preparer — forms, thresholds, and deadlines are volatile; carry a **retrieval date**. See [`../../knowledge/tax-preparation-practice-patterns-2026.md`](../../knowledge/tax-preparation-practice-patterns-2026.md).
