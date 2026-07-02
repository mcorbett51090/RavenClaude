# Travel Agency / Tour Operations — 2026 Reference

> Dated reference for the `travel-agency-tour-operations` team: the concepts that distinguish leisure-travel operations and the norms agents reach for. The durable reasoning lives in [`travel-agency-decision-trees.md`](travel-agency-decision-trees.md); this file is the freshness-anchored "what the numbers and rules are."
>
> **Advisory, not legal, tax, or financial advice.** Every commission rate, supplier fare rule, cancellation penalty, settlement mechanic, and seller-of-travel requirement below is **volatile and supplier-/jurisdiction-specific**. Each row carries a **source placeholder + retrieval date + `[verify-at-use]`** — re-confirm against the live supplier agreement, settlement statement, or the jurisdiction before it drives a quote, a booking, or a commission claim. No traveler PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Treat every specific as `[verify-at-use]` unless re-confirmed this session._

---

## 1. Revenue models — the core distinction

| Model | How margin is earned | When it fits | Source / retrieved | Flag |
|---|---|---|---|---|
| Commission | Supplier pays the agency a % of the booking's commissionable value | Commissionable product (cruise, tour, hotel, package) where commission covers the work | _<source placeholder — supplier agreement>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Service / planning fee | Fee charged to the traveler for the agency's expertise/time | Complex FIT, heavy research, or low/uncommissionable product | _<source placeholder>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Markup on net | Agency buys at a net rate and adds a margin | Net-rate supplier contracts (some DMCs, wholesalers) | _<source placeholder>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Host split | Independent advisor keeps a % of commission after the host's share | Advisors operating under a host agency | _<source placeholder — host agreement>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> **Model rule (durable):** match the model to the work and commissionability — see the revenue-model decision tree. Specific rates and splits: `[verify-at-use]`.

---

## 2. Commission norms by supplier type `[ESTIMATE]`

| Supplier type | Commission (concept) `[ESTIMATE]` | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| Cruise lines | Meaningfully commissionable; preferred/consortia rates run higher | A core margin engine for leisure agencies | _<source placeholder — cruise line agreement>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Tour operators / packages | Commissionable, varies by operator and program | Often the FIT-alternative margin source | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Hotels (direct / consortia) | Commissionable on many rates; consortia programs add amenities + overrides | Non-commissionable (net/OTA) rates exist — check | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Air (bare ticket) | Often minimal or zero commission | Most air margin now comes from a service/ticketing fee | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Travel insurance | Commissionable | Also a duty-of-care / E&O touchpoint | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |

> These are planning anchors, not quotable facts. Confirm the current rate in the specific supplier agreement before promising margin.

---

## 3. Air settlement — BSP / ARC basics

| Concept | What it is | Source / retrieved | Flag |
|---|---|---|---|
| BSP | IATA's Billing & Settlement Plan — settles air ticketing between agencies and airlines internationally | _<source placeholder — IATA>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| ARC | Airlines Reporting Corporation — the US air-ticket settlement/accreditation rail | _<source placeholder — ARC>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Air commission | Bare-air commission is typically minimal; margin comes from fees | _<source placeholder>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Accreditation | Selling air on these rails requires accreditation/relationship (often via a host) | _<source placeholder>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> Don't expect air commission the rail was never going to pay. Confirm accreditation path and settlement cadence per host/rail.

---

## 4. Cancellation-policy & group patterns

| Concept | Pattern (durable shape) | Source / retrieved | Flag |
|---|---|---|---|
| Cancellation penalty schedule | Escalating penalty by proximity to travel (deposit → partial → full) | _<source placeholder — supplier terms>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Final payment date | The date the balance is due before penalties escalate | _<source placeholder>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Group cutoff date | When unsold blocked rooms/seats release | _<source placeholder>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Attrition | % of the block the agency owes even if unsold | _<source placeholder>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Tour-conductor (TC) comp | Comp/reduced slot per N paid travelers | _<source placeholder>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> Every penalty schedule and group term is supplier-contract-specific. Record it per booking and `[verify-at-use]` at booking.

---

## 5. Regulatory & risk touchpoints

| Concept | What it is | Source / retrieved | Flag |
|---|---|---|---|
| Seller-of-travel registration | Some jurisdictions require registration/bonding to sell travel | _<source placeholder — jurisdiction>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| E&O insurance | Errors & omissions cover for advice/booking errors | _<source placeholder>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Consortia / preferred supplier | Buying groups (e.g. host/consortia programs) with higher commission + amenities | _<source placeholder>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> Registration and bonding are **jurisdiction-specific legal requirements** — confirm with counsel/the regulator, not this file.

---

## 6. How to use this file

1. Find the concept/norm/rule you need.
2. Read its retrieval date — if stale or unconfirmed this session, **re-verify** against the cited source type before quoting.
3. Quote it with its flag (`[ESTIMATE]` / `[verify-at-use]`) intact when it informs a client-facing number.
4. For anything that drives a quote, a booking, a commission claim, or a compliance obligation: confirm against the supplier agreement, settlement statement, or jurisdiction first.

---

## See also

- [`travel-agency-decision-trees.md`](travel-agency-decision-trees.md) — the durable revenue-model / group-vs-FIT / recovery / commission-chase trees.
- Domain-neutral protocols: [`../../ravenclaude-core/CLAUDE.md`](../../ravenclaude-core/CLAUDE.md).
