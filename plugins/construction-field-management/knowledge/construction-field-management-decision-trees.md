# Construction Field Management — Decision Trees

_Decision trees + a dated standards/forms map. Map rows are `[verify-at-build]` — re-check against the current AIA/EJCDC/OSHA source and the specific contract before quoting. Last reviewed: 2026-06-08._

Traverse before sending an RFI, sequencing a submittal, deciding whether a field event is a change order, or setting a QA hold point.

## Decision Tree: Is this field event a change order, or just an RFI / no-cost clarification?

Scope-bearing answers get priced *before* they're built; pure clarifications don't.

```mermaid
graph TD
  A[Field condition / RFI answer / owner directive] --> B{Does it change scope, cost, or time vs. the contract documents?}
  B -- No, it only clarifies intent --> C[RFI clarification only - log the answer, no change; proceed]
  B -- Yes --> D{Is the design intent ambiguous / a documents conflict?}
  D -- Yes --> E[Send an RFI first - get the design answer; the answer may resolve at no cost or confirm a change]
  D -- No, it is clearly added/changed work --> F{Has it been priced and time-impacted yet?}
  F -- No --> G[Stop - price it as a PCO/COR and assess time impact BEFORE it is built]
  F -- Yes --> H{Is the change executed/authorized in writing?}
  H -- No --> I[Get a signed CO or written directive; proceeding on a verbal is a claim risk]
  H -- Yes --> J[Execute the CO, update SOV + budget + schedule, then build]
```

_Nothing scope-bearing gets built unpriced. A verbal "just do it" with no written authorization is how margin disappears and disputes start._

## Decision Tree: When must this submittal / inspection happen relative to the work?

Schedule backward from the need/install date; a hold point gates the next activity.

```mermaid
graph TD
  A[Item needed in the field] --> B{Is it a submittal for material to be installed?}
  B -- Yes --> C[Required-by = install date - lead time - review time]
  C --> D{Is the required-by date already in the past?}
  D -- Yes --> E[Late now - escalate as a schedule risk; expedite review or re-sequence]
  D -- No --> F[Log it with ball-in-court + required-by; track to approved/approved-as-noted]
  B -- No, it is an inspection / QA check --> G{Does it gate work that will be covered up?}
  G -- Yes --> H[Hold point - work cannot proceed past until inspected and signed off]
  G -- No, observe only --> I[Witness point - inspect during, do not stop the work]
  H --> J{Special inspection or AHJ required?}
  J -- Yes --> K[Schedule the special inspector / AHJ against the activity; confirm before cover-up]
  J -- No --> L[Internal QA sign-off at the hold point before next activity]
```

_If the required-by math lands in the past, the item is already late — surface it now, not the week of install. A hold point with no teeth is a checkbox._

## Decision Tree: How do I bill this change — PCO/COR, CCD, or hold?

A change is two columns — cost *and* time — and it gets authorized in writing before it's built and before it's billed.

```mermaid
graph TD
  A[Added/changed work identified] --> B{Is scope, cost, and time impact defined yet?}
  B -- No --> C[Price it as a PCO/COR; assess the time impact and route it to project-management]
  B -- Yes --> D{Is the price agreed with the owner?}
  D -- Yes --> E[Execute the CO - update SOV + budget + schedule, then bill on the next pay app]
  D -- No, but work cannot wait --> F{Will the owner issue a written directive?}
  F -- Yes --> G[Construction change directive / NTE - proceed under written authorization; reconcile price later]
  F -- No --> H[Do not build - proceeding on a verbal is a waived-claim risk; escalate]
  E --> I{Does the CO change contract time?}
  I -- Yes --> J[Route the time-impact to project-management; update the schedule + any LD exposure]
  I -- No --> K[Cost-only CO; log it with ball-in-court to executed]
```

_A change with no time-impact analysis is half-priced. Nothing scope-bearing gets billed before it's executed or covered by a written directive._

## Decision Tree: Is the cost report honest — what does the cost-to-complete say?

"Under budget" is a mirage until committed, actual, forecast, and CTC all tie by cost code.

```mermaid
graph TD
  A[Cost report shows under/over budget] --> B{Are all approved/pending changes posted to the budget?}
  B -- No --> C[Post the changes first - an unposted CO hides the real budget]
  B -- Yes --> D{Are signed subcontracts/POs counted as committed, even if unbilled?}
  D -- No --> E[Add unbilled commitments - committed money is real cost; leave it out and the report lies]
  D -- Yes --> F{Is there a cost-to-complete by cost code, not just actuals-vs-budget?}
  F -- No --> G[Build the CTC - forecast remaining cost per code; that is the honest number]
  F -- Yes --> H{Projected final cost vs. budget by code?}
  H -- Over on a code --> I[Flag the overrun now, name the driver, route any time-impact to project-management]
  H -- Within budget --> J[Report committed/actual/forecast/CTC + projected final cost - the real picture]
```

