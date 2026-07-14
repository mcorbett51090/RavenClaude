# Knowledge — Treasury-management decision trees

> **Last reviewed:** 2026-07-14 · **Confidence:** Medium-High (consensus on the liquidity-buffer, invest-vs-payoff, hedge-vs-accept, pooling/in-house-bank, and payment-method framings, and on the safety>liquidity>yield ordering; **specific hedge-accounting mechanics (ASC 815 / IFRS 9), bank-fee/AFP codes, ISO 20022 migration timing, and rating criteria are volatile — re-verify before a board/bank commitment**).
> The most-asked treasury questions are "how much cash do we need and where?", "invest the surplus or pay down debt?", "hedge this exposure or accept it?", "pool/sweep or run an in-house bank?", and "which payment method?". These are the decision trees the `treasury-strategy-lead` traverses **before** naming a structure or instrument, plus the trade-off tables and the seams to adjacent plugins.

The team's discipline: **name the objective first (solvency/liquidity before yield), name the exposure before the hedge, and name the structure before the instrument.** This is **not legal, tax, or accounting advice** — volatile rule and bank specifics carry a retrieval date and are verified at use. FP&A/budget/P&L questions — the *earnings plan* — leave this layer for `finance`; treasury owns the **cash** and the **bank relationship**.

---

## Decision Tree 1: sizing the minimum-cash / liquidity buffer

Gate on the **forecast trough under stress**, not the average month.

```mermaid
graph TD
  Start([How much cash must we hold?]) --> POS[Build the cash position<br/>· per currency & entity<br/>· available liquidity today]
  POS --> FC[Rolling 13-week direct forecast<br/>· receipts driven by DSO<br/>· disbursements by AP run / payroll / tax / debt]
  FC --> TROUGH{Find the intra-period trough<br/>the worst cumulative low}
  TROUGH --> STRESS{Stress it}
  STRESS -->|Receipts shock<br/>big customer slips| S1[Deepen the trough]
  STRESS -->|Facility pulled<br/>uncommitted line withdrawn| S2[Remove that liquidity]
  STRESS -->|Covenant tightens<br/>revolver draw blocked| S3[Committed headroom not really available]
  STRESS -->|Seasonality low| S4[Model the worst season]
  S1 --> BUF
  S2 --> BUF
  S3 --> BUF
  S4 --> BUF
  BUF[Minimum-cash / buffer target =<br/>stressed trough + covenant / min-operating floor] --> GAP{Buffer > cash on hand?}
  GAP -->|Yes| FAC[Cover with COMMITTED facilities<br/>· revolver headroom you can draw stressed<br/>· check draw conditions/covenants]
  GAP -->|No| HOLD[Hold to buffer; invest only the true surplus<br/>see Tree 2]
```

---

## Decision Tree 2: invest the surplus vs pay down debt (and the IPS gate)

Only the **true surplus** above the buffer is investable; the IPS orders **safety > liquidity > yield**.

```mermaid
graph TD
  Start([Surplus cash above the buffer?]) -->|No surplus| NONE[Hold to buffer — nothing to deploy]
  Start -->|Yes, true surplus| DEBT{Revolver / expensive debt drawn?}
  DEBT -->|Yes| PAYOFF[Pay down the revolver / highest-rate debt first<br/>· risk-free after-tax return = the rate saved<br/>· restores committed headroom]
  DEBT -->|No / debt is cheap fixed| INVEST{Invest per the IPS}
  INVEST --> IPS[IPS order: SAFETY &gt; LIQUIDITY &gt; YIELD]
  IPS --> HORIZON{When is the cash needed?}
  HORIZON -->|Days / operating| MMF[Same-day: bank deposit / MMF / T-bills<br/>· capital preservation + instant access]
  HORIZON -->|Weeks-months / strategic| SHORT[Short-dated high-grade:<br/>· CP, agency, short T-notes<br/>· within credit/concentration/tenor limits]
  HORIZON -->|Structural excess| RETURN[Return to shareholders / M&A<br/>· a capital-allocation call → finance]
```

> **The classic failure:** reaching for yield with **operating** cash. Operating cash is for solvency and access; only the strategic surplus, within the IPS limits, chases return — and paying down drawn expensive debt is usually the best risk-free "investment."

---

## Decision Tree 3: hedge the exposure vs accept it

