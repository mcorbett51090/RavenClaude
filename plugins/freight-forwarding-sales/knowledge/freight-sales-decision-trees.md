# Freight-sales decision trees

> **Last reviewed: 2026-06-04 by `claude`.** Canonical decision trees for the recurring routing/strategy calls a freight-forwarding sales manager makes. Each tree has an observable entry condition, a `Last verified` date, a Mermaid graph, per-leaf rationale, and a tradeoffs table where there are ≥3 leaves. These encode **industry-standard** practice (mode economics, tender qualification, Incoterms 2020, spot/contract strategy) — not any one carrier's confidential method. Crossover thresholds are heuristics: **calibrate to your own lanes and rates.**
>
> **Decision-tree traversal (priors).** When a situation matches an entry condition, traverse the relevant graph **top-to-bottom** before deciding — do **not** pattern-match on keywords in the request. The first branch that resolves cleanly is the leaf to apply.

Refresh triggers: a new Incoterms revision (next ICP cycle), a structural shift in mode economics (e.g., sustained air/ocean rate inversion), or a change in how tenders are commonly run.

---

## Decision Tree: Mode selection

**When this applies:** a shipment or lane needs a transport mode and you want the right cost/transit/risk fit before quoting.

**Last verified:** 2026-06-04 against standard forwarding practice (urgency × density × value × volume).

```mermaid
flowchart TD
    START[Shipment to move] --> Q1{Must arrive in days / time-critical?}
    Q1 -->|YES, small + urgent| EXPRESS[Express courier / integrator]
    Q1 -->|YES, larger but still urgent| AIR[Air freight]
    Q1 -->|NO| Q2{High value-density or perishable / where inventory carrying cost is high?}
    Q2 -->|YES| AIRSEA[Air, or sea-air hybrid]
    Q2 -->|NO| Q3{Volume fills a container? approx 15+ CBM or a full 20'/40'}
    Q3 -->|NO, part-load| LCL[Ocean LCL]
    Q3 -->|YES| Q4{Standard containerizable cargo?}
    Q4 -->|YES| FCL[Ocean FCL]
    Q4 -->|NO, oversized / project / vehicles| BREAKBULK[Breakbulk / RoRo / project cargo]
```

**Rationale per leaf:**
- **Express** — door-to-door speed for small, urgent, high-value parcels; priced on chargeable weight (often /5000 divisor); least paperwork burden on the shipper.
- **Air** — fast, reliable transit for time-sensitive or high-value-density cargo; expensive per kg, charged on chargeable weight; the right call when the inventory carrying cost or st-out cost beats the freight premium.
- **Air / sea-air** — sea-air hybrids trade some transit for big cost savings vs pure air on the right lanes; consider for medium urgency + high value.
- **LCL** — part-loads that don't justify a full box; priced per W/M; carries CFS handling and longer transit (consolidation/deconsolidation) but avoids paying for empty container space.
- **FCL** — once volume approaches a container, FCL usually beats LCL per unit and is faster/lower-risk (no co-loading); the LCL→FCL break-even is roughly **~13–15 CBM** but **calibrate to the lane**.
- **Breakbulk / RoRo / project** — for cargo that won't containerize (oversized, heavy-lift, vehicles, plant); specialist handling and quoting.

**Tradeoffs summary:**

| Leaf | Speed | Cost | Best for | Watch-out |
|---|---|---|---|---|
| Express | Fastest | Highest/kg | Small urgent parcels | Volumetric /5000 inflates bulky |
| Air | Fast | High/kg | Time-/value-sensitive | Chargeable weight, fuel/security surcharges |
| Sea-air | Medium | Medium | Cost-aware but not slow | Lane availability, transshipment |
| LCL | Slow | Low (part) | Part-loads | CFS charges, consolidation delay/risk |
| FCL | Medium | Low/unit at volume | Container-fill volume | Demurrage/detention if box held |
| Breakbulk | Slow | Variable | Oversized/project | Specialist, bespoke quoting |

---

## Decision Tree: Quote vs qualify (bid / no-bid)

**When this applies:** an RFQ/RFP/tender has landed and you must decide whether to invest hours pricing it.

**Last verified:** 2026-06-04 against standard tender-qualification practice.

```mermaid
flowchart TD
    START[Tender / RFQ received] --> Q1{Is it an RFI / intel-only?}
    Q1 -->|YES| LEAN[Respond lean - get on shortlist, learn criteria]
    Q1 -->|NO| Q2{Strategic fit - our lanes / modes / strength?}
    Q2 -->|NO| DECLINE[Polite decline - preserve relationship]
    Q2 -->|YES| Q3{Volume real and material, not a price-check?}
    Q3 -->|NO| DECLINE
    Q3 -->|YES| Q4{Do we have a relationship and known decision criteria?}
    Q4 -->|NO / single-threaded + opaque| Q5{Can we widen + learn criteria before deadline?}
    Q5 -->|NO| DECLINE
    Q5 -->|YES| BID
    Q4 -->|YES| Q6{Winnable at acceptable margin AND can we deliver it?}
    Q6 -->|NO| DECLINE
    Q6 -->|YES| BID[Bid - qualify-led, value narrative + matrix]
```

