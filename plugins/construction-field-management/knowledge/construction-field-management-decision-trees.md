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

_Seam reference: design intent / drawings / BIM → `architecture-aec`; master CPM schedule, risk, RAID → `project-management`; trade means-and-methods and subcontract scope → `skilled-trades-contracting`. Re-verify any standard, form edition, or contract term before quoting it to an owner or building off it._
