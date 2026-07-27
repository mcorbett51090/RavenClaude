# Knowledge — Tax-preparation-practice decision trees

> **Last reviewed:** 2026-07-17 · **Confidence:** Medium-High (consensus on the engagement-acceptance, entity→form routing, review-gate, extension, and notice-response framings, and on the engagement-letter-before-preparation and separate-eyes-review disciplines; **specific forms, line numbers, dollar thresholds, phase-outs, filing deadlines, and Circular 230 clause numbers are volatile and jurisdiction-specific — re-verify against current IRS/state guidance before filing**).
> The most-asked practice questions are "should we accept this client?", "which form does this entity file?", "who reviews before e-file?", "do we extend?", "how do we answer this notice?", and "should this client be an S-corp?". These are the decision trees the `tax-practice-lead` and `tax-preparation-specialist` traverse **before** accepting an engagement, routing a form, or naming a position, plus the trade-off tables and the seams to adjacent plugins.

The team's discipline: **the engagement letter and organizer come before the first keystroke; review is a separate step by a separate set of eyes; an extension is a tool, not a failure; and a position is defensible before it is aggressive.** This is **not legal, tax, or accounting advice** and does not replace a credentialed preparer — volatile forms/thresholds/deadlines carry a retrieval date and are verified at use. Bookkeeping / monthly-close questions — the *ledger the return sits on* — leave this layer for `accounting-bookkeeping`; investment advisory leaves for `wealth-management-ria`.

---

## Decision Tree 1: engagement accept / decline (screen before the season)

Gate on **competence, niche fit, and risk** — a bad client accepted in January is a liability in April.

```mermaid
graph TD
  Start([New / returning client]) --> COMP{Inside our competence & niche?<br/>Circular 230 competence}
  COMP -->|No — outside expertise| DECLINE[DECLINE or refer<br/>· don't learn on the client's return]
  COMP -->|Yes| RISK{Risk screen}
  RISK -->|Missing records · aggressive expectations · prior-preparer red flags| DECLINE2[DECLINE or condition acceptance<br/>· document the reason]
  RISK -->|Conflict of interest| CONFLICT[Resolve / waiver per Circular 230<br/>· or decline]
  RISK -->|Clean| SCOPE[Scope the engagement<br/>· which returns · which years · what's NOT included]
  SCOPE --> LETTER[[Engagement letter + organizer<br/>BEFORE the first keystroke<br/>· scope · fee basis · responsibilities · docs standard]]
  LETTER --> PRICE{Pricing model}
  PRICE -->|Standard, defined scope| FLAT[Per-return / flat + scope clause]
  PRICE -->|Planning-heavy / complex| VALUE[Value-based]
  PRICE -->|Open scope / representation| HOURLY[Hourly]
```

---

## Decision Tree 2: entity → form routing

The **entity drives the form**; the **form drives the schedules**. A wrong form is a wrong return.

```mermaid
graph TD
  Start([What entity is filing?]) --> TYPE{Entity type}
  TYPE -->|Individual| F1040[Form 1040<br/>· Sch A itemized · B int/div · C sole-prop<br/>· D cap gains · E rental/K-1 · SE self-employment]
  TYPE -->|C corporation| F1120[Form 1120<br/>· entity-level tax]
  TYPE -->|S corporation| F1120S[Form 1120-S<br/>· K-1s to shareholders<br/>· REASONABLE COMPENSATION before distributions]
  TYPE -->|Partnership / multi-member LLC| F1065[Form 1065<br/>· K-1s to partners<br/>· basis / at-risk / §704 capital accounts]
  F1120S --> PASS[Pass-through → owner 1040<br/>· K-1 flows to Sch E]
  F1065 --> PASS
  F1040 --> QBI{Pass-through / Sch C income?}
  PASS --> QBI
  QBI -->|Yes| S199A[QBI / §199A deduction<br/>· SSTB limit · W-2 wage / UBIA limit]
  QBI -->|No| DONE[Prepare schedules from source docs]
  S199A --> DONE
```