**Rationale per leaf:**
- **Lean (RFI)** — don't over-invest before it's a real bid; respond enough to shortlist and learn the criteria.
- **Decline** — a fast, reasoned, relationship-preserving no on a poor-fit / unreal-volume / un-winnable / undeliverable tender returns the week to winnable bids and keeps you on the next list. Declining well is a skill, not a failure.
- **Bid** — only when fit + real volume + a relationship/criteria path + winnable economics + deliverability all hold. Then compete on the value narrative, not price alone.

**Tradeoffs summary:**

| Leaf | When | Cost to you | Upside |
|---|---|---|---|
| Lean | RFI / very early | Low | Shortlist + intel |
| Decline | Poor fit / unreal / un-winnable | Near-zero | Time back, relationship kept |
| Bid | All qualifiers pass | High (pricing hours) | Real win probability |

---

## Decision Tree: Incoterms selection

**When this applies:** you're proposing terms for a deal and must pick the Incoterm 2020 that fits the customer's capability and your service scope.

**Last verified:** 2026-06-04 against ICC Incoterms® 2020 (standard interpretation; cite ICC text for binding questions).

```mermaid
flowchart TD
    START[Choose Incoterm] --> Q1{Containerized cargo? not bulk/breakbulk over a rail}
    Q1 -->|NO, bulk/breakbulk by sea| SEA[Use sea-only terms: FAS/FOB/CFR/CIF]
    Q1 -->|YES| Q2{Who should control + pay the main carriage?}
    Q2 -->|Buyer controls freight| FCA[FCA named place - correct minimal-seller term for containers]
    Q2 -->|Seller arranges freight to destination| Q3{Seller deliver to destination + bear risk in transit?}
    Q3 -->|NO, risk passes at origin, seller just pays freight| Q4{Include insurance?}
    Q4 -->|NO| CPT[CPT named dest]
    Q4 -->|YES| CIP[CIP named dest - ICC A all-risks]
    Q3 -->|YES, delivered terms| Q5{Seller also clear import + pay duty/VAT?}
    Q5 -->|NO| DAP[DAP / DPU named dest]
    Q5 -->|YES, and can be importer of record| DDP[DDP - heavy: duty+VAT+IOR exposure]
```

**Rationale per leaf:**
- **Sea-only terms** — FAS/FOB/CFR/CIF assume goods crossing the ship's side; correct for bulk/breakbulk, **wrong for containers** (risk-gap at the CY/CFS). CIF insurance is minimum ICC C.
- **FCA** — the correct minimal-seller term for **containerized** cargo; risk passes at hand-over to the carrier, not at the rail.
- **CPT / CIP** — seller pays main carriage to a named destination but **risk passes at origin** (first carrier); CIP carries **all-risks (ICC A)** insurance by default — don't confuse with CIF's minimum cover.
- **DAP / DPU** — delivered terms; seller bears risk to destination (DPU also unloads); buyer handles import + duty.
- **DDP** — seller pays **everything incl. import duty + VAT** and usually must be/appoint the importer of record; propose only when the seller can actually carry that compliance and cost. EXW (the mirror extreme) puts export clearance awkwardly on the buyer — usually prefer FCA over EXW.

**Tradeoffs summary:**

| Leaf | Seller burden | Risk passes | Key trap |
|---|---|---|---|
| FCA | Low | Origin hand-over | The right container term (vs FOB misuse) |
| CPT/CIP | Medium | Origin (1st carrier) | Cost ≠ risk point; CIP = ICC A |
| CFR/CIF | Medium | On board (origin) | Sea-only; CIF = ICC C minimum |
| DAP/DPU | High | Destination | DPU = seller unloads |
| DDP | Highest | Destination | Duty/VAT + importer-of-record exposure |

---

## Decision Tree: Spot vs contract rate

**When this applies:** you're deciding how to price against rate volatility — a held/fixed rate, a contract, or a spot/floating quote.

**Last verified:** 2026-06-04 against standard ocean/air pricing practice.

```mermaid
flowchart TD
    START[How to price vs volatility] --> Q1{Regular, predictable volume on the lane?}
    Q1 -->|YES, recurring| Q2{Lane currently volatile? GRI/PSS/BAF moving}
    Q2 -->|NO, stable| CONTRACT[Fixed-term contract rate - certainty both sides]
    Q2 -->|YES, volatile| INDEX[Contract with index/floating surcharge clause]
    Q1 -->|NO, one-off / irregular| Q3{Customer wants a held rate?}
    Q3 -->|NO| SPOT[Spot quote, short validity]
    Q3 -->|YES| HELD[Spot with a short 'valid until' + subject-to GRI/PSS]
```

