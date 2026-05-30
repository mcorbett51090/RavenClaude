# Forecast near-term cash by the direct method over thirteen weeks — not an indirect derivation

**Status:** Pattern
**Domain:** Treasury / cash management
**Applies to:** `finance`

---

## Why this exists

Near-term liquidity is a survival question, and the indirect cash-flow statement — useful as it is inside the three-statement model — is the wrong tool for it. The indirect method starts from net income and adjusts for accruals; it tells you whether the *business* generates cash over a quarter, not whether *this Friday's payroll clears*. The `treasury-analyst` rule is "direct method beats indirect for cash forecasting: AR cohorts in, AP buckets out — much harder to fool yourself than starting from net income," and "13-week is the right horizon — shorter is operational, longer is FP&A's job." The direct method forecasts actual receipts (by source, timed to collection behaviour) and actual disbursements (by category, timed to payment terms), so the closing-cash line is a real bank-balance projection you can act on, and a downside scenario tells you the exact week cash runs tight.

## How to apply

Forecast receipts by source and disbursements by category, week by week, opening + flows = closing; always carry a downside and a covenant-headroom line:

```
Week:                    W1    W2    ...   W13
Opening cash             ...
+ Receipts (by source):  AR collections (by aging cohort), other inflows
− Disbursements (by cat): payroll, AP runs, debt service, taxes, rent, capex, earnouts, deferred comp
= Net cash flow
= Closing cash           -> opening of next week
Scenarios:  base / downside (revenue −X%, collections +Y days delay) / stress
Covenant headroom:       min-liquidity covenant − projected low-point closing cash   (must stay > 0)
```

**Do:**
- Time receipts to **collection behaviour** (AR aging cohorts), not to invoice date — cash lands when customers pay, not when you bill.
- Include every material disbursement — payroll, tax payments, debt service, earnouts, deferred comp — the named gap is "missing material disbursements."
- Carry a downside/stress scenario and a covenant-headroom row; track forecast-vs-actual cash by week and recalibrate when bias > ~5% (the agent's discipline).

**Don't:**
- Present an indirect (net-income-derived) forecast as if it were a 13-week direct cash forecast — that is the named anti-pattern.
- Run base case only — a treasury forecast without a downside is a constitution §4 anti-pattern.
- Net receipts and disbursements into one line — you lose the ability to see *which* lever (collections vs. spend) to pull.

## Edge cases / when the rule does NOT apply

- **Longer-range cash** (quarters / years for runway and planning) is FP&A's indirect, driver-based job, not the 13-week direct artifact — different horizon, different method.
- **Deeply cash-rich, low-volatility businesses** may extend the cadence, but the direct method and the downside scenario still apply when liquidity tightens.
- **The model's own indirect CF** (inside the three-statement build) is a separate, legitimate artifact — see [`./model-derive-the-cash-flow-bridge-from-net-income.md`](./model-derive-the-cash-flow-bridge-from-net-income.md); this rule governs the *treasury* forecast.

## See also

- [`./model-derive-the-cash-flow-bridge-from-net-income.md`](./model-derive-the-cash-flow-bridge-from-net-income.md) — the indirect bridge this is explicitly *not*.
- [`./treasury-manage-the-cash-conversion-cycle.md`](./treasury-manage-the-cash-conversion-cycle.md) — the DSO/DPO/DIO drivers that shape the timing of receipts and disbursements.
- [`./treasury-cite-the-agreement-on-every-covenant.md`](./treasury-cite-the-agreement-on-every-covenant.md) — the covenant-headroom line references the agreement.
- [`../agents/treasury-analyst.md`](../agents/treasury-analyst.md) — "direct method beats indirect"; "13-week is the right horizon"; forecast-bias discipline.
- [`../skills/thirteen-week-cash-forecast/SKILL.md`](../skills/thirteen-week-cash-forecast/SKILL.md) — the full build playbook.

## Provenance

Codifies the `treasury-analyst` opinions "direct method beats indirect for cash forecasting" and "13-week is the right horizon," its missing-disbursements / indirect-presented-as-direct anti-patterns, and the constitution §4 anti-pattern "treasury forecasts without a downside / stress scenario" ([`../CLAUDE.md`](../CLAUDE.md)). New.

---

_Last reviewed: 2026-05-30 by `claude`_
