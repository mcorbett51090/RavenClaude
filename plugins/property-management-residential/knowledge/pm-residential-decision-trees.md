# Property Management — Residential Decision Trees + 2026 Capability Map

> Canonical knowledge bank for `property-management-residential`. **Traverse the relevant Mermaid
> tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding
> Protocol. Volatile product/pricing facts carry a retrieval date and a re-verify-at-use rider.

---

## Decision Tree 1: Renew vs. Turn

```mermaid
flowchart TD
  A[Lease expiring — resident has NOT given notice to vacate] --> B{Is the resident a good-standing tenant?}
  B -->|No: chronic late payer, lease violations, prior damage| Z[Non-renewal: do not offer renewal. Begin pre-turn planning immediately.]
  B -->|Yes: on-time, no violations, good care of unit| C{What is the renewal rent vs. market rent?}
  C -->|Unit is at or above market| D[Offer renewal at flat or modest increase. Retention economics strongly favor renewal.]
  C -->|Unit is significantly below market — >10% gap| E{What is the turn cost estimate?}
  E -->|Turn cost > annual concession to close the gap| F[Offer a partial market increase with retention bonus. Run pm_calc.py to confirm economics.]
  E -->|Turn cost < annual concession| G[Offer market-rate renewal. Tenant may not-renew — accept that outcome.]
  D --> H[Issue renewal offer 90 days before expiration. Document offer and response.]
  F --> H
  G --> H
  H --> I{Resident accepts renewal?}
  I -->|Yes| J[Execute renewal addendum. Update lease end date in PM software.]
  I -->|No| K[Begin pre-turn planning: schedule move-out inspection, pre-book vendors, update leasing status.]
```

**Leaf rule:** the economics of turning a unit (days-vacant × daily rent + make-ready cost) almost
always favor retaining a good-standing tenant within a reasonable rent range. Run the numbers with
`scripts/pm_calc.py` before pushing a market-rate renewal that risks losing a reliable resident.
A 10-day vacancy at $1,800/month = $600 in lost rent alone, before make-ready costs.

---

## Decision Tree 2: Repair vs. Replace / Make-Ready

```mermaid
flowchart TD
  A[Item needs attention during make-ready or in-place repair] --> B{Is this a habitability / safety item?}
  B -->|Yes: HVAC, electrical, plumbing, smoke detector| C[Replace or fully repair — no deferred action. Habitability items must be code-compliant and functional.]
  B -->|No: cosmetic or functional but not safety| D{What is the item's remaining useful life?}
  D -->|< 1 lease term remaining — likely to fail again| E[Replace. The cost of a callback and emergency dispatch in-lease exceeds the replacement cost.]
  D -->|1+ lease terms of useful life| F{What is the repair cost as % of replacement cost?}
  F -->|> 50% of replacement| G[Replace. Repair is false economy — you'll be back here next turn.]
  F -->|≤ 50% of replacement| H{Has this item been repaired before in the last 2 years?}
  H -->|Yes — repeat repair| I[Replace. Repeat repairs signal end of useful life.]
  H -->|No — first repair| J[Repair. Document in work order. Flag for replacement at next turn if it recurs.]
  C --> K[Document in make-ready scope. Obtain permits if required.]
  E --> K
  G --> K
  I --> K
  J --> K
```

**Leaf rule:** for make-ready decisions, the guiding question is not "can we fix it cheaply today?"
but "will it fail again before this lease ends?" A callback during tenancy costs more than the
in-turn replacement — in vendor time, resident satisfaction, and potential habitability liability.

---

## Decision Tree 3: Delinquency Action Ladder

```mermaid
flowchart TD
  A[Rent not received by end of grace period] --> B[Day 1–3: Late fee assessed. Auto-notice sent. PM reviews delinquency report.]
  B --> C{Balance > $500 or 2+ prior late payments?}
  C -->|No| D[Day 3–5: Auto-notice only. Monitor.]
  C -->|Yes| E[Day 3–5: Manual contact — call + portal message. Log attempt.]
  D --> F{Paid by day 5?}
  E --> F
  F -->|Yes| G[Case closed. Document payment. Note late history.]
  F -->|No| H[Day 5–10: Second contact attempt. Escalate to PM if no contact made.]
  H --> I{Resident responds with a credible payment plan?}
  I -->|Yes — good history, ≤1.5mo balance, specific plan| J[Day 10–14: Written payment arrangement. Document: schedule + default consequence.]
  I -->|No — no contact, or non-credible plan| K[Day 14–21: Issue statutory pay-or-quit notice. Verify jurisdiction: form, timeline, delivery method.]
  J --> L{Payment arrangement honored?}
  L -->|Yes| G
  L -->|No| K
  K --> M{Paid in full within notice cure period?}
  M -->|Yes| G
  M -->|No — cure period expired| N[Day 21–30: Consult landlord-tenant attorney. Prepare tenant file for filing.]
  N --> O[Day 30+: Eviction filing per attorney direction. Document every step.]
```