**Rationale per leaf:**
- **Contract** — recurring, stable lanes: a fixed-term rate gives both sides certainty and protects the relationship; you carry some volatility risk, so price it in.
- **Index / floating-surcharge contract** — recurring but volatile lanes: lock the base but pass through BAF/GRI via an agreed index or clause, so neither side is whipsawed.
- **Spot** — one-off/irregular: quote at the live spot with **short validity**; don't hold a price you can't buy tomorrow.
- **Held spot** — customer wants a held number on a one-off: give a short "valid until" and mark GRI/PSS/BAF as subject-to-change, or fold them into a priced-in all-in.

**Tradeoffs summary:**

| Leaf | Certainty | Your risk | Best for |
|---|---|---|---|
| Contract | High both sides | You carry volatility | Stable recurring lanes |
| Index/floating | Medium | Shared via clause | Volatile recurring lanes |
| Spot | Low | Minimal | One-off/irregular |
| Held spot | Short-term | Bounded by validity | One-off with a price ask |

---

## Decision Tree: Rate Objection — Hold, Adjust, or Give-Get

**When this applies:** a customer has responded to a quote or renewal with a price objection — they say the rate is too high, they have a lower offer from a competitor, or they ask for a better rate. The seller must decide whether to hold price, adjust, or offer a conditional give-get. The decision gates a discount.

**Last verified:** 2026-06-05 against standard freight-forwarding commercial practice.

```mermaid
flowchart TD
    START[Customer rate objection received] --> Q1{Is the competitor offer verified - same scope and Incoterm?}
    Q1 -->|NO - scope or Incoterm unclear| CLARIFY[Clarify the comparison first - apples-to-apples check]
    Q1 -->|YES - comparable scope and terms| Q2{Is the competitor offer at or below our minimum margin floor?}
    Q2 -->|YES - below our floor| HOLD_OR_WALK[Hold price - explain value or decline the lane]
    Q2 -->|NO - above our floor| Q3{Is this a strategic account or a material lane?}
    Q3 -->|NO - small or one-off| HOLD[Hold price - value pitch; one-off lane not worth discounting]
    Q3 -->|YES - strategic or high-volume| Q4{Can we structure a give-get?}
    Q4 -->|YES - volume commit or term extension available| GIVGET[Offer conditional reduction - volume or term give-get]
    Q4 -->|NO - customer refuses give-get| Q5{Is losing this lane acceptable?}
    Q5 -->|YES - margin or fit not worth it| WALK[Decline to match - preserve margin discipline]
    Q5 -->|NO - must retain| ADJUST[Partial adjustment - document impact, flag to manager]
```

**Rationale per leaf:**
- *Clarify the comparison* — a competitor quote at "lower price" often includes a different Incoterm scope, a different routing, or excludes surcharges the customer will discover at invoice; clarify before any concession.
- *Hold price / decline the lane* — below the margin floor is a hard stop; accepting below-margin freight to retain volume is a margin-erosion decision, not a relationship decision.
- *Hold with value pitch* — small or one-off lanes don't justify training the customer that asking always produces a discount; hold and present value.
- *Give-get* — the right structure for strategic accounts: a rate concession tied to a volume commitment or term extension recovers the margin over time.
- *Walk* — a lane the forwarder can't competitively serve at acceptable margin is better declined; the capacity goes to margin-positive freight.
- *Partial adjustment* — only when losing the lane is genuinely unacceptable; must be documented and flagged, not silently absorbed.

**Tradeoffs summary:**

| Method | Margin impact | Relationship | Use when |
|---|---|---|---|
| Clarify comparison | Neutral | Constructive | Scope or Incoterm unclear |
| Hold price + value pitch | Preserved | Moderate risk | Non-strategic; competitor scope unclear |
| Give-get reduction | Recovered over time | Strong | Strategic account, real volume commitment |
| Walk from lane | Margin protected | One-time friction | Below floor or poor-fit lane |
| Partial adjustment | Degraded | Preserved | Must-retain account, no give-get path |

---

## Decision Tree: Account Risk Classification — Healthy, Watch, or At-Risk

**When this applies:** the account manager is reviewing the customer portfolio and must classify each account's retention risk before the next QBR cycle. The observable entry: volume or shipment frequency has changed, a service failure occurred, the customer has gone quiet, or a competitor has been in contact.

**Last verified:** 2026-06-05 against standard key account management practice in logistics.

