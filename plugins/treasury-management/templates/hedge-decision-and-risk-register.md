# Hedge decision & FX/rate risk register — <company / entity>

> Captured when deciding whether and how to hedge an FX or interest-rate exposure, and the running register of the exposures and their hedges. Pairs with
> [`cash-forecast-and-liquidity-policy.md`](cash-forecast-and-liquidity-policy.md) (the cash/liquidity side of the same treasury policy).
> **Not legal, tax, or accounting advice.** Hedge-accounting mechanics (ASC 815 / IFRS 9) are volatile — carry a retrieval date and confirm treatment with a qualified accountant before booking.

**Owner:** <name> · **Date:** <YYYY-MM-DD> · **Reporting currency:** <e.g. USD> · **Status:** draft / approved · **Review cadence:** <monthly>

## 1. Exposure scope (scope before you hedge)
- **Exposure:** <what it is — e.g. €10M highly-probable EUR revenue over 12 months / $200M floating-rate term loan>
- **Class:** <transaction (contracted/highly-probable cash) · translation (foreign-sub net assets) · economic/operating>
- **Amount & currency / rate:** <€10M · SOFR + 250>
- **Timing / horizon:** <when the cash flows / the tenor>
- **Materiality:** <material / immaterial — vs earnings, cash, covenants>
- **Measurable & (for forecast) highly probable?** <yes / no>

## 2. Hedge-vs-accept decision
- **Decision:** <HEDGE · ACCEPT (do nothing) — governed>
- **Rationale:** <material + measurable + adverse-volatility matters → hedge · immaterial / naturally offset / un-economic / translation-only → accept>
- **If ACCEPT:** <why it's a governed accept — natural offset · immateriality · hedge cost > risk reduced · non-cash translation>

## 3. Hedge design (if hedging)
- **Hedge ratio:** <e.g. 75% near / 50% far — layered/laddered — WHY>
- **Horizon:** <matched to certainty — e.g. 12 months, declining coverage>
- **Instrument:** <forward · swap · option · collar — WHY that payoff>
- **Counterparty:** <bank(s) · credit line used · sanctions-screen cleared>

## 4. Hedge accounting stance (ASC 815 / IFRS 9 — a deliberate cost)
- **Seek hedge accounting?** <yes / no>
- **Designation:** <cash-flow (variable/forecast → OCI, release to P&L) · fair-value (fixed → both through P&L) · none (economic — through P&L)>
- **Contemporaneous documentation done?** <at inception — exposure, instrument, risk, effectiveness method>
- **Effectiveness method & result:** <method · latest assessment>
- **If none:** <accept the P&L volatility — disclosed>
- *Confirm current ASC 815 / IFRS 9 treatment with a qualified accountant (<retrieval date>).*

## 5. Flip conditions (what changes the design)
- <e.g. forecast flow drops below "highly probable" → cash-flow designation lost → through P&L>
- <e.g. rates expected to fall → collar/option beats a locked forward>
- <e.g. exposure becomes immaterial → flip to accept>

## 6. Risk register (running)
| # | Exposure | Class | Amount | Decision | Instrument | Hedge ratio | Accounting | Next review | Owner |
|---|---|---|---|---|---|---|---|---|---|
| 1 | <EUR revenue> | transaction | €10M | hedge | forward+collar | 75/50 | cash-flow | <date> | <name> |
| 2 | <floating debt> | transaction | $200M | hedge | payer swap | 60% | cash-flow | <date> | <name> |
| 3 | <EUR sub net assets> | translation | €40M | accept | — | — | n/a | <date> | <name> |

## 7. Execution & settlement (hand-off to operations)
- **Trade execution:** <who executes · when · at policy ratio>
- **Confirmation / settlement / rollover:** <mechanics · rollover dates>
- **Booking:** <designated per §4 · documentation filed>

## Seams (not this team)
- **The accounting entries / audit of hedge accounting:** the controller / external auditor (this is not accounting advice)
- **Deep sanctions/counterparty screening program:** regulatory-compliance
- **Trade / confirmation / treasury systems engineering:** fintech-payments-engineering
- **FP&A budget / P&L plan the exposure feeds:** finance
- **Controls audit:** internal-audit

## Open questions / risks
- <list>

**Sign-off:** <treasurer / CFO> · <date> · *Not legal/tax/accounting advice — ASC 815 / IFRS 9 treatment confirmed with a qualified accountant (<retrieval date>).*
