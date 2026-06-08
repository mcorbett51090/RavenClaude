# Hospitality Hotels — Decision Trees + 2026 Capability Map

> Canonical knowledge bank for `hospitality-hotels`. **Traverse the relevant Mermaid tree
> top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
> Volatile product/version/pricing facts in the capability map carry a retrieval date and a
> re-verify-at-use rider. Mark any volatile figure you cite with `[verify-at-use]`.

---

## Decision Tree 1: Raise or Hold Rate (BAR Strategy)

```mermaid
flowchart TD
  A[What is the current OTB pace vs. forecast?] -->|Significantly ahead of forecast| B[Compression signal — demand is outpacing supply]
  A -->|On pace or slightly ahead| C[Neutral — check comp-set position]
  A -->|Behind forecast| D[Soft period — rate increase will suppress demand further]
  B --> E{Is days-to-arrival > 14 days?}
  E -->|Yes — time to optimize| F{Is current BAR at or below comp-set average?}
  F -->|Yes — we are priced too low| G[RAISE: move BAR above comp-set average by demand-justified increment]
  F -->|No — already at premium| H[HOLD: BAR is correctly positioned; monitor pick-up daily]
  E -->|No — inside 14 days| I{Is OTB occupancy > 80%?}
  I -->|Yes — near full house| J[RAISE: compression pricing justified — last-room-value logic applies]
  I -->|No — still filling| K{Is comp-set raising rate?}
  K -->|Yes| L[RAISE: follow comp-set to avoid leaving rate on the table]
  K -->|No — comp holding| M[HOLD: premature raise risks losing transient demand to comp]
  C --> N{Is our BAR below comp-set average?}
  N -->|Yes| O[RAISE modestly: recover rate gap without demand risk]
  N -->|No — at parity or premium| P[HOLD: rate correctly positioned; watch pick-up]
  D --> Q{Is the soft period > 30 days out?}
  Q -->|Yes — time to stimulate| R[Consider tactical rate reduction or package to stimulate demand — verify RevPAR math first]
  Q -->|No — close-in soft| S[LOWER only if displacement is RevPAR-positive; otherwise HOLD and accept the gap]
```

**Leaf rule:** never move rate without citing the demand basis (OTB pace, comp-set position, or
days-to-arrival window). A rate set on intuition is a guess. On compression nights, the
**last-room-value principle** applies: the marginal room is worth the most when supply is tightest
— do not discount it. A soft-period rate reduction is only RevPAR-positive if the incremental
occupied rooms cover the revenue surrendered on already-committed demand.

---

## Decision Tree 2: Direct Booking vs. OTA Channel

```mermaid
flowchart TD
  A[What is the property's current OTA share of room revenue?] -->|< 35%| B[Healthy mix — direct channel is competitive. Maintain and optimize.]
  A -->|35–55%| C[Watch zone — OTA is the dominant source. Assess whether the mix is structural or cyclical.]
  A -->|> 55%| D[OTA dependency — distribution cost is likely eroding net ADR materially. Intervention warranted.]
  C --> E{Is the direct channel's total acquisition cost lower than OTA commission?}
  E -->|Yes — direct is cheaper per booking| F[Invest in direct: metasearch presence, booking-engine UX, loyalty member rate]
  E -->|No — direct CAC is higher| G[Assess why: Is booking-engine converting poorly? Is there no metasearch? Is loyalty weak?]
  G --> H[Fix the cheapest direct-channel lever first before committing to a shift]
  D --> I{Are there parity violations on any OTA channel?}
  I -->|Yes| J[Fix parity FIRST — violations trigger OTA algorithm suppression and compound the dependency]
  I -->|No — parity is clean| K{Is the hotel's booking engine competitive in rate, UX, and mobile?}
  K -->|No weaknesses| L[Invest in metasearch bidding: Google Hotel Ads direct-booking link is the fastest shift lever]
  K -->|Yes — booking engine is weak| M[Booking-engine upgrade is a pre-requisite: no shift is sustainable with a poor direct channel]
  B --> N[Confirm net ADR is optimized across retained OTA channels. Check commission rates annually.]
  F --> N
  L --> N
```

**Leaf rule:** OTA commission is a customer-acquisition cost, not a fixed tariff. Compare it to the
hotel's all-in direct CAC (booking-engine fee + payment processing + metasearch bid cost) before
declaring OTA "too expensive." At scale, direct is typically cheaper — but only if the booking
engine converts. Fix the weakest direct-channel lever before investing in a mix shift. Parity
violations must be resolved before any shift investment, because OTA algorithm suppression from
a violation actively redirects direct bookings back through the OTA.

---

## Decision Tree 3: Overbook or Not