---

## Decision Tree 3: preparation → review → e-file (the review gate)

**Self-review is not the review gate.** A separate set of eyes signs off before e-file.

```mermaid
graph TD
  Start([Documents intaken]) --> COMPLETE{Completeness check<br/>vs prior year + expected schedules}
  COMPLETE -->|Gaps — missing W-2/K-1/1099/basis| REQUEST[Request the missing docs<br/>· do NOT prepare on incomplete data]
  COMPLETE -->|Complete| PREP[Prepare on the right form<br/>· tie each figure to its schedule<br/>· flag judgment positions]
  PREP --> SELF[Self-review vs the checklist<br/>· carryovers · prior-year compare · diagnostics]
  SELF --> TIER{Complexity vs my sign-off tier}
  TIER -->|Above my tier| UP[Escalate to a senior reviewer]
  TIER -->|Within tier| REVIEW[[SEPARATE reviewer sign-off<br/>HARD GATE before e-file]]
  UP --> REVIEW
  REVIEW --> DEADLINE{Can we file accurately by the deadline?}
  DEADLINE -->|Yes| EFILE[Collect 8879 → e-file under EFIN<br/>→ TRACK acknowledgment to ACCEPTED]
  DEADLINE -->|No — late data / complexity| EXT[File EXTENSION 4868/7004<br/>· PAY estimated balance WITH it<br/>· extension is to file, not to pay]
  EFILE --> REJECT{Accepted?}
  REJECT -->|Rejected| FIX[Fix reject code → re-transmit<br/>· a rejected return is NOT filed]
  REJECT -->|Accepted| FILED[Return filed]
```

---

## Decision Tree 4: IRS / state notice response

**Identify the type and deadline first**; a CP2000 is a *proposed* change, not a bill and not an audit.

```mermaid
graph TD
  Start([Client received a notice]) --> ID{Identify the notice type}
  ID -->|CP2000 — document-matching| PROPOSED[PROPOSED change, not a bill/audit<br/>· hard response deadline]
  ID -->|CP14 — balance due| BALANCE[Balance-due notice<br/>· pay or installment agreement]
  ID -->|CP3219 / stat. notice of deficiency| DEFICIENCY[90-day letter<br/>· Tax Court clock → refer to attorney]
  PROPOSED --> RECON[Reconcile agency figures vs the return]
  BALANCE --> RECON
  RECON --> MATCH{Notice right or wrong?}
  MATCH -->|Right — missed item| AGREE[AGREE · corrected balance + payment/installment]
  MATCH -->|Wrong — basis/wash-sale/already-reported| DISAGREE[DISAGREE · explanation + substantiation]
  MATCH -->|Mix| PARTIAL[PARTIALLY AGREE · both]
  AGREE --> POSTURE
  DISAGREE --> POSTURE
  PARTIAL --> POSTURE
  DEFICIENCY --> POSTURE
  POSTURE{Representation posture} -->|CP reply · 2848/8821| HANDLE[Preparer handles<br/>· respond calmly, on time]
  POSTURE -->|Exam / appeals / collections / Tax Court| REFER[[Refer beyond credentials<br/>→ tax attorney / legal-small-firm]]
```

---

## Decision Tree 5: entity-choice planning (SE-tax vs S-corp), with QBI

Model the **combined** SE-tax-vs-S-corp trade-off **with** the §199A interaction — not each alone.

```mermaid
graph TD
  Start([Profitable pass-through / sole-prop]) --> INCOME{Net income above the S-corp break-even?}
  INCOME -->|No / marginal| STAY[Stay as-is<br/>· all net income = SE tax<br/>· S-corp cost not yet justified]
  INCOME -->|Yes| SCORP{Model the S-corp}
  SCORP --> COMP[Set REASONABLE compensation<br/>· wages = payroll tax<br/>· distributions = no SE/payroll tax]
  COMP --> COST{Saving > added cost?<br/>payroll + 1120-S + state fees + reasonable-comp exposure}
  COST -->|No| STAY
  COST -->|Yes| QBI[Layer QBI / §199A<br/>· S-corp WAGES REDUCE the QBI base<br/>· SSTB & wage/UBIA limits]
  QBI --> OPT[Optimize the COMBINED optimum<br/>· comp too low = QBI + audit exposure<br/>· comp too high = lost SE-tax saving]
  OPT --> LEVERS[Retirement + timing levers<br/>· SEP / solo-401k / DB · bracket timing<br/>· scenarios + assumptions + current-law verify]
```