**Leaf rule:** work the ladder in order — skip no steps. Every contact attempt, every notice, and
every payment arrangement is documented in the tenant file before moving to the next step. An
eviction filing without documented prior notices and contact attempts is legally and factually weak.
Always verify state/local statutory notice requirements before issuing a legal notice.

---

## 2026 Capability Map — PM Software, Screening, and Payments (dated, re-verify at use)

_Retrieved 2026-06-08. Product features, pricing, and integrations are volatile — re-confirm at
use. This is orientation, not a procurement recommendation. [verify-at-use]_

### PM Software Platforms

| Platform | Best fit | Notable capabilities |
| --- | --- | --- |
| **AppFolio Property Manager** | Mid-market to enterprise residential (50+ units) | Resident portal, online leasing, integrated screening, AI maintenance triage, owner portal, advanced reporting [verify-at-use] |
| **Buildium** | Small to mid-market residential (1–5,000 units) | Leasing, accounting, maintenance, resident portal, owner portal — straightforward onboarding [verify-at-use] |
| **Yardi Breeze / Breeze Premier** | Small to mid-market residential and commercial | Clean UI, Breeze Premier adds more accounting depth; scales to Yardi Voyager for enterprise [verify-at-use] |
| **Rent Manager** | Mid-market, especially mixed portfolios | Deep accounting, flexible configuration, strong for single-family and mixed portfolios [verify-at-use] |
| **DoorLoop** | Small portfolio / owner-operators | Low entry cost, modern UI, basic leasing and accounting [verify-at-use] |
| **Propertyware** | Single-family residential | Purpose-built for SFR portfolios; strong maintenance and inspection tools [verify-at-use] |

### Screening Integrations (as of 2026) [verify-at-use]

| Provider | Notes |
| --- | --- |
| **TransUnion SmartMove** | Resident-initiated pull; widely used for smaller PM operations |
| **RentSpree** | Integrated into Zillow / Trulia listing flow; credit + background |
| **Checkr** | Background-focused; strong for individualized criminal history assessment (HUD 2016 guidance-aligned workflows) |
| **AppFolio Screening (native)** | Built into AppFolio; credit + criminal + eviction + income verification |
| **Buildium Screening (native)** | Integrated screening via TransUnion or tenant-initiated |

**HUD criminal history guidance (2016) [verify-at-use — guidance has not been formally rescinded
as of 2026-06-08 but has been subject to ongoing policy review; verify current status before use]:**
Blanket bans on criminal history create disparate impact. The defensible approach is an
individualized assessment: nature and severity of offense, time elapsed, evidence of rehabilitation,
nexus to tenancy risk.

### Payment Collection Integrations [verify-at-use]

| Tool | Notes |
| --- | --- |
| **PayLease (Zego)** | Widely used; ACH, card, cash-pay (PayNearMe network) |
| **Forte** | ACH-focused; bank-level integrations |
| **PM software native ACH** | AppFolio, Buildium, Yardi all offer native ACH collection — lowest friction for residents |
| **PayNearMe** | Cash-pay at retail; reaches unbanked residents |

> Provenance: product positioning based on vendor documentation and PM industry reports, 2026-06-08.
> Shares, feature sets, and integrations change; verify at use. No invented products.

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — team constitution and seams.
- [`../best-practices/README.md`](../best-practices/README.md) — the named, citable rules.
- [`../scripts/pm_calc.py`](../scripts/pm_calc.py) — occupancy, NOI, delinquency rate, turn cost,
  rent-to-income ratio calculator.
- Neighbor decision trees: `commercial-real-estate`, `skilled-trades-contracting`,
  `field-service-management`.

_Last reviewed: 2026-06-08 by `claude`._
