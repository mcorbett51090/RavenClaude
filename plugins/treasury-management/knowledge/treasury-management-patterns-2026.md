# Knowledge — Treasury-management patterns (2026)

> **Last reviewed:** 2026-07-14 · **Confidence:** High on the durable concepts (the cash-conversion cycle, direct vs indirect forecasting, the 13-week, hedge instruments & the transaction/translation/economic exposure split, account structures, positive pay / dual auth / BEC controls); **Medium on the dated regulatory/standard/tooling map — hedge-accounting mechanics, ISO 20022 migration timing, AFP codes, and TMS categories change and carry retrieval dates below.**
> The reference the `cash-and-risk-operations-specialist` reads when building forecasts, executing hedges, running payment controls, and administering banks — plus a 2026 standards/tooling snapshot. **This is not legal, tax, or accounting advice; volatile specifics carry a retrieval date and are verified at use.**

The team's discipline: **position cash before forecasting; forecast direct for the near term with a variance loop; scope the exposure before hedging and book the hedge deliberately; run payment controls as procedures not intentions; and reconcile the banks.**

---

## The cash-conversion cycle (CCC) — the working-capital anchor

`CCC = DSO + DIO − DPO`

| Component | Definition | Lever direction |
|---|---|---|
| **DSO** — days sales outstanding | Avg days to collect receivables = (AR / revenue) × days | **Lower** it (collect faster) — frees cash |
| **DIO** — days inventory outstanding | Avg days inventory is held = (inventory / COGS) × days | **Lower** it (turn faster) — frees cash |
| **DPO** — days payable outstanding | Avg days to pay suppliers = (AP / COGS) × days | **Raise** it (pay later, within supplier tolerance) — frees cash |

CCC (days) × daily sales ≈ the cash tied up in operations. A shorter CCC releases cash structurally — the highest-quality liquidity there is (no fee, no covenant). But **DPO extension has a supplier-health ceiling**: past it, terms return as price increases or supply risk — which is why **supply-chain finance** and **dynamic discounting** exist as structured alternatives (see the decision tree).

---

## Cash forecasting — direct vs indirect, and the 13-week

**Direct (receipts-and-disbursements)** — build the forecast from **actual expected cash movements**: receipts (collections driven by the AR aging / DSO, plus known one-offs) minus disbursements (AP payment-run timing / DPO, payroll, tax, debt service, capex, dividends). Granular, accurate near-term, and driver-diagnosable. **This is the method for the operating horizon and the 13-week.**

**Indirect** — start from **net income**, add back non-cash items (D&A), and adjust for **working-capital changes** (Δ AR, Δ inventory, Δ AP) and financing/investing — i.e. forecast cash from the P&L and balance sheet. Coarser but sustainable over a **longer, statement-linked horizon** (quarters/year). Use it where line-by-line direct forecasting can't be maintained.

**The 13-week cash flow (TWCF)** — the treasury workhorse: 13 weekly columns, built **direct**, rolled forward every week with a **variance-to-actual loop** (forecast → actuals → variance by line → re-forecast, tuning drivers from the miss). It's the operating-liquidity radar — the trough it reveals sizes the buffer. A 13-week without a back-test is a wish, not a forecast.

**The cash position** — the anchor beneath the forecast: opening bank balances + confirmed receipts − confirmed disbursements → **available liquidity** per currency and entity (net of holds, minimums, un-cleared items). Forecast from where the money *is*, not from the earnings.

---

## Liquidity policy — buffer, committed vs uncommitted, the revolver

- **Minimum-cash / liquidity buffer** — sized on the **stressed forecast trough** (a receipts shock, a facility pulled, a covenant tightening, a seasonal low), plus any covenant / minimum-operating-cash floor — **not** the average month.
- **Committed vs uncommitted facilities** — **committed** = contractually available (a revolver, worth its commitment fee) → size the buffer on this; **uncommitted** = withdrawable at the bank's discretion → flexibility, but never the backstop.
- **Revolver management** — keep headroom you can actually **draw when stressed**; check the draw conditions and financial covenants don't lock the line exactly when a seasonal swing or a shock would breach them. A committed line behind a covenant you'll trip is not really available.

---

## Bank relationship & account structure

