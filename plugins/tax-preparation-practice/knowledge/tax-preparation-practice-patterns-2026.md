# Knowledge — Tax-preparation-practice patterns (2026)

> **Last reviewed:** 2026-07-17 · **Confidence:** High on the durable concepts (the engagement-letter/organizer intake discipline, the entity→form map, the preparation→separate-review→e-file pipeline, extensions vs estimates, the notice-response and representation framing, the entity-choice/QBI/retirement/timing planning levers, and the Circular 230 / PTIN / EFIN professional-standards fence); **Medium on the dated regulatory/threshold/deadline map — forms, line numbers, dollar thresholds, phase-outs, filing deadlines, and Circular 230 clause numbers change every year and carry retrieval dates below.**
> The reference the `tax-preparation-specialist` reads when intaking documents, preparing and reviewing returns, filing extensions and estimates, responding to notices, and running the planning calc — plus a 2026 standards/tooling snapshot. **This is not legal, tax, or accounting advice and does not replace a credentialed preparer; volatile specifics carry a retrieval date and are verified at use before filing.**

The team's discipline: **open with the engagement letter and organizer; check completeness before preparing; match the form to the entity; self-review then hand to a separate reviewer before e-file; extend to protect accuracy; answer notices fast and calmly; and model planning as caveated scenarios.**

---

## The engagement — letter and organizer before the first keystroke

