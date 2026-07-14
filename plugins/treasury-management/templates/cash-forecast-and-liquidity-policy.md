# Cash forecast & liquidity policy — <company / entity>

> The one-page artifact captured when setting the liquidity plan. Pairs with
> [`hedge-decision-and-risk-register.md`](hedge-decision-and-risk-register.md) (the FX/rate side of the same treasury policy).
> **Not legal, tax, or accounting advice.** Volatile facility/covenant/bank specifics carry a retrieval date — verify at use.

**Owner:** <name> · **Date:** <YYYY-MM-DD> · **Reporting currency:** <e.g. USD> · **Status:** draft / approved · **Review cadence:** <weekly forecast / quarterly policy>

## 1. Cash position (the anchor — from where the money is)
| Entity / currency | Bank(s) | Opening balance | Confirmed in | Confirmed out | Available liquidity | Notes (holds / minimums) |
|---|---|---|---|---|---|---|
| <US / USD> | <bank> | <$> | <$> | <$> | <$> | <un-cleared / min-operating> |
| <EU / EUR> | <bank> | <€> | <€> | <€> | <€> | |
| **Total (reporting ccy)** | | | | | **<$>** | |

## 2. Forecast method
- **Operating horizon (13-week):** direct / receipts-and-disbursements
- **Longer horizon (quarters/year):** indirect (net income + working-capital changes) — <if maintained>
- **Rebuild cadence:** rolled forward <weekly>, with a variance-to-actual loop

## 3. Rolling 13-week (direct) — summary
```
Wk:      1   2   3   4   5   6   7   8   9  10  11  12  13
Recpts   .   .   .   .   .   .   .   .   .   .   .   .   .   (driver: DSO / AR aging + one-offs)
Disbmts  .   .   .   .   .   .   .   .   .   .   .   .   .   (driver: AP run / payroll / tax / debt / capex)
Net      .   .   .   .   .   .   .   .   .   .   .   .   .
Cum cash .   .   .   .   .  [TROUGH]  .   .   .   .   .   .
```
- **Intra-period trough:** <$ · which weeks>
- **Key receipt drivers:** <DSO assumption · top customers · one-offs>
- **Key disbursement drivers:** <AP run timing / DPO · payroll · tax · debt service · capex · dividends>

## 4. Variance loop (last cycle)
| Line | Forecast | Actual | Variance | Driver correction |
|---|---|---|---|---|
| Receipts | <$> | <$> | <$> | <collections ran N days slow → tune DSO> |
| Disbursements | <$> | <$> | <$> | <run slipped a week → shift> |

## 5. Minimum-cash / liquidity buffer (stress-tested)
- **Base trough:** <$>
- **Stress applied:** <receipts shock · facility pulled · covenant tightening · seasonal low>
- **Stressed trough:** <$>
- **Covenant / min-operating floor:** <$>
- **BUFFER TARGET (minimum cash to hold):** **<$>**

## 6. Facilities & revolver
| Facility | Committed? | Limit | Drawn | Headroom | Commitment fee | Draw conditions / covenants |
|---|---|---|---|---|---|---|
| <Revolver> | committed | <$> | <$> | <$> | <bps> | <leverage / coverage — could block draw?> |
| <Line> | uncommitted | <$> | — | <not counted in buffer> | — | <withdrawable> |
- **Gap (buffer − cash on hand):** <$> → covered by <committed revolver headroom>
- **Committed headroom actually drawable when stressed?** <yes — covenant OK · no — buffer must absorb>

## 7. Surplus deployment (only above the buffer — IPS: safety > liquidity > yield)
- **True surplus above buffer:** <$>
- **Pay down expensive/drawn debt first?** <revolver rate saved = risk-free return>
- **Invest the remainder:** <MMF / T-bills / short high-grade — within IPS credit/concentration/tenor limits>

## 8. Resize conditions (what changes the buffer/facility plan)
- <e.g. a top-3 customer's terms extend → trough deepens → buffer rises>
- <e.g. revolver covenant tightens → committed headroom not available → buffer absorbs>

## Seams (not this team)
- **FP&A budget / P&L plan / capital budgeting:** finance
- **Payment-rail / API engineering:** fintech-payments-engineering
- **Deep AML / OFAC / sanctions program:** regulatory-compliance
- **Supplier payment-term negotiation:** procurement-sourcing
- **Controls audit:** internal-audit

## Open questions / risks
- <list>

**Sign-off:** <treasurer / CFO> · <date> · *Not legal/tax/accounting advice — volatile specifics verified at use (<retrieval date>).*