- **Relationship banking & wallet share** — credit is scarce; banks allocate it to clients who give them ancillary business (cash management, FX, fees). Concentrate the **wallet** to the banks you need to **lend**, and don't spread it so thin that no bank values the relationship.
- **Account rationalization** — close redundant accounts; every account is fee, fraud surface, and reconciliation cost. Fewer, purposeful accounts.
- **ZBA / target-balance** — auto-sweep operating accounts to/from a header account so balances concentrate and idle cash is minimized (same legal entity/country).
- **Notional vs physical pooling** — *notional*: offset entity balances for **interest** with **no title transfer** (simplest; not permitted in every jurisdiction/bank). *Physical*: actually **sweep** cash to concentrate it, creating **intercompany loans** → transfer-pricing / thin-cap questions.
- **In-house bank (POBO / COBO)** — payments-on-behalf-of / collections-on-behalf-of: centralize payments, FX, and liquidity with internal accounts per entity. A **scale** play with heavy **tax/legal/regulatory** design — route that design out.
- **KYC / onboarding** — new accounts require KYC, beneficial-ownership, and signer/entitlement setup; budget the lead time.
- **Bank fee analysis (AFP service codes)** — banks bill monthly account-analysis statements using standardized **AFP service codes**; reconcile the **billed** charges against the **analyzed volume** — misbilling and un-negotiated per-item prices are common and recoverable.
- **Reporting & connectivity** — **BAI2** (legacy US balance/transaction format) and **ISO 20022 `camt`** (camt.052/.053/.054 — intraday/prior-day/notification statements) for reporting; **`pain`** (pain.001 payment initiation, pain.002 status) for sending payments. Transport over **host-to-host** (direct file exchange), **SWIFT** (the bank-agnostic network, incl. SCORE/gpi), or **bank APIs** — matched to volume and the bank's support. _(ISO 20022 formats/versions are volatile — retrieved 2026-07-14.)_

---

## Investment & debt

- **Investment policy statement (IPS)** — orders objectives **safety > liquidity > yield**: capital preservation first, same-day access second, return last. Specifies **eligible instruments** (bank deposits, government MMFs, T-bills, high-grade CP/agency), **credit-quality floors**, **concentration** and **tenor limits**, and the **approval/exception** path. Chasing yield with operating cash is the classic treasury failure.
- **Money-market instruments** — T-bills, government/prime MMFs, commercial paper, repo, short agencies — the operating-surplus toolkit within the IPS limits.
- **Debt & covenants** — track **financial covenants** (leverage, interest-coverage, minimum-liquidity) continuously, not at quarter-end; a covenant breach can block a revolver draw or accelerate debt. Model covenant headroom in the 13-week / forecast.
- **Rating agencies** — for rated issuers, the rating drives funding cost and market access; treasury manages the metrics and the agency relationship. _(Rating criteria are volatile — verify at use.)_

---

## FX & interest-rate risk

**Exposure classes** (scope before hedging):

| Class | What it is | Typical stance |
|---|---|---|
| **Transaction** | A contracted / highly-probable foreign-currency cash flow, or a floating-rate coupon | Hedge if material — real, datable cash risk |
| **Translation** | The reporting-currency value of a foreign sub's net assets on consolidation | Usually **accept** — non-cash equity/OCI; hedging spends cash to smooth a non-cash line |
| **Economic / operating** | Competitive exposure to rates/FX not tied to one contracted flow | Structural / operational hedges (pricing, sourcing); financial hedge rarely a clean fit |