_Unbilled commitments are real money. The cost report lies the month before the overrun lands if the CTC is missing._

## Decision Tree: Is this job ready for substantial completion / closeout?

Substantial completion is not final completion; closeout is the assembled package that releases retainage.

```mermaid
graph TD
  A[Approaching the finish] --> B{Is the punch list driven to zero by responsible trade?}
  B -- No --> C[Not substantially complete - close the punch list first, re-inspect each item]
  B -- Yes --> D{Are AHJ/final inspections passed and the certificate of occupancy issued?}
  D -- No --> E[Schedule final inspections against the activities they gate; hold closeout until passed]
  D -- Yes --> F{Is the package assembled - O&M, as-builts/record drawings, warranties, attic stock?}
  F -- No --> G[Assemble + verify the missing deliverable - it is the cash-flow item holding retainage, not paperwork]
  F -- Yes --> H{Is the retainage-release milestone in the contract met?}
  H -- No --> I[Confirm the contract trigger - substantial vs. final; verify state retainage law]
  H -- Yes --> J[Submit closeout + final pay app to release retainage]
```

_An incomplete closeout package is usually what's actually holding the owner's money — treat the missing deliverable as the cash-flow item it is._

---

## Standards / forms map (2026, `[verify-at-build]`)

| Area | Standard / form | Notes |
|---|---|---|
| Pay application | AIA G702 Application and Certificate for Payment + G703 Continuation Sheet | The continuation sheet carries the SOV line items; verify the current AIA edition and the contract's required form `[verify-at-build]` |
| Contract family (alt) | EJCDC, ConsensusDocs | Some owners use EJCDC/ConsensusDocs instead of AIA — confirm which governs before building a pay app/CO `[verify-at-build]` |
| Schedule of values | Per the prime contract; tied to cost codes (e.g. CSI MasterFormat divisions) | Front-loading judgment is contract- and owner-specific; abusive front-loading gets the draw rejected `[verify-at-build]` |
| Change documents | PCO (potential change order) / COR (change order request) / CO (change order); construction change directive (CCD) | Terminology varies by contract; a CCD authorizes work before price is agreed — verify the contract's change clause `[verify-at-build]` |
| Retainage | Typically 5-10% withheld; release at substantial/final completion | The % and release milestone come from the specific contract and state retainage law `[verify-at-build]` |
| Schedule method | CPM (critical path method); look-ahead (3-week) | Master CPM build/owns → `project-management`; this plugin coordinates the field to it `[verify-at-build]` |
| QA/QC | Inspection-and-test plan (ITP); hold points / witness points; special inspections (IBC Ch. 17) | Special-inspection scope is set by the building code + the statement of special inspections `[verify-at-build]` |
| Safety | OSHA 29 CFR 1926 (construction); JHA / JSA; toolbox talks; fall protection, excavation, LOTO, scaffolding | OSHA is the floor; the JHA control is the specific one the task needs — verify the current standard `[verify-at-build]` |
| Closeout | Substantial vs. final completion; O&M manuals, as-builts/record drawings, warranties, attic stock, certificate of occupancy | Closeout deliverables and the retainage-release trigger come from the contract `[verify-at-build]` |
| Earned value | CV / SV / CPI / SPI from BCWP (EV) / ACWP (AC) / BCWS (PV); EAC = BAC / CPI | CPI/SPI < 1.0 means over budget / behind schedule; pair the EV read with a real cost-to-complete by code `[verify-at-build]` |
| Field records | Daily logs, RFI/submittal logs, change logs, inspection records, JHAs — written contemporaneously | Contemporaneous records are the project's memory and, in a claim, its evidence; a log written days later from memory is not credible `[verify-at-build]` |

_Runnable check:_ [`../scripts/construction_calc.py`](../scripts/construction_calc.py) computes a G702/G703-style draw (`payapp`), a running adjusted contract sum after change orders (`changeorder`), and earned-value CV/SV/CPI/SPI (`earned-value`) — stdlib-only, for sanity-checking a number before it goes to an owner. It does not replace the contract; verify the retainage %, change clause, and SOV against the prime contract.

_Seam reference: design intent / drawings / BIM → `architecture-aec`; master CPM schedule, risk, RAID → `project-management`; trade means-and-methods and subcontract scope → `skilled-trades-contracting`. Re-verify any standard, form edition, or contract term before quoting it to an owner or building off it._
