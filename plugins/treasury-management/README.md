# treasury-management

> The **corporate-treasury layer** for Claude Code — the team that answers *"how much cash do we need and where, in what currency and at what rate — who banks us, and how do we move and protect the money?"* and executes the answer. Two agents: the **treasury-strategy-lead** (sets the liquidity policy, bank & account structure, investment policy statement, FX/rate hedge program, and TMS strategy) and the **cash-and-risk-operations-specialist** (positions cash, builds the forecast, executes & books hedges, runs the payment fraud controls, and administers the banks).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

> **Not legal, tax, or accounting advice.** Volatile hedge-accounting (ASC 815 / IFRS 9), bank/regulatory, and standards specifics carry a retrieval date — verify at use, and confirm with a qualified professional before a board/bank commitment.

## What it does

| You ask | It returns |
|---|---|
| "How much cash and committed liquidity should we hold, and in what facilities?" | A stress-tested minimum-cash/buffer target, a committed vs uncommitted facility mix, and revolver headroom — with the conditions that would resize it |
| "Build our 13-week cash forecast and today's cash position." | A per-currency/entity cash position and a rolling 13-week direct (receipts-and-disbursements) forecast with driver assumptions and a variance-to-actual loop |
| "Should we notional-pool, physically sweep, or run an in-house bank?" | An account-structure recommendation (ZBA/target-balance, notional vs physical pooling, in-house bank/POBO-COBO, account rationalization) with the tax/legal/regulatory seams flagged |
| "Should we hedge this FX / interest-rate exposure — and how?" | A hedge-vs-accept decision (with "do nothing" on the menu), hedge ratio & horizon, the instrument (forward/swap/option/collar), and the ASC 815 / IFRS 9 accounting stance |
| "Set up positive pay and dual authorization on our payment run." | A payments-controls implementation: positive pay/reverse positive pay, dual auth + segregation of duties, and a BEC / vendor-bank-change callback-verification procedure |
| "How do we free up working capital?" | The cash-conversion-cycle levers (DSO/DIO/DPO) ranked by cash freed — DPO vs supply-chain finance / dynamic discounting, DSO reduction, inventory financing |
| "Have we outgrown spreadsheets — do we need a TMS?" | A TMS-tier recommendation (spreadsheet / ERP treasury module / dedicated TMS) tied to the entity/bank/currency/hedge/connectivity complexity triggers |

**Two rules it never breaks:** *liquidity is survival, yield is a bonus* (safety > liquidity > yield; size the buffer on the stressed trough), and *payment fraud controls are non-negotiable* (positive pay, dual auth, segregation of duties, and callback verification of every vendor bank-detail change — BEC is when-not-if).

## What's inside

- **2 agents** — `treasury-strategy-lead` (sets the liquidity policy, bank & account structure, investment policy statement, FX/rate risk-management policy & hedge program, and TMS strategy) and `cash-and-risk-operations-specialist` (positions cash, builds the 13-week/direct forecast, executes & books hedges with hedge accounting, runs positive pay / dual auth / BEC controls, and does bank admin — onboarding, AFP-code fee analysis, ISO 20022 camt/pain connectivity).
- **3 skills** — `build-cash-forecast-and-liquidity-plan`, `design-fx-and-interest-rate-hedge`, `optimize-working-capital-and-payments`.
- **2 knowledge files** — a Mermaid treasury decision tree (buffer sizing, invest-vs-payoff, hedge-vs-accept, pooling/in-house-bank, payment-method + trade-off tables) and a 2026 treasury-patterns reference (the cash-conversion cycle, direct/indirect forecasting, hedge instruments & ASC 815 / IFRS 9 hedge accounting, account structures, payment fraud controls, the TMS landscape, and a dated standards/tooling map).
- **2 templates** — a cash forecast & liquidity policy and a hedge decision & FX/rate risk register.

## Where it sits in the finance stack

```
treasury-management (HERE)     →  the CASH and the BANK RELATIONSHIP     ("how much cash, where; who banks us; move & protect it")
finance                        →  FP&A / budgeting / the P&L plan         ("the earnings plan")
fintech-payments-engineering   →  payment-rail / API / ledger code        ("building the movement of money")
regulatory-compliance          →  deep AML / OFAC / sanctions programs     ("the compliance program")
procurement-sourcing           →  supplier terms & sourcing               ("the DPO source")
internal-audit                 →  audit of treasury controls              ("independent assurance")
```

This plugin is the **corporate-treasury layer**: it forecasts and protects the **cash** and owns the **bank relationship**, and stays clear of the *earnings plan* (`finance`), the *rail engineering* (`fintech-payments-engineering`), and the *compliance program* (`regulatory-compliance`).

## Domain stance

Concept-first (liquidity before yield, the cash-conversion cycle, the stressed-trough buffer, direct vs indirect forecasting + the 13-week + variance loop, exposure-class-before-hedge with "do nothing" as a valid decision, notional vs physical pooling and the in-house bank as a scale play, positive pay / dual auth / SoD / BEC controls), fluent across **committed vs uncommitted facilities**, **ZBA / notional & physical pooling / POBO-COBO**, the **safety > liquidity > yield** investment policy, **forwards / swaps / options / collars** with **ASC 815 / IFRS 9** hedge accounting, **AFP-service-code** bank-fee analysis, **BAI2 / ISO 20022 (camt / pain)** reporting over host-to-host / SWIFT / API, and the **spreadsheet → treasury module → TMS** tiering. Hedge-accounting rules, AFP codes, ISO 20022 timing, and rating criteria carry retrieval dates — re-verify (and confirm with a qualified professional) before pinning in a client deliverable. **Not legal, tax, or accounting advice.**

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install treasury-management@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