**Hedge dials** — **hedge ratio** (rarely 100% — layer/ladder more of the near, less of the far) and **hedge horizon** (matched to the exposure's certainty; highly-probable flows can be hedged further out).

**Instruments:**

| Instrument | Payoff | Use for |
|---|---|---|
| **Forward** | Locks a rate; zero premium; gives up favorable moves (obligation) | A certain FX transaction exposure — the default |
| **Swap** | Exchanges rate/currency streams (fixed↔floating; cross-currency) | Interest-rate exposure; cross-currency funding |
| **Option** | Premium buys protection while keeping the upside | Uncertain flows; when the upside has value |
| **Collar** | Buy a protective option, sell one to fund it — caps cost, caps upside | A premium-reduced middle ground |

**Hedge accounting (ASC 815 / IFRS 9)** — *optional* special accounting bought with **contemporaneous documentation** + ongoing **effectiveness** testing, to align the hedge's P&L timing with the hedged item:

- **Cash-flow hedge** — for a **variable/forecast** exposure (a future FX flow, a floating-rate coupon); the **effective** gain/loss parks in **OCI** and releases to P&L when the hedged item hits earnings. Smooths reported P&L.
- **Fair-value hedge** — for a **fixed** exposure whose fair value moves (fixed-rate debt vs rates); both the hedge and the hedged item are marked through **P&L**.
- **No designation** — book it as an **economic hedge through P&L**; valid when the documentation cost exceeds the smoothing benefit — just disclose the earnings volatility.

> **Volatile + not accounting advice:** ASC 815 (US GAAP) and IFRS 9 mechanics — designation criteria, effectiveness methods, the highly-probable threshold — change and have nuance. Treat the above as durable concepts, and **confirm the current treatment with a qualified accountant before booking.** _(Retrieved 2026-07-14.)_

---

## Payments & fraud controls

- **Positive pay** — send the bank the **issued-check file** (number, amount, payee); the bank holds any mismatch for review. **Reverse positive pay** — the bank sends presented items for the company to approve/decline. **ACH debit blocks/filters** — block unauthorized ACH debits; allow only whitelisted originators.
- **Dual authorization & segregation of duties (SoD)** — **initiator ≠ approver ≠ reconciler** on every payment run; no one person can create, release, and reconcile a payment.
- **BEC / vendor-impersonation** — business email compromise is the **dominant** payments-fraud loss vector. Defense: any **vendor bank-detail change** is verified by a **callback to a known number** (never the number/contact on the change request), and urgency-pressured payment-instruction emails are treated as suspect. Out-of-band verification is the control that works.
- **Sanctions screening** — screen the payee/counterparty against sanctions lists as a payment control; **deep OFAC/AML program design and list management route to `regulatory-compliance`** — treasury runs the screen, compliance owns the program.

---

## Working-capital optimization (structured levers)

- **DSO reduction** — e-invoicing (kill dispute lag), electronic payment options, tighter credit terms/limits, disciplined collections/dunning, early-pay incentives (weigh the discount vs days saved).
- **DPO extension** — free cash by paying later, **within supplier tolerance**; past it, terms return as price increases.
- **Supply-chain finance (reverse factoring)** — a bank/platform pays the supplier early at the **buyer's** credit rating; the buyer holds/extends DPO, the supplier gets cheaper faster cash. Best when the buyer's rating ≫ suppliers'. **Watch the accounting/disclosure** — aggressive SCF can look like hidden debt to rating agencies/regulators.
- **Dynamic discounting** — the **buyer** uses its **own** surplus cash to pay early for a sliding discount; an *investment* decision, valid when the discount yield beats the short-term investment alternative and the cash isn't needed for the buffer.
- **Inventory financing / warehouse receipts** — bridge a seasonal build (a timing gap), not a permanent DIO problem.

---

## TMS (treasury management system) landscape — dated, volatile

The tiering, not the vendors:

| Tier | Fits | Selection trigger to the next tier |
|---|---|---|
| **Spreadsheet** | Few entities/banks/currencies, low hedge volume, manual bank logins | Entity/bank/currency count rises; error/key-person risk; manual reconciliation dominates |
| **ERP treasury module** | Already on a major ERP; moderate complexity; wants integration with GL/AP/AR | Need multi-bank connectivity, hedge/exposure management, or a real cash-forecasting engine the ERP module lacks |
| **Dedicated TMS** | Many entities/banks/currencies, rolling hedge programs, in-house bank / pooling, SWIFT/host-to-host connectivity, strong controls & audit | (Top tier) — justify by complexity, connectivity, and control needs, not prestige |

**Selection triggers (the real drivers):** entity / bank / account / currency count; hedge and intercompany volume; connectivity needs (host-to-host, SWIFT, ISO 20022, API); pooling / in-house-bank structure; and the control/audit/reporting bar. Don't buy a dedicated TMS for spreadsheet-scale complexity, and don't run a global in-house bank on spreadsheets. _(TMS categories/vendors are volatile — retrieved 2026-07-14; re-verify before a selection.)_

---

## 2026 standards & tooling map (dated — volatile, re-verify before quoting)

- **Payment/reporting standards:** **ISO 20022** — `camt` (statements: camt.052/.053/.054), `pain` (initiation: pain.001, status pain.002) — is the modern XML standard; **BAI2** remains a legacy US reporting format. High-value rails have been migrating to ISO 20022. _(Retrieved 2026-07-14; migration timing volatile.)_
- **Connectivity:** host-to-host (direct file exchange), **SWIFT** (bank-agnostic network — SCORE, gpi tracking), and **bank APIs** (real-time balances/payments) — support varies by bank. _(Retrieved 2026-07-14.)_
- **Bank-fee analysis:** **AFP service codes** standardize account-analysis line items for cross-bank fee comparison. _(Retrieved 2026-07-14.)_
- **Hedge-accounting standards:** **ASC 815** (US GAAP) and **IFRS 9** — cash-flow vs fair-value, documentation + effectiveness. **Not accounting advice; confirm current treatment with a qualified accountant.** _(Retrieved 2026-07-14.)_
- **TMS categories:** spreadsheet → ERP treasury module → dedicated TMS (plus point solutions for forecasting, connectivity, and fraud controls). Vendor landscape volatile — verify at selection. _(Retrieved 2026-07-14.)_

---

## Provenance

- Durable concepts (the cash-conversion cycle, direct vs indirect forecasting, the 13-week + variance loop, the cash position, stressed-trough buffer sizing, committed vs uncommitted facilities, relationship banking, ZBA / notional vs physical pooling / in-house bank, the safety>liquidity>yield IPS ordering, the transaction/translation/economic exposure split, forwards/swaps/options/collars, cash-flow vs fair-value hedge concepts, positive pay / dual auth / SoD / BEC controls, SCF vs dynamic discounting) are consensus corporate-treasury practice reviewed 2026-07-14 — **High confidence**.
- The regulatory/standard/tooling map — ASC 815 / IFRS 9 mechanics, ISO 20022 (`camt`/`pain`) versions & migration timing, AFP service codes, rating criteria, and TMS categories — is a **2026-07 snapshot**; these are volatile, carry the retrieval dates above, and are **not legal/tax/accounting advice** — re-verify with `ravenclaude-core/deep-researcher` and a qualified professional before pinning in a deliverable. _(Reviewed 2026-07-14.)_