Scope the **exposure class first**; **"do nothing" is a valid, governed outcome.**

```mermaid
graph TD
  Start([An FX or rate exposure]) --> CLASS{Which class?}
  CLASS -->|Transaction<br/>contracted / highly-probable cash flow| MAT1{Material & measurable?}
  CLASS -->|Translation<br/>foreign-sub net assets on consolidation| TRANS[Usually ACCEPT<br/>· non-cash equity/OCI item<br/>· hedging spends cash to smooth a non-cash line<br/>· hedge only for a specific covenant/rating reason]
  CLASS -->|Economic / operating<br/>competitive rate/FX exposure| ECON[Structural / operational hedges<br/>· pricing, sourcing, natural offset<br/>· financial hedge rarely a clean fit]
  MAT1 -->|No — immaterial / naturally offset| ACCEPT[ACCEPT — do nothing<br/>· governed, documented]
  MAT1 -->|Yes| HEDGE{Hedge cost &lt; risk reduced?}
  HEDGE -->|No| ACCEPT
  HEDGE -->|Yes| RATIO[Set hedge ratio &amp; horizon<br/>· layer/ladder — more near, less far<br/>· match horizon to certainty]
  RATIO --> INSTR{Instrument for the payoff}
  INSTR -->|Certain FX flow, no premium| FWD[Forward — locks rate, gives up upside]
  INSTR -->|Interest-rate / cross-currency stream| SWAP[Swap — fixed↔floating / currency]
  INSTR -->|Uncertain flow, keep upside| OPT[Option — premium buys protection + upside]
  INSTR -->|Premium-reduced middle| COLLAR[Collar — buy protection, sell to fund it]
  FWD --> HA
  SWAP --> HA
  OPT --> HA
  COLLAR --> HA
  HA{Hedge accounting? ASC 815 / IFRS 9} -->|Variable / forecast exposure| CFH[Cash-flow hedge → OCI, release to P&L<br/>· needs contemporaneous docs + effectiveness]
  HA -->|Fixed exposure whose fair value moves| FVH[Fair-value hedge → both through P&L]
  HA -->|Docs cost &gt; smoothing benefit| PL[Economic hedge through P&L<br/>· disclose the earnings volatility]
```

---

## Decision Tree 4: account structure & cash concentration (pooling / in-house bank)

Structure follows the **cash map**; scale justifies the structure.

```mermaid
graph TD
  Start([Rationalize the account structure]) --> RAT[Account rationalization<br/>· close redundant accounts<br/>· concentrate wallet to relationship banks that lend]
  RAT --> CONC{Concentrate cash how?}
  CONC -->|Same legal entity / country| ZBA[ZBA / target-balance sweeps<br/>· auto-sweep to a header account<br/>· operational, low complexity]
  CONC -->|Multi-entity, keep balances gross| NOTIONAL[Notional pooling<br/>· offset balances for interest, NO title transfer<br/>· bank & jurisdiction must permit it]
  CONC -->|Multi-entity, physically move cash| PHYSICAL[Physical pooling / cash concentration<br/>· real sweeps → intercompany loans<br/>· transfer-pricing / thin-cap questions]
  ZBA --> SCALE
  NOTIONAL --> SCALE
  PHYSICAL --> SCALE
  SCALE{Scale: many entities / currencies / high intercompany volume?} -->|Yes| IHB[In-house bank / POBO-COBO<br/>· centralize payments & FX<br/>· internal accounts per entity<br/>· TAX + LEGAL + REGULATORY seams]
  SCALE -->|No| KEEP[Keep pooling/ZBA — don't over-engineer]
  IHB --> SEAM[[Route tax/legal/regulatory design out:<br/>transfer pricing, thin-cap, sanctions → the right seam]]
```

> **Notional vs physical:** *notional* offsets balances for interest with **no** movement of title (simplest, but not permitted in every jurisdiction/bank); *physical* actually sweeps cash, creating **intercompany loans** with transfer-pricing and thin-cap implications. An **in-house bank** (payments-on-behalf-of / collections-on-behalf-of) is a scale play — powerful, but its tax/legal/regulatory design is **not** decided here.

---

## Decision Tree 5: payment-method choice

Match method to **value, urgency, finality, and cost**.