---

## Trade-off table — pricing models

| Model | Sweet spot | Watch out for |
|---|---|---|
| **Per-return / flat** | Standard, defined-scope returns; rewards efficiency | Needs a tight scope clause — the quietly-tripling return kills realization |
| **Value-based** | Planning-heavy or high-complexity work | Requires articulating the value; harder to quote up front |
| **Hourly** | Open-scope projects, representation, messy clean-ups | Client wants a cap; discipline the time tracking |
| **Per-form add-on** | Extra schedules beyond the base engagement | Reserve it in the engagement letter or you can't bill it |

## Trade-off table — extension vs rush-to-file

| Choice | Sweet spot | Watch out for |
|---|---|---|
| **File on time** | Complete data, within reviewed-hours | Rushing incomplete/complex work to beat the date → errors, amended returns |
| **Extension (4868 / 7004)** | Late data, high complexity, capacity peak | It's to *file*, not to *pay* — pay the estimated balance with it or interest+penalty run |
| **Amended (1040-X / 1120-X)** | A genuine post-filing correction | Not a substitute for getting it right — flags the return, re-opens the clock |

## Trade-off table — entity choice

| Structure | Sweet spot | Watch out for |
|---|---|---|
| **Sole-prop / single-member LLC** | Low net income; simplicity | All net income hit by SE tax |
| **S-corp (1120-S)** | Net income above the break-even; wages + distribution split | Reasonable-comp exposure; payroll + 1120-S + state cost; wages reduce QBI |
| **Partnership (1065)** | Multiple owners; flexible allocations | SE tax on general partners; basis/at-risk/§704 complexity |
| **C-corp (1120)** | Retained earnings, certain benefits, some scale plays | Double taxation; a bigger, separate analysis — often a `legal-small-firm` seam |

---

## Seams (this team owns the return and the practice, not the whole finance stack)

- **The books / monthly close / write-up / bookkeeping** → `accounting-bookkeeping` (the *ledger* the return is prepared from; tax reads it, doesn't keep it).
- **Investment advisory / financial planning / portfolio** → `wealth-management-ria` (the *investment* side of a plan; tax owns the return).
- **Corporate FP&A / budgeting / the earnings plan** → `finance`.
- **Entity-formation law, a legal opinion, exam/appeals/Tax-Court representation beyond preparer credentials** → `legal-small-firm` (or a tax attorney).
- **Deep AML / BSA / sanctions program** → `regulatory-compliance`.
- **Verifying a volatile claim** (a form, line number, threshold, phase-out, deadline, or Circular 230 clause) → `ravenclaude-core/deep-researcher`.

---

## Provenance

- Durable framings (the engagement-letter-and-organizer-before-preparation discipline, entity→form routing, the separate-eyes review gate, the extension as a load valve, completeness-check-before-prep, identify-notice-type-and-deadline-first, the SE-tax-vs-S-corp-with-QBI combined model, defensible-before-aggressive positions) are consensus US tax-practice practice reviewed 2026-07-17 — **Medium-High confidence**.
- Specific forms, line numbers, dollar thresholds, phase-outs, filing deadlines, safe-harbor percentages, and Circular 230 clause numbers are **volatile and jurisdiction-specific**, carry retrieval dates, and are **not legal/tax/accounting advice** — re-verify with `ravenclaude-core/deep-researcher` and against current IRS/state guidance (and confirm with a credentialed preparer) before filing. _(Reviewed 2026-07-17.)_
