# Public-Sector Grants — Decision Trees

_Decision trees + a dated grant-lifecycle / authority map. Authority rows are `[verify-at-build]` — re-check against the current 2 CFR, the award terms, and the NOFO before quoting any threshold, deadline, or rate. Last reviewed: 2026-06-08._

Traverse before committing to pursue an opportunity, before charging a cost to a federal award, before classifying a sub-award relationship, before pledging a match, and before charging a selected item of cost. Five decision trees follow, then the dated authority map.

## Decision Tree: Go or no-go on this opportunity?

A grant is justified by mission fit and a plausible win + sustainability — not by the dollar amount on offer.

```mermaid
graph TD
  A[New funding opportunity / NOFO] --> B{Are we eligible AND is it on-mission?}
  B -- No --> C[No-go - ineligible or off-mission; a won off-mission grant is a liability]
  B -- Yes --> D{Can we name the funder's review criteria and meet them?}
  D -- No --> E[Research the rubric first; if we still can't map to it, no-go]
  D -- Yes --> F{Is the probability of award worth the cost-to-apply?}
  F -- No --> G[No-go - low win odds vs. high writing/opportunity cost; a disciplined no is a win]
  F -- Yes --> H{Can we fund the match AND sustain the program past the period of performance?}
  H -- No --> I[No-go or defer - the match is real money and the sustainability tail is part of fit]
  H -- Yes --> J[Go - hand the logic model to proposal-writer; flag match/allowability to compliance]
```

_Fund the mission, don't chase the money. Name the cost-to-apply, the probability of award, the strings (match/reporting), and the sustainability tail before writing a word._

## Decision Tree: Is this cost allowable on a federal award?

Every federal dollar passes the three-part test — allowable, allocable, AND reasonable — or it doesn't go on the grant.

```mermaid
graph TD
  A[Proposed cost] --> B{Allowable? Permitted by 2 CFR 200 cost principles AND the award terms - not a prohibited/excluded item}
  B -- No --> C[Unallowable - find another funding source; 'mission-critical' does not override the test]
  B -- Yes --> D{Allocable? Benefits the award in proportion to the amount charged}
  D -- No --> E[Unallowable as charged - allocate only the benefiting share]
  D -- Yes --> F{Reasonable? A prudent person would incur it; consistent with market/policy}
  F -- No --> G[Unallowable - reduce to the reasonable amount or remove]
  F -- Yes --> H{Incurred within the period of performance AND documented?}
  H -- No --> I[Need explicit authority pre-award/post-period AND contemporaneous documentation]
  H -- Yes --> J[Allowable - charge it; keep the documentation; mark advisory for the authorized official]
```

_Allowable, allocable, reasonable — all three, every cost. Decide allowability at the budget stage, not after the award. The determination is advisory; the authorized official signs._

## Decision Tree: Sub-recipient or contractor?

The classification drives the entire monitoring and audit obligation; get it right at the sub-award, by substance not by the agreement's label.

```mermaid
graph TD
  A[Outside party receiving award funds] --> B{Does it carry out part of the PROGRAM and make programmatic decisions?}
  B -- No --> C{Does it provide goods/services in a competitive market to many buyers, within its normal business?}
  C -- Yes --> D[Contractor/vendor - owe PROCUREMENT compliance, not sub-recipient monitoring]
  C -- No --> E[Mixed/ambiguous - make a case-by-case call on substance; document the determination]
  B -- Yes --> F{Is it measured against the program's objectives AND subject to the federal compliance requirements?}
  F -- No --> E
  F -- Yes --> G[Sub-recipient - owe the full chain]
  G --> H[Risk assessment -> flow-down sub-award terms -> ongoing monitoring -> single-audit follow-up]
  H --> I[Their finding becomes YOUR finding - build monitoring contemporaneously, not at audit time]
```

_The sub-recipient is your liability. Substance over form — the agreement's title doesn't decide it, the relationship does. Reconstructed-at-audit monitoring is already a finding._

## Decision Tree: Where does the match / cost-share come from?

A required match is real money, sourced and documented at the proposal — not a number scrambled for each quarter once the award is spent.