```mermaid
flowchart TD
  A[Do you have at least 12 months of no-show and cancellation rate history?] -->|No — insufficient history| B[Do NOT overbook yet. Collect data first. Use a conservative hold-back of 1–2 rooms if pressure is high.]
  A -->|Yes — data available| C[Calculate the net cancellation rate: no-show % + same-day cancel % − same-day rebook %]
  C --> D{Is the net cancellation rate > 2%?}
  D -->|No — very low no-show/cancel| E[Overbooking benefit is marginal. The walk-cost risk likely exceeds the RevPAR uplift. HOLD.]
  D -->|Yes — meaningful no-show/cancel rate| F[Calculate expected walk count at proposed overbook level]
  F --> G{Is the expected walk cost less than the expected RevPAR uplift?}
  G -->|No — walk cost > uplift| H[Do NOT overbook at that level. Reduce to the break-even overbook level or HOLD.]
  G -->|Yes — uplift > walk cost| I{Is there a walk-recovery playbook in place?}
  I -->|No — no playbook| J[Build the walk playbook FIRST: relocation protocol, compensation standard, loyalty impact. Then overbook.]
  I -->|Yes — playbook is live| K[OVERBOOK at the calculated level. Review monthly as no-show/cancel rates change.]
  K --> L[Monitor: after each walk, compare actual walk cost to model. Adjust overbook level if model is wrong.]
```

**Leaf rule:** overbooking is a calculated risk, never a fixed percentage applied without history.
The math required before any overbook recommendation: (1) 12-month no-show + same-day cancel rate
from the PMS; (2) expected same-day rebookings that offset; (3) a walk-cost model (relocation rate
+ compensation + loyalty impact per walked guest); (4) the RevPAR uplift of selling the rooms that
would otherwise go empty. Without all four inputs, the correct answer is "do not overbook." A walk
that damages a loyal guest relationship has a cost that extends beyond the night's room revenue.

---

## 2026 Capability Map — Hotel Technology Stack

_Retrieved 2026-06-08. Product pricing, feature sets, and market positions are volatile —
re-confirm at use; this is orientation, not a procurement recommendation. [verify-at-use] for all
specific figures._

| Category | Leading Options (2026) | Notes |
| --- | --- | --- |
| **PMS (Property Management System)** | **Opera Cloud** (Oracle — dominant full-service and branded), **Mews** (cloud-native, strong mid-market and lifestyle), **Cloudbeds** (all-in-one for independents and smaller properties), **Apaleo** (API-first, composable stack) | Opera Cloud is the most common enterprise/branded choice; Mews and Cloudbeds are the fastest-growing cloud-native alternatives. Apaleo is favored by tech-forward independents needing API flexibility. [verify-at-use] |
| **RMS (Revenue Management System)** | **IDeaS G3 RMS** (SAS-owned, market leader for mid-size to large), **Duetto GameChanger** (known for Open Pricing, strong in upscale/luxury), **Infor HMS Revenue**, **OTA Insight / Lighthouse** (rate intelligence + RMS entry-level) | IDeaS and Duetto are the dominant enterprise RMS. OTA Insight (now rebranding as Lighthouse) is widely used for rate-shopping intelligence even by hotels with a separate RMS. [verify-at-use] |
| **Channel Manager** | **SiteMinder** (global market leader for independent hotels), **Cloudbeds Channel Manager** (bundled), **RateGain**, **Booking.com Connectivity** | A channel manager syncs availability and rates to OTAs in near-real time. SiteMinder connects to 450+ OTA channels. [verify-at-use] |
| **Booking Engine (Direct Channel)** | **SynXis** (Sabre — dominant for branded and larger independents), **Booking Button** (Booking.com's direct engine), **SiteMinder Booking Engine**, **Mews Booking Engine**, **Cloudbeds Booking Engine** | The booking engine's conversion rate and mobile UX are the most critical direct-channel metrics. [verify-at-use] |
| **GDS** | **Sabre GDS**, **Amadeus GDS**, **Travelport (Galileo/Worldspan)** | GDS is the backbone of corporate/agency and consortia (BCD, AMEX GBT, Carlson Wagonlit) bookings. Rates loaded via a CRS (Central Reservation System) or direct connect. [verify-at-use] |
| **Review / Reputation Management** | **TrustYou** (aggregates reviews, produces Trust Score), **ReviewPro** (Shiji group — GRI score, widely used in branded hotels), **Revinate** (email marketing + reputation combined), **Medallia (formerly Helixa)** | TrustYou and ReviewPro are the two primary reputation-score aggregation platforms in hospitality. Both produce a composite score from OTA, TripAdvisor, and Google reviews. [verify-at-use] |
| **Rate Shopping / Competitive Intelligence** | **OTA Insight / Lighthouse**, **RateGain**, **Duetto Pulse**, **Hotelligence (TravelClick/Amadeus)** | Rate shopping tools provide near-real-time comp-set BAR visibility. Most RMS platforms include a built-in rate-shopping feed. [verify-at-use] |
| **CRM / Guest Data** | **Salesforce (Hospitality Cloud)**, **Revinate CRM**, **Cendyn**, **Amadeus GMS** | Guest CRM powers personalization, repeat-guest recognition, and pre-arrival upsell programs. Most are PMS-integrated via profile sync. [verify-at-use] |

> Provenance: hotel-technology landscape knowledge based on publicly available vendor documentation
> and industry analyst reports as of 2026-06-08. Market share figures, pricing, and product names
> are volatile — re-verify at use. No invented products.

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — team constitution & seams.
- [`../best-practices/README.md`](../best-practices/README.md) — the named, citable rules.
- [`../scripts/hotel_calc.py`](../scripts/hotel_calc.py) — the RevPAR / ADR / GOPPAR / net-ADR
  calculator. Run it for the arithmetic in any decision-tree leaf.

_Last reviewed: 2026-06-08 by `claude`._
