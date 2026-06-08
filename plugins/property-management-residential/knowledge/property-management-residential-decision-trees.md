# Property Management (Residential) — Decision Trees

_Decision trees + a dated reference map. Reference rows are `[verify-at-build]` — re-check against current law/vendor before relying on them. Fair-housing, eviction, and habitability are **legal** questions: these trees route operational decisions, they do not state the law. Last reviewed: 2026-06-08._

Traverse before classifying a maintenance request or deciding a lease renewal. Anything that turns on legality stops and routes to qualified counsel.

## Decision Tree: Maintenance triage — emergency, routine, or deferred?

Classify by risk to person and habitability first; cost is the tie-breaker, never the gate.

```mermaid
graph TD
  A[Work-order intake] --> B{Risk to person safety NOW? gas, fire, electrical, no lock}
  B -- Yes --> C[EMERGENCY - dispatch now; when in doubt, treat as emergency]
  B -- No --> D{Loss of an essential service? no heat in winter, no water, no power, sewage}
  D -- Yes --> E[HABITABILITY EMERGENCY - duty to act fast; FLAG warranty-of-habitability to counsel]
  D -- No --> F{Will it worsen / cause damage if it waits? active leak, no AC in heat}
  F -- Yes --> G[URGENT - schedule within 24-72h before it escalates]
  F -- No --> H{Tenant-impacting but stable? cosmetic, minor, convenience}
  H -- Yes --> I[ROUTINE - schedule into the normal queue]
  H -- No --> J[DEFER - log WITH the reason and a revisit date; never silently drop]
```

_No-heat-in-winter, no-water, sewage, gas, and no-lock are habitability/emergency events with a duty to act fast — they never sit in the routine queue. Whether a condition legally breaches the warranty of habitability is a counsel question, not a triage output._

## Decision Tree: Lease renewal — renew, raise, or non-renew?

The number is a math problem framed by law: market vs. in-place rent and turn/vacancy cost decide it; the *legality* of the increase or non-renewal is always a counsel question.

```mermaid
graph TD
  A[Lease approaching renewal] --> B{Is the tenant in good standing? paying, lease-compliant}
  B -- No --> C[FLAG to counsel: non-renewal / non-payment legality, notice & cure rules - do not adjudicate]
  B -- Yes --> D{Is in-place rent below market?}
  D -- No --> E[RENEW at or near current - retaining a good paying tenant beats turn + vacancy loss]
  D -- Yes --> F{Does a raise to market exceed turn cost + vacancy loss + re-lease risk?}
  F -- No --> G[Modest raise toward market - keep the tenant, capture some upside]
  F -- Yes --> H{Any notice cap / rent-increase limit in play? rent control, lease, jurisdiction}
  H -- Unsure / Yes --> I[FLAG to counsel for the cap & notice rules, THEN set the number within them]
  H -- No --> J[Raise toward market with required notice - document the standard applied]
```

_A renewal decision is uniform and documented: the same market-vs-in-place + turn-cost logic for every unit. Steering a renewal/non-renewal by anything protected-class-adjacent is a fair-housing flag, not a judgment call._

---

## Reference map (2026, `[verify-at-build]`)

| Area | Reference points | Notes |
|---|---|---|
| Fair-housing protected classes (federal) | Race, color, national origin, religion, sex (incl. gender identity / sexual orientation per HUD guidance), familial status, disability | Federal Fair Housing Act baseline; **many state/local laws add classes** (source of income, age, marital status, etc.) `[verify-at-build]` |
| Fair-housing — what agents do | FLAG and route to counsel | Agents never adjudicate ads, denials, accommodations, or steering — they surface the risk `[verify-at-build]` |
| Screening signals (consistent, documented) | Income multiple (e.g. ~2.5-3x rent), credit history, prior eviction/judgment history, rental references, occupancy standard | Apply the SAME written standard to every applicant; criminal-history and source-of-income use is legally constrained — `[verify-at-build]` |
| Habitability / emergency list | No heat (cold), no water, no power, sewage backup, gas leak, no working lock, no hot water | Implied warranty of habitability varies by jurisdiction; the OPERATIONAL duty-to-act-fast does not `[verify-at-build]` |
| PM-software landscape | AppFolio, Yardi (Voyager / Breeze), RealPage, Buildium, Rent Manager, DoorLoop, TenantCloud | Agents are system-neutral; map the schema to whatever the client runs `[verify-at-build]` |
| Screening / tenant-data providers | TransUnion SmartMove, Experian/RentBureau, RentGrow, Checkr-style background | Screening reports are sensitive PII — minimize, never quote in outputs `[verify-at-build]` |
| Rent-roll fields | Unit, tenant, lease start/end, market rent, actual rent, balance/aging, status (occupied / vacant / notice / down) | The source of truth; reconcile to reality every period `[verify-at-build]` |
| NOI & owner-reporting metrics | NOI = operating income − operating expenses (EXCL. debt service, capex, depreciation); occupancy (physical vs. economic); vacancy loss; delinquency aging; renewal rate; time-to-lease; turn time | NOI is operating-only and is NOT cash flow; the books of record are `finance`'s `[verify-at-build]` |

_Legal disclaimer: fair-housing, eviction, rent-control/notice, and warranty-of-habitability rules are jurisdiction-specific law that changes. These rows orient operations; they are not legal advice and must be verified with qualified counsel before any consequential action. The books of record (trust-account, GL, tax) belong to `finance`._