```mermaid
graph TD
  A[NOFO/award requires a match or cost-share] --> B{Is the match REQUIRED by the program, or only encouraged?}
  B -- Encouraged only --> C[Pledge only what you can verifiably deliver - an unmet voluntary match committed in the proposal becomes a binding obligation]
  B -- Required --> D{Can you source it from allowable NON-federal funds AND/OR allowable third-party in-kind?}
  D -- No --> E[Match gap - this is a go/no-go input; an unfundable match is a no-go, not a writing problem]
  D -- Yes --> F{Is each match item itself allowable, allocable, reasonable AND verifiable/valued per 2 CFR?}
  F -- No --> G[Drop it - federal funds cannot match federal funds; unvaluable in-kind does not count]
  F -- Yes --> H[Document the source, value, and method now; track match drawdown alongside federal drawdown]
```

_Compliance starts at the proposal. The match is a fit input — surface a match gap at go/no-go, value in-kind per 2 CFR, and never match federal dollars with federal dollars._

## Decision Tree: Is this a selected item of cost (extra test required)?

Beyond the three-part test, 2 CFR 200 Subpart E calls out specific cost types with their own conditions — clear those before charging.

```mermaid
graph TD
  A[Cost passed allowable/allocable/reasonable] --> B{Is it a 'selected item of cost' with a specific 2 CFR rule? e.g. travel, equipment, conferences, compensation, indirect}
  B -- No --> C[Charge per the general cost principles + the award terms; document]
  B -- Yes --> D{Does it meet that item's SPECIFIC conditions? prior approval, caps, definitions, exclusions}
  D -- No --> E{Is there explicit prior written approval from the awarding agency where required?}
  E -- No --> F[Unallowable as charged - obtain prior approval first or remove the cost]
  E -- Yes --> G[Allowable with the approval on file - keep it with the documentation]
  D -- Yes --> H[Allowable - cite the specific selected-item section, not just the general principle]
```

_Cite the authority, not a memory. The three-part test is necessary but not sufficient — selected items (travel, equipment, conferences, compensation, the indirect rate) carry their own conditions and some need prior written approval._

---

## Grant-lifecycle / authority map (2026, `[verify-at-build]`)

| Stage | What happens | Key system / authority |
|---|---|---|
| Find | Search opportunities; read the NOFO/RFP; confirm eligibility | Grants.gov (federal opportunity search & apply); agency program pages `[verify-at-build]` |
| Register | Active registration required before applying for / receiving federal funds | SAM.gov registration + Unique Entity ID (UEI) `[verify-at-build]` |
| Propose | Logic model, narrative mapped to review criteria, SMART objectives, budget + budget narrative | The NOFO review/scoring criteria are the rubric `[verify-at-build]` |
| Award | Notice of Award; accept the terms & conditions; period of performance set | 2 CFR 200 + agency-specific terms; the award document `[verify-at-build]` |
| Manage | Charge only allowable/allocable/reasonable costs; apply the indirect rate; monitor sub-recipients | 2 CFR 200 Subpart E (Cost Principles); de-minimis indirect rate option `[verify-at-build]` |
| Report | Federal Financial Report (FFR) + program performance reports; draw down to need | FFR (SF-425) cadence; cash-management (draw-to-need) rules `[verify-at-build]` |
| Close & audit | Final reports, liquidation, closeout; Single Audit if over the threshold | 2 CFR 200 Subpart F (Audit Requirements); the single-audit threshold + the SEFA `[verify-at-build]` |

_Authority reference: 2 CFR Part 200 (Uniform Administrative Requirements, Cost Principles, and Audit Requirements) — Subpart E is the cost principles (allowable/allocable/reasonable + selected items of cost); Subpart F is the audit requirements (the Single Audit, the SEFA, major-program determination). The single-audit threshold, the de-minimis indirect-cost rate, and all reporting deadlines change — re-verify every threshold/rate/deadline against the current 2 CFR and the specific award terms before quoting it to a recipient. Nothing here is legal, financial, or audit advice; the org's authorized official and auditor own the binding determination._
