# Knowledge — HOA / community-association decision trees

> **Last reviewed:** 2026-07-17 · **Confidence:** Medium-High (consensus on the governing-document-first, budget-and-reserve, even-handed-enforcement, collections-to-the-legal-gate, insurance, and developer-transition framings, and on the board-decides/manager-advises separation; **specific HOA/condo statutes, assessment caps, special-assessment vote thresholds, lien priority & foreclosure procedure, reserve-study standards, ARC deemed-approval timeframes, notice/quorum/records-retention rules, and fair-housing/FDCPA/state-collection rules are volatile and jurisdiction-specific — re-verify before acting and route legal questions to counsel**).
> The most-asked community-association questions are "what do we budget and charge?", "how much do we fund the reserves / how do we fund the next big project?", "can we enforce this covenant / approve this change?", "when do we lien a delinquent owner?", "how do we run the meeting and keep records?", and "how do we transition from the developer?". These are the decision trees the `association-management-lead` traverses **before** setting a policy or naming an action, plus the trade-off tables and the seams to adjacent plugins.

The team's discipline: **read the governing documents first (they are the constitution), fund reserves on the study, enforce evenly by the documented process, and keep the board-decides / manager-advises line.** This is **not legal, financial, or insurance advice** — volatile statute/lien/reserve specifics carry a retrieval date and are verified at use, and legal questions route to **counsel**. A landlord's rental units and leases leave this layer for `property-management`; this plugin owns the **community association** and its common-interest governance.

---

## Decision Tree 1: budget & assessment (dues) setting

Gate on the **governing-document authority**, then budget **operating + reserves**.

```mermaid
graph TD
  Start([Set the annual budget & assessment]) --> AUTH[Read the governing documents + state act<br/>· assessment-increase cap?<br/>· special-assessment vote threshold?<br/>· reserve-study / funding mandate?]
  AUTH --> OP[Operating budget<br/>· management · insurance · utilities · landscaping<br/>· maintenance · amenities · admin · contingency]
  OP --> RS{Reserve study current?}
  RS -->|Yes| PF[Read percent-funded + funding plan]
  RS -->|No / stale| COMMISSION[Commission / update the reserve study<br/>→ reserve analyst]
  PF --> METHOD{Funding method}
  METHOD -->|Lowest special-assessment risk| FULL[Full funding ~100%]
  METHOD -->|Balance above zero across horizon| BASE[Baseline funding]
  METHOD -->|Hold a chosen floor| THRESH[Threshold funding]
  METHOD -->|Statutory minimum only| MIN[Statutory-minimum funding]
  FULL --> DUES
  BASE --> DUES
  THRESH --> DUES
  MIN --> DUES
  DUES[Assessment = operating + reserve contribution<br/>÷ ownership-allocation formula] --> CAP{Increase within the cap?}
  CAP -->|Yes| ADOPT[Board adopts the budget & assessment]
  CAP -->|No| CHOICE[Phase the increase · seek member vote ·<br/>OR flag the reserve underfunding — don't hide it]
```

---

## Decision Tree 2: reserve funding & the major-project decision

Only fund the **study's plan**; pick the **funding path** by the trade-offs.

```mermaid
graph TD
  Start([A major component nears end-of-life]) --> STUDY{Reserve adequate for it?}
  STUDY -->|Yes, funded on plan| ONPLAN[Replace from reserves on schedule]
  STUDY -->|No, underfunded| PATH{Funding path}
  PATH -->|Lead time exists| RAISE[Raise reserve contributions now<br/>· spreads cost · least disruptive · needs runway]
  PATH -->|Need cash fast, members can bear it| SPECIAL[Special assessment<br/>· one-time · fast · painful · may need a vote]
  PATH -->|Preserve cash, spread over time| LOAN[Association loan<br/>· spreads cost at interest · adds debt · covenant]
  PATH -->|Do it in stages| PHASE[Phase the work<br/>· as funds allow · risk of mid-phase failure]
  RAISE --> VOTE
  SPECIAL --> VOTE
  LOAN --> VOTE
  PHASE --> VOTE
  VOTE{Membership-vote threshold or statutory limit?} -->|Yes| COUNSEL[[Route the vote / procedure to counsel]]
  VOTE -->|No, board authority| BOARD[Board adopts the funding plan]
```

> **The classic failure:** holding dues artificially low by **starving reserves**. Deferred reserve funding is a special assessment waiting to happen — the members pay either way, and later is more expensive and more disruptive.

---

## Decision Tree 3: covenant enforcement & architectural review

Enforce **evenly** by the **documented due process**, or don't enforce at all.

```mermaid
graph TD
  Start([A covenant issue or a change request]) --> KIND{Enforcement or ARC?}
  KIND -->|Owner made / wants an exterior change| ARC[Architectural review]
  KIND -->|Owner is violating a covenant| ENF[Enforcement]
  ARC --> GUIDE{Meets the published design guidelines?}
  GUIDE -->|Yes| APPROVE[Approve · record the decision & rationale]
  GUIDE -->|No| DENY[Deny consistently · cite the guideline · record]
  GUIDE -->|No decision in the required window| DEEMED[Watch the clock — may be deemed approved]
  ENF --> EVEN{Enforced evenly against all owners?}
  EVEN -->|No — selectively| RISK[[Selective-enforcement / waiver risk → counsel<br/>before acting]]
  EVEN -->|Yes| NOTICE[Written violation notice<br/>· cite the covenant · specific violation · cure period]
  NOTICE --> CURE{Cured in the period?}
  CURE -->|Yes| CLOSE[Close · document]
  CURE -->|No| HEARING[Offer the hearing<br/>· owner's opportunity to be heard]
  HEARING --> REMEDY[Fine per the schedule · self-help/abatement where authorized<br/>· serious/continuing → counsel]
```