- **Engagement letter** — the written scope, fee basis, responsibilities (client provides X; firm does Y), documentation standard, and the **limits** (what's *not* included). It is the scope-creep and fee-dispute control, and it's a professional-standards expectation. No letter, no return.
- **Client organizer** — the structured intake that drives document collection and the completeness check; a prior-year comparison built in surfaces the missing schedule.
- **Completeness check** — reconcile the intake against the **prior-year return** and the **expected schedules** (every W-2, 1099-INT/DIV/B/NEC/R, K-1, brokerage basis, and the entity books) **before** preparation. The gap found before prep is a request; found at review it's re-work; found after filing it's an amended return.
- **Kickoff sequence:** signed engagement → organizer sent → documents in → completeness gate → prepare. Skipping the gate is the single most common source of re-work.

---

## Entity → form map

| Entity | Return | Key schedules / questions |
|---|---|---|
| **Individual** | **Form 1040** | Sch A (itemized), B (int/div), C (sole-prop + SE tax), D (cap gains), E (rental / K-1 pass-through), SE (self-employment) |
| **C corporation** | **Form 1120** | Entity-level tax; separate from the owners |
| **S corporation** | **Form 1120-S** | K-1s to shareholders; **reasonable compensation** (wages before distributions); pass-through to owner 1040 |
| **Partnership / multi-member LLC** | **Form 1065** | K-1s to partners; **basis / at-risk / §704(b)** capital accounts; SE tax on general partners |

> The **entity drives the form**; the **form drives the schedules**. A pass-through (1120-S / 1065) issues **K-1s** that flow to the owner's **1040 Schedule E** — a return isn't done until the K-1 ties. _(Form/schedule specifics are volatile — retrieved 2026-07-17.)_

---

## The preparation → review → e-file pipeline

- **Prepare from source documents**, tie each figure to its schedule, reconcile to the books/organizer, and **flag the judgment positions** (home-office allocation, QBI determination, basis/at-risk limitation) for the reviewer rather than burying them.
- **Self-review** — the preparer's own pass against the checklist: carryovers (NOLs, capital losses, passive losses, credits), prior-year comparison, e-file diagnostics, direct-deposit info, signatures.
- **Separate-reviewer sign-off (the hard gate)** — a **different set of eyes** reviews and signs off **before e-file**. Self-prepared-and-self-reviewed is a risk, not an efficiency; the review tier scales with complexity, and work above a preparer's sign-off tier goes up.
- **E-file mechanics** — collect **Form 8879** (e-file signature authorization) before transmitting, file under the firm's **EFIN**, and **track the acknowledgment**: an **accepted** ack is a filed return; a **rejected** one is not — reconcile the reject code and re-transmit. _(E-file rules are volatile — retrieved 2026-07-17.)_

---

## Extensions & quarterly estimates

- **Extensions** — **Form 4868** (individual) / **Form 7004** (business) extend the time **to file**, typically six months. **An extension is not an extension to pay** — the estimated balance is due at the original deadline; **pay it with the extension** or interest and the failure-to-pay penalty run. An extension filed to protect accuracy under deadline pressure is a *tool*, not a failure.
- **Quarterly estimates** — for income without withholding (self-employment, S-corp distributions, investment income). Two common bases:
  - **Prior-year safe harbor** — pay **100%** of the prior-year tax (**110%** for higher-income taxpayers) to avoid the underpayment penalty regardless of the current year.
  - **Annualized method** — pay on the actual income earned each period; better for lumpy/seasonal income.
- **Underpayment penalty (Form 2210 / 2220)** — the exposure when estimates fall short of the safe harbor; flag it and set the payment calendar. _(Safe-harbor percentages and thresholds are volatile — retrieved 2026-07-17.)_

---

## IRS / state notices & representation posture

- **Identify the type and the deadline first.** A **CP2000** is a **proposed** change from IRS document-matching — **not a bill and not an audit** — with a hard response deadline. A **CP14** is a balance-due notice. A **CP3219 / statutory notice of deficiency** ("90-day letter") starts the **Tax Court** clock. The deadline governs everything.
- **Reconcile then respond** — match the agency figures to the return; the notice is often right (a missed 1099), sometimes wrong (basis the IRS didn't have, a wash sale, an already-differently-reported item). Respond **agree / partially agree / disagree** with substantiation, **calmly and on time**. A notice answered fast beats one ignored, which becomes a lien or a deficiency.
- **Representation posture — know the line.** A CP-notice reply is ordinary **preparer** work with authorization (**Form 2848** power of attorney / **8821** information authorization). An **EA or CPA** has practice rights before the IRS (exam, appeals, collections within limits); **Tax Court** requires admission (attorneys, or non-attorneys who pass the Tax Court exam). Refer exam/appeals/collections beyond the firm's credentials, and Tax Court, to a tax attorney / `legal-small-firm`.

---

## Tax-planning levers (scenarios with assumptions, never a promise)

- **Entity choice** — a profitable sole-prop/partnership pays **self-employment tax** on all net income; an **S-corp** splits **reasonable wages** (payroll tax) from **distributions** (no SE/payroll tax), net of the added payroll/1120-S/state cost. The S-corp wins above a break-even where the SE-tax saving beats the added cost — **model it**, and set reasonable comp defensibly (too low is an exam exposure).
- **QBI / §199A** — the 20% qualified-business-income deduction, subject to the **SSTB** limitation (specified service trades phase out at higher income) and the **W-2-wage / UBIA** limits. It **interacts with entity choice**: S-corp **wages reduce the QBI base**, so reasonable comp trades SE-tax saving against QBI — optimize the **combined** figure, not each alone.
- **Retirement plans** — SEP-IRA, **solo-401(k)**, SIMPLE, and defined-benefit (for high, stable earners) defer income and build basis; the plan choice shifts the bracket.
- **Timing** — income deferral/acceleration across a bracket boundary, **bunching** itemized deductions into alternate years, **loss harvesting**, and estimated-payment timing — bracket-smoothing levers. Route investment-dependent moves to `wealth-management-ria`.

> **Volatile + not tax advice:** every threshold, phase-out, deduction limit, and safe-harbor percentage changes — treat the above as durable *mechanics* and **verify each figure against current-year law** before advising or filing. _(Retrieved 2026-07-17.)_

---

## Professional standards — the fence the practice operates inside

- **PTIN** — every paid preparer needs a current **Preparer Tax Identification Number** on every return they prepare.
- **EFIN** — the firm needs an **Electronic Filing Identification Number** in good standing to e-file; safeguard it (it's a target for identity theft).
- **Circular 230** — Treasury's rules of practice: **competence** (don't prepare beyond your expertise), **due diligence** (reasonable reliance and inquiry), **conflict-of-interest** rules, and the standards for advising on positions. Preparer-penalty exposure (unreasonable positions, willful understatement) sits here too.
- **Due-diligence documentation** — refundable-credit due diligence (EITC / CTC / AOTC — **Form 8867**) and the general obligation to document the basis for positions.
- **Disclosure** — a position that doesn't meet the substantial-authority / reasonable-basis standard may need **adequate disclosure** (**Form 8275**) — defensible-before-aggressive.
- **Data security / WISP** — a **Written Information Security Plan** is a professional and FTC-Safeguards obligation for firms handling taxpayer data; it's part of the license to operate. _(Circular 230 clause numbers, form numbers, and the WISP obligation are volatile — retrieved 2026-07-17.)_

---

## Busy-season practice management

- **Capacity** — model **return volume × preparer-hours** (by complexity band) against **available preparer *and reviewed* hours** across the compressed Jan–Apr window. **Review** capacity is usually the binding constraint, not prep.
- **Staffing** — the **preparer → reviewer** split; don't let review be the step cut when the queue backs up.
- **Extension policy** — extend late-data and high-complexity returns by default to protect accuracy and smooth the peak.
- **Pricing / realization** — per-return/flat (needs a scope clause), value-based (planning-heavy), or hourly (open-scope/representation); defend **realization** (billed vs collected vs hours sunk) against scope creep with the engagement-letter clause.

---

## 2026 standards & tooling map (dated — volatile, re-verify before quoting)

- **Filing & e-file:** e-file under the firm **EFIN**; **Form 8879** authorizes each e-filed return; track acknowledgments to *accepted*. _(Retrieved 2026-07-17; e-file rules change.)_
- **Professional credentials:** **PTIN** (per preparer), **EFIN** (per firm), **Circular 230** rules of practice, **2848/8821** for representation authorization. _(Retrieved 2026-07-17.)_
- **Forms map (durable identifiers, verify line-level detail):** 1040 / 1120 / 1120-S / 1065 returns; 4868 / 7004 extensions; 1040-X / 1120-X amended; 2210 / 2220 underpayment; 8275 disclosure; 8867 due diligence; 8879 e-file auth. _(Form availability/versions volatile — retrieved 2026-07-17.)_
- **Software tiers:** professional prep software (1040 + business modules), a document-management / portal system, and e-signature — the practice stack. Vendor landscape volatile — verify at selection. _(Retrieved 2026-07-17.)_
- **Thresholds & deadlines:** standard deduction, QBI phase-outs, SE-tax rate/wage base, estimated-payment safe-harbor percentages, and all filing deadlines **change yearly and by jurisdiction** — never quote from memory; verify against current IRS/state guidance. _(Retrieved 2026-07-17.)_

---

## Provenance

- Durable concepts (the engagement-letter/organizer-before-preparation discipline, the completeness check, the entity→form map, the preparation→separate-review→e-file pipeline, the 8879/EFIN e-file mechanics, extensions vs estimates and file≠pay, the safe-harbor vs annualized estimate methods, the CP-notice identify-type-and-deadline-first framing and the preparer-vs-attorney representation line, the SE-tax-vs-S-corp-with-QBI entity-choice model, the retirement/timing levers, and the Circular 230 / PTIN / EFIN / WISP professional-standards fence) are consensus US tax-practice practice reviewed 2026-07-17 — **High confidence**.
- The regulatory/threshold/deadline map — specific forms, line numbers, dollar thresholds, phase-outs, filing deadlines, safe-harbor percentages, and Circular 230 clause numbers — is a **2026-07 snapshot**; these are volatile and jurisdiction-specific, carry the retrieval dates above, and are **not legal/tax/accounting advice and do not replace a credentialed preparer** — re-verify with `ravenclaude-core/deep-researcher` and against current IRS/state guidance before pinning in a client deliverable or filing. _(Reviewed 2026-07-17.)_