```mermaid
flowchart TD
    START[Account under review] --> Q1{Has shipment volume declined more than 20% quarter-over-quarter?}
    Q1 -->|YES| Q2{Is the decline explained by seasonal or market factors - not us?}
    Q2 -->|YES - external factor| WATCH[Watch - confirm with customer; no action yet]
    Q2 -->|NO or UNCLEAR - may be diverting to competitor| ATRISK[At-risk - immediate outreach and account review]
    Q1 -->|NO - volume stable or growing| Q3{Is there an unresolved service failure or open complaint?}
    Q3 -->|YES| Q4{Has it been acknowledged and a recovery plan communicated?}
    Q4 -->|NO| ATRISK
    Q4 -->|YES and customer acknowledged| WATCH
    Q3 -->|NO| Q5{Is the primary contact still reachable and engaged?}
    Q5 -->|NO - contact gone dark or departed| ATRISK
    Q5 -->|YES| Q6{Is the account multi-threaded - multiple contacts at decision level?}
    Q6 -->|NO - single-threaded| WATCH[Watch - build second contact before the first leaves]
    Q6 -->|YES| HEALTHY[Healthy - maintain standard QBR cadence]
```

**Rationale per leaf:**
- *Watch* — accounts with an external volume decline or a single-contact risk are not immediately at risk but need attention before they become so; schedule a check-in.
- *At-risk* — volume diversion to a competitor, an unacknowledged service failure, or a dark primary contact are early churn signals; escalate immediately.
- *Healthy* — stable volume, no open issues, and multi-threaded relationship: maintain the QBR cadence and look for whitespace.
- *Single-threaded watch* — the single most preventable account loss in freight sales is when the one contact the seller knows leaves; build the second contact now.

**Tradeoffs summary:**

| Classification | Action required | Cadence | Key risk |
|---|---|---|---|
| Healthy | Standard QBR + whitespace | Quarterly | Complacency |
| Watch | Check-in within 2 weeks | Monthly | External becomes internal driver |
| At-risk | Immediate outreach + recovery plan | Weekly until resolved | Churn if not acted on fast |

---

## Decision Tree: New Business Pursuit — Prioritize or Deprioritize

**When this applies:** the seller has a list of prospective accounts to develop and limited prospecting hours. The question is how to allocate pursuit effort across the list. Observable entry: a target list exists, a territory plan is being built, or a pipeline review shows an under-populated early stage.

**Last verified:** 2026-06-05 against standard freight-forwarding ICP and territory-planning practice.

```mermaid
flowchart TD
    START[Prospect on target list] --> Q1{Does the prospect's trade-lane profile match our network strengths?}
    Q1 -->|NO - lanes outside our network| DEPRIO[Deprioritize - add to long-list for future network expansion]
    Q1 -->|YES| Q2{Is there a known trigger event in the last 90 days?}
    Q2 -->|YES - trigger found| HIGHPRIO[High priority - lead with trigger event in outreach]
    Q2 -->|NO - no trigger| Q3{Is the estimated annual freight spend material - above threshold?}
    Q3 -->|NO - small spend| LOW[Low priority - include in automated nurture sequence]
    Q3 -->|YES - material spend| Q4{Do we have a warm intro or an existing contact?}
    Q4 -->|YES| HIGHPRIO
    Q4 -->|NO - cold outreach required| Q5{Can we find a lane-specific hook from available intel?}
    Q5 -->|YES| MED[Medium priority - build hook and sequence; outreach within 2 weeks]
    Q5 -->|NO - no lane intel available| LOW[Low priority - research first before outreach]
```

**Rationale per leaf:**
- *Deprioritize (network mismatch)* — time spent pursuing lanes you cannot competitively serve is time not spent on winnable business; defer until network coverage improves.
- *High priority with trigger* — a trigger event (new sourcing country, carrier service cut, trade lane disruption) is the best opening for outreach; act within 5 days of the trigger.
- *High priority with warm intro* — a warm introduction converts cold outreach into a warm conversation; prioritize regardless of trigger event status.
- *Medium priority* — material spend with a lane hook is winnable business; build the sequence and move quickly.
- *Low priority / research first* — cold outreach without a hook is spam; invest 30 minutes in research before moving to outreach or move the prospect down the list.
- *Automated nurture* — small-spend prospects are not worth direct outreach time but should remain in a light-touch sequence in case their volume grows.

**Tradeoffs summary:**

| Priority | Action | Time investment | Win probability |
|---|---|---|---|
| High (trigger/warm) | Direct outreach within 5 days | High | High |
| Medium (material + hook) | Sequence within 2 weeks | Medium | Medium |
| Low (no hook available) | Research, then sequence | Low upfront | Low until hook found |
| Deprioritize | Long-list, no active outreach | Near-zero | Low until network match |