---

## Decision Tree 4: assessment collections & delinquency

Sequence the steps **evenly**; **stop at the legal line**.

```mermaid
graph TD
  Start([A delinquent assessment account]) --> AGE[Age the receivable · apply payments per the<br/>governing-document / statutory order]
  AGE --> R1[Payment reminder / friendly notice]
  R1 --> LATE[Late fee per the schedule]
  LATE --> DEMAND[Demand / intent-to-lien notice<br/>· statutory pre-lien notice where required]
  DEMAND --> GATE{At the lien-referral threshold?}
  GATE -->|No| CONTINUE[Continue the sequence · keep the record]
  GATE -->|Yes| LEGAL[[Record the lien · foreclosure · FDCPA / fair-housing /<br/>state-collection rules → COUNSEL — not the manager]]
  LEGAL --> DECIDE{Whether to lien / foreclose?}
  DECIDE -->|Policy call| LEAD[Board / association-management-lead decides]
  DECIDE -->|Mechanics| COUNSEL2[Counsel executes]
```

> **The legal line:** the manager runs the reminders, late fees, and demand notices **evenly**; recording a **lien**, **foreclosing**, and complying with **FDCPA / fair-housing / state-collection** rules are **counsel's** — never advised in-plugin as legal steps.

---

## Trade-off table — major-project funding

| Path | Sweet spot | Watch out for |
|---|---|---|
| **Raise reserves now** | Lead time exists before the component fails | Needs runway; may exceed an assessment-increase cap |
| **Special assessment** | Cash needed fast; members can bear a one-time hit | Painful; may need a membership vote; hardship exposure |
| **Association loan** | Preserve cash, spread cost over years | Interest cost; adds debt + a lender covenant; pledges future assessments |
| **Phase the work** | Budget can't cover it all at once | Component may fail mid-phase; escalating cost |

## Trade-off table — reserve-funding methods

| Method | Sweet spot | Watch out for |
|---|---|---|
| **Full funding (~100%)** | Lowest special-assessment risk; smoothest dues | Highest current contribution |
| **Baseline** | Keep the balance above zero across the horizon | Thin cushion; a surprise can force a special assessment |
| **Threshold** | Hold a chosen percent-funded floor | Judgment call on the floor |
| **Statutory minimum** | Meets the legal floor at the lowest cost | Often underfunds — highest special-assessment risk |

## Trade-off table — insurance layers (route the design to a broker)

| Coverage | Protects | Watch out for |
|---|---|---|
| **Master property policy** | The common elements / buildings (per the declaration's coverage form) | Bare-walls vs all-in vs single-entity form — mismatch to the CC&Rs leaves a gap |
| **General liability** | The association vs common-area injury claims | Adequate limits vs the amenity risk (pool, playground) |
| **D&O (directors & officers)** | Board members vs governance/decision claims | Volunteer-board exposure; check the enforcement/discrimination coverage |
| **Fidelity / crime** | Association funds vs theft (manager/board) | Statute/document may mandate a minimum limit |

---

## Seams (this is the community-association layer, not the whole real-estate stack)

- **Lien, foreclosure, statute interpretation, fair-housing / FDCPA, governing-document amendment, contested hearings** → **counsel** (`legal-small-firm`) — this plugin runs the business process, not the legal one; it is **not legal advice**.
- **A landlord's rental units, tenant leases, rent collection, evictions** → `property-management` (rental operations of individual units; distinct from the community association).
- **Buying or selling a home in the community** (the resale certificate / estoppel package feeds it) → `residential-real-estate-brokerage`.
- **CRE brokerage / asset management** → `commercial-real-estate` (not the common-interest community).
- **The audit, tax return (e.g., Form 1120-H), and bookkeeping** → `accounting-bookkeeping`.
- **Investing / banking the reserve and operating funds** → `treasury-management` (safety > liquidity > yield on reserve cash).
- **The reserve study itself, and component-condition engineering** → a **reserve analyst / engineer** (procured, not produced in-plugin).

---

## Provenance

- Durable framings (governing-documents-first, operating + reserve budgeting, fund-reserves-on-the-study, the reserve-funding-method and major-project-funding trade-offs, even-handed documented enforcement due process, architectural review against published guidelines, the collections sequence to the legal gate, the board-decides / manager-advises separation, minutes-and-records as the legal shield, the insurance layers, and developer-to-homeowner transition) are consensus community-association-management practice reviewed 2026-07-17 — **High confidence**.
- Specific **HOA/condo statutes, assessment caps, special-assessment vote thresholds, lien priority & foreclosure procedure, reserve-study standards, ARC deemed-approval timeframes, notice/quorum/records-retention & owner-inspection rules, and fair-housing/FDCPA/state-collection rules** are **volatile and jurisdiction-specific**, carry retrieval dates, and are **not legal, financial, or insurance advice** — re-verify with `ravenclaude-core/deep-researcher` and confirm with **counsel** before acting. _(Reviewed 2026-07-17.)_