```mermaid
graph TD
  Start([Which payment method?]) --> URG{Time-critical & final?}
  URG -->|Yes, high value| WIRE[Wire — fast, final, expensive]
  URG -->|Yes, instant + final| RTP[RTP / instant rail — fast + final]
  URG -->|No, batch at volume| ACH[ACH — cheap, batched, reversible window<br/>· payroll, vendors]
  Start --> REBATE{Rebate/float & accepted?}
  REBATE -->|Yes| CARD[Card — rebate + float, merchant cost]
  Start --> LEGACY{Legacy / no electronic option?}
  LEGACY -->|Yes| CHECK[Check — MINIMIZE<br/>· highest fraud exposure<br/>· require positive pay]
```

---

## Trade-off table — liquidity facilities

| Facility | Sweet spot | Watch out for |
|---|---|---|
| **Committed revolver** | Backstop liquidity you can rely on when stressed | Commitment fee; covenants can block the draw exactly when needed — check them |
| **Uncommitted line** | Cheap day-to-day flexibility | Can be withdrawn at the bank's discretion — don't size the buffer on it |
| **Term debt** | Funding a known long-dated need | Rate/covenant lock; less flexible than a revolver |
| **Money-market / MMF / T-bills** | Parking the operating surplus with same-day access | Yield ≠ the goal; watch credit quality & the IPS limits |

## Trade-off table — DPO levers (working capital)

| Lever | Sweet spot | Watch out for |
|---|---|---|
| **Extend payment terms** | Free cash when suppliers can absorb it | Pushed too far → price increases, supply risk |
| **Supply-chain finance (reverse factoring)** | Buyer rating ≫ supplier rating; supplier gets cheap early cash, buyer holds DPO | Accounting/disclosure — can look like hidden debt to rating agencies/regulators |
| **Dynamic discounting** | Cash-rich buyer; discount yield beats the MMF alternative | It's an *investment* of surplus cash — don't deploy the buffer |
| **Inventory financing / warehouse receipts** | Bridge a seasonal build (a timing gap) | Costs interest — not a fix for a permanent DIO problem |

## Trade-off table — cash concentration structures

| Structure | Sweet spot | Watch out for |
|---|---|---|
| **ZBA / target-balance** | Same-entity/country auto-concentration | Operational only; doesn't cross legal entities cleanly |
| **Notional pooling** | Interest offset without moving cash | Not permitted in every jurisdiction/bank; regulatory constraints |
| **Physical pooling** | Actually concentrating multi-entity cash | Creates intercompany loans → transfer-pricing / thin-cap |
| **In-house bank (POBO/COBO)** | Large, multi-entity, high intercompany volume | Heavy tax/legal/regulatory design — route out; don't over-engineer for small scale |

---

## Seams (treasury is the cash & bank layer, not the whole finance stack)

- **FP&A / budget / P&L / capital budgeting** → `finance` (the *earnings plan*; treasury forecasts the **cash**, not the earnings).
- **Payment-rail / API / ledger engineering** (building the movement of money in code) → `fintech-payments-engineering`.
- **Deep AML / OFAC / sanctions program design & screening** → `regulatory-compliance` (treasury *runs* the screen; the program is designed there).
- **Supplier payment-term negotiation & procurement** (the DPO source) → `procurement-sourcing`.
- **Independent audit of treasury controls** → `internal-audit`.
- **The tax/legal design of pooling, intercompany loans, and in-house banks** → the relevant tax/legal function (not decided in this plugin).

---

## Provenance

- Durable framings (solvency/liquidity before yield, stressed-trough buffer sizing, the safety>liquidity>yield IPS ordering, exposure-class-before-hedge, "do nothing" as a governed hedge choice, notional vs physical pooling, in-house-bank as a scale play, the payment-method and DPO-lever trade-offs, the cash-conversion cycle) are consensus corporate-treasury practice reviewed 2026-07-14 — **High confidence**.
- Hedge-accounting mechanics (ASC 815 / IFRS 9 cash-flow vs fair-value, documentation & effectiveness), bank-fee/AFP service codes, ISO 20022 (`camt`/`pain`) migration timing, and rating-agency criteria are **volatile**, carry retrieval dates, and are **not legal/tax/accounting advice** — re-verify with `ravenclaude-core/deep-researcher` and a qualified professional before a board/bank commitment. _(Reviewed 2026-07-14.)_
